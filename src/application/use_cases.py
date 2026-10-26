"""
Casos de uso de la aplicación (Orquestación).
Dependen de las abstracciones del Dominio (EspecieRepository, EvaluadorDiagnostico, Medicion).
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import uuid

from src.application.dtos import (
    DiagnosticoInputDTO,
    DiagnosticoResponseDTO,
    EspecieDTO,
    ParametroDiagnosticoDTO,
    RangoDetalleDTO,
    SesionQRDTO,
)
from src.domain.entities import EstadoSesionQR, Medicion, SesionQR
from src.domain.exceptions import EspecieNoSoportadaError, SesionQRNoEncontradaError
from src.domain.repositories import EspecieRepository, SesionQRRepository
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


class GenerarSesionQRUseCase:
    """
    Caso de uso: generar una nueva sesión QR para inicio de sesión o vinculación.
    Crea la entidad en estado PENDIENTE con tiempo de expiración configurable.
    """

    def __init__(self, sesion_repo: SesionQRRepository, duracion_segundos: int = 300):
        self._sesion_repo = sesion_repo
        self._duracion_segundos = duracion_segundos

    def ejecutar(self, sesion_id: Optional[str] = None) -> SesionQRDTO:
        ahora = datetime.now(timezone.utc)
        id_final = sesion_id or uuid.uuid4().hex
        expira_en = ahora + timedelta(seconds=self._duracion_segundos)

        sesion = SesionQR(
            id=id_final,
            estado=EstadoSesionQR.PENDIENTE,
            creada_en=ahora,
            expira_en=expira_en,
        )
        self._sesion_repo.guardar(sesion)

        return SesionQRDTO(
            id=sesion.id,
            estado=sesion.estado.value,
            usuario_id=sesion.usuario_id,
            token=sesion.token,
            expira_en=sesion.expira_en.isoformat(),
        )


class AutorizarSesionQRUseCase:
    """
    Caso de uso: autorizar una sesión QR desde un dispositivo móvil o cliente autenticado.
    Totalmente agnóstico de frameworks de transporte (Flask/SocketIO).
    """

    def __init__(self, sesion_repo: SesionQRRepository):
        self._sesion_repo = sesion_repo

    def ejecutar(self, sesion_id: str, usuario_id: str, token: str) -> SesionQRDTO:
        sesion = self._sesion_repo.obtener_por_id(sesion_id)
        if sesion is None:
            raise SesionQRNoEncontradaError(sesion_id)

        sesion.autorizar(usuario_id=usuario_id, token=token)
        self._sesion_repo.guardar(sesion)

        return SesionQRDTO(
            id=sesion.id,
            estado=sesion.estado.value,
            usuario_id=sesion.usuario_id,
            token=sesion.token,
            expira_en=sesion.expira_en.isoformat() if sesion.expira_en else None,
        )


class ConsultarSesionQRUseCase:
    """
    Caso de uso: consultar el estado actual de una sesión QR.
    Actualiza automáticamente a EXPIRADA si ha transcurrido el tiempo límite.
    """

    def __init__(self, sesion_repo: SesionQRRepository):
        self._sesion_repo = sesion_repo

    def ejecutar(self, sesion_id: str) -> SesionQRDTO:
        sesion = self._sesion_repo.obtener_por_id(sesion_id)
        if sesion is None:
            raise SesionQRNoEncontradaError(sesion_id)

        if sesion.estado == EstadoSesionQR.PENDIENTE and sesion.esta_expirada():
            sesion.estado = EstadoSesionQR.EXPIRADA
            self._sesion_repo.guardar(sesion)

        return SesionQRDTO(
            id=sesion.id,
            estado=sesion.estado.value,
            usuario_id=sesion.usuario_id,
            token=sesion.token,
            expira_en=sesion.expira_en.isoformat() if sesion.expira_en else None,
        )

