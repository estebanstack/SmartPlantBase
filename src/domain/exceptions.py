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


class SesionQRError(DominioError):
    """Excepción base para errores de sesiones QR."""
    pass


class SesionQRNoEncontradaError(SesionQRError):
    """Lanzada cuando la sesión QR solicitada no existe."""
    def __init__(self, sesion_id: str):
        super().__init__(f"No se encontró la sesión QR '{sesion_id}'.")
        self.sesion_id = sesion_id


class SesionQRInvalidaError(SesionQRError):
    """Lanzada cuando una sesión QR está en un estado no permitido (expirada o ya utilizada)."""
    pass

