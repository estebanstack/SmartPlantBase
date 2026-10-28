<style>
@page {
    size: letter;
    margin: 11mm 14mm 11mm 14mm;
    @bottom-right {
        content: "Página " counter(page) " de " counter(pages);
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.6pt;
        color: #64748b;
    }
    @bottom-left {
        content: "Universidad Sergio Arboleda · Arquitectura de Software · SmartPlantBase";
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.6pt;
        color: #64748b;
    }
}
body {
    font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 8.3pt;
    line-height: 1.32;
    color: #1e293b;
}
.header-box {
    border-bottom: 1.5pt solid #0f172a;
    padding-bottom: 4px;
    margin-bottom: 6px;
}
.header-box .institution {
    font-size: 7.6pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #475569;
    margin: 0;
}
.header-box h1 {
    font-size: 13pt;
    font-weight: 800;
    color: #0f172a;
    margin: 2px 0;
    line-height: 1.18;
    border-bottom: none !important;
    padding-bottom: 0 !important;
}
.header-box .meta {
    font-size: 8pt;
    color: #334155;
    margin: 0;
}
h2 {
    font-size: 9.6pt;
    font-weight: 700;
    color: #0f172a !important;
    margin-top: 5px;
    margin-bottom: 2.5px;
    padding-bottom: 1px;
    border-bottom: 0.75pt solid #cbd5e1 !important;
    break-after: avoid;
    page-break-after: avoid;
}
h3 {
    font-size: 8.5pt;
    font-weight: 700;
    color: #1e293b !important;
    margin-top: 3.5px;
    margin-bottom: 1.5px;
    break-after: avoid;
    page-break-after: avoid;
}
p, ul, ol {
    margin-top: 1px;
    margin-bottom: 2.5px;
}
ul, ol {
    padding-left: 13px;
}
li {
    margin-bottom: 1.2px;
}
code {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 7.3pt !important;
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 0.5px 2.5px !important;
    border-radius: 2px !important;
    border: none !important;
}
pre {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 7.0pt !important;
    line-height: 1.18 !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 0.75pt solid #cbd5e1 !important;
    border-radius: 3px !important;
    padding: 3.5px 6px !important;
    margin: 2.5px 0 !important;
    white-space: pre-wrap !important;
    word-break: break-all !important;
    break-inside: avoid;
    page-break-inside: avoid;
}
pre code {
    display: block !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    color: inherit !important;
    font-family: inherit !important;
    font-size: inherit !important;
    line-height: inherit !important;
    white-space: pre-wrap !important;
}
table {
    width: 100% !important;
    border-collapse: collapse !important;
    border: none !important;
    margin: 2.5px 0 3.5px 0 !important;
    font-size: 7.0pt !important;
    line-height: 1.15 !important;
    break-inside: avoid;
    page-break-inside: avoid;
}
table th, table td {
    border-left: none !important;
    border-right: none !important;
    padding: 1.6px 3.5px !important;
}
table th {
    border-top: 1.2pt solid #0f172a !important;
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
    border-bottom: 1.2pt solid #0f172a !important;
}
.figure-container {
    text-align: center;
    margin: 3px 0 4px 0;
    break-inside: avoid;
    page-break-inside: avoid;
}
.figure-caption {
    font-size: 7.3pt;
    color: #64748b;
    margin-top: 2px;
    font-style: italic;
    break-before: avoid;
}
.page-break {
    page-break-before: always;
    break-before: page;
}
blockquote {
    border-left: 2.5px solid #3b82f6;
    margin: 3px 0;
    padding: 2px 8px;
    background-color: #f8fafc;
    font-style: italic;
    font-size: 7.8pt;
    color: #334155;
}
</style>

