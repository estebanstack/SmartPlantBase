"""
Pruebas unitarias de la capa de Dominio (Evidencia de RA4 y Entregable d).
Ejercita las reglas de negocio sin levantar el servidor web y sin leer archivos ni bases de datos.
Utiliza un doble de prueba (FakeEspecieRepository) que implementa la abstracción de RA5.
"""
import pytest
from typing import Dict, List, Optional

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


class FakeEspecieRepository(EspecieRepository):
    """
    Doble de prueba (Test Double / In-Memory Fake) de la abstracción EspecieRepository.
    Permite probar el dominio de forma 100% aislada, sin depender de infraestructura ni archivos.
    """

    def __init__(self, catalogo: Optional[Dict[str, Especie]] = None):
        self._catalogo = catalogo or {
            "sansevieria": Especie(
                nombre="sansevieria",
                rango_humedad=RangoParametro(minimo=20.0, maximo=45.0, unidad="%"),
                rango_luz=RangoParametro(minimo=200.0, maximo=1500.0, unidad="lux"),
                rango_temperatura=RangoParametro(minimo=15.0, maximo=29.0, unidad="°C"),
            ),
            "helecho": Especie(
                nombre="helecho",
                rango_humedad=RangoParametro(minimo=60.0, maximo=85.0, unidad="%"),
                rango_luz=RangoParametro(minimo=150.0, maximo=800.0, unidad="lux"),
                rango_temperatura=RangoParametro(minimo=16.0, maximo=26.0, unidad="°C"),
            ),
        }

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        return self._catalogo.get(nombre.strip().lower())

    def obtener_todas(self) -> List[Especie]:
        return list(self._catalogo.values())


@pytest.fixture
def fake_repo() -> EspecieRepository:
    """Fixture que provee el doble de prueba del repositorio."""
    return FakeEspecieRepository()


def test_planta_saludable_con_todos_los_parametros_en_rango_optimo(fake_repo: EspecieRepository):
    """
    Caso 1: Todos los parámetros están dentro de los rangos óptimos.
    El estado derivado debe ser SALUDABLE y sin recomendaciones.
    """
    especie = fake_repo.obtener_por_nombre("sansevieria")
    assert especie is not None

    medicion = Medicion(
        especie="sansevieria",
        humedad=32.5,     # Óptimo: 20-45%
        luz=850.0,        # Óptimo: 200-1500 lux
        temperatura=21.0  # Óptimo: 15-29°C
    )

    diagnostico: Diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.SALUDABLE
    assert len(diagnostico.recomendaciones) == 0
    assert all(param.estado == EstadoParametro.OPTIMO for param in diagnostico.parametros)


def test_un_parametro_bajo_deriva_en_riesgo_con_recomendacion(fake_repo: EspecieRepository):
    """
    Caso 2: Un solo parámetro está por debajo del mínimo (desviación = 1).
    El estado derivado debe ser EN_RIESGO y debe incluir la recomendación correspondiente.
    """
    especie = fake_repo.obtener_por_nombre("sansevieria")
    assert especie is not None

    medicion = Medicion(
        especie="sansevieria",
        humedad=10.0,     # BAJO (mínimo es 20%)
        luz=850.0,        # Óptimo
        temperatura=21.0  # Óptimo
    )

    diagnostico: Diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert len(diagnostico.recomendaciones) == 1
    assert "por debajo del rango recomendado: riegue moderadamente" in diagnostico.recomendaciones[0]

    param_humedad = next(p for p in diagnostico.parametros if p.nombre == "humedad")
    assert param_humedad.estado == EstadoParametro.BAJO


def test_un_parametro_alto_deriva_en_riesgo_con_recomendacion(fake_repo: EspecieRepository):
    """
    Caso 3: Un solo parámetro está por encima del máximo (desviación = 1).
    El estado derivado debe ser EN_RIESGO y debe sugerir ventilación o sombra.
    """
    especie = fake_repo.obtener_por_nombre("sansevieria")
    assert especie is not None

    medicion = Medicion(
        especie="sansevieria",
        humedad=30.0,     # Óptimo
        luz=850.0,        # Óptimo
        temperatura=35.0  # ALTO (máximo es 29°C)
    )

    diagnostico: Diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.EN_RIESGO
    assert len(diagnostico.recomendaciones) == 1
    assert "temperatura ambiental es excesiva" in diagnostico.recomendaciones[0]

    param_temp = next(p for p in diagnostico.parametros if p.nombre == "temperatura")
    assert param_temp.estado == EstadoParametro.ALTO


def test_multiples_parametros_desviados_derivan_estado_critico(fake_repo: EspecieRepository):
    """
    Caso 4: Dos o más parámetros fuera de rango (desviaciones >= 2).
    La regla de agregación debe clasificar a la planta en estado CRITICO.
    """
    especie = fake_repo.obtener_por_nombre("helecho")
    assert especie is not None

    medicion = Medicion(
        especie="helecho",
        humedad=40.0,     # BAJO (óptimo 60-85%)
        luz=1200.0,       # ALTO (óptimo 150-800 lux)
        temperatura=20.0  # Óptimo (16-26°C)
    )

    diagnostico: Diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

    assert diagnostico.estado == EstadoPlanta.CRITICO
    assert len(diagnostico.recomendaciones) == 2
    estados = {p.nombre: p.estado for p in diagnostico.parametros}
    assert estados["humedad"] == EstadoParametro.BAJO
    assert estados["luz"] == EstadoParametro.ALTO
    assert estados["temperatura"] == EstadoParametro.OPTIMO


def test_medicion_con_humedad_fisicamente_imposible_lanza_error():
    """
    Caso 5: La medición rechaza valores fuera de las leyes de la física (% negativo o >100).
    Debe lanzar ParametroInvalidoError con el campo afectado (RF6).
    """
    with pytest.raises(ParametroInvalidoError) as exc_info_negativa:
        Medicion(especie="sansevieria", humedad=-5.0, luz=500.0, temperatura=22.0)
    assert exc_info_negativa.value.campo == "humedad"

    with pytest.raises(ParametroInvalidoError) as exc_info_exceso:
        Medicion(especie="sansevieria", humedad=105.0, luz=500.0, temperatura=22.0)
    assert exc_info_exceso.value.campo == "humedad"


def test_medicion_con_luz_o_temperatura_imposibles_lanza_error():
    """
    Caso 6: La medición rechaza lux negativo o temperatura inverosímil.
    Debe lanzar ParametroInvalidoError (RF6).
    """
    with pytest.raises(ParametroInvalidoError) as exc_luz:
        Medicion(especie="sansevieria", humedad=50.0, luz=-10.0, temperatura=22.0)
    assert exc_luz.value.campo == "luz"

    with pytest.raises(ParametroInvalidoError) as exc_temp:
        Medicion(especie="sansevieria", humedad=50.0, luz=500.0, temperatura=150.0)
    assert exc_temp.value.campo == "temperatura"


def test_doble_de_prueba_sustituible_y_aislamiento_total(fake_repo: EspecieRepository):
    """
    Caso 7: Verifica que el doble de prueba sustituye a la abstracción sin conocimiento
    de persistencia (LSP y RA4). Si la especie no existe en el catálogo, retorna None.
    """
    resultado = fake_repo.obtener_por_nombre("orquidea_desconocida")
    assert resultado is None

    especies = fake_repo.obtener_todas()
    assert len(especies) == 2
