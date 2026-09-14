"""
Entidades y Objetos de Valor del Dominio.
Contienen la estructura de datos pura y reglas de invariantes físicas.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
from src.domain.exceptions import ParametroInvalidoError


class EstadoParametro(str, Enum):
    BAJO = "BAJO"
    OPTIMO = "OPTIMO"
    ALTO = "ALTO"


class EstadoPlanta(str, Enum):
    SALUDABLE = "SALUDABLE"
    EN_RIESGO = "EN_RIESGO"
    CRITICO = "CRITICO"


@dataclass(frozen=True)
class RangoParametro:
    """Rango de referencia óptimo para una variable ambiental."""
    minimo: float
    maximo: float
    unidad: str

    def __post_init__(self):
        if self.minimo > self.maximo:
            raise ValueError(f"El mínimo ({self.minimo}) no puede ser mayor al máximo ({self.maximo}).")


@dataclass(frozen=True)
class Especie:
    """Representa una especie botánica con sus rangos de referencia ideales."""
    nombre: str
    rango_humedad: RangoParametro
    rango_luz: RangoParametro
    rango_temperatura: RangoParametro


@dataclass(frozen=True)
class Medicion:
    """
    Medición ambiental tomada por sensores o ingresada por el usuario.
    Valida que los valores correspondan a rangos físicamente posibles (RF6).
    """
    especie: str
    humedad: float
    luz: float
    temperatura: float

    # Constantes de límites físicos posibles en la Tierra para cultivo botánico
    HUMEDAD_MIN_FISICA = 0.0
    HUMEDAD_MAX_FISICA = 100.0
    LUZ_MIN_FISICA = 0.0
    LUZ_MAX_FISICA = 150000.0  # lux (luz solar directa extrema a mediodía ~100k-130k lux)
    TEMP_MIN_FISICA = -50.0   # °C
    TEMP_MAX_FISICA = 80.0    # °C

    def __post_init__(self):
        if not self.especie or not isinstance(self.especie, str) or not self.especie.strip():
            raise ParametroInvalidoError("especie", "La especie es obligatoria y no puede estar vacía.")

        if not isinstance(self.humedad, (int, float)):
            raise ParametroInvalidoError("humedad", "El valor de humedad debe ser numérico.")
        if not (self.HUMEDAD_MIN_FISICA <= self.humedad <= self.HUMEDAD_MAX_FISICA):
            raise ParametroInvalidoError(
                "humedad",
                f"Humedad de {self.humedad}% está fuera del rango físicamente posible ({self.HUMEDAD_MIN_FISICA}% - {self.HUMEDAD_MAX_FISICA}%)."
            )

        if not isinstance(self.luz, (int, float)):
            raise ParametroInvalidoError("luz", "El valor de luz debe ser numérico.")
        if not (self.LUZ_MIN_FISICA <= self.luz <= self.LUZ_MAX_FISICA):
            raise ParametroInvalidoError(
                "luz",
                f"Nivel de luz de {self.luz} lux está fuera del rango físicamente posible ({self.LUZ_MIN_FISICA} - {self.LUZ_MAX_FISICA} lux)."
            )

        if not isinstance(self.temperatura, (int, float)):
            raise ParametroInvalidoError("temperatura", "El valor de temperatura debe ser numérico.")
        if not (self.TEMP_MIN_FISICA <= self.temperatura <= self.TEMP_MAX_FISICA):
            raise ParametroInvalidoError(
                "temperatura",
                f"Temperatura de {self.temperatura}°C está fuera del rango físicamente posible ({self.TEMP_MIN_FISICA}°C - {self.TEMP_MAX_FISICA}°C)."
            )


@dataclass(frozen=True)
class ParametroEvaluado:
    """Resultado de la evaluación individual de un parámetro contra el rango de referencia."""
    nombre: str
    valor: float
    unidad: str
    rango_optimo: Tuple[float, float]
    estado: EstadoParametro


@dataclass(frozen=True)
class Diagnostico:
    """Diagnóstico integral del estado de la planta con recomendaciones."""
    especie: str
    estado: EstadoPlanta
    parametros: List[ParametroEvaluado]
    recomendaciones: List[str]
