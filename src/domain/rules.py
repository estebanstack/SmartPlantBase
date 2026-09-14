"""
Reglas de negocio del dominio botánico.
Contiene la lógica de evaluación (RF2), regla de agregación global (RF3)
y generación de recomendaciones (RF4).
"""
from typing import List
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
    Servicio de dominio puro que evalúa mediciones contra los rangos de una especie.
    Agnóstico a frameworks y mecanismos de persistencia (RA4).
    """

    @staticmethod
    def _clasificar_parametro(valor: float, rango: RangoParametro) -> EstadoParametro:
        """Clasifica un valor numérico respecto al rango óptimo (RF2)."""
        if valor < rango.minimo:
            return EstadoParametro.BAJO
        elif valor > rango.maximo:
            return EstadoParametro.ALTO
        return EstadoParametro.OPTIMO

    @staticmethod
    def _generar_recomendacion(nombre_parametro: str, estado: EstadoParametro) -> str:
        """Genera una recomendación textual específica cuando un parámetro está fuera de rango (RF4)."""
        recomendaciones = {
            ("humedad", EstadoParametro.BAJO): (
                "La humedad del sustrato está por debajo del rango recomendado: riegue moderadamente."
            ),
            ("humedad", EstadoParametro.ALTO): (
                "La humedad del sustrato supera el rango recomendado: suspenda el riego y facilite el drenaje."
            ),
            ("luz", EstadoParametro.BAJO): (
                "El nivel de luz es insuficiente para esta especie: ubique la planta en un lugar con mayor exposición solar."
            ),
            ("luz", EstadoParametro.ALTO): (
                "El nivel de luz es excesivo: proteja la planta con sombra parcial o retírela de la radiación solar directa."
            ),
            ("temperatura", EstadoParametro.BAJO): (
                "La temperatura ambiental es demasiado baja: traslade la planta a un espacio más cálido o protegido."
            ),
            ("temperatura", EstadoParametro.ALTO): (
                "La temperatura ambiental es excesiva: ventile el espacio o traslade la planta a un lugar fresco."
            ),
        }
        return recomendaciones.get(
            (nombre_parametro.lower(), estado),
            f"El parámetro {nombre_parametro} se encuentra en estado {estado.value}, ajuste las condiciones."
        )

    @classmethod
    def evaluar(cls, medicion: Medicion, especie: Especie) -> Diagnostico:
        """
        Ejecuta la evaluación integral de una medición contra la especie dada.
        Aplica RF2 (clasificación), RF3 (estado global) y RF4 (recomendaciones).
        """
        parametros_evaluados: List[ParametroEvaluado] = []
        recomendaciones: List[str] = []
        desviaciones: int = 0

        # Mapeo de parámetros a evaluar
        evaluaciones = [
            ("humedad", medicion.humedad, especie.rango_humedad),
            ("luz", medicion.luz, especie.rango_luz),
            ("temperatura", medicion.temperatura, especie.rango_temperatura),
        ]

        for nombre, valor, rango in evaluaciones:
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

        # Regla de agregación del estado global (RF3):
        # - 0 desviaciones: La planta cuenta con todas sus variables en rango ideal -> SALUDABLE.
        # - 1 desviación: Estrés leve corregible de forma aislada -> EN_RIESGO.
        # - 2 o más desviaciones: Múltiples factores adversos simultáneos comprometen la supervivencia -> CRITICO.
        if desviaciones == 0:
            estado_global = EstadoPlanta.SALUDABLE
        elif desviaciones == 1:
            estado_global = EstadoPlanta.EN_RIESGO
        else:
            estado_global = EstadoPlanta.CRITICO

        return Diagnostico(
            especie=especie.nombre,
            estado=estado_global,
            parametros=parametros_evaluados,
            recomendaciones=recomendaciones,
        )
