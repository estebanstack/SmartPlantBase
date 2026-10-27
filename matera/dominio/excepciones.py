"""
Excepciones de la capa de Dominio (Núcleo Hexagonal).
POPOs puros sin dependencias de frameworks web, bases de datos o librerías de infraestructura.
"""


class DominioError(Exception):
    """Excepción base para todos los errores de dominio."""
    pass


class EspecieNoSoportadaError(DominioError):
    """Lanzada cuando una especie no existe en el catálogo de referencia."""
    def __init__(self, especie: str):
        super().__init__(f"La especie '{especie}' no está registrada en el catálogo de referencia.")
        self.especie = especie


class ParametroInvalidoError(DominioError):
    """Lanzada cuando una lectura o dato contiene parámetros inválidos o físicamente imposibles."""
    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje


class PlantaNoEncontradaError(DominioError):
    """Lanzada cuando no se encuentra la planta solicitada."""
    def __init__(self, planta_id: str):
        super().__init__(f"La planta con identificador '{planta_id}' no fue encontrada.")
        self.planta_id = planta_id


class DispositivoNoEncontradoError(DominioError):
    """Lanzada cuando un dispositivo que intenta reportar no está vinculado a ninguna planta."""
    def __init__(self, dispositivo_id: str):
        super().__init__(f"El dispositivo '{dispositivo_id}' no está registrado o no tiene una planta asociada.")
        self.dispositivo_id = dispositivo_id


class AccesoNoAutorizadoPlantaError(DominioError):
    """Lanzada cuando un usuario intenta consultar o modificar una planta que no le pertenece."""
    def __init__(self, usuario_id: str, planta_id: str):
        super().__init__(f"El usuario '{usuario_id}' no tiene autorización para acceder a la planta '{planta_id}'.")
        self.usuario_id = usuario_id
        self.planta_id = planta_id


class UsuarioYaExisteError(DominioError):
    """Lanzada al intentar registrar un usuario con un correo ya existente."""
    def __init__(self, email: str):
        super().__init__(f"El usuario con correo '{email}' ya se encuentra registrado.")
        self.email = email


class CredencialesInvalidasError(DominioError):
    """Lanzada cuando las credenciales de inicio de sesión no coinciden."""
    def __init__(self, mensaje: str = "Credenciales de acceso inválidas."):
        super().__init__(mensaje)
        self.mensaje = mensaje


class DispositivoYaVinculadoError(DominioError):
    """Lanzada al registrar una planta con un dispositivo que ya está asociado a otra planta."""
    def __init__(self, dispositivo_id: str):
        super().__init__(f"El dispositivo '{dispositivo_id}' ya está vinculado a otra planta.")
        self.dispositivo_id = dispositivo_id
