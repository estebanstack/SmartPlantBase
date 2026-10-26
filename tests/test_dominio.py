"""
Pruebas unitarias puras del Núcleo de Dominio (Arquitectura Hexagonal).
Ejercita las entidades, reglas de negocio y casos de uso (puertos de entrada)
usando dobles en memoria (tests/fakes.py) sin tocar archivos, SQLite ni Flask.
"""
from datetime import datetime
import pytest

from matera.dominio.excepciones import (
    AccesoNoAutorizadoPlantaError,
    CredencialesInvalidasError,
    DispositivoNoEncontradoError,
    EspecieNoSoportadaError,
    ParametroInvalidoError,
    PlantaNoEncontradaError,
    UsuarioYaExisteError,
)
from matera.dominio.modelo import (
    Diagnostico,
    EstadoParametro,
    EstadoPlanta,
    Lectura,
    Planta,
)
from matera.dominio.validador import ServicioMateraDominio, ValidadorDeEstado
from tests.fakes import (
    FakeEmisorToken,
    FakeHistorialLecturas,
    FakeTablaReferencia,
    FakeUsuariosPlantas,
)


@pytest.fixture
def fake_tabla():
    return FakeTablaReferencia()


@pytest.fixture
def fake_historial():
    return FakeHistorialLecturas()


@pytest.fixture
def fake_usuarios_plantas():
    repo = FakeUsuariosPlantas()
    # Pre-cargar usuario dueño y planta asociada a un ESP32
    planta = Planta(
        id="planta-01",
        nombre="Sansevieria de Sala",
        especie="sansevieria",
        usuario_id="usr-ana",
        dispositivo_id="esp32-01",
    )
    repo.guardar_planta(planta)
    return repo


@pytest.fixture
def fake_emisor():
    return FakeEmisorToken()


@pytest.fixture
def servicio_dominio(fake_tabla, fake_historial, fake_usuarios_plantas, fake_emisor):
    return ServicioMateraDominio(
        tabla_referencia=fake_tabla,
        historial_lecturas=fake_historial,
        usuarios_plantas=fake_usuarios_plantas,
        emisor_token=fake_emisor,
    )


# -----------------------------------------------------------------------------
# 1. Pruebas de Entidad Lectura e Invariantes Físicas
# -----------------------------------------------------------------------------

def test_lectura_incluye_timestamp_utc_y_marca_tiempo_por_defecto():
    """Crítico para Commit 4: Lectura incluye timestamp: datetime y marca_tiempo ISO."""
    lectura = Lectura(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
    )
    assert isinstance(lectura.timestamp, datetime)
    assert isinstance(lectura.marca_tiempo, str)
    assert len(lectura.marca_tiempo) > 10


def test_lectura_rechaza_humedad_negativa():
    with pytest.raises(ParametroInvalidoError) as exc_info:
        Lectura(
            especie="sansevieria",
            valores={"humedad": -5.0, "luz": 500.0, "temperatura": 22.0},
        )
    assert "humedad" in exc_info.value.campo


def test_lectura_rechaza_temperatura_fisicamente_imposible():
    with pytest.raises(ParametroInvalidoError) as exc_info:
        Lectura(
            especie="sansevieria",
            valores={"humedad": 30.0, "luz": 500.0, "temperatura": 99.0},
        )
    assert "temperatura" in exc_info.value.campo


def test_lectura_rechaza_valor_booleano_o_no_numerico():
    with pytest.raises(ParametroInvalidoError):
        Lectura(
            especie="sansevieria",
            valores={"humedad": True, "luz": 500.0, "temperatura": 22.0},
        )


# -----------------------------------------------------------------------------
# 2. Pruebas del Evaluador Botánico (ValidadorDeEstado)
# -----------------------------------------------------------------------------

def test_planta_saludable_con_todos_los_parametros_en_rango_optimo(fake_tabla):
    especie = fake_tabla.obtener_por_nombre("sansevieria")
    lectura = Lectura(
        especie="sansevieria",
        valores={"humedad": 32.5, "luz": 850.0, "temperatura": 21.0},
    )

    diagnostico: Diagnostico = ValidadorDeEstado.evaluar(lectura, especie)

    assert diagnostico.estado == EstadoPlanta.SALUDABLE
    assert len(diagnostico.recomendaciones) == 0
    assert all(p.estado == EstadoParametro.OPTIMO for p in diagnostico.parametros)


