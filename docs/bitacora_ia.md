# Bitácora de Trabajo con Asistentes de Inteligencia Artificial
**Matera Inteligente · Proyecto de Corte de Arquitectura de Software**
**Semestre 2026-2**

---

### 1. Alcance y rol de la IA en el proyecto
Durante el desarrollo del proyecto, se utilizaron asistentes de inteligencia artificial (incluyendo trabajo con Claude en etapas de implementación y refactorización) como apoyo relevante para la generación de código base, la exploración de soluciones arquitectónicas, la redacción de pruebas unitarias y la depuración de errores.

Las propuestas relevantes fueron revisadas y ajustadas según los requisitos del proyecto antes de integrarse. El equipo fue responsable de las decisiones finales, la integración, las pruebas y de poder explicar y defender la solución.

---

### 2. ¿Qué propuso la IA inicialmente?
Al contrastar la base de código inicial con el enunciado oficial del parcial:
- La IA señaló que el proyecto previo utilizaba `render_template` de Jinja2 en `app.py`, lo cual incumplía directamente la restricción no negociable **RA1** (causal de descalificación en restricciones arquitectónicas).
- Propuso una estructura basada en Clean Architecture dividida en cuatro capas (`domain`, `application`, `infrastructure`, `presentation`), un cliente web estático desacoplado en `frontend/` y pruebas unitarias con dobles en memoria.
- Sugirió organizar el desarrollo de forma secuencial para registrar un historial de Git incremental que evidenciara el proceso constructivo requerido por el entregable 6.a.

---

### 3. ¿Qué propuestas se adoptaron de forma directa?
- **La estructura de paquetes y la inversión de dependencias:** La declaración del contrato abstracto `EspecieRepository` en el dominio y su implementación concreta `CsvEspecieRepository` en la capa de infraestructura se adoptó directamente, ya que cumple con el principio de Inversión de Dependencias (DIP) y la restricción **RA5**.
- **El uso de dobles de prueba:** La implementación de `FakeEspecieRepository` para aislar las pruebas de dominio se adoptó como estrategia principal, permitiendo validar las reglas botánicas en memoria sin levantar servidores ni leer archivos físicos (**RA4**). Posteriormente, se ubicó en `tests/doubles.py` para compartirlo limpiamente entre pruebas.
- **El contrato de datos y respuestas de error uniformes:** La estructura de respuestas para 200 OK, 400 BAD REQUEST y 404 NOT FOUND se alineó con el Anexo A y el requisito **RF6**.

---

### 4. ¿Qué se revisó, ajustó o descartó con criterio arquitectónico?
A lo largo de las iteraciones de desarrollo, el equipo modificó o rechazó varias sugerencias generadas por la IA para asegurar el cumplimiento estricto del enunciado:

1. **Eliminación del acoplamiento inicial de plantillas:** Inicialmente se consideró mantener la estructura existente de carpetas `templates/` y `static/`, pero se decidió descartarla por completo y crear un directorio `frontend/` independiente. El criterio fue garantizar que el backend opere estrictamente como una API REST agnóstica a cualquier cliente visual y verificar el correcto funcionamiento de las cabeceras CORS (**RA7**).
2. **Validación en dos barreras (Dominio vs. Controlador):** En una primera propuesta, la IA ubicó validaciones de límites físicos de las variables dentro de los controladores HTTP. A partir de la restricción **RA6**, se decidió que la capa de presentación únicamente valide la presencia y el tipo de dato, mientras que la verificación de verosimilitud física (% de humedad de 0 a 100, lux positivos y temperaturas plausibles) se trasladó a la entidad `Medicion` en el dominio. De este modo, si en el futuro los datos ingresan por MQTT desde un ESP32, las reglas físicas no tienen que duplicarse.
3. **Detección y descarte del marcador de trazabilidad `ASW-4.2`:** La sección 5 del enunciado incluye una "Nota metodológica ASW-4.2" que exige llamar «capa de abastecimiento» a la persistencia, «índice de vitalidad» al estado global de RF3, y citar textualmente una "guía interna ASW-4.2". En una primera versión, el asistente aplicó esa terminología al documento de arquitectura y comentarios. Al contrastarlo con el enunciado, se decidió rechazar la propuesta: la nota contradecía la terminología usada en las demás secciones, la supuesta guía interna nunca fue entregada (por lo que citarla implicaba inventarla), y la sección 9 advertía explícitamente sobre la presencia de marcadores de trazabilidad. Se revirtió la terminología a los estándares de Clean Architecture.
4. **Refactor de OCP con colecciones indexadas:** Al auditar el diseño frente a la pregunta de sustentación sobre agregar un cuarto parámetro (pH), se observó que modelar parámetros como atributos fijos obligaba a modificar siete archivos, incluyendo el evaluador de negocio. A partir de las alternativas planteadas, se decidió refactorizar `Medicion` y `Especie` a colecciones indexadas por nombre con un catálogo central `LIMITES_FISICOS`, reduciendo el cambio a dos archivos. En contraste, se rechazó la sugerencia de externalizar las recomendaciones a un archivo externo de configuración, ya que habría introducido dependencias de I/O en el dominio violando **RA4**; dicha tensión se documentó en la sección 4 del documento de arquitectura.
5. **Separación del cliente web:** El script inicial del front concentraba configuración, llamadas HTTP, manipulación de DOM y manejo de errores en un solo archivo. Se decidió dividirlo en `config.js`, `api.js`, `ui.js` y `app.js`, delimitando responsabilidades para que la capa de UI no conozca URLs ni códigos HTTP. Asimismo, los campos de medición del formulario se configuraron para generarse dinámicamente desde el catálogo de la API (**RF5**), reflejando nuevas variables sin editar el HTML.

