"""
Adaptador de Entrada: Verificación de Seguridad y Filtros JWT (R7).
Intercepta las solicitudes HTTP en el borde del sistema, valida la firma y el alcance (scope),
y entrega a los controladores o casos de uso únicamente una identidad verificada (usuario_id o dispositivo_id).
El dominio jamás ve ni procesa un token JWT.
"""
from functools import wraps
from typing import Callable
from flask import g, jsonify, request
import jwt

from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter


def extraer_bearer_token() -> str:
    """Extrae el token Bearer del encabezado Authorization."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise ValueError("Encabezado Authorization no suministrado.")

    partes = auth_header.strip().split(" ")
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise ValueError("Formato de autorización inválido. Debe ser: 'Bearer <token>'.")

    return partes[1]


def requiere_jwt_usuario(emisor_jwt: JwtEmisorTokenAdapter):
    """
    Decorador para endpoints accesibles exclusivamente por usuarios autenticados.
    Rechaza tokens expirados, firmas inválidas y tokens con alcance no correspondiente (ej. dispositivo).
    Inyecta `usuario_id` en el contexto `g.usuario_id` y en los argumentos de la función.
    """
    def decorador(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = extraer_bearer_token()
                payload = emisor_jwt.decodificar_token(token)
            except ValueError as ve:
                return jsonify({
                    "error": "AUTORIZACION_REQUERIDA",
                    "mensaje": str(ve),
                    "detalle": {},
                }), 401
            except jwt.ExpiredSignatureError:
                return jsonify({
                    "error": "TOKEN_EXPIRADO",
                    "mensaje": "El token JWT ha expirado. Inicie sesión nuevamente.",
                    "detalle": {},
                }), 401
            except jwt.PyJWTError:
                return jsonify({
                    "error": "TOKEN_INVALIDO",
                    "mensaje": "La firma o estructura del token JWT es inválida.",
                    "detalle": {},
                }), 401

            scope = payload.get("scope")
            if scope != "usuario":
                return jsonify({
                    "error": "ACCESO_DENEGADO",
                    "mensaje": "Este endpoint requiere un token con alcance de usuario.",
                    "detalle": {"scope_presente": scope},
                }), 403

            usuario_id = payload.get("sub")
            if not usuario_id:
                return jsonify({
                    "error": "TOKEN_INVALIDO",
                    "mensaje": "El token no contiene un identificador de usuario válido.",
                    "detalle": {},
                }), 401

            g.usuario_id = usuario_id
            return func(*args, usuario_id=usuario_id, **kwargs)
        return wrapper
    return decorador


def requiere_jwt_dispositivo(emisor_jwt: JwtEmisorTokenAdapter):
    """
    Decorador para el endpoint de reporte de lecturas de sensores (ESP32).
    Valida que el token tenga alcance 'dispositivo' y que el id del dispositivo
    del token coincida con el parámetro {id} de la URL (Sección 6.2 del plan).
    """
    def decorador(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = extraer_bearer_token()
                payload = emisor_jwt.decodificar_token(token)
            except ValueError as ve:
                return jsonify({
                    "error": "AUTORIZACION_REQUERIDA",
                    "mensaje": str(ve),
                    "detalle": {},
                }), 401
            except jwt.ExpiredSignatureError:
                return jsonify({
                    "error": "TOKEN_EXPIRADO",
                    "mensaje": "El token de dispositivo ha expirado.",
                    "detalle": {},
                }), 401
            except jwt.PyJWTError:
                return jsonify({
                    "error": "TOKEN_INVALIDO",
                    "mensaje": "La firma del token de dispositivo es inválida.",
                    "detalle": {},
                }), 401

            scope = payload.get("scope")
            if scope != "dispositivo":
                return jsonify({
                    "error": "ACCESO_DENEGADO",
                    "mensaje": "Este endpoint requiere un token de dispositivo sensor.",
                    "detalle": {"scope_presente": scope},
                }), 403

            dispositivo_token = payload.get("sub")
            dispositivo_url = kwargs.get("id") or kwargs.get("dispositivo_id")

            # Segregación: un token de esp32-01 no puede reportar en /api/dispositivos/esp32-02/lecturas
            if dispositivo_url and dispositivo_token != dispositivo_url:
                return jsonify({
                    "error": "ACCESO_DENEGADO",
                    "mensaje": f"El token del dispositivo '{dispositivo_token}' no tiene autorización para reportar como '{dispositivo_url}'.",
                    "detalle": {"dispositivo_token": dispositivo_token, "dispositivo_url": dispositivo_url},
                }), 403

            g.dispositivo_id = dispositivo_token
            return func(*args, **kwargs)
        return wrapper
    return decorador
