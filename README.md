# SmartPlantBase · Matera Inteligente

**Universidad Sergio Arboleda · Arquitectura de Software · 2026-3**
**Fase 2:** del sensor al dominio, con arquitectura hexagonal (puertos y adaptadores).
**Stack:** Python 3.10+ · Flask · SQLite · PyJWT · pytest. Front en HTML, CSS y JavaScript estáticos.

El sistema recibe lecturas de humedad del sustrato, luz y temperatura de una matera (un ESP32, aquí simulado), las compara con los rangos de referencia de su especie y calcula el estado de la planta: `SALUDABLE`, `EN_RIESGO` o `CRITICO`. Cada usuario ve solo sus plantas, su estado actual y su historial.

---

## 1. Arquitectura

```
                 ADAPTADORES DE ENTRADA                 DOMINIO                       ADAPTADORES DE SALIDA
  front (fetch) ─► api_front.py ─────┐                                         ┌──► tabla_csv.py / tabla_bd.py
  ESP32 / sim.  ─► api_dispositivos.py ─► puertos de entrada ─► casos_uso ─► puertos de salida ──► historial_bd.py, plantas_bd.py, usuarios_bd.py
  pruebas       ─► (directo)         ┘        (seguridad.py verifica el token antes)     └──► emisor_jwt.py, hasher_werkzeug.py
```

Las dependencias apuntan hacia adentro: los adaptadores conocen los puertos y el dominio no conoce a los adaptadores.

- **Dominio (`matera/dominio/`)**: no importa Flask, HTTP, SQL, CSV, JSON ni PyJWT.
  - `modelo.py`: `Lectura`, `Especie`, `Planta`, `Usuario`, `Diagnostico` y los objetos que devuelven los casos de uso.
  - `validador.py`: `ValidadorDeEstado`, que clasifica cada parámetro (BAJO, OPTIMO, ALTO) y deriva el estado global: 0 desviaciones da SALUDABLE, 1 da EN_RIESGO y 2 o más da CRITICO.
  - `casos_uso/`: un caso de uso por puerto de entrada. `casos_uso/propiedad.py` tiene la regla "un usuario solo ve sus plantas".
  - `puertos/entrada.py` y `puertos/salida.py`: los contratos los define el dominio.
- **Adaptadores de entrada (`matera/adaptadores/entrada/`)**: traducen HTTP a llamadas a los puertos y los objetos del dominio a JSON (`serializacion.py`). `seguridad.py` verifica el token antes del caso de uso, a través de `VerificadorTokenPort`, implementado con PyJWT en `verificador_jwt.py`.
- **Adaptadores de salida (`matera/adaptadores/salida/`)**: un adaptador por puerto (CSV, SQLite, PyJWT, werkzeug).
- **Composición (`matera/app.py`)**: el único lugar donde se decide qué adaptador va con qué puerto.

### Puertos y adaptadores

| Puerto | Tipo | Lo implementa / lo usa |
|---|---|---|
| `ValidarLecturaPort`, `ConsultarEspeciesPort` | Entrada | `ValidarLectura`, `ConsultarEspecies` · usados por `api_front.py` |
| `RegistrarLecturaPort` | Entrada | `RegistrarLectura` · usado por `api_dispositivos.py` |
| `ConsultarEstadoPort`, `ConsultarHistorialPort`, `ListarPlantasPort` | Entrada | `ConsultarEstado`, `ConsultarHistorial`, `ListarPlantas` · usados por `api_front.py` |
| `RegistrarPlantaPort`, `EmitirTokenDispositivoPort` | Entrada | `RegistrarPlanta`, `EmitirTokenDispositivo` · usados por `api_front.py` |
| `AutenticarUsuarioPort` | Entrada | `AutenticarUsuario` · usado por `api_front.py` |
| `TablaReferenciaPort` | Salida | `CsvTablaReferenciaAdapter` (`tabla_csv.py`) o `BdTablaReferenciaAdapter` (`tabla_bd.py`) |
| `HistorialLecturasPort` | Salida | `BdHistorialLecturasAdapter` (`historial_bd.py`) |
| `PlantasPort` / `UsuariosPort` | Salida | `BdPlantasAdapter` (`plantas_bd.py`) / `BdUsuariosAdapter` (`usuarios_bd.py`) |
| `EmisorTokenPort` | Salida | `JwtEmisorTokenAdapter` (`emisor_jwt.py`) |
| `HasherContrasenaPort` | Salida | `WerkzeugHasherAdapter` (`hasher_werkzeug.py`) |
| `VerificadorTokenPort` | Borde de entrada | `JwtVerificadorToken` (`verificador_jwt.py`) · usado por `seguridad.py` |

### Dónde se emite y dónde se verifica el JWT

- **Se emite** en `adaptadores/salida/emisor_jwt.py`, cuando el caso de uso `AutenticarUsuario` (login o registro) o `RegistrarPlanta` / `EmitirTokenDispositivo` lo piden a través de `EmisorTokenPort`.
- **Se verifica** en `adaptadores/entrada/seguridad.py` (decoradores `@requiere_usuario` y `@requiere_dispositivo`), que usan `verificador_jwt.py`. Al caso de uso le llega solo el `usuario_id`, nunca el token.
- **Hay dos alcances.** El token de **usuario** dura 24 h y sirve para el front. El token de **dispositivo** dura 1 año y solo sirve para `POST /api/dispositivos/{su id}/lecturas`.

