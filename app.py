"""
Punto de entrada de la aplicación Flask (Composición de Capas y Ensamblado).
Configura CORS (RA7), inyecta dependencias e inicia el servidor API REST en JSON (RA1, RA8).
"""
import os
from pathlib import Path
from typing import Optional
from flask import Flask
from flask_cors import CORS

from src.application.use_cases import EvaluarDiagnosticoUseCase, ListarEspeciesUseCase
from src.infrastructure.repositories.csv_especie_repository import CsvEspecieRepository
from src.presentation.controllers import crear_api_blueprint
from src.presentation.error_handlers import registrar_manejadores_error


def create_app(ruta_csv: Optional[str] = None) -> Flask:
    """
    Fábrica de la aplicación Flask.
    Ensambla las capas: Infraestructura -> Aplicación -> Presentación.
    """
    app = Flask(__name__)

    # RA7: Habilitar CORS para permitir peticiones desde clientes en otros orígenes o puertos
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ruta por defecto al archivo CSV de especies
    if ruta_csv is None:
        ruta_base = Path(__file__).parent
        ruta_csv = str(ruta_base / "data" / "especies_referencia.csv")

    # Inyección de Dependencias
    # 1. Capa de Infraestructura / Abastecimiento
    especie_repository = CsvEspecieRepository(ruta_csv)

    # 2. Capa de Aplicación
    evaluar_use_case = EvaluarDiagnosticoUseCase(especie_repository)
    listar_use_case = ListarEspeciesUseCase(especie_repository)

    # 3. Capa de Presentación
    api_bp = crear_api_blueprint(evaluar_use_case, listar_use_case)
    app.register_blueprint(api_bp)

    # Manejo de errores uniforme (RF6)
    registrar_manejadores_error(app)

    return app


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5000))
    aplicacion = create_app()
    print(f"Iniciando API de Diagnóstico de Plantas en http://localhost:{puerto}")
    aplicacion.run(host="0.0.0.0", port=puerto, debug=True)
