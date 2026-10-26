"""
Puertos de Entrada (Driving / Primary Ports).
Interfaces abstractas que exponen los casos de uso del dominio a los adaptadores de entrada.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping
from matera.dominio.modelo import Diagnostico, Especie, EstadoActualPlanta, Planta


class ValidarLecturaPort(ABC):
    """R1: Conserva la validación directa de una lectura desde la interfaz contra la tabla de referencia."""
    @abstractmethod
    def validar(self, especie: str, valores: Mapping[str, float]) -> Diagnostico:
        pass

    @abstractmethod
    def listar_especies(self) -> List[Especie]:
        pass


class RegistrarLecturaPort(ABC):
    """R2 y R5: Registra una lectura proveniente de un sensor/dispositivo, evalúa su estado y la persiste."""
    @abstractmethod
    def registrar(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> Diagnostico:
        pass


class ConsultarEstadoPort(ABC):
    """R5, R6 y R7: Consulta el estado actual y el historial de una planta verificando pertenencia."""
    @abstractmethod
    def consultar_estado(self, usuario_id: str, planta_id: str) -> EstadoActualPlanta:
        pass

    @abstractmethod
    def consultar_historial(
        self, usuario_id: str, planta_id: str, limite: int = 20
    ) -> List[Any]:
        pass

    @abstractmethod
    def listar_plantas_usuario(self, usuario_id: str) -> List[Planta]:
        pass


class AutenticarUsuarioPort(ABC):
    """R7: Casos de uso de registro e inicio de sesión de usuarios y emisión de tokens."""
    @abstractmethod
    def registrar_usuario(self, nombre: str, email: str, password: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def iniciar_sesion(self, email: str, password: str) -> Dict[str, Any]:
        pass
