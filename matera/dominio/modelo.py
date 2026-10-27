"""
Entidades y Objetos de Valor del Dominio (Núcleo Hexagonal).
Estructuras de datos puras (POPOs) e invariantes físicas del dominio botánico.
0 dependencias de frameworks o infraestructura externa.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Dict, List, Mapping, Optional, Tuple

from matera.dominio.excepciones import ParametroInvalidoError


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
    Define los valores que un sensor puede medir antes de considerarse lectura físicamente imposible.
    """
    minimo: float
    maximo: float
    unidad: str


LIMITES_FISICOS: Mapping[str, LimiteFisico] = MappingProxyType({
    "humedad": LimiteFisico(minimo=0.0, maximo=100.0, unidad="%"),
    "luz": LimiteFisico(minimo=0.0, maximo=150000.0, unidad="lux"),
    "temperatura": LimiteFisico(minimo=-50.0, maximo=80.0, unidad="°C"),
})

PARAMETROS_SOPORTADOS: Tuple[str, ...] = tuple(LIMITES_FISICOS.keys())


@dataclass(frozen=True)
class RangoParametro:
    """Rango de referencia óptimo de una variable ambiental para una especie botánica."""
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
    """
    nombre: str
    rangos: Mapping[str, RangoParametro]

    def __post_init__(self):
        if not self.rangos:
            raise ValueError(f"La especie '{self.nombre}' debe declarar al menos un rango de referencia.")
        object.__setattr__(self, "rangos", MappingProxyType(dict(self.rangos)))


@dataclass(frozen=True)
class Lectura:
    """
    Lectura ambiental reportada por un sensor (ESP32) o ingresada manualmente desde la interfaz.
    Valida límites físicos al construirse (humedad 0-100%, luz 0-150000 lux, temp -50 a 80°C).
    """
    especie: str
    valores: Mapping[str, float]
    marca_tiempo: str = ""
    dispositivo_id: Optional[str] = None
    planta_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.especie, str) or not self.especie.strip():
            raise ParametroInvalidoError("especie", "La especie es obligatoria y no puede estar vacía.")

        if not self.valores:
            raise ParametroInvalidoError("valores", "La lectura debe contener al menos un parámetro.")

        normalizados: Dict[str, float] = {}
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

        # Sincronización de marca de tiempo ISO-8601
        if not self.marca_tiempo:
            marca = self.timestamp.isoformat() if self.timestamp else datetime.utcnow().isoformat()
            object.__setattr__(self, "marca_tiempo", marca)

    def valor_de(self, nombre: str) -> float:
        """Devuelve el valor medido de un parámetro, o falla si no está presente."""
        if nombre not in self.valores:
            raise ParametroInvalidoError(nombre, f"La lectura no incluye el parámetro '{nombre}'.")
        return self.valores[nombre]


# Alias para compatibilidad con nombres de Fase 1
Medicion = Lectura


@dataclass(frozen=True)
class ParametroEvaluado:
    """Resultado de la evaluación de un parámetro contra el rango óptimo de referencia."""
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


@dataclass(frozen=True)
class Planta:
    """
    Planta registrada en el sistema.
    Pertenece a un usuario específico y está vinculada a un dispositivo ESP32.
    """
    id: str
    nombre: str
    especie: str
    usuario_id: str
    dispositivo_id: str

    def pertenece_a(self, usuario_id: str) -> bool:
        """Regla de negocio de pertenencia en el dominio."""
        return self.usuario_id == usuario_id


@dataclass(frozen=True)
class Usuario:
    """Usuario propietario de una o más plantas."""
    id: str
    nombre: str
    email: str
    password_hash: str


@dataclass(frozen=True)
class EstadoActualPlanta:
    """Vista agregada del estado actual de una planta a partir de su última lectura."""
    planta: Planta
    ultima_lectura: Optional[Lectura]
    diagnostico: Optional[Diagnostico]


@dataclass(frozen=True)
class RegistroLectura:
    """Una lectura guardada en el historial junto con el estado que se calculó para ella."""
    lectura: Lectura
    estado: EstadoPlanta


@dataclass(frozen=True)
class SesionUsuario:
    """Resultado de registrarse o iniciar sesión: el usuario y el token que se le emitió."""
    usuario: Usuario
    token: str
