"""
Punto de entrada de la aplicación Flask (Composición de Capas y Ensamblado).
Configura CORS (RA7), inyecta dependencias e inicia el servidor API REST en JSON (RA1, RA8)
y el servidor WebSocket con arquitectura dual (Pre-Auth QR y Post-Auth Usuario).
"""
import os
from pathlib import Path
from typing import Optional
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.exceptions import NotFound

from src.application.use_cases import (
    AutorizarSesionQRUseCase,
    ConsultarSesionQRUseCase,
    EvaluarDiagnosticoUseCase,
    GenerarSesionQRUseCase,
    ListarEspeciesUseCase,
)
from src.infrastructure.repositories.csv_especie_repository import CsvEspecieRepository
from src.infrastructure.repositories.memoria_sesion_qr_repository import MemoriaSesionQRRepository
from src.presentation.controllers import crear_api_blueprint
from src.presentation.error_handlers import registrar_manejadores_error
from src.presentation.websocket_handlers import registrar_websocket_handlers


def create_app(
    ruta_csv: Optional[str] = None,
    sesion_qr_repo: Optional[MemoriaSesionQRRepository] = None,
    socketio_instance: Optional[SocketIO] = None,
) -> Flask:
    """
    Fábrica de la aplicación Flask.
    Ensambla las capas: Infraestructura -> Aplicación -> Presentación (REST + WebSockets).
    """
    app = Flask(__name__)

    # Preserva el orden de los parámetros declarado por el dominio en lugar de
    # ordenar las claves alfabéticamente (afecta el orden del formulario web).
    app.json.sort_keys = False

    # RA7: Habilitar CORS para permitir peticiones desde clientes en otros orígenes o puertos
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configuración de Flask-SocketIO (arquitectura dual en memoria)
    sio = socketio_instance or SocketIO()
    sio.init_app(app, cors_allowed_origins="*")
    app.socketio = sio

    # Ruta por defecto al archivo CSV de especies
    if ruta_csv is None:
        ruta_base = Path(__file__).parent
        ruta_csv = str(ruta_base / "data" / "especies_referencia.csv")

    # Inyección de Dependencias
    # 1. Capa de Infraestructura
    especie_repository = CsvEspecieRepository(ruta_csv)
    sesion_repository = sesion_qr_repo if sesion_qr_repo is not None else MemoriaSesionQRRepository()

    # 2. Capa de Aplicación
    evaluar_use_case = EvaluarDiagnosticoUseCase(especie_repository)
    listar_use_case = ListarEspeciesUseCase(especie_repository)
    generar_qr_use_case = GenerarSesionQRUseCase(sesion_repository)
    autorizar_qr_use_case = AutorizarSesionQRUseCase(sesion_repository)
    consultar_qr_use_case = ConsultarSesionQRUseCase(sesion_repository)

    # Handlers WebSocket (Salas pre-auth 'qr_{id}' y post-auth 'user_{id}')
    registrar_websocket_handlers(
        socketio=sio,
        autorizar_qr_use_case=autorizar_qr_use_case,
        consultar_qr_use_case=consultar_qr_use_case,
    )

    # 3. Capa de Presentación (REST)
    api_bp = crear_api_blueprint(
        evaluar_use_case=evaluar_use_case,
        listar_use_case=listar_use_case,
        generar_qr_use_case=generar_qr_use_case,
        autorizar_qr_use_case=autorizar_qr_use_case,
        consultar_qr_use_case=consultar_qr_use_case,
        socketio=sio,
    )
    app.register_blueprint(api_bp)

    # Rutas para la Demo Interactiva y Frontend Estático
    ruta_frontend = Path(__file__).parent / "frontend"

    @app.route("/")
    def servir_index():
        return send_from_directory(str(ruta_frontend), "index.html")

    @app.route("/demo")
    @app.route("/demo_websocket.html")
    def servir_demo():
        return send_from_directory(str(ruta_frontend), "demo_websocket.html")

    @app.route("/<path:nombre_archivo>")
    def servir_estaticos(nombre_archivo: str):
        archivo = ruta_frontend / nombre_archivo
        if archivo.is_file():
            return send_from_directory(str(ruta_frontend), nombre_archivo)
        raise NotFound()

    # Manejo de errores uniforme (RF6)
    registrar_manejadores_error(app)

    return app


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5000))
    aplicacion = create_app()
    print(f"Iniciando API y WebSockets de Diagnóstico de Plantas en http://localhost:{puerto}")
    aplicacion.socketio.run(aplicacion, host="0.0.0.0", port=puerto, debug=True, allow_unsafe_werkzeug=True)

