"""
Validador de Estado Botánico (Núcleo Hexagonal).
Regla de negocio central: clasifica cada parámetro y deriva el estado global de la planta.
No sabe de dónde vienen los datos: lo usan los casos de uso de matera/dominio/casos_uso/.
"""
from typing import Dict, List, Tuple

from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    EstadoParametro,
    EstadoPlanta,
    Lectura,
    ParametroEvaluado,
    RangoParametro,
)


class ValidadorDeEstado:
    """
    Servicio de dominio puro que evalúa una lectura contra los rangos de referencia de una especie.
    Agnóstico a frameworks, HTTP y mecanismos de almacenamiento.
    """

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
        Clasifica un valor respecto al rango óptimo.
        El rango es cerrado: un valor en los extremos se considera OPTIMO.
        """
        if valor < rango.minimo:
            return EstadoParametro.BAJO
        if valor > rango.maximo:
            return EstadoParametro.ALTO
        return EstadoParametro.OPTIMO

    @classmethod
    def _generar_recomendacion(cls, nombre_parametro: str, estado: EstadoParametro) -> str:
        """Devuelve la recomendación para un parámetro fuera de rango."""
        return cls._RECOMENDACIONES.get(
            (nombre_parametro.lower(), estado),
            f"El parámetro {nombre_parametro} se encuentra en estado {estado.value}, ajuste las condiciones."
        )

    @classmethod
    def evaluar(cls, lectura: Lectura, especie: Especie) -> Diagnostico:
        """
        Evalúa una lectura contra los rangos declarados por la especie.
        Aplica clasificación por variable, derivación de estado global y generación de recomendaciones.
        """
        parametros_evaluados: List[ParametroEvaluado] = []
        recomendaciones: List[str] = []
        desviaciones = 0

        for nombre, rango in especie.rangos.items():
            valor = lectura.valor_de(nombre)
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
        Regla de agregación del estado global:
        - 0 desviaciones -> SALUDABLE.
        - 1 desviación -> EN_RIESGO.
        - 2 o más desviaciones -> CRITICO.
        """
        if desviaciones == 0:
            return EstadoPlanta.SALUDABLE
        if desviaciones == 1:
            return EstadoPlanta.EN_RIESGO
        return EstadoPlanta.CRITICO
