"""
Pruebas del borde HTTP: el backend responde SIEMPRE en JSON, con el cuerpo uniforme
{"error", "mensaje", "detalle"}, y una petición mal armada es 400, nunca 500.
"""
import tempfile
from pathlib import Path

import pytest

from matera.app import create_app

CLAVE_PRUEBAS = "clave-solo-para-pruebas-con-32-bytes-o-mas"
LECTURA_VALIDA = {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0,
                  "marca_tiempo": "2026-10-27T15:00:00Z"}


@pytest.fixture
def client():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta_bd = f.name
    app = create_app(ruta_bd=ruta_bd, clave_jwt=CLAVE_PRUEBAS, datos_demo=True)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
    Path(ruta_bd).unlink(missing_ok=True)


def _token_usuario(client):
    return client.post(
        "/api/auth/login", json={"email": "ana@matera.edu.co", "password": "clave123"}
    ).get_json()["token"]


def _token_dispositivo(client):
    cabecera = {"Authorization": f"Bearer {_token_usuario(client)}"}
    respuesta = client.post("/api/plantas/planta-01/token-dispositivo", headers=cabecera)
    return respuesta.get_json()["token_dispositivo"]


def _es_error_uniforme(respuesta, status, codigo=None):
    assert respuesta.status_code == status
    assert respuesta.is_json, "el backend nunca debe responder HTML"
    cuerpo = respuesta.get_json()
    assert set(cuerpo) == {"error", "mensaje", "detalle"}
    if codigo:
        assert cuerpo["error"] == codigo
    return cuerpo


# --- Errores que genera Flask por su cuenta --------------------------------------

def test_metodo_no_permitido_responde_json_y_no_html(client):
    _es_error_uniforme(client.get("/api/v1/diagnosticos"), 405, "METODO_NO_PERMITIDO")
    _es_error_uniforme(client.delete("/api/v1/especies"), 405, "METODO_NO_PERMITIDO")


def test_ruta_inexistente_responde_json(client):
    _es_error_uniforme(client.get("/api/no-existe"), 404, "RECURSO_NO_ENCONTRADO")


# --- Cuerpos mal armados: 400, no 500 ----------------------------------------------

@pytest.mark.parametrize("cuerpo", [[1, 2], 42, "texto"])
def test_cuerpo_que_no_es_objeto_json_es_400(client, cuerpo):
    cabecera = {"Authorization": f"Bearer {_token_usuario(client)}"}
    cuerpo_error = _es_error_uniforme(
        client.post("/api/v1/diagnosticos", json=cuerpo, headers=cabecera), 400, "PARAMETRO_INVALIDO"
    )
    assert cuerpo_error["detalle"]["campo"] == "body"
    _es_error_uniforme(client.post("/api/auth/registro", json=cuerpo), 400, "PARAMETRO_INVALIDO")
    _es_error_uniforme(client.post("/api/auth/login", json=cuerpo), 400, "PARAMETRO_INVALIDO")


def test_lectura_del_dispositivo_que_no_es_objeto_json_es_400(client):
    cabecera = {"Authorization": f"Bearer {_token_dispositivo(client)}"}
    respuesta = client.post("/api/dispositivos/esp32-01/lecturas", json=[LECTURA_VALIDA], headers=cabecera)
    _es_error_uniforme(respuesta, 400, "PARAMETRO_INVALIDO")


@pytest.mark.parametrize("campo", ["nombre", "email", "password"])
def test_registro_con_campo_que_no_es_texto_es_400(client, campo):
    datos = {"nombre": "Luisa", "email": "luisa@matera.edu.co", "password": "secreta1"}
    datos[campo] = 123
    cuerpo = _es_error_uniforme(client.post("/api/auth/registro", json=datos), 400, "PARAMETRO_INVALIDO")
    assert cuerpo["detalle"]["campo"] == campo


@pytest.mark.parametrize("valor", ["NaN", "Infinity", "-Infinity"])
def test_nan_e_infinito_se_rechazan_como_no_numericos(client, valor):
    cabecera = {"Authorization": f"Bearer {_token_usuario(client)}"}
    cuerpo_crudo = '{"especie": "potos", "humedad": %s, "luz": 500, "temperatura": 22}' % valor
    respuesta = client.post(
        "/api/v1/diagnosticos", data=cuerpo_crudo, content_type="application/json", headers=cabecera
    )
    cuerpo = _es_error_uniforme(respuesta, 400, "PARAMETRO_INVALIDO")
    assert cuerpo["detalle"]["campo"] == "humedad"
    assert "no es un número válido" in cuerpo["mensaje"]


@pytest.mark.parametrize("limite", ["abc", "0", "-1", "1000"])
def test_limite_del_historial_invalido_es_400(client, limite):
    cabecera = {"Authorization": f"Bearer {_token_usuario(client)}"}
    respuesta = client.get(f"/api/plantas/planta-01/historial?limite={limite}", headers=cabecera)
    cuerpo = _es_error_uniforme(respuesta, 400, "PARAMETRO_INVALIDO")
    assert cuerpo["detalle"]["campo"] == "limite"
