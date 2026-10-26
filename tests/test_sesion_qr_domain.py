"""
Pruebas unitarias para la entidad de dominio SesionQR.
Verifica las invariantes de negocio, transiciones de estado, autorización y expiración.
"""
from datetime import datetime, timedelta, timezone
import pytest

from src.domain.entities import EstadoSesionQR, SesionQR
from src.domain.exceptions import SesionQRInvalidaError


def test_creacion_sesion_qr_por_defecto():
    """Verifica que una nueva sesión QR inicie en estado PENDIENTE y sin usuario/token."""
    sesion = SesionQR(id="qr_test_123")
    assert sesion.id == "qr_test_123"
    assert sesion.estado == EstadoSesionQR.PENDIENTE
    assert sesion.usuario_id is None
    assert sesion.token is None
    assert sesion.esta_expirada() is False


def test_autorizar_sesion_qr_exitosa():
    """Verifica que la autorización asigne usuario, token y cambie el estado a AUTORIZADA."""
    ahora = datetime.now(timezone.utc)
    sesion = SesionQR(
        id="qr_test_456",
        creada_en=ahora,
        expira_en=ahora + timedelta(minutes=5),
    )

    sesion.autorizar(usuario_id="user_abc", token="jwt_token_xyz", ahora=ahora)

    assert sesion.estado == EstadoSesionQR.AUTORIZADA
    assert sesion.usuario_id == "user_abc"
    assert sesion.token == "jwt_token_xyz"


def test_autorizar_sesion_qr_expirada_lanza_error():
    """Verifica que intentar autorizar una sesión expirada marque EXPIRADA y lance excepción."""
    ahora = datetime.now(timezone.utc)
    expirada_en = ahora - timedelta(seconds=1)
    sesion = SesionQR(
        id="qr_expired",
        creada_en=ahora - timedelta(minutes=5),
        expira_en=expirada_en,
    )

    assert sesion.esta_expirada(ahora) is True

    with pytest.raises(SesionQRInvalidaError, match="expirado"):
        sesion.autorizar(usuario_id="user_abc", token="jwt_token_xyz", ahora=ahora)

    assert sesion.estado == EstadoSesionQR.EXPIRADA


def test_autorizar_sesion_ya_autorizada_lanza_error():
    """Verifica que no se pueda autorizar dos veces la misma sesión QR (invariante de un solo uso)."""
    ahora = datetime.now(timezone.utc)
    sesion = SesionQR(
        id="qr_reauth",
        creada_en=ahora,
        expira_en=ahora + timedelta(minutes=5),
    )
    sesion.autorizar(usuario_id="user_1", token="tok_1", ahora=ahora)

    with pytest.raises(SesionQRInvalidaError, match="no está pendiente"):
        sesion.autorizar(usuario_id="user_2", token="tok_2", ahora=ahora)


def test_autorizar_con_parametros_vacios():
    """Verifica que no se permitan usuario_id o token vacíos."""
    sesion = SesionQR(id="qr_empty_params")

    with pytest.raises(ValueError, match="usuario_id es obligatorio"):
        sesion.autorizar(usuario_id="", token="tok_valido")

    with pytest.raises(ValueError, match="token de autenticación es obligatorio"):
        sesion.autorizar(usuario_id="usr_valido", token="   ")
