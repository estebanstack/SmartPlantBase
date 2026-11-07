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
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from matera.adaptadores.entrada.api_dispositivos import crear_api_dispositivos_blueprint
from matera.adaptadores.entrada.api_front import crear_api_front_blueprint
from matera.adaptadores.entrada.errores_http import registrar_manejadores_error
from matera.adaptadores.entrada.verificador_jwt import JwtVerificadorToken
from matera.adaptadores.entrada.websocket_handlers import registrar_websocket_handlers
from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.adaptadores.salida.hasher_werkzeug import WerkzeugHasherAdapter
from matera.adaptadores.salida.historial_bd import BdHistorialLecturasAdapter
from matera.adaptadores.salida.notificador_ws import SocketIONotificadorAdapter
from matera.adaptadores.salida.plantas_bd import BdPlantasAdapter
from matera.adaptadores.salida.sesiones_qr_memoria import MemoriaSesionesQRAdapter
from matera.adaptadores.salida.sqlite_bd import inicializar_bd
from matera.adaptadores.salida.tabla_bd import BdTablaReferenciaAdapter
from matera.adaptadores.salida.tabla_csv import CsvTablaReferenciaAdapter
from matera.adaptadores.salida.usuarios_bd import BdUsuariosAdapter
from matera.dominio.casos_uso import (
    AutenticarUsuario,
    AutorizarSesionQR,
    ConsultarEspecies,
    ConsultarEstado,
    ConsultarHistorial,
    ConsultarSesionQR,
    EmitirTokenDispositivo,
    GenerarSesionQR,
    ListarPlantas,
    RegistrarLectura,
    RegistrarPlanta,
    ValidarLectura,
)
from matera.dominio.puertos.salida import SesionesQRPort


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
    sesion_qr_repo: Optional[SesionesQRPort] = None,
    socketio_instance: Optional[SocketIO] = None,
) -> Flask:
    """
    Fábrica de la aplicación Flask en Arquitectura Hexagonal.
    Ensambla adaptadores de salida y entrada (REST + WebSockets) alrededor del núcleo de dominio.
    """
    load_dotenv()
    app = Flask(__name__)
    app.json.sort_keys = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 0. Servidor WebSocket (Flask-SocketIO) para salas qr_{session_id} y user_{usuario_id}
    sio = socketio_instance or SocketIO()
    sio.init_app(app, cors_allowed_origins="*")
    app.socketio = sio


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

    # 4c. Adaptadores de sesiones QR en memoria y notificaciones en tiempo real (WebSockets)
    sesiones_qr = sesion_qr_repo if sesion_qr_repo is not None else MemoriaSesionesQRAdapter()
    notificador_ws = SocketIONotificadorAdapter(sio)

    # 5. Casos de uso del dominio: cada uno recibe solo los puertos de salida que necesita
    validar_lectura = ValidarLectura(tabla_referencia)
    consultar_especies = ConsultarEspecies(tabla_referencia)
    registrar_lectura = RegistrarLectura(
        tabla_referencia, plantas, historial, notificador=notificador_ws
    )
    consultar_estado = ConsultarEstado(tabla_referencia, plantas, historial)
    consultar_historial = ConsultarHistorial(plantas, historial)
    listar_plantas = ListarPlantas(plantas)
    registrar_planta = RegistrarPlanta(tabla_referencia, plantas, emisor_token)
    emitir_token_dispositivo = EmitirTokenDispositivo(plantas, emisor_token)
    autenticar = AutenticarUsuario(usuarios, hasher, emisor_token)
    generar_sesion_qr = GenerarSesionQR(sesiones_qr)
    consultar_sesion_qr = ConsultarSesionQR(sesiones_qr)
    autorizar_sesion_qr = AutorizarSesionQR(
        sesiones_qr,
        plantas=plantas,
        emisor_token=emisor_token,
        notificador=notificador_ws,
    )

    # 5b. Adaptador de entrada WebSocket (salas qr_{id} y user_{id})
    registrar_websocket_handlers(
        socketio=sio,
        autorizar_qr_use_case=autorizar_sesion_qr,
        consultar_qr_use_case=consultar_sesion_qr,
        verificador=verificador_token,
    )

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
        generar_sesion_qr=generar_sesion_qr,
        consultar_sesion_qr=consultar_sesion_qr,
        autorizar_sesion_qr=autorizar_sesion_qr,
        socketio=sio,
    ))
    app.register_blueprint(crear_api_dispositivos_blueprint(
        puerto_registro=registrar_lectura,
        verificador=verificador_token,
    ))


    # 7. Traducción de errores a JSON (adaptadores/entrada/errores_http.py)
    registrar_manejadores_error(app)

    return app
