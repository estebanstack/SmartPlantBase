"""
Casos de uso del dominio: uno por cada puerto de entrada.
Cada clase recibe por constructor solo los puertos de salida que necesita.
"""
from matera.dominio.casos_uso.autenticar_usuario import AutenticarUsuario
from matera.dominio.casos_uso.consultar_especies import ConsultarEspecies
from matera.dominio.casos_uso.consultar_estado import ConsultarEstado
from matera.dominio.casos_uso.consultar_historial import ConsultarHistorial
from matera.dominio.casos_uso.listar_plantas import ListarPlantas
from matera.dominio.casos_uso.registrar_lectura import RegistrarLectura
from matera.dominio.casos_uso.validar_lectura import ValidarLectura

__all__ = [
    "AutenticarUsuario",
    "ConsultarEspecies",
    "ConsultarEstado",
    "ConsultarHistorial",
    "ListarPlantas",
    "RegistrarLectura",
    "ValidarLectura",
]
