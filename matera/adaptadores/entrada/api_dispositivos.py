"""
Adaptador de Entrada: Controlador REST para Dispositivos y Sensores ESP32 (R2).
Expone el endpoint POST /api/dispositivos/{id}/lecturas para recibir telemetría ambiental periódica.
Se conecta exclusivamente al puerto de entrada RegistrarLecturaPort sin tocar el dominio.
"""
from typing import Any, Dict, Optional
from flask import Blueprint, jsonify, request

from matera.adaptadores.entrada.serializacion import diagnostico_a_json
from matera.adaptadores.entrada.seguridad_jwt import requiere_jwt_dispositivo
from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS
from matera.dominio.puertos.entrada import RegistrarLecturaPort


def crear_api_dispositivos_blueprint(
    puerto_registro: RegistrarLecturaPort,
    emisor_jwt: Optional[JwtEmisorTokenAdapter] = None,
) -> Blueprint:
    """
    Fábrica del Blueprint REST para dispositivos IoT / sensores (ESP32).
    """
    api_bp = Blueprint("api_dispositivos", __name__, url_prefix="/api")

    def _parse_float(campo: str, valor: Any) -> float:
        if isinstance(valor, bool):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise ParametroInvalidoError(campo, f"El valor de '{campo}' no es un número válido.")

    def _verificador_dispositivo(f):
        if emisor_jwt:
            return requiere_jwt_dispositivo(emisor_jwt)(f)
        return f

    @api_bp.route("/dispositivos/<id>/lecturas", methods=["POST"])
    @_verificador_dispositivo
    def registrar_lectura(id: str):
        """
        POST /api/dispositivos/{id}/lecturas (R2).
        Recibe la lectura ambiental de un dispositivo ESP32, valida los tipos y límites
        a través de RegistrarLecturaPort y retorna el diagnóstico generado.
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")

        datos: Dict[str, Any] = request.get_json(silent=True) or {}

        # 1. Parseo y verificación de campos obligatorios
        valores: Dict[str, float] = {}
        for campo in PARAMETROS_SOPORTADOS:
            if campo not in datos or datos[campo] is None:
                raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio en la lectura.")
            valores[campo] = _parse_float(campo, datos[campo])

        # 2. Marca de tiempo suministrada o inferida
        marca_tiempo = datos.get("marca_tiempo") or datos.get("timestamp") or ""

        # 3. Invocación al puerto de entrada
        diagnostico = puerto_registro.registrar(
            dispositivo_id=id,
            valores=valores,
            marca_tiempo=str(marca_tiempo),
        )

        # 4. Respuesta 201 Created con diagnóstico calculado
        return jsonify({
            "mensaje": "Lectura registrada correctamente.",
            "dispositivo_id": id,
            "estado": diagnostico.estado.value,
            "diagnostico": diagnostico_a_json(diagnostico),
        }), 201

    return api_bp
