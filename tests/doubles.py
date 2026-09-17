"""
Dobles de prueba de las abstracciones del dominio.
Permiten ejercitar las reglas de negocio sin infraestructura: ni archivos,
ni base de datos, ni servidor web (evidencia de RA4).
"""
from typing import Dict, List, Optional, Tuple

from src.domain.entities import Especie, RangoParametro
from src.domain.repositories import EspecieRepository


def especie_de_prueba(
    nombre: str,
    humedad: Tuple[float, float],
    luz: Tuple[float, float],
    temperatura: Tuple[float, float],
) -> Especie:
    """Constructor auxiliar para armar especies de prueba de forma legible."""
    return Especie(
        nombre=nombre,
        rangos={
            "humedad": RangoParametro(minimo=humedad[0], maximo=humedad[1], unidad="%"),
            "luz": RangoParametro(minimo=luz[0], maximo=luz[1], unidad="lux"),
            "temperatura": RangoParametro(minimo=temperatura[0], maximo=temperatura[1], unidad="°C"),
        },
    )


class FakeEspecieRepository(EspecieRepository):
    """
    Doble en memoria de la abstracción EspecieRepository (RA5).
    Sustituye a CsvEspecieRepository sin que el dominio ni los casos de uso
    se enteren: esa sustituibilidad es la evidencia ejecutable de LSP y DIP.
    """

    def __init__(self, catalogo: Optional[Dict[str, Especie]] = None):
        self._catalogo = catalogo or {
            "sansevieria": especie_de_prueba("sansevieria", (20.0, 45.0), (200.0, 1500.0), (15.0, 29.0)),
            "helecho": especie_de_prueba("helecho", (60.0, 85.0), (150.0, 800.0), (16.0, 26.0)),
        }

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        return self._catalogo.get(nombre.strip().lower())

    def obtener_todas(self) -> List[Especie]:
        return list(self._catalogo.values())
