# SmartPlantBase · Matera Inteligente (Fase 2: Arquitectura Hexagonal)
**Universidad Sergio Arboleda · Arquitectura de Software · Semestre 2026-3**  
**Entrega 2:** Del sensor al dominio: puertos y adaptadores  
**Framework y Lenguaje:** Python 3.14 / Flask / SQLite / PyJWT / pytest  

---

## 1. Resumen de la Arquitectura Hexagonal

SmartPlantBase implementa el patrón **Puertos y Adaptadores (Alistair Cockburn, 2005)**:
- **Núcleo de Dominio (`matera/dominio/`):** Entidades (`Lectura`, `Especie`, `Planta`, `Usuario`, `Diagnostico`), reglas botánicas (`ValidadorDeEstado`) y excepciones puras. **0 dependencias de frameworks, HTTP, bases de datos o librerías de seguridad.**
- **Puertos de Entrada (`matera/puertos/entrada.py`):** Casos de uso definidos mediante interfaces abstractas (`ValidarLecturaPort`, `RegistrarLecturaPort`, `ConsultarEstadoPort`, `AutenticarUsuarioPort`).
- **Puertos de Salida (`matera/puertos/salida.py`):** Contratos abstractos requeridos por el dominio (`TablaReferenciaPort`, `HistorialLecturasPort`, `UsuariosPlantasPort`, `EmisorTokenPort`).
- **Adaptadores de Entrada (`matera/adaptadores/entrada/`):**
  - `api_front.py`: Controlador REST para clientes web y autenticación.
  - `api_dispositivos.py`: Controlador REST para sensores IoT (`POST /api/dispositivos/{id}/lecturas`).
  - `seguridad_jwt.py`: Decoradores que verifican firma, alcance (`scope: usuario` vs `dispositivo`) y entregan identidades limpias al caso de uso.
- **Adaptadores de Salida (`matera/adaptadores/salida/`):**
  - `tabla_csv.py`: Lector de referencia botánica desde CSV (`CsvTablaReferenciaAdapter`).
  - `tabla_bd.py`: Lector de referencia botánica desde SQLite (`BdTablaReferenciaAdapter`).
  - `historial_bd.py`: Persistencia de lecturas, usuarios y plantas en SQLite (`BdHistorialYPlantasAdapter`).
  - `emisor_jwt.py`: Emisión de tokens con `PyJWT` (`JwtEmisorTokenAdapter`).
- **Punto Único de Composición (`matera/app.py`):** Instancia adaptadores, resuelve dependencias y ensambla la aplicación.

---

## 2. Requisitos y Configuración Rápida

1. **Clonar repositorio y activar entorno virtual:**
   ```bash
   cd SmartPlantBase
   source ../venv/bin/activate    # o python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ejecutar la suite completa de pruebas:**
   ```bash
   pytest
   ```
   *Ejecuta 66 pruebas unitarias y de integración en menos de 0.3 segundos con 100% de éxito.*

---

## 3. Demostración en Vivo para Sustentación Oral (4 Pasos)

La base de datos SQLite autogenera datos semilla para demostrar de inmediato en clase:
- **Usuario 1 (Principal):** `ana@matera.edu.co` / `clave123` (`usr-ana`), dueña de `planta-01` (Sansevieria, vinculada a `esp32-01`).
- **Usuario 2 (Ajeno):** `carlos@matera.edu.co` / `clave123` (`usr-carlos`), dueño de `planta-02` (Helecho, vinculado a `esp32-02`).

### Demostración 1: Simulador ESP32 enviando lecturas y Front actualizándose solo (R2, R3, R5, R6)
1. **Terminal 1 (Backend):**
   ```bash
   python app.py
   ```
2. **Terminal 2 (Frontend Web):**
   ```bash
   python3 -m http.server 8000 --directory frontend/
   ```
   Abre en el navegador: `http://localhost:8000`.  
   Haz clic en **"👤 Entrar como Ana"**. Observarás el panel de telemetría en vivo con polling automático cada 3 segundos.
3. **Terminal 3 (Simulador ESP32):**
   ```bash
   python simulador_esp32.py --intervalo 2
   ```
   Observa cómo el frontend refleja en tiempo real las lecturas saludables (`SALUDABLE`), las alertas de sequía/calor (`EN_RIESGO` / `CRITICO`) y cómo los datos corruptos son rechazados con `400 Bad Request` sin detener el sistema.

