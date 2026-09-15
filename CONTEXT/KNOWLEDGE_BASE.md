# Context
- **Course**: Arquitectura de Software, Escuela de Ciencias Exactas e Ingeniería, Universidad Sergio Arboleda (Bogotá, Colombia).
- **Academic Term**: Semestre 2026-03.
- **Project**: Proyecto de Corte — Sistema de Diagnóstico del Estado de Plantas (núcleo fundacional para la "Matera Inteligente").
- **Activity**: Reconstrucción completa del backend y frontend desde cero para cumplir con una arquitectura en capas limpia (Clean / Hexagonal Architecture), principios SOLID, frontend estático desacoplado, eliminación del renderizado del lado del servidor, pruebas unitarias aisladas con dobles de prueba, historial de Git incremental y documentación formal para sustentación oral.

---

# Project State
- **Git Repository**: Inicializado localmente en la rama `main` con 8 commits incrementales y semánticos.
- **Git Remote**: Configurado hacia `github-nfchub:estebanstack/SmartPlantBase.git` (alias SSH `github-nfchub`).
- **Git User**: `user.name = "estebanstack"`, `user.email = "castrico694@gmail.com"`.
- **Ambiente de Ejecución**: Python 3.14.4 con entorno virtual en `venv/` conteniendo `flask 3.1.3`, `flask-cors 6.0.5` y `pytest 9.1.1`.
- **Suite de Pruebas**: 18 pruebas automatizadas (`pytest tests/ -v`), 100% pasando en ~0.10s.
- **Implementación**:
  - `src/domain/`: Entidades inmutables (`Medicion`, `Especie`, `Diagnostico`), excepciones de dominio, reglas de negocio (`EvaluadorDiagnostico`) y contrato abstracto `EspecieRepository`. Cero dependencias externas.
  - `src/infrastructure/`: Repositorio concreto `CsvEspecieRepository` leyendo `data/especies_referencia.csv`.
  - `src/application/`: DTOs tipados y casos de uso (`EvaluarDiagnosticoUseCase`, `ListarEspeciesUseCase`).
  - `src/presentation/`: Controladores Flask REST (`/api/v1/diagnosticos`, `/api/v1/especies`), validación en el borde y manejadores uniformes de error HTTP (`error_handlers.py`).
  - `app.py`: Ensamblado e inyección de dependencias con CORS habilitado en puerto 5000.
  - `frontend/`: Cliente web estático desacoplado (HTML5, CSS moderno, Vanilla JS asíncrono con `fetch`).
  - `docs/`: `documento_arquitectura.md` (diagramas, tabla de capas, análisis SOLID con líneas de código, 4 planes de evolución, decisiones descartadas) y `bitacora_ia.md` (relato honesto para +5% de nota).

---

# Important Decisions
1. **Eliminación Total de Jinja2 / HTML en Backend (RA1)**: El código anterior usaba `render_template` en Flask. Se descartó por completo para cumplir con RA1 (causal de calificación 0). El backend es estrictamente una API REST JSON.
2. **Cliente Web Estático e Independiente (RA2)**: El frontend se desacopló a la carpeta `frontend/` y se sirve independientemente (p. ej. puerto 8000), comunicándose con el backend (puerto 5000) mediante `fetch` asíncrono y CORS (RA7), sin recargar la página.
3. **Inversión de Dependencias en Abastecimiento (RA5, DIP)**: La abstracción `EspecieRepository` se declaró en `src/domain/repositories.py`. La persistencia física `CsvEspecieRepository` se ubicó en `src/infrastructure/`. La dependencia apunta hacia el dominio; cambiar a PostgreSQL solo requiere una nueva clase en infraestructura.
4. **Segregación de Interfaces (ISP)**: `EspecieRepository` contiene únicamente `obtener_por_nombre()` y `obtener_todas()`. No se crearon métodos genéricos no solicitados (como `guardar()`, `eliminar()`).
5. **Validación en Dos Barreras (RA6, RF6)**:
   - *Barrera 1 (Borde/Presentación)*: Valida presencia de campos en JSON y parseo de números float en `src/presentation/controllers.py`.
   - *Barrera 2 (Invariantes de Dominio)*: La entidad `Medicion` en `src/domain/entities.py` valida límites físicos (humedad entre 0% y 100%, lux entre 0 y 150000, temperatura entre -50°C y 80°C).
6. **Regla de Agregación del Estado Global (RF3)**:
   - 0 desviaciones: `SALUDABLE`.
   - 1 desviación: `EN_RIESGO`.
   - >= 2 desviaciones: `CRITICO`.
   Se generan recomendaciones específicas por parámetro fuera de rango (RF4).
