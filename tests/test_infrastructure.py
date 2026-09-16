"""
Pruebas de la capa de infraestructura (lectura de la tabla de referencia CSV).
Verifica que el repositorio CSV cargue correctamente la tabla de referencia.
"""
from pathlib import Path
from src.infrastructure.repositories.csv_especie_repository import CsvEspecieRepository


def test_csv_especie_repository_carga_especies_anexo_b():
    ruta_csv = Path(__file__).parent.parent / "data" / "especies_referencia.csv"
    repo = CsvEspecieRepository(ruta_csv)

    especies = repo.obtener_todas()
    assert len(especies) >= 5

    nombres = {e.nombre for e in especies}
    assert "sansevieria" in nombres
    assert "potos" in nombres
    assert "suculenta" in nombres
    assert "helecho" in nombres
    assert "lavanda" in nombres

    sansevieria = repo.obtener_por_nombre("sansevieria")
    assert sansevieria is not None
    assert sansevieria.rango_humedad.minimo == 20.0
    assert sansevieria.rango_humedad.maximo == 45.0
    assert sansevieria.rango_luz.minimo == 200.0
    assert sansevieria.rango_luz.maximo == 1500.0
    assert sansevieria.rango_temperatura.minimo == 15.0
    assert sansevieria.rango_temperatura.maximo == 29.0
