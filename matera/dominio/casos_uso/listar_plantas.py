"""Caso de uso R7: plantas que pertenecen a un usuario."""
from typing import List

from matera.dominio.modelo import Planta
from matera.dominio.puertos.entrada import ListarPlantasPort
from matera.dominio.puertos.salida import PlantasPort


class ListarPlantas(ListarPlantasPort):
    def __init__(self, plantas: PlantasPort):
        self._plantas = plantas

    def listar_plantas_usuario(self, usuario_id: str) -> List[Planta]:
        return self._plantas.listar_plantas_por_usuario(usuario_id)
