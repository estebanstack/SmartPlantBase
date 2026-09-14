"""
Implementación de persistencia basada en archivo CSV (Capa de Abastecimiento / Infraestructura).
Implementa la abstracción EspecieRepository definida en el Dominio (RA5, DIP).
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional

from src.domain.entities import Especie, RangoParametro
from src.domain.repositories import EspecieRepository


class CsvEspecieRepository(EspecieRepository):
    """
    Adaptador secundario que lee las especies de referencia desde un archivo CSV.
    La dirección de la dependencia apunta hacia el Dominio (EspecieRepository),
    garantizando que el dominio desconozca por completo los detalles de I/O y CSV.
    """

    def __init__(self, ruta_archivo_csv: str | Path):
        self._ruta = Path(ruta_archivo_csv)
        self._cache: Optional[Dict[str, Especie]] = None

    def _cargar_datos(self) -> Dict[str, Especie]:
        """Lee y mapea el CSV en entidades de dominio."""
        if not self._ruta.exists():
            raise FileNotFoundError(f"El archivo de referencia CSV no existe en la ruta: {self._ruta}")

        especies: Dict[str, Especie] = {}
        with open(self._ruta, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                nombre = fila["especie"].strip().lower()
                especie = Especie(
                    nombre=nombre,
                    rango_humedad=RangoParametro(
                        minimo=float(fila["humedad_min"]),
                        maximo=float(fila["humedad_max"]),
                        unidad="%",
                    ),
                    rango_luz=RangoParametro(
                        minimo=float(fila["luz_min"]),
                        maximo=float(fila["luz_max"]),
                        unidad="lux",
                    ),
                    rango_temperatura=RangoParametro(
                        minimo=float(fila["temp_min"]),
                        maximo=float(fila["temp_max"]),
                        unidad="°C",
                    ),
                )
                especies[nombre] = especie

        return especies

    def _obtener_catalogo(self) -> Dict[str, Especie]:
        if self._cache is None:
            self._cache = self._cargar_datos()
        return self._cache

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        """Busca una especie por nombre en el CSV."""
        catalogo = self._obtener_catalogo()
        return catalogo.get(nombre.strip().lower())

    def obtener_todas(self) -> List[Especie]:
        """Obtiene la lista completa de especies del CSV."""
        catalogo = self._obtener_catalogo()
        return list(catalogo.values())
