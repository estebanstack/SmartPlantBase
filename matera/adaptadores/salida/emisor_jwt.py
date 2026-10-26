"""
Adaptador de Salida: Emisor de Tokens JWT (R7).
Implementa EmisorTokenPort utilizando la librería PyJWT (HS256).
Es el ÚNICO archivo de infraestructura que importa la librería PyJWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import jwt

from matera.puertos.salida import EmisorTokenPort


class JwtEmisorTokenAdapter(EmisorTokenPort):
    """
    Adaptador secundario para emisión y verificación criptográfica de JSON Web Tokens.
    Segrega tokens de usuario (scope='usuario') y tokens de dispositivo (scope='dispositivo').
    """

    def __init__(self, secret_key: str = "matera-secret-key-arquitectura-2026-segura", algoritmo: str = "HS256"):
        self._secret_key = secret_key
        self._algoritmo = algoritmo

    def emitir_token_usuario(self, usuario_id: str, email: str) -> str:
        """
        Emite un JWT para un usuario autenticado con alcance de consulta e inspección.
        Vigencia estándar: 24 horas.
        """
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
        """
        Emite un JWT para un dispositivo sensor (ESP32) con alcance restringido a su planta.
        Vigencia estándar: 1 año.
        """
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": dispositivo_id,
            "planta_id": planta_id,
            "scope": "dispositivo",
            "iat": ahora,
            "exp": ahora + timedelta(days=365),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algoritmo)

    def decodificar_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica la firma y expiración del token.
        Lanza jwt.PyJWTError si el token es inválido o expiró.
        """
        return jwt.decode(token, self._secret_key, algorithms=[self._algoritmo])
