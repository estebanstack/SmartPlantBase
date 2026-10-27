"""
Adaptador de Entrada: filtro de seguridad (R7).

Aquí se decide quién puede entrar a cada endpoint ANTES de llegar al caso de uso.
El filtro no sabe que el token es un JWT: le pide a un VerificadorTokenPort que lo
revise y recibe una IdentidadToken (quién es y qué alcance tiene).
Al caso de uso solo le llega el id ya verificado (usuario_id), nunca el token ni las cabeceras.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Callable

from flask import jsonify, request

ALCANCE_USUARIO = "usuario"
ALCANCE_DISPOSITIVO = "dispositivo"


@dataclass(frozen=True)
class IdentidadToken:
    """Lo que se sabe de quien llama, después de verificar su token."""
    sujeto: str   # usuario_id o dispositivo_id
    alcance: str  # "usuario" o "dispositivo"


class TokenRechazadoError(Exception):
    """El token no sirve: firma mala, expirado o sin los datos mínimos."""

    def __init__(self, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje


class VerificadorTokenPort(ABC):
    """
    Contrato que necesita este filtro. Lo define quien lo usa (el borde de entrada)
    y lo implementa verificador_jwt.py con PyJWT. Cambiar a OAuth sería otra implementación.
    """

    @abstractmethod
    def verificar(self, token: str) -> IdentidadToken:
        """Devuelve la identidad o lanza TokenRechazadoError."""


def _error(codigo: str, mensaje: str, status: int, detalle=None):
    return jsonify({"error": codigo, "mensaje": mensaje, "detalle": detalle or {}}), status


def _extraer_bearer_token() -> str:
    cabecera = request.headers.get("Authorization", "").strip()
    if not cabecera:
        raise TokenRechazadoError("AUTORIZACION_REQUERIDA", "Encabezado Authorization no suministrado.")
    partes = cabecera.split(" ")
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise TokenRechazadoError(
            "AUTORIZACION_REQUERIDA", "Formato de autorización inválido. Debe ser: 'Bearer <token>'."
        )
    return partes[1]


def _identificar(verificador: VerificadorTokenPort, alcance_requerido: str):
    """Devuelve (identidad, None) si todo está bien o (None, respuesta_de_error)."""
    try:
        identidad = verificador.verificar(_extraer_bearer_token())
    except TokenRechazadoError as error:
        return None, _error(error.codigo, error.mensaje, 401)

    if identidad.alcance != alcance_requerido:
        return None, _error(
            "ACCESO_DENEGADO",
            f"Este endpoint requiere un token con alcance de {alcance_requerido}.",
            403,
            {"scope_presente": identidad.alcance},
        )
    return identidad, None


def requiere_usuario(verificador: VerificadorTokenPort):
    """Solo deja pasar tokens de usuario. Inyecta `usuario_id` en el endpoint."""
    def decorador(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identidad, respuesta_error = _identificar(verificador, ALCANCE_USUARIO)
            if respuesta_error:
                return respuesta_error
            return func(*args, usuario_id=identidad.sujeto, **kwargs)
        return wrapper
    return decorador


def requiere_dispositivo(verificador: VerificadorTokenPort):
    """
    Solo deja pasar tokens de dispositivo, y solo para reportar como sí mismo:
    el token de esp32-01 no puede enviar lecturas a /api/dispositivos/esp32-02/lecturas.
    """
    def decorador(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identidad, respuesta_error = _identificar(verificador, ALCANCE_DISPOSITIVO)
            if respuesta_error:
                return respuesta_error

            dispositivo_url = kwargs.get("id") or kwargs.get("dispositivo_id")
            if dispositivo_url and identidad.sujeto != dispositivo_url:
                return _error(
                    "ACCESO_DENEGADO",
                    f"El token del dispositivo '{identidad.sujeto}' no tiene autorización "
                    f"para reportar como '{dispositivo_url}'.",
                    403,
                    {"dispositivo_token": identidad.sujeto, "dispositivo_url": dispositivo_url},
                )
            return func(*args, **kwargs)
        return wrapper
    return decorador
