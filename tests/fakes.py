"""
Dobles de prueba en memoria para los Puertos de Salida de Arquitectura Hexagonal.
Permite ejercitar las reglas de negocio, los puertos de entrada y los casos de uso
sin necesidad de archivos, base de datos ni servidor web.
"""
from typing import Any, Dict, List, Optional, Tuple
from matera.dominio.modelo import (
    Diagnostico,
    Especie,
    Lectura,
    Planta,
    RangoParametro,
    Usuario,
)
from matera.dominio.puertos.salida import (
    EmisorTokenPort,
    HistorialLecturasPort,
    TablaReferenciaPort,
    UsuariosPlantasPort,
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
        self.registros: List[Dict[str, Any]] = []

    def guardar_lectura(self, lectura: Lectura, diagnostico: Diagnostico) -> None:
        self.registros.append({
            "lectura": lectura,
            "diagnostico": diagnostico,
            "planta_id": lectura.planta_id or "",
            "marca_tiempo": lectura.marca_tiempo,
        })

    def obtener_ultima_lectura(self, planta_id: str) -> Optional[Lectura]:
        for reg in reversed(self.registros):
            if reg["planta_id"] == planta_id:
                return reg["lectura"]
        return None

    def obtener_historial(self, planta_id: str, limite: int = 20) -> List[Any]:
        filtrados = [reg for reg in reversed(self.registros) if reg["planta_id"] == planta_id]
        return filtrados[:limite]


class FakeUsuariosPlantas(UsuariosPlantasPort):
    """Doble en memoria de UsuariosPlantasPort."""

    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}
        self.plantas: Dict[str, Planta] = {}

    def guardar_usuario(self, usuario: Usuario) -> None:
        self.usuarios[usuario.id] = usuario

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        for u in self.usuarios.values():
            if u.email.lower() == email.lower():
                return u
        return None

    def obtener_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        return self.usuarios.get(usuario_id)

    def obtener_planta_por_id(self, planta_id: str) -> Optional[Planta]:
        return self.plantas.get(planta_id)

    def obtener_planta_por_dispositivo(self, dispositivo_id: str) -> Optional[Planta]:
        for p in self.plantas.values():
            if p.dispositivo_id == dispositivo_id:
                return p
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
