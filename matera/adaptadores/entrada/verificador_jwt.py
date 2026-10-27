"""
Adaptador de Entrada: verificación de tokens con PyJWT (R7).
Implementa VerificadorTokenPort. Revisa firma y expiración y traduce los
errores de la librería a TokenRechazadoError, para que el filtro no dependa de PyJWT.
"""
import jwt

from matera.adaptadores.entrada.seguridad import (
    IdentidadToken,
    TokenRechazadoError,
    VerificadorTokenPort,
)


class JwtVerificadorToken(VerificadorTokenPort):

    def __init__(self, secret_key: str, algoritmo: str = "HS256"):
        self._secret_key = secret_key
        self._algoritmo = algoritmo

    def verificar(self, token: str) -> IdentidadToken:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algoritmo])
        except jwt.ExpiredSignatureError:
            raise TokenRechazadoError("TOKEN_EXPIRADO", "El token ha expirado. Inicie sesión nuevamente.")
        except jwt.PyJWTError:
            raise TokenRechazadoError("TOKEN_INVALIDO", "La firma o estructura del token es inválida.")

        sujeto = payload.get("sub")
        alcance = payload.get("scope")
        if not sujeto or not alcance:
            raise TokenRechazadoError("TOKEN_INVALIDO", "El token no trae identidad ni alcance.")
        return IdentidadToken(sujeto=sujeto, alcance=alcance)
