"""
Pruebas del Matera-Gotchi: reglas del dominio (puras), adaptador SQLite, integración con
RegistrarLectura y los campos `gotchi` de la API (respuesta del dispositivo, GET y WebSocket).
También la regla nueva de vinculación por QR iniciada por el dispositivo.
"""
import sqlite3

import pytest

from matera.adaptadores.salida.gamificacion_bd import BdGamificacionAdapter
from matera.adaptadores.salida.sqlite_bd import inicializar_bd
from matera.app import create_app
from matera.dominio.casos_uso import AutorizarSesionQR, ConsultarGotchi, GenerarSesionQR, RegistrarLectura
from matera.dominio.excepciones import AccesoNoAutorizadoPlantaError, DispositivoYaVinculadoError
from matera.dominio.gamificacion import (
    EXPRESIONES,
    EstadoAnimico,
    MotorGamificacion,
    PerfilGamificacion,
    detectar_riego,
)
from matera.dominio.modelo import Lectura, Planta, EstadoSesionQR
from matera.dominio.validador import ValidadorDeEstado
from tests.fakes import (
    FakeEmisorToken,
    FakeGamificacion,
    FakeHistorialLecturas,
    FakeNotificadorTiempoReal,
    FakePlantas,
    FakeSesionesQR,
    FakeTablaReferencia,
)

# Sansevieria: humedad 20-45, luz 200-1500, temperatura 15-29
OPTIMO = {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0}


def _lectura(valores=None, marca="2026-11-23T10:00:00Z"):
    return Lectura(especie="sansevieria", valores=valores or OPTIMO, marca_tiempo=marca, planta_id="p1")


def _evaluar(valores=None, perfil=None, anterior=None, marca="2026-11-23T10:00:00Z"):
    lectura = _lectura(valores, marca)
    especie = FakeTablaReferencia().obtener_por_nombre("sansevieria")
    diagnostico = ValidadorDeEstado.evaluar(lectura, especie)
    return MotorGamificacion.evaluar(perfil or PerfilGamificacion("p1"), diagnostico, lectura, anterior)


# --- Dominio ------------------------------------------------------------------------------------

@pytest.mark.parametrize("valores, esperado", [
    (OPTIMO, EstadoAnimico.CONTENTA),
    ({**OPTIMO, "humedad": 10.0}, EstadoAnimico.SEDIENTA),
    ({**OPTIMO, "humedad": 70.0}, EstadoAnimico.AHOGADA),
    ({**OPTIMO, "temperatura": 35.0}, EstadoAnimico.SOFOCADA),
    ({**OPTIMO, "luz": 5000.0}, EstadoAnimico.SOFOCADA),
    ({**OPTIMO, "temperatura": 5.0}, EstadoAnimico.CONGELADA),
    ({**OPTIMO, "humedad": 10.0, "temperatura": 5.0}, EstadoAnimico.MARCHITA),  # dos desviaciones = CRITICO
])
def test_estado_animico_segun_diagnostico(valores, esperado):
    assert _evaluar(valores).ultimo_animo == esperado


def test_cada_estado_tiene_cara_ascii_corta_para_la_oled():
    assert set(EXPRESIONES) == set(EstadoAnimico)
    for expresion in EXPRESIONES.values():
        assert expresion.cara.isascii() and len(expresion.cara) <= 8
        assert expresion.mensaje and expresion.emoji


def test_riego_es_salto_de_mas_de_15_puntos_en_menos_de_5_minutos():
    antes = _lectura({**OPTIMO, "humedad": 20.0}, "2026-11-23T10:00:00Z")
    despues = _lectura({**OPTIMO, "humedad": 40.0}, "2026-11-23T10:03:00Z")
    assert detectar_riego(despues, antes)
    # El mismo salto pero 10 minutos después no cuenta como riego
    tarde = _lectura({**OPTIMO, "humedad": 40.0}, "2026-11-23T10:10:00Z")
    assert not detectar_riego(tarde, antes)
    # Un salto de 15 justos tampoco (tiene que ser mayor)
    justo = _lectura({**OPTIMO, "humedad": 35.0}, "2026-11-23T10:01:00Z")
    assert not detectar_riego(justo, antes)
    assert not detectar_riego(despues, None)


