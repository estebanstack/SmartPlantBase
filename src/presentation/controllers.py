"""
Controladores REST (Capa de Presentación).
Valida las peticiones HTTP en el borde del sistema (RA6) y delega a los casos de uso.
Responde estrictamente en formato JSON sin renderizar HTML (RA1).
"""
from typing import Any, Dict
from flask import Blueprint, jsonify, request

from src.application.dtos import DiagnosticoInputDTO
from src.application.use_cases import EvaluarDiagnosticoUseCase, ListarEspeciesUseCase
from src.domain.exceptions import ParametroInvalidoError


def crear_api_blueprint(
    evaluar_use_case: EvaluarDiagnosticoUseCase,
    listar_use_case: ListarEspeciesUseCase,
) -> Blueprint:
    """Fábrica de Blueprint REST con inyección de dependencias de los casos de uso."""
    api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

    @api_bp.route("/diagnosticos", methods=["POST"])
    def evaluar_diagnostico():
        """
        Endpoint POST /api/v1/diagnosticos (Anexo A).
        Valida tipos y obligatoriedad en el borde (RA6) antes de invocar al caso de uso.
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

        datos: Dict[str, Any] = request.get_json(silent=True) or {}

        # 1. Validación de presencia de parámetros obligatorios
        campos_requeridos = ["especie", "humedad", "luz", "temperatura"]
        for campo in campos_requeridos:
            if campo not in datos or datos[campo] is None:
                raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio.")

        # 2. Validación de tipo de la especie
        especie_raw = datos["especie"]
        if not isinstance(especie_raw, str) or not especie_raw.strip():
            raise ParametroInvalidoError("especie", "El parámetro 'especie' debe ser un texto no vacío.")

        # 3. Validación y conversión numérica de mediciones en el borde
        def parse_float(campo: str, valor: Any) -> float:
            if isinstance(valor, bool):  # en Python bool es subclase de int, rechazar True/False
                raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
            try:
                return float(valor)
            except (ValueError, TypeError):
                raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

        humedad = parse_float("humedad", datos["humedad"])
        luz = parse_float("luz", datos["luz"])
        temperatura = parse_float("temperatura", datos["temperatura"])

        # 4. Creación del DTO de entrada tipado (borde del sistema hacia aplicación)
        dto_entrada = DiagnosticoInputDTO(
            especie=especie_raw.strip().lower(),
            humedad=humedad,
            luz=luz,
            temperatura=temperatura,
        )

        # 5. Ejecución del caso de uso
        resultado_dto = evaluar_use_case.ejecutar(dto_entrada)

        return jsonify(resultado_dto.to_dict()), 200

    @api_bp.route("/especies", methods=["GET"])
    def listar_especies():
        """
        Endpoint GET /api/v1/especies (RF5 y Anexo A).
        Retorna la lista de especies soportadas con sus rangos de referencia.
        """
        especies = listar_use_case.ejecutar()
        return jsonify([esp.to_dict() for esp in especies]), 200

    return api_bp
