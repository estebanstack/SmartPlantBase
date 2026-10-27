"""
Núcleo de Dominio de la Matera Inteligente.
Contiene las entidades, objetos de valor, reglas botánicas y excepciones de negocio puras.
0 dependencias externas o de infraestructura.
"""
from matera.dominio.excepciones import (
    AccesoNoAutorizadoPlantaError,
    CredencialesInvalidasError,
    DispositivoNoEncontradoError,
    DispositivoYaVinculadoError,
    DominioError,
    EspecieNoSoportadaError,
    ParametroInvalidoError,
    PlantaNoEncontradaError,
    UsuarioYaExisteError,
)
from matera.dominio.modelo import (
    LIMITES_FISICOS,
    PARAMETROS_SOPORTADOS,
    Diagnostico,
    Especie,
    EstadoActualPlanta,
    EstadoParametro,
    EstadoPlanta,
    Lectura,
    LimiteFisico,
    Medicion,
    ParametroEvaluado,
    Planta,
    PlantaRegistrada,
    RangoParametro,
    RegistroLectura,
    SesionUsuario,
    Usuario,
)
from matera.dominio.validador import ValidadorDeEstado

__all__ = [
    "DominioError",
    "EspecieNoSoportadaError",
    "ParametroInvalidoError",
    "PlantaNoEncontradaError",
    "DispositivoNoEncontradoError",
    "DispositivoYaVinculadoError",
    "AccesoNoAutorizadoPlantaError",
    "UsuarioYaExisteError",
    "CredencialesInvalidasError",
    "EstadoParametro",
    "EstadoPlanta",
    "LimiteFisico",
    "LIMITES_FISICOS",
    "PARAMETROS_SOPORTADOS",
    "RangoParametro",
    "Especie",
    "Lectura",
    "Medicion",
    "ParametroEvaluado",
    "Diagnostico",
    "Planta",
    "PlantaRegistrada",
    "Usuario",
    "EstadoActualPlanta",
    "RegistroLectura",
    "SesionUsuario",
    "ValidadorDeEstado",
]
