"""
Adaptador de Entrada: Controlador REST para la Interfaz Web y Consulta de Diagnósticos (R1).
Implementa los endpoints HTTP que conectan a los puertos de entrada ValidarLecturaPort, ConsultarEstadoPort y AutenticarUsuarioPort.
"""
from typing import Any, Dict, Optional
from flask import Blueprint, jsonify, request

from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS
from matera.puertos.entrada import (
    AutenticarUsuarioPort,
    ConsultarEstadoPort,
    ValidarLecturaPort,
)


def crear_api_front_blueprint(
    puerto_validacion: ValidarLecturaPort,
    puerto_consultas: Optional[ConsultarEstadoPort] = None,
    puerto_auth: Optional[AutenticarUsuarioPort] = None,
) -> Blueprint:
    """
    Fábrica del Blueprint REST para clientes web / frontend.
    Conecta las rutas HTTP con los puertos de entrada del hexágono.
    """
    api_bp = Blueprint("api_front", __name__, url_prefix="/api")

    def _parse_float(campo: str, valor: Any) -> float:
        if isinstance(valor, bool):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

    # -------------------------------------------------------------------------
    # R1: Endpoints compatibles con Fase 1 (/api/v1/...)
    # -------------------------------------------------------------------------
    @api_bp.route("/v1/diagnosticos", methods=["POST"])
    def evaluar_diagnostico_v1():
        """
        POST /api/v1/diagnosticos (R1 - Conservar validación de Fase 1).
        Valida tipos y presencia en el adaptador de entrada y delega a ValidarLecturaPort.
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

        diagnostico = puerto_validacion.validar(
            especie=especie_raw.strip().lower(),
            valores=valores,
        )

        respuesta = {
            "especie": diagnostico.especie,
            "estado": diagnostico.estado.value,
            "parametros": [
                {
                    "nombre": p.nombre,
                    "valor": p.valor,
                    "unidad": p.unidad,
                    "rango_optimo": [p.rango_optimo[0], p.rango_optimo[1]],
                    "estado": p.estado.value,
                }
                for p in diagnostico.parametros
            ],
            "recomendaciones": diagnostico.recomendaciones,
        }
        return jsonify(respuesta), 200

    @api_bp.route("/v1/especies", methods=["GET"])
    def listar_especies_v1():
        """
        GET /api/v1/especies (R1).
        Retorna la lista de especies soportadas con sus rangos de referencia.
        """
        especies = puerto_validacion.listar_especies()
        respuesta = [
            {
                "nombre": esp.nombre,
                "rangos": {
                    nombre: {
                        "min": rango.minimo,
                        "max": rango.maximo,
                        "unidad": rango.unidad,
                    }
                    for nombre, rango in esp.rangos.items()
                },
            }
            for esp in especies
        ]
        return jsonify(respuesta), 200

    return api_bp
