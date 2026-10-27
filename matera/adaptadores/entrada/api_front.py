"""
Adaptador de Entrada: Controlador REST para la Interfaz Web, Auth y Consulta de Plantas (R1, R5, R6, R7).
Traduce HTTP a llamadas a los puertos de entrada y los objetos del dominio a JSON.
Cada endpoint recibe solo el puerto que necesita.
"""
from typing import Any, Dict
from flask import Blueprint, jsonify, request

from matera.adaptadores.entrada.seguridad import VerificadorTokenPort, requiere_usuario
from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS
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
    ListarPlantasPort,
    ValidarLecturaPort,
)


def crear_api_front_blueprint(
    validar_lectura: ValidarLecturaPort,
    consultar_especies: ConsultarEspeciesPort,
    consultar_estado: ConsultarEstadoPort,
    consultar_historial: ConsultarHistorialPort,
    listar_plantas: ListarPlantasPort,
    autenticar: AutenticarUsuarioPort,
    verificador: VerificadorTokenPort,
) -> Blueprint:
    """
    Fábrica del Blueprint REST para clientes web / frontend.
    Conecta las rutas HTTP con los puertos de entrada del hexágono.
    """
    api_bp = Blueprint("api_front", __name__, url_prefix="/api")

    def _parse_float(campo: str, valor: Any) -> float:
        if isinstance(valor, bool):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

    # -------------------------------------------------------------------------
    # R1: Endpoints compatibles con Fase 1 (/api/v1/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/v1/diagnosticos", methods=["POST"])
    def evaluar_diagnostico_v1():
        """
        POST /api/v1/diagnosticos (R1 - Conservar validación de Fase 1).
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

        diagnostico = validar_lectura.validar(
            especie=especie_raw.strip().lower(),
            valores=valores,
        )
        return jsonify(diagnostico_a_json(diagnostico)), 200

    @api_bp.route("/v1/especies", methods=["GET"])
    def listar_especies_v1():
        """
        GET /api/v1/especies (R1).
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
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")

        datos = request.get_json(silent=True) or {}
        nombre = datos.get("nombre", "").strip()
        email = datos.get("email", "").strip()
        password = datos.get("password", "")

        if not nombre:
            raise ParametroInvalidoError("nombre", "El nombre es obligatorio.")
        if not email or "@" not in email:
            raise ParametroInvalidoError("email", "El correo electrónico es inválido.")
        if not password or len(password) < 6:
            raise ParametroInvalidoError("password", "La contraseña debe tener al menos 6 caracteres.")

        sesion = autenticar.registrar_usuario(nombre=nombre, email=email, password=password)
        return jsonify({"mensaje": "Usuario registrado exitosamente.", **sesion_a_json(sesion)}), 201

    @api_bp.route("/auth/login", methods=["POST"])
    def iniciar_sesion():
        """
        POST /api/auth/login (R7).
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")

        datos = request.get_json(silent=True) or {}
        email = datos.get("email", "").strip()
        password = datos.get("password", "")

        if not email:
            raise ParametroInvalidoError("email", "El correo es obligatorio.")
        if not password:
            raise ParametroInvalidoError("password", "La contraseña es obligatoria.")

        sesion = autenticar.iniciar_sesion(email=email, password=password)
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
        limite = request.args.get("limite", default=20, type=int)
        historial = consultar_historial.consultar_historial(
            usuario_id=usuario_id,
            planta_id=planta_id,
            limite=limite,
        )
        return jsonify([registro_a_json(r) for r in historial]), 200

    return api_bp
