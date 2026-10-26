"""
Pruebas de los casos de uso de gestión de sesiones QR (Capa de Aplicación).
Verifica GenerarSesionQRUseCase, AutorizarSesionQRUseCase y ConsultarSesionQRUseCase.
"""
from datetime import datetime, timedelta, timezone
import pytest

from src.application.use_cases import (
    AutorizarSesionQRUseCase,
    ConsultarSesionQRUseCase,
    GenerarSesionQRUseCase,
)
from src.domain.entities import EstadoSesionQR, SesionQR
from src.domain.exceptions import SesionQRInvalidaError, SesionQRNoEncontradaError
from src.infrastructure.repositories.memoria_sesion_qr_repository import MemoriaSesionQRRepository


@pytest.fixture
def repo():
    return MemoriaSesionQRRepository()


def test_generar_sesion_qr_use_case(repo):
    """Verifica que el caso de uso genere una sesión pendiente y la persista en el repositorio."""
    use_case = GenerarSesionQRUseCase(repo, duracion_segundos=120)
    resultado = use_case.ejecutar(sesion_id="sesion_manual_1")

    assert resultado.id == "sesion_manual_1"
    assert resultado.estado == "PENDIENTE"
    assert resultado.usuario_id is None
    assert resultado.token is None
    assert resultado.expira_en is not None

    persisitida = repo.obtener_por_id("sesion_manual_1")
    assert persisitida is not None
    assert persisitida.estado == EstadoSesionQR.PENDIENTE


def test_generar_sesion_qr_genera_uuid_si_no_se_pasa_id(repo):
    """Verifica la generación automática de ID único si no se suministra uno manual."""
    use_case = GenerarSesionQRUseCase(repo)
    resultado = use_case.ejecutar()

    assert resultado.id is not None
    assert len(resultado.id) > 10
    assert repo.obtener_por_id(resultado.id) is not None


def test_autorizar_sesion_qr_use_case_exitoso(repo):
    """Verifica que autorizar una sesión actualice el repositorio con los datos del usuario."""
    generador = GenerarSesionQRUseCase(repo, duracion_segundos=300)
    sesion_dto = generador.ejecutar("sesion_auth_1")

    autorizador = AutorizarSesionQRUseCase(repo)
    autorizada_dto = autorizador.ejecutar(
        sesion_id="sesion_auth_1",
        usuario_id="usuario_esteban",
        token="jwt_token_seguro_999",
    )

    assert autorizada_dto.id == "sesion_auth_1"
    assert autorizada_dto.estado == "AUTORIZADA"
    assert autorizada_dto.usuario_id == "usuario_esteban"
    assert autorizada_dto.token == "jwt_token_seguro_999"

    en_repo = repo.obtener_por_id("sesion_auth_1")
    assert en_repo.estado == EstadoSesionQR.AUTORIZADA


def test_autorizar_sesion_inexistente_lanza_error(repo):
    """Verifica que autorizar una sesión que no existe lance SesionQRNoEncontradaError."""
    autorizador = AutorizarSesionQRUseCase(repo)
    with pytest.raises(SesionQRNoEncontradaError, match="No se encontró la sesión QR 'inexistente'"):
        autorizador.ejecutar(
            sesion_id="inexistente",
            usuario_id="usuario_esteban",
            token="token_123",
        )


def test_consultar_sesion_qr_actualiza_si_expirada(repo):
    """Verifica que consultar una sesión vencida cambie su estado a EXPIRADA."""
    ahora = datetime.now(timezone.utc)
    sesion = SesionQR(
        id="qr_vencido",
        creada_en=ahora - timedelta(minutes=10),
        expira_en=ahora - timedelta(minutes=5),
        estado=EstadoSesionQR.PENDIENTE,
    )
    repo.guardar(sesion)

    consultar = ConsultarSesionQRUseCase(repo)
    resultado = consultar.ejecutar("qr_vencido")

    assert resultado.estado == "EXPIRADA"
    assert repo.obtener_por_id("qr_vencido").estado == EstadoSesionQR.EXPIRADA
