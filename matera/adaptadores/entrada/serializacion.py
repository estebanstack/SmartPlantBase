"""
Traducción de objetos del dominio a JSON (borde de salida HTTP).
La comparten api_front.py y api_dispositivos.py para que la respuesta tenga
siempre la misma forma, sin repetir el mismo código en cada controlador.
"""
from typing import Any, Dict

from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    EstadoActualPlanta,
    Lectura,
    Planta,
    RegistroLectura,
    SesionUsuario,
)


def diagnostico_a_json(diagnostico: Diagnostico) -> Dict[str, Any]:
    return {
        "especie": diagnostico.especie,
        "estado": diagnostico.estado.value,
        "parametros": [
            {
                "nombre": p.nombre,
                "valor": p.valor,
                "unidad": p.unidad,
                "rango_optimo": [p.rango_optimo[0], p.rango_optimo[1]],
                "estado": p.estado.value,
            }
            for p in diagnostico.parametros
        ],
        "recomendaciones": list(diagnostico.recomendaciones),
    }


def especie_a_json(especie: Especie) -> Dict[str, Any]:
    return {
        "nombre": especie.nombre,
        "rangos": {
            nombre: {"min": rango.minimo, "max": rango.maximo, "unidad": rango.unidad}
            for nombre, rango in especie.rangos.items()
        },
    }


def planta_a_json(planta: Planta) -> Dict[str, Any]:
    return {
        "id": planta.id,
        "nombre": planta.nombre,
        "especie": planta.especie,
        "usuario_id": planta.usuario_id,
        "dispositivo_id": planta.dispositivo_id,
    }


def lectura_a_json(lectura: Lectura) -> Dict[str, Any]:
    return {
        "especie": lectura.especie,
        "valores": dict(lectura.valores),
        "marca_tiempo": lectura.marca_tiempo,
        "dispositivo_id": lectura.dispositivo_id,
        "planta_id": lectura.planta_id,
    }


def registro_a_json(registro: RegistroLectura) -> Dict[str, Any]:
    datos = lectura_a_json(registro.lectura)
    datos["estado_planta"] = registro.estado.value
    return datos


def estado_actual_a_json(estado: EstadoActualPlanta) -> Dict[str, Any]:
    return {
        "planta": planta_a_json(estado.planta),
        "ultima_lectura": lectura_a_json(estado.ultima_lectura) if estado.ultima_lectura else None,
        "diagnostico": diagnostico_a_json(estado.diagnostico) if estado.diagnostico else None,
    }


def sesion_a_json(sesion: SesionUsuario) -> Dict[str, Any]:
    return {
        "token": sesion.token,
        "usuario": {
            "id": sesion.usuario.id,
            "nombre": sesion.usuario.nombre,
            "email": sesion.usuario.email,
        },
    }
