"""Adaptador de Salida: plantas en SQLite (R7). Implementa PlantasPort."""
import sqlite3
from pathlib import Path
from typing import List, Optional

from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.modelo import Planta
from matera.dominio.puertos.salida import PlantasPort

_COLUMNAS = "id, nombre, especie, usuario_id, dispositivo_id"


class BdPlantasAdapter(PlantasPort):

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def _conectar(self) -> sqlite3.Connection:
        return conectar(self._ruta)

    def _buscar_una(self, condicion: str, valor: str) -> Optional[Planta]:
        with self._conectar() as con:
            fila = con.execute(f"SELECT {_COLUMNAS} FROM plantas WHERE {condicion} = ?", (valor,)).fetchone()
        return self._a_planta(fila) if fila else None

    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        return self._buscar_una("id", planta_id)

    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        return self._buscar_una("dispositivo_id", dispositivo_id)

    def listar_plantas_por_usuario(self, usuario_id: str) -> List[Planta]:
        with self._conectar() as con:
            filas = con.execute(
                f"SELECT {_COLUMNAS} FROM plantas WHERE usuario_id = ? ORDER BY id ASC", (usuario_id,)
            ).fetchall()
        return [self._a_planta(f) for f in filas]

    def guardar_planta(self, planta: Planta) -> None:
        with self._conectar() as con:
            con.execute(
                f"INSERT INTO plantas ({_COLUMNAS}) VALUES (?, ?, ?, ?, ?)",
                (planta.id, planta.nombre, planta.especie, planta.usuario_id, planta.dispositivo_id),
            )

    @staticmethod
    def _a_planta(fila: sqlite3.Row) -> Planta:
        return Planta(
            id=fila["id"],
            nombre=fila["nombre"],
            especie=fila["especie"],
            usuario_id=fila["usuario_id"],
            dispositivo_id=fila["dispositivo_id"],
        )
