"""
Punto Único de Composición y Ensamblado Hexagonal (Composition Root).
Instancia adaptadores de salida, inyecta dependencias en los servicios del dominio
y conecta los adaptadores de entrada (Blueprints HTTP).
"""
import os
from pathlib import Path
from typing import Optional
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from matera.adaptadores.entrada.api_dispositivos import crear_api_dispositivos_blueprint
from matera.adaptadores.entrada.api_front import crear_api_front_blueprint
from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.adaptadores.salida.historial_bd import BdHistorialYPlantasAdapter
from matera.adaptadores.salida.tabla_bd import BdTablaReferenciaAdapter
from matera.adaptadores.salida.tabla_csv import CsvTablaReferenciaAdapter
from matera.dominio.excepciones import (
    AccesoNoAutorizadoPlantaError,
    CredencialesInvalidasError,
    DispositivoNoEncontradoError,
    EspecieNoSoportadaError,
    ParametroInvalidoError,
    PlantaNoEncontradaError,
    UsuarioYaExisteError,
)
from matera.dominio.validador import ServicioMateraDominio


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

    @app.errorhandler(PlantaNoEncontradaError)
    def manejar_planta_no_encontrada(error: PlantaNoEncontradaError):
        cuerpo = {
            "error": "PLANTA_NO_ENCONTRADA",
            "mensaje": str(error),
            "detalle": {"planta_id": error.planta_id},
        }
        return jsonify(cuerpo), 404

    @app.errorhandler(DispositivoNoEncontradoError)
    def manejar_dispositivo_no_encontrado(error: DispositivoNoEncontradoError):
        cuerpo = {
            "error": "DISPOSITIVO_NO_ENCONTRADO",
            "mensaje": str(error),
            "detalle": {"dispositivo_id": error.dispositivo_id},
        }
        return jsonify(cuerpo), 404

    @app.errorhandler(AccesoNoAutorizadoPlantaError)
    def manejar_acceso_no_autorizado(error: AccesoNoAutorizadoPlantaError):
        cuerpo = {
            "error": "ACCESO_DENEGADO",
            "mensaje": str(error),
            "detalle": {"usuario_id": error.usuario_id, "planta_id": error.planta_id},
        }
        return jsonify(cuerpo), 403

    @app.errorhandler(UsuarioYaExisteError)
    def manejar_usuario_ya_existe(error: UsuarioYaExisteError):
        cuerpo = {
            "error": "USUARIO_YA_EXISTE",
            "mensaje": str(error),
            "detalle": {"email": error.email},
        }
        return jsonify(cuerpo), 409

    @app.errorhandler(CredencialesInvalidasError)
    def manejar_credenciales_invalidas(error: CredencialesInvalidasError):
        cuerpo = {
            "error": "CREDENCIALES_INVALIDAS",
            "mensaje": str(error),
            "detalle": {},
        }
        return jsonify(cuerpo), 401

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
        app.logger.exception("Error interno no controlado", exc_info=error)
        cuerpo = {
            "error": "ERROR_INTERNO_SERVIDOR",
            "mensaje": "Ocurrió un error inesperado al procesar la solicitud.",
        }
        return jsonify(cuerpo), 500


def create_app(
    driver_tabla: Optional[str] = None,
    ruta_csv: Optional[str] = None,
    ruta_bd: Optional[str] = None,
) -> Flask:
    """
    Fábrica de la aplicación Flask en Arquitectura Hexagonal.
    Ensambla adaptadores de salida y entrada alrededor del núcleo de dominio.
    """
    app = Flask(__name__)
    app.json.sort_keys = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 1. Configuración de rutas por defecto
    ruta_base = Path(__file__).parent.parent
    if ruta_csv is None:
        ruta_csv = str(ruta_base / "data" / "especies_referencia.csv")
    if ruta_bd is None:
        ruta_bd = str(ruta_base / "data" / "matera.db")

    # 2. Selección del adaptador de TablaReferenciaPort (R4: CSV vs SQLite)
    modo_tabla = (driver_tabla or os.getenv("TABLA_REFERENCIA_DRIVER", "csv")).strip().lower()
    if modo_tabla == "bd":
        tabla_referencia = BdTablaReferenciaAdapter(ruta_bd)
    else:
        tabla_referencia = CsvTablaReferenciaAdapter(ruta_csv)

    # 3. Adaptador de persistencia SQLite para historial de lecturas y usuarios/plantas (R5, R7)
    persistencia_bd = BdHistorialYPlantasAdapter(ruta_bd)

    # 4. Adaptador de Emisión de Tokens JWT (R7)
    clave_jwt = os.getenv("JWT_SECRET", "matera-secret-key-arquitectura-2026-segura")
    emisor_token = JwtEmisorTokenAdapter(secret_key=clave_jwt)

    # 5. Núcleo de Dominio (Casos de uso / Puertos de entrada)
    servicio_dominio = ServicioMateraDominio(
        tabla_referencia=tabla_referencia,
        historial_lecturas=persistencia_bd,
        usuarios_plantas=persistencia_bd,
        emisor_token=emisor_token,
    )

    # 6. Registro de Adaptadores de Entrada (Blueprints)
    app.register_blueprint(crear_api_front_blueprint(
        puerto_validacion=servicio_dominio,
        puerto_consultas=servicio_dominio,
        puerto_auth=servicio_dominio,
        emisor_jwt=emisor_token,
    ))
    app.register_blueprint(crear_api_dispositivos_blueprint(
        puerto_registro=servicio_dominio,
        emisor_jwt=emisor_token,
    ))

    # 5. Manejadores de error
    registrar_manejadores_error(app)

    return app
