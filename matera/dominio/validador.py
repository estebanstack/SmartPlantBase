"""
Servicios de Dominio y Validador de Estado Botánico (Núcleo Hexagonal).
Implementa las reglas botánicas de salud y orquesta los casos de uso detrás de los puertos de entrada.
0 dependencias de frameworks externos (POPOs puros).
"""
import hashlib
import uuid
from typing import Any, Dict, List, Mapping, Optional, Tuple

from matera.dominio.excepciones import (
    AccesoNoAutorizadoPlantaError,
    CredencialesInvalidasError,
    DispositivoNoEncontradoError,
    EspecieNoSoportadaError,
    PlantaNoEncontradaError,
    UsuarioYaExisteError,
)
from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    EstadoActualPlanta,
    EstadoParametro,
    EstadoPlanta,
    Lectura,
    ParametroEvaluado,
    Planta,
    RangoParametro,
    Usuario,
)
from matera.dominio.puertos.entrada import (
    AutenticarUsuarioPort,
    ConsultarEstadoPort,
    RegistrarLecturaPort,
    ValidarLecturaPort,
)
from matera.dominio.puertos.salida import (
    EmisorTokenPort,
    HistorialLecturasPort,
    TablaReferenciaPort,
    UsuariosPlantasPort,
)


class ValidadorDeEstado:
    """
    Servicio de dominio puro que evalúa una lectura contra los rangos de referencia de una especie.
    Agnóstico a frameworks, HTTP y mecanismos de almacenamiento.
    """

    _RECOMENDACIONES: Dict[Tuple[str, EstadoParametro], str] = {
        ("humedad", EstadoParametro.BAJO):
            "La humedad del sustrato está por debajo del rango recomendado: riegue moderadamente.",
        ("humedad", EstadoParametro.ALTO):
            "La humedad del sustrato supera el rango recomendado: suspenda el riego y facilite el drenaje.",
        ("luz", EstadoParametro.BAJO):
            "El nivel de luz es insuficiente para esta especie: ubique la planta en un lugar con mayor exposición solar.",
        ("luz", EstadoParametro.ALTO):
            "El nivel de luz es excesivo: proteja la planta con sombra parcial o retírela de la radiación solar directa.",
        ("temperatura", EstadoParametro.BAJO):
            "La temperatura ambiental es demasiado baja: traslade la planta a un espacio más cálido o protegido.",
        ("temperatura", EstadoParametro.ALTO):
            "La temperatura ambiental es excesiva: ventile el espacio o traslade la planta a un lugar fresco.",
    }

    @staticmethod
    def _clasificar_parametro(valor: float, rango: RangoParametro) -> EstadoParametro:
        """
        Clasifica un valor respecto al rango óptimo.
        El rango es cerrado: un valor en los extremos se considera OPTIMO.
        """
        if valor < rango.minimo:
            return EstadoParametro.BAJO
        if valor > rango.maximo:
            return EstadoParametro.ALTO
        return EstadoParametro.OPTIMO

    @classmethod
    def _generar_recomendacion(cls, nombre_parametro: str, estado: EstadoParametro) -> str:
        """Devuelve la recomendación para un parámetro fuera de rango."""
        return cls._RECOMENDACIONES.get(
            (nombre_parametro.lower(), estado),
            f"El parámetro {nombre_parametro} se encuentra en estado {estado.value}, ajuste las condiciones."
        )

    @classmethod
    def evaluar(cls, lectura: Lectura, especie: Especie) -> Diagnostico:
        """
        Evalúa una lectura contra los rangos declarados por la especie.
        Aplica clasificación por variable, derivación de estado global y generación de recomendaciones.
        """
        parametros_evaluados: List[ParametroEvaluado] = []
        recomendaciones: List[str] = []
        desviaciones = 0

        for nombre, rango in especie.rangos.items():
            valor = lectura.valor_de(nombre)
            estado = cls._clasificar_parametro(valor, rango)

            parametros_evaluados.append(
                ParametroEvaluado(
                    nombre=nombre,
                    valor=valor,
                    unidad=rango.unidad,
                    rango_optimo=(rango.minimo, rango.maximo),
                    estado=estado,
                )
            )

            if estado != EstadoParametro.OPTIMO:
                desviaciones += 1
                recomendaciones.append(cls._generar_recomendacion(nombre, estado))

        return Diagnostico(
            especie=especie.nombre,
            estado=cls._derivar_estado_global(desviaciones),
            parametros=parametros_evaluados,
            recomendaciones=recomendaciones,
        )

    @staticmethod
    def _derivar_estado_global(desviaciones: int) -> EstadoPlanta:
        """
        Regla de agregación del estado global:
        - 0 desviaciones -> SALUDABLE.
        - 1 desviación -> EN_RIESGO.
        - 2 o más desviaciones -> CRITICO.
        """
        if desviaciones == 0:
            return EstadoPlanta.SALUDABLE
        if desviaciones == 1:
            return EstadoPlanta.EN_RIESGO
        return EstadoPlanta.CRITICO


