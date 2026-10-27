"""
Adaptador de Salida: historial de lecturas en SQLite (R5).
Implementa HistorialLecturasPort. Los valores medidos se guardan como JSON en una
sola columna, así un parámetro nuevo (por ejemplo pH) no obliga a cambiar la tabla.
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.modelo import Diagnostico, EstadoPlanta, Lectura, RegistroLectura
from matera.dominio.puertos.salida import HistorialLecturasPort


class BdHistorialLecturasAdapter(HistorialLecturasPort):

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        with conectar(self._ruta) as con:
            con.execute(
                """
                INSERT INTO historial_lecturas
                    (planta_id, dispositivo_id, especie, valores, estado_planta, marca_tiempo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lectura.planta_id or "",
                    lectura.dispositivo_id or "",
                    lectura.especie,
                    json.dumps(dict(lectura.valores)),
                    diagnostico.estado.value,
                    lectura.marca_tiempo,
                ),
            )

    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        registros = self.obtener_historial(planta_id, limite=1)
        return registros[0].lectura if registros else None

    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[RegistroLectura]:
        with conectar(self._ruta) as con:
            filas = con.execute(
                """
                SELECT planta_id, dispositivo_id, especie, valores, estado_planta, marca_tiempo
                FROM historial_lecturas
                WHERE planta_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (planta_id, limite),
            ).fetchall()
        return [self._a_registro(fila) for fila in filas]

    @staticmethod
    def _a_registro(fila: sqlite3.Row) -> RegistroLectura:
        lectura = Lectura(
            especie=fila["especie"],
            valores=json.loads(fila["valores"]),
            marca_tiempo=fila["marca_tiempo"],
            dispositivo_id=fila["dispositivo_id"] or None,
            planta_id=fila["planta_id"] or None,
        )
        return RegistroLectura(lectura=lectura, estado=EstadoPlanta(fila["estado_planta"]))