def test_un_parametro_bajo_deriva_en_riesgo(fake_tabla):
    especie = fake_tabla.obtener_por_nombre("sansevieria")
    lectura = Lectura(
        especie="sansevieria",
        valores={"humedad": 10.0, "luz": 850.0, "temperatura": 21.0},
    )

    diagnostico = ValidadorDeEstado.evaluar(lectura, especie)

    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert len(diagnostico.recomendaciones) == 1
    assert "por debajo del rango recomendado" in diagnostico.recomendaciones[0]


def test_multiples_desviaciones_derivan_estado_critico(fake_tabla):
    especie = fake_tabla.obtener_por_nombre("helecho")
    lectura = Lectura(
        especie="helecho",
        valores={"humedad": 40.0, "luz": 1200.0, "temperatura": 20.0},
    )

    diagnostico = ValidadorDeEstado.evaluar(lectura, especie)

    assert diagnostico.estado == EstadoPlanta.CRITICO
    assert len(diagnostico.recomendaciones) == 2


def test_valores_en_extremos_son_optimos(fake_tabla):
    especie = fake_tabla.obtener_por_nombre("sansevieria")
    # min humedad: 20.0, max humedad: 45.0
    lectura = Lectura(
        especie="sansevieria",
        valores={"humedad": 20.0, "luz": 200.0, "temperatura": 15.0},
    )
    diagnostico = ValidadorDeEstado.evaluar(lectura, especie)
    assert diagnostico.estado == EstadoPlanta.SALUDABLE


# -----------------------------------------------------------------------------
# 3. Pruebas de Puertos de Entrada con ServicioMateraDominio
# -----------------------------------------------------------------------------

def test_puerto_validar_lectura_y_listar_especies(servicio_dominio):
    # R1: ValidarLecturaPort
    diag = servicio_dominio.validar(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
    )
    assert diag.estado == EstadoPlanta.SALUDABLE

    especies = servicio_dominio.listar_especies()
    assert len(especies) >= 3


def test_puerto_validar_especie_inexistente_lanza_error(servicio_dominio):
    with pytest.raises(EspecieNoSoportadaError):
        servicio_dominio.validar(
            especie="especie_desconocida",
            valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        )


def test_puerto_registrar_lectura_dispositivo(servicio_dominio, fake_historial):
    # R2 y R5: RegistrarLecturaPort
    diag = servicio_dominio.registrar(
        dispositivo_id="esp32-01",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        marca_tiempo="2026-10-26T16:00:00Z",
    )
    assert diag.estado == EstadoPlanta.SALUDABLE
    assert len(fake_historial.registros) == 1
    assert fake_historial.registros[0]["planta_id"] == "planta-01"


def test_puerto_registrar_lectura_dispositivo_desconocido_falla(servicio_dominio):
    with pytest.raises(DispositivoNoEncontradoError):
        servicio_dominio.registrar(
            dispositivo_id="esp32-inexistente",
            valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        )


def test_puerto_consultar_estado_regla_propiedad(servicio_dominio):
    # R7: Dueña legítima (usr-ana) puede consultar su planta
    estado_ana = servicio_dominio.consultar_estado(
        usuario_id="usr-ana",
        planta_id="planta-01",
    )
    assert estado_ana.planta.id == "planta-01"

    # Intruso (usr-carlos) recibe AccesoNoAutorizadoPlantaError en el dominio
    with pytest.raises(AccesoNoAutorizadoPlantaError):
        servicio_dominio.consultar_estado(
            usuario_id="usr-carlos",
            planta_id="planta-01",
        )


def test_puerto_autenticacion_usuario(servicio_dominio):
    # R7: AutenticarUsuarioPort
    reg = servicio_dominio.registrar_usuario(
        nombre="Ana María",
        email="ana@matera.edu.co",
        password="claveSegura123",
    )
    assert reg["email"] == "ana@matera.edu.co"
    assert "token" in reg

    # Intento de registro duplicado
    with pytest.raises(UsuarioYaExisteError):
        servicio_dominio.registrar_usuario(
            nombre="Ana María 2",
            email="ana@matera.edu.co",
            password="otraClave",
        )

    # Login exitoso
    login_ok = servicio_dominio.iniciar_sesion(
        email="ana@matera.edu.co",
        password="claveSegura123",
    )
    assert login_ok["usuario_id"] == reg["usuario_id"]

    # Login con contraseña errónea
    with pytest.raises(CredencialesInvalidasError):
        servicio_dominio.iniciar_sesion(
            email="ana@matera.edu.co",
            password="claveIncorrecta",
        )
