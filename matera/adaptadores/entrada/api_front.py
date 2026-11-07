"""
Adaptador de Entrada: Controlador REST para la Interfaz Web, Auth y Consulta de Plantas (R1, R5, R6, R7).
Solo rutas: cada una lee la petición (peticion_http.py), llama a su puerto de entrada
y devuelve el resultado en JSON (serializacion.py). Los errores los traduce errores_http.py.
"""
from typing import Any, Optional

from flask import Blueprint, jsonify, request

from matera.adaptadores.entrada import peticion_http
from matera.adaptadores.entrada.seguridad import (
    ALCANCE_USUARIO,
    TokenRechazadoError,
    VerificadorTokenPort,
    requiere_usuario,
)
from matera.adaptadores.entrada.serializacion import (
    diagnostico_a_json,
    especie_a_json,
    estado_actual_a_json,
    planta_a_json,
    registro_a_json,
    sesion_a_json,
    sesion_qr_a_json,
)
from matera.adaptadores.entrada.websocket_handlers import (
    notificar_alerta_usuario,
    notificar_telemetria_usuario,
)
from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.puertos.entrada import (
    AutenticarUsuarioPort,
    AutorizarSesionQRPort,
    ConsultarEspeciesPort,
    ConsultarEstadoPort,
    ConsultarHistorialPort,
    ConsultarSesionQRPort,
    EmitirTokenDispositivoPort,
    GenerarSesionQRPort,
    ListarPlantasPort,
    RegistrarPlantaPort,
    ValidarLecturaPort,
)