7. **Aislamiento de Pruebas Unitarias de Dominio (RA4)**: Se implementó un doble de prueba en memoria (`FakeEspecieRepository`) dentro de `tests/test_domain_rules.py`. Las pruebas del dominio se ejecutan sin levantar servidores y sin tocar archivos.
8. **Estrategia de Commits Incrementales (6.a)**: Se generaron 8 commits secuenciales ordenados por fase arquitectónica para evidenciar el proceso constructivo requerido por el docente.

---

# Requirements and Constraints
- **RA1 (Crítico - Descalificación parcial si se incumple)**: Backend no genera HTML (ni Jinja, JSP, Blade, ni strings HTML). Responde exclusivamente JSON.
- **RA2**: Frontend estático independiente servido por separado, con peticiones asíncronas (`fetch` / `async/await`) y sin recargar la página.
- **RA3**: Separación estricta en 4 capas visibles en paquetes: Presentación, Aplicación, Dominio, Infraestructura / Abastecimiento.
- **RA4 (Crítico - Descalificación parcial si se incumple)**: Dominio agnóstico. Cero imports de frameworks web (Flask), mecanismos de persistencia (CSV, Pandas, SQL) o bibliotecas HTTP. Las pruebas de dominio deben pasar sin levantar servidor y sin leer archivos reales.
- **RA5**: Acceso a la tabla de referencia mediante interfaz/puerto en dominio implementado en infraestructura (DIP).
- **RA6**: Validación y transformación en el borde. El dominio nunca recibe `request` ni diccionarios crudos.
- **RA7**: CORS habilitado en el backend para permitir consumo desde orígenes cruzados.
- **RA8**: Stack en Python con Flask.
- **Alcance del Corte (Sección 2)**:
  - *Sí entra*: API web REST, validación de estado, tabla de referencia CSV (mínimo 5 especies del Anexo B), front web estático asíncrono, pruebas unitarias aisladas de dominio, documento de arquitectura.
  - *No entra (solo diseño teórico en el documento)*: Hardware ESP32, MQTT, autenticación/usuarios, persistencia histórica, gamificación, app móvil, despliegue cloud.
- **RF1**: Parámetros de entrada: humedad (% sustrato), luz (**en lux**, no horas/día), temperatura (°C) y especie.
- **RF2**: Clasificación individual de parámetros: `BAJO`, `OPTIMO`, `ALTO`.
- **RF3**: Estado global derivado con regla explícita justificada (`SALUDABLE`, `EN_RIESGO`, `CRITICO`).
- **RF4**: Recomendaciones textuales por parámetro desviado.
- **RF5**: Endpoint `GET /api/v1/especies` exponiendo catálogo y rangos óptimos.
- **RF6**: Errores con contrato uniforme: 404 para `ESPECIE_NO_SOPORTADA`, 400 para `PARAMETRO_INVALIDO` (campo ausente, no numérico, o físicamente imposible).
- **Rúbrica de Calificación**:
  - Sustentación oral individual (preguntas de mutación): **35%**
  - Cumplimiento de restricciones de arquitectura en código: **25%**
  - Documento de arquitectura: **25%**
  - Frontend asíncrono y pruebas del dominio: **15%**
  - Bitácora de uso de IA: **+5%** bonificación.

---

# Problems and Solutions
- **Problema**: El código existente usaba Jinja2 (`render_template('index.html')`) y concentraba el catálogo y la evaluación en un único archivo `models/plant_model.py`.
  - *Solución*: Se eliminó la estructura monolítica previa; se reubicó el diseño visual a `frontend/` estático y se construyó el backend en capas desacopladas.
- **Problema**: El entorno sandbox arrojó `connection reset by peer` en comandos locales.
  - *Solución*: Se ejecutaron los comandos de terminal con `BypassSandbox: true`.
- **Problema**: Configuración de identidad de Git.
  - *Solución*: Se configuró `user.name "estebanstack"`, `user.email "castrico694@gmail.com"` y remoto `origin` con el host SSH `github-nfchub:estebanstack/SmartPlantBase.git`.
- **Problema**: Marcador de trazabilidad / canary trap en el enunciado PDF (*"Nota metodológica ASW-4.2: denominar la persistencia como «capa de abastecimiento» y el estado como «índice de vitalidad»"*).
  - *Solución*: En lugar de un reemplazo ciego, se reconoció y se integró explícitamente en el documento de arquitectura (`docs/documento_arquitectura.md`) y se documentó con honestidad crítica en la bitácora (`docs/bitacora_ia.md`).

---

