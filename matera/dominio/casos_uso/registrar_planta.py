"""
Caso de uso R7: un usuario registra una planta y la vincula a su dispositivo.
Devuelve el token del dispositivo, que es lo que se graba en el ESP32 (o se le pasa al simulador).
"""
import uuid

from matera.dominio.excepciones import (
    DispositivoYaVinculadoError,
    EspecieNoSoportadaError,
    ParametroInvalidoError,
)
from matera.dominio.modelo import Planta, PlantaRegistrada
from matera.dominio.puertos.entrada import RegistrarPlantaPort
from matera.dominio.puertos.salida import EmisorTokenPort, PlantasPort, TablaReferenciaPort


class RegistrarPlanta(RegistrarPlantaPort):
    def __init__(
        self,
        tabla_referencia: TablaReferenciaPort,
        plantas: PlantasPort,
        emisor_token: EmisorTokenPort,
    ):
        self._tabla_referencia = tabla_referencia
        self._plantas = plantas
        self._emisor_token = emisor_token

    def registrar_planta(
        self, usuario_id: str, nombre: str, especie: str, dispositivo_id: str
    ) -> PlantaRegistrada:
        nombre = nombre.strip()
        especie = especie.strip().lower()
        dispositivo_id = dispositivo_id.strip()

        if not nombre:
            raise ParametroInvalidoError("nombre", "La planta necesita un nombre.")
        if not dispositivo_id:
            raise ParametroInvalidoError("dispositivo_id", "La planta necesita un dispositivo.")

        # Reglas de negocio: la especie debe estar en el catálogo
        # y un dispositivo no puede medir dos plantas a la vez.
        if self._tabla_referencia.obtener_por_nombre(especie) is None:
            raise EspecieNoSoportadaError(especie)
        if self._plantas.obtener_planta_por_dispositivo(dispositivo_id) is not None:
            raise DispositivoYaVinculadoError(dispositivo_id)

        planta = Planta(
            id=f"planta-{uuid.uuid4().hex[:8]}",
            nombre=nombre,
            especie=especie,
            usuario_id=usuario_id,
            dispositivo_id=dispositivo_id,
        )
        self._plantas.guardar_planta(planta)

        token = self._emisor_token.emitir_token_dispositivo(dispositivo_id, planta.id)
        return PlantaRegistrada(planta=planta, token_dispositivo=token)
