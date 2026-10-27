"""
Traducción de errores a HTTP (borde de entrada).
Convierte las excepciones del dominio y los errores de Flask en respuestas JSON
con un cuerpo uniforme: {"error": ..., "mensaje": ..., "detalle": {...}}.
Ninguna respuesta de error sale en HTML (ni siquiera un 405 o un 415 de Flask).
"""
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from matera.dominio.excepciones import (
    AccesoNoAutorizadoPlantaError,
    CredencialesInvalidasError,
    DispositivoNoEncontradoError,
    DispositivoYaVinculadoError,
    EspecieNoSoportadaError,
    ParametroInvalidoError,
    PlantaNoEncontradaError,
    UsuarioYaExisteError,
)

# Código de error para cada estado HTTP que Flask puede generar por su cuenta
_CODIGOS_HTTP = {
    400: "PARAMETRO_INVALIDO",
    401: "AUTORIZACION_REQUERIDA",
    403: "ACCESO_DENEGADO",
    404: "RECURSO_NO_ENCONTRADO",
    405: "METODO_NO_PERMITIDO",
    413: "CUERPO_DEMASIADO_GRANDE",
    415: "TIPO_DE_CONTENIDO_NO_SOPORTADO",
}


def _respuesta(codigo: str, mensaje: str, status: int, detalle=None):
    return jsonify({"error": codigo, "mensaje": mensaje, "detalle": detalle or {}}), status


def registrar_manejadores_error(app: Flask) -> None:
    """Registra en la aplicación la traducción de cada error a su respuesta JSON."""

    # --- Errores del dominio ----------------------------------------------
    @app.errorhandler(EspecieNoSoportadaError)
    def especie_no_soportada(error: EspecieNoSoportadaError):
        return _respuesta("ESPECIE_NO_SOPORTADA", str(error), 404, {"especie": error.especie})

    @app.errorhandler(ParametroInvalidoError)
    def parametro_invalido(error: ParametroInvalidoError):
        return _respuesta("PARAMETRO_INVALIDO", str(error), 400, {"campo": error.campo})

    @app.errorhandler(PlantaNoEncontradaError)
    def planta_no_encontrada(error: PlantaNoEncontradaError):
        return _respuesta("PLANTA_NO_ENCONTRADA", str(error), 404, {"planta_id": error.planta_id})

    @app.errorhandler(DispositivoNoEncontradoError)
    def dispositivo_no_encontrado(error: DispositivoNoEncontradoError):
        return _respuesta(
            "DISPOSITIVO_NO_ENCONTRADO", str(error), 404, {"dispositivo_id": error.dispositivo_id}
        )

    @app.errorhandler(DispositivoYaVinculadoError)
    def dispositivo_ya_vinculado(error: DispositivoYaVinculadoError):
        return _respuesta(
            "DISPOSITIVO_YA_VINCULADO", str(error), 409, {"dispositivo_id": error.dispositivo_id}
        )

    @app.errorhandler(AccesoNoAutorizadoPlantaError)
    def acceso_no_autorizado(error: AccesoNoAutorizadoPlantaError):
        return _respuesta(
            "ACCESO_DENEGADO", str(error), 403,
            {"usuario_id": error.usuario_id, "planta_id": error.planta_id},
        )

    @app.errorhandler(UsuarioYaExisteError)
    def usuario_ya_existe(error: UsuarioYaExisteError):
        return _respuesta("USUARIO_YA_EXISTE", str(error), 409, {"email": error.email})

    @app.errorhandler(CredencialesInvalidasError)
    def credenciales_invalidas(error: CredencialesInvalidasError):
        return _respuesta("CREDENCIALES_INVALIDAS", str(error), 401)

    # --- Errores de Flask / HTTP --------------------------------------------
    @app.errorhandler(400)
    def solicitud_incorrecta(error):
        return _respuesta(
            "PARAMETRO_INVALIDO",
            getattr(error, "description", "Solicitud incorrecta."),
            400,
            {"campo": "body"},
        )

    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return _respuesta("RECURSO_NO_ENCONTRADO", "El recurso o endpoint solicitado no existe.", 404)

    @app.errorhandler(500)
    def error_interno(error):
        app.logger.exception("Error interno no controlado", exc_info=error)
        return _respuesta(
            "ERROR_INTERNO_SERVIDOR", "Ocurrió un error inesperado al procesar la solicitud.", 500
        )

    @app.errorhandler(HTTPException)
    def cualquier_otro_error_http(error: HTTPException):
        """405, 413, 415...: Flask los respondería en HTML; aquí salen en JSON."""
        status = error.code or 500
        return _respuesta(_CODIGOS_HTTP.get(status, "ERROR_HTTP"), error.description or error.name, status)
