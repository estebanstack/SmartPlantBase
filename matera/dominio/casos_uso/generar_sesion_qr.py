"""
Caso de uso: generar una sesión efímera QR en estado PENDIENTE.
Sirve tanto para vincular el dispositivo de una planta por WebSocket como para
autorización rápida entre dispositivos sin copiar tokens manualmente.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from matera.dominio.modelo import EstadoSesionQR, SesionQR
from matera.dominio.puertos.entrada import GenerarSesionQRPort
from matera.dominio.puertos.salida import SesionesQRPort


class GenerarSesionQR(GenerarSesionQRPort):
    def __init__(self, sesiones_qr: SesionesQRPort, duracion_segundos: int = 300):
        self._sesiones_qr = sesiones_qr
        self._duracion_segundos = duracion_segundos

    def generar_sesion_qr(
        self,
        sesion_id: Optional[str] = None,
        dispositivo_id: Optional[str] = None,
        planta_id: Optional[str] = None,
    ) -> SesionQR:
        ahora = datetime.now(timezone.utc)
        id_final = (sesion_id.strip() if sesion_id and sesion_id.strip() else uuid.uuid4().hex)
        expira_en = ahora + timedelta(seconds=self._duracion_segundos)

        sesion = SesionQR(
            id=id_final,
            estado=EstadoSesionQR.PENDIENTE,
            planta_id=planta_id.strip() if planta_id and planta_id.strip() else None,
            dispositivo_id=dispositivo_id.strip() if dispositivo_id and dispositivo_id.strip() else None,
            creada_en=ahora,
            expira_en=expira_en,
        )
        self._sesiones_qr.guardar_sesion(sesion)
        return sesion
