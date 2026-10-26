"""
Pruebas de integración del Adaptador de Entrada de Dispositivos (R2 y R3).
Verifica:
1. Recepción de telemetría de sensores en POST /api/dispositivos/{id}/lecturas.
2. Validación de tokens de dispositivo con scope='dispositivo'.
3. Restricción de alcance: un dispositivo sólo puede reportar a su propio {id}.
4. Manejo de lecturas válidas (201 Created), fuera de rango botánico (201 EN_RIESGO/CRITICO)
   y físicamente imposibles (400 Bad Request).
5. Persistencia y reflejo inmediato en la consulta de estado de la planta.
"""
import tempfile
from pathlib import Path
import pytest

from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.app import create_app


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta = f.name
    yield ruta
    Path(ruta).unlink(missing_ok=True)


@pytest.fixture
def emisor_jwt():
    return JwtEmisorTokenAdapter(secret_key="matera-secret-key-arquitectura-2026-segura")


@pytest.fixture
def app(temp_db):
    test_app = create_app(ruta_bd=temp_db)
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def token_esp32_01(emisor_jwt):
    return emisor_jwt.emitir_token_dispositivo("esp32-01", "planta-01")


@pytest.fixture
def token_esp32_02(emisor_jwt):
    return emisor_jwt.emitir_token_dispositivo("esp32-02", "planta-02")


def test_dispositivo_reporta_sin_token_falla(client):
    """Petición sin autenticación retorna 401."""
    payload = {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0}
    resp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "AUTORIZACION_REQUERIDA"


def test_token_de_usuario_rechazado_en_endpoint_de_dispositivo(client, emisor_jwt):
    """Un token con scope='usuario' no puede reportar lecturas como dispositivo (403)."""
    token_usuario = emisor_jwt.emitir_token_usuario("usr-ana", "ana@matera.edu.co")
    headers = {"Authorization": f"Bearer {token_usuario}"}
    payload = {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0}

    resp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload, headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "ACCESO_DENEGADO"


def test_dispositivo_no_puede_suplantar_a_otro(client, token_esp32_01):
    """Un token emitido para esp32-01 no puede reportar a /api/dispositivos/esp32-02/lecturas."""
    headers = {"Authorization": f"Bearer {token_esp32_01}"}
    payload = {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0}

    resp = client.post("/api/dispositivos/esp32-02/lecturas", json=payload, headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "ACCESO_DENEGADO"


def test_dispositivo_reporte_exitoso_y_reflejo_en_consulta(client, token_esp32_01, emisor_jwt):
    """
    R2 y R5: esp32-01 reporta lectura óptima (201 Created), se almacena en el historial
    y el usuario Ana la observa al consultar el estado de planta-01.
    """
    headers_disp = {"Authorization": f"Bearer {token_esp32_01}"}
    payload = {
        "humedad": 35.0,
        "luz": 600.0,
        "temperatura": 22.0,
        "marca_tiempo": "2026-10-26T17:00:00Z",
    }

    # 1. Registro por sensor ESP32
    resp_disp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload, headers=headers_disp)
    assert resp_disp.status_code == 201
    datos_disp = resp_disp.get_json()
    assert datos_disp["estado"] == "SALUDABLE"
    assert datos_disp["dispositivo_id"] == "esp32-01"

    # 2. Ana consulta el estado de su planta
    token_ana = emisor_jwt.emitir_token_usuario("usr-ana", "ana@matera.edu.co")
    headers_ana = {"Authorization": f"Bearer {token_ana}"}

    resp_ana = client.get("/api/plantas/planta-01/estado", headers=headers_ana)
    assert resp_ana.status_code == 200
    datos_ana = resp_ana.get_json()
    assert datos_ana["ultima_lectura"]["marca_tiempo"] == "2026-10-26T17:00:00Z"
    assert datos_ana["ultima_lectura"]["valores"]["humedad"] == 35.0
    assert datos_ana["diagnostico"]["estado"] == "SALUDABLE"


def test_dispositivo_reporte_fuera_de_rango_botanico(client, token_esp32_01):
    """Lectura válida en límites físicos pero fuera de rango óptimo genera alerta botánica (201 EN_RIESGO)."""
    headers = {"Authorization": f"Bearer {token_esp32_01}"}
    payload = {
        "humedad": 10.0,  # Sequía para Sansevieria (min 20%)
        "luz": 600.0,
        "temperatura": 22.0,
    }

    resp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload, headers=headers)
    assert resp.status_code == 201
    datos = resp.get_json()
    assert datos["estado"] == "EN_RIESGO"
    assert len(datos["diagnostico"]["recomendaciones"]) >= 1


def test_dispositivo_reporte_dato_fisicamente_imposible_rechazado(client, token_esp32_01):
    """Sensor corrupto enviando humedad 150% es rechazado con 400 Bad Request."""
    headers = {"Authorization": f"Bearer {token_esp32_01}"}
    payload = {
        "humedad": 150.0,
        "luz": 600.0,
        "temperatura": 22.0,
    }

    resp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload, headers=headers)
    assert resp.status_code == 400
    datos = resp.get_json()
    assert datos["error"] == "PARAMETRO_INVALIDO"
    assert datos["detalle"]["campo"] == "humedad"


def test_dispositivo_reporte_campo_ausente_rechazado(client, token_esp32_01):
    """Payload sin luz o sin temperatura es rechazado con 400 Bad Request."""
    headers = {"Authorization": f"Bearer {token_esp32_01}"}
    payload = {"humedad": 30.0}

    resp = client.post("/api/dispositivos/esp32-01/lecturas", json=payload, headers=headers)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "PARAMETRO_INVALIDO"
