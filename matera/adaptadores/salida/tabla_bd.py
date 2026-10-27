"""
Adaptador de Salida: Tabla de Referencia en SQLite (R4).
Implementa TablaReferenciaPort leyendo las especies desde la base de datos relacional.
Intercambiable con CsvTablaReferenciaAdapter mediante configuración sin tocar el dominio.
"""
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional

from matera.dominio.modelo import (
    LIMITES_FISICOS,
    Especie,
    RangoParametro,
)
from matera.dominio.puertos.salida import TablaReferenciaPort


def inicializar_bd(ruta_bd: str | Path) -> None:
    """Crea las tablas y carga datos de semilla si la base de datos es nueva o no existen."""
    ruta = str(ruta_bd)
    # Crear directorio si no es :memory:
    if ruta != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(ruta) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS especies (
                nombre TEXT PRIMARY KEY,
                humedad_min REAL NOT NULL,
                humedad_max REAL NOT NULL,
                luz_min REAL NOT NULL,
                luz_max REAL NOT NULL,
                temp_min REAL NOT NULL,
                temp_max REAL NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS plantas (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                especie TEXT NOT NULL,
                usuario_id TEXT NOT NULL,
                dispositivo_id TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historial_lecturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planta_id TEXT NOT NULL,
                dispositivo_id TEXT,
                especie TEXT NOT NULL,
                humedad REAL NOT NULL,
                luz REAL NOT NULL,
                temperatura REAL NOT NULL,
                estado_planta TEXT NOT NULL,
                marca_tiempo TEXT NOT NULL,
                FOREIGN KEY(planta_id) REFERENCES plantas(id)
            )
        """)

        # Semilla de las 5 especies del Anexo B
        especies_semilla = [
            ("sansevieria", 20.0, 45.0, 200.0, 1500.0, 15.0, 29.0),
            ("potos", 40.0, 70.0, 300.0, 1200.0, 18.0, 30.0),
            ("suculenta", 10.0, 30.0, 800.0, 2500.0, 15.0, 32.0),
            ("helecho", 60.0, 85.0, 150.0, 800.0, 16.0, 26.0),
            ("lavanda", 25.0, 50.0, 1000.0, 3000.0, 15.0, 30.0),
        ]
        cur.executemany("""
            INSERT OR IGNORE INTO especies (nombre, humedad_min, humedad_max, luz_min, luz_max, temp_min, temp_max)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, especies_semilla)

        # Semilla de usuarios y plantas de demostración (clave: clave123)
        import hashlib
        pwd_hash = hashlib.sha256(b"clave123").hexdigest()
        usuarios_semilla = [
            ("usr-ana", "Ana María", "ana@matera.edu.co", pwd_hash),
            ("usr-carlos", "Carlos Ruiz", "carlos@matera.edu.co", pwd_hash),
        ]
        cur.executemany("""
            INSERT OR IGNORE INTO usuarios (id, nombre, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, usuarios_semilla)

        plantas_semilla = [
            ("planta-01", "Sansevieria de Sala", "sansevieria", "usr-ana", "esp32-01"),
            ("planta-02", "Helecho de Balcón", "helecho", "usr-carlos", "esp32-02"),
        ]
        cur.executemany("""
            INSERT OR IGNORE INTO plantas (id, nombre, especie, usuario_id, dispositivo_id)
            VALUES (?, ?, ?, ?, ?)
        """, plantas_semilla)

        con.commit()


class BdTablaReferenciaAdapter(TablaReferenciaPort):
    """
    Adaptador de salida que implementa TablaReferenciaPort conectándose a SQLite.
    Garantiza que la lógica botánica sea indistinguible de la leída en CSV.
    """

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)
        inicializar_bd(self._ruta)

    def _conectar(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._ruta)
        con.row_factory = sqlite3.Row
        return con

    def _mapear_fila_a_especie(self, fila: sqlite3.Row) -> Especie:
        nombre = fila["nombre"]
        rangos = {
            "humedad": RangoParametro(
                minimo=float(fila["humedad_min"]),
                maximo=float(fila["humedad_max"]),
                unidad=LIMITES_FISICOS["humedad"].unidad,
            ),
            "luz": RangoParametro(
                minimo=float(fila["luz_min"]),
                maximo=float(fila["luz_max"]),
                unidad=LIMITES_FISICOS["luz"].unidad,
            ),
            "temperatura": RangoParametro(
                minimo=float(fila["temp_min"]),
                maximo=float(fila["temp_max"]),
                unidad=LIMITES_FISICOS["temperatura"].unidad,
            ),
        }
        return Especie(nombre=nombre, rangos=rangos)

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT nombre, humedad_min, humedad_max, luz_min, luz_max, temp_min, temp_max
                FROM especies
                WHERE lower(nombre) = lower(?)
            """, (nombre.strip(),))
            fila = cur.fetchone()
            if fila is None:
                return None
            return self._mapear_fila_a_especie(fila)

    def obtener_todas(self) -> List[Especie]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT nombre, humedad_min, humedad_max, luz_min, luz_max, temp_min, temp_max
                FROM especies
                ORDER BY nombre ASC
            """)
            filas = cur.fetchall()
            return [self._mapear_fila_a_especie(fila) for fila in filas]
