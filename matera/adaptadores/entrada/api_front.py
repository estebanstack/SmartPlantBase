"""
Adaptador de Entrada: Controlador REST para la Interfaz Web, Auth y Consulta de Plantas (R1, R5, R6, R7).
Implementa los endpoints HTTP que conectan a los puertos de entrada ValidarLecturaPort, ConsultarEstadoPort y AutenticarUsuarioPort.
"""
from typing import Any, Dict, Optional
from flask import Blueprint, jsonify, request

from matera.adaptadores.entrada.seguridad_jwt import requiere_jwt_usuario
from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS
from matera.dominio.puertos.entrada import (
    AutenticarUsuarioPort,
    ConsultarEstadoPort,
    ValidarLecturaPort,
)


def crear_api_front_blueprint(
    puerto_validacion: ValidarLecturaPort,
    puerto_consultas: Optional[ConsultarEstadoPort] = None,
    puerto_auth: Optional[AutenticarUsuarioPort] = None,
    emisor_jwt: Optional[JwtEmisorTokenAdapter] = None,
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

        diagnostico = puerto_validacion.validar(
            especie=especie_raw.strip().lower(),
            valores=valores,
        )

        respuesta = {
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
            "recomendaciones": diagnostico.recomendaciones,
        }
        return jsonify(respuesta), 200

    @api_bp.route("/v1/especies", methods=["GET"])
    def listar_especies_v1():
        """
        GET /api/v1/especies (R1).
        """
        especies = puerto_validacion.listar_especies()
        respuesta = [
            {
                "nombre": esp.nombre,
                "rangos": {
                    nombre: {
                        "min": rango.minimo,
                        "max": rango.maximo,
                        "unidad": rango.unidad,
                    }
                    for nombre, rango in esp.rangos.items()
                },
            }
            for esp in especies
        ]
        return jsonify(respuesta), 200

    # -------------------------------------------------------------------------
    # R7: Endpoints de Autenticación (/api/auth/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/auth/registro", methods=["POST"])
    def registrar_usuario():
        """
        POST /api/auth/registro (R7).
        """
        if not puerto_auth:
            return jsonify({"error": "SERVICIO_NO_DISPONIBLE", "mensaje": "Autenticación no disponible."}), 503

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

        resultado = puerto_auth.registrar_usuario(nombre=nombre, email=email, password=password)
        return jsonify({
            "mensaje": "Usuario registrado exitosamente.",
            "token": resultado["token"],
            "usuario": {
                "id": resultado["usuario_id"],
                "nombre": resultado["nombre"],
                "email": resultado["email"],
            },
        }), 201

    @api_bp.route("/auth/login", methods=["POST"])
    def iniciar_sesion():
        """
        POST /api/auth/login (R7).
        """
        if not puerto_auth:
            return jsonify({"error": "SERVICIO_NO_DISPONIBLE", "mensaje": "Autenticación no disponible."}), 503

        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")

        datos = request.get_json(silent=True) or {}
        email = datos.get("email", "").strip()
        password = datos.get("password", "")

        if not email:
            raise ParametroInvalidoError("email", "El correo es obligatorio.")
        if not password:
            raise ParametroInvalidoError("password", "La contraseña es obligatoria.")

        resultado = puerto_auth.iniciar_sesion(email=email, password=password)
        return jsonify({
            "mensaje": "Sesión iniciada correctamente.",
            "token": resultado["token"],
            "usuario": {
                "id": resultado["usuario_id"],
                "nombre": resultado["nombre"],
                "email": resultado["email"],
            },
        }), 200

    # -------------------------------------------------------------------------
    # R5, R6, R7: Endpoints de Consulta de Plantas e Historial (/api/plantas/...)
    # -------------------------------------------------------------------------
    def _verificador_usuario(f):
        if emisor_jwt:
            return requiere_jwt_usuario(emisor_jwt)(f)
        return f

    @api_bp.route("/plantas", methods=["GET"])
    @_verificador_usuario
    def listar_plantas(usuario_id: str):
        """
        GET /api/plantas (R7).
        Lista las plantas registradas que pertenecen al usuario autenticado.
        """
        if not puerto_consultas:
            return jsonify([]), 200

        plantas = puerto_consultas.listar_plantas_usuario(usuario_id)
        return jsonify([
            {
                "id": p.id,
                "nombre": p.nombre,
                "especie": p.especie,
                "usuario_id": p.usuario_id,
                "dispositivo_id": p.dispositivo_id,
            }
            for p in plantas
        ]), 200

    @api_bp.route("/plantas/<planta_id>/estado", methods=["GET"])
    @_verificador_usuario
    def consultar_estado_planta(planta_id: str, usuario_id: str):
        """
        GET /api/plantas/{id}/estado (R5, R6, R7).
        Retorna el estado agregado y última lectura de la planta.
        El dominio verifica la propiedad y rechaza con 403 si pertenece a otro usuario.
        """
        if not puerto_consultas:
            return jsonify({"error": "SERVICIO_NO_DISPONIBLE"}), 503

        estado_agregado = puerto_consultas.consultar_estado(usuario_id=usuario_id, planta_id=planta_id)

        diagnostico_json = None
        if estado_agregado.diagnostico:
            diag = estado_agregado.diagnostico
            diagnostico_json = {
                "especie": diag.especie,
                "estado": diag.estado.value,
                "parametros": [
                    {
                        "nombre": p.nombre,
                        "valor": p.valor,
                        "unidad": p.unidad,
                        "rango_optimo": [p.rango_optimo[0], p.rango_optimo[1]],
                        "estado": p.estado.value,
                    }
                    for p in diag.parametros
                ],
                "recomendaciones": diag.recomendaciones,
            }

        ultima_lectura_json = None
        if estado_agregado.ultima_lectura:
            lec = estado_agregado.ultima_lectura
            ultima_lectura_json = {
                "especie": lec.especie,
                "valores": dict(lec.valores),
                "marca_tiempo": lec.marca_tiempo,
                "dispositivo_id": lec.dispositivo_id,
                "planta_id": lec.planta_id,
            }

        return jsonify({
            "planta": {
                "id": estado_agregado.planta.id,
                "nombre": estado_agregado.planta.nombre,
                "especie": estado_agregado.planta.especie,
                "usuario_id": estado_agregado.planta.usuario_id,
                "dispositivo_id": estado_agregado.planta.dispositivo_id,
            },
            "ultima_lectura": ultima_lectura_json,
            "diagnostico": diagnostico_json,
        }), 200

    @api_bp.route("/plantas/<planta_id>/historial", methods=["GET"])
    @_verificador_usuario
    def consultar_historial_planta(planta_id: str, usuario_id: str):
        """
        GET /api/plantas/{id}/historial (R5, R6, R7).
        Retorna la lista de lecturas históricas de la planta.
        """
        if not puerto_consultas:
            return jsonify([]), 200

        limite = request.args.get("limite", default=20, type=int)
        historial = puerto_consultas.consultar_historial(
            usuario_id=usuario_id,
            planta_id=planta_id,
            limite=limite,
        )
        return jsonify(historial), 200

    return api_bp
