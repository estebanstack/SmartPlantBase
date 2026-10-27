"""
Puertos de Salida (Driven / Secondary Ports).
Lo que el dominio necesita del mundo exterior, dicho en términos de negocio.
La infraestructura (matera/adaptadores/salida/) los implementa con una tecnología concreta.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    Lectura,
    Planta,
    RegistroLectura,
    Usuario,
)


class TablaReferenciaPort(ABC):
    """P3 (R4): rangos óptimos de cada especie. Se implementa en CSV o en base de datos."""

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        ...

    @abstractmethod
    def obtener_todas(self) -> List[Especie]:
        ...


class HistorialLecturasPort(ABC):
    """P4 (R5): guardar lecturas y consultar la última o el historial de una planta."""

    @abstractmethod
    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        ...

    @abstractmethod
    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        ...

    @abstractmethod
    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[RegistroLectura]:
        ...


class UsuariosPort(ABC):
    """R7: guardar y buscar usuarios. Solo lo usa la autenticación."""

    @abstractmethod
    def guardar_usuario(self, usuario: Usuario) -> None:
        ...

    @abstractmethod
    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        ...


class PlantasPort(ABC):
    """R7: guardar y buscar plantas, y saber qué planta tiene cada dispositivo."""

    @abstractmethod
    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        ...

    @abstractmethod
    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        ...

    @abstractmethod
    def listar_plantas_por_usuario(self, usuario_id: str) -> List[Planta]:
        ...

    @abstractmethod
    def guardar_planta(self, planta: Planta) -> None:
        ...


class EmisorTokenPort(ABC):
    """
    R7: emitir tokens. El dominio pide "dame un token para este usuario"
    sin saber que por debajo se usa PyJWT.
    """

    @abstractmethod
    def emitir_token_usuario(self, usuario_id: str, email: str) -> str:
        ...

    @abstractmethod
    def emitir_token_dispositivo(self, dispositivo_id: str, planta_id: str) -> str:
        ...
