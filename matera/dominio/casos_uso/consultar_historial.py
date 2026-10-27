"""Caso de uso R5: historial de lecturas de una planta del usuario."""
from typing import List

from matera.dominio.casos_uso.propiedad import obtener_planta_del_usuario
from matera.dominio.modelo import RegistroLectura
from matera.dominio.puertos.entrada import ConsultarHistorialPort
from matera.dominio.puertos.salida import HistorialLecturasPort, PlantasPort


class ConsultarHistorial(ConsultarHistorialPort):
    def __init__(self, plantas: PlantasPort, historial: HistorialLecturasPort):
        self._plantas = plantas
        self._historial = historial

    def consultar_historial(
        self, usuario_id: str, planta_id: str, limite: int = 20
    ) -> List[RegistroLectura]:
        planta = obtener_planta_del_usuario(self._plantas, usuario_id, planta_id)
        return self._historial.obtener_historial(planta.id, limite)
