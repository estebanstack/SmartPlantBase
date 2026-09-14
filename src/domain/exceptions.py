"""
Excepciones de la capa de Dominio.
Independientes de frameworks web o mecanismos de persistencia.
"""


class DominioError(Exception):
    """Excepción base para errores ocurridos en la capa de dominio."""
    pass


class EspecieNoSoportadaError(DominioError):
    """Lanzada cuando una especie solicitada no existe en el catálogo de referencia."""
    def __init__(self, especie: str):
        super().__init__(f"La especie '{especie}' no está registrada en el catálogo de referencia.")
        self.especie = especie


class ParametroInvalidoError(DominioError):
    """Lanzada cuando una medición contiene parámetros inválidos o físicamente imposibles."""
    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje
