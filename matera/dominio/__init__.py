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
    PARAMETROS_AMBIENTALES,
    PARAMETROS_SOPORTADOS,
    Diagnostico,
    Especie,
    EstadoActualPlanta,
    EstadoParametro,
    EstadoPlanta,
    Lectura,
    ParametroAmbiental,
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
    "ParametroAmbiental",
    "PARAMETROS_AMBIENTALES",
    "PARAMETROS_SOPORTADOS",
    "RangoParametro",
    "Especie",
    "Lectura",
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
