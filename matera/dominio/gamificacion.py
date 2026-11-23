"""
Subdominio de gamificación: Matera-Gotchi (docs/propuesta_gamificacion_tamagotchi.md).
La planta tiene un estado de ánimo (según su diagnóstico y si la acaban de regar) y un perfil
con XP, nivel y racha. Python puro: sin Flask, sin SQLite, sin reloj propio. El ValidadorDeEstado
no se toca; este módulo solo lee su Diagnostico.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple

from matera.dominio.modelo import Diagnostico, EstadoParametro, EstadoPlanta, Lectura

# --- Reglas (valores de la propuesta, sección 2) -------------------------------------------------
SALTO_HUMEDAD_RIEGO = 15.0                 # puntos de humedad que debe subir entre dos lecturas
VENTANA_RIEGO = timedelta(minutes=5)       # ...y en menos de este tiempo
RACHA_PARA_RADIANTE = 3                    # días de racha para pasar de CONTENTA a RADIANTE
DURACION_RACHA = timedelta(hours=24)

# XP mínima para entrar a cada nivel (1 a 5) y su nombre
XP_MINIMA_NIVEL: Tuple[int, ...] = (0, 151, 451, 1001, 2001)
NOMBRES_NIVEL: Tuple[str, ...] = (
    "Semilla", "Plántula", "Planta Joven", "Planta Florecida", "Guardián Botánico",
)


class EstadoAnimico(str, Enum):
    RADIANTE = "RADIANTE"
    CONTENTA = "CONTENTA"
    SEDIENTA = "SEDIENTA"
    AHOGADA = "AHOGADA"
    SOFOCADA = "SOFOCADA"
    CONGELADA = "CONGELADA"
    AGRADECIDA = "AGRADECIDA"
    MARCHITA = "MARCHITA"


@dataclass(frozen=True)
class Expresion:
    """Cómo se ve y qué dice la planta en cada estado. La cara es ASCII corto para la pantalla OLED."""
    emoji: str
    cara: str
    mensaje: str
    xp: int  # XP que suma (o resta) cada lectura en este estado


EXPRESIONES: Mapping[EstadoAnimico, Expresion] = {
    EstadoAnimico.RADIANTE: Expresion(
        "🌸✨", "(^o^)", "¡Estoy en mi mejor momento! El sol y el agua están perfectos.", 25),
    EstadoAnimico.CONTENTA: Expresion(
        "🌿😊", "(^_^)", "Me siento muy bien. Gracias por cuidar de mí con constancia.", 10),
    EstadoAnimico.SEDIENTA: Expresion(
        "💧🥺", "(;_;)", "Tengo sed; mi tierra está bastante seca. ¿Me das un poco de agua?", -5),
    EstadoAnimico.AHOGADA: Expresion(
        "🌊🤢", "(@_@)", "¡Mucha agua! Mis raíces se están asfixiando, déjame secar un poco.", -10),
    EstadoAnimico.SOFOCADA: Expresion(
        "☀️🥵", "(>_<)", "Hace demasiado calor aquí. ¿Podrías ubicarme en un lugar fresco?", -10),
    EstadoAnimico.CONGELADA: Expresion(
        "❄️🥶", "(-.-)", "¡Qué frío! Mis hojas se están entumeciendo, protégeme del viento.", -10),
    EstadoAnimico.AGRADECIDA: Expresion(
        "💚🥰", "\\(^o^)/", "¡Agua fresca! Justo lo que necesitaba para revivir. ¡Muchas gracias!", 50),
    EstadoAnimico.MARCHITA: Expresion(
        "🥀💀", "(x_x)", "Mis hojas están decaídas y débiles... Necesito atención urgente.", -30),
}


@dataclass(frozen=True)
class PerfilGamificacion:
    """Progreso acumulado de una planta. El nivel no se guarda: se calcula desde la XP."""
    planta_id: str
    xp_total: int = 0
    racha_dias: int = 0
    racha_desde: Optional[str] = None      # marca de tiempo (ISO-8601) en que empezó la racha actual
    ultimo_animo: EstadoAnimico = EstadoAnimico.CONTENTA
    ultima_actualizacion: str = ""

    @property
    def nivel(self) -> int:
        return sum(1 for minimo in XP_MINIMA_NIVEL if self.xp_total >= minimo)

    @property
    def expresion(self) -> Expresion:
        return EXPRESIONES[self.ultimo_animo]

    def como_dict(self, compacto: bool = False) -> Dict[str, Any]:
        """
        Vista del gotchi para el JSON. Compacto = lo mínimo que necesita el ESP32 (cabe en su RAM);
        completo = lo que pinta el panel web (emoji, barra de nivel, racha).
        """
        exp = self.expresion
        datos: Dict[str, Any] = {
            "estado": self.ultimo_animo.value,
            "cara": exp.cara,
            "mensaje": exp.mensaje,
            "nivel": self.nivel,
            "xp": self.xp_total,
        }
        if compacto:
            return datos
        siguiente = XP_MINIMA_NIVEL[self.nivel] if self.nivel < len(XP_MINIMA_NIVEL) else None
        datos.update({
            "emoji": exp.emoji,
            "nivel_nombre": NOMBRES_NIVEL[self.nivel - 1],
            "xp_nivel_actual": XP_MINIMA_NIVEL[self.nivel - 1],
            "xp_siguiente_nivel": siguiente,   # None en el nivel máximo
            "racha_dias": self.racha_dias,
        })
        return datos


@dataclass(frozen=True)
class ResultadoLectura:
    """Lo que devuelve registrar una lectura: el diagnóstico y, si la gamificación funcionó, el perfil."""
    diagnostico: Diagnostico
    gotchi: Optional[PerfilGamificacion] = None


def _a_fecha(marca_tiempo: str) -> datetime:
    momento = datetime.fromisoformat(marca_tiempo.replace("Z", "+00:00"))
    return momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)


def detectar_riego(lectura: Lectura, anterior: Optional[Lectura]) -> bool:
    """Riego = la humedad subió más de 15 puntos respecto a la lectura anterior, en menos de 5 minutos."""
    if anterior is None or "humedad" not in lectura.valores or "humedad" not in anterior.valores:
        return False
    try:
        pasado = _a_fecha(lectura.marca_tiempo) - _a_fecha(anterior.marca_tiempo)
    except ValueError:
        return False
    salto = lectura.valores["humedad"] - anterior.valores["humedad"]
    return timedelta(0) <= pasado <= VENTANA_RIEGO and salto > SALTO_HUMEDAD_RIEGO


def _elegir_estado(diagnostico: Diagnostico, riego: bool, racha_dias: int) -> EstadoAnimico:
    """Prioridad: riego, estado crítico, problemas de humedad, de clima, y por último contenta/radiante."""
    if riego:
        return EstadoAnimico.AGRADECIDA
    if diagnostico.estado == EstadoPlanta.CRITICO:
        return EstadoAnimico.MARCHITA
    estados = {p.nombre: p.estado for p in diagnostico.parametros}
    if estados.get("humedad") == EstadoParametro.BAJO:
        return EstadoAnimico.SEDIENTA
    if estados.get("humedad") == EstadoParametro.ALTO:
        return EstadoAnimico.AHOGADA
    if EstadoParametro.ALTO in (estados.get("temperatura"), estados.get("luz")):
        return EstadoAnimico.SOFOCADA
    if estados.get("temperatura") == EstadoParametro.BAJO:
        return EstadoAnimico.CONGELADA
    return EstadoAnimico.RADIANTE if racha_dias >= RACHA_PARA_RADIANTE else EstadoAnimico.CONTENTA


class MotorGamificacion:
    """Reglas puras: mismos datos de entrada, mismo resultado. No guarda nada ni lee el reloj."""

    @staticmethod
    def evaluar(
        perfil: PerfilGamificacion,
        diagnostico: Diagnostico,
        lectura: Lectura,
        lectura_anterior: Optional[Lectura] = None,
    ) -> PerfilGamificacion:
        """Devuelve el perfil nuevo; su `ultimo_animo` es el estado de ánimo de esta lectura."""
        ahora = _a_fecha(lectura.marca_tiempo)

        # Racha: +1 por cada 24 h seguidas en SALUDABLE; un estado CRITICO la reinicia.
        # En riesgo no suma ni reinicia (nivel 4 en la propuesta tolera un descuido leve).
        racha_desde, racha_dias = perfil.racha_desde, perfil.racha_dias
        if diagnostico.estado == EstadoPlanta.CRITICO:
            racha_desde, racha_dias = None, 0
        elif diagnostico.estado == EstadoPlanta.SALUDABLE:
            racha_desde = racha_desde or lectura.marca_tiempo
            racha_dias = max(0, int((ahora - _a_fecha(racha_desde)) / DURACION_RACHA))

        estado = _elegir_estado(diagnostico, detectar_riego(lectura, lectura_anterior), racha_dias)
        return replace(
            perfil,
            xp_total=max(0, perfil.xp_total + EXPRESIONES[estado].xp),  # la XP nunca baja de 0
            racha_dias=racha_dias,
            racha_desde=racha_desde,
            ultimo_animo=estado,
            ultima_actualizacion=lectura.marca_tiempo,
        )
