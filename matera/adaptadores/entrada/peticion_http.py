"""
Lectura de la petición HTTP (borde de entrada).
Es el camino de ida de serializacion.py: toma el cuerpo JSON de la petición y lo
convierte en datos limpios (textos, números, marca de tiempo) antes de llamar al puerto.
Así los controladores (api_front.py y api_dispositivos.py) solo tienen rutas, y el
dominio nunca recibe un request ni un dict crudo.
"""
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict

from flask import request

from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS

_ID_DISPOSITIVO_VALIDO = re.compile(r"[A-Za-z0-9_-]{1,40}")


def cuerpo_json() -> Dict[str, Any]:
    """El cuerpo debe ser un objeto JSON ({...}); una lista, un número o un texto se rechazan."""
    if not request.is_json:
        raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")
    return datos


def texto(datos: Dict[str, Any], campo: str, recortar: bool = True) -> str:
    """Campo de texto obligatorio. Si llega vacío o con otro tipo (número, lista...) es 400."""
    valor = datos.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ParametroInvalidoError(campo, f"El campo '{campo}' es obligatorio y debe ser texto.")
    return valor.strip() if recortar else valor


def correo(datos: Dict[str, Any]) -> str:
    """Correo obligatorio y con forma de correo (tiene @)."""
    valor = texto(datos, "email")
    if "@" not in valor:
        raise ParametroInvalidoError("email", "El correo electrónico es inválido.")
    return valor


def contrasena_nueva(datos: Dict[str, Any], minimo: int = 6) -> str:
    """Contraseña para crear una cuenta: texto de al menos `minimo` caracteres."""
    valor = texto(datos, "password", recortar=False)
    if len(valor) < minimo:
        raise ParametroInvalidoError("password", f"La contraseña debe tener al menos {minimo} caracteres.")
    return valor


def numero(campo: str, valor: Any) -> float:
    """Convierte a número. Rechaza booleanos, textos como "ERR" y también NaN e Infinity."""
    if valor is None:
        raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio.")
    if isinstance(valor, bool):
        raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
    try:
        convertido = float(valor)
    except (ValueError, TypeError):
        raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
    if not math.isfinite(convertido):
        raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
    return convertido


def valores_medidos(datos: Dict[str, Any]) -> Dict[str, float]:
    """Los parámetros que el dominio sabe evaluar (humedad, luz, temperatura...), ya como números."""
    return {campo: numero(campo, datos.get(campo)) for campo in PARAMETROS_SOPORTADOS}


def marca_tiempo(datos: Dict[str, Any]) -> str:
    """
    Marca de tiempo obligatoria en ISO-8601 (ej. 2026-10-27T15:00:00Z o 2026-10-27T10:00:00-05:00).
    Se normaliza a UTC con un formato fijo (AAAA-MM-DDTHH:MM:SSZ) para que el historial
    se pueda ordenar por la hora de la medición. Si no trae zona horaria, se toma como UTC.
    """
    valor = datos.get("marca_tiempo")
    if not isinstance(valor, str) or not valor.strip():
        raise ParametroInvalidoError("marca_tiempo", "La lectura debe traer su marca_tiempo (ISO-8601).")
    try:
        # Python < 3.11 no acepta la "Z" final, por eso se cambia por +00:00
        momento = datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
    except ValueError:
        raise ParametroInvalidoError(
            "marca_tiempo", f"La marca_tiempo '{valor}' no está en formato ISO-8601."
        )
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def id_dispositivo(datos: Dict[str, Any]) -> str:
    """Id del dispositivo: solo letras, números, guiones y guion bajo (máx. 40)."""
    valor = texto(datos, "dispositivo_id")
    if not _ID_DISPOSITIVO_VALIDO.fullmatch(valor):
        raise ParametroInvalidoError(
            "dispositivo_id",
            "El id del dispositivo solo admite letras, números, guiones y guion bajo (máx. 40).",
        )
    return valor


def mismo_dispositivo(datos: Dict[str, Any], id_url: str) -> None:
    """Si la lectura trae dispositivo_id en el cuerpo, debe ser el mismo de la URL."""
    dispositivo_cuerpo = datos.get("dispositivo_id")
    if dispositivo_cuerpo is not None and dispositivo_cuerpo != id_url:
        raise ParametroInvalidoError(
            "dispositivo_id", "El dispositivo_id del cuerpo no coincide con el de la URL."
        )


def limite_de_consulta(por_defecto: int = 20, maximo: int = 100) -> int:
    """Parámetro ?limite= del historial: entero entre 1 y `maximo`."""
    valor = request.args.get("limite")
    if valor is None:
        return por_defecto
    try:
        limite = int(valor)
    except ValueError:
        raise ParametroInvalidoError("limite", "El límite debe ser un número entero.")
    if not 1 <= limite <= maximo:
        raise ParametroInvalidoError("limite", f"El límite debe estar entre 1 y {maximo}.")
    return limite
