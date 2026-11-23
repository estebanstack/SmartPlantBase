"""
Caso de uso R2 y R5: un dispositivo reporta una lectura.
Se busca la planta del dispositivo, se evalúa contra su especie, se guarda en el historial
y se notifica en tiempo real al propietario a través de NotificadorTiempoRealPort.
"""
import logging
from typing import Mapping, Optional

from matera.dominio.excepciones import DispositivoNoEncontradoError, EspecieNoSoportadaError
from matera.dominio.gamificacion import MotorGamificacion, PerfilGamificacion, ResultadoLectura
from matera.dominio.modelo import Diagnostico, EstadoPlanta, Lectura
from matera.dominio.puertos.entrada import RegistrarLecturaPort
from matera.dominio.puertos.salida import (
    GamificacionPort,
    HistorialLecturasPort,
    NotificadorTiempoRealPort,
    PlantasPort,
    TablaReferenciaPort,
)
from matera.dominio.validador import ValidadorDeEstado

logger = logging.getLogger(__name__)


class RegistrarLectura(RegistrarLecturaPort):
    def __init__(
        self,
        tabla_referencia: TablaReferenciaPort,
        plantas: PlantasPort,
        historial: HistorialLecturasPort,
        notificador: Optional[NotificadorTiempoRealPort] = None,
        gamificacion: Optional[GamificacionPort] = None,
    ):
        self._tabla_referencia = tabla_referencia
        self._plantas = plantas
        self._historial = historial
        self._notificador = notificador
        self._gamificacion = gamificacion

    def registrar(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> Diagnostico:
        return self.registrar_con_gotchi(dispositivo_id, valores, marca_tiempo).diagnostico

    def registrar_con_gotchi(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> ResultadoLectura:
        planta = self._plantas.obtener_planta_por_dispositivo(dispositivo_id)
        if planta is None:
            raise DispositivoNoEncontradoError(dispositivo_id)

        lectura = Lectura(
            especie=planta.especie,
            valores=valores,
            marca_tiempo=marca_tiempo,
            dispositivo_id=dispositivo_id,
            planta_id=planta.id,
        )

        especie_entidad = self._tabla_referencia.obtener_por_nombre(planta.especie)
        if especie_entidad is None:
            raise EspecieNoSoportadaError(planta.especie)

        diagnostico = ValidadorDeEstado.evaluar(lectura, especie_entidad)
        # La lectura anterior se pide antes de guardar la nueva: sirve para detectar el riego
        anterior = self._historial.obtener_ultima_lectura(planta.id)
        self._historial.guardar_lectura(lectura, diagnostico)
        gotchi = self._actualizar_gotchi(planta.id, diagnostico, lectura, anterior)

        if self._notificador is not None:
            self._notificador.notificar_telemetria(planta, lectura, diagnostico, gotchi)
            if diagnostico.estado in (EstadoPlanta.EN_RIESGO, EstadoPlanta.CRITICO):
                self._notificador.notificar_alerta(planta, lectura, diagnostico)

        return ResultadoLectura(diagnostico, gotchi)

    def _actualizar_gotchi(
        self,
        planta_id: str,
        diagnostico: Diagnostico,
        lectura: Lectura,
        anterior: Optional[Lectura],
    ) -> Optional[PerfilGamificacion]:
        """
        El Gotchi es un extra: si falla (base de datos, regla), la lectura ya quedó guardada
        y el dispositivo igual recibe su 201, solo que sin el campo gotchi.
        """
        if self._gamificacion is None:
            return None
        try:
            perfil = self._gamificacion.obtener_perfil(planta_id) or PerfilGamificacion(planta_id=planta_id)
            nuevo = MotorGamificacion.evaluar(perfil, diagnostico, lectura, anterior)
            self._gamificacion.guardar_perfil(nuevo)
            return nuevo
        except Exception:
            logger.warning("No se pudo actualizar el Matera-Gotchi de %s", planta_id, exc_info=True)
            return None

