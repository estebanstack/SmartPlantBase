"""
Adaptador de Entrada: Controlador REST para Dispositivos y Sensores ESP32 (R2).
Expone el endpoint POST /api/dispositivos/{id}/lecturas para recibir telemetría ambiental periódica.
Solo rutas: lee la petición con peticion_http.py y llama al puerto RegistrarLecturaPort.
"""
from flask import Blueprint, jsonify

from matera.adaptadores.entrada import peticion_http
from matera.adaptadores.entrada.serializacion import diagnostico_a_json
from matera.adaptadores.entrada.seguridad import VerificadorTokenPort, requiere_dispositivo
from matera.dominio.puertos.entrada import RegistrarLecturaPort


def crear_api_dispositivos_blueprint(
    puerto_registro: RegistrarLecturaPort,
    verificador: VerificadorTokenPort,
) -> Blueprint:
    """
    Fábrica del Blueprint REST para dispositivos IoT / sensores (ESP32).
    """
    api_bp = Blueprint("api_dispositivos", __name__, url_prefix="/api")

    @api_bp.route("/dispositivos/<id>/lecturas", methods=["POST"])
    @requiere_dispositivo(verificador)
    def registrar_lectura(id: str):
        """
        POST /api/dispositivos/{id}/lecturas (R2).
        Recibe la lectura ambiental de un dispositivo ESP32, la pasa a RegistrarLecturaPort
        y retorna el diagnóstico generado. Los límites físicos los valida el dominio.
        """
        datos = peticion_http.cuerpo_json()

        # 1. Cada lectura trae el id del dispositivo, la marca de tiempo y los valores (R2)
        peticion_http.mismo_dispositivo(datos, id)

        # 2. Invocación al puerto de entrada con los valores y la marca de tiempo ya validados
        diagnostico = puerto_registro.registrar(
            dispositivo_id=id,
            valores=peticion_http.valores_medidos(datos),
            marca_tiempo=peticion_http.marca_tiempo(datos),
        )

        # 3. Respuesta 201 Created con diagnóstico calculado
        return jsonify({
            "mensaje": "Lectura registrada correctamente.",
            "dispositivo_id": id,
            "estado": diagnostico.estado.value,
            "diagnostico": diagnostico_a_json(diagnostico),
        }), 201

    return api_bp
