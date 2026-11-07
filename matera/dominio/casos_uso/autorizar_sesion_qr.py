"""
Caso de uso: autorizar una sesión QR.
Si se vincula una planta del usuario, verifica la regla de propiedad en el dominio,
emite el token del dispositivo por debajo (R7) y notifica a la sala WebSocket qr_{id}
sin que el usuario tenga que copiar ni pegar manualmente el token.
"""
from datetime import datetime, timezone
from typing import Optional

from matera.dominio.casos_uso.propiedad import obtener_planta_del_usuario
from matera.dominio.excepciones import AccesoNoAutorizadoPlantaError, SesionQRNoEncontradaError
from matera.dominio.modelo import EstadoSesionQR, SesionQR
from matera.dominio.puertos.entrada import AutorizarSesionQRPort
from matera.dominio.puertos.salida import (
    EmisorTokenPort,
    NotificadorTiempoRealPort,
    PlantasPort,
    SesionesQRPort,
)


class AutorizarSesionQR(AutorizarSesionQRPort):
    def __init__(
        self,
        sesiones_qr: SesionesQRPort,
        plantas: Optional[PlantasPort] = None,
        emisor_token: Optional[EmisorTokenPort] = None,
        notificador: Optional[NotificadorTiempoRealPort] = None,
    ):
        self._sesiones_qr = sesiones_qr
        self._plantas = plantas
        self._emisor_token = emisor_token
        self._notificador = notificador

    def autorizar_sesion_qr(
        self,
        sesion_id: str,
        usuario_id: str,
        token: Optional[str] = None,
        planta_id: Optional[str] = None,
    ) -> SesionQR:
        sesion = self._sesiones_qr.obtener_sesion_por_id(sesion_id)

        # Si el usuario autoriza directamente el QR de una planta/dispositivo cuya sesión aún no fue
        # precreada, y tenemos el catálogo de plantas, la inicializamos al vuelo para su dispositivo.
        if sesion is None and planta_id and self._plantas is not None:
            planta_auto = obtener_planta_del_usuario(self._plantas, usuario_id, planta_id)
            ahora = datetime.now(timezone.utc)
            sesion = SesionQR(
                id=sesion_id,
                estado=EstadoSesionQR.PENDIENTE,
                planta_id=planta_auto.id,
                dispositivo_id=planta_auto.dispositivo_id,
                creada_en=ahora,
            )

        if sesion is None:
            raise SesionQRNoEncontradaError(sesion_id)

        planta_objetivo_id = planta_id or sesion.planta_id
        dispositivo_objetivo_id = sesion.dispositivo_id
        token_final = token

        # Si se indica planta (o la sesión QR fue abierta por un dispositivo vinculado) y no se pasó token manual,
        # verificamos propiedad en el dominio y emitimos el token de dispositivo automáticamente (R7).
        if self._plantas is not None and self._emisor_token is not None:
            if planta_objetivo_id:
                planta = obtener_planta_del_usuario(self._plantas, usuario_id, planta_objetivo_id)
                planta_objetivo_id = planta.id
                dispositivo_objetivo_id = planta.dispositivo_id
                if not token_final:
                    token_final = self._emisor_token.emitir_token_dispositivo(
                        planta.dispositivo_id, planta.id
                    )
            elif dispositivo_objetivo_id and not token_final:
                planta = self._plantas.obtener_planta_por_dispositivo(dispositivo_objetivo_id)
                if planta is not None:
                    if not planta.pertenece_a(usuario_id):
                        raise AccesoNoAutorizadoPlantaError(usuario_id, planta.id)
                    planta_objetivo_id = planta.id
                    token_final = self._emisor_token.emitir_token_dispositivo(
                        planta.dispositivo_id, planta.id
                    )

        sesion.autorizar(
            usuario_id=usuario_id,
            token=token_final or "",
            planta_id=planta_objetivo_id,
            dispositivo_id=dispositivo_objetivo_id,
        )
        self._sesiones_qr.guardar_sesion(sesion)

        if self._notificador is not None:
            self._notificador.notificar_qr_autorizado(sesion)

        return sesion
