"""
Adaptador de Entrada: Controlador REST para la Interfaz Web, Auth y Consulta de Plantas (R1, R5, R6, R7).
Solo rutas: cada una lee la petición (peticion_http.py), llama a su puerto de entrada
y devuelve el resultado en JSON (serializacion.py). Los errores los traduce errores_http.py.
"""
from flask import Blueprint, jsonify

from matera.adaptadores.entrada import peticion_http
from matera.adaptadores.entrada.seguridad import VerificadorTokenPort, requiere_usuario
from matera.adaptadores.entrada.serializacion import (
    diagnostico_a_json,
    especie_a_json,
    estado_actual_a_json,
    planta_a_json,
    registro_a_json,
    sesion_a_json,
)
from matera.dominio.puertos.entrada import (
    AutenticarUsuarioPort,
    ConsultarEspeciesPort,
    ConsultarEstadoPort,
    ConsultarHistorialPort,
    EmitirTokenDispositivoPort,
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
        Exige JWT de usuario (R7). El usuario_id no se usa: el diagnóstico manual
        no depende de quién lo pida, pero solo usuarios con sesión pueden pedirlo.
        """
        datos = peticion_http.cuerpo_json()
        diagnostico = validar_lectura.validar(
            especie=peticion_http.texto(datos, "especie").lower(),
            valores=peticion_http.valores_medidos(datos),
        )
        return jsonify(diagnostico_a_json(diagnostico)), 200

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

    return api_bp
