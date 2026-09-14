"""
Manejadores de errores uniformes para la API REST (RF6).
Asegura que todas las respuestas de error tengan un contrato uniforme:
{
    "error": "CODIGO_ERROR",
    "mensaje": "Descripción legible",
    "detalle": { ... }
}
"""
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from src.domain.exceptions import EspecieNoSoportadaError, ParametroInvalidoError


def registrar_manejadores_error(app: Flask) -> None:
    """Registra los manejadores de error centralizados en la aplicación Flask."""

    @app.errorhandler(EspecieNoSoportadaError)
    def manejar_especie_no_soportada(error: EspecieNoSoportadaError):
        cuerpo = {
            "error": "ESPECIE_NO_SOPORTADA",
            "mensaje": str(error),
            "detalle": {"especie": error.especie},
        }
        return jsonify(cuerpo), 404

    @app.errorhandler(ParametroInvalidoError)
    def manejar_parametro_invalido(error: ParametroInvalidoError):
        cuerpo = {
            "error": "PARAMETRO_INVALIDO",
            "mensaje": str(error),
            "detalle": {"campo": error.campo},
        }
        return jsonify(cuerpo), 400

    @app.errorhandler(400)
    def manejar_bad_request_http(error):
        cuerpo = {
            "error": "PARAMETRO_INVALIDO",
            "mensaje": getattr(error, "description", "Solicitud incorrecta."),
            "detalle": {"campo": "body"},
        }
        return jsonify(cuerpo), 400

    @app.errorhandler(404)
    def manejar_not_found_http(error):
        cuerpo = {
            "error": "RECURSO_NO_ENCONTRADO",
            "mensaje": "El recurso o endpoint solicitado no existe.",
            "detalle": {"ruta": getattr(error, "description", "")},
        }
        return jsonify(cuerpo), 404

    @app.errorhandler(500)
    def manejar_error_servidor_http(error):
        cuerpo = {
            "error": "ERROR_INTERNO_SERVIDOR",
            "mensaje": "Ocurrió un error inesperado al procesar la solicitud.",
            "detalle": {},
        }
        return jsonify(cuerpo), 500

    @app.errorhandler(Exception)
    def manejar_excepcion_inesperada(error: Exception):
        if isinstance(error, HTTPException):
            return jsonify({
                "error": "ERROR_HTTP",
                "mensaje": error.description,
                "detalle": {"codigo": error.code},
            }), error.code

        cuerpo = {
            "error": "ERROR_INTERNO_SERVIDOR",
            "mensaje": "Ocurrió un error inesperado en el servidor.",
            "detalle": {"tipo": type(error).__name__},
        }
        return jsonify(cuerpo), 500
