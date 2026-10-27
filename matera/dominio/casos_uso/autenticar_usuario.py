"""
Caso de uso R7: registro e inicio de sesión de usuarios.
No sabe qué algoritmo protege las contraseñas (HasherContrasenaPort)
ni que el token es un JWT (EmisorTokenPort).
"""
import uuid

from matera.dominio.excepciones import CredencialesInvalidasError, UsuarioYaExisteError
from matera.dominio.modelo import SesionUsuario, Usuario
from matera.dominio.puertos.entrada import AutenticarUsuarioPort
from matera.dominio.puertos.salida import EmisorTokenPort, HasherContrasenaPort, UsuariosPort


class AutenticarUsuario(AutenticarUsuarioPort):
    def __init__(
        self,
        usuarios: UsuariosPort,
        hasher: HasherContrasenaPort,
        emisor_token: EmisorTokenPort,
    ):
        self._usuarios = usuarios
        self._hasher = hasher
        self._emisor_token = emisor_token

    def registrar_usuario(self, nombre: str, email: str, password: str) -> SesionUsuario:
        email_limpio = email.strip().lower()
        if self._usuarios.obtener_usuario_por_email(email_limpio) is not None:
            raise UsuarioYaExisteError(email_limpio)

        usuario = Usuario(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            nombre=nombre.strip(),
            email=email_limpio,
            password_hash=self._hasher.generar_hash(password),
        )
        self._usuarios.guardar_usuario(usuario)
        return self._abrir_sesion(usuario)

    def iniciar_sesion(self, email: str, password: str) -> SesionUsuario:
        usuario = self._usuarios.obtener_usuario_por_email(email.strip().lower())
        if usuario is None or not self._hasher.verificar(password, usuario.password_hash):
            # Mismo error en ambos casos: no se revela si el correo existe
            raise CredencialesInvalidasError()
        return self._abrir_sesion(usuario)

    def _abrir_sesion(self, usuario: Usuario) -> SesionUsuario:
        token = self._emisor_token.emitir_token_usuario(usuario.id, usuario.email)
        return SesionUsuario(usuario=usuario, token=token)