class ServicioMateraDominio(
    ValidarLecturaPort,
    RegistrarLecturaPort,
    ConsultarEstadoPort,
    AutenticarUsuarioPort,
):
    """
    Orquestador de Casos de Uso del Núcleo Hexagonal.
    Implementa todos los puertos de entrada coordinando las reglas de dominio
    con los puertos de salida requeridos.
    """

    def __init__(
        self,
        tabla_referencia: TablaReferenciaPort,
        historial_lecturas: Optional[HistorialLecturasPort] = None,
        usuarios_plantas: Optional[UsuariosPlantasPort] = None,
        emisor_token: Optional[EmisorTokenPort] = None,
    ):
        self._tabla_referencia = tabla_referencia
        self._historial_lecturas = historial_lecturas
        self._usuarios_plantas = usuarios_plantas
        self._emisor_token = emisor_token

    # -------------------------------------------------------------------------
    # R1: ValidarLecturaPort
    # -------------------------------------------------------------------------
    def validar(self, especie: str, valores: Mapping[str, float]) -> Diagnostico:
        lectura = Lectura(especie=especie, valores=valores)
        especie_entidad = self._tabla_referencia.obtener_por_nombre(lectura.especie)
        if not especie_entidad:
            raise EspecieNoSoportadaError(lectura.especie)
        return ValidadorDeEstado.evaluar(lectura, especie_entidad)

    def listar_especies(self) -> List[Especie]:
        return self._tabla_referencia.obtener_todas()

    # -------------------------------------------------------------------------
    # R2 y R5: RegistrarLecturaPort
    # -------------------------------------------------------------------------
    def registrar(
        self,
        dispositivo_id: str,
        valores: Mapping[str, float],
        marca_tiempo: str = "",
    ) -> Diagnostico:
        if not self._usuarios_plantas:
            raise RuntimeError("UsuariosPlantasPort no configurado.")

        planta = self._usuarios_plantas.obtener_planta_por_dispositivo(dispositivo_id)
        if not planta:
            raise DispositivoNoEncontradoError(dispositivo_id)

        lectura = Lectura(
            especie=planta.especie,
            valores=valores,
            marca_tiempo=marca_tiempo,
            dispositivo_id=dispositivo_id,
            planta_id=planta.id,
        )

        especie_entidad = self._tabla_referencia.obtener_por_nombre(planta.especie)
        if not especie_entidad:
            raise EspecieNoSoportadaError(planta.especie)

        diagnostico = ValidadorDeEstado.evaluar(lectura, especie_entidad)

        if self._historial_lecturas:
            self._historial_lecturas.guardar_lectura(lectura, diagnostico)

        return diagnostico

    # -------------------------------------------------------------------------
    # R5, R6 y R7: ConsultarEstadoPort
    # -------------------------------------------------------------------------
    def consultar_estado(self, usuario_id: str, planta_id: str) -> EstadoActualPlanta:
        if not self._usuarios_plantas:
            raise RuntimeError("UsuariosPlantasPort no configurado.")

        planta = self._usuarios_plantas.obtener_planta_por_id(planta_id)
        if not planta:
            raise PlantaNoEncontradaError(planta_id)

        # Regla de propiedad en el dominio (R7)
        if not planta.pertenece_a(usuario_id):
            raise AccesoNoAutorizadoPlantaError(usuario_id, planta_id)

        ultima_lectura = (
            self._historial_lecturas.obtener_ultima_lectura(planta_id)
            if self._historial_lecturas
            else None
        )

        diagnostico = None
        if ultima_lectura:
            especie_entidad = self._tabla_referencia.obtener_por_nombre(planta.especie)
            if especie_entidad:
                diagnostico = ValidadorDeEstado.evaluar(ultima_lectura, especie_entidad)

        return EstadoActualPlanta(
            planta=planta,
            ultima_lectura=ultima_lectura,
            diagnostico=diagnostico,
        )

    def consultar_historial(
        self, usuario_id: str, planta_id: str, limite: int = 20
    ) -> List[Any]:
        if not self._usuarios_plantas:
            raise RuntimeError("UsuariosPlantasPort no configurado.")

        planta = self._usuarios_plantas.obtener_planta_por_id(planta_id)
        if not planta:
            raise PlantaNoEncontradaError(planta_id)

        if not planta.pertenece_a(usuario_id):
            raise AccesoNoAutorizadoPlantaError(usuario_id, planta_id)

        if not self._historial_lecturas:
            return []

        return self._historial_lecturas.obtener_historial(planta_id, limite)

    def listar_plantas_usuario(self, usuario_id: str) -> List[Planta]:
        if not self._usuarios_plantas:
            return []
        return self._usuarios_plantas.listar_plantas_por_usuario(usuario_id)

    # -------------------------------------------------------------------------
    # R7: AutenticarUsuarioPort
    # -------------------------------------------------------------------------
    def registrar_usuario(self, nombre: str, email: str, password: str) -> Dict[str, Any]:
        if not self._usuarios_plantas:
            raise RuntimeError("UsuariosPlantasPort no configurado.")

        email_clean = email.strip().lower()
        if self._usuarios_plantas.obtener_usuario_por_email(email_clean):
            raise UsuarioYaExisteError(email_clean)

        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        usuario_id = f"usr-{uuid.uuid4().hex[:8]}"
        usuario = Usuario(
            id=usuario_id,
            nombre=nombre.strip(),
            email=email_clean,
            password_hash=password_hash,
        )
        self._usuarios_plantas.guardar_usuario(usuario)

        token = (
            self._emisor_token.emitir_token_usuario(usuario.id, usuario.email)
            if self._emisor_token
            else ""
        )

        return {
            "token": token,
            "usuario_id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
        }

    def iniciar_sesion(self, email: str, password: str) -> Dict[str, Any]:
        if not self._usuarios_plantas:
            raise RuntimeError("UsuariosPlantasPort no configurado.")

        email_clean = email.strip().lower()
        usuario = self._usuarios_plantas.obtener_usuario_por_email(email_clean)
        if not usuario:
            raise CredencialesInvalidasError()

        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if usuario.password_hash != password_hash:
            raise CredencialesInvalidasError()

        token = (
            self._emisor_token.emitir_token_usuario(usuario.id, usuario.email)
            if self._emisor_token
            else ""
        )

        return {
            "token": token,
            "usuario_id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
        }
