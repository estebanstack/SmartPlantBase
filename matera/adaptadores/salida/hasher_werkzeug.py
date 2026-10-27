"""
Adaptador de Salida: hash de contraseñas con werkzeug.security (R7).
Implementa HasherContrasenaPort. Usa scrypt (el algoritmo por defecto de werkzeug)
con una sal aleatoria por contraseña,
así dos usuarios con la misma clave quedan con hashes distintos.
Si mañana se cambia a bcrypt o argon2, se escribe otro adaptador y el dominio no cambia.
"""
from werkzeug.security import check_password_hash, generate_password_hash

from matera.dominio.puertos.salida import HasherContrasenaPort


class WerkzeugHasherAdapter(HasherContrasenaPort):

    def generar_hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verificar(self, password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)
