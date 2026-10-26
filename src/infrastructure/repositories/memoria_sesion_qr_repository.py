"""
Implementación en memoria del repositorio de sesiones QR (Capa de Infraestructura).
Sigue el criterio de proporcionalidad técnica (anti-overengineering):
Las sesiones QR son efímeras y para el entorno actual una estructura concurrente
en memoria es suficiente, rápida y no añade dependencias pesadas como Redis.
"""
import threading
from typing import Dict, Optional

from src.domain.entities import SesionQR
from src.domain.repositories import SesionQRRepository


class MemoriaSesionQRRepository(SesionQRRepository):
    """
    Repositorio en memoria protegido con un lock para acceso concurrente seguro.
    """

    def __init__(self) -> None:
        self._sesiones: Dict[str, SesionQR] = {}
        self._lock = threading.Lock()

    def guardar(self, sesion: SesionQR) -> None:
        with self._lock:
            self._sesiones[sesion.id] = sesion

    def obtener_por_id(self, sesion_id: str) -> Optional[SesionQR]:
        with self._lock:
            return self._sesiones.get(sesion_id)

    def limpiar(self) -> None:
        """Limpia todas las sesiones almacenadas (ideal para pruebas)."""
        with self._lock:
            self._sesiones.clear()
