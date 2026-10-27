"""Caso de uso R1: diagnosticar una medición ingresada a mano desde el front."""
from typing import Mapping

from matera.dominio.excepciones import EspecieNoSoportadaError
from matera.dominio.modelo import Diagnostico, Lectura
from matera.dominio.puertos.entrada import ValidarLecturaPort
from matera.dominio.puertos.salida import TablaReferenciaPort
from matera.dominio.validador import ValidadorDeEstado


class ValidarLectura(ValidarLecturaPort):
    def __init__(self, tabla_referencia: TablaReferenciaPort):
        self._tabla_referencia = tabla_referencia

    def validar(self, especie: str, valores: Mapping[str, float]) -> Diagnostico:
        lectura = Lectura(especie=especie, valores=valores)
        especie_entidad = self._tabla_referencia.obtener_por_nombre(lectura.especie)
        if especie_entidad is None:
            raise EspecieNoSoportadaError(lectura.especie)
        return ValidadorDeEstado.evaluar(lectura, especie_entidad)
