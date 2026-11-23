"""
Caso de uso Matera-Gotchi: el dueño de una planta consulta su estado de ánimo, XP, nivel y racha.
Si la planta aún no ha enviado lecturas, devuelve un perfil nuevo (sin guardarlo).
"""
from matera.dominio.casos_uso.propiedad import obtener_planta_del_usuario
from matera.dominio.gamificacion import PerfilGamificacion
from matera.dominio.puertos.entrada import ConsultarGotchiPort
from matera.dominio.puertos.salida import GamificacionPort, PlantasPort


class ConsultarGotchi(ConsultarGotchiPort):
    def __init__(self, plantas: PlantasPort, gamificacion: GamificacionPort):
        self._plantas = plantas
        self._gamificacion = gamificacion

    def consultar_gotchi(self, usuario_id: str, planta_id: str) -> PerfilGamificacion:
        planta = obtener_planta_del_usuario(self._plantas, usuario_id, planta_id)
        return self._gamificacion.obtener_perfil(planta.id) or PerfilGamificacion(planta_id=planta.id)
