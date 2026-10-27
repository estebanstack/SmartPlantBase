"""
Dobles de prueba en memoria para los Puertos de Salida de Arquitectura Hexagonal.
Permite ejercitar las reglas de negocio, los puertos de entrada y los casos de uso
sin necesidad de archivos, base de datos ni servidor web.
"""
from typing import Dict, List, Optional, Tuple
from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    Lectura,
    Planta,
    RangoParametro,
    RegistroLectura,
    Usuario,
)
from matera.dominio.puertos.salida import (
    EmisorTokenPort,
    HistorialLecturasPort,
    PlantasPort,
    TablaReferenciaPort,
    UsuariosPort,
)


def especie_de_prueba(
    nombre: str,
    humedad: Tuple[float, float],
    luz: Tuple[float, float],
    temperatura: Tuple[float, float],
) -> Especie:
    """Constructor auxiliar para armar especies de prueba."""
    return Especie(
        nombre=nombre,
        rangos={
            "humedad": RangoParametro(minimo=humedad[0], maximo=humedad[1], unidad="%"),
            "luz": RangoParametro(minimo=luz[0], maximo=luz[1], unidad="lux"),
            "temperatura": RangoParametro(minimo=temperatura[0], maximo=temperatura[1], unidad="°C"),
        },
    )


class FakeTablaReferencia(TablaReferenciaPort):
    """Doble en memoria de TablaReferenciaPort."""

    def __init__(self, catalogo: Optional[Dict[str, Especie]] = None):
        self._catalogo = catalogo or {
            "sansevieria": especie_de_prueba("sansevieria", (20.0, 45.0), (200.0, 1500.0), (15.0, 29.0)),
            "helecho": especie_de_prueba("helecho", (60.0, 85.0), (150.0, 800.0), (16.0, 26.0)),
            "suculenta": especie_de_prueba("suculenta", (10.0, 30.0), (1000.0, 5000.0), (18.0, 32.0)),
        }

    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        return self._catalogo.get(nombre.strip().lower())

    def obtener_todas(self) -> List[Especie]:
        return list(self._catalogo.values())


class FakeHistorialLecturas(HistorialLecturasPort):
    """Doble en memoria de HistorialLecturasPort."""

    def __init__(self):
        self.registros: List[RegistroLectura] = []

    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        self.registros.append(RegistroLectura(lectura=lectura, estado=diagnostico.estado))

    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        for registro in reversed(self.registros):
            if registro.lectura.planta_id == planta_id:
                return registro.lectura
        return None

    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[RegistroLectura]:
        filtrados = [r for r in reversed(self.registros) if r.lectura.planta_id == planta_id]
        return filtrados[:limite]


class FakeUsuarios(UsuariosPort):
    """Doble en memoria de UsuariosPort."""

    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}

    def guardar_usuario(self, usuario: Usuario) -> None:
        self.usuarios[usuario.id] = usuario

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        for usuario in self.usuarios.values():
            if usuario.email.lower() == email.lower():
                return usuario
        return None


class FakePlantas(PlantasPort):
    """Doble en memoria de PlantasPort."""

    def __init__(self):
        self.plantas: Dict[str, Planta] = {}

    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        return self.plantas.get(planta_id)

    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        for planta in self.plantas.values():
            if planta.dispositivo_id == dispositivo_id:
                return planta
        return None

    def listar_plantas_por_usuario(self, usuario_id: str) -> List[Planta]:
        return [p for p in self.plantas.values() if p.usuario_id == usuario_id]

    def guardar_planta(self, planta: Planta) -> None:
        self.plantas[planta.id] = planta


class FakeEmisorToken(EmisorTokenPort):
    """Doble en memoria de EmisorTokenPort."""

    def emitir_token_usuario(self, usuario_id: str, email: str) -> str:
        return f"fake-jwt-user-{usuario_id}"

    def emitir_token_dispositivo(self, dispositivo_id: str, planta_id: str) -> str:
        return f"fake-jwt-disp-{dispositivo_id}"
