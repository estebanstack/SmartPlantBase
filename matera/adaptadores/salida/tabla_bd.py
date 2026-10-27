"""
Adaptador de Salida: Tabla de Referencia en SQLite (R4).
Implementa TablaReferenciaPort leyendo las especies desde la base de datos relacional.
Intercambiable con CsvTablaReferenciaAdapter mediante configuración sin tocar el dominio.
Las tablas las crea data/bd/esquema.sql (ver sqlite_bd.py); este adaptador solo las consulta.
"""
from pathlib import Path
import sqlite3
from typing import List, Optional

from matera.dominio.modelo import (
    LIMITES_FISICOS,
    Especie,
    RangoParametro,
)
from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.puertos.salida import TablaReferenciaPort


class BdTablaReferenciaAdapter(TablaReferenciaPort):
    """
    Adaptador de salida que implementa TablaReferenciaPort conectándose a SQLite.
    Garantiza que la lógica botánica sea indistinguible de la leída en CSV.
    """

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def _conectar(self) -> sqlite3.Connection:
        return conectar(self._ruta)

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
