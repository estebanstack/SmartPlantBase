"""
Pruebas unitarias de la capa de Aplicación.
Verifica la orquestación de casos de uso usando dobles de prueba.
"""
import pytest
from src.application.dtos import DiagnosticoInputDTO
from src.application.use_cases import EvaluarDiagnosticoUseCase, ListarEspeciesUseCase
from src.domain.exceptions import EspecieNoSoportadaError
from tests.doubles import FakeEspecieRepository


def test_evaluar_diagnostico_use_case_exitoso():
    fake_repo = FakeEspecieRepository()
    use_case = EvaluarDiagnosticoUseCase(fake_repo)

    dto_in = DiagnosticoInputDTO(
        especie="sansevieria",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
    )
    resultado = use_case.ejecutar(dto_in)

    assert resultado.especie == "sansevieria"
    assert resultado.estado == "SALUDABLE"
    assert len(resultado.parametros) == 3
    dict_res = resultado.to_dict()
    assert dict_res["estado"] == "SALUDABLE"


def test_evaluar_diagnostico_use_case_especie_no_soportada():
    fake_repo = FakeEspecieRepository()
    use_case = EvaluarDiagnosticoUseCase(fake_repo)

    dto_in = DiagnosticoInputDTO(
        especie="bonsai_inexistente",
        valores={"humedad": 30.0, "luz": 500.0, "temperatura": 22.0},
    )
    with pytest.raises(EspecieNoSoportadaError):
        use_case.ejecutar(dto_in)


def test_listar_especies_use_case():
    fake_repo = FakeEspecieRepository()
    use_case = ListarEspeciesUseCase(fake_repo)

    lista = use_case.ejecutar()
    assert len(lista) == 2
    nombres = [item.nombre for item in lista]
    assert "sansevieria" in nombres
    assert "helecho" in nombres
    dict_item = lista[0].to_dict()
    assert "rangos" in dict_item
    assert "humedad" in dict_item["rangos"]
