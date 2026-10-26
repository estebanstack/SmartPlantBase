"""
Puertos de Salida (Driven / Secondary Ports).
Interfaces abstractas requeridas por el dominio para interactuar con persistencia y emisión de tokens.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from matera.dominio.modelo import Diagnostico, Especie, Lectura, Planta, Usuario


class TablaReferenciaPort(ABC):
    """P3 (R4): Contrato para obtener los rangos óptimos de las especies (implementable en CSV o SQLite)."""
    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        pass

    @abstractmethod
    def obtener_todas(self) -> List[Especie]:
        pass


class HistorialLecturasPort(ABC):
    """P4 (R5): Contrato para persistir y consultar lecturas históricas por planta o dispositivo."""
    @abstractmethod
    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        pass

    @abstractmethod
    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        pass

    @abstractmethod
    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[Any]:
        pass


class UsuariosPlantasPort(ABC):
    """Contrato de salida para persistir y consultar usuarios, plantas y su relación con dispositivos."""
    @abstractmethod
    def guardar_usuario(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        pass

    @abstractmethod
    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        pass

    @abstractmethod
    def listar_plantas_por_usuario(self, usuario_id: str) -> List[Planta]:
        pass

    @abstractmethod
    def guardar_planta(self, planta: Planta) -> None:
        pass


class EmisorTokenPort(ABC):
    """
    Puerto de salida para emisión de tokens (JWT).
    El dominio sólo invoca el contrato sin conocer PyJWT ni el algoritmo criptográfico.
    """
    @abstractmethod
    def emitir_token_usuario(self, usuario_id: str, email: str) -> str:
        pass

    @abstractmethod
    def emitir_token_dispositivo(self, dispositivo_id: str, planta_id: str) -> str:
        pass
