"""
Implementación de persistencia basada en archivo CSV (Capa de Infraestructura).
Implementa la abstracción EspecieRepository definida en el Dominio (RA5, DIP).
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional

from src.domain.entities import (
    LIMITES_FISICOS,
    PARAMETROS_SOPORTADOS,
    Especie,
    RangoParametro,
)
from src.domain.repositories import EspecieRepository


class CsvEspecieRepository(EspecieRepository):
    """
    Adaptador secundario que lee las especies de referencia desde un archivo CSV.
    La dirección de la dependencia apunta hacia el Dominio (EspecieRepository),
    garantizando que el dominio desconozca por completo los detalles de I/O y CSV.
    """

    # El Anexo B abrevia la columna de temperatura. Cualquier parámetro cuyo
    # nombre de dominio coincida con el prefijo de sus columnas (p. ej. ph_min /
    # ph_max) se resuelve sin tocar esta clase.
    _PREFIJOS_CSV: Dict[str, str] = {"temperatura": "temp"}

    def __init__(self, ruta_archivo_csv: str | Path):
        self._ruta = Path(ruta_archivo_csv)
        self._cache: Optional[Dict[str, Especie]] = None

    @classmethod
    def _columnas_de(cls, parametro: str) -> tuple[str, str]:
        prefijo = cls._PREFIJOS_CSV.get(parametro, parametro)
        return f"{prefijo}_min", f"{prefijo}_max"

    def _cargar_datos(self) -> Dict[str, Especie]:
        """Lee el CSV y lo mapea a entidades de dominio."""
        if not self._ruta.exists():
            raise FileNotFoundError(f"El archivo de referencia CSV no existe en la ruta: {self._ruta}")

        especies: Dict[str, Especie] = {}
        with open(self._ruta, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                nombre = fila["especie"].strip().lower()

                rangos: Dict[str, RangoParametro] = {}
                for parametro in PARAMETROS_SOPORTADOS:
                    col_min, col_max = self._columnas_de(parametro)
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

                especies[nombre] = Especie(nombre=nombre, rangos=rangos)

        return especies

    def _obtener_catalogo(self) -> Dict[str, Especie]:
        if self._cache is None:
            self._cache = self._cargar_datos()
        return self._cache

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        """Busca una especie por nombre en el CSV."""
        return self._obtener_catalogo().get(nombre.strip().lower())

    def obtener_todas(self) -> List[Especie]:
        """Obtiene la lista completa de especies del CSV."""
        return list(self._obtener_catalogo().values())
