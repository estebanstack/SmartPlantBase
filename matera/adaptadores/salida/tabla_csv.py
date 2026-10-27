"""
Adaptador de Salida: Tabla de Referencia en CSV (R4).
Implementa el puerto de salida TablaReferenciaPort leyendo el catálogo botánico desde un archivo CSV.
El formato de las columnas lo define columnas_referencia.py (el mismo que usa tabla_bd.py).
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional

from matera.adaptadores.salida.columnas_referencia import especie_desde_fila
from matera.dominio.modelo import Especie
from matera.dominio.puertos.salida import TablaReferenciaPort


class CsvTablaReferenciaAdapter(TablaReferenciaPort):
    """
    Adaptador secundario que implementa TablaReferenciaPort a través de un archivo CSV.
    Permite cargar las especies de referencia manteniendo el dominio 100% agnóstico al formato de archivo.
    """

    def __init__(self, ruta_archivo_csv: str | Path):
        self._ruta = Path(ruta_archivo_csv)
        self._cache: Optional[Dict[str, Especie]] = None

    def _cargar_datos(self) -> Dict[str, Especie]:
        if not self._ruta.exists():
            raise FileNotFoundError(f"El archivo de referencia CSV no existe en la ruta: {self._ruta}")

        especies: Dict[str, Especie] = {}
        with open(self._ruta, mode="r", encoding="utf-8") as archivo:
            for fila in csv.DictReader(archivo):
                nombre = fila["especie"].strip().lower()
                especies[nombre] = especie_desde_fila(nombre, fila)
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
