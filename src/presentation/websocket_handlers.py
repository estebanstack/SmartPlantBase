"""
Manejadores de eventos WebSocket y gestión de salas en Flask-SocketIO (Capa de Presentación).

Implementa la arquitectura dual de WebSockets:
1. Sala Pre-Auth: 'qr_{session_id}' para confirmación en tiempo real de inicio de sesión o vinculación QR.
2. Sala Post-Auth: 'user_{usuario_id}' para notificaciones, telemetría y alertas botánicas en tiempo real.

Diseñado de manera proporcional y defendible:
Utiliza las salas nativas en memoria de Flask-SocketIO sin requerir brokers externos (como Redis o RabbitMQ).
"""
import logging
from typing import Any, Dict, Optional
from flask_socketio import SocketIO, join_room, leave_room

from src.application.use_cases import AutorizarSesionQRUseCase, ConsultarSesionQRUseCase
from src.domain.exceptions import SesionQRError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funciones Notificadoras / Hooks hacia las salas
# ---------------------------------------------------------------------------

def notificar_qr_autorizado(socketio: SocketIO, session_id: str, datos: Dict[str, Any]) -> None:
    """
    Emite el evento 'qr_autorizado' a la sala efímera de la sesión QR.
    Notifica instantáneamente al navegador que el dispositivo móvil autorizó el acceso.
    """
    sala = f"qr_{session_id}"
    socketio.emit("qr_autorizado", datos, to=sala)
    logger.info("Emitido 'qr_autorizado' hacia la sala %s", sala)


def notificar_alerta_usuario(socketio: SocketIO, usuario_id: str, alerta: Dict[str, Any]) -> None:
    """
    Emite una alerta botánica al canal personal del usuario autenticado.
    Se utiliza cuando el evaluador de diagnóstico detecta un parámetro EN_RIESGO o CRITICO.
    """
    sala = f"user_{usuario_id}"
    socketio.emit("alerta_planta", alerta, to=sala)
    logger.info("Emitido 'alerta_planta' hacia la sala %s", sala)


def notificar_telemetria_usuario(socketio: SocketIO, usuario_id: str, telemetria: Dict[str, Any]) -> None:
    """
    Emite lecturas ambientales actualizadas en vivo a la sala personal del usuario.
    """
    sala = f"user_{usuario_id}"
    socketio.emit("telemetria_actualizada", telemetria, to=sala)
    logger.info("Emitido 'telemetria_actualizada' hacia la sala %s", sala)


# ---------------------------------------------------------------------------
# Registro de manejadores de eventos SocketIO
# ---------------------------------------------------------------------------