def crear_api_front_blueprint(
    validar_lectura: ValidarLecturaPort,
    consultar_especies: ConsultarEspeciesPort,
    consultar_estado: ConsultarEstadoPort,
    consultar_historial: ConsultarHistorialPort,
    listar_plantas: ListarPlantasPort,
    registrar_planta: RegistrarPlantaPort,
    emitir_token_dispositivo: EmitirTokenDispositivoPort,
    autenticar: AutenticarUsuarioPort,
    verificador: VerificadorTokenPort,
    generar_sesion_qr: Optional[GenerarSesionQRPort] = None,
    consultar_sesion_qr: Optional[ConsultarSesionQRPort] = None,
    autorizar_sesion_qr: Optional[AutorizarSesionQRPort] = None,
    socketio: Optional[Any] = None,
) -> Blueprint:
    """
    Fábrica del Blueprint REST para clientes web / frontend.
    Conecta las rutas HTTP con los puertos de entrada del hexágono.
    """
    api_bp = Blueprint("api_front", __name__, url_prefix="/api")

    # -------------------------------------------------------------------------
    # R1: Endpoints compatibles con Fase 1 (/api/v1/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/v1/diagnosticos", methods=["POST"])
    @requiere_usuario(verificador)
    def evaluar_diagnostico_v1(usuario_id: str):
        """
        POST /api/v1/diagnosticos (R1 - Conservar validación de Fase 1).
        Exige JWT de usuario (R7). Si hay canal WebSocket activo para el usuario,
        notifica la evaluación y alertas en tiempo real.
        """
        datos = peticion_http.cuerpo_json()
        valores = peticion_http.valores_medidos(datos)
        diagnostico = validar_lectura.validar(
            especie=peticion_http.texto(datos, "especie").lower(),
            valores=valores,
        )
        resultado_json = diagnostico_a_json(diagnostico)

        if socketio is not None:
            canal_usr = str(datos.get("usuario_id") or usuario_id).strip()
            notificar_telemetria_usuario(
                socketio,
                canal_usr,
                {"especie": diagnostico.especie, "valores": valores, "estado": diagnostico.estado.value},
            )
            if diagnostico.estado.value in ("EN_RIESGO", "CRITICO"):
                notificar_alerta_usuario(socketio, canal_usr, resultado_json)

        return jsonify(resultado_json), 200


    @api_bp.route("/v1/especies", methods=["GET"])
    def listar_especies_v1():
        """
        GET /api/v1/especies (R1).
        Público a propósito: es el catálogo de referencia, no tiene datos de ningún usuario.
        """
        especies = consultar_especies.listar_especies()
        return jsonify([especie_a_json(e) for e in especies]), 200

    # -------------------------------------------------------------------------
    # R7: Endpoints de Autenticación (/api/auth/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/auth/registro", methods=["POST"])
    def registrar_usuario():
        """
        POST /api/auth/registro (R7).
        """
        datos = peticion_http.cuerpo_json()
        sesion = autenticar.registrar_usuario(
            nombre=peticion_http.texto(datos, "nombre"),
            email=peticion_http.correo(datos),
            password=peticion_http.contrasena_nueva(datos),
        )
        return jsonify({"mensaje": "Usuario registrado exitosamente.", **sesion_a_json(sesion)}), 201

    @api_bp.route("/auth/login", methods=["POST"])
    def iniciar_sesion():
        """
        POST /api/auth/login (R7).
        """
        datos = peticion_http.cuerpo_json()
        sesion = autenticar.iniciar_sesion(
            email=peticion_http.texto(datos, "email"),
            password=peticion_http.texto(datos, "password", recortar=False),
        )
        return jsonify({"mensaje": "Sesión iniciada correctamente.", **sesion_a_json(sesion)}), 200

    # -------------------------------------------------------------------------
    # R5, R6, R7: Endpoints de Consulta de Plantas e Historial (/api/plantas/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/plantas", methods=["GET"])
    @requiere_usuario(verificador)
    def obtener_plantas_usuario(usuario_id: str):
        """
        GET /api/plantas (R7).
        Lista las plantas registradas que pertenecen al usuario autenticado.
        """
        plantas = listar_plantas.listar_plantas_usuario(usuario_id)
        return jsonify([planta_a_json(p) for p in plantas]), 200

    @api_bp.route("/plantas", methods=["POST"])
    @requiere_usuario(verificador)
    def crear_planta(usuario_id: str):
        """
        POST /api/plantas (R7).
        El usuario autenticado registra una planta y la vincula a un dispositivo.
        La respuesta trae el token del dispositivo, que se le entrega al ESP32 o al simulador.
        """
        datos = peticion_http.cuerpo_json()
        registrada = registrar_planta.registrar_planta(
            usuario_id=usuario_id,
            nombre=peticion_http.texto(datos, "nombre"),
            especie=peticion_http.texto(datos, "especie"),
            dispositivo_id=peticion_http.id_dispositivo(datos),
        )
        return jsonify({
            "planta": planta_a_json(registrada.planta),
            "token_dispositivo": registrada.token_dispositivo,
        }), 201

    @api_bp.route("/plantas/<planta_id>/token-dispositivo", methods=["POST"])
    @requiere_usuario(verificador)
    def generar_token_dispositivo(planta_id: str, usuario_id: str):
        """
        POST /api/plantas/{id}/token-dispositivo (R7).
        El dueño de la planta obtiene un token nuevo para su dispositivo.
        """
        token = emitir_token_dispositivo.emitir_token_dispositivo(usuario_id=usuario_id, planta_id=planta_id)
        return jsonify({"planta_id": planta_id, "token_dispositivo": token}), 200

    @api_bp.route("/plantas/<planta_id>/estado", methods=["GET"])
    @requiere_usuario(verificador)
    def consultar_estado_planta(planta_id: str, usuario_id: str):
        """
        GET /api/plantas/{id}/estado (R5, R6, R7).
        Retorna el estado agregado y última lectura de la planta.
        El dominio verifica la propiedad y rechaza con 403 si pertenece a otro usuario.
        """
        estado = consultar_estado.consultar_estado(usuario_id=usuario_id, planta_id=planta_id)
        return jsonify(estado_actual_a_json(estado)), 200

    @api_bp.route("/plantas/<planta_id>/historial", methods=["GET"])
    @requiere_usuario(verificador)
    def consultar_historial_planta(planta_id: str, usuario_id: str):
        """
        GET /api/plantas/{id}/historial (R5, R6, R7).
        Retorna la lista de lecturas históricas de la planta.
        """
        limite = peticion_http.limite_de_consulta()
        historial = consultar_historial.consultar_historial(
            usuario_id=usuario_id,
            planta_id=planta_id,
            limite=limite,
        )
        return jsonify([registro_a_json(r) for r in historial]), 200

    # -------------------------------------------------------------------------
    # Vinculación y Autorización de Sesiones QR + WebSockets (/api/auth/qr/...)
    # -------------------------------------------------------------------------
    if generar_sesion_qr is not None:
        @api_bp.route("/auth/qr/generar", methods=["POST"])
        @api_bp.route("/v1/auth/qr/generar", methods=["POST"])
        def crear_sesion_qr():
            """POST /api/auth/qr/generar - Crea una sesión efímera QR en estado PENDIENTE."""
            datos = request.get_json(silent=True) if request.is_json else {}
            if not isinstance(datos, dict):
                datos = {}
            sesion_id = datos.get("session_id") or datos.get("id")
            dispositivo_id = datos.get("dispositivo_id")
            planta_id = datos.get("planta_id")
            sesion = generar_sesion_qr.generar_sesion_qr(
                sesion_id=str(sesion_id) if sesion_id else None,
                dispositivo_id=str(dispositivo_id) if dispositivo_id else None,
                planta_id=str(planta_id) if planta_id else None,
            )
            return jsonify(sesion_qr_a_json(sesion)), 201

    if consultar_sesion_qr is not None:
        @api_bp.route("/auth/qr/<session_id>", methods=["GET"])
        @api_bp.route("/v1/auth/qr/<session_id>", methods=["GET"])
        def obtener_estado_sesion_qr(session_id: str):
            """GET /api/auth/qr/<session_id> - Consulta el estado actual de una sesión QR."""
            sesion = consultar_sesion_qr.consultar_sesion_qr(sesion_id=session_id)
            return jsonify(sesion_qr_a_json(sesion)), 200

    if autorizar_sesion_qr is not None:
        @api_bp.route("/auth/qr/<session_id>/autorizar", methods=["POST"])
        @api_bp.route("/v1/auth/qr/<session_id>/autorizar", methods=["POST"])
        def confirmar_autorizacion_qr(session_id: str):
            """
            POST /api/auth/qr/<session_id>/autorizar
            Autoriza la sesión QR (emitiendo el token de dispositivo de la planta o asignando el token)
            y notifica en tiempo real por WebSocket a la sala qr_{session_id}.
            """
            datos = peticion_http.cuerpo_json()
            planta_id = datos.get("planta_id")
            usuario_id = datos.get("usuario_id")
            token = datos.get("token")

            # Si la petición trae cabecera Authorization: Bearer <token_usuario>, extraemos usuario_id verificado
            cabecera_auth = request.headers.get("Authorization", "").strip()
            if cabecera_auth.lower().startswith("bearer "):
                token_bearer = cabecera_auth.split(" ", 1)[1].strip()
                try:
                    identidad = verificador.verificar(token_bearer)
                except TokenRechazadoError as err:
                    return jsonify({"error": err.codigo, "mensaje": err.mensaje, "detalle": {}}), 401
                if identidad.alcance != ALCANCE_USUARIO:
                    return jsonify({
                        "error": "ACCESO_DENEGADO",
                        "mensaje": "Este endpoint requiere un token con alcance de usuario.",
                        "detalle": {"scope_presente": identidad.alcance},
                    }), 403
                usuario_id = identidad.sujeto

            if not usuario_id or not isinstance(usuario_id, str) or not usuario_id.strip():
                raise ParametroInvalidoError("usuario_id", "El parámetro 'usuario_id' es obligatorio.")
            if (not token or not isinstance(token, str) or not token.strip()) and not planta_id:
                raise ParametroInvalidoError(
                    "token", "Se requiere 'token' o 'planta_id' para autorizar la sesión QR."
                )

            sesion = autorizar_sesion_qr.autorizar_sesion_qr(
                sesion_id=session_id,
                usuario_id=usuario_id.strip(),
                token=token.strip() if isinstance(token, str) and token.strip() else None,
                planta_id=str(planta_id).strip() if planta_id else None,
            )
            return jsonify(sesion_qr_a_json(sesion)), 200

    return api_bp

