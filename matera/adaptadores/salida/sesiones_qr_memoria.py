"""
Adaptador de Salida: almacenamiento en memoria de sesiones efímeras de QR.
Implementa SesionesQRPort (y alias de compatibilidad guardar/obtener_por_id).
Las sesiones QR son efímeras (5 minutos) y se sincronizan en el mismo proceso con SocketIO.
"""
import threading
from typing import Dict, Optional

from matera.dominio.modelo import SesionQR
from matera.dominio.puertos.salida import SesionesQRPort


class MemoriaSesionesQRAdapter(SesionesQRPort):
    """Repositorio en memoria protegido con lock para acceso concurrente seguro."""

    def __init__(self) -> None:
        self._sesiones: Dict[str, SesionQR] = {}
        self._lock = threading.Lock()

    def guardar_sesion(self, sesion: SesionQR) -> None:
        with self._lock:
            self._sesiones[sesion.id] = sesion

    def obtener_sesion_por_id(self, sesion_id: str) -> Optional[SesionQR]:
        with self._lock:
            return self._sesiones.get(sesion_id)

    # Alias para compatibilidad con pruebas previas
    def guardar(self, sesion: SesionQR) -> None:
        self.guardar_sesion(sesion)

    def obtener_por_id(self, sesion_id: str) -> Optional[SesionQR]:
        return self.obtener_sesion_por_id(sesion_id)

    def limpiar(self) -> None:
        with self._lock:
            self._sesiones.clear()
