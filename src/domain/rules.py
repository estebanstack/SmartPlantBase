"""
Reglas de negocio del dominio botánico.
Contiene la clasificación de parámetros (RF2), la regla de agregación del
estado global (RF3) y la generación de recomendaciones (RF4).
"""
from typing import Dict, List, Tuple

from src.domain.entities import (
    Diagnostico,
    Especie,
    EstadoParametro,
    EstadoPlanta,
    Medicion,
    ParametroEvaluado,
    RangoParametro,
)


class EvaluadorDiagnostico:
    """
    Servicio de dominio puro que evalúa una medición contra los rangos de una especie.
    Agnóstico a frameworks y a mecanismos de persistencia (RA4).

    El método evaluar() no enumera parámetros: recorre los que la especie declare.
    Incorporar una nueva variable ambiental no modifica esta clase (OCP).
    """

    # Catálogo de recomendaciones por (parámetro, estado). Un parámetro sin entrada
    # propia recibe el texto genérico de _generar_recomendacion(): el cálculo queda
    # cerrado a modificación, el catálogo de textos sigue siendo extensible.
    _RECOMENDACIONES: Dict[Tuple[str, EstadoParametro], str] = {
        ("humedad", EstadoParametro.BAJO):
            "La humedad del sustrato está por debajo del rango recomendado: riegue moderadamente.",
        ("humedad", EstadoParametro.ALTO):
            "La humedad del sustrato supera el rango recomendado: suspenda el riego y facilite el drenaje.",
        ("luz", EstadoParametro.BAJO):
            "El nivel de luz es insuficiente para esta especie: ubique la planta en un lugar con mayor exposición solar.",
        ("luz", EstadoParametro.ALTO):
            "El nivel de luz es excesivo: proteja la planta con sombra parcial o retírela de la radiación solar directa.",
        ("temperatura", EstadoParametro.BAJO):
            "La temperatura ambiental es demasiado baja: traslade la planta a un espacio más cálido o protegido.",
        ("temperatura", EstadoParametro.ALTO):
            "La temperatura ambiental es excesiva: ventile el espacio o traslade la planta a un lugar fresco.",
    }

    @staticmethod
    def _clasificar_parametro(valor: float, rango: RangoParametro) -> EstadoParametro:
        """
        Clasifica un valor respecto al rango óptimo (RF2).
        El rango es cerrado: un valor igual al mínimo o al máximo se considera OPTIMO.
        """
        if valor < rango.minimo:
            return EstadoParametro.BAJO
        if valor > rango.maximo:
            return EstadoParametro.ALTO
        return EstadoParametro.OPTIMO

    @classmethod
    def _generar_recomendacion(cls, nombre_parametro: str, estado: EstadoParametro) -> str:
        """Devuelve la recomendación textual de un parámetro fuera de rango (RF4)."""
        return cls._RECOMENDACIONES.get(
            (nombre_parametro.lower(), estado),
            f"El parámetro {nombre_parametro} se encuentra en estado {estado.value}, ajuste las condiciones."
        )

    @classmethod
    def evaluar(cls, medicion: Medicion, especie: Especie) -> Diagnostico:
        """
        Evalúa una medición contra los rangos de referencia de la especie.
        Aplica RF2 (clasificación), RF3 (estado global) y RF4 (recomendaciones).
        """
        parametros_evaluados: List[ParametroEvaluado] = []
        recomendaciones: List[str] = []
        desviaciones = 0

        # Se recorren los parámetros declarados por la especie, no una lista fija.
        for nombre, rango in especie.rangos.items():
            valor = medicion.valor_de(nombre)
            estado = cls._clasificar_parametro(valor, rango)

            parametros_evaluados.append(
                ParametroEvaluado(
                    nombre=nombre,
                    valor=valor,
                    unidad=rango.unidad,
                    rango_optimo=(rango.minimo, rango.maximo),
                    estado=estado,
                )
            )

            if estado != EstadoParametro.OPTIMO:
                desviaciones += 1
                recomendaciones.append(cls._generar_recomendacion(nombre, estado))

        return Diagnostico(
            especie=especie.nombre,
            estado=cls._derivar_estado_global(desviaciones),
            parametros=parametros_evaluados,
            recomendaciones=recomendaciones,
        )

    @staticmethod
    def _derivar_estado_global(desviaciones: int) -> EstadoPlanta:
        """
        Regla de agregación del estado global (RF3):
        - 0 desviaciones: todas las variables en rango ideal -> SALUDABLE.
        - 1 desviación: estrés leve, corregible de forma aislada -> EN_RIESGO.
        - 2 o más: factores adversos simultáneos comprometen la supervivencia -> CRITICO.
        """
        if desviaciones == 0:
            return EstadoPlanta.SALUDABLE
        if desviaciones == 1:
            return EstadoPlanta.EN_RIESGO
        return EstadoPlanta.CRITICO
