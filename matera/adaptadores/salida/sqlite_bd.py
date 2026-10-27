"""
Infraestructura compartida de SQLite.

- conectar(): abre una conexión que devuelve filas con acceso por nombre de columna.
- inicializar_bd(): ejecuta los scripts de data/bd/ (esquema, carga de especies y,
  si se pide, datos de demostración). Lo llama el punto de composición (matera/app.py),
  no cada adaptador: así ningún adaptador depende de otro para que existan sus tablas.

También se puede usar desde la terminal para crear la base a mano:
    python -m matera.adaptadores.salida.sqlite_bd data/matera.db --demo
"""
import argparse
import sqlite3
from pathlib import Path

CARPETA_SCRIPTS = Path(__file__).resolve().parents[3] / "data" / "bd"
SCRIPT_ESQUEMA = CARPETA_SCRIPTS / "esquema.sql"
SCRIPT_ESPECIES = CARPETA_SCRIPTS / "carga_especies.sql"
SCRIPT_DEMO = CARPETA_SCRIPTS / "datos_demo.sql"


def conectar(ruta_bd: str) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta_bd)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd(ruta_bd: str, datos_demo: bool = False) -> None:
    """Crea las tablas que falten y carga las especies; con datos_demo también a Ana y Carlos."""
    if ruta_bd != ":memory:":
        Path(ruta_bd).parent.mkdir(parents=True, exist_ok=True)

    scripts = [SCRIPT_ESQUEMA, SCRIPT_ESPECIES] + ([SCRIPT_DEMO] if datos_demo else [])
    with conectar(ruta_bd) as conexion:
        for script in scripts:
            conexion.executescript(script.read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea la base de datos SQLite de SmartPlantBase")
    parser.add_argument("ruta", nargs="?", default="data/matera.db", help="Archivo de la base de datos")
    parser.add_argument("--demo", action="store_true", help="Cargar también los usuarios y plantas de demostración")
    args = parser.parse_args()
    inicializar_bd(args.ruta, datos_demo=args.demo)
    print(f"Base de datos lista en {args.ruta}" + (" (con datos de demostración)" if args.demo else ""))
