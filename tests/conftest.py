"""
Configuración compartida de pytest.

create_app() lee el archivo .env (load_dotenv). Sin esto, las pruebas dependerían del
.env de cada computador: con CARGAR_DATOS_DEMO=0 no existirían Ana y Carlos, y con
TABLA_REFERENCIA_DRIVER=bd cambiaría la fuente de las especies.

Antes de cada prueba se fijan aquí los valores de prueba. load_dotenv() no sobrescribe
variables que ya existen, así que el .env local deja de influir en los resultados.
Las pruebas que necesitan otro valor lo pasan explícitamente a create_app().
"""
import pytest

CONFIGURACION_DE_PRUEBAS = {
    "TABLA_REFERENCIA_DRIVER": "csv",
    "CARGAR_DATOS_DEMO": "1",
    "JWT_SECRET": "clave-solo-para-pruebas-con-32-bytes-o-mas",
}


@pytest.fixture(autouse=True)
def configuracion_aislada(monkeypatch):
    for variable, valor in CONFIGURACION_DE_PRUEBAS.items():
        monkeypatch.setenv(variable, valor)
