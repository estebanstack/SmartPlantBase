"""
Data Transfer Objects (DTOs) de la capa de aplicación.
Desacoplan los modelos internos del dominio de los contratos de entrada/salida de la API.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class DiagnosticoInputDTO:
    """Datos validados que ingresan al caso de uso de diagnóstico."""
    especie: str
    humedad: float
    luz: float
    temperatura: float


@dataclass(frozen=True)
class ParametroDiagnosticoDTO:
    """Representación de un parámetro evaluado para la respuesta."""
    nombre: str
    valor: float
    unidad: str
    rango_optimo: Tuple[float, float]
    estado: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "valor": self.valor,
            "unidad": self.unidad,
            "rangoOptimo": list(self.rango_optimo),
            "estado": self.estado,
        }


@dataclass(frozen=True)
class DiagnosticoResponseDTO:
    """Estructura de salida del caso de uso de diagnóstico correspondiente a Anexo A."""
    especie: str
    estado: str
    parametros: List[ParametroDiagnosticoDTO]
    recomendaciones: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "especie": self.especie,
            "estado": self.estado,
            "parametros": [p.to_dict() for p in self.parametros],
            "recomendaciones": self.recomendaciones,
        }


@dataclass(frozen=True)
class RangoDetalleDTO:
    min: float
    max: float
    unidad: str

    def to_dict(self) -> Dict[str, Any]:
        return {"min": self.min, "max": self.max, "unidad": self.unidad}


@dataclass(frozen=True)
class EspecieDTO:
    """Estructura de catálogo de especie correspondiente a RF5 y Anexo A."""
    nombre: str
    rangos: Dict[str, RangoDetalleDTO]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "rangos": {k: v.to_dict() for k, v in self.rangos.items()},
        }
