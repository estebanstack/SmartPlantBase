"""
Adaptadores de Salida: Historial de Lecturas y Gestión de Usuarios/Plantas en SQLite (R5, R7).
Implementa HistorialLecturasPort, UsuariosPort y PlantasPort para la persistencia relacional en SQLite.
"""
from pathlib import Path
import sqlite3
from typing import List, Optional

from matera.adaptadores.salida.tabla_bd import inicializar_bd
from matera.dominio.modelo import Diagnostico, EstadoPlanta, Lectura, Planta, RegistroLectura, Usuario
from matera.dominio.puertos.salida import HistorialLecturasPort, PlantasPort, UsuariosPort


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

    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[RegistroLectura]:
        with self._conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT planta_id, dispositivo_id, especie, humedad, luz, temperatura, estado_planta, marca_tiempo
                FROM historial_lecturas
                WHERE planta_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (planta_id, limite))
            return [
                RegistroLectura(
                    lectura=Lectura(
                        especie=fila["especie"],
                        valores={
                            "humedad": float(fila["humedad"]),
                            "luz": float(fila["luz"]),
                            "temperatura": float(fila["temperatura"]),
                        },
                        marca_tiempo=fila["marca_tiempo"],
                        dispositivo_id=fila["dispositivo_id"] or None,
                        planta_id=fila["planta_id"] or None,
                    ),
                    estado=EstadoPlanta(fila["estado_planta"]),
                )
                for fila in cur.fetchall()
            ]


class BdUsuariosPlantasAdapter(UsuariosPort, PlantasPort):
    """
    Adaptador de salida que implementa UsuariosPort y PlantasPort en SQLite.
    Una sola clase puede implementar varios puertos; el dominio sigue viendo puertos separados.
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
    Adaptador compuesto que satisface HistorialLecturasPort, UsuariosPort y PlantasPort
    sobre la misma conexión/archivo de base de datos SQLite.
    """
    pass
