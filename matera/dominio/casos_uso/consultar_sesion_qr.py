"""
Caso de uso: consultar el estado actual de una sesión QR.
Actualiza automáticamente el estado a EXPIRADA si venció su ventana de validez.
"""
from matera.dominio.excepciones import SesionQRNoEncontradaError
from matera.dominio.modelo import EstadoSesionQR, SesionQR
from matera.dominio.puertos.entrada import ConsultarSesionQRPort
from matera.dominio.puertos.salida import SesionesQRPort


class ConsultarSesionQR(ConsultarSesionQRPort):
    def __init__(self, sesiones_qr: SesionesQRPort):
        self._sesiones_qr = sesiones_qr

    def consultar_sesion_qr(self, sesion_id: str) -> SesionQR:
        sesion = self._sesiones_qr.obtener_sesion_por_id(sesion_id)
        if sesion is None:
            raise SesionQRNoEncontradaError(sesion_id)

        if sesion.estado == EstadoSesionQR.PENDIENTE and sesion.esta_expirada():
            sesion.estado = EstadoSesionQR.EXPIRADA
            self._sesiones_qr.guardar_sesion(sesion)

        return sesion