def test_riego_da_agradecida_y_50_xp():
    antes = _lectura({**OPTIMO, "humedad": 20.0}, "2026-11-23T10:00:00Z")
    perfil = _evaluar({**OPTIMO, "humedad": 40.0}, anterior=antes, marca="2026-11-23T10:00:20Z")
    assert perfil.ultimo_animo == EstadoAnimico.AGRADECIDA
    assert perfil.xp_total == 50


def test_xp_por_estado_y_nunca_negativa():
    assert _evaluar().xp_total == 10                                            # contenta +10
    sedienta = _evaluar({**OPTIMO, "humedad": 10.0}, perfil=PerfilGamificacion("p1", xp_total=3))
    assert sedienta.xp_total == 0                                               # 3 - 5 se queda en 0
    marchita = _evaluar({**OPTIMO, "humedad": 10.0, "temperatura": 5.0}, perfil=PerfilGamificacion("p1", xp_total=100))
    assert marchita.xp_total == 70                                              # -30


@pytest.mark.parametrize("xp, nivel", [(0, 1), (150, 1), (151, 2), (450, 2), (451, 3), (1000, 3), (1001, 4), (2000, 4), (2001, 5)])
def test_niveles_segun_xp(xp, nivel):
    assert PerfilGamificacion("p1", xp_total=xp).nivel == nivel


def test_racha_suma_un_dia_cada_24h_saludable_y_da_radiante():
    perfil = _evaluar(marca="2026-11-23T10:00:00Z")
    assert (perfil.racha_dias, perfil.ultimo_animo) == (0, EstadoAnimico.CONTENTA)
    perfil = _evaluar(perfil=perfil, marca="2026-11-24T10:00:00Z")
    assert perfil.racha_dias == 1
    perfil = _evaluar(perfil=perfil, marca="2026-11-26T10:00:01Z")
    assert perfil.racha_dias == 3
    assert perfil.ultimo_animo == EstadoAnimico.RADIANTE
    assert perfil.xp_total == 10 + 10 + 25


def test_estado_critico_reinicia_la_racha_pero_no_la_xp():
    perfil = PerfilGamificacion("p1", xp_total=200, racha_dias=5, racha_desde="2026-11-18T10:00:00Z")
    perfil = _evaluar({**OPTIMO, "humedad": 10.0, "temperatura": 5.0}, perfil=perfil)
    assert (perfil.racha_dias, perfil.racha_desde) == (0, None)
    assert perfil.xp_total == 170


def test_motor_es_puro_no_modifica_el_perfil_recibido():
    original = PerfilGamificacion("p1", xp_total=5)
    _evaluar(perfil=original)
    assert original.xp_total == 5


def test_como_dict_compacto_y_completo():
    perfil = PerfilGamificacion("p1", xp_total=200, ultimo_animo=EstadoAnimico.SEDIENTA)
    assert set(perfil.como_dict(compacto=True)) == {"estado", "cara", "mensaje", "nivel", "xp"}
    completo = perfil.como_dict()
    assert completo["nivel"] == 2 and completo["nivel_nombre"] == "Plántula"
    assert (completo["xp_nivel_actual"], completo["xp_siguiente_nivel"]) == (151, 451)
    assert PerfilGamificacion("p1", xp_total=3000).como_dict()["xp_siguiente_nivel"] is None


# --- Adaptador SQLite -----------------------------------------------------------------------------

