<style>
@page {
    size: letter;
    margin: 12mm 15mm 12mm 15mm;
    @bottom-right {
        content: "Página " counter(page) " de " counter(pages);
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.8pt;
        color: #64748b;
    }
    @bottom-left {
        content: "Universidad Sergio Arboleda · Arquitectura de Software · SmartPlantBase";
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.8pt;
        color: #64748b;
    }
}
body {
    font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 8.5pt;
    line-height: 1.36;
    color: #1e293b;
}
.header-box {
    border-bottom: 1.5pt solid #0f172a;
    padding-bottom: 5px;
    margin-bottom: 8px;
}
.header-box .institution {
    font-size: 7.8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #475569;
    margin: 0;
}
.header-box h1 {
    font-size: 13.5pt;
    font-weight: 800;
    color: #0f172a;
    margin: 2px 0;
    line-height: 1.2;
    border-bottom: none !important;
    padding-bottom: 0 !important;
}
.header-box .meta {
    font-size: 8.2pt;
    color: #334155;
    margin: 0;
}
h2 {
    font-size: 10pt;
    font-weight: 700;
    color: #0f172a !important;
    margin-top: 6px;
    margin-bottom: 3px;
    padding-bottom: 1px;
    border-bottom: 0.75pt solid #cbd5e1 !important;
    break-after: avoid;
    page-break-after: avoid;
}
h3 {
    font-size: 8.8pt;
    font-weight: 700;
    color: #1e293b !important;
    margin-top: 4px;
    margin-bottom: 2px;
    break-after: avoid;
    page-break-after: avoid;
}
p, ul, ol {
    margin-top: 1px;
    margin-bottom: 3px;
}
ul, ol {
    padding-left: 14px;
}
li {
    margin-bottom: 1.5px;
}
code {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 7.6pt !important;
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 1px 3px !important;
    border-radius: 3px !important;
    border: none !important;
}
pre, pre code {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 7.2pt !important;
    line-height: 1.2 !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 4px !important;
    padding: 4px 6px !important;
    margin: 3px 0 !important;
    white-space: pre-wrap !important;
    word-break: break-all !important;
    break-inside: avoid;
    page-break-inside: avoid;
}
table {
    width: 100% !important;
    border-collapse: collapse !important;
    border: none !important;
    margin: 4px 0 6px 0 !important;
    font-size: 7.4pt !important;
    line-height: 1.22 !important;
    break-inside: avoid;
    page-break-inside: avoid;
}
table th, table td {
    border-left: none !important;
    border-right: none !important;
    padding: 2.5px 4.5px !important;
}
table th {
    border-top: 1.5pt solid #0f172a !important;
    border-bottom: 0.75pt solid #0f172a !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    text-align: left;
}
table td {
    border-bottom: 0.5pt solid #e2e8f0 !important;
    vertical-align: top;
    color: #334155 !important;
}
table tr:last-child td {
    border-bottom: 1.5pt solid #0f172a !important;
}
.figure-container {
    text-align: center;
    margin: 4px 0 6px 0;
    break-inside: avoid;
    page-break-inside: avoid;
}
.figure-caption {
    font-size: 7.5pt;
    color: #64748b;
    margin-top: 2px;
    font-style: italic;
    break-before: avoid;
}
.page-break {
    page-break-before: always;
    break-before: page;
}
.lead-text {
    font-size: 8.5pt;
    color: #334155;
    margin-bottom: 4px;
}
.callout {
    background-color: #f8fafc;
    border-left: 3px solid #0284c7;
    padding: 4px 8px;
    margin: 4px 0;
    font-size: 8.2pt;
}
</style>

<div class="header-box">
  <p class="institution">Universidad Sergio Arboleda · Escuela de Ciencias Exactas e Ingeniería · Arquitectura de Software</p>
  <h1>Documento de Arquitectura — Sistema SmartPlantBase (Fase 2)</h1>
  <p class="meta"><strong>Proyecto Matera Inteligente</strong> · Arquitectura Hexagonal (Puertos y Adaptadores) · <strong>Estudiante:</strong> Esteban Castro · <strong>Semestre:</strong> 2026-3 · <strong>Tecnologías:</strong> Python 3.14, Flask, SQLite, PyJWT, pytest</p>
