"""
Pruebas de integración de Adaptadores de Salida (R4 y R5).
Verifica la intercambiabilidad de TablaReferenciaPort (CSV vs SQLite)
y la persistencia de HistorialLecturasPort, UsuariosPort y PlantasPort en SQLite.
"""
from pathlib import Path
import sqlite3
import tempfile
import pytest

from matera.adaptadores.salida.historial_bd import BdHistorialLecturasAdapter
from matera.adaptadores.salida.plantas_bd import BdPlantasAdapter
from matera.adaptadores.salida.sqlite_bd import conectar, inicializar_bd
from matera.adaptadores.salida.usuarios_bd import BdUsuariosAdapter
from matera.adaptadores.salida.tabla_bd import BdTablaReferenciaAdapter
from matera.adaptadores.salida.tabla_csv import CsvTablaReferenciaAdapter
from matera.app import create_app
from matera.dominio.modelo import Diagnostico, EstadoPlanta, Lectura


@pytest.fixture
def temp_db():
    """Base SQLite temporal, creada con los scripts de data/bd/ y los datos de demostración."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta = f.name
    inicializar_bd(ruta, datos_demo=True)
    yield ruta
    Path(ruta).unlink(missing_ok=True)


@pytest.fixture
def ruta_csv():
    return str(Path(__file__).parent.parent / "data" / "especies_referencia.csv")


def test_intercambiabilidad_tabla_referencia_csv_vs_bd(temp_db, ruta_csv):
    """
    R4: Demuestra que CsvTablaReferenciaAdapter y BdTablaReferenciaAdapter
    satisfacen el mismo contrato TablaReferenciaPort y devuelven especies equivalentes.
    """
    adaptador_csv = CsvTablaReferenciaAdapter(ruta_csv)
    adaptador_bd = BdTablaReferenciaAdapter(temp_db)

    # 1. Ambas devuelven las 5 especies
    todas_csv = {e.nombre: e for e in adaptador_csv.obtener_todas()}
    todas_bd = {e.nombre: e for e in adaptador_bd.obtener_todas()}

    assert len(todas_csv) == 5
    assert len(todas_bd) == 5
    assert set(todas_csv.keys()) == set(todas_bd.keys())

    # 2. Rangos de referencia idénticos para cada especie
    for nombre in todas_csv:
        esp_csv = todas_csv[nombre]
        esp_bd = todas_bd[nombre]
        assert esp_csv.nombre == esp_bd.nombre
        for param in esp_csv.rangos:
            assert esp_bd.rangos[param].minimo == esp_csv.rangos[param].minimo
            assert esp_bd.rangos[param].maximo == esp_csv.rangos[param].maximo
            assert esp_bd.rangos[param].unidad == esp_csv.rangos[param].unidad


def test_historial_lecturas_sqlite(temp_db):
    """
    R5: Persistencia y consulta de lecturas e historial en SQLite.
    """
    adaptador = BdHistorialLecturasAdapter(temp_db)

    lectura_1 = Lectura(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        marca_tiempo="2026-10-26T12:00:00Z",
        dispositivo_id="esp32-01",
        planta_id="planta-01",
    )
    diagnostico_1 = Diagnostico(
        especie="sansevieria",
        estado=EstadoPlanta.SALUDABLE,
        parametros=[],
        recomendaciones=[],
    )

    adaptador.guardar_lectura(lectura_1, diagnostico_1)

    # Segunda lectura (más reciente)
    lectura_2 = Lectura(
        especie="sansevieria",
        valores={"humedad": 15.0, "luz": 600.0, "temperatura": 25.0},
        marca_tiempo="2026-10-26T12:05:00Z",
        dispositivo_id="esp32-01",
        planta_id="planta-01",
    )
    diagnostico_2 = Diagnostico(
        especie="sansevieria",
        estado=EstadoPlanta.EN_RIESGO,
        parametros=[],
        recomendaciones=["Regar moderadamente"],
    )

    adaptador.guardar_lectura(lectura_2, diagnostico_2)

    # Obtener última lectura
    ultima = adaptador.obtener_ultima_lectura("planta-01")
    assert ultima is not None
    assert ultima.valor_de("humedad") == 15.0
    assert ultima.marca_tiempo == "2026-10-26T12:05:00Z"

    # Obtener historial (orden descendente)
    historial = adaptador.obtener_historial("planta-01", limite=10)
    assert len(historial) == 2
    assert historial[0].lectura.marca_tiempo == "2026-10-26T12:05:00Z"
    assert historial[0].estado == EstadoPlanta.EN_RIESGO
    assert historial[1].lectura.marca_tiempo == "2026-10-26T12:00:00Z"
    assert historial[1].estado == EstadoPlanta.SALUDABLE


def test_usuarios_y_plantas_sqlite(temp_db):
    """R7: los datos de demostración y las consultas de usuarios y plantas en SQLite."""
    usuarios = BdUsuariosAdapter(temp_db)
    plantas = BdPlantasAdapter(temp_db)

    ana = usuarios.obtener_usuario_por_email("ANA@matera.edu.co")
    assert ana is not None
    assert ana.id == "usr-ana"
    assert ana.nombre == "Ana María"

    planta = plantas.obtener_planta_por_id("planta-01")
    assert planta is not None
    assert planta.usuario_id == "usr-ana"
    assert planta.dispositivo_id == "esp32-01"

    assert plantas.obtener_planta_por_dispositivo("esp32-01").id == "planta-01"
    assert [p.id for p in plantas.listar_plantas_por_usuario("usr-ana")] == ["planta-01"]


def test_historial_guarda_los_valores_como_json(temp_db):
    """Los valores van en una columna JSON: la tabla no tiene una columna por parámetro."""
    adaptador = BdHistorialLecturasAdapter(temp_db)
    lectura = Lectura(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
        planta_id="planta-01",
    )
    adaptador.guardar_lectura(lectura, Diagnostico("sansevieria", EstadoPlanta.SALUDABLE, [], []))

    with conectar(temp_db) as con:
        columnas = {fila["name"] for fila in con.execute("PRAGMA table_info(historial_lecturas)")}
    assert "valores" in columnas
    assert not {"humedad", "luz", "temperatura"} & columnas
    assert dict(adaptador.obtener_ultima_lectura("planta-01").valores) == dict(lectura.valores)


def test_sin_datos_demo_no_hay_usuarios_pero_si_especies():
    """Los usuarios de prueba solo existen si se piden; las especies siempre se cargan."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ruta = f.name
    try:
        inicializar_bd(ruta, datos_demo=False)
        assert BdUsuariosAdapter(ruta).obtener_usuario_por_email("ana@matera.edu.co") is None
        assert len(BdTablaReferenciaAdapter(ruta).obtener_todas()) == 5
    finally:
        Path(ruta).unlink(missing_ok=True)


