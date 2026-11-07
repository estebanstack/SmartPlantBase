"""
Pruebas de integración de los adaptadores WebSocket (Flask-SocketIO) y Sesiones QR:
- Vinculación de dispositivos mediante QR sin exponer tokens manualmente en la UI.
- Notificaciones push en tiempo real en la sala `qr_{session_id}` al autorizar un QR.
- Telemetría en tiempo real (`telemetria_actualizada`) y alertas (`alerta_planta`)
  en la sala `user_{usuario_id}` cuando el ESP32 reporta lecturas.
"""
import pytest

from matera.app import create_app


@pytest.fixture
def app_ws(tmp_path):
    db_test = str(tmp_path / "matera_ws_test.db")
    app = create_app(ruta_bd=db_test, datos_demo=False)
    app.config["TESTING"] = True
    return app


def _registrar_usuario_y_planta(client):
    resp_reg = client.post(
        "/api/auth/registro",
        json={
            "nombre": "Esteban",
            "email": "esteban@matera.edu.co",
            "password": "password123",
        },
    )
    assert resp_reg.status_code == 201
    datos_reg = resp_reg.get_json()
    token_usr = datos_reg["token"]
    usuario_id = datos_reg["usuario"]["id"]

    resp_planta = client.post(
        "/api/plantas",
        headers={"Authorization": f"Bearer {token_usr}"},
        json={
            "nombre": "Helecho de Estudio",
            "especie": "helecho",
            "dispositivo_id": "esp32-qr-01",
        },
    )
    assert resp_planta.status_code == 201
    planta_id = resp_planta.get_json()["planta"]["id"]
    return token_usr, usuario_id, planta_id


def test_flujo_qr_emite_evento_websocket_y_vincula_dispositivo(app_ws):
    client = app_ws.test_client()
    socketio = app_ws.socketio
    token_usr, usuario_id, planta_id = _registrar_usuario_y_planta(client)

    # 1. Se genera una sesión QR para el dispositivo esp32-qr-01
    resp_qr = client.post(
        "/api/auth/qr/generar",
        json={"dispositivo_id": "esp32-qr-01"},
    )
    assert resp_qr.status_code == 201
    datos_qr = resp_qr.get_json()
    session_id = datos_qr["session_id"]
    assert datos_qr["estado"] == "PENDIENTE"

    # 2. Un cliente WebSocket se suscribe a la sala qr_{session_id}
    ws_client = socketio.test_client(app_ws)
    ack_join = ws_client.emit("unirse_sesion_qr", {"session_id": session_id}, callback=True)
    assert ack_join["status"] == "ok"
    assert ack_join["sala"] == f"qr_{session_id}"

    # 3. El usuario autenticado autoriza el QR (vía REST o WebSocket)
    resp_aut = client.post(
        f"/api/auth/qr/{session_id}/autorizar",
        headers={"Authorization": f"Bearer {token_usr}"},
        json={"planta_id": planta_id},
    )
    assert resp_aut.status_code == 200
    datos_aut = resp_aut.get_json()
    assert datos_aut["estado"] == "AUTORIZADA"
    assert datos_aut["dispositivo_id"] == "esp32-qr-01"
    assert datos_aut["token"]

    # 4. El cliente WebSocket en la sala qr_{session_id} recibe `qr_autorizado` instantáneamente
    recibidos_qr = ws_client.get_received()
    eventos_qr = [ev for ev in recibidos_qr if ev["name"] == "qr_autorizado"]
    assert len(eventos_qr) == 1
    payload_ws = eventos_qr[0]["args"][0]
    assert payload_ws["id"] == session_id
    assert payload_ws["estado"] == "AUTORIZADA"
    assert payload_ws["token"] == datos_aut["token"]

    ws_client.disconnect()


