"""
Abstracción del repositorio de especies (Puerto en arquitectura hexagonal).
Cumple con RA5 (inversión de dependencias) e ISP (interfaz segregada y mínima).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Especie


class EspecieRepository(ABC):
    """
    Contrato abstracto para la obtención de datos de especies botánicas.
    El dominio depende de esta abstracción, no de CSV, bases de datos o APIs.
    """

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        """Obtiene la configuración y rangos de una especie por su nombre normalizado."""
        pass

    @abstractmethod
    def obtener_todas(self) -> List[Especie]:
        """Obtiene la lista completa de todas las especies soportadas."""
        pass
