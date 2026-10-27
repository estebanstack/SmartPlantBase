"""
Adaptador de Entrada: Controlador REST para Dispositivos y Sensores ESP32 (R2).
Expone el endpoint POST /api/dispositivos/{id}/lecturas para recibir telemetría ambiental periódica.
Se conecta exclusivamente al puerto de entrada RegistrarLecturaPort sin tocar el dominio.
"""
from datetime import datetime
from typing import Any, Dict
from flask import Blueprint, jsonify, request

from matera.adaptadores.entrada.serializacion import diagnostico_a_json
from matera.adaptadores.entrada.seguridad import VerificadorTokenPort, requiere_dispositivo
from matera.dominio.excepciones import ParametroInvalidoError
from matera.dominio.modelo import PARAMETROS_SOPORTADOS
from matera.dominio.puertos.entrada import RegistrarLecturaPort


def crear_api_dispositivos_blueprint(
    puerto_registro: RegistrarLecturaPort,
    verificador: VerificadorTokenPort,
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

    def _parse_marca_tiempo(valor: Any) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroInvalidoError("marca_tiempo", "La lectura debe traer su marca_tiempo (ISO-8601).")
        try:
            # Python < 3.11 no acepta la "Z" final, por eso se cambia por +00:00 solo para validar
            datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
        except ValueError:
            raise ParametroInvalidoError(
                "marca_tiempo", f"La marca_tiempo '{valor}' no está en formato ISO-8601."
            )
        return valor.strip()

    @api_bp.route("/dispositivos/<id>/lecturas", methods=["POST"])
    @requiere_dispositivo(verificador)
    def registrar_lectura(id: str):
        """
        POST /api/dispositivos/{id}/lecturas (R2).
        Recibe la lectura ambiental de un dispositivo ESP32, valida los tipos y límites
        a través de RegistrarLecturaPort y retorna el diagnóstico generado.
        """
        if not request.is_json:
            raise ParametroInvalidoError("body", "El cuerpo de la solicitud debe ser un objeto JSON.")

        datos: Dict[str, Any] = request.get_json(silent=True) or {}

        # 1. Cada lectura trae el id del dispositivo, la marca de tiempo y los valores (R2)
        dispositivo_cuerpo = datos.get("dispositivo_id")
        if dispositivo_cuerpo is not None and dispositivo_cuerpo != id:
            raise ParametroInvalidoError(
                "dispositivo_id", "El dispositivo_id del cuerpo no coincide con el de la URL."
            )

        valores: Dict[str, float] = {}
        for campo in PARAMETROS_SOPORTADOS:
            if campo not in datos or datos[campo] is None:
                raise ParametroInvalidoError(campo, f"El parámetro '{campo}' es obligatorio en la lectura.")
            valores[campo] = _parse_float(campo, datos[campo])

        # 2. Marca de tiempo obligatoria y en formato ISO-8601 (ej. 2026-10-27T15:00:00Z)
        marca_tiempo = _parse_marca_tiempo(datos.get("marca_tiempo"))

        # 3. Invocación al puerto de entrada
        diagnostico = puerto_registro.registrar(
            dispositivo_id=id,
            valores=valores,
            marca_tiempo=marca_tiempo,
        )

        # 4. Respuesta 201 Created con diagnóstico calculado
        return jsonify({
            "mensaje": "Lectura registrada correctamente.",
            "dispositivo_id": id,
            "estado": diagnostico.estado.value,
            "diagnostico": diagnostico_a_json(diagnostico),
        }), 201

    return api_bp
