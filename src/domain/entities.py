"""
Entidades y Objetos de Valor del Dominio.
Contienen la estructura de datos pura y las reglas de invariantes físicas.

Los parámetros ambientales se modelan como una colección indexada por nombre
(no como campos fijos), de modo que incorporar una nueva variable ambiental
sea una entrada en LIMITES_FISICOS y no una modificación del evaluador (OCP).
"""
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import List, Mapping, Tuple

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
class LimiteFisico:
    """
    Límite de verosimilitud física de una variable ambiental.
    Define qué valores puede tomar el sensor antes de considerarse una lectura
    imposible, con independencia de la especie que se esté midiendo.
    """
    minimo: float
    maximo: float
    unidad: str


# Catálogo de variables ambientales soportadas por el dominio.
# Agregar una variable nueva (p. ej. pH del sustrato) consiste en añadir una
# entrada aquí; ni el evaluador ni los casos de uso ni el controlador cambian.
LIMITES_FISICOS: Mapping[str, LimiteFisico] = MappingProxyType({
    "humedad": LimiteFisico(minimo=0.0, maximo=100.0, unidad="%"),
    # 150000 lux: por encima de la luz solar directa extrema al mediodía (~100k-130k lux)
    "luz": LimiteFisico(minimo=0.0, maximo=150000.0, unidad="lux"),
    "temperatura": LimiteFisico(minimo=-50.0, maximo=80.0, unidad="°C"),
})

# Orden canónico de los parámetros. Lo consumen la infraestructura (columnas del
# CSV), la presentación (campos obligatorios de la petición) y la salida de la API.
PARAMETROS_SOPORTADOS: Tuple[str, ...] = tuple(LIMITES_FISICOS.keys())


@dataclass(frozen=True)
class RangoParametro:
    """Rango de referencia óptimo de una variable ambiental para una especie."""
    minimo: float
    maximo: float
    unidad: str

    def __post_init__(self):
        if self.minimo > self.maximo:
            raise ValueError(f"El mínimo ({self.minimo}) no puede ser mayor al máximo ({self.maximo}).")


@dataclass(frozen=True)
class Especie:
    """
    Especie botánica con sus rangos de referencia, indexados por nombre de parámetro.
    Una especie declara qué variables le aplican; el evaluador recorre lo declarado.
    """
    nombre: str
    rangos: Mapping[str, RangoParametro]

    def __post_init__(self):
        if not self.rangos:
            raise ValueError(f"La especie '{self.nombre}' debe declarar al menos un rango de referencia.")
        object.__setattr__(self, "rangos", MappingProxyType(dict(self.rangos)))


@dataclass(frozen=True)
class Medicion:
    """
    Medición ambiental tomada por sensores o ingresada por el usuario.

    No es un diccionario crudo: es un objeto de valor que sólo puede construirse
    si supera sus invariantes (parámetro reconocido, valor numérico y físicamente
    posible). El dominio nunca recibe datos sin validar (RA6, RF6).
    """
    especie: str
    valores: Mapping[str, float]

    def __post_init__(self):
        if not isinstance(self.especie, str) or not self.especie.strip():
            raise ParametroInvalidoError("especie", "La especie es obligatoria y no puede estar vacía.")

        if not self.valores:
            raise ParametroInvalidoError("valores", "La medición debe contener al menos un parámetro.")

        normalizados = {}
        for nombre, valor in self.valores.items():
            if nombre not in LIMITES_FISICOS:
                raise ParametroInvalidoError(
                    nombre, f"El parámetro '{nombre}' no es una variable ambiental reconocida."
                )

            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ParametroInvalidoError(nombre, f"El valor de '{nombre}' debe ser numérico.")

            limite = LIMITES_FISICOS[nombre]
            if not (limite.minimo <= valor <= limite.maximo):
                raise ParametroInvalidoError(
                    nombre,
                    f"El valor de {nombre} ({valor}{limite.unidad}) está fuera del rango "
                    f"físicamente posible ({limite.minimo}{limite.unidad} - {limite.maximo}{limite.unidad})."
                )

            normalizados[nombre] = float(valor)

        object.__setattr__(self, "valores", MappingProxyType(normalizados))

    def valor_de(self, nombre: str) -> float:
        """Devuelve el valor medido de un parámetro, o falla si no fue medido."""
        if nombre not in self.valores:
            raise ParametroInvalidoError(nombre, f"La medición no incluye el parámetro '{nombre}'.")
        return self.valores[nombre]


@dataclass(frozen=True)
class ParametroEvaluado:
    """Resultado de la evaluación de un parámetro contra el rango de referencia."""
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
