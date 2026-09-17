"""
Pruebas unitarias de la capa de Dominio (evidencia de RA4 y del entregable d).
Ejercitan las reglas de negocio sin levantar el servidor web y sin leer archivos
ni bases de datos, usando el doble de prueba de tests/doubles.py.
"""
import pytest

from src.domain.entities import (
    Diagnostico,
    Especie,
    EstadoParametro,
    EstadoPlanta,
    Medicion,
    RangoParametro,
)
from src.domain.exceptions import ParametroInvalidoError
from src.domain.repositories import EspecieRepository
from src.domain.rules import EvaluadorDiagnostico
from tests.doubles import FakeEspecieRepository


@pytest.fixture
def fake_repo() -> EspecieRepository:
    """Fixture que provee el doble de prueba del repositorio."""
    return FakeEspecieRepository()


def test_planta_saludable_con_todos_los_parametros_en_rango_optimo(fake_repo: EspecieRepository):
    """
    Caso 1: todos los parámetros dentro de los rangos óptimos.
    El estado derivado debe ser SALUDABLE y sin recomendaciones.
    """
    especie = fake_repo.obtener_por_nombre("sansevieria")
    medicion = Medicion(
        especie="sansevieria",
        valores={"humedad": 32.5, "luz": 850.0, "temperatura": 21.0},
    )

    diagnostico: Diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.SALUDABLE
    assert len(diagnostico.recomendaciones) == 0
    assert all(p.estado == EstadoParametro.OPTIMO for p in diagnostico.parametros)


def test_un_parametro_bajo_deriva_en_riesgo_con_recomendacion(fake_repo: EspecieRepository):
    """Caso 2: una sola desviación por debajo del mínimo -> EN_RIESGO con su recomendación."""
    especie = fake_repo.obtener_por_nombre("sansevieria")
    medicion = Medicion(
        especie="sansevieria",
        valores={"humedad": 10.0, "luz": 850.0, "temperatura": 21.0},
    )

    diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert len(diagnostico.recomendaciones) == 1
    assert "por debajo del rango recomendado: riegue moderadamente" in diagnostico.recomendaciones[0]
    param_humedad = next(p for p in diagnostico.parametros if p.nombre == "humedad")
    assert param_humedad.estado == EstadoParametro.BAJO


def test_un_parametro_alto_deriva_en_riesgo_con_recomendacion(fake_repo: EspecieRepository):
    """Caso 3: una sola desviación por encima del máximo -> EN_RIESGO."""
    especie = fake_repo.obtener_por_nombre("sansevieria")
    medicion = Medicion(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 850.0, "temperatura": 35.0},
    )

    diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert len(diagnostico.recomendaciones) == 1
    assert "temperatura ambiental es excesiva" in diagnostico.recomendaciones[0]
    param_temp = next(p for p in diagnostico.parametros if p.nombre == "temperatura")
    assert param_temp.estado == EstadoParametro.ALTO


def test_multiples_parametros_desviados_derivan_estado_critico(fake_repo: EspecieRepository):
    """Caso 4: dos o más desviaciones -> CRITICO (regla de agregación RF3)."""
    especie = fake_repo.obtener_por_nombre("helecho")
    medicion = Medicion(
        especie="helecho",
        valores={"humedad": 40.0, "luz": 1200.0, "temperatura": 20.0},
    )

    diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.CRITICO
    assert len(diagnostico.recomendaciones) == 2
    estados = {p.nombre: p.estado for p in diagnostico.parametros}
    assert estados["humedad"] == EstadoParametro.BAJO
    assert estados["luz"] == EstadoParametro.ALTO
    assert estados["temperatura"] == EstadoParametro.OPTIMO


def test_valores_en_los_extremos_del_rango_se_consideran_optimos(fake_repo: EspecieRepository):
    """
    Caso 5: el rango de referencia es cerrado.
    Un valor exactamente igual al mínimo o al máximo se clasifica como OPTIMO.
    """
    especie = fake_repo.obtener_por_nombre("sansevieria")  # humedad 20-45, luz 200-1500, temp 15-29
    medicion = Medicion(
        especie="sansevieria",
        valores={"humedad": 20.0, "luz": 1500.0, "temperatura": 15.0},
    )

    diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.SALUDABLE
    assert all(p.estado == EstadoParametro.OPTIMO for p in diagnostico.parametros)


