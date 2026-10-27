"""
Adaptadores de Salida: Historial de Lecturas y Gestión de Usuarios/Plantas en SQLite (R5, R7).
Implementa HistorialLecturasPort y UsuariosPlantasPort para la persistencia relacional en SQLite.
"""
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from matera.adaptadores.salida.tabla_bd import inicializar_bd
from matera.dominio.modelo import Diagnostico, Lectura, Planta, Usuario
from matera.dominio.puertos.salida import HistorialLecturasPort, UsuariosPlantasPort


class BdHistorialLecturasAdapter(HistorialLecturasPort):
    """
    Adaptador de salida para persistir lecturas y consultar historial/última lectura en SQLite.
    """

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)
        inicializar_bd(self._ruta)

    def _conectar(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._ruta)
        con.row_factory = sqlite3.Row
        return con

    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO historial_lecturas (
                    planta_id, dispositivo_id, especie, humedad, luz, temperatura, estado_planta, marca_tiempo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lectura.planta_id or "",
                lectura.dispositivo_id or "",
                lectura.especie,
                lectura.valor_de("humedad"),
                lectura.valor_de("luz"),
                lectura.valor_de("temperatura"),
                diagnostico.estado.value,
                lectura.marca_tiempo,
            ))
            con.commit()

    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT planta_id, dispositivo_id, especie, humedad, luz, temperatura, marca_tiempo
                FROM historial_lecturas
                WHERE planta_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (planta_id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return Lectura(
                especie=fila["especie"],
                valores={
                    "humedad": float(fila["humedad"]),
                    "luz": float(fila["luz"]),
                    "temperatura": float(fila["temperatura"]),
                },
                marca_tiempo=fila["marca_tiempo"],
                dispositivo_id=fila["dispositivo_id"] or None,
                planta_id=fila["planta_id"] or None,
            )

    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[Dict[str, Any]]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, planta_id, dispositivo_id, especie, humedad, luz, temperatura, estado_planta, marca_tiempo
                FROM historial_lecturas
                WHERE planta_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (planta_id, limite))
            filas = cur.fetchall()
            return [
                {
                    "id": fila["id"],
                    "planta_id": fila["planta_id"],
                    "dispositivo_id": fila["dispositivo_id"],
                    "especie": fila["especie"],
                    "valores": {
                        "humedad": float(fila["humedad"]),
                        "luz": float(fila["luz"]),
                        "temperatura": float(fila["temperatura"]),
                    },
                    "estado_planta": fila["estado_planta"],
                    "marca_tiempo": fila["marca_tiempo"],
                }
                for fila in filas
            ]


class BdUsuariosPlantasAdapter(UsuariosPlantasPort):
    """
    Adaptador de salida para gestionar usuarios y plantas en SQLite.
    """

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)
        inicializar_bd(self._ruta)

    def _conectar(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._ruta)
        con.row_factory = sqlite3.Row
        return con

    def guardar_usuario(self, usuario: Usuario) -> None:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO usuarios (id, nombre, email, password_hash)
                VALUES (?, ?, ?, ?)
            """, (usuario.id, usuario.nombre, usuario.email.lower(), usuario.password_hash))
            con.commit()

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, nombre, email, password_hash
                FROM usuarios
                WHERE lower(email) = lower(?)
            """, (email.strip(),))
            fila = cur.fetchone()
            if not fila:
                return None
            return Usuario(
                id=fila["id"],
                nombre=fila["nombre"],
                email=fila["email"],
                password_hash=fila["password_hash"],
            )

    def obtener_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, nombre, email, password_hash
                FROM usuarios
                WHERE id = ?
            """, (usuario_id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return Usuario(
                id=fila["id"],
                nombre=fila["nombre"],
                email=fila["email"],
                password_hash=fila["password_hash"],
            )

    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, nombre, especie, usuario_id, dispositivo_id
                FROM plantas
                WHERE id = ?
            """, (planta_id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return Planta(
                id=fila["id"],
                nombre=fila["nombre"],
                especie=fila["especie"],
                usuario_id=fila["usuario_id"],
                dispositivo_id=fila["dispositivo_id"],
            )

    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, nombre, especie, usuario_id, dispositivo_id
                FROM plantas
                WHERE dispositivo_id = ?
            """, (dispositivo_id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return Planta(
                id=fila["id"],
                nombre=fila["nombre"],
                especie=fila["especie"],
                usuario_id=fila["usuario_id"],
                dispositivo_id=fila["dispositivo_id"],
            )

    def listar_plantas_por_usuario(self, usuario_id: str) -> List[Planta]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, nombre, especie, usuario_id, dispositivo_id
                FROM plantas
                WHERE usuario_id = ?
                ORDER BY id ASC
            """, (usuario_id,))
            filas = cur.fetchall()
            return [
                Planta(
                    id=f["id"],
                    nombre=f["nombre"],
                    especie=f["especie"],
                    usuario_id=f["usuario_id"],
                    dispositivo_id=f["dispositivo_id"],
                )
                for f in filas
            ]

    def guardar_planta(self, planta: Planta) -> None:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO plantas (id, nombre, especie, usuario_id, dispositivo_id)
                VALUES (?, ?, ?, ?, ?)
            """, (planta.id, planta.nombre, planta.especie, planta.usuario_id, planta.dispositivo_id))
            con.commit()


class BdHistorialYPlantasAdapter(BdHistorialLecturasAdapter, BdUsuariosPlantasAdapter):
    """
    Adaptador compuesto que satisface tanto HistorialLecturasPort como UsuariosPlantasPort
    sobre la misma conexión/archivo de base de datos SQLite.
    """
    pass
