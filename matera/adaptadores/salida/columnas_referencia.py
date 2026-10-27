"""
Formato de la tabla de referencia (Anexo B), compartido por el CSV y la base de datos.

Cada parámetro del dominio tiene dos columnas: <prefijo>_min y <prefijo>_max.
El prefijo es el nombre del parámetro, salvo temperatura, que en la tabla se llama "temp".
Así los dos adaptadores (tabla_csv.py y tabla_bd.py) recorren PARAMETROS_SOPORTADOS
y un parámetro nuevo (por ejemplo pH) solo necesita sus columnas en los datos.
"""
from typing import Mapping, Tuple

from matera.dominio.modelo import LIMITES_FISICOS, PARAMETROS_SOPORTADOS, Especie, RangoParametro

_PREFIJOS: Mapping[str, str] = {"temperatura": "temp"}


def columnas_de(parametro: str) -> Tuple[str, str]:
    """Nombres de las columnas de mínimo y máximo de un parámetro."""
    prefijo = _PREFIJOS.get(parametro, parametro)
    return f"{prefijo}_min", f"{prefijo}_max"


def especie_desde_fila(nombre: str, fila: Mapping[str, object]) -> Especie:
    """
    Arma una Especie a partir de una fila (del CSV o de la base de datos).
    Falla con un mensaje claro si a la tabla le faltan las columnas de algún parámetro.
    """
    rangos = {}
    for parametro in PARAMETROS_SOPORTADOS:
        col_min, col_max = columnas_de(parametro)
        if col_min not in fila or col_max not in fila:
            raise ValueError(
                f"La tabla de referencia no define las columnas '{col_min}' y '{col_max}' "
                f"requeridas por el parámetro '{parametro}'."
            )
        rangos[parametro] = RangoParametro(
            minimo=float(fila[col_min]),
            maximo=float(fila[col_max]),
            unidad=LIMITES_FISICOS[parametro].unidad,
        )
    return Especie(nombre=nombre, rangos=rangos)
