"""
Regla de negocio compartida: un usuario solo puede ver sus propias plantas (R7).
La usan ConsultarEstado y ConsultarHistorial para no repetir la misma verificación.
"""
from matera.dominio.excepciones import AccesoNoAutorizadoPlantaError, PlantaNoEncontradaError
from matera.dominio.modelo import Planta
from matera.dominio.puertos.salida import PlantasPort


def obtener_planta_del_usuario(plantas: PlantasPort, usuario_id: str, planta_id: str) -> Planta:
    """Devuelve la planta si existe y es del usuario; si no, lanza el error de dominio."""
    planta = plantas.obtener_planta_por_id(planta_id)
    if planta is None:
        raise PlantaNoEncontradaError(planta_id)
    if not planta.pertenece_a(usuario_id):
        raise AccesoNoAutorizadoPlantaError(usuario_id, planta_id)
    return planta
