"""
Entidades y Objetos de Valor del Dominio (Núcleo Hexagonal).
Estructuras de datos puras (POPOs) e invariantes físicas del dominio botánico.
0 dependencias de frameworks o infraestructura externa.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
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
class ParametroAmbiental:
    """
    Todo lo que el dominio sabe de una variable ambiental, en un solo lugar:
    su unidad, el rango que un sensor puede medir (fuera de él la lectura es físicamente
    imposible) y qué recomendar cuando queda por debajo o por encima del rango óptimo.
    Agregar un parámetro (por ejemplo pH) es agregar una entrada en PARAMETROS_AMBIENTALES;
    el evaluador (validador.py) no cambia.
    """
    unidad: str
    minimo_fisico: float
    maximo_fisico: float
    recomendacion_bajo: str
    recomendacion_alto: str

    def recomendacion(self, estado: "EstadoParametro") -> Optional[str]:
        """Qué hacer si el parámetro quedó BAJO o ALTO; None si está OPTIMO."""
        if estado == EstadoParametro.BAJO:
            return self.recomendacion_bajo
        if estado == EstadoParametro.ALTO:
            return self.recomendacion_alto
        return None


PARAMETROS_AMBIENTALES: Mapping[str, ParametroAmbiental] = MappingProxyType({
    "humedad": ParametroAmbiental(
        unidad="%",
        minimo_fisico=0.0,
        maximo_fisico=100.0,
        recomendacion_bajo="La humedad del sustrato está por debajo del rango recomendado: riegue moderadamente.",
        recomendacion_alto="La humedad del sustrato supera el rango recomendado: suspenda el riego y facilite el drenaje.",
    ),
    "luz": ParametroAmbiental(
        unidad="lux",
        minimo_fisico=0.0,
        maximo_fisico=150000.0,
        recomendacion_bajo="El nivel de luz es insuficiente para esta especie: ubique la planta en un lugar con mayor exposición solar.",
        recomendacion_alto="El nivel de luz es excesivo: proteja la planta con sombra parcial o retírela de la radiación solar directa.",
    ),
    "temperatura": ParametroAmbiental(
        unidad="°C",
        minimo_fisico=-50.0,
        maximo_fisico=80.0,
        recomendacion_bajo="La temperatura ambiental es demasiado baja: traslade la planta a un espacio más cálido o protegido.",
        recomendacion_alto="La temperatura ambiental es excesiva: ventile el espacio o traslade la planta a un lugar fresco.",
    ),
})

PARAMETROS_SOPORTADOS: Tuple[str, ...] = tuple(PARAMETROS_AMBIENTALES.keys())


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

    def __post_init__(self):
        if not isinstance(self.especie, str) or not self.especie.strip():
            raise ParametroInvalidoError("especie", "La especie es obligatoria y no puede estar vacía.")

        if not self.valores:
            raise ParametroInvalidoError("valores", "La lectura debe contener al menos un parámetro.")

        normalizados: Dict[str, float] = {}
        for nombre, valor in self.valores.items():
            if nombre not in PARAMETROS_AMBIENTALES:
                raise ParametroInvalidoError(
                    nombre, f"El parámetro '{nombre}' no es una variable ambiental reconocida."
                )

            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ParametroInvalidoError(nombre, f"El valor de '{nombre}' debe ser numérico.")

            parametro = PARAMETROS_AMBIENTALES[nombre]
            if not (parametro.minimo_fisico <= valor <= parametro.maximo_fisico):
                u = parametro.unidad
                raise ParametroInvalidoError(
                    nombre,
                    f"El valor de {nombre} ({valor}{u}) está fuera del rango "
                    f"físicamente posible ({parametro.minimo_fisico}{u} - {parametro.maximo_fisico}{u})."
                )

            normalizados[nombre] = float(valor)

        object.__setattr__(self, "valores", MappingProxyType(normalizados))

        # Si nadie dice cuándo se midió (diagnóstico manual), se usa el momento actual en UTC (ISO-8601)
        if not self.marca_tiempo:
            object.__setattr__(self, "marca_tiempo", datetime.now(timezone.utc).isoformat())

    def valor_de(self, nombre: str) -> float:
        """Devuelve el valor medido de un parámetro, o falla si no está presente."""
        if nombre not in self.valores:
            raise ParametroInvalidoError(nombre, f"La lectura no incluye el parámetro '{nombre}'.")
        return self.valores[nombre]


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


@dataclass(frozen=True)
class PlantaRegistrada:
    """Resultado de registrar una planta: la planta y el token que debe grabarse en su dispositivo."""
    planta: Planta
    token_dispositivo: str