def test_adaptador_guarda_actualiza_y_lee_el_perfil(tmp_path):
    ruta = str(tmp_path / "g.db")
    inicializar_bd(ruta, datos_demo=True)
    adaptador = BdGamificacionAdapter(ruta)
    assert adaptador.obtener_perfil("planta-01") is None

    perfil = PerfilGamificacion("planta-01", xp_total=60, racha_dias=1, racha_desde="2026-11-23T10:00:00Z",
                                ultimo_animo=EstadoAnimico.AGRADECIDA, ultima_actualizacion="2026-11-23T10:00:00Z")
    adaptador.guardar_perfil(perfil)
    assert adaptador.obtener_perfil("planta-01") == perfil

    adaptador.guardar_perfil(PerfilGamificacion("planta-01", xp_total=70))
    assert adaptador.obtener_perfil("planta-01").xp_total == 70


def test_tabla_se_crea_en_una_base_que_ya_existia(tmp_path):
    ruta = str(tmp_path / "vieja.db")
    inicializar_bd(ruta)
    with sqlite3.connect(ruta) as con:
        con.execute("DROP TABLE gamificacion")          # como una matera.db de antes del Gotchi
    inicializar_bd(ruta)                                # lo que hace create_app al arrancar
    with sqlite3.connect(ruta) as con:
        assert con.execute("SELECT COUNT(*) FROM gamificacion").fetchone() == (0,)


# --- Casos de uso ---------------------------------------------------------------------------------

@pytest.fixture
def plantas():
    repo = FakePlantas()
    repo.guardar_planta(Planta("planta-01", "Sansevieria", "sansevieria", "usr-ana", "esp32-01"))
    return repo


def test_registrar_lectura_actualiza_el_gotchi_y_lo_notifica(plantas):
    gam, noti = FakeGamificacion(), FakeNotificadorTiempoReal()
    caso = RegistrarLectura(FakeTablaReferencia(), plantas, FakeHistorialLecturas(), notificador=noti, gamificacion=gam)
    resultado = caso.registrar_con_gotchi("esp32-01", OPTIMO, "2026-11-23T10:00:00Z")
    assert resultado.gotchi.ultimo_animo == EstadoAnimico.CONTENTA
    assert gam.perfiles["planta-01"].xp_total == 10
    assert len(noti.eventos_telemetria) == 1


def test_registrar_lectura_detecta_riego_con_la_lectura_anterior(plantas):
    caso = RegistrarLectura(FakeTablaReferencia(), plantas, FakeHistorialLecturas(), gamificacion=FakeGamificacion())
    caso.registrar("esp32-01", {**OPTIMO, "humedad": 20.0}, "2026-11-23T10:00:00Z")
    resultado = caso.registrar_con_gotchi("esp32-01", {**OPTIMO, "humedad": 42.0}, "2026-11-23T10:00:10Z")
    assert resultado.gotchi.ultimo_animo == EstadoAnimico.AGRADECIDA


def test_si_falla_la_gamificacion_la_lectura_igual_se_guarda(plantas):
    class Rota(FakeGamificacion):
        def guardar_perfil(self, perfil):
            raise RuntimeError("disco lleno")

    historial = FakeHistorialLecturas()
    caso = RegistrarLectura(FakeTablaReferencia(), plantas, historial, gamificacion=Rota())
    resultado = caso.registrar_con_gotchi("esp32-01", OPTIMO, "2026-11-23T10:00:00Z")
    assert resultado.gotchi is None
    assert len(historial.registros) == 1


def test_consultar_gotchi_aplica_propiedad_y_da_perfil_nuevo(plantas):
    caso = ConsultarGotchi(plantas, FakeGamificacion())
    assert caso.consultar_gotchi("usr-ana", "planta-01").xp_total == 0
    with pytest.raises(AccesoNoAutorizadoPlantaError):
        caso.consultar_gotchi("usr-carlos", "planta-01")


# --- Vinculación por QR iniciada por el dispositivo -----------------------------------------------

