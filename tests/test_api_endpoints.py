"""
Pruebas de integración de la API REST (Capa de Presentación).
Verifica los endpoints /api/v1/diagnosticos y /api/v1/especies,
el cumplimiento de Anexo A y el manejo uniforme de errores de RF6.
"""
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_endpoint_listar_especies(client):
    """Verifica GET /api/v1/especies (RF5 y Anexo A)."""
    response = client.get("/api/v1/especies")
    assert response.status_code == 200
    datos = response.get_json()
    assert isinstance(datos, list)
    assert len(datos) >= 5
    nombres = [item["nombre"] for item in datos]
    assert "sansevieria" in nombres
    assert "humedad" in datos[0]["rangos"]


def test_endpoint_evaluar_diagnostico_exitoso(client):
    """Verifica POST /api/v1/diagnosticos con datos válidos (200 OK)."""
    payload = {
        "especie": "sansevieria",
        "humedad": 32.5,
        "luz": 850,
        "temperatura": 21.0,
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 200
    datos = response.get_json()
    assert datos["especie"] == "sansevieria"
    assert datos["estado"] == "SALUDABLE"
    assert len(datos["parametros"]) == 3
    assert "recomendaciones" in datos


def test_endpoint_evaluar_diagnostico_con_desviacion_y_recomendaciones(client):
    """Verifica POST /api/v1/diagnosticos con una desviación que genera recomendación (RF4)."""
    payload = {
        "especie": "sansevieria",
        "humedad": 15.0,  # por debajo de 20%
        "luz": 850,
        "temperatura": 21.0,
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 200
    datos = response.get_json()
    assert datos["estado"] == "EN_RIESGO"
    assert len(datos["recomendaciones"]) == 1
    assert "por debajo del rango recomendado" in datos["recomendaciones"][0]


def test_endpoint_evaluar_error_especie_desconocida(client):
    """Verifica 404 NOT FOUND para especie desconocida (RF6 y Anexo A)."""
    payload = {
        "especie": "planta_fantasma_xyz",
        "humedad": 30.0,
        "luz": 500,
        "temperatura": 22.0,
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 404
    datos = response.get_json()
    assert datos["error"] == "ESPECIE_NO_SOPORTADA"
    assert "detalle" in datos
    assert datos["detalle"]["especie"] == "planta_fantasma_xyz"


def test_endpoint_evaluar_error_parametro_ausente(client):
    """Verifica 400 BAD REQUEST cuando falta un parámetro obligatorio (RF6)."""
    payload = {
        "especie": "sansevieria",
        "humedad": 30.0,
        # falta luz y temperatura
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 400
    datos = response.get_json()
    assert datos["error"] == "PARAMETRO_INVALIDO"
    assert "luz" in datos["mensaje"] or datos["detalle"]["campo"] in ["luz", "temperatura"]


def test_endpoint_evaluar_error_valor_no_numerico(client):
    """Verifica 400 BAD REQUEST cuando un parámetro no es numérico (RF6)."""
    payload = {
        "especie": "sansevieria",
        "humedad": "no_es_un_numero",
        "luz": 500,
        "temperatura": 22.0,
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 400
    datos = response.get_json()
    assert datos["error"] == "PARAMETRO_INVALIDO"
    assert datos["detalle"]["campo"] == "humedad"


def test_endpoint_evaluar_error_valor_fisicamente_imposible(client):
    """Verifica 400 BAD REQUEST cuando un parámetro está fuera de límites físicos (RF6)."""
    payload = {
        "especie": "sansevieria",
        "humedad": -15.0,  # % negativo
        "luz": 500,
        "temperatura": 22.0,
    }
    response = client.post("/api/v1/diagnosticos", json=payload)
    assert response.status_code == 400
    datos = response.get_json()
    assert datos["error"] == "PARAMETRO_INVALIDO"
    assert datos["detalle"]["campo"] == "humedad"