def test_create_app_switch_csv_vs_bd(temp_db, ruta_csv):
    """
    R4: create_app() soporta conmutar entre 'csv' y 'bd' mediante driver_tabla.
    """
    app_csv = create_app(driver_tabla="csv", ruta_csv=ruta_csv, ruta_bd=temp_db)
    client_csv = app_csv.test_client()
    resp_csv = client_csv.get("/api/v1/especies")
    assert resp_csv.status_code == 200
    assert len(resp_csv.get_json()) == 5

    app_bd = create_app(driver_tabla="bd", ruta_csv=ruta_csv, ruta_bd=temp_db)
    client_bd = app_bd.test_client()
    resp_bd = client_bd.get("/api/v1/especies")
    assert resp_bd.status_code == 200
    assert len(resp_bd.get_json()) == 5


def test_hasher_werkzeug_usa_sal_y_verifica():
    """R7: el adaptador real de contraseñas genera hashes distintos para la misma clave y los verifica."""
    from matera.adaptadores.salida.hasher_werkzeug import WerkzeugHasherAdapter

    hasher = WerkzeugHasherAdapter()
    hash_1 = hasher.generar_hash("clave123")
    hash_2 = hasher.generar_hash("clave123")

    assert hash_1 != "clave123"
    assert hash_1 != hash_2  # sal aleatoria
    assert hasher.verificar("clave123", hash_1)
    assert not hasher.verificar("otra", hash_1)


def test_conectar_cierra_la_conexion_al_salir_del_with(temp_db):
    with conectar(temp_db) as con:
        con.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        con.execute("SELECT 1")  # ya está cerrada


def test_conectar_deshace_los_cambios_si_hay_un_error(temp_db):
    with pytest.raises(RuntimeError):
        with conectar(temp_db) as con:
            con.execute("DELETE FROM especies")
            raise RuntimeError("falla a mitad de la operación")
    with conectar(temp_db) as con:
        assert con.execute("SELECT COUNT(*) FROM especies").fetchone()[0] == 5
