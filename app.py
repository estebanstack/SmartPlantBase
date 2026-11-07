"""
Punto de entrada de la aplicación Flask (SmartPlantBase).
Carga la configuración del archivo .env (si existe) y delega al punto de
composición de la arquitectura hexagonal en matera.app.
"""
import os

from dotenv import load_dotenv

from matera.app import create_app

if __name__ == "__main__":
    load_dotenv()  # lee JWT_SECRET, TABLA_REFERENCIA_DRIVER y PORT desde .env
    puerto = int(os.getenv("PORT", 5000))
    aplicacion = create_app()
    print(f"Iniciando API y Servidor WebSocket en http://localhost:{puerto}")
    aplicacion.socketio.run(aplicacion, host="0.0.0.0", port=puerto, debug=True, allow_unsafe_werkzeug=True)

