"""
Pruebas integrales de la Arquitectura Dual de WebSockets y Endpoints de Autenticación QR.
Verifica:
1. Gestión de salas Pre-Auth ('qr_{session_id}') y Post-Auth ('user_{usuario_id}').
2. Difusión (broadcast) de autorización QR en tiempo real.
3. Notificaciones en vivo de alertas botánicas y telemetría hacia salas de usuario.
4. Integración fluida entre peticiones HTTP REST y eventos WebSocket.
"""
import pytest
from app import create_app
from src.infrastructure.repositories.memoria_sesion_qr_repository import MemoriaSesionQRRepository
from src.presentation.websocket_handlers import (
    notificar_alerta_usuario,
    notificar_qr_autorizado,
    notificar_telemetria_usuario,
)


@pytest.fixture
def app_instance():
    """Instancia de la aplicación Flask con SocketIO y repositorio en memoria limpio."""
    repo = MemoriaSesionQRRepository()
    app = create_app(sesion_qr_repo=repo)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def socket_client(app_instance):
    """Cliente de prueba WebSocket nativo de Flask-SocketIO."""
    client = app_instance.socketio.test_client(app_instance)
    yield client
    if client.is_connected():
        client.disconnect()


@pytest.fixture
def http_client(app_instance):
    """Cliente HTTP de prueba para endpoints REST."""
    with app_instance.test_client() as client:
        yield client


# ===========================================================================
# 1. Pruebas de Gestión de Salas (Pre-Auth y Post-Auth)
# ===========================================================================

def test_unirse_y_salir_sala_pre_auth_qr(socket_client):
    """Verifica que un cliente no autenticado pueda unirse y salir de una sala QR efímera."""
    # Unirse a la sala QR
    ack = socket_client.emit("unirse_sesion_qr", {"session_id": "sesion_abc_123"}, callback=True)
    assert ack["status"] == "ok"
    assert ack["sala"] == "qr_sesion_abc_123"

    # Salir de la sala QR
    ack_leave = socket_client.emit("salir_sesion_qr", {"session_id": "sesion_abc_123"}, callback=True)
    assert ack_leave["status"] == "ok"
    assert ack_leave["sala"] == "qr_sesion_abc_123"


def test_unirse_y_salir_sala_post_auth_usuario(socket_client):
    """Verifica que un usuario autenticado pueda unirse y salir de su canal personal."""
    ack = socket_client.emit("unirse_canal_usuario", {"usuario_id": "usr_esteban_777"}, callback=True)
    assert ack["status"] == "ok"
    assert ack["sala"] == "user_usr_esteban_777"

    ack_leave = socket_client.emit("salir_canal_usuario", {"usuario_id": "usr_esteban_777"}, callback=True)
    assert ack_leave["status"] == "ok"
    assert ack_leave["sala"] == "user_usr_esteban_777"


def test_unirse_sala_con_datos_invalidos(socket_client):
    """Verifica el manejo de error cuando no se envían los identificadores de sala requeridos."""
    ack_qr = socket_client.emit("unirse_sesion_qr", {}, callback=True)
    assert ack_qr["error"] == "PARAMETRO_INVALIDO"

    ack_usr = socket_client.emit("unirse_canal_usuario", {}, callback=True)
    assert ack_usr["error"] == "PARAMETRO_INVALIDO"


# ===========================================================================
# 2. Pruebas de Autorización QR en Tiempo Real vía WebSocket
# ===========================================================================

def test_flujo_completo_autorizacion_qr_websocket(app_instance):
    """
    Simula el flujo dual:
    1. El navegador Web se une a la sala 'qr_sess_web_1'.
    2. El teléfono Móvil autoriza la sesión enviando el evento 'autorizar_qr'.
    3. El navegador Web recibe inmediatamente el evento 'qr_autorizado' con las credenciales.
    """
    # Crear sesión QR previa mediante el use case / endpoint
    http_cli = app_instance.test_client()
    resp_init = http_cli.post("/api/v1/auth/qr/generar", json={"session_id": "sess_web_1"})
    assert resp_init.status_code == 201

    # Cliente 1: Navegador Web esperando en la sala pre-auth
    web_client = app_instance.socketio.test_client(app_instance)
    web_client.emit("unirse_sesion_qr", {"session_id": "sess_web_1"}, callback=True)

    # Cliente 2: Teléfono móvil enviando autorización
    movil_client = app_instance.socketio.test_client(app_instance)
    ack_auth = movil_client.emit(
        "autorizar_qr",
        {
            "session_id": "sess_web_1",
            "usuario_id": "usr_movil_42",
            "token": "bearer_jwt_movil_token_xyz",
        },
        callback=True,
    )
    assert ack_auth["status"] == "ok"
    assert ack_auth["sesion"]["estado"] == "AUTORIZADA"

    # Verificar que el Navegador Web recibió la notificación en la sala
    recibidos = web_client.get_received()
    eventos_qr = [e for e in recibidos if e["name"] == "qr_autorizado"]
    assert len(eventos_qr) == 1
    datos_recibidos = eventos_qr[0]["args"][0]
    assert datos_recibidos["usuario_id"] == "usr_movil_42"
    assert datos_recibidos["token"] == "bearer_jwt_movil_token_xyz"
    assert datos_recibidos["estado"] == "AUTORIZADA"

    web_client.disconnect()
    movil_client.disconnect()


