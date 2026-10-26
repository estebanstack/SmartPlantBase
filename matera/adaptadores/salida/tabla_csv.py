"""
Adaptador de Salida: Tabla de Referencia en CSV (R4).
Implementa el puerto de salida TablaReferenciaPort leyendo el catálogo botánico desde un archivo CSV.
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional

from matera.dominio.modelo import (
    LIMITES_FISICOS,
    PARAMETROS_SOPORTADOS,
    Especie,
    RangoParametro,
)
from matera.puertos.salida import TablaReferenciaPort


class CsvTablaReferenciaAdapter(TablaReferenciaPort):
    """
    Adaptador secundario que implementa TablaReferenciaPort a través de un archivo CSV.
    Permite cargar las especies de referencia manteniendo el dominio 100% agnóstico al formato de archivo.
    """

    _PREFIJOS_CSV: Dict[str, str] = {"temperatura": "temp"}

    def __init__(self, ruta_archivo_csv: str | Path):
        self._ruta = Path(ruta_archivo_csv)
        self._cache: Optional[Dict[str, Especie]] = None

    @classmethod
    def _columnas_de(cls, parametro: str) -> tuple[str, str]:
        prefijo = cls._PREFIJOS_CSV.get(parametro, parametro)
        return f"{prefijo}_min", f"{prefijo}_max"

    def _cargar_datos(self) -> Dict[str, Especie]:
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
