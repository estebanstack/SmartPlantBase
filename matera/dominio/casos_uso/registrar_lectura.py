"""
Caso de uso R2 y R5: un dispositivo reporta una lectura.
Se busca la planta del dispositivo, se evalúa contra su especie, se guarda en el historial
y se notifica en tiempo real al propietario a través de NotificadorTiempoRealPort.
"""
from typing import Mapping, Optional

from matera.dominio.excepciones import DispositivoNoEncontradoError, EspecieNoSoportadaError
from matera.dominio.modelo import Diagnostico, EstadoPlanta, Lectura
from matera.dominio.puertos.entrada import RegistrarLecturaPort
from matera.dominio.puertos.salida import (
    HistorialLecturasPort,
    NotificadorTiempoRealPort,
    PlantasPort,
    TablaReferenciaPort,
)
from matera.dominio.validador import ValidadorDeEstado


class RegistrarLectura(RegistrarLecturaPort):
    def __init__(
        self,
        tabla_referencia: TablaReferenciaPort,
        plantas: PlantasPort,
        historial: HistorialLecturasPort,
        notificador: Optional[NotificadorTiempoRealPort] = None,
    ):
        self._tabla_referencia = tabla_referencia
        self._plantas = plantas
        self._historial = historial
        self._notificador = notificador

    def registrar(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> Diagnostico:
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
        self._historial.guardar_lectura(lectura, diagnostico)

        if self._notificador is not None:
            self._notificador.notificar_telemetria(planta, lectura, diagnostico)
            if diagnostico.estado in (EstadoPlanta.EN_RIESGO, EstadoPlanta.CRITICO):
                self._notificador.notificar_alerta(planta, lectura, diagnostico)

        return diagnostico

