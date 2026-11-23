"""Adaptador de Salida: perfil del Matera-Gotchi en SQLite. Implementa GamificacionPort."""
import sqlite3
from pathlib import Path
from typing import Optional

from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.gamificacion import EstadoAnimico, PerfilGamificacion
from matera.dominio.puertos.salida import GamificacionPort


class BdGamificacionAdapter(GamificacionPort):

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def obtener_perfil(self, planta_id: str) -> Optional[PerfilGamificacion]:
        with conectar(self._ruta) as con:
            fila = con.execute("SELECT * FROM gamificacion WHERE planta_id = ?", (planta_id,)).fetchone()
        return self._a_perfil(fila) if fila else None

    def guardar_perfil(self, perfil: PerfilGamificacion) -> None:
        with conectar(self._ruta) as con:
            con.execute(
                """
                INSERT INTO gamificacion
                    (planta_id, xp_total, racha_dias, racha_desde, ultimo_animo, ultima_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(planta_id) DO UPDATE SET
                    xp_total = excluded.xp_total,
                    racha_dias = excluded.racha_dias,
                    racha_desde = excluded.racha_desde,
                    ultimo_animo = excluded.ultimo_animo,
                    ultima_actualizacion = excluded.ultima_actualizacion
                """,
                (
                    perfil.planta_id, perfil.xp_total, perfil.racha_dias, perfil.racha_desde,
                    perfil.ultimo_animo.value, perfil.ultima_actualizacion,
                ),
            )

    @staticmethod
    def _a_perfil(fila: sqlite3.Row) -> PerfilGamificacion:
        return PerfilGamificacion(
            planta_id=fila["planta_id"],
            xp_total=fila["xp_total"],
            racha_dias=fila["racha_dias"],
            racha_desde=fila["racha_desde"],
            ultimo_animo=EstadoAnimico(fila["ultimo_animo"]),
            ultima_actualizacion=fila["ultima_actualizacion"],
        )
