"""
Punto de entrada de la aplicación Flask (SmartPlantBase).
Delega al Composition Root de Arquitectura Hexagonal en matera.app.
"""
import os
from typing import Optional
from flask import Flask

from matera.app import create_app

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5000))
    aplicacion = create_app()
    print(f"Iniciando API de Diagnóstico de Plantas en http://localhost:{puerto}")
    aplicacion.run(host="0.0.0.0", port=puerto, debug=True)
