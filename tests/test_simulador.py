"""
Pruebas del simulador del ESP32 (R3).
1. Es independiente: no importa nada del paquete matera.
2. Genera lecturas realistas (dentro de lo físicamente posible, ciclo de luz, secado y riego).
3. Sabe dañar lecturas de las cuatro formas previstas.
4. De punta a punta: con el token que entrega el backend, sus lecturas válidas
   entran al historial y las inválidas se rechazan.
"""
import ast
import random
import tempfile
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

import simulador_esp32 as sim
from matera.app import create_app

RUTA_SIMULADOR = Path(__file__).parent.parent / "simulador_esp32.py"
CLAVE_PRUEBAS = "clave-solo-para-pruebas-con-32-bytes-o-mas"


def test_simulador_no_importa_nada_del_proyecto():
    arbol = ast.parse(RUTA_SIMULADOR.read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            modulos.add(nodo.module or "")
    assert not any(m == "matera" or m.startswith("matera.") for m in modulos)


def test_lecturas_realistas_dentro_de_limites_fisicos():
    matera = sim.MateraSimulada(random.Random(7), minutos_por_lectura=30, luz_maxima=1800)
    lecturas = [matera.leer() for _ in range(48 * 3)]  # tres días simulados

    for lectura in lecturas:
        assert 0 <= lectura["humedad"] <= 100
        assert 0 <= lectura["luz"] <= 1800 * 1.05
        assert 10 <= lectura["temperatura"] <= 30

    luces = [l["luz"] for l in lecturas]
    assert min(luces) < 10 and max(luces) > 800  # hay noche y hay día


def test_la_tierra_se_seca_y_luego_riegan():
    matera = sim.MateraSimulada(random.Random(3), minutos_por_lectura=30, luz_maxima=1800)
    humedades = []
    hubo_riego = False
    for _ in range(300):
        humedades.append(matera.leer()["humedad"])
        hubo_riego = hubo_riego or matera.regada
    assert min(humedades) < 20  # se secó lo suficiente como para salir de rango
    assert hubo_riego


@pytest.mark.parametrize("tipo", sim.TIPOS_DE_ERROR)
def test_danar_lectura(tipo):
    original = {"humedad": 40.0, "luz": 700.0, "temperatura": 22.0}
    danada = sim.danar_lectura(original, tipo, random.Random(1))

    if tipo == "imposible":
        assert danada.get("humedad") == 150.0 or danada.get("temperatura") == -99.0
    elif tipo == "no_numerico":
        assert "ERR" in danada.values()
    elif tipo == "campo_faltante":
        assert len(danada) == 2
    else:  # sin_token no toca los valores
        assert danada == original
    assert original == {"humedad": 40.0, "luz": 700.0, "temperatura": 22.0}


@pytest.fixture
def servidor():
    """Levanta el backend de verdad en un puerto libre, como en la demo."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta_bd = f.name
    app = create_app(ruta_bd=ruta_bd, clave_jwt=CLAVE_PRUEBAS)
    http = make_server("127.0.0.1", 0, app)
    hilo = threading.Thread(target=http.serve_forever, daemon=True)
    hilo.start()
    yield app, f"http://127.0.0.1:{http.server_port}"
    http.shutdown()
    Path(ruta_bd).unlink(missing_ok=True)


def test_simulador_de_punta_a_punta(servidor, capsys):
    app, url = servidor
    cliente = app.test_client()

    # El dueño se registra y crea su planta: el backend le entrega el token del dispositivo
    token_usuario = cliente.post(
        "/api/auth/registro", json={"nombre": "Leo", "email": "leo@matera.edu.co", "password": "clave123"}
    ).get_json()["token"]
    cabeceras = {"Authorization": f"Bearer {token_usuario}"}
    registrada = cliente.post(
        "/api/plantas",
        json={"nombre": "Potos", "especie": "potos", "dispositivo_id": "esp32-sim"},
        headers=cabeceras,
    ).get_json()

    # El simulador corre con ese token
    sim.main([
        "--url", url,
        "--dispositivo-id", "esp32-sim",
        "--token", registrada["token_dispositivo"],
        "--iteraciones", "30",
        "--intervalo", "0",
        "--prob-error", "0.3",
        "--semilla", "11",
    ])
    salida = capsys.readouterr().out

    assert "-> 201" in salida   # lecturas válidas aceptadas
    assert "-> 400" in salida   # datos dañados rechazados
    assert "-> 401" in salida   # petición sin token rechazada
    aceptadas = salida.count("-> 201")

    historial = cliente.get(
        f"/api/plantas/{registrada['planta']['id']}/historial?limite=100", headers=cabeceras
    ).get_json()
    assert len(historial) == aceptadas  # solo las válidas quedaron guardadas