def _autorizador(plantas, sesiones):
    return AutorizarSesionQR(sesiones, plantas=plantas, emisor_token=FakeEmisorToken())


def test_sesion_creada_por_el_dispositivo_reasigna_la_planta_a_ese_dispositivo(plantas):
    sesiones = FakeSesionesQR()
    sesion = GenerarSesionQR(sesiones).generar_sesion_qr(dispositivo_id="esp32-A1B2C3")
    resultado = _autorizador(plantas, sesiones).autorizar_sesion_qr(sesion.id, "usr-ana", planta_id="planta-01")
    assert resultado.estado == EstadoSesionQR.AUTORIZADA
    assert resultado.dispositivo_id == "esp32-A1B2C3"
    assert resultado.token == "fake-jwt-disp-esp32-A1B2C3"
    assert plantas.obtener_planta_por_id("planta-01").dispositivo_id == "esp32-A1B2C3"


def test_al_mover_el_dispositivo_la_otra_planta_del_usuario_queda_libre(plantas):
    plantas.guardar_planta(Planta("planta-02", "Helecho", "helecho", "usr-ana", "esp32-A1B2C3"))
    sesiones = FakeSesionesQR()
    sesion = GenerarSesionQR(sesiones).generar_sesion_qr(dispositivo_id="esp32-A1B2C3")
    _autorizador(plantas, sesiones).autorizar_sesion_qr(sesion.id, "usr-ana", planta_id="planta-01")
    assert plantas.obtener_planta_por_dispositivo("esp32-A1B2C3").id == "planta-01"
    assert plantas.obtener_planta_por_id("planta-02").dispositivo_id == "libre-planta-02"


def test_no_se_le_quita_el_dispositivo_a_una_planta_de_otro_usuario(plantas):
    plantas.guardar_planta(Planta("planta-02", "Helecho", "helecho", "usr-carlos", "esp32-A1B2C3"))
    sesiones = FakeSesionesQR()
    sesion = GenerarSesionQR(sesiones).generar_sesion_qr(dispositivo_id="esp32-A1B2C3")
    with pytest.raises(DispositivoYaVinculadoError):
        _autorizador(plantas, sesiones).autorizar_sesion_qr(sesion.id, "usr-ana", planta_id="planta-01")
    assert plantas.obtener_planta_por_id("planta-02").dispositivo_id == "esp32-A1B2C3"


# --- API ------------------------------------------------------------------------------------------

@pytest.fixture
def app(tmp_path):
    aplicacion = create_app(ruta_bd=str(tmp_path / "api.db"), datos_demo=False)
    aplicacion.config["TESTING"] = True
    return aplicacion


def _usuario_con_planta(client, dispositivo="esp32-g-01"):
    sesion = client.post("/api/auth/registro", json={
        "nombre": "Esteban", "email": "e@matera.edu.co", "password": "password123"}).get_json()
    cabecera = {"Authorization": f"Bearer {sesion['token']}"}
    registrada = client.post("/api/plantas", headers=cabecera, json={
        "nombre": "Sansevieria", "especie": "sansevieria", "dispositivo_id": dispositivo}).get_json()
    token_disp = {"Authorization": f"Bearer {registrada['token_dispositivo']}"}
    return cabecera, token_disp, registrada["planta"]["id"], sesion["usuario"]["id"]


def _enviar(client, token_disp, humedad=30.0, marca="2026-11-23T10:00:00Z", dispositivo="esp32-g-01"):
    return client.post(f"/api/dispositivos/{dispositivo}/lecturas", headers=token_disp, json={
        "humedad": humedad, "luz": 500.0, "temperatura": 22.0, "marca_tiempo": marca})


