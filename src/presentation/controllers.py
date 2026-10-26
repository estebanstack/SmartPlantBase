"""
Controladores REST (Capa de Presentación).
Valida las peticiones HTTP en el borde del sistema (RA6) y delega a los casos de uso.
Responde estrictamente en formato JSON, sin renderizar HTML (RA1).
"""
from typing import Any, Dict, Optional
from flask import Blueprint, jsonify, request

from src.application.dtos import DiagnosticoInputDTO
from src.application.use_cases import (
    AutorizarSesionQRUseCase,
    ConsultarSesionQRUseCase,
    EvaluarDiagnosticoUseCase,
    GenerarSesionQRUseCase,
    ListarEspeciesUseCase,
)
from src.domain.entities import PARAMETROS_SOPORTADOS
from src.domain.exceptions import ParametroInvalidoError
from src.presentation.websocket_handlers import (
    notificar_alerta_usuario,
    notificar_qr_autorizado,
    notificar_telemetria_usuario,
)


def crear_api_blueprint(
    evaluar_use_case: EvaluarDiagnosticoUseCase,
    listar_use_case: ListarEspeciesUseCase,
    generar_qr_use_case: Optional[GenerarSesionQRUseCase] = None,
    autorizar_qr_use_case: Optional[AutorizarSesionQRUseCase] = None,
    consultar_qr_use_case: Optional[ConsultarSesionQRUseCase] = None,
    socketio: Optional[Any] = None,
) -> Blueprint:

    """Fábrica de Blueprint REST con inyección de dependencias de los casos de uso."""
    api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

    def _parse_float(campo: str, valor: Any) -> float:
        # En Python bool es subclase de int: se rechaza explícitamente True/False.
        if isinstance(valor, bool):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

    @api_bp.route("/diagnosticos", methods=["POST"])
    def evaluar_diagnostico():
        """
        POST /api/v1/diagnosticos (Anexo A).
        Valida presencia y tipo en el borde (RA6) y construye el DTO de entrada.
        Los parámetros exigidos son los que declara el dominio: agregar una
        variable ambiental no modifica este controlador.
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

        datos: Dict[str, Any] = request.get_json(silent=True) or {}

        especie_raw = datos.get("especie")
        if not isinstance(especie_raw, str) or not especie_raw.strip():
            raise ParametroInvalidoError("especie", "El parámetro 'especie' es obligatorio y debe ser un texto no vacío.")

        valores: Dict[str, float] = {}
        for campo in PARAMETROS_SOPORTADOS:
            if campo not in datos or datos[campo] is None:
                raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio.")
            valores[campo] = _parse_float(campo, datos[campo])

        dto_entrada = DiagnosticoInputDTO(
            especie=especie_raw.strip().lower(),
            valores=valores,
        )

        resultado_dto = evaluar_use_case.ejecutar(dto_entrada)

        # Hook WebSocket: Notificación en tiempo real si se asocia un usuario
        usuario_id = datos.get("usuario_id")
        if usuario_id and socketio:
            usuario_str = str(usuario_id).strip()
            # Enviar actualización de telemetría a la sala user_{usuario_id}
            notificar_telemetria_usuario(
                socketio,
                usuario_str,
                {"especie": resultado_dto.especie, "valores": valores, "estado": resultado_dto.estado},
            )
            # Si el estado es de alerta (EN_RIESGO o CRITICO), emitir alerta a la sala del usuario
            if resultado_dto.estado in ("EN_RIESGO", "CRITICO"):
                notificar_alerta_usuario(socketio, usuario_str, resultado_dto.to_dict())

        return jsonify(resultado_dto.to_dict()), 200

    @api_bp.route("/especies", methods=["GET"])
    def listar_especies():
        """
        GET /api/v1/especies (RF5 y Anexo A).
        Retorna la lista de especies soportadas con sus rangos de referencia.
        """
        especies = listar_use_case.ejecutar()
        return jsonify([esp.to_dict() for esp in especies]), 200

    if generar_qr_use_case:
        @api_bp.route("/auth/qr/generar", methods=["POST"])
        def generar_sesion_qr():
            """POST /api/v1/auth/qr/generar - Crea una sesión efímera para login QR."""
            datos = request.get_json(silent=True) or {}
            sesion_id = datos.get("session_id") or datos.get("id")
            sesion_dto = generar_qr_use_case.ejecutar(sesion_id=sesion_id)
            return jsonify(sesion_dto.to_dict()), 201

    if consultar_qr_use_case:
        @api_bp.route("/auth/qr/<session_id>", methods=["GET"])
        def consultar_sesion_qr(session_id: str):
            """GET /api/v1/auth/qr/<session_id> - Consulta el estado de una sesión QR."""
            sesion_dto = consultar_qr_use_case.ejecutar(session_id=session_id)
            return jsonify(sesion_dto.to_dict()), 200

    if autorizar_qr_use_case:
        @api_bp.route("/auth/qr/<session_id>/autorizar", methods=["POST"])
        def autorizar_sesion_qr(session_id: str):
            """
            POST /api/v1/auth/qr/<session_id>/autorizar
            Autoriza la sesión QR y notifica por WebSocket a la sala qr_{session_id}.
            """
            if not request.is_json:
                raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

            datos = request.get_json(silent=True) or {}
            usuario_id = datos.get("usuario_id")
            token = datos.get("token")

            if not usuario_id or not isinstance(usuario_id, str) or not usuario_id.strip():
                raise ParametroInvalidoError("usuario_id", "El parámetro 'usuario_id' es obligatorio.")
            if not token or not isinstance(token, str) or not token.strip():
                raise ParametroInvalidoError("token", "El parámetro 'token' es obligatorio.")

            sesion_dto = autorizar_qr_use_case.ejecutar(
                sesion_id=session_id,
                usuario_id=usuario_id.strip(),
                token=token.strip(),
            )

            # Notificación en tiempo real a la sala pre-auth qr_{session_id}
            if socketio:
                notificar_qr_autorizado(socketio, session_id, sesion_dto.to_dict())

            return jsonify(sesion_dto.to_dict()), 200

    return api_bp

