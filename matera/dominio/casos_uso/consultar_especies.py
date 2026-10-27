"""Caso de uso R1: devolver el catálogo de especies con sus rangos de referencia."""
from typing import List

from matera.dominio.modelo import Especie
from matera.dominio.puertos.entrada import ConsultarEspeciesPort
from matera.dominio.puertos.salida import TablaReferenciaPort


class ConsultarEspecies(ConsultarEspeciesPort):
    def __init__(self, tabla_referencia: TablaReferenciaPort):
        self._tabla_referencia = tabla_referencia

    def listar_especies(self) -> List[Especie]:
        return self._tabla_referencia.obtener_todas()