def test_autorizar_qr_directamente_por_evento_websocket(app_ws):
    client = app_ws.test_client()
    socketio = app_ws.socketio
    token_usr, usuario_id, planta_id = _registrar_usuario_y_planta(client)

    resp_qr = client.post("/api/auth/qr/generar", json={"planta_id": planta_id})
    session_id = resp_qr.get_json()["id"]

    ws_espera = socketio.test_client(app_ws)
    ws_espera.emit("unirse_sesion_qr", {"session_id": session_id})
    ws_espera.get_received()

    ws_movil = socketio.test_client(app_ws)
    ack_aut = ws_movil.emit(
        "autorizar_qr",
        {
            "session_id": session_id,
            "token_usuario": token_usr,
            "planta_id": planta_id,
        },
        callback=True,
    )
    assert ack_aut["status"] == "ok"

    recibidos = ws_espera.get_received()
    eventos_qr = [ev for ev in recibidos if ev["name"] == "qr_autorizado"]
    assert len(eventos_qr) == 1
    assert eventos_qr[0]["args"][0]["dispositivo_id"] == "esp32-qr-01"

    ws_espera.disconnect()
    ws_movil.disconnect()


def test_telemetria_y_alertas_push_en_tiempo_real_al_registrar_lectura(app_ws):
    client = app_ws.test_client()
    socketio = app_ws.socketio
    token_usr, usuario_id, planta_id = _registrar_usuario_y_planta(client)

    # Obtenemos el token de dispositivo vía QR
    resp_qr = client.post("/api/auth/qr/generar", json={"planta_id": planta_id})
    session_id = resp_qr.get_json()["id"]
    resp_aut = client.post(
        f"/api/auth/qr/{session_id}/autorizar",
        headers={"Authorization": f"Bearer {token_usr}"},
        json={"planta_id": planta_id},
    )
    token_disp = resp_aut.get_json()["token"]

    # El dashboard se une a la sala del usuario `user_{usuario_id}` usando su JWT
    ws_dashboard = socketio.test_client(app_ws)
    ack_user = ws_dashboard.emit(
        "unirse_canal_usuario", {"token_usuario": token_usr}, callback=True
    )
    assert ack_user["status"] == "ok"
    assert ack_user["sala"] == f"user_{usuario_id}"
    ws_dashboard.get_received()

    # 1. El ESP32 envía una lectura SALUDABLE: llega `telemetria_actualizada`, sin `alerta_planta`
    resp_lectura_ok = client.post(
        "/api/dispositivos/esp32-qr-01/lecturas",
        headers={"Authorization": f"Bearer {token_disp}"},
        json={
            "humedad": 70.0,
            "luz": 400.0,
            "temperatura": 21.0,
            "marca_tiempo": "2026-10-27T15:00:00Z",
        },
    )
    assert resp_lectura_ok.status_code == 201

    eventos_ok = ws_dashboard.get_received()
    nombres_ok = [ev["name"] for ev in eventos_ok]
    assert "telemetria_actualizada" in nombres_ok
    assert "alerta_planta" not in nombres_ok

    # 2. El ESP32 envía una lectura CRÍTICA: llegan tanto `telemetria_actualizada` como `alerta_planta`
    resp_lectura_crit = client.post(
        "/api/dispositivos/esp32-qr-01/lecturas",
        headers={"Authorization": f"Bearer {token_disp}"},
        json={
            "humedad": 15.0,
            "luz": 2000.0,
            "temperatura": 34.0,
            "marca_tiempo": "2026-10-27T15:05:00Z",
        },
    )
    assert resp_lectura_crit.status_code == 201

    eventos_crit = ws_dashboard.get_received()
    telemetrias = [ev for ev in eventos_crit if ev["name"] == "telemetria_actualizada"]
    alertas = [ev for ev in eventos_crit if ev["name"] == "alerta_planta"]
    assert len(telemetrias) == 1
    assert len(alertas) == 1
    assert alertas[0]["args"][0]["estado"] == "CRITICO"
    assert alertas[0]["args"][0]["planta_id"] == planta_id
    assert len(alertas[0]["args"][0]["recomendaciones"]) >= 2

    ws_dashboard.disconnect()