<div class="header-box">
  <p class="institution">Universidad Sergio Arboleda · Escuela de Ciencias Exactas e Ingeniería · Arquitectura de Software</p>
  <h1>Documento de Arquitectura — Sistema SmartPlantBase (Fase 2)</h1>
  <p class="meta"><strong>Proyecto Matera Inteligente</strong> · Arquitectura Hexagonal (Puertos y Adaptadores) · <strong>Estudiante:</strong> Esteban Castro · <strong>Semestre:</strong> 2026-2 · <strong>Tecnologías:</strong> Python 3.14, Flask, SQLite, PyJWT, Werkzeug, pytest</p>
</div>

## 1. Diagrama Hexagonal del Sistema

Para la segunda fase de SmartPlantBase estructuramos la aplicación mediante el patrón de **Puertos y Adaptadores (Alistair Cockburn, 2005)**. El objetivo principal es aislar la lógica botánica y las reglas de negocio de cualquier detalle tecnológico: protocolos de transporte, frameworks web, controladores de persistencia o mecanismos criptográficos.

La Figura 1 ilustra la vista de referencia de nuestra arquitectura, reflejando con exactitud los paquetes, casos de uso atómicos, puertos segregados y adaptadores implementados en el código:

<div class="figure-container">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 380" width="100%" height="auto" style="max-height: 250px; font-family: 'Liberation Sans', -apple-system, sans-serif;">
  <defs>
    <style>
      .bg-card { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.1; rx: 4px; }
      .bg-zone-entry { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1.2; stroke-dasharray: 4,3; rx: 6px; }
      .bg-zone-exit { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1.2; stroke-dasharray: 4,3; rx: 6px; }
      .bg-core { fill: #f1f5f9; stroke: #0f172a; stroke-width: 1.7; rx: 7px; }
      .bg-port-in { fill: #e0e7ff; stroke: #4f46e5; stroke-width: 1; rx: 4px; }
      .bg-port-out { fill: #fef3c7; stroke: #d97706; stroke-width: 1; rx: 4px; }
      .bg-sec { fill: #fef2f2; stroke: #dc2626; stroke-width: 1; rx: 4px; }
      .title-zone { font-size: 9.5px; font-weight: 700; text-transform: uppercase; fill: #475569; }
      .title-core { font-size: 11.5px; font-weight: 800; text-transform: uppercase; fill: #0f172a; }
      .card-title { font-size: 9.5px; font-weight: 700; fill: #1e293b; }
      .card-sub { font-size: 8.3px; font-weight: 600; fill: #475569; }
      .card-text { font-size: 7.7px; fill: #334155; }
      .badge-in { font-size: 8.3px; font-weight: 700; fill: #3730a3; }
      .badge-out { font-size: 8.3px; font-weight: 700; fill: #92400e; }
      .arrow { stroke: #64748b; stroke-width: 1.2; fill: none; marker-end: url(#arrow-h); }
      .arrow-accent { stroke: #4f46e5; stroke-width: 1.3; fill: none; marker-end: url(#arrow-ha); }
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
  <rect x="10" y="8" width="225" height="364" class="bg-zone-entry" />
  <text x="20" y="24" class="title-zone">Adaptadores de Entrada (Driving)</text>

  <rect x="18" y="32" width="209" height="100" class="bg-card" />
  <text x="26" y="46" class="card-title">api_front.py (REST Flask)</text>
  <text x="26" y="58" class="card-sub">• Interfaz Web y Consultas</text>
  <text x="26" y="70" class="card-text">POST /api/v1/diagnosticos (R1) · Especies</text>
  <text x="26" y="82" class="card-text">POST /api/auth/login · registro (R7)</text>
  <text x="26" y="94" class="card-text">GET  /api/plantas/{id}/estado (R5, R6)</text>
  <text x="26" y="106" class="card-text">GET  /api/plantas/{id}/historial (R5)</text>
  <text x="26" y="118" class="card-text">GET/POST /api/plantas · Token disp. (R7)</text>

  <rect x="18" y="138" width="209" height="74" class="bg-card" />
  <text x="26" y="153" class="card-title">api_dispositivos.py (REST)</text>
  <text x="26" y="165" class="card-sub">• Telemetría Sensores IoT (ESP32)</text>
  <text x="26" y="178" class="card-text">POST /api/dispositivos/{id}/lecturas (R2)</text>
  <text x="26" y="190" class="card-text">Alimentado por simulador_esp32.py (R3)</text>
  <text x="26" y="202" class="card-text">Bearer Token con scope="dispositivo"</text>

  <rect x="18" y="218" width="209" height="76" class="bg-sec" />
  <text x="26" y="233" class="card-title" fill="#991b1b">seguridad.py / verificador_jwt.py</text>
  <text x="26" y="246" class="card-text">• Decoradores: @requiere_jwt_usuario</text>
  <text x="26" y="258" class="card-text">  y @requiere_jwt_dispositivo</text>
  <text x="26" y="270" class="card-text">• Valida firma PyJWT y filtra scope</text>
  <text x="26" y="282" class="card-text">• Entrega sujeto verificado al caso de uso</text>

  <rect x="18" y="300" width="209" height="62" class="bg-card" />
  <text x="26" y="316" class="card-title">tests/test_dominio.py</text>
  <text x="26" y="329" class="card-sub">• Pruebas Unitarias del Dominio</text>
  <text x="26" y="342" class="card-text">Inyección de dobles en memoria (fakes.py)</text>
  <text x="26" y="354" class="card-text">Ejecución 100% aislada sin base ni red</text>

  <!-- ZONE 2: NÚCLEO HEXAGONAL -->
  <rect x="246" y="8" width="418" height="364" class="bg-core" />
  <text x="355" y="25" class="title-core">Núcleo de Dominio y Puertos</text>

  <rect x="256" y="32" width="398" height="64" class="bg-port-in" />
  <text x="264" y="46" class="badge-in">PUERTOS DE ENTRADA (matera/dominio/puertos/entrada.py)</text>
  <text x="264" y="59" class="card-text">• ValidarLecturaPort · ConsultarEspeciesPort (R1: diagnóstico y catálogo)</text>
  <text x="264" y="71" class="card-text">• RegistrarLecturaPort (R2, R5) · ConsultarEstadoPort · ConsultarHistorialPort (R5)</text>
  <text x="264" y="83" class="card-text">• ListarPlantasPort · RegistrarPlantaPort · EmitirTokenDispositivoPort · AutenticarUsuarioPort (R7)</text>

  <rect x="256" y="102" width="398" height="162" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1" rx="5px" />
  <text x="264" y="117" class="card-title">Dominio Puro y Casos de Uso Atómicos (matera/dominio/)</text>
  <text x="264" y="131" class="card-sub">Casos de Uso Atómicos (casos_uso/):</text>
  <text x="272" y="144" class="card-text">• ValidarLectura · ConsultarEspecies · RegistrarLectura · ConsultarEstado</text>
  <text x="272" y="156" class="card-text">• ConsultarHistorial · ListarPlantas · RegistrarPlanta · EmitirTokenDispositivo · AutenticarUsuario</text>
  <text x="264" y="171" class="card-sub">Regla de Propiedad Botánica (casos_uso/propiedad.py):</text>
  <text x="272" y="184" class="card-text">• obtener_planta_del_usuario() valida: planta.pertenece_a(usuario_id)</text>
  <text x="264" y="199" class="card-sub">Entidades y Validador (modelo.py / validador.py):</text>
  <text x="272" y="212" class="card-text">• Lectura, Especie, Planta, Usuario, Diagnostico · ValidadorDeEstado</text>
  <text x="264" y="228" class="card-sub" fill="#047857">Invariante: Cero imports de Flask, SQL, CSV, JSON o PyJWT</text>
  <text x="264" y="241" class="card-text" fill="#64748b">Excepciones botánicas: AccesoNoAutorizadoPlantaError, EspecieNoSoportadaError...</text>
  <text x="264" y="253" class="card-text" fill="#475569">Cada caso de uso recibe solo los puertos que necesita (DIP + ISP)</text>

  <rect x="256" y="270" width="398" height="92" class="bg-port-out" />
  <text x="264" y="284" class="badge-out">PUERTOS DE SALIDA (matera/dominio/puertos/salida.py)</text>
  <text x="264" y="298" class="card-text">• TablaReferenciaPort: consulta catálogo botánico y rangos óptimos (R4)</text>
  <text x="264" y="311" class="card-text">• HistorialLecturasPort: persistencia de lecturas y consulta de última medición (R5)</text>
  <text x="264" y="324" class="card-text">• UsuariosPort: persistencia y búsqueda de usuarios por email/id (R7)</text>
  <text x="264" y="337" class="card-text">• PlantasPort: persistencia de plantas y relación sensor-dispositivo (R7)</text>
  <text x="264" y="350" class="card-text">• EmisorTokenPort: firma de JWT · HasherContrasenaPort: hashing seguro (R7)</text>

  <!-- ZONE 3: ADAPTADORES DE SALIDA -->
  <rect x="676" y="8" width="234" height="364" class="bg-zone-exit" />
  <text x="688" y="24" class="title-zone">Adaptadores de Salida (Driven)</text>

  <rect x="686" y="32" width="214" height="66" class="bg-card" />
  <text x="694" y="46" class="card-title">tabla_csv.py / tabla_bd.py</text>
  <text x="694" y="58" class="card-sub">• Implementan TablaReferenciaPort (R4)</text>
  <text x="694" y="70" class="card-text">CsvTablaReferenciaAdapter (CSV)</text>
  <text x="694" y="82" class="card-text">BdTablaReferenciaAdapter (SQLite)</text>
  <text x="694" y="93" class="card-text">Conmutables por TABLA_REFERENCIA_DRIVER</text>

  <rect x="686" y="104" width="214" height="114" class="bg-card" />
  <text x="694" y="119" class="card-title">Adaptadores SQLite (data/matera.db)</text>
  <text x="694" y="131" class="card-sub">• Un adaptador por puerto (R5, R7):</text>
  <text x="694" y="144" class="card-text">historial_bd.py -> BdHistorialLecturasAdapter</text>
  <text x="694" y="156" class="card-text">usuarios_bd.py  -> BdUsuariosAdapter</text>
  <text x="694" y="168" class="card-text">plantas_bd.py   -> BdPlantasAdapter</text>
  <text x="694" y="181" class="card-sub">• Infraestructura compartida (sqlite_bd.py):</text>
  <text x="694" y="193" class="card-text">conectar() con contextmanager y rollback</text>
  <text x="694" y="205" class="card-text">inicializar_bd() ejecuta esquema y demo</text>

  <rect x="686" y="224" width="214" height="82" class="bg-card" />
  <text x="694" y="239" class="card-title">Seguridad e Infraestructura (R7)</text>
  <text x="694" y="252" class="card-text">emisor_jwt.py -> JwtEmisorTokenAdapter</text>
  <text x="694" y="264" class="card-text">  (Firma HS256 con PyJWT)</text>
  <text x="694" y="277" class="card-text">hasher_werkzeug.py -> WerkzeugHasherAdapter</text>
  <text x="694" y="290" class="card-text">  (Hashing scrypt seguro con Werkzeug)</text>

  <rect x="686" y="312" width="214" height="50" fill="#e2e8f0" stroke="#64748b" stroke-width="1" rx="4px" />
  <text x="694" y="326" class="card-title" font-size="9px">matera/app.py (Composition Root)</text>
  <text x="694" y="338" class="card-text">Carga .env, inicializa DB, crea adaptadores e</text>
  <text x="694" y="350" class="card-text">inyecta dependencias en cada caso de uso</text>

  <!-- CONEXIONES -->
  <path d="M 227 75 L 256 60" class="arrow" />
  <path d="M 227 175 L 256 70" class="arrow-accent" />
  <path d="M 227 330 L 256 80" class="arrow" />

  <path d="M 654 295 L 686 65" class="arrow" />
  <path d="M 654 320 L 686 160" class="arrow" />
  <path d="M 654 345 L 686 265" class="arrow" />
</svg>
<div class="figure-caption">Figura 1. Vista hexagonal del sistema con adaptadores, puertos segregados, casos de uso atómicos y el Composition Root.</div>
</div>

El flujo de dependencias apunta siempre hacia adentro:
- **Adaptadores de entrada (primarios):** Traducen estímulos del exterior a invocaciones de los puertos de entrada. El módulo `api_front.py` atiende solicitudes web del usuario y `api_dispositivos.py` recibe la telemetría periódica del ESP32. El filtro `seguridad.py` valida tokens y entrega identidades limpias.
- **Núcleo de dominio:** Agrupa casos de uso atómicos (`matera/dominio/casos_uso/`), entidades botánicas (`Lectura`, `Especie`, `Planta`, `Usuario`, `Diagnostico`) y evaluadores de reglas (`ValidadorDeEstado`). No contiene librerías externas ni referencias a HTTP o SQL.
- **Adaptadores de salida (secundarios):** Implementan los puertos de salida para interactuar con la infraestructura: almacenamiento especializado en SQLite (`historial_bd.py`, `usuarios_bd.py`, `plantas_bd.py`), catálogo botánico (`tabla_csv.py`, `tabla_bd.py`), firma de tokens (`emisor_jwt.py`) y hash criptográfico (`hasher_werkzeug.py`).

<div class="page-break"></div>

## 2. Tabla de Puertos y Adaptadores

Los puertos desacoplan el núcleo mediante contratos explícitos en `matera/dominio/puertos/` (`entrada.py` y `salida.py`). Cada caso de uso atómico implementa un puerto de entrada, y cada adaptador satisface un puerto de salida:

| Puerto (Contrato) | Tipo | Adaptador Concreto / Implementación | Responsabilidad en el Negocio |
| :--- | :---: | :--- | :--- |
| **ValidarLecturaPort** | Entrada | `ValidarLectura` *(invocado por `api_front`)* | Evalúa lecturas manuales contra los rangos de la especie (R1). |
| **ConsultarEspeciesPort** | Entrada | `ConsultarEspecies` *(invocado por `api_front`)* | Provee catálogo de especies para selectores de la interfaz web (R1). |
| **RegistrarLecturaPort** | Entrada | `RegistrarLectura` *(invocado por `api_dispositivos`)* | Procesa telemetría ESP32, evalúa estado botánico y persiste (R2, R5). |
| **ConsultarEstadoPort** | Entrada | `ConsultarEstado` *(invocado por `api_front`)* | Retorna última lectura y diagnóstico validando propiedad (R5, R6, R7). |
| **ConsultarHistorialPort** | Entrada | `ConsultarHistorial` *(invocado por `api_front`)* | Retorna serie temporal histórica de la planta del usuario (R5, R7). |
| **ListarPlantasPort** | Entrada | `ListarPlantas` *(invocado por `api_front`)* | Lista las plantas registradas del usuario autenticado (R7). |
| **RegistrarPlantaPort** | Entrada | `RegistrarPlanta` *(invocado por `api_front`)* | Registra planta, vincula sensor y genera token inicial de dispositivo (R7). |
| **EmitirTokenDispositivoPort** | Entrada | `EmitirTokenDispositivo` *(invocado por `api_front`)* | Permite al dueño reemitir la credencial JWT de su ESP32 (R7). |
| **AutenticarUsuarioPort** | Entrada | `AutenticarUsuario` *(invocado por `api_front`)* | Registro, login, validación de hash y emisión de JWT de sesión (R7). |
| **TablaReferenciaPort** | Salida | `CsvTablaReferenciaAdapter` / `BdTablaReferenciaAdapter` | Catálogo botánico. Conmutable por `TABLA_REFERENCIA_DRIVER` (R4). |
| **HistorialLecturasPort** | Salida | `BdHistorialLecturasAdapter` (`historial_bd.py`) | Persistencia y consulta histórica de lecturas en SQLite (R5). |
| **UsuariosPort** | Salida | `BdUsuariosAdapter` (`usuarios_bd.py`) | Almacenamiento y búsqueda de usuarios en SQLite (R7). |
| **PlantasPort** | Salida | `BdPlantasAdapter` (`plantas_bd.py`) | Persistencia de plantas y relación planta-sensor en SQLite (R7). |
| **EmisorTokenPort** | Salida | `JwtEmisorTokenAdapter` (`emisor_jwt.py`) | Firma de tokens JWT HS256 con scopes segregados (R7). |
| **HasherContrasenaPort** | Salida | `WerkzeugHasherAdapter` (`hasher_werkzeug.py`) | Generación y verificación de hashes criptográficos scrypt (R7). |

## 3. Manejo de Seguridad, Alcances de JWT y Regla de Propiedad

La autenticación y autorización protegen el sistema en el perímetro sin invadir el núcleo del dominio:

- **Segregación de Alcances (User vs Device):** El claim `scope` define dos tipos de token disyuntos. El **token de usuario** (`scope="usuario"`), emitido en `/api/auth/login`, autoriza la consulta y gestión de plantas propias. El **token de dispositivo** (`scope="dispositivo"`), asignado al ESP32, autoriza únicamente el reporte de telemetría en `POST /api/dispositivos/{id}/lecturas`.
- **Puntos de Emisión y Verificación:** La emisión se delega al puerto de salida `EmisorTokenPort` (`JwtEmisorTokenAdapter` en `emisor_jwt.py`, único punto con `PyJWT`). La verificación perimetral ocurre en `seguridad.py` (`JwtVerificadorToken`), donde `@requiere_jwt_usuario` y `@requiere_jwt_dispositivo` rechazan con HTTP 403 Forbidden cualquier intento de cruzar alcances antes de invocar al dominio.
- **Aislamiento del Dominio:** El dominio desconoce JWT y encabezados HTTP. El filtro perimetral extrae la identidad limpia (`usuario_id` o `dispositivo_id`) y la pasa como argumento, permitiendo probar el dominio con dobles en memoria sin claves criptográficas.
- **Regla de Propiedad en el Dominio:** La verificación de pertenencia es una regla de negocio y reside en el dominio:
```python
# matera/dominio/casos_uso/propiedad.py
def obtener_planta_del_usuario(plantas: PlantasPort, usuario_id: str, planta_id: str) -> Planta:
    planta = plantas.obtener_planta_por_id(planta_id)
    if planta is None: raise PlantaNoEncontradaError(planta_id)
    if not planta.pertenece_a(usuario_id): raise AccesoNoAutorizadoPlantaError(usuario_id, planta_id)
    return planta
```
Tanto `ConsultarEstado` como `ConsultarHistorial` utilizan esta función. Si un usuario intenta acceder a una planta ajena, el dominio lanza `AccesoNoAutorizadoPlantaError`, y la capa HTTP (`errores_http.py`) responde con HTTP 403 (`ACCESO_DENEGADO`).

<div class="page-break"></div>

## 4. Justificación de Principios SOLID en el Código

La estructura modular y atómica del proyecto aplica rigurosamente los principios de diseño orientado a objetos:

- **Inversión de Dependencias (DIP):** El núcleo de dominio no depende de bibliotecas externas ni de adaptadores concretos; depende exclusivamente de abstracciones (puertos). Por ejemplo, el caso de uso `RegistrarLectura` recibe interfaces abstractas (`TablaReferenciaPort`, `PlantasPort`, `HistorialLecturasPort`):
```python
# matera/dominio/casos_uso/registrar_lectura.py
class RegistrarLectura(RegistrarLecturaPort):
    def __init__(self, tabla_referencia: TablaReferenciaPort, plantas: PlantasPort, historial: HistorialLecturasPort):
        self._tabla_referencia = tabla_referencia
        self._plantas = plantas
        self._historial = historial
```
Ni los casos de uso ni el evaluador botánico importan `sqlite3`, `csv`, `flask` o `jwt`.
- **Abierto/Cerrado (OCP):** El sistema permite incorporar nuevas fuentes o canales mediante la adición de adaptadores, manteniendo el dominio cerrado a modificaciones. Al añadir la telemetría del ESP32 (R2) y el simulador (R3), únicamente construimos `api_dispositivos.py` y `simulador_esp32.py`; el evaluador botánico no requirió ajustes. Igualmente, alternar entre catálogo CSV y SQLite (R4) se resuelve en el Composition Root (`matera/app.py`) sin tocar una sola línea de lógica de negocio.
- **Segregación de Interfaces (ISP):** Refactorizamos los antiguos puertos monolíticos en contratos atómicos y especializados. En lugar de un puerto sobrecargado, existen interfaces pequeñas y enfocadas: `UsuariosPort`, `PlantasPort`, `HistorialLecturasPort`, `TablaReferenciaPort`, `EmisorTokenPort` y `HasherContrasenaPort`. Cada caso de uso recibe únicamente los puertos que consume; por ejemplo, `ListarPlantas` solo recibe `PlantasPort`, permaneciendo completamente ajeno a contraseñas, tokens, historiales o catálogos.
- **Responsabilidad Única (SRP):** Cada clase tiene una única razón de cambio. Cada caso de uso atómico (`ValidarLectura`, `ConsultarEstado`, etc.) orquesta exactamente una operación del negocio. En la infraestructura, cada adaptador SQLite (`usuarios_bd.py`, `plantas_bd.py`, `historial_bd.py`) responde únicamente al esquema relacional de su entidad, y la infraestructura común de conexión reside en `sqlite_bd.py`.

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
git diff 8c4b6d8~1 8c4b6d8 -- matera/dominio/ matera/dominio/puertos/
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
   - Se instancia el nuevo adaptador `suscriptor_mqtt` pasándole la misma instancia existente de `registrar_lectura` (que implementa `RegistrarLecturaPort`).
   - Se inicia el bucle de red del cliente MQTT en segundo plano (`client.loop_start()`).
2. **Dependencias del proyecto (`requirements.txt`):**
   - Se añade la dependencia del cliente MQTT (`paho-mqtt`).

### Componentes que Permanecen Intactos
- **Núcleo de dominio (`matera/dominio/*`):** `modelo.py`, `validador.py`, `casos_uso/` y `excepciones.py` no requieren ningún cambio. El caso de uso `RegistrarLectura` desconoce por completo si las lecturas provinieron de un paquete TCP, un socket MQTT o una petición HTTP.
- **Puertos de entrada y salida (`matera/dominio/puertos/*`):** `RegistrarLecturaPort` conserva su firma agnóstica (`dispositivo_id: str`, `valores: Mapping`, `marca_tiempo: str`), ya que fue diseñado pensando en el caso de uso y no en el protocolo.
- **Adaptadores de salida (`matera/adaptadores/salida/*`):** La persistencia en SQLite (`historial_bd.py`), la consulta de plantas (`plantas_bd.py`) y el catálogo (`tabla_csv.py` / `tabla_bd.py`) se ejecutan exactamente igual.

---

## 7. Conclusión y Síntesis de la Arquitectura

La adopción de arquitectura hexagonal con casos de uso atómicos y puertos segregados en esta segunda fase de SmartPlantBase resuelve el desacoplamiento entre las reglas botánicas y la tecnología externa. Al aislar la autenticación y validación de tokens en los adaptadores primarios, atomizar la persistencia SQLite en adaptadores especializados y centralizar la regla de propiedad en el dominio puro, logramos un sistema robusto, testeable al 100% en memoria con dobles y preparado para admitir nuevos protocolos de transporte (como MQTT) sin deuda técnica.
