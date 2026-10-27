"""
Punto Único de Composición y Ensamblado Hexagonal (Composition Root).
Instancia adaptadores de salida, inyecta dependencias en los servicios del dominio
y conecta los adaptadores de entrada (Blueprints HTTP).
"""
import logging
import os
import secrets
from pathlib import Path
from typing import Optional
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from matera.adaptadores.entrada.api_dispositivos import crear_api_dispositivos_blueprint
from matera.adaptadores.entrada.api_front import crear_api_front_blueprint
from matera.adaptadores.entrada.verificador_jwt import JwtVerificadorToken
from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.adaptadores.salida.hasher_werkzeug import WerkzeugHasherAdapter
from matera.adaptadores.salida.historial_bd import BdHistorialLecturasAdapter
from matera.adaptadores.salida.plantas_bd import BdPlantasAdapter
from matera.adaptadores.salida.sqlite_bd import inicializar_bd
from matera.adaptadores.salida.tabla_bd import BdTablaReferenciaAdapter
from matera.adaptadores.salida.tabla_csv import CsvTablaReferenciaAdapter
from matera.adaptadores.salida.usuarios_bd import BdUsuariosAdapter
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
from matera.dominio.casos_uso import (
    AutenticarUsuario,
    ConsultarEspecies,
    ConsultarEstado,
    ConsultarHistorial,
    EmitirTokenDispositivo,
    ListarPlantas,
    RegistrarLectura,
    RegistrarPlanta,
    ValidarLectura,
)


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

    @app.errorhandler(DispositivoYaVinculadoError)
    def manejar_dispositivo_ya_vinculado(error: DispositivoYaVinculadoError):
        cuerpo = {
            "error": "DISPOSITIVO_YA_VINCULADO",
            "mensaje": str(error),
            "detalle": {"dispositivo_id": error.dispositivo_id},
        }
        return jsonify(cuerpo), 409

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


def _clave_temporal() -> str:
    """
    Si no se configuró JWT_SECRET, se inventa una clave al azar para esta ejecución.
    Sirve para probar, pero los tokens dejan de valer cuando se reinicia el servidor.
    """
    logging.getLogger(__name__).warning(
        "JWT_SECRET no está configurada: se usa una clave temporal. "
        "Copie .env.example a .env y defina JWT_SECRET para que los tokens sobrevivan a un reinicio."
    )
    return secrets.token_urlsafe(32)


def create_app(
    driver_tabla: Optional[str] = None,
    ruta_csv: Optional[str] = None,
    ruta_bd: Optional[str] = None,
    clave_jwt: Optional[str] = None,
    datos_demo: Optional[bool] = None,
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

    # 1b. Base de datos: tablas desde data/bd/esquema.sql; los datos de demostración
    #     (Ana y Carlos) solo se cargan si se piden con CARGAR_DATOS_DEMO=1.
    if datos_demo is None:
        datos_demo = os.getenv("CARGAR_DATOS_DEMO", "1").strip() == "1"
    inicializar_bd(ruta_bd, datos_demo=datos_demo)

    # 2. Selección del adaptador de TablaReferenciaPort (R4: CSV vs SQLite)
    modo_tabla = (driver_tabla or os.getenv("TABLA_REFERENCIA_DRIVER", "csv")).strip().lower()
    if modo_tabla == "bd":
        tabla_referencia = BdTablaReferenciaAdapter(ruta_bd)
    else:
        tabla_referencia = CsvTablaReferenciaAdapter(ruta_csv)

    # 3. Adaptadores SQLite: uno por puerto de salida (R5, R7)
    historial = BdHistorialLecturasAdapter(ruta_bd)
    usuarios = BdUsuariosAdapter(ruta_bd)
    plantas = BdPlantasAdapter(ruta_bd)

    # 4. Tokens JWT (R7): la misma clave firma (emisor, salida) y verifica (verificador, entrada)
    clave_jwt = clave_jwt or os.getenv("JWT_SECRET") or _clave_temporal()
    emisor_token = JwtEmisorTokenAdapter(secret_key=clave_jwt)
    verificador_token = JwtVerificadorToken(secret_key=clave_jwt)

    # 4b. Adaptador de hash de contraseñas (R7)
    hasher = WerkzeugHasherAdapter()

    # 5. Casos de uso del dominio: cada uno recibe solo los puertos de salida que necesita
    validar_lectura = ValidarLectura(tabla_referencia)
    consultar_especies = ConsultarEspecies(tabla_referencia)
    registrar_lectura = RegistrarLectura(tabla_referencia, plantas, historial)
    consultar_estado = ConsultarEstado(tabla_referencia, plantas, historial)
    consultar_historial = ConsultarHistorial(plantas, historial)
    listar_plantas = ListarPlantas(plantas)
    registrar_planta = RegistrarPlanta(tabla_referencia, plantas, emisor_token)
    emitir_token_dispositivo = EmitirTokenDispositivo(plantas, emisor_token)
    autenticar = AutenticarUsuario(usuarios, hasher, emisor_token)

    # 6. Adaptadores de entrada (Blueprints): cada endpoint recibe solo su puerto de entrada
    app.register_blueprint(crear_api_front_blueprint(
        validar_lectura=validar_lectura,
        consultar_especies=consultar_especies,
        consultar_estado=consultar_estado,
        consultar_historial=consultar_historial,
        listar_plantas=listar_plantas,
        registrar_planta=registrar_planta,
        emitir_token_dispositivo=emitir_token_dispositivo,
        autenticar=autenticar,
        verificador=verificador_token,
    ))
    app.register_blueprint(crear_api_dispositivos_blueprint(
        puerto_registro=registrar_lectura,
        verificador=verificador_token,
    ))

    # 7. Manejadores de error
    registrar_manejadores_error(app)

    return app
