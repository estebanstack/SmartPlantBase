"""
Adaptador de Salida: notificaciones en tiempo real mediante Flask-SocketIO.
Implementa NotificadorTiempoRealPort emitiendo eventos a las salas:
- 'qr_{session_id}': confirmación de vinculación/autorización QR en tiempo real.
- 'user_{usuario_id}': telemetría y alertas botánicas en vivo para el propietario.
"""
import logging
from typing import Any, Dict

from flask_socketio import SocketIO

from matera.dominio.modelo import Diagnostico, Lectura, Planta, SesionQR
from matera.dominio.puertos.salida import NotificadorTiempoRealPort

logger = logging.getLogger(__name__)


class SocketIONotificadorAdapter(NotificadorTiempoRealPort):
    """Adaptador secundario que traduce eventos del dominio a emisiones en salas de SocketIO."""

    def __init__(self, socketio: SocketIO):
        self._socketio = socketio

    def notificar_qr_autorizado(self, sesion: SesionQR) -> None:
        datos: Dict[str, Any] = {
            "id": sesion.id,
            "estado": sesion.estado.value,
            "usuario_id": sesion.usuario_id,
            "token": sesion.token,
            "planta_id": sesion.planta_id,
            "dispositivo_id": sesion.dispositivo_id,
            "expira_en": sesion.expira_en.isoformat() if sesion.expira_en else None,
        }
        sala = f"qr_{sesion.id}"
        self._socketio.emit("qr_autorizado", datos, to=sala)
        logger.info("Emitido 'qr_autorizado' hacia la sala %s", sala)

        if sesion.dispositivo_id and sesion.dispositivo_id != sesion.id:
            sala_disp = f"qr_{sesion.dispositivo_id}"
            self._socketio.emit("qr_autorizado", datos, to=sala_disp)

    def notificar_telemetria(
        self, planta: Planta, lectura: Lectura, diagnostico: Diagnostico
    ) -> None:
        sala = f"user_{planta.usuario_id}"
        diag_dict = {
            "especie": diagnostico.especie,
            "estado": diagnostico.estado.value,
            "parametros": [
                {
                    "nombre": p.nombre,
                    "valor": p.valor,
                    "unidad": p.unidad,
                    "rango_optimo": [p.rango_optimo[0], p.rango_optimo[1]],
                    "estado": p.estado.value,
                }
                for p in diagnostico.parametros
            ],
            "recomendaciones": list(diagnostico.recomendaciones),
        }
        lectura_dict = {
            "especie": lectura.especie,
            "valores": dict(lectura.valores),
            "marca_tiempo": lectura.marca_tiempo,
            "dispositivo_id": lectura.dispositivo_id,
            "planta_id": lectura.planta_id,
        }
        payload: Dict[str, Any] = {
            "planta_id": planta.id,
            "planta_nombre": planta.nombre,
            "dispositivo_id": planta.dispositivo_id,
            "especie": planta.especie,
            "valores": dict(lectura.valores),
            "marca_tiempo": lectura.marca_tiempo,
            "estado": diagnostico.estado.value,
            "ultima_lectura": lectura_dict,
            "diagnostico": diag_dict,
        }
        self._socketio.emit("telemetria_actualizada", payload, to=sala)
        logger.info("Emitido 'telemetria_actualizada' hacia la sala %s", sala)

    def notificar_alerta(
        self, planta: Planta, lectura: Lectura, diagnostico: Diagnostico
    ) -> None:
        sala = f"user_{planta.usuario_id}"
        alerta: Dict[str, Any] = {
            "planta_id": planta.id,
            "planta_nombre": planta.nombre,
            "dispositivo_id": planta.dispositivo_id,
            "especie": diagnostico.especie,
            "estado": diagnostico.estado.value,
            "marca_tiempo": lectura.marca_tiempo,
            "valores": dict(lectura.valores),
            "parametros": [
                {
                    "nombre": p.nombre,
                    "valor": p.valor,
                    "unidad": p.unidad,
                    "rango_optimo": [p.rango_optimo[0], p.rango_optimo[1]],
                    "estado": p.estado.value,
                }
                for p in diagnostico.parametros
            ],
            "recomendaciones": list(diagnostico.recomendaciones),
        }
        self._socketio.emit("alerta_planta", alerta, to=sala)
        logger.info("Emitido 'alerta_planta' hacia la sala %s", sala)
