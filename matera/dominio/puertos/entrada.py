"""
Puertos de Entrada (Driving / Primary Ports).
Cada puerto es una cosa que alguien de afuera (el front, un dispositivo, una prueba)
le puede pedir al dominio. Cada uno lo implementa un caso de uso en matera/dominio/casos_uso/.
"""
from abc import ABC, abstractmethod
from typing import List, Mapping

from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    EstadoActualPlanta,
    Planta,
    RegistroLectura,
    SesionUsuario,
)


class ValidarLecturaPort(ABC):
    """R1: diagnosticar una medición ingresada a mano desde el front."""

    @abstractmethod
    def validar(self, especie: str, valores: Mapping[str, float]) -> Diagnostico:
        ...


class ConsultarEspeciesPort(ABC):
    """R1: catálogo de especies soportadas con sus rangos (llena el selector del front)."""

    @abstractmethod
    def listar_especies(self) -> List[Especie]:
        ...


class RegistrarLecturaPort(ABC):
    """R2 y R5: un dispositivo reporta una lectura; se evalúa y se guarda en el historial."""

    @abstractmethod
    def registrar(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> Diagnostico:
        ...


class ConsultarEstadoPort(ABC):
    """R5 y R6: estado actual (última lectura + diagnóstico) de una planta del usuario."""

    @abstractmethod
    def consultar_estado(self, usuario_id: str, planta_id: str) -> EstadoActualPlanta:
        ...


class ConsultarHistorialPort(ABC):
    """R5: lecturas anteriores de una planta del usuario, de la más reciente a la más antigua."""

    @abstractmethod
    def consultar_historial(
        self, usuario_id: str, planta_id: str, limite: int = 20
    ) -> List[RegistroLectura]:
        ...


class ListarPlantasPort(ABC):
    """R7: plantas que pertenecen al usuario autenticado."""

    @abstractmethod
    def listar_plantas_usuario(self, usuario_id: str) -> List[Planta]:
        ...


class AutenticarUsuarioPort(ABC):
    """R7: registro e inicio de sesión de usuarios."""

    @abstractmethod
    def registrar_usuario(self, nombre: str, email: str, password: str) -> SesionUsuario:
        ...

    @abstractmethod
    def iniciar_sesion(self, email: str, password: str) -> SesionUsuario:
        ...