### Demostración 2: Conmutación de CSV a Base de Datos por configuración (R4)
Reinicia el backend cambiando el driver por variable de entorno:
```bash
TABLA_REFERENCIA_DRIVER=bd python app.py
```
El sistema lee las especies desde la tabla SQLite `especies` sin modificar ni una sola línea de código en el dominio.

### Demostración 3: Intento de acceso a una planta ajena — debe fallar (R7)
1. En el frontend, haz clic en **"👤 Entrar como Carlos"**.
2. Haz clic en el botón rojo **"🚨 Probar acceso no autorizado a planta de Ana"**.
3. El frontend muestra la notificación de rechazo con **HTTP 403 Forbidden (`ACCESO_DENEGADO`)**, evidenciando que la regla de propiedad reside en el núcleo de dominio: `planta.pertenece_a(usuario_id)`.

### Demostración 4: Verificación de la Prueba de Cambio (15% de la Rúbrica)
Para demostrar al profesor que el Commit 4 no modificó el dominio:
```bash
git show 8c4b6d8 --stat
```
Verás que sólo se crearon `api_dispositivos.py`, `simulador_esp32.py`, su prueba y la línea de registro en `matera/app.py`. **Cero (0) archivos modificados en `matera/dominio/` y `matera/puertos/`.**

---

## 4. Estructura del Repositorio

```
SmartPlantBase/
├── data/
│   ├── especies_referencia.csv       # Catálogo CSV de 5 especies (Anexo B)
│   └── matera.db                     # Base de datos SQLite autogenerada
├── frontend/
│   ├── index.html                    # Dashboard (Login + Polling R6 + Form R1)
│   ├── css/style.css
│   └── js/
│       ├── config.js                 # Dirección de la API
│       ├── api.js                    # Fetch con cabeceras Bearer
│       ├── ui.js                     # Renderizado en DOM
│       └── app.js                    # Polling cada 3s y control de sesión
├── matera/
│   ├── dominio/
│   │   ├── modelo.py                 # Entidades puras: Lectura, Especie, Planta, Usuario
│   │   ├── validador.py              # ValidadorDeEstado y ServicioMateraDominio
│   │   └── excepciones.py            # Excepciones de negocio (0 dependencias)
│   ├── puertos/
│   │   ├── entrada.py                # ValidarLecturaPort, RegistrarLecturaPort, etc.
│   │   └── salida.py                 # TablaReferenciaPort, HistorialLecturasPort, etc.
│   ├── adaptadores/
│   │   ├── entrada/
│   │   │   ├── api_front.py          # Endpoints web REST (/api/v1/..., /api/auth/...)
│   │   │   ├── api_dispositivos.py   # Endpoint sensor: POST /api/dispositivos/{id}/lecturas
│   │   │   └── seguridad_jwt.py      # Decoradores @requiere_jwt_usuario y @requiere_jwt_dispositivo
│   │   └── salida/
│   │       ├── tabla_csv.py          # Adaptador CSV de TablaReferenciaPort
│   │       ├── tabla_bd.py           # Adaptador SQLite de TablaReferenciaPort
│   │       ├── historial_bd.py       # Adaptador SQLite de Historial y Plantas
│   │       └── emisor_jwt.py         # Adaptador PyJWT de EmisorTokenPort
│   └── app.py                        # Composition Root (create_app)
├── app.py                            # Punto de arranque en raíz (delega a matera.app)
├── simulador_esp32.py                # Script independiente del simulador ESP32
├── tests/
│   ├── fakes.py                      # Dobles de prueba en memoria
│   ├── test_dominio.py               # Pruebas unitarias puras del dominio
│   ├── test_adaptadores_salida.py    # Pruebas de persistencia e intercambiabilidad
│   ├── test_seguridad_jwt.py         # Pruebas de JWT y regla de propiedad
│   └── test_api_dispositivos.py      # Pruebas del endpoint de sensores ESP32
├── docs/
│   ├── plan_fase2_arquitectura_hexagonal.md
│   └── documento_arquitectura.md     # Documento entregable (máximo 4 páginas)
├── requirements.txt
└── README.md
```