def test_medicion_con_humedad_fisicamente_imposible_lanza_error():
    """Caso 6: la medición rechaza porcentajes de humedad imposibles (RF6)."""
    with pytest.raises(ParametroInvalidoError) as negativa:
        Medicion(especie="sansevieria", valores={"humedad": -5.0, "luz": 500.0, "temperatura": 22.0})
    assert negativa.value.campo == "humedad"

    with pytest.raises(ParametroInvalidoError) as exceso:
        Medicion(especie="sansevieria", valores={"humedad": 105.0, "luz": 500.0, "temperatura": 22.0})
    assert exceso.value.campo == "humedad"


def test_medicion_con_luz_o_temperatura_imposibles_lanza_error():
    """Caso 7: la medición rechaza lux negativos y temperaturas inverosímiles (RF6)."""
    with pytest.raises(ParametroInvalidoError) as luz:
        Medicion(especie="sansevieria", valores={"humedad": 50.0, "luz": -10.0, "temperatura": 22.0})
    assert luz.value.campo == "luz"

    with pytest.raises(ParametroInvalidoError) as temp:
        Medicion(especie="sansevieria", valores={"humedad": 50.0, "luz": 500.0, "temperatura": 150.0})
    assert temp.value.campo == "temperatura"


def test_medicion_rechaza_parametros_no_reconocidos_y_valores_no_numericos():
    """
    Caso 8: la entidad de dominio no es un diccionario crudo.
    Rechaza variables desconocidas y valores no numéricos antes de construirse (RA6).
    """
    with pytest.raises(ParametroInvalidoError) as desconocido:
        Medicion(especie="sansevieria", valores={"salinidad": 3.0})
    assert desconocido.value.campo == "salinidad"

    with pytest.raises(ParametroInvalidoError) as no_numerico:
        Medicion(especie="sansevieria", valores={"humedad": "mucha", "luz": 500.0, "temperatura": 22.0})
    assert no_numerico.value.campo == "humedad"


def test_el_evaluador_recorre_los_parametros_que_declara_la_especie():
    """
    Caso 9 (evidencia de OCP): el evaluador no enumera parámetros.
    Una especie que declara sólo dos variables se diagnostica correctamente
    sin ninguna modificación de EvaluadorDiagnostico.
    """
    especie_parcial = Especie(
        nombre="musgo",
        rangos={
            "humedad": RangoParametro(minimo=70.0, maximo=95.0, unidad="%"),
            "luz": RangoParametro(minimo=50.0, maximo=400.0, unidad="lux"),
        },
    )
    medicion = Medicion(especie="musgo", valores={"humedad": 80.0, "luz": 900.0})

    diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie_parcial)

    assert len(diagnostico.parametros) == 2
    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert [p.nombre for p in diagnostico.parametros] == ["humedad", "luz"]


def test_falta_un_parametro_que_la_especie_exige(fake_repo: EspecieRepository):
    """Caso 10: si la especie declara un rango que la medición no trae, el dominio falla (RF6)."""
    especie = fake_repo.obtener_por_nombre("sansevieria")
    medicion = Medicion(especie="sansevieria", valores={"humedad": 30.0, "luz": 500.0})

    with pytest.raises(ParametroInvalidoError) as error:
        EvaluadorDiagnostico.evaluar(medicion, especie)
    assert error.value.campo == "temperatura"


def test_doble_de_prueba_sustituible_y_aislamiento_total(fake_repo: EspecieRepository):
    """Caso 11: el doble sustituye a la abstracción sin conocimiento de persistencia (LSP, RA4)."""
    assert fake_repo.obtener_por_nombre("orquidea_desconocida") is None
    assert len(fake_repo.obtener_todas()) == 2