</div>

## 1. Diagrama Hexagonal del Sistema

Para la segunda fase de SmartPlantBase estructuramos la aplicación mediante el patrón de **Puertos y Adaptadores (Alistair Cockburn, 2005)**. El objetivo principal es aislar la lógica botánica y las reglas de negocio de cualquier detalle tecnológico: protocolos de transporte, frameworks web, controladores de bases de datos o mecanismos de serialización.

La Figura 1 ilustra la vista de referencia de nuestra arquitectura, reflejando con exactitud los paquetes, clases, puertos y adaptadores implementados en el código:

<div class="figure-container">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 375" width="100%" height="auto" style="max-height: 250px; font-family: 'Liberation Sans', -apple-system, sans-serif;">
  <defs>
    <style>
      .bg-card { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.2; rx: 5px; }
      .bg-zone-entry { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1.2; stroke-dasharray: 4,3; rx: 7px; }
      .bg-zone-exit { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1.2; stroke-dasharray: 4,3; rx: 7px; }
      .bg-core { fill: #f1f5f9; stroke: #0f172a; stroke-width: 1.8; rx: 8px; }
      .bg-port-in { fill: #e0e7ff; stroke: #4f46e5; stroke-width: 1.1; rx: 4px; }
      .bg-port-out { fill: #fef3c7; stroke: #d97706; stroke-width: 1.1; rx: 4px; }
      .bg-sec { fill: #fef2f2; stroke: #dc2626; stroke-width: 1.1; rx: 4px; }
      .title-zone { font-size: 10px; font-weight: 700; text-transform: uppercase; fill: #475569; }
      .title-core { font-size: 12px; font-weight: 800; text-transform: uppercase; fill: #0f172a; }
      .card-title { font-size: 10px; font-weight: 700; fill: #1e293b; }
      .card-sub { font-size: 8.8px; font-weight: 600; fill: #475569; }
      .card-text { font-size: 8px; fill: #334155; }
      .badge-in { font-size: 8.5px; font-weight: 700; fill: #3730a3; }
      .badge-out { font-size: 8.5px; font-weight: 700; fill: #92400e; }
      .arrow { stroke: #64748b; stroke-width: 1.3; fill: none; marker-end: url(#arrow-h); }
      .arrow-accent { stroke: #4f46e5; stroke-width: 1.4; fill: none; marker-end: url(#arrow-ha); }
    </style>
    <marker id="arrow-h" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
    </marker>
    <marker id="arrow-ha" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#4f46e5" />
    </marker>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" />

  <!-- ZONE 1: ADAPTADORES DE ENTRADA -->
  <rect x="12" y="10" width="225" height="355" class="bg-zone-entry" />
  <text x="25" y="28" class="title-zone">Adaptadores de Entrada (Driving)</text>

  <rect x="20" y="38" width="209" height="92" class="bg-card" />
  <text x="28" y="53" class="card-title">api_front.py (REST Flask)</text>
  <text x="28" y="66" class="card-sub">• Interfaz Web y Consultas</text>
  <text x="28" y="80" class="card-text">POST /api/v1/diagnosticos (R1)</text>
  <text x="28" y="93" class="card-text">POST /api/auth/login · registro (R7)</text>
  <text x="28" y="106" class="card-text">GET  /api/plantas/{id}/estado (R5, R6)</text>
  <text x="28" y="119" class="card-text">GET  /api/plantas/{id}/historial</text>

  <rect x="20" y="136" width="209" height="80" class="bg-card" />
  <text x="28" y="152" class="card-title">api_dispositivos.py (REST)</text>
  <text x="28" y="165" class="card-sub">• Telemetría Sensores IoT (ESP32)</text>
  <text x="28" y="180" class="card-text">POST /api/dispositivos/{id}/lecturas (R2)</text>
  <text x="28" y="193" class="card-text">Alimentado por simulador_esp32.py (R3)</text>
  <text x="28" y="206" class="card-text">Exige Bearer Token con scope="dispositivo"</text>

  <rect x="20" y="222" width="209" height="70" class="bg-sec" />
  <text x="28" y="238" class="card-title" fill="#991b1b">seguridad_jwt.py (Borde)</text>
  <text x="28" y="252" class="card-text">• Decoradores: @requiere_jwt_usuario</text>
  <text x="28" y="265" class="card-text">  y @requiere_jwt_dispositivo</text>
  <text x="28" y="278" class="card-text">• Valida firma y segrega por scope</text>

  <rect x="20" y="298" width="209" height="58" class="bg-card" />
  <text x="28" y="315" class="card-title">tests/test_dominio.py</text>
  <text x="28" y="328" class="card-sub">• Pruebas Unitarias del Dominio</text>
  <text x="28" y="342" class="card-text">Dobles en memoria puros (tests/fakes.py)</text>

  <!-- ZONE 2: NÚCLEO HEXAGONAL -->
  <rect x="260" y="10" width="395" height="355" class="bg-core" />
  <text x="365" y="30" class="title-core">Núcleo de Dominio y Puertos</text>

  <rect x="272" y="42" width="371" height="66" class="bg-port-in" />
  <text x="282" y="56" class="badge-in">PUERTOS DE ENTRADA (matera/puertos/entrada.py)</text>
  <text x="282" y="71" class="card-text">• ValidarLecturaPort (R1: validación manual)</text>
  <text x="282" y="84" class="card-text">• RegistrarLecturaPort (R2: telemetría sensor y evaluación)</text>
  <text x="282" y="97" class="card-text">• ConsultarEstadoPort (R5, R6) · AutenticarUsuarioPort (R7)</text>

  <rect x="272" y="114" width="371" height="142" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1" rx="5px" />
  <text x="282" y="130" class="card-title">Dominio Puro (matera/dominio/)</text>
  <text x="282" y="145" class="card-sub">Entidades (modelo.py):</text>
  <text x="290" y="158" class="card-text">Lectura · Especie · Planta · Usuario · Diagnostico</text>
  <text x="282" y="174" class="card-sub">Servicios y Reglas Botánicas (validador.py):</text>
  <text x="290" y="188" class="card-text">• ValidadorDeEstado: evaluación según límites y rangos de especie</text>
  <text x="290" y="201" class="card-text">• ServicioMateraDominio: orquestador de los casos de uso</text>
  <text x="290" y="214" class="card-text">• Regla de Propiedad (R7): planta.pertenece_a(usuario_id)</text>
  <text x="282" y="233" class="card-sub" fill="#047857">Invariante: Cero imports de Flask, SQL, CSV, JSON o PyJWT</text>
  <text x="282" y="246" class="card-text" fill="#64748b">Excepciones botánicas: AccesoNoAutorizado, EspecieNoSoportada...</text>

  <rect x="272" y="262" width="371" height="92" class="bg-port-out" />
  <text x="282" y="277" class="badge-out">PUERTOS DE SALIDA (matera/puertos/salida.py)</text>
  <text x="282" y="292" class="card-text">• TablaReferenciaPort (R4: consulta rangos de especies)</text>
  <text x="282" y="305" class="card-text">• HistorialLecturasPort (R5: persistencia y última lectura)</text>
  <text x="282" y="318" class="card-text">• UsuariosPlantasPort (R7: consulta y relación planta-usuario)</text>
  <text x="282" y="331" class="card-text">• EmisorTokenPort (R7: contrato abstracto para emisión de tokens)</text>
  <text x="282" y="346" class="card-text" fill="#b45309">El dominio declara la necesidad; la infraestructura la satisface</text>

  <!-- ZONE 3: ADAPTADORES DE SALIDA -->
  <rect x="678" y="10" width="230" height="355" class="bg-zone-exit" />
  <text x="692" y="28" class="title-zone">Adaptadores de Salida (Driven)</text>

  <rect x="688" y="38" width="210" height="94" class="bg-card" />
  <text x="698" y="53" class="card-title">tabla_csv.py / tabla_bd.py</text>
  <text x="698" y="66" class="card-sub">• Implementan TablaReferenciaPort (R4)</text>
  <text x="698" y="80" class="card-text">CsvTablaReferenciaAdapter (CSV)</text>
  <text x="698" y="93" class="card-text">BdTablaReferenciaAdapter (SQLite)</text>
  <text x="698" y="108" class="card-text">Conmutables por configuración mediante</text>
  <text x="698" y="121" class="card-text">la variable TABLA_REFERENCIA_DRIVER</text>

  <rect x="688" y="138" width="210" height="96" class="bg-card" />
  <text x="698" y="154" class="card-title">historial_bd.py (SQLite)</text>
  <text x="698" y="167" class="card-sub">• Implementa:</text>
  <text x="698" y="180" class="card-text">  - HistorialLecturasPort (R5)</text>
  <text x="698" y="193" class="card-text">  - UsuariosPlantasPort (R7)</text>
  <text x="698" y="208" class="card-text">BdHistorialYPlantasAdapter:</text>
  <text x="698" y="221" class="card-text">Persiste lecturas, diagnósticos y usuarios</text>

  <rect x="688" y="240" width="210" height="74" class="bg-card" />
  <text x="698" y="256" class="card-title">emisor_jwt.py (PyJWT)</text>
  <text x="698" y="269" class="card-sub">• Implementa EmisorTokenPort (R7)</text>
  <text x="698" y="284" class="card-text">JwtEmisorTokenAdapter:</text>
  <text x="698" y="297" class="card-text">Firma tokens HS256 con claims estructurados</text>

  <rect x="688" y="320" width="210" height="36" fill="#e2e8f0" stroke="#64748b" stroke-width="1" rx="4px" />
  <text x="698" y="335" class="card-title" font-size="9.5px">matera/app.py</text>
  <text x="698" y="347" class="card-text">Punto Único de Composición (Composition Root)</text>

  <!-- CONEXIONES -->
  <path d="M 229 84 L 272 75" class="arrow" />
  <path d="M 229 176 L 272 85" class="arrow-accent" />
  <path d="M 229 327 L 272 95" class="arrow" />

  <path d="M 643 285 L 688 85" class="arrow" />
  <path d="M 643 310 L 688 185" class="arrow" />
  <path d="M 643 330 L 688 277" class="arrow" />
</svg>
<div class="figure-caption">Figura 1. Vista hexagonal del sistema con los adaptadores, puertos y el núcleo de dominio implementados en el proyecto.</div>
</div>

El flujo de dependencias apunta siempre hacia adentro:
- **Adaptadores de entrada (primarios):** Traducen estímulos del exterior a invocaciones de los puertos de entrada. El módulo `api_front.py` maneja las solicitudes HTTP web del usuario y `api_dispositivos.py` recibe la telemetría periódica del ESP32.
- **Núcleo de dominio:** Agrupa las entidades botánicas (`Lectura`, `Especie`, `Planta`, `Usuario`, `Diagnostico`) y los servicios de evaluación (`ValidadorDeEstado`). No contiene librerías externas ni referencias a HTTP o SQL.
- **Adaptadores de salida (secundarios):** Implementan los contratos definidos por el dominio para interactuar con la infraestructura: almacenamiento relacional en SQLite (`historial_bd.py`), catálogo botánico (`tabla_csv.py` y `tabla_bd.py`) y firma de credenciales (`emisor_jwt.py`).

<div class="page-break"></div>

## 2. Tabla de Puertos y Adaptadores

Los puertos desacoplan el núcleo de las tecnologías externas mediante contratos explícitos definidos en Python con clases base abstractas (`abc.ABC`):

| Puerto | Dirección | Archivo de Interfaz | Adaptador Concreto | Responsabilidad en el Negocio |
| :--- | :---: | :--- | :--- | :--- |
| **ValidarLecturaPort** | Entrada | `matera/puertos/entrada.py` | ServicioMateraDominio *(consumido por `api_front.py`)* | Evalúa lecturas enviadas de forma manual desde la interfaz web contra los rangos de la especie (R1). |
| **RegistrarLecturaPort** | Entrada | `matera/puertos/entrada.py` | ServicioMateraDominio *(consumido por `api_dispositivos.py`)* | Procesa la telemetría enviada por el ESP32 (R2), calcula el diagnóstico botánico y solicita la persistencia histórica (R5). |
| **ConsultarEstadoPort** | Entrada | `matera/puertos/entrada.py` | ServicioMateraDominio *(consumido por `api_front.py`)* | Recupera el estado actual y el historial de una planta, aplicando la validación de propiedad de usuario (R5, R6, R7). |
| **AutenticarUsuarioPort** | Entrada | `matera/puertos/entrada.py` | ServicioMateraDominio *(consumido por `api_front.py`)* | Autentica credenciales de usuarios, registra cuentas nuevas y coordina la generación de tokens de sesión (R7). |
| **TablaReferenciaPort** | Salida | `matera/puertos/salida.py` | CsvTablaReferenciaAdapter<br>BdTablaReferenciaAdapter | Proporciona las especies botánicas y sus rangos óptimos. Es intercambiable por configuración (CSV o SQLite) (R4). |
| **HistorialLecturasPort** | Salida | `matera/puertos/salida.py` | BdHistorialYPlantasAdapter | Persiste cada lectura recibida junto con su diagnóstico y consulta el registro más reciente por planta (R5). |
| **UsuariosPlantasPort** | Salida | `matera/puertos/salida.py` | BdHistorialYPlantasAdapter | Almacena y consulta la información de usuarios, plantas registradas y la relación entre sensor y planta (R7). |
| **EmisorTokenPort** | Salida | `matera/puertos/salida.py` | JwtEmisorTokenAdapter | Firma tokens criptográficos JWT segregados para usuarios y dispositivos mediante el algoritmo HS256 (R7). |

## 3. Manejo de Seguridad, Alcances de JWT y Regla de Propiedad

La autenticación y autorización protegen el sistema en el perímetro sin invadir el núcleo del dominio:

- **Segregación de Alcances (User vs Device):** El sistema emite dos tipos de tokens disyuntos mediante el claim `scope`. El **token de usuario** (`scope="usuario"`), emitido en `/api/auth/login`, autoriza la consulta y gestión de plantas propias. El **token de dispositivo** (`scope="dispositivo"`), asignado al sensor ESP32, autoriza únicamente el reporte de telemetría en `POST /api/dispositivos/{id}/lecturas`.
- **Puntos de Emisión y Verificación:** La emisión se delega al puerto de salida `EmisorTokenPort`, implementado por `JwtEmisorTokenAdapter` en `matera/adaptadores/salida/emisor_jwt.py` (único punto que utiliza `PyJWT` con algoritmo HS256). La verificación ocurre en los adaptadores de entrada mediante los decoradores `@requiere_jwt_usuario` y `@requiere_jwt_dispositivo` (`seguridad_jwt.py`), rechazando con HTTP 403 Forbidden cualquier intento de cruzar alcances antes de invocar al dominio.
- **Aislamiento del Dominio:** El dominio desconoce el estándar RFC 7519 y las cabeceras HTTP `Authorization`. El decorador extrae la identidad limpia (`usuario_id` o `dispositivo_id`) y la entrega como parámetro al caso de uso, permitiendo probar el dominio de forma aislada sin generar tokens ni depender de claves criptográficas.
- **Regla de Propiedad en el Dominio:** La verificación de pertenencia es una regla botánica y reside en el dominio:
```python
# matera/dominio/validador.py (ConsultarEstadoPort)
planta = self._usuarios_plantas.obtener_planta_por_id(planta_id)
if not planta.pertenece_a(usuario_id):
    raise AccesoNoAutorizadoPlantaError(usuario_id=usuario_id, planta_id=planta_id)
```
Si un usuario autenticado intenta consultar una planta que no le pertenece, el dominio lanza `AccesoNoAutorizadoPlantaError`, y la capa HTTP responde con HTTP 403 Forbidden (`ACCESO_DENEGADO`).

<div class="page-break"></div>

## 4. Justificación de Principios SOLID en el Código

La estructura de paquetes y clases del proyecto aplica los principios de diseño orientado a objetos:

- **Inversión de Dependencias (DIP):** El núcleo de dominio no depende de bibliotecas externas ni de adaptadores concretos; depende de abstracciones. `ServicioMateraDominio` recibe la interfaz `TablaReferenciaPort`, por lo que desconoce si las especies provienen de un archivo de texto o de SQLite:
```python
# matera/puertos/salida.py
class TablaReferenciaPort(ABC):
    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Especie]:
        """Contrato para consultar especie sin acoplarse al medio de persistencia."""
```
Tanto `CsvTablaReferenciaAdapter` como `BdTablaReferenciaAdapter` implementan esta abstracción. El módulo `validador.py` no importa `sqlite3` ni `csv`.

- **Abierto/Cerrado (OCP):** El sistema permite incorporar nuevas funcionalidades mediante la adición de adaptadores, manteniendo el dominio cerrado a modificaciones. Al añadir la telemetría del ESP32 (R2) y el simulador (R3), únicamente construimos `api_dispositivos.py` y `simulador_esp32.py`; el evaluador botánico no requirió ajustes. Igualmente, alternar entre CSV y base de datos (R4) se resuelve en el Composition Root (`matera/app.py`) sin tocar el dominio.

- **Segregación de Interfaces (ISP):** Definimos puertos específicos en lugar de interfaces genéricas sobrecargadas. `TablaReferenciaPort` contiene únicamente lectura de especies botánicas; `HistorialLecturasPort` expone persistencia de telemetría; `EmisorTokenPort` define la generación de tokens. Los adaptadores de entrada solo conocen el puerto que requieren para su caso de uso (por ejemplo, `api_dispositivos.py` solo recibe `RegistrarLecturaPort`).

- **Responsabilidad Única (SRP):** Cada componente tiene una única razón de cambio. `ValidadorDeEstado` se modifica únicamente si cambian las reglas botánicas de evaluación; `seguridad_jwt.py` cambia si varía la política de autenticación HTTP; y `historial_bd.py` cambia si se altera el esquema relacional de SQLite.

---

## 5. Verificación de la Prueba de Cambio: Sensor ESP32

Para verificar que la arquitectura permite integrar nuevos canales sin perturbar las reglas de negocio, la incorporación del sensor ESP32 y su simulador se realizó en un commit dedicado:

- **Identificador de Commit:** [`8c4b6d8685aeb2bf2784258d349550a6cbf25812`](https://github.com/usuario/SmartPlantBase/commit/8c4b6d8685aeb2bf2784258d349550a6cbf25812)
- **Mensaje del Commit:** `feat(dispositivos): adaptador de dispositivos y simulador ESP32 (Prueba de Cambio)`
- **Archivos creados y modificados:**
  - `matera/adaptadores/entrada/api_dispositivos.py` (nuevo adaptador REST para el sensor)
  - `simulador_esp32.py` (script autónomo de telemetría y pruebas de robustez)
  - `tests/test_api_dispositivos.py` (suite de integración para el nuevo endpoint)
  - `matera/app.py` (registro del blueprint en el punto de composición)

### Comprobación de Invarianza del Dominio
Al auditar los cambios introducidos entre dicho commit y su predecesor sobre las carpetas de negocio:
```bash
git diff 8c4b6d8~1 8c4b6d8 -- matera/dominio/ matera/puertos/
```
El resultado no reporta ninguna diferencia. Los archivos `modelo.py`, `validador.py`, `excepciones.py`, `entrada.py` y `salida.py` no sufrieron alteraciones. 

Esto confirma que el requerimiento R2 se conectó utilizando el puerto preexistente `RegistrarLecturaPort`, demostrando que la separación entre adaptadores y dominio preserva la estabilidad del núcleo cuando se añaden nuevas fuentes de datos.

<div class="page-break"></div>

## 6. Análisis de Pregunta de Cambio: Migración de Transporte a MQTT

Durante la sustentación se evalúa la capacidad de evolución del sistema ante un cambio tecnológico imprevisto:

> *"Si mañana las lecturas ambientales de la matera ya no llegaran por solicitudes HTTP REST, sino mediante mensajes asíncronos publicados en un broker MQTT (por ejemplo, en el tópico `matera/dispositivos/{id}/telemetria`), ¿qué componentes del repositorio cambiarían y cuáles permanecerían intactos?"*

### Componentes Nuevos a Implementar (Adaptador de Entrada)
1. **Nuevo adaptador de suscripción MQTT (`matera/adaptadores/entrada/suscriptor_mqtt.py`):**
   - Utiliza una librería de cliente MQTT como `paho-mqtt`.
   - Se suscribe al patrón de tópicos `matera/dispositivos/+/telemetria`.
   - Al recibir un mensaje en su callback `on_message`, extrae el identificador del dispositivo del tópico, deserializa el payload JSON y valida la integridad de los campos (`humedad`, `luz`, `temperatura`, `marca_tiempo`).
   - Invoca directamente el puerto de entrada:
```python
diagnostico = self._puerto_registro.registrar(
    dispositivo_id=dispositivo_id,
    valores=valores_medidos,
    marca_tiempo=marca_tiempo,
)
```
2. **Suite de pruebas del adaptador (`tests/test_suscriptor_mqtt.py`):**
   - Verifica la recepción de mensajes, el manejo de payloads corruptos y la correcta llamada a `RegistrarLecturaPort` mediante dobles de prueba.

### Componentes Existentes a Modificar (Únicamente Composición y Entorno)
1. **Punto único de composición (`matera/app.py`):**
   - Se instancia el nuevo adaptador `suscriptor_mqtt` pasándole la misma instancia existente de `servicio_dominio` (que implementa `RegistrarLecturaPort`).
   - Se inicia el bucle de red del cliente MQTT en segundo plano (`client.loop_start()`).
2. **Dependencias del proyecto (`requirements.txt`):**
   - Se añade la dependencia del cliente MQTT (`paho-mqtt`).

### Componentes que Permanecen Intactos
- **Núcleo de dominio (`matera/dominio/*`):** `modelo.py`, `validador.py` y `excepciones.py` no requieren ningún cambio. El evaluador botánico desconoce por completo si las lecturas provinieron de un paquete TCP, un socket MQTT o una petición HTTP.
- **Puertos de entrada y salida (`matera/puertos/*`):** `RegistrarLecturaPort` conserva su firma agnóstica (`dispositivo_id: str`, `valores: Mapping`, `marca_tiempo: str`), ya que fue diseñado pensando en el caso de uso y no en el protocolo.
- **Adaptadores de salida (`matera/adaptadores/salida/*`):** La persistencia del historial en SQLite (`historial_bd.py`) y la consulta de rangos de especies (`tabla_csv.py` / `tabla_bd.py`) se ejecutan exactamente igual.

---

## 7. Conclusión y Síntesis de la Arquitectura

La adopción de arquitectura hexagonal en esta segunda fase de SmartPlantBase resuelve dos problemas fundamentales de la ingeniería de software: el desacoplamiento de la tecnología frente a las reglas botánicas y la segregación limpia de responsabilidades de seguridad. Al ubicar la verificación de tokens JWT en los adaptadores primarios y delegar la regla de propiedad al dominio, logramos un sistema robusto, fácil de someter a pruebas unitarias en memoria y preparado para incorporar futuros clientes móviles o sensores industriales sin deuda técnica.