# ===========================================================================
# 3. Pruebas de Notificaciones de Telemetría y Alertas Botánicas
# ===========================================================================

def test_notificaciones_alerta_y_telemetria_sala_usuario(app_instance, socket_client):
    """Verifica el envío de alertas y telemetría a la sala privada del usuario."""
    socket_client.emit("unirse_canal_usuario", {"usuario_id": "usr_verde_1"}, callback=True)

    # 1. Disparar alerta botánica
    notificar_alerta_usuario(
        socketio=app_instance.socketio,
        usuario_id="usr_verde_1",
        alerta={"planta_id": "planta_albahaca_1", "mensaje": "Humedad crítica baja", "estado": "CRITICO"},
    )

    # 2. Disparar telemetría en tiempo real
    notificar_telemetria_usuario(
        socketio=app_instance.socketio,
        usuario_id="usr_verde_1",
        telemetria={"humedad": 18.0, "luz": 400.0, "temperatura": 24.5},
    )

    recibidos = socket_client.get_received()
    eventos_alerta = [e for e in recibidos if e["name"] == "alerta_planta"]
    eventos_telemetria = [e for e in recibidos if e["name"] == "telemetria_actualizada"]

    assert len(eventos_alerta) == 1
    assert eventos_alerta[0]["args"][0]["estado"] == "CRITICO"

    assert len(eventos_telemetria) == 1
    assert eventos_telemetria[0]["args"][0]["humedad"] == 18.0


# ===========================================================================
# 4. Pruebas de Integración Híbrida: REST + WebSockets
# ===========================================================================

def test_autorizacion_via_rest_notifica_a_websocket(app_instance, http_client, socket_client):
    """
    Verifica que al autorizar por POST /api/v1/auth/qr/<id>/autorizar (típico de app móvil),
    el navegador conectado por WebSocket en la sala 'qr_<id>' recibe el evento 'qr_autorizado'.
    """
    # 1. Crear sesión QR
    resp_crear = http_client.post("/api/v1/auth/qr/generar", json={"session_id": "qr_hibrido_99"})
    assert resp_crear.status_code == 201

    # 2. Navegador entra a la sala por WebSocket
    socket_client.emit("unirse_sesion_qr", {"session_id": "qr_hibrido_99"}, callback=True)

    # 3. Móvil envía autorización vía REST HTTP
    resp_auth = http_client.post(
        "/api/v1/auth/qr/qr_hibrido_99/autorizar",
        json={"usuario_id": "usr_celular_55", "token": "jwt_celular_abc"},
    )
    assert resp_auth.status_code == 200
    assert resp_auth.get_json()["estado"] == "AUTORIZADA"

    # 4. Verificar que el socket del navegador recibió el evento
    recibidos = socket_client.get_received()
    eventos_qr = [e for e in recibidos if e["name"] == "qr_autorizado"]
    assert len(eventos_qr) == 1
    assert eventos_qr[0]["args"][0]["usuario_id"] == "usr_celular_55"


def test_evaluacion_diagnostico_emite_alerta_a_sala_usuario(app_instance, http_client, socket_client):
    """
    Verifica que al evaluar un diagnóstico para un usuario específico con valores en riesgo,
    el WebSocket de dicho usuario reciba la alerta y la actualización de telemetría.
    """
    # El usuario se conecta a su canal personal
    socket_client.emit("unirse_canal_usuario", {"usuario_id": "usr_jardinero_1"}, callback=True)

    # Se evalúa una medición en riesgo enviando usuario_id
    payload = {
        "especie": "sansevieria",
        "humedad": 10.0,  # Muy bajo para sansevieria (óptimo 20-50%)
        "luz": 800.0,
        "temperatura": 22.0,
        "usuario_id": "usr_jardinero_1",
    }
    resp = http_client.post("/api/v1/diagnosticos", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["estado"] == "EN_RIESGO"

    # Verificar que el usuario recibió alerta y telemetría por WebSocket
    recibidos = socket_client.get_received()
    eventos_alerta = [e for e in recibidos if e["name"] == "alerta_planta"]
    eventos_telemetria = [e for e in recibidos if e["name"] == "telemetria_actualizada"]

    assert len(eventos_alerta) == 1
    assert eventos_alerta[0]["args"][0]["estado"] == "EN_RIESGO"
    assert len(eventos_telemetria) == 1
    assert eventos_telemetria[0]["args"][0]["valores"]["humedad"] == 10.0
