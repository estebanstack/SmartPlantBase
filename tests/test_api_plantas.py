"""
Pruebas de integración del registro de plantas y del token del dispositivo (R7).
Recorre el flujo completo que se muestra en la sustentación:
usuario nuevo -> registra su planta -> recibe el token del dispositivo ->
el dispositivo reporta con ese token -> el dueño ve el estado; otro usuario no puede.
"""
import tempfile
from pathlib import Path

import pytest

from matera.app import create_app

CLAVE_PRUEBAS = "clave-solo-para-pruebas-con-32-bytes-o-mas"


@pytest.fixture
def client():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta_bd = f.name
    app = create_app(ruta_bd=ruta_bd, clave_jwt=CLAVE_PRUEBAS)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
    Path(ruta_bd).unlink(missing_ok=True)


def _registrar(client, email):
    resp = client.post("/api/auth/registro", json={"nombre": "Prueba", "email": email, "password": "clave123"})
    assert resp.status_code == 201
    return {"Authorization": f"Bearer {resp.get_json()['token']}"}


def _crear_planta(client, headers, dispositivo_id="esp32-leo", especie="potos"):
    return client.post(
        "/api/plantas",
        json={"nombre": "Potos de la sala", "especie": especie, "dispositivo_id": dispositivo_id},
        headers=headers,
    )


def test_flujo_completo_planta_nueva_con_su_dispositivo(client):
    headers_leo = _registrar(client, "leo@matera.edu.co")

    # 1. Leo registra su planta y recibe el token del dispositivo
    resp = _crear_planta(client, headers_leo)
    assert resp.status_code == 201
    datos = resp.get_json()
    planta_id = datos["planta"]["id"]
    token_dispositivo = datos["token_dispositivo"]
    assert datos["planta"]["dispositivo_id"] == "esp32-leo"

    # 2. La planta aparece en su lista
    plantas = client.get("/api/plantas", headers=headers_leo).get_json()
    assert [p["id"] for p in plantas] == [planta_id]

    # 3. El dispositivo reporta con el token que entregó el backend
    resp = client.post(
        "/api/dispositivos/esp32-leo/lecturas",
        json={"humedad": 55.0, "luz": 600.0, "temperatura": 22.0, "marca_tiempo": "2026-10-27T15:00:00Z"},
        headers={"Authorization": f"Bearer {token_dispositivo}"},
    )
    assert resp.status_code == 201

    # 4. Leo ve el estado actualizado
    estado = client.get(f"/api/plantas/{planta_id}/estado", headers=headers_leo).get_json()
    assert estado["diagnostico"]["estado"] == "SALUDABLE"


def test_otro_usuario_no_puede_pedir_el_token_de_una_planta_ajena(client):
    headers_leo = _registrar(client, "leo@matera.edu.co")
    headers_eva = _registrar(client, "eva@matera.edu.co")
    planta_id = _crear_planta(client, headers_leo).get_json()["planta"]["id"]

    resp_dueno = client.post(f"/api/plantas/{planta_id}/token-dispositivo", headers=headers_leo)
    assert resp_dueno.status_code == 200
    assert resp_dueno.get_json()["token_dispositivo"]

    resp_ajena = client.post(f"/api/plantas/{planta_id}/token-dispositivo", headers=headers_eva)
    assert resp_ajena.status_code == 403
    assert resp_ajena.get_json()["error"] == "ACCESO_DENEGADO"


def test_dispositivo_repetido_responde_409(client):
    headers_leo = _registrar(client, "leo@matera.edu.co")
    assert _crear_planta(client, headers_leo).status_code == 201

    resp = _crear_planta(client, headers_leo)
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "DISPOSITIVO_YA_VINCULADO"


def test_crear_planta_valida_los_datos(client):
    headers_leo = _registrar(client, "leo@matera.edu.co")

    resp = _crear_planta(client, headers_leo, especie="rosa")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "ESPECIE_NO_SOPORTADA"

    resp = _crear_planta(client, headers_leo, dispositivo_id="esp32 con espacios")
    assert resp.status_code == 400
    assert resp.get_json()["detalle"]["campo"] == "dispositivo_id"

    resp = client.post("/api/plantas", json={"especie": "potos"}, headers=headers_leo)
    assert resp.status_code == 400


def test_crear_planta_exige_token_de_usuario(client):
    resp = client.post("/api/plantas", json={"nombre": "x", "especie": "potos", "dispositivo_id": "esp32-x"})
    assert resp.status_code == 401
