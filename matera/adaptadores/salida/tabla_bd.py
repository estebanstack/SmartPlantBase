"""
Adaptador de Salida: Tabla de Referencia en SQLite (R4).
Implementa TablaReferenciaPort leyendo las especies desde la base de datos relacional.
Intercambiable con CsvTablaReferenciaAdapter mediante configuración sin tocar el dominio.
Las tablas las crea data/bd/esquema.sql (ver sqlite_bd.py); este adaptador solo las consulta.
El formato de las columnas lo define columnas_referencia.py (el mismo que usa tabla_csv.py),
así un parámetro nuevo no obliga a cambiar este archivo, solo a agregar sus columnas.
"""
from pathlib import Path
from typing import List, Optional

from matera.adaptadores.salida.columnas_referencia import especie_desde_fila
from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.modelo import Especie
from matera.dominio.puertos.salida import TablaReferenciaPort


class BdTablaReferenciaAdapter(TablaReferenciaPort):
    """
    Adaptador de salida que implementa TablaReferenciaPort conectándose a SQLite.
    Garantiza que la lógica botánica sea indistinguible de la leída en CSV.
    """

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        with conectar(self._ruta) as con:
            fila = con.execute(
                "SELECT * FROM especies WHERE lower(nombre) = lower(?)", (nombre.strip(),)
            ).fetchone()
        return especie_desde_fila(fila["nombre"], dict(fila)) if fila else None

    def obtener_todas(self) -> List[Especie]:
        with conectar(self._ruta) as con:
            filas = con.execute("SELECT * FROM especies ORDER BY nombre ASC").fetchall()
        return [especie_desde_fila(fila["nombre"], dict(fila)) for fila in filas]