---

## 2. Instalación

```bash
git clone https://github.com/estebanstack/SmartPlantBase.git
cd SmartPlantBase
python -m venv venv
source venv/bin/activate          # en Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # en Windows: copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"   # pegar el resultado en JWT_SECRET dentro de .env
```

Variables de `.env`:

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `JWT_SECRET` | Clave para firmar y verificar los tokens | Clave temporal (los tokens dejan de valer al reiniciar) |
| `TABLA_REFERENCIA_DRIVER` | De dónde se leen las especies: `csv` o `bd` | `csv` |
| `CARGAR_DATOS_DEMO` | `1` carga a Ana y Carlos con sus plantas; `0` deja la base vacía | `1` |
| `PORT` | Puerto del backend | `5000` |

La base `data/matera.db` se crea sola al arrancar, con los scripts de `data/bd/` (`esquema.sql`, `carga_especies.sql` y, si se pide, `datos_demo.sql`). También se puede crear a mano:

```bash
python -m matera.adaptadores.salida.sqlite_bd data/matera.db --demo
```

> Si tienen una `data/matera.db` de una versión anterior, bórrenla: el esquema del historial cambió.

---

## 3. Ejecución

Se usan tres terminales.

**1. Backend**
```bash
python app.py
```

**2. Front** (servido aparte, desde otro origen)
```bash
python -m http.server 8000 --directory frontend
```
Abrir `http://localhost:8000`. Usuarios de demostración: `ana@matera.edu.co` y `carlos@matera.edu.co`, los dos con la clave `clave123`. También se puede crear una cuenta nueva.

**3. Simulador del ESP32**

El simulador necesita el token de su dispositivo, y ese token lo entrega el backend:
- **Desde el front:** en "Mis plantas", pulsar **Obtener token del dispositivo** (o registrar una planta nueva) y luego **Copiar comando**.
- **Desde la terminal**, para la planta de Ana (`planta-01`, dispositivo `esp32-01`):
  ```bash
  TOKEN_ANA=$(curl -s -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"ana@matera.edu.co","password":"clave123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

  TOKEN_DISPOSITIVO=$(curl -s -X POST http://localhost:5000/api/plantas/planta-01/token-dispositivo \
    -H "Authorization: Bearer $TOKEN_ANA" | python -c "import sys,json;print(json.load(sys.stdin)['token_dispositivo'])")

  python simulador_esp32.py --dispositivo-id esp32-01 --token "$TOKEN_DISPOSITIVO" --intervalo 3
  ```

Qué hace el simulador:
- **Lecturas realistas.** La tierra se va secando según la luz y el calor, y de vez en cuando "riegan". La luz sigue el ciclo del día y la temperatura sube de día y baja de noche.
- **Valores fuera de rango.** Salen solos, por ejemplo cuando la tierra se seca o hay demasiado sol, y el backend responde **201** con `EN_RIESGO` o `CRITICO`.
- **Datos inválidos a propósito**, cerca del 15 % por defecto: valor imposible, valor no numérico o campo faltante (**400**), y peticiones sin token (**401**). Ninguno entra al historial.
- **Opciones:** `--intervalo`, `--iteraciones`, `--prob-error 0` (sin datos inválidos), `--minutos-por-lectura`, `--humedad-inicial`, `--semilla` (repetir la misma secuencia). Con `python simulador_esp32.py --help` se ven todas.

El simulador es un script independiente: solo usa la librería estándar y no importa nada de `matera/`.

---

## 4. API

Todas las respuestas son JSON. Los errores tienen siempre la misma forma: `{"error": "CODIGO", "mensaje": "...", "detalle": {...}}`.

| Método y ruta | Token | Qué hace |
|---|---|---|
| `GET /api/v1/especies` | — | Catálogo de especies con sus rangos (público) |
| `POST /api/v1/diagnosticos` | Usuario | Diagnóstico de una medición escrita a mano |
| `POST /api/auth/registro` | — | Crea una cuenta y devuelve el token de usuario |
| `POST /api/auth/login` | — | Inicia sesión y devuelve el token de usuario |
| `GET /api/plantas` | Usuario | Plantas del usuario |
| `POST /api/plantas` | Usuario | Registra una planta con su dispositivo y devuelve el `token_dispositivo` |
| `POST /api/plantas/{id}/token-dispositivo` | Usuario (dueño) | Token nuevo para el dispositivo de la planta |
| `GET /api/plantas/{id}/estado` | Usuario (dueño) | Última lectura y su diagnóstico |
| `GET /api/plantas/{id}/historial?limite=20` | Usuario (dueño) | Lecturas guardadas, de la más reciente a la más antigua |
| `POST /api/dispositivos/{id}/lecturas` | Dispositivo (el mismo `{id}`) | El ESP32 reporta una lectura |

