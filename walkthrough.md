# Recorrido de Implementación y Verificación (Walkthrough)

## Resumen del Proyecto Completado
Se implementó de manera íntegra el núcleo de servicio de diagnóstico ambiental para la **Matera Inteligente**, satisfaciendo cada una de las restricciones no negociables (**RA1–RA8**), requisitos funcionales (**RF1–RF6**), principios **SOLID**, cliente web estático asíncrono y los entregables documentales solicitados en el enunciado del curso.

---

## Historial de Commits Incrementales
El repositorio se construyó paso a paso mediante commits semánticos y organizados por capa/fase (Entregable 6.a):

```
b352e71 docs: agregar README detallado, documento de arquitectura y bitácora de IA
ce12469 feat(frontend): crear cliente web estático asíncrono desacoplado con consumo de API
34bd2f7 feat(presentation): implementar controladores REST, DTOs de borde y manejo uniforme de errores
add99a2 feat(application): implementar casos de uso y DTOs de orquestación
2b952a8 feat(infrastructure): implementar repositorio de especies basado en CSV
84b5368 test(domain): agregar pruebas unitarias de dominio con dobles de prueba
363c557 feat(domain): implementar entidades, reglas de negocio y abstracción de repositorio
5023c9d chore: inicializar repositorio, requerimientos y dataset de referencia
```

---

## Verificación de Restricciones y Requisitos