def test_201_del_dispositivo_trae_gotchi_compacto(app):
    client = app.test_client()
    _, token_disp, _, _ = _usuario_con_planta(client)
    resp = _enviar(client, token_disp)
    assert resp.status_code == 201
    gotchi = resp.get_json()["gotchi"]
    assert set(gotchi) == {"estado", "cara", "mensaje", "nivel", "xp"}
    assert gotchi["estado"] == "CONTENTA" and gotchi["xp"] == 10 and gotchi["cara"].isascii()


def test_riego_en_la_api_da_agradecida(app):
    client = app.test_client()
    _, token_disp, _, _ = _usuario_con_planta(client)
    _enviar(client, token_disp, humedad=20.0, marca="2026-11-23T10:00:00Z")
    resp = _enviar(client, token_disp, humedad=45.0, marca="2026-11-23T10:00:10Z")
    assert resp.get_json()["gotchi"]["estado"] == "AGRADECIDA"


def test_get_gotchi_completo_requiere_ser_el_dueno(app):
    client = app.test_client()
    cabecera, token_disp, planta_id, _ = _usuario_con_planta(client)

    nuevo = client.get(f"/api/plantas/{planta_id}/gotchi", headers=cabecera)
    assert nuevo.status_code == 200 and nuevo.get_json()["xp"] == 0   # aún sin lecturas

    _enviar(client, token_disp)
    datos = client.get(f"/api/plantas/{planta_id}/gotchi", headers=cabecera).get_json()
    assert datos["xp"] == 10 and datos["emoji"] and datos["nivel_nombre"] == "Semilla"

    assert client.get(f"/api/plantas/{planta_id}/gotchi").status_code == 401
    otro = client.post("/api/auth/registro", json={
        "nombre": "Otro", "email": "o@matera.edu.co", "password": "password123"}).get_json()
    assert client.get(f"/api/plantas/{planta_id}/gotchi",
                      headers={"Authorization": f"Bearer {otro['token']}"}).status_code == 403


def test_el_evento_websocket_de_telemetria_incluye_el_gotchi(app):
    client = app.test_client()
    cabecera, token_disp, _, _ = _usuario_con_planta(client)
    ws = app.socketio.test_client(app)
    ws.emit("unirse_canal_usuario", {"token_usuario": cabecera["Authorization"].split()[1]})
    ws.get_received()
    _enviar(client, token_disp)
    eventos = [e for e in ws.get_received() if e["name"] == "telemetria_actualizada"]
    assert eventos and eventos[0]["args"][0]["gotchi"]["estado"] == "CONTENTA"


def test_flujo_qr_iniciado_por_el_esp32_reasigna_dispositivo_y_deja_reportar(app):
    client = app.test_client()
    cabecera, _, planta_id, _ = _usuario_con_planta(client)
    sesion = client.post("/api/auth/qr/generar", json={"dispositivo_id": "esp32-A1B2C3"}).get_json()
    resp = client.post(f"/api/auth/qr/{sesion['session_id']}/autorizar", headers=cabecera, json={"planta_id": planta_id})
    assert resp.status_code == 200 and resp.get_json()["dispositivo_id"] == "esp32-A1B2C3"
    token = client.get(f"/api/auth/qr/{sesion['session_id']}").get_json()["token"]
    nueva = _enviar(client, {"Authorization": f"Bearer {token}"}, dispositivo="esp32-A1B2C3")
    assert nueva.status_code == 201 and nueva.get_json()["gotchi"]


def test_panel_web_se_sirve_desde_flask(app):
    client = app.test_client()
    assert b"<html" in client.get("/").data.lower()
    assert client.get("/js/config.js").status_code == 200
    assert client.get("/css/style.css").status_code == 200


def test_simulador_regar_sube_la_humedad_de_golpe():
    import random
    import simulador_esp32 as sim

    matera = sim.MateraSimulada(random.Random(1), 30, 1800, humedad_inicial=40.0)
    matera.leer()
    antes = matera.humedad
    matera.riego_pendiente = True
    matera.leer()
    assert matera.regada and matera.humedad - antes > 15
