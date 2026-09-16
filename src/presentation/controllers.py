"""
Controladores REST (Capa de Presentación).
Valida las peticiones HTTP en el borde del sistema (RA6) y delega a los casos de uso.
Responde estrictamente en formato JSON, sin renderizar HTML (RA1).
"""
from typing import Any, Dict
from flask import Blueprint, jsonify, request

from src.application.dtos import DiagnosticoInputDTO
from src.application.use_cases import EvaluarDiagnosticoUseCase, ListarEspeciesUseCase
from src.domain.entities import PARAMETROS_SOPORTADOS
from src.domain.exceptions import ParametroInvalidoError


def crear_api_blueprint(
    evaluar_use_case: EvaluarDiagnosticoUseCase,
    listar_use_case: ListarEspeciesUseCase,
) -> Blueprint:
    """Fábrica de Blueprint REST con inyección de dependencias de los casos de uso."""
    api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

    def _parse_float(campo: str, valor: Any) -> float:
        # En Python bool es subclase de int: se rechaza explícitamente True/False.
        if isinstance(valor, bool):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

    @api_bp.route("/diagnosticos", methods=["POST"])
    def evaluar_diagnostico():
        """
        POST /api/v1/diagnosticos (Anexo A).
        Valida presencia y tipo en el borde (RA6) y construye el DTO de entrada.
        Los parámetros exigidos son los que declara el dominio: agregar una
        variable ambiental no modifica este controlador.
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

        datos: Dict[str, Any] = request.get_json(silent=True) or {}

        especie_raw = datos.get("especie")
        if not isinstance(especie_raw, str) or not especie_raw.strip():
            raise ParametroInvalidoError("especie", "El parámetro 'especie' es obligatorio y debe ser un texto no vacío.")

        valores: Dict[str, float] = {}
        for campo in PARAMETROS_SOPORTADOS:
            if campo not in datos or datos[campo] is None:
                raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio.")
            valores[campo] = _parse_float(campo, datos[campo])

        dto_entrada = DiagnosticoInputDTO(
            especie=especie_raw.strip().lower(),
            valores=valores,
        )

        resultado_dto = evaluar_use_case.ejecutar(dto_entrada)
        return jsonify(resultado_dto.to_dict()), 200

    @api_bp.route("/especies", methods=["GET"])
    def listar_especies():
        """
        GET /api/v1/especies (RF5 y Anexo A).
        Retorna la lista de especies soportadas con sus rangos de referencia.
        """
        especies = listar_use_case.ejecutar()
        return jsonify([esp.to_dict() for esp in especies]), 200

    return api_bp
