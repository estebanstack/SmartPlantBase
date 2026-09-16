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
    Caso de uso: evaluar el estado de salud de una planta.
    Orquesta la construcción de la entidad de dominio, la consulta de la especie
    a través de la abstracción del repositorio y la ejecución de las reglas.
    """

    def __init__(self, especie_repository: EspecieRepository):
        self._especie_repo = especie_repository

    def ejecutar(self, entrada: DiagnosticoInputDTO) -> DiagnosticoResponseDTO:
        # 1. Transformación a entidad de dominio (valida invariantes físicas, RF6)
        medicion = Medicion(especie=entrada.especie, valores=entrada.valores)

        # 2. Búsqueda de la especie a través de la abstracción del repositorio (RA5)
        especie = self._especie_repo.obtener_por_nombre(medicion.especie)
        if not especie:
            raise EspecieNoSoportadaError(medicion.especie)

        # 3. Ejecución de las reglas de negocio en el dominio
        diagnostico = EvaluadorDiagnostico.evaluar(medicion, especie)

        # 4. Mapeo a DTO de salida
        return DiagnosticoResponseDTO(
            especie=diagnostico.especie,
            estado=diagnostico.estado.value,
            parametros=[
                ParametroDiagnosticoDTO(
                    nombre=p.nombre,
                    valor=p.valor,
                    unidad=p.unidad,
                    rango_optimo=p.rango_optimo,
                    estado=p.estado.value,
                )
                for p in diagnostico.parametros
            ],
            recomendaciones=diagnostico.recomendaciones,
        )


class ListarEspeciesUseCase:
    """Caso de uso: listar especies disponibles con sus rangos de referencia (RF5)."""

    def __init__(self, especie_repository: EspecieRepository):
        self._especie_repo = especie_repository

    def ejecutar(self) -> List[EspecieDTO]:
        return [
            EspecieDTO(
                nombre=esp.nombre,
                rangos={
                    nombre: RangoDetalleDTO(
                        min=rango.minimo,
                        max=rango.maximo,
                        unidad=rango.unidad,
                    )
                    for nombre, rango in esp.rangos.items()
                },
            )
            for esp in self._especie_repo.obtener_todas()
        ]
