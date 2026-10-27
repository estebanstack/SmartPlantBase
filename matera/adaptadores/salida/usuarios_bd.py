"""Adaptador de Salida: usuarios en SQLite (R7). Implementa UsuariosPort."""
from pathlib import Path
from typing import Optional

from matera.adaptadores.salida.sqlite_bd import conectar
from matera.dominio.modelo import Usuario
from matera.dominio.puertos.salida import UsuariosPort


class BdUsuariosAdapter(UsuariosPort):

    def __init__(self, ruta_bd: str | Path):
        self._ruta = str(ruta_bd)

    def guardar_usuario(self, usuario: Usuario) -> None:
        with conectar(self._ruta) as con:
            con.execute(
                "INSERT INTO usuarios (id, nombre, email, password_hash) VALUES (?, ?, ?, ?)",
                (usuario.id, usuario.nombre, usuario.email.lower(), usuario.password_hash),
            )

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        with conectar(self._ruta) as con:
            fila = con.execute(
                "SELECT id, nombre, email, password_hash FROM usuarios WHERE lower(email) = lower(?)",
                (email.strip(),),
            ).fetchone()
        if fila is None:
            return None
        return Usuario(
            id=fila["id"],
            nombre=fila["nombre"],
            email=fila["email"],
            password_hash=fila["password_hash"],
        )
