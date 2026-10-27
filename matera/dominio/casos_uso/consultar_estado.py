"""Caso de uso R5 y R6: estado actual de una planta (última lectura y su diagnóstico)."""
from matera.dominio.casos_uso.propiedad import obtener_planta_del_usuario
from matera.dominio.modelo import EstadoActualPlanta
from matera.dominio.puertos.entrada import ConsultarEstadoPort
from matera.dominio.puertos.salida import HistorialLecturasPort, PlantasPort, TablaReferenciaPort
from matera.dominio.validador import ValidadorDeEstado


class ConsultarEstado(ConsultarEstadoPort):
    def __init__(
        self,
        tabla_referencia: TablaReferenciaPort,
        plantas: PlantasPort,
        historial: HistorialLecturasPort,
    ):
        self._tabla_referencia = tabla_referencia
        self._plantas = plantas
        self._historial = historial

    def consultar_estado(self, usuario_id: str, planta_id: str) -> EstadoActualPlanta:
        planta = obtener_planta_del_usuario(self._plantas, usuario_id, planta_id)

        ultima_lectura = self._historial.obtener_ultima_lectura(planta.id)
        diagnostico = None
        if ultima_lectura is not None:
            especie = self._tabla_referencia.obtener_por_nombre(planta.especie)
            if especie is not None:
                diagnostico = ValidadorDeEstado.evaluar(ultima_lectura, especie)

        return EstadoActualPlanta(
            planta=planta,
            ultima_lectura=ultima_lectura,
            diagnostico=diagnostico,
        )
