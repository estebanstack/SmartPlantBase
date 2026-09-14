"""
Casos de uso de la aplicación (Orquestación).
Dependen de las abstracciones del Dominio (EspecieRepository, EvaluadorDiagnostico, Medicion).
"""
from typing import List

from src.application.dtos import (
    DiagnosticoInputDTO,
    DiagnosticoResponseDTO,
    EspecieDTO,
    ParametroDiagnosticoDTO,
    RangoDetalleDTO,
)
from src.domain.entities import Medicion
from src.domain.exceptions import EspecieNoSoportadaError
from src.domain.repositories import EspecieRepository
from src.domain.rules import EvaluadorDiagnostico


class EvaluarDiagnosticoUseCase:
    """
    Caso de uso: Evaluar el estado de salud de una planta.
    Orquesta la validación de la entidad del dominio, la consulta de la especie
    en la abstracción del repositorio y la evaluación de las reglas de negocio.
    """

    def __init__(self, especie_repository: EspecieRepository):
        self._especie_repo = especie_repository

    def ejecutar(self, entrada: DiagnosticoInputDTO) -> DiagnosticoResponseDTO:
        # 1. Transformación a entidad de dominio (RA6: la entidad valida límites físicos RF6)
        medicion = Medicion(
            especie=entrada.especie,
            humedad=entrada.humedad,
            luz=entrada.luz,
            temperatura=entrada.temperatura,
        )

        # 2. Búsqueda de la especie a través de la abstracción del repositorio (RA5)
        especie = self._especie_repo.obtener_por_nombre(medicion.especie)
        if not especie:
            raise EspecieNoSoportadaError(medicion.especie)

        # 3. Ejecución del servicio de reglas de negocio en el dominio
        diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

        # 4. Mapeo a DTO de salida
        parametros_dto = [
            ParametroDiagnosticoDTO(
                nombre=p.nombre,
                valor=p.valor,
                unidad=p.unidad,
                rango_optimo=p.rango_optimo,
                estado=p.estado.value,
            )
            for p in diagnostico.parametros
        ]

        return DiagnosticoResponseDTO(
            especie=diagnostico.especie,
            estado=diagnostico.estado.value,
            parametros=parametros_dto,
            recomendaciones=diagnostico.recomendaciones,
        )


class ListarEspeciesUseCase:
    """
    Caso de uso: Listar especies disponibles con sus rangos de referencia (RF5).
    """

    def __init__(self, especie_repository: EspecieRepository):
        self._especie_repo = especie_repository

    def ejecutar(self) -> List[EspecieDTO]:
        especies = self._especie_repo.obtener_todas()
        resultado: List[EspecieDTO] = []

        for esp in especies:
            dto = EspecieDTO(
                nombre=esp.nombre,
                rangos={
                    "humedad": RangoDetalleDTO(
                        min=esp.rango_humedad.minimo,
                        max=esp.rango_humedad.maximo,
                        unidad=esp.rango_humedad.unidad,
                    ),
                    "luz": RangoDetalleDTO(
                        min=esp.rango_luz.minimo,
                        max=esp.rango_luz.maximo,
                        unidad=esp.rango_luz.unidad,
                    ),
                    "temperatura": RangoDetalleDTO(
                        min=esp.rango_temperatura.minimo,
                        max=esp.rango_temperatura.maximo,
                        unidad=esp.rango_temperatura.unidad,
                    ),
                },
            )
            resultado.append(dto)

        return resultado
