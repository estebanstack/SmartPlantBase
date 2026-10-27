"""
Caso de uso R7: registro e inicio de sesión de usuarios.
El token lo emite EmisorTokenPort; este caso de uso no sabe que existe JWT.
"""
import hashlib
import uuid

from matera.dominio.excepciones import CredencialesInvalidasError, UsuarioYaExisteError
from matera.dominio.modelo import SesionUsuario, Usuario
from matera.dominio.puertos.entrada import AutenticarUsuarioPort
from matera.dominio.puertos.salida import EmisorTokenPort, UsuariosPort


class AutenticarUsuario(AutenticarUsuarioPort):
    def __init__(self, usuarios: UsuariosPort, emisor_token: EmisorTokenPort):
        self._usuarios = usuarios
        self._emisor_token = emisor_token

    def registrar_usuario(self, nombre: str, email: str, password: str) -> SesionUsuario:
        email_limpio = email.strip().lower()
        if self._usuarios.obtener_usuario_por_email(email_limpio) is not None:
            raise UsuarioYaExisteError(email_limpio)

        usuario = Usuario(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            nombre=nombre.strip(),
            email=email_limpio,
            password_hash=hashlib.sha256(password.encode("utf-8")).hexdigest(),
        )
        self._usuarios.guardar_usuario(usuario)
        return self._abrir_sesion(usuario)

    def iniciar_sesion(self, email: str, password: str) -> SesionUsuario:
        usuario = self._usuarios.obtener_usuario_por_email(email.strip().lower())
        if usuario is None:
            raise CredencialesInvalidasError()

        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if usuario.password_hash != password_hash:
            raise CredencialesInvalidasError()

        return self._abrir_sesion(usuario)

    def _abrir_sesion(self, usuario: Usuario) -> SesionUsuario:
        token = self._emisor_token.emitir_token_usuario(usuario.id, usuario.email)
        return SesionUsuario(usuario=usuario, token=token)
