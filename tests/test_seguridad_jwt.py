"""
Pruebas de Seguridad con JWT y Control de Acceso (R7).
Verifica:
1. Emisión de tokens de usuario y dispositivo con PyJWT fuera del dominio.
2. Validación en el adaptador de entrada (seguridad.py + verificador_jwt.py).
3. Regla de negocio en el dominio: un usuario sólo puede consultar el estado e historial de sus propias plantas (403).
4. Rechazo de tokens con alcance incorrecto (ej. token de dispositivo usado en endpoint de usuario).
"""
import tempfile
from pathlib import Path
import pytest

from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.app import create_app

CLAVE_PRUEBAS = "clave-solo-para-pruebas-con-32-bytes-o-mas"


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta = f.name
    yield ruta
    Path(ruta).unlink(missing_ok=True)


@pytest.fixture
def app(temp_db):
    test_app = create_app(ruta_bd=temp_db, clave_jwt=CLAVE_PRUEBAS)
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def emisor_jwt():
    return JwtEmisorTokenAdapter(secret_key=CLAVE_PRUEBAS)


def test_flujo_registro_y_login_usuario(client):
    """Verifica registro e inicio de sesión con emisión de JWT."""
    # 1. Registro
    payload_registro = {
        "nombre": "Esteban Estudiante",
        "email": "esteban@matera.edu.co",
        "password": "claveSuperSegura2026",
    }
    resp_reg = client.post("/api/auth/registro", json=payload_registro)
    assert resp_reg.status_code == 201
    datos_reg = resp_reg.get_json()
    assert "token" in datos_reg
    assert datos_reg["usuario"]["email"] == "esteban@matera.edu.co"

    # 2. Rechazo de correo duplicado (409)
    resp_dup = client.post("/api/auth/registro", json=payload_registro)
    assert resp_dup.status_code == 409
    assert resp_dup.get_json()["error"] == "USUARIO_YA_EXISTE"

    # 3. Login exitoso
    resp_login = client.post("/api/auth/login", json={
        "email": "esteban@matera.edu.co",
        "password": "claveSuperSegura2026",
    })
    assert resp_login.status_code == 200
    datos_login = resp_login.get_json()
    assert "token" in datos_login
    assert datos_login["usuario"]["email"] == "esteban@matera.edu.co"

    # 4. Login con clave errónea (401)
    resp_bad = client.post("/api/auth/login", json={
        "email": "esteban@matera.edu.co",
        "password": "claveIncorrecta",
    })
    assert resp_bad.status_code == 401
    assert resp_bad.get_json()["error"] == "CREDENCIALES_INVALIDAS"


def test_acceso_protegido_requiere_token(client):
    """Peticiones a /api/plantas sin cabecera Authorization son rechazadas con 401."""
    resp = client.get("/api/plantas")
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "AUTORIZACION_REQUERIDA"


def test_token_malformado_o_invalido(client):
    """Tokens con firma o formato incorrecto son rechazados con 401."""
    headers = {"Authorization": "Bearer token_completamente_invalido_xyz"}
    resp = client.get("/api/plantas", headers=headers)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "TOKEN_INVALIDO"


def test_regla_propiedad_planta_propia_vs_ajena(client):
    """
    R7: Ana (usr-ana) puede consultar su planta (planta-01).
    Carlos (usr-carlos) es rechazado con 403 al intentar consultar la planta de Ana.
    """
    # 1. Login como Ana
    login_ana = client.post("/api/auth/login", json={
        "email": "ana@matera.edu.co",
        "password": "clave123",
    }).get_json()
    token_ana = login_ana["token"]
    headers_ana = {"Authorization": f"Bearer {token_ana}"}

    # 2. Login como Carlos
    login_carlos = client.post("/api/auth/login", json={
        "email": "carlos@matera.edu.co",
        "password": "clave123",
    }).get_json()
    token_carlos = login_carlos["token"]
    headers_carlos = {"Authorization": f"Bearer {token_carlos}"}

    # 3. Ana consulta planta-01 (suya) -> 200 OK
    resp_ana = client.get("/api/plantas/planta-01/estado", headers=headers_ana)
    assert resp_ana.status_code == 200
    datos_ana = resp_ana.get_json()
    assert datos_ana["planta"]["id"] == "planta-01"
    assert datos_ana["planta"]["usuario_id"] == "usr-ana"

    # 4. Carlos intenta consultar planta-01 (de Ana) -> 403 Forbidden por regla de dominio
    resp_carlos = client.get("/api/plantas/planta-01/estado", headers=headers_carlos)
    assert resp_carlos.status_code == 403
    datos_carlos = resp_carlos.get_json()
    assert datos_carlos["error"] == "ACCESO_DENEGADO"

    # 5. Carlos consulta planta-02 (suya) -> 200 OK
    resp_carlos_ok = client.get("/api/plantas/planta-02/estado", headers=headers_carlos)
    assert resp_carlos_ok.status_code == 200
    assert resp_carlos_ok.get_json()["planta"]["id"] == "planta-02"


def test_token_de_dispositivo_rechazado_en_endpoints_de_usuario(client, emisor_jwt):
    """
    R7: Un token emitido para un sensor ESP32 (scope='dispositivo')
    no puede ser utilizado para acceder a endpoints del frontend/usuario (403).
    """
    token_disp = emisor_jwt.emitir_token_dispositivo(
        dispositivo_id="esp32-01",
        planta_id="planta-01",
    )
    headers = {"Authorization": f"Bearer {token_disp}"}

    # Intento de listar plantas
    resp = client.get("/api/plantas", headers=headers)
    assert resp.status_code == 403
    datos = resp.get_json()
    assert datos["error"] == "ACCESO_DENEGADO"
    assert datos["detalle"]["scope_presente"] == "dispositivo"


def test_token_firmado_con_otra_clave_es_rechazado(client):
    """Un token con firma válida pero de otra clave (por ejemplo, fabricado por fuera) no entra."""
    falso = JwtEmisorTokenAdapter(secret_key="otra-clave-distinta-tambien-de-32-bytes").emitir_token_usuario("usr-ana", "ana@matera.edu.co")
    resp = client.get("/api/plantas", headers={"Authorization": f"Bearer {falso}"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "TOKEN_INVALIDO"


def test_token_expirado_es_rechazado(client):
    """Un token vencido devuelve TOKEN_EXPIRADO."""
    from datetime import datetime, timedelta, timezone
    import jwt

    vencido = jwt.encode(
        {"sub": "usr-ana", "scope": "usuario", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        CLAVE_PRUEBAS,
        algorithm="HS256",
    )
    resp = client.get("/api/plantas", headers={"Authorization": f"Bearer {vencido}"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "TOKEN_EXPIRADO"