| ID | Restricción / Requisito | Estado | Evidencia en Código |
| :--- | :--- | :---: | :--- |
| **RA1** | Backend no genera HTML (cero Jinja, solo JSON) | ✅ Cumplido | [controllers.py](file:///home/esteban/Documents/ARQUIT/src/presentation/controllers.py): Todas las rutas responden con `jsonify` y códigos HTTP limpios. Se eliminó todo uso de `render_template`. |
| **RA2** | Frontend estático e independiente asíncrono | ✅ Cumplido | [frontend/index.html](file:///home/esteban/Documents/ARQUIT/frontend/index.html) y [script.js](file:///home/esteban/Documents/ARQUIT/frontend/js/script.js): Cliente estático servido independientemente, sin recargas de página (`e.preventDefault()`), consumiendo la API vía `fetch`. |
| **RA3** | Separación en capas (presentación, aplicación, dominio, infraestructura) | ✅ Cumplido | Estructura en `src/presentation/`, `src/application/`, `src/domain/` y `src/infrastructure/`. |
| **RA4** | Dominio agnóstico a frameworks y persistencia | ✅ Cumplido | [src/domain/](file:///home/esteban/Documents/ARQUIT/src/domain/): Cero dependencias externas (solo Python stdlib). Las pruebas [test_domain_rules.py](file:///home/esteban/Documents/ARQUIT/tests/test_domain_rules.py) pasan sin servidor y sin leer CSV ni base de datos. |
| **RA5** | Abstracción en dominio (interfaz / puerto) e implementación en infraestructura | ✅ Cumplido | [EspecieRepository](file:///home/esteban/Documents/ARQUIT/src/domain/repositories.py#L10) declarado en Dominio; [CsvEspecieRepository](file:///home/esteban/Documents/ARQUIT/src/infrastructure/repositories/csv_especie_repository.py#L13) implementado en Infraestructura (DIP). |
| **RA6** | Validación y transformación en el borde (DTOs) | ✅ Cumplido | [controllers.py](file:///home/esteban/Documents/ARQUIT/src/presentation/controllers.py#L27-L67): El controlador valida tipos y presencia y construye `DiagnosticoInputDTO`. El dominio nunca recibe un `request` ni un diccionario crudo. |
| **RA7** | CORS configurado para orígenes cruzados | ✅ Cumplido | [app.py](file:///home/esteban/Documents/ARQUIT/app.py#L23): `CORS(app, resources={r"/api/*": {"origins": "*"}})`. |
| **RA8** | Stack Python con Flask | ✅ Cumplido | Implementado en Python 3.14 con Flask 3.1.3 y `flask-cors`. |
| **RF1-RF4** | Evaluación, agregación global (índice de vitalidad) y recomendaciones | ✅ Cumplido | [rules.py](file:///home/esteban/Documents/ARQUIT/src/domain/rules.py#L62-L110): Clasifica parámetros, deriva estado (`SALUDABLE`, `EN_RIESGO`, `CRITICO`) y genera recomendaciones específicas por desviación. |
| **RF5** | Catálogo de especies y rangos de referencia | ✅ Cumplido | Endpoint `GET /api/v1/especies` y caso de uso `ListarEspeciesUseCase`. |
| **RF6** | Manejo uniforme de errores (400, 404, 500) | ✅ Cumplido | [error_handlers.py](file:///home/esteban/Documents/ARQUIT/src/presentation/error_handlers.py): Estructura estándar `{"error": "...", "mensaje": "...", "detalle": {...}}`. |

---

## Resultados de Pruebas Automatizadas
Se ejecutaron un total de **18 pruebas automatizadas** que cubren todas las capas:

```bash
$ ./venv/bin/pytest -v
============================= test session starts ==============================
tests/test_api_endpoints.py::test_endpoint_listar_especies PASSED        [  5%]
tests/test_api_endpoints.py::test_endpoint_evaluar_diagnostico_exitoso PASSED [ 11%]
tests/test_api_endpoints.py::test_endpoint_evaluar_diagnostico_con_desviacion_y_recomendaciones PASSED [ 16%]
tests/test_api_endpoints.py::test_endpoint_evaluar_error_especie_desconocida PASSED [ 22%]
tests/test_api_endpoints.py::test_endpoint_evaluar_error_parametro_ausente PASSED [ 27%]
tests/test_api_endpoints.py::test_endpoint_evaluar_error_valor_no_numerico PASSED [ 33%]
tests/test_api_endpoints.py::test_endpoint_evaluar_error_valor_fisicamente_imposible PASSED [ 38%]
tests/test_domain_rules.py::test_planta_saludable_con_todos_los_parametros_en_rango_optimo PASSED [ 44%]
tests/test_domain_rules.py::test_un_parametro_bajo_deriva_en_riesgo_con_recomendacion PASSED [ 50%]
tests/test_domain_rules.py::test_un_parametro_alto_deriva_en_riesgo_con_recomendacion PASSED [ 55%]
tests/test_domain_rules.py::test_multiples_parametros_desviados_derivan_estado_critico PASSED [ 61%]
tests/test_domain_rules.py::test_medicion_con_humedad_fisicamente_imposible_lanza_error PASSED [ 66%]
tests/test_domain_rules.py::test_medicion_con_luz_o_temperatura_imposibles_lanza_error PASSED [ 72%]
tests/test_domain_rules.py::test_doble_de_prueba_sustituible_y_aislamiento_total PASSED [ 77%]
tests/test_infrastructure.py::test_csv_especie_repository_carga_especies_anexo_b PASSED [ 83%]
tests/test_use_cases.py::test_evaluar_diagnostico_use_case_exitoso PASSED [ 88%]
tests/test_use_cases.py::test_evaluar_diagnostico_use_case_especie_no_soportada PASSED [ 94%]
tests/test_use_cases.py::test_listar_especies_use_case PASSED            [100%]
============================== 18 passed in 0.10s ==============================
```

---

## Preparación para Preguntas de Sustentación (Sección 7 del Enunciado)

1. **"Mañana el dato llega por MQTT desde un ESP32 en lugar de por HTTP. ¿Qué archivos cambias y cuáles garantizas que no se tocan?"**
   - *Se cambia/agrega:* Se agrega un adaptador en `src/presentation/mqtt_subscriber.py` y se inicializa en `app.py`.
   - *Garantizo que NO se tocan:* Toda la capa de dominio (`src/domain/*`) y la capa de aplicación (`src/application/*`). El caso de uso `EvaluarDiagnosticoUseCase` recibe el mismo DTO sin enterarse de si provino de HTTP o MQTT.
2. **"La tabla de referencia pasa de CSV a PostgreSQL. Muéstrame la clase que tendrías que escribir y la línea exacta donde se conecta."**
   - *Se escribe:* `PostgresEspecieRepository` en `src/infrastructure/repositories/postgres_especie_repository.py` implementando `EspecieRepository`.
   - *Línea exacta donde se conecta:* En [app.py:L33](file:///home/esteban/Documents/ARQUIT/app.py#L33): `especie_repository = PostgresEspecieRepository(db_url)` en lugar de `CsvEspecieRepository(ruta_csv)`.
3. **"Se agrega un cuarto parámetro, el pH del sustrato. ¿Cuántos archivos modificas? ¿Por qué no menos?"**
   - *Archivos modificados:*
     1. [src/domain/entities.py](file:///home/esteban/Documents/ARQUIT/src/domain/entities.py): agregar el campo `ph` en `Medicion` y su rango en `Especie`.
     2. [src/domain/rules.py](file:///home/esteban/Documents/ARQUIT/src/domain/rules.py): agregar la tupla `("ph", medicion.ph, especie.rango_ph)` en la lista de evaluación de `EvaluadorDiagnostico`.
     3. [data/especies_referencia.csv](file:///home/esteban/Documents/ARQUIT/data/especies_referencia.csv) y [csv_especie_repository.py](file:///home/esteban/Documents/ARQUIT/src/infrastructure/repositories/csv_especie_repository.py): para leer las columnas `ph_min` y `ph_max`.
     4. [src/application/dtos.py](file:///home/esteban/Documents/ARQUIT/src/application/dtos.py) y [src/presentation/controllers.py](file:///home/esteban/Documents/ARQUIT/src/presentation/controllers.py): para recibir y validar `ph` en el JSON.
     5. [frontend/index.html](file:///home/esteban/Documents/ARQUIT/frontend/index.html): para agregar el input en el formulario.
   - *Por qué no menos:* Porque el sistema está organizado en capas con tipado y contratos explícitos; un nuevo parámetro físico requiere viajar desde la captura en la interfaz hasta el cálculo del dominio.
4. **"¿En qué capa pondrías la gamificación y por qué no en el dominio de la planta?"**
   - En un módulo/servicio de aplicación independiente (`src/gamification/`) escuchando eventos de dominio (`DiagnosticoGeneradoEvent`).
   - *Por qué no en el dominio de la planta:* Porque la salud biológica de una planta es ajena al concepto de "puntos", "rachas" o "medallas" del usuario. Mezclarlos violaría el principio de Responsabilidad Única (SRP) y acoplaría el modelo botánico con la experiencia lúdica del usuario.
5. **"Señálame en tu código la línea donde un objeto del dominio deja de saber que existe HTTP."**
   - En [src/presentation/controllers.py:L57-L65](file:///home/esteban/Documents/ARQUIT/src/presentation/controllers.py#L57-L65): Allí se extraen los datos de la petición HTTP, se valida que existan y sean números, y se crea un `DiagnosticoInputDTO`. El caso de uso y el dominio nunca reciben el objeto `request` de Flask.
6. **"Si borro la carpeta de infraestructura, ¿compilan/pasan tus pruebas de dominio?"**
   - Sí, pasan al 100%. Ejecutar: `pytest tests/test_domain_rules.py -v`.
   - Las pruebas de dominio no importan nada de `src.infrastructure`; utilizan el doble de prueba `FakeEspecieRepository` implementado localmente en la suite de pruebas.

---

## Entregables Generados
1. Código fuente del backend en capas: `src/domain/`, `src/application/`, `src/infrastructure/`, `src/presentation/`, `app.py`.
2. Pruebas unitarias de dominio y de integración: `tests/`.
3. Cliente web estático desacoplado: `frontend/index.html`, `frontend/css/style.css`, `frontend/js/script.js`.
4. Dataset de especies: `data/especies_referencia.csv`.
5. Guía de ejecución del proyecto: `README.md`.
6. Documento de arquitectura: `docs/documento_arquitectura.md`.
7. Bitácora de uso de IA: `docs/bitacora_ia.md`.