Cuerpo de una lectura del dispositivo:
```json
{ "dispositivo_id": "esp32-01", "marca_tiempo": "2026-10-27T15:00:00Z",
  "humedad": 34.2, "luz": 820, "temperatura": 22.4 }
```

Códigos de error:

| Código | HTTP | Cuándo |
|---|---|---|
| `PARAMETRO_INVALIDO` | 400 | Falta un campo, no es numérico, está fuera de lo físicamente posible o la `marca_tiempo` no es ISO-8601 |
| `AUTORIZACION_REQUERIDA`, `TOKEN_INVALIDO`, `TOKEN_EXPIRADO`, `CREDENCIALES_INVALIDAS` | 401 | Sin token, token malo o vencido, o clave equivocada |
| `ACCESO_DENEGADO` | 403 | Token con otro alcance, dispositivo que se hace pasar por otro, o planta de otro usuario |
| `ESPECIE_NO_SOPORTADA`, `PLANTA_NO_ENCONTRADA`, `DISPOSITIVO_NO_ENCONTRADO` | 404 | No existe |
| `USUARIO_YA_EXISTE`, `DISPOSITIVO_YA_VINCULADO` | 409 | Correo o dispositivo ya usados |

---

## 5. Pruebas

```bash
pytest
```

| Archivo | Qué prueba |
|---|---|
| `tests/test_dominio.py` | Reglas y casos de uso **sin servidor, sin archivos y sin base de datos**, con los dobles de `tests/fakes.py` |
| `tests/test_adaptadores_salida.py` | CSV y SQLite devuelven las mismas especies, el historial, los usuarios, las plantas y el hasher |
| `tests/test_api_endpoints.py` | Diagnóstico manual y catálogo (R1) y errores uniformes |
| `tests/test_api_dispositivos.py` | Endpoint del dispositivo: token, suplantación, lecturas válidas e inválidas |
| `tests/test_api_plantas.py` | Flujo completo: usuario → planta → token → lectura → estado |
| `tests/test_seguridad_jwt.py` | Login, tokens inválidos o vencidos, alcances y planta ajena (403) |
| `tests/test_simulador.py` | El simulador no importa el proyecto, genera datos realistas y funciona de punta a punta |

Para comprobar que el dominio no depende de la infraestructura, se puede quitar la carpeta de adaptadores y correr solo las pruebas del dominio:

```bash
mv matera/adaptadores /tmp/adaptadores && pytest tests/test_dominio.py; mv /tmp/adaptadores matera/adaptadores
```

---

## 6. Guion de la sustentación

1. **Simulador en vivo:** backend, front y simulador corriendo. El panel de la planta cambia solo cada 3 s y el historial va creciendo.
2. **CSV → base de datos por configuración:** detener el backend y arrancarlo con `TABLA_REFERENCIA_DRIVER=bd python app.py`, o cambiar la variable en `.env`. El catálogo sigue igual y no se toca código.
3. **Planta ajena:** iniciar sesión como Carlos, escribir `planta-01` (es de Ana) en **"Probar acceso a otra planta por su id"** y pulsar **Consultar**. Responde **403**: el token es válido, pero la regla de propiedad del dominio lo rechaza.
4. **Prueba de cambio:** los commits que agregan el adaptador de dispositivos y el simulador no tocan `matera/dominio/`:
   ```bash
   git show --stat 8c4b6d8   # adaptador de dispositivos + primer simulador
   git show --stat e6e5acd   # simulador independiente
   ```

---

## 7. Estructura del repositorio

```
SmartPlantBase/
├── app.py                         # Arranque: carga .env y llama a create_app()
├── simulador_esp32.py             # Simulador independiente del ESP32
├── .env.example                   # Plantilla de configuración (copiar como .env)
├── data/
│   ├── especies_referencia.csv    # Tabla de referencia en CSV (5 especies, Anexo B)
│   └── bd/
│       ├── esquema.sql            # Creación de tablas
│       ├── carga_especies.sql     # Carga de las 5 especies
│       └── datos_demo.sql         # Ana y Carlos con sus plantas (solo demo)
├── matera/
│   ├── app.py                     # Punto de composición (create_app)
│   ├── dominio/
│   │   ├── modelo.py · validador.py · excepciones.py
│   │   ├── casos_uso/             # Un caso de uso por puerto de entrada
│   │   └── puertos/               # entrada.py y salida.py
│   └── adaptadores/
│       ├── entrada/               # api_front, api_dispositivos, seguridad, verificador_jwt, serializacion
│       └── salida/                # tabla_csv, tabla_bd, historial_bd, plantas_bd, usuarios_bd,
│                                  # sqlite_bd, emisor_jwt, hasher_werkzeug
├── frontend/
│   ├── index.html · css/style.css
│   └── js/                        # config.js, api.js (HTTP), ui.js (DOM), app.js (orquestación)
├── tests/                         # Pruebas (ver sección 5) y dobles en fakes.py
└── docs/
    ├── enunciados/                # Enunciados de la Fase 1 y la Fase 2
    ├── diagramas/
    ├── documento_arquitectura.md
    └── bitacora_ia.md
```