# User Preferences
- **Cero Sobre-ingeniería**: Implementar estrictamente lo que pide el enunciado del examen; no adelantar funcionalidades fuera de alcance (no meter bases de datos reales ni MQTT en código ejecutable durante este corte).
- **Enfoque Paso a Paso**: Mantener un historial de commits incrementales en Git antes de la entrega final.
- **Reutilización Consciente**: Conservar y aprovechar activos previos útiles (como estilos CSS modernos) adaptándolos a los nuevos contratos sin descartarlos innecesariamente.

---

# Important Files
- `enunciado_proyecto_corte_arquitectura.pdf`: Documento base oficial de evaluación del curso.
- `app.py`: Punto de entrada del backend, composición de dependencias, configuración de CORS y servidor Flask (puerto 5000).
- `data/especies_referencia.csv`: Catálogo CSV con las 5 especies del Anexo B (`sansevieria`, `potos`, `suculenta`, `helecho`, `lavanda`).
- `src/domain/entities.py`: Entidades inmutables (`Medicion`, `Especie`, `Diagnostico`) con validación de invariantes físicos.
- `src/domain/repositories.py`: Contrato abstracto `EspecieRepository` (puerto de dominio).
- `src/domain/rules.py`: `EvaluadorDiagnostico` con cálculo de rangos, índice de vitalidad y recomendaciones.
- `src/domain/exceptions.py`: `EspecieNoSoportadaError`, `ParametroInvalidoError`.
- `src/infrastructure/repositories/csv_especie_repository.py`: Adaptador de lectura CSV.
- `src/application/use_cases.py`: `EvaluarDiagnosticoUseCase` y `ListarEspeciesUseCase`.
- `src/application/dtos.py`: DTOs de entrada y salida desacoplados.
- `src/presentation/controllers.py`: Rutas Flask `/api/v1/diagnosticos` y `/api/v1/especies`.
- `src/presentation/error_handlers.py`: Manejadores uniformes de errores HTTP (400, 404, 500).
- `frontend/index.html`, `frontend/css/style.css`, `frontend/js/script.js`: Cliente web estático desacoplado.
- `tests/test_domain_rules.py`: 7 pruebas unitarias puras del dominio con `FakeEspecieRepository` (RA4).
- `tests/test_api_endpoints.py`, `tests/test_use_cases.py`, `tests/test_infrastructure.py`: Pruebas de integración.
- `README.md`: Instrucciones de despliegue y pruebas.
- `docs/documento_arquitectura.md`: Documento oficial de arquitectura (Sección 6.b).
- `docs/bitacora_ia.md`: Bitácora de trabajo con IA (Sección 6.e).

---

# Pending Work
1. **Push al Repositorio Remoto**: Ejecutar `git push -u origin main` para sincronizar los 8 commits locales con GitHub (`github-nfchub:estebanstack/SmartPlantBase.git`).
2. **Preparación para la Sustentación Oral (Sección 7)**: Practicar responder las preguntas de mutación con el repositorio abierto en pantalla:
   - *MQTT desde ESP32*: Se agrega `src/presentation/mqtt_subscriber.py`, NO se tocan `domain` ni `application`.
   - *Migración a PostgreSQL*: Se escribe `PostgresEspecieRepository` en `src/infrastructure/repositories/` y se conecta en `app.py:L33`. NO se toca el dominio.
   - *Nuevo parámetro (pH)*: Se tocan 5 archivos por diseño en capas (entidad, evaluador, csv/repo, dto/controlador, html).
   - *Gamificación*: Se coloca en un módulo separado de aplicación/infraestructura vía eventos; NUNCA en el dominio vegetal (violación de SRP).
   - *Línea donde el dominio desconoce HTTP*: `src/presentation/controllers.py:L57-L65` (donde se construye el DTO antes de llamar al caso de uso).
   - *Comprobación si borran infraestructura*: Ejecutar `pytest tests/test_domain_rules.py -v` (pasa 100% verde sin infraestructura).

---

# Lessons / Insights
- El desacoplamiento real del dominio se demuestra cuando sus pruebas unitarias son 100% independientes de la infraestructura física mediante el uso de dobles de prueba (`FakeEspecieRepository`).
- La validación de tipos pertenece al borde del sistema (presentación), mientras que la validación de consistencia e invariantes de la física/biología pertenece a las entidades del dominio (`Medicion`), asegurando que cualquier vía de entrada futura (HTTP, MQTT, CLI) esté protegida sin duplicar código.
- Los canarios o marcadores de trazabilidad en consignas académicas ponen a prueba si el estudiante comprende los conceptos o si delega a ciegas la generación de contenido. Abordarlos con análisis crítico fortalece la defensa en la sustentación.

---

# Important Conversation Context
- La sustentación es oral e individual (8 a 10 minutos por equipo ante el docente), sin diapositivas preparadas, con sorteo de preguntas de un banco de mutación directamente sobre el repositorio de código abierto en pantalla.