def registrar_websocket_handlers(
    socketio: SocketIO,
    autorizar_qr_use_case: Optional[AutorizarSesionQRUseCase] = None,
    consultar_qr_use_case: Optional[ConsultarSesionQRUseCase] = None,
) -> None:
    """
    Registra los eventos de conexión, desconexión y gestión de salas en la instancia de SocketIO.
    """

    @socketio.on("connect")
    def handle_connect():
        logger.debug("Cliente WebSocket conectado.")
        return {"status": "conectado"}

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.debug("Cliente WebSocket desconectado.")

    # -----------------------------------------------------------------------
    # 1. Gestión de Sala Pre-Auth: qr_{session_id}
    # -----------------------------------------------------------------------

    def _unirse_sala_qr(data: Any):
        if not isinstance(data, dict):
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'session_id'."}
        session_id = data.get("session_id") or data.get("id")
        if not session_id:
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'session_id'."}
        session_id = str(session_id).strip()
        sala = f"qr_{session_id}"
        join_room(sala)
        logger.debug("Cliente unido a sala QR: %s", sala)
        return {"status": "ok", "sala": sala, "session_id": session_id}

    @socketio.on("unirse_sesion_qr")
    def on_unirse_sesion_qr(data):
        return _unirse_sala_qr(data)

    @socketio.on("join_qr_session")
    def on_join_qr_session(data):
        return _unirse_sala_qr(data)

    def _salir_sala_qr(data: Any):
        if not isinstance(data, dict):
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'session_id'."}
        session_id = data.get("session_id") or data.get("id")
        if not session_id:
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'session_id'."}
        session_id = str(session_id).strip()
        sala = f"qr_{session_id}"
        leave_room(sala)
        logger.debug("Cliente salió de sala QR: %s", sala)
        return {"status": "ok", "sala": sala}

    @socketio.on("salir_sesion_qr")
    def on_salir_sesion_qr(data):
        return _salir_sala_qr(data)

    @socketio.on("leave_qr_session")
    def on_leave_qr_session(data):
        return _salir_sala_qr(data)

    # -----------------------------------------------------------------------
    # 2. Gestión de Sala Post-Auth: user_{usuario_id}
    # -----------------------------------------------------------------------

    def _unirse_sala_usuario(data: Any):
        if not isinstance(data, dict) or not data.get("usuario_id"):
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'usuario_id'."}
        usuario_id = str(data["usuario_id"]).strip()
        sala = f"user_{usuario_id}"
        join_room(sala)
        logger.debug("Cliente unido a canal de usuario: %s", sala)
        return {"status": "ok", "sala": sala, "usuario_id": usuario_id}

    @socketio.on("unirse_canal_usuario")
    def on_unirse_canal_usuario(data):
        return _unirse_sala_usuario(data)

    @socketio.on("join_user_channel")
    def on_join_user_channel(data):
        return _unirse_sala_usuario(data)

    def _salir_sala_usuario(data: Any):
        if not isinstance(data, dict) or not data.get("usuario_id"):
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere 'usuario_id'."}
        usuario_id = str(data["usuario_id"]).strip()
        sala = f"user_{usuario_id}"
        leave_room(sala)
        logger.debug("Cliente salió del canal de usuario: %s", sala)
        return {"status": "ok", "sala": sala}

    @socketio.on("salir_canal_usuario")
    def on_salir_canal_usuario(data):
        return _salir_sala_usuario(data)

    @socketio.on("leave_user_channel")
    def on_leave_user_channel(data):
        return _salir_sala_usuario(data)

    # -----------------------------------------------------------------------
    # 3. Autorización directa vía WebSocket
    # -----------------------------------------------------------------------

    def _autorizar_qr_handler(data: Any):
        if autorizar_qr_use_case is None:
            return {"error": "SERVICIO_NO_DISPONIBLE", "mensaje": "El caso de uso no está configurado."}
        if not isinstance(data, dict):
            return {"error": "PARAMETRO_INVALIDO", "mensaje": "Se requiere un objeto con datos de autorización."}

        session_id = data.get("session_id") or data.get("id")
        usuario_id = data.get("usuario_id")
        token = data.get("token")

        if not session_id or not usuario_id or not token:
            return {
                "error": "PARAMETRO_INVALIDO",
                "mensaje": "Se requieren 'session_id', 'usuario_id' y 'token'.",
            }

        try:
            resultado_dto = autorizar_qr_use_case.ejecutar(
                sesion_id=str(session_id).strip(),
                usuario_id=str(usuario_id).strip(),
                token=str(token).strip(),
            )
            datos_notificacion = resultado_dto.to_dict()
            notificar_qr_autorizado(socketio, str(session_id).strip(), datos_notificacion)
            return {"status": "ok", "sesion": datos_notificacion}
        except SesionQRError as err:
            return {"error": type(err).__name__, "mensaje": str(err)}
        except ValueError as val_err:
            return {"error": "PARAMETRO_INVALIDO", "mensaje": str(val_err)}

    @socketio.on("autorizar_qr")
    def on_autorizar_qr(data):
        return _autorizar_qr_handler(data)

    @socketio.on("authorize_qr")
    def on_authorize_qr(data):
        return _autorizar_qr_handler(data)
