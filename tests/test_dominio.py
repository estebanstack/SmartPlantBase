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
from matera.dominio.casos_uso import (
    AutenticarUsuario,
    ConsultarEspecies,
    ConsultarEstado,
    ConsultarHistorial,
    ListarPlantas,
    RegistrarLectura,
    ValidarLectura,
)
from matera.dominio.validador import ValidadorDeEstado
from tests.fakes import (
    FakeEmisorToken,
    FakeHistorialLecturas,
    FakePlantas,
    FakeTablaReferencia,
    FakeUsuarios,
)


@pytest.fixture
def fake_tabla():
    return FakeTablaReferencia()


@pytest.fixture
def fake_historial():
    return FakeHistorialLecturas()


@pytest.fixture
def fake_plantas():
    repo = FakePlantas()
    # Planta de Ana asociada al ESP32 "esp32-01"
    repo.guardar_planta(Planta(
        id="planta-01",
        nombre="Sansevieria de Sala",
        especie="sansevieria",
        usuario_id="usr-ana",
        dispositivo_id="esp32-01",
    ))
    return repo


@pytest.fixture
def fake_usuarios():
    return FakeUsuarios()


@pytest.fixture
def fake_emisor():
    return FakeEmisorToken()


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
# 3. Pruebas de los Casos de Uso (puertos de entrada) con dobles de prueba
# -----------------------------------------------------------------------------

def test_validar_lectura_y_listar_especies(fake_tabla):
    # R1: ValidarLecturaPort y ConsultarEspeciesPort
    diag = ValidarLectura(fake_tabla).validar(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
    )
    assert diag.estado == EstadoPlanta.SALUDABLE

    especies = ConsultarEspecies(fake_tabla).listar_especies()
    assert len(especies) >= 3


def test_validar_especie_inexistente_lanza_error(fake_tabla):
    with pytest.raises(EspecieNoSoportadaError):
        ValidarLectura(fake_tabla).validar(
            especie="especie_desconocida",
            valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        )


def test_registrar_lectura_dispositivo(fake_tabla, fake_plantas, fake_historial):
    # R2 y R5: RegistrarLecturaPort
    caso_uso = RegistrarLectura(fake_tabla, fake_plantas, fake_historial)
    diag = caso_uso.registrar(
        dispositivo_id="esp32-01",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        marca_tiempo="2026-10-26T16:00:00Z",
    )
    assert diag.estado == EstadoPlanta.SALUDABLE
    assert len(fake_historial.registros) == 1
    assert fake_historial.registros[0].lectura.planta_id == "planta-01"


def test_registrar_lectura_dispositivo_desconocido_falla(fake_tabla, fake_plantas, fake_historial):
    caso_uso = RegistrarLectura(fake_tabla, fake_plantas, fake_historial)
    with pytest.raises(DispositivoNoEncontradoError):
        caso_uso.registrar(
            dispositivo_id="esp32-inexistente",
            valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        )


def test_registrar_lectura_invalida_no_se_guarda(fake_tabla, fake_plantas, fake_historial):
    # Un sensor dañado manda humedad 150 %: se rechaza y no entra al historial
    caso_uso = RegistrarLectura(fake_tabla, fake_plantas, fake_historial)
    with pytest.raises(ParametroInvalidoError):
        caso_uso.registrar(
            dispositivo_id="esp32-01",
            valores={"humedad": 150.0, "luz": 500.0, "temperatura": 22.0},
        )
    assert fake_historial.registros == []


def test_consultar_estado_regla_propiedad(fake_tabla, fake_plantas, fake_historial):
    # R7: la dueña (usr-ana) ve su planta; otro usuario recibe error de dominio
    caso_uso = ConsultarEstado(fake_tabla, fake_plantas, fake_historial)

    estado_ana = caso_uso.consultar_estado(usuario_id="usr-ana", planta_id="planta-01")
    assert estado_ana.planta.id == "planta-01"

    with pytest.raises(AccesoNoAutorizadoPlantaError):
        caso_uso.consultar_estado(usuario_id="usr-carlos", planta_id="planta-01")


def test_consultar_estado_planta_inexistente(fake_tabla, fake_plantas, fake_historial):
    caso_uso = ConsultarEstado(fake_tabla, fake_plantas, fake_historial)
    with pytest.raises(PlantaNoEncontradaError):
        caso_uso.consultar_estado(usuario_id="usr-ana", planta_id="planta-99")


def test_consultar_historial_devuelve_registros_y_aplica_propiedad(
    fake_tabla, fake_plantas, fake_historial
):
    registrar = RegistrarLectura(fake_tabla, fake_plantas, fake_historial)
    registrar.registrar("esp32-01", {"humedad": 30.0, "luz": 500.0, "temperatura": 22.0})
    registrar.registrar("esp32-01", {"humedad": 10.0, "luz": 500.0, "temperatura": 22.0})

    caso_uso = ConsultarHistorial(fake_plantas, fake_historial)
    historial = caso_uso.consultar_historial(usuario_id="usr-ana", planta_id="planta-01")

    # Más reciente primero, y cada registro trae el estado que se le calculó
    assert [r.estado for r in historial] == [EstadoPlanta.EN_RIESGO, EstadoPlanta.SALUDABLE]

    with pytest.raises(AccesoNoAutorizadoPlantaError):
        caso_uso.consultar_historial(usuario_id="usr-carlos", planta_id="planta-01")


def test_listar_plantas_solo_del_usuario(fake_plantas):
    caso_uso = ListarPlantas(fake_plantas)
    assert [p.id for p in caso_uso.listar_plantas_usuario("usr-ana")] == ["planta-01"]
    assert caso_uso.listar_plantas_usuario("usr-carlos") == []


def test_autenticacion_usuario(fake_usuarios, fake_emisor):
    # R7: AutenticarUsuarioPort
    caso_uso = AutenticarUsuario(fake_usuarios, fake_emisor)

    sesion = caso_uso.registrar_usuario(
        nombre="Ana María",
        email="ana@matera.edu.co",
        password="claveSegura123",
    )
    assert sesion.usuario.email == "ana@matera.edu.co"
    assert sesion.token

    # Registro duplicado
    with pytest.raises(UsuarioYaExisteError):
        caso_uso.registrar_usuario(nombre="Ana 2", email="ana@matera.edu.co", password="otraClave")

    # Login correcto
    login = caso_uso.iniciar_sesion(email="ana@matera.edu.co", password="claveSegura123")
    assert login.usuario.id == sesion.usuario.id

    # Contraseña equivocada
    with pytest.raises(CredencialesInvalidasError):
        caso_uso.iniciar_sesion(email="ana@matera.edu.co", password="claveIncorrecta")
