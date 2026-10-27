"""
Caso de uso R7: el dueño de una planta pide el token de su dispositivo.
Sirve si se perdió el token o para las plantas que ya existían antes (las de la semilla).
Solo el dueño puede pedirlo: se aplica la misma regla de propiedad que en las consultas.
"""
from matera.dominio.casos_uso.propiedad import obtener_planta_del_usuario
from matera.dominio.puertos.entrada import EmitirTokenDispositivoPort
from matera.dominio.puertos.salida import EmisorTokenPort, PlantasPort


class EmitirTokenDispositivo(EmitirTokenDispositivoPort):
    def __init__(self, plantas: PlantasPort, emisor_token: EmisorTokenPort):
        self._plantas = plantas
        self._emisor_token = emisor_token

    def emitir_token_dispositivo(self, usuario_id: str, planta_id: str) -> str:
        planta = obtener_planta_del_usuario(self._plantas, usuario_id, planta_id)
        return self._emisor_token.emitir_token_dispositivo(planta.dispositivo_id, planta.id)
