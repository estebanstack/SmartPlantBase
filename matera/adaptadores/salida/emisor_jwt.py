"""
Adaptador de Salida: emisión de tokens con PyJWT (R7).
Implementa EmisorTokenPort, que es lo que pide el dominio al registrar o iniciar sesión.
La verificación de tokens vive aparte, en adaptadores/entrada/verificador_jwt.py.
"""
from datetime import datetime, timedelta, timezone

import jwt

from matera.dominio.puertos.salida import EmisorTokenPort


class JwtEmisorTokenAdapter(EmisorTokenPort):
    """
    Emite dos tipos de token con alcances distintos:
    - usuario: para el front; dura 24 horas.
    - dispositivo: para el ESP32; solo sirve para reportar lecturas de su planta; dura 1 año.
    """

    def __init__(self, secret_key: str, algoritmo: str = "HS256"):
        if not secret_key:
            raise ValueError("Se necesita una clave secreta para firmar los tokens.")
        self._secret_key = secret_key
        self._algoritmo = algoritmo

    def emitir_token_usuario(self, usuario_id: str, email: str) -> str:
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": usuario_id,
            "email": email,
            "scope": "usuario",
            "iat": ahora,
            "exp": ahora + timedelta(hours=24),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algoritmo)

    def emitir_token_dispositivo(self, dispositivo_id: str, planta_id: str) -> str:
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": dispositivo_id,
            "planta_id": planta_id,
            "scope": "dispositivo",
            "iat": ahora,
            "exp": ahora + timedelta(days=365),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algoritmo)
