<style>
@page {
    size: letter;
    margin: 10mm 12mm 10mm 12mm;
    @bottom-right {
        content: "Página " counter(page) " de " counter(pages);
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.2pt;
        color: #64748b;
    }
    @bottom-left {
        content: "Universidad Sergio Arboleda · ARQUIT 2026-2 · Matera-Gotchi (SmartPlantBase)";
        font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 7.2pt;
        color: #64748b;
    }
}
body {
    font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 7.8pt;
    line-height: 1.28;
    color: #1e293b;
}
.header-box {
    border-bottom: 2pt solid #0f172a;
    padding-bottom: 4px;
    margin-bottom: 7px;
}
.header-box .institution {
    font-size: 7.4pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #475569;
    margin: 0;
}
.header-box h1 {
    font-size: 13pt;
    font-weight: 800;
    color: #0f172a;
    margin: 2px 0 1px 0;
    line-height: 1.15;
    border-bottom: none !important;
    padding-bottom: 0 !important;
}
.header-box .subtitle {
    font-size: 8.8pt;
    font-weight: 700;
    color: #047857;
    margin: 0 0 3px 0;
}
.header-box .meta {
    font-size: 7.4pt;
    color: #334155;
    margin: 0;
}
h2 {
    font-size: 9.3pt;
    font-weight: 800;
    color: #0f172a !important;
    margin-top: 7px;
    margin-bottom: 2.5px;
    padding-bottom: 1.5px;
    border-bottom: 0.75pt solid #cbd5e1 !important;
    break-after: avoid;
    page-break-after: avoid;
}
h3 {
    font-size: 8.2pt;
    font-weight: 700;
    color: #1e293b !important;
    margin-top: 4.5px;
    margin-bottom: 2px;
    break-after: avoid;
    page-break-after: avoid;
}
h4 {
    font-size: 7.8pt;
    font-weight: 700;
    color: #334155 !important;
    margin-top: 3px;
    margin-bottom: 1px;
}
p, ul, ol {
    margin-top: 1px;
    margin-bottom: 2.5px;
}
ul, ol {
    padding-left: 14px;
}
li {
    margin-bottom: 1.2px;
}
code {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 7.1pt !important;
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 0.5px 2.5px !important;
    border-radius: 2px !important;
    border: none !important;
}
pre {
    font-family: "Liberation Mono", Consolas, monospace !important;
    font-size: 6.8pt !important;
    line-height: 1.16 !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 0.75pt solid #cbd5e1 !important;
    border-radius: 3px !important;
    padding: 3.5px 5.5px !important;
    margin: 2.5px 0 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
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
    margin: 3px 0 4px 0 !important;
    font-size: 6.9pt !important;
    line-height: 1.15 !important;
}
table th, table td {
    border-left: none !important;
    border-right: none !important;
    padding: 1.8px 3.5px !important;
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
    vertical-align: middle;
    color: #334155 !important;
}
table tr:last-child td {
    border-bottom: 1.2pt solid #0f172a !important;
}
.box-highlight {
    background-color: #f0fdf4;
    border: 0.75pt solid #86efac;
    border-left: 3pt solid #16a34a;
    border-radius: 3px;
    padding: 3.5px 6px;
    margin: 2.5px 0;
}
.box-alert {
    background-color: #fffbeb;
    border: 0.75pt solid #fde68a;
    border-left: 3pt solid #d97706;
    border-radius: 3px;
    padding: 3.5px 6px;
    margin: 2.5px 0;
}
.keep-together {
    break-inside: avoid;
    page-break-inside: avoid;
}

/* Grids and Cards inspired by Canva presentation */
.concept-grid {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin: 4px 0 6px 0;
}
.concept-card {
    flex: 1;
    background: #ffffff;
    border: 1pt solid #cbd5e1;
    border-radius: 4px;
    padding: 6px 8px;
}
.concept-card.problem {
    border-top: 3pt solid #ef4444;
    background: #fef2f2;
}
.concept-card.solution {
    border-top: 3pt solid #10b981;
    background: #f0fdf4;
}
.concept-card.mechanic {
    border-top: 3pt solid #3b82f6;
    background: #eff6ff;
}
.concept-card h4 {
    margin: 0 0 2px 0;
    font-size: 7.6pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.concept-card.problem h4 { color: #991b1b; }
.concept-card.solution h4 { color: #065f46; }
.concept-card.mechanic h4 { color: #1e40af; }
.concept-card p {
    margin: 0;
    font-size: 6.9pt;
    line-height: 1.22;
    color: #334155;
}

/* Tamagotchi Widget Mini-Preview Card */
.tamagotchi-preview-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 1.2pt solid #86efac;
    border-radius: 6px;
    padding: 6px 10px;
    margin: 4px 0 6px 0;
}
.gotchi-avatar-badge {
    display: flex;
    align-items: center;
    gap: 8px;
}
.gotchi-avatar-icon {
    font-size: 18pt;
    line-height: 1;
}
.gotchi-avatar-text h4 {
    margin: 0;
    font-size: 8.2pt;
    color: #065f46;
    font-weight: 800;
}
.gotchi-avatar-text p {
    margin: 0;
    font-size: 7pt;
    color: #047857;
    font-style: italic;
}
.gotchi-stats-pills {
    display: flex;
    gap: 5px;
}
.stat-pill {
    background: #ffffff;
    border: 0.75pt solid #a7f3d0;
    border-radius: 12px;
    padding: 2px 7px;
    font-size: 6.8pt;
    font-weight: 700;
    color: #065f46;
}

/* 5-Step Pipeline Flow Diagram */
.flow-diagram-5 {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: #f8fafc;
    border: 1pt solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 8px;
    margin: 5px 0;
}
.flow-row-5 {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 5px;
}
.flow-step-card {
    flex: 1;
    background: #ffffff;
    border: 0.75pt solid #cbd5e1;
    border-top: 2.5pt solid #2563eb;
    border-radius: 4px;
    padding: 4px 6px;
}
.flow-step-card.step-1 { border-top-color: #64748b; }
.flow-step-card.step-2 { border-top-color: #0284c7; }
.flow-step-card.step-3 { border-top-color: #10b981; }
.flow-step-card.step-4 { border-top-color: #f59e0b; }
.flow-step-card.step-5 { border-top-color: #8b5cf6; }
.flow-step-num {
    display: inline-block;
    width: 13px;
    height: 13px;
    line-height: 13px;
    text-align: center;
    border-radius: 50%;
    background: #0f172a;
    color: #ffffff;
    font-size: 6.2pt;
    font-weight: 800;
    margin-right: 3px;
}
.flow-step-card h4 {
    margin: 0 0 1px 0;
    font-size: 7.1pt;
    color: #0f172a;
    display: flex;
    align-items: center;
}
.flow-step-card p {
    margin: 0;
    font-size: 6.4pt;
    line-height: 1.15;
    color: #475569;
}
.flow-arrow-h {
    display: flex;
    align-items: center;
    font-size: 9pt;
    color: #94a3b8;
    font-weight: bold;
}

/* Badge States */
.badge-state {
    display: inline-block;
    padding: 1.2px 5px;
    border-radius: 9px;
    font-size: 6.3pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.badge-radiante  { background: #dcfce7; color: #166534; border: 0.5pt solid #86efac; }
.badge-contenta  { background: #d1fae5; color: #065f46; border: 0.5pt solid #6ee7b7; }
.badge-sedienta  { background: #e0f2fe; color: #0369a1; border: 0.5pt solid #7dd3fc; }
.badge-ahogada   { background: #ede9fe; color: #5b21b6; border: 0.5pt solid #c4b5fd; }
.badge-sofocada  { background: #ffedd5; color: #c2410c; border: 0.5pt solid #fdba74; }
.badge-congelada { background: #e0f7fa; color: #006064; border: 0.5pt solid #80deea; }
.badge-agradecida{ background: #ecfdf5; color: #047857; border: 0.5pt solid #34d399; }
.badge-marchita  { background: #fee2e2; color: #991b1b; border: 0.5pt solid #fca5a5; }

.xp-badge {
    display: inline-block;
    padding: 1px 4px;
    border-radius: 4px;
    font-weight: 800;
    font-size: 6.4pt;
}
.xp-pos { background: #dcfce7; color: #15803d; }
.xp-neg { background: #fee2e2; color: #b91c1c; }

/* 2-Column Specs Grid */
.specs-grid {
    display: flex;
    gap: 8px;
    margin: 4px 0;
}
.specs-col {
    flex: 1;
    background: #f8fafc;
    border: 1pt solid #cbd5e1;
    border-radius: 4px;
    padding: 5px 8px;
}
.specs-col h4 {
    margin: 0 0 3px 0;
    font-size: 7.6pt;
    font-weight: 800;
    text-transform: uppercase;
    border-bottom: 0.75pt solid #cbd5e1;
    padding-bottom: 2px;
}
.specs-col.rf h4 { color: #0369a1; border-color: #7dd3fc; }
.specs-col.rnf h4 { color: #047857; border-color: #6ee7b7; }
.specs-col ul {
    margin: 0;
    padding-left: 11px;
}
.specs-col li {
    font-size: 6.7pt;
    line-height: 1.18;
    margin-bottom: 2px;
}

/* Conclusion Grid */
.conclusion-grid {
    display: flex;
    gap: 6px;
    margin: 4px 0;
}
.conclusion-card {
    flex: 1;
    background: #ffffff;
    border: 1pt solid #cbd5e1;
    border-top: 2.5pt solid #0f172a;
    border-radius: 4px;
    padding: 5px 7px;
}
.conclusion-card.c1 { border-top-color: #10b981; }
.conclusion-card.c2 { border-top-color: #3b82f6; }
.conclusion-card.c3 { border-top-color: #8b5cf6; }
.conclusion-card h4 {
    margin: 0 0 2px 0;
    font-size: 7.4pt;
    font-weight: 800;
}
.conclusion-card p {
    margin: 0;
    font-size: 6.7pt;
    line-height: 1.2;
    color: #475569;
}
</style>

<div class="header-box">
    <p class="institution">Universidad Sergio Arboleda · Escuela de Ciencias Exactas e Ingeniería</p>
    <h1>SmartPlantBase · Matera-Gotchi</h1>
    <p class="subtitle">Matera-Gotchi: Sistema de Gamificación y Computación Afectiva para SmartPlantBase</p>
    <p class="meta"><strong>Asignatura:</strong> Arquitectura de Software · <strong>Semestre:</strong> 2026-2 · <strong>Estudiantes:</strong> Esteban Castro, Natalia Moreno, Sebastian Gonzalez · <strong>Núcleo:</strong> Arquitectura Hexagonal</p>
</div>

<div class="tamagotchi-preview-banner">
    <div class="gotchi-avatar-badge">
        <div class="gotchi-avatar-icon">🌿</div>
        <div class="gotchi-avatar-text">
            <h4>Matera-Gotchi en Vivo · ¡Estoy feliz!</h4>
            <p>"Gracias por cuidarme, mis parámetros están en armonía."</p>
        </div>
    </div>
    <div class="gotchi-stats-pills">
        <span class="stat-pill">Nivel 5 (Guardián)</span>
        <span class="stat-pill">850 XP</span>
        <span class="stat-pill">Racha: 12 días</span>
        <span class="stat-pill" style="background: #ecfdf5; border-color: #34d399; color: #047857;">Felicidad: 85%</span>
    </div>
</div>

## 1. Resumen y Concepto: De Telemetría Fría a Mascota Digital

En la Fase 2 de **SmartPlantBase** implementamos una arquitectura hexagonal completa que procesa telemetría de sensores físicos (humedad del suelo en %, temperatura ambiental en °C y luminosidad en lux) y la evalúa contra rangos biológicos según la especie vegetal. Los datos se transmiten en tiempo real mediante WebSockets a un panel web.

Aunque el backend resuelve con solidez el diagnóstico biológico, la experiencia de usuario (*UX*) revela una barrera crítica: las métricas numéricas y las alertas técnicas terminan siendo ignoradas por el usuario hasta que la planta muere. Para resolverlo, esta propuesta integra una **mecánica de interacción tipo Tamagotchi**, humanizando los datos de telemetría y transformando la matera inteligente en un organismo afectivo y lúdico:

<div class="concept-grid">
    <div class="concept-card problem">
        <h4>El Problema</h4>
        <p>Las lecturas numéricas y advertencias frías son ignoradas o postergadas por el usuario hasta que el daño vegetal es irreversible.</p>
    </div>
    <div class="concept-card solution">
        <h4>La Solución</h4>
        <p>Antropomorfismo botánico: la planta cobra vida, habla en primera persona con diálogos adaptados y expresa sus emociones.</p>
    </div>
    <div class="concept-card mechanic">
        <h4>Mecánica Central</h4>
        <p>Los hábitos diarios de cuidado se convierten en progresión tangible: puntos de experiencia (XP), niveles crecientes y rachas de días.</p>
    </div>
</div>

### Principios Fundamentales del Sistema
1. **Computación Afectiva y Estado Anímico Visual:** En lugar de desplegar solo cifras estáticas, la planta reacciona con expresiones gráficas (emojis y caras ASCII) y mensajes en primera persona según su estado físico (radiante, contenta, sedienta, ahogada, sofocada, congelada, agradecida o marchita).
2. **Progresión por Hábitos Saludables (XP y Rachas):** Mantener la planta en rangos óptimos genera puntos de experiencia (*XP*) y consolida días de racha consecutivos. El descuido continuado penaliza la felicidad y reinicia la racha, incentivando la constancia sin frustrar el avance histórico acumulado.
3. **Reacción Reactiva Inmediata a Acciones Físicas:** Cuando el usuario riega la planta o la expone a la luz requerida, el sensor capta el cambio en tiempo real y la planta responde inmediatamente con el estado `AGRADECIDA` y animaciones festivas en el frontend.
4. **Aislamiento Arquitectónico Estricto (RA3, RA4):** La gamificación se concibe como un **subdominio desacoplado**. La clase de dominio biológico `ValidadorDeEstado` permanece inalterada; la lógica lúdica es coordinada por un servicio especializado (`MotorGamificacion`) mediante puertos y adaptadores dedicados.

<div class="flow-diagram-5">
    <div style="font-weight: 800; font-size: 7.2pt; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 0.75pt solid #cbd5e1; padding-bottom: 2px;">
        Pipeline IoT y Flujo de Datos en Tiempo Real (Extremo a Extremo en &lt;5 ms)
    </div>
    <div class="flow-row-5">
        <div class="flow-step-card step-1">
            <h4><span class="flow-step-num">1</span> Ingesta IoT</h4>
            <p>ESP32 envía telemetría cruda vía HTTP POST al backend.</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-2">
            <h4><span class="flow-step-num">2</span> Dominio Biológico</h4>
            <p><code>ValidadorDeEstado</code> genera diagnóstico puro según especie.</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-3">
            <h4><span class="flow-step-num">3</span> Motor Lúdico</h4>
            <p><code>MotorGamificacion</code> calcula emoción, delta XP y diálogo.</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-4">
            <h4><span class="flow-step-num">4</span> Persistencia</h4>
            <p><code>GamificacionPort</code> persiste perfil en SQLite relacional.</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-5">
            <h4><span class="flow-step-num">5</span> Streaming WS</h4>
            <p>WebSocket emite bloque <code>tamagotchi</code> hacia <code>user_{id}</code>.</p>
        </div>
    </div>
</div>

---

## 2. Mecánica del Tamagotchi: Estados Anímicos y Progresión

### 2.1 Matriz de Estados Anímicos y Emociones
El estado anímico se determina de manera **determinista** evaluando el diagnóstico biológico del sensor, los límites fisiológicos de la especie vegetal y la tasa de cambio de humedad (detección de riego):

| Estado Anímico | Emoji | Expresión ASCII | Disparador Biológico / Físico | Mensaje al Usuario en Primera Persona | Impacto XP / Felicidad |
|---|:---:|:---:|---|---|:---:|
| <span class="badge-state badge-radiante">RADIANTE</span> | 🌸✨ | `( ˘ ³˘)♥` | Parámetros óptimos y racha > 3 días consecutivos. | *"¡Estoy en mi mejor momento! El sol y el agua están perfectos."* | <span class="xp-badge xp-pos">+25 XP</span> / 100% |
| <span class="badge-state badge-contenta">CONTENTA</span> | 🌿😊 | `(✿◠‿◠)` | Todos los parámetros dentro del rango biológico saludable. | *"Me siento muy bien. Gracias por cuidar de mí con constancia."* | <span class="xp-badge xp-pos">+10 XP</span> / 85% |
| <span class="badge-state badge-sedienta">SEDIENTA</span> | 💧🥺 | `( •́︿•̀ )` | Humedad del sustrato en nivel `BAJO`; solicita riego urgente. | *"Tengo sed; mi tierra está bastante seca. ¿Me das un poco de agua?"* | <span class="xp-badge xp-neg">-5 XP</span> / 40% |
| <span class="badge-state badge-ahogada">AHOGADA</span> | 🌊🤢 | `(×_×;)` | Humedad saturada `ALTO`; riesgo inminente de pudrición radicular. | *"¡Mucha agua! Mis raíces se están asfixiando, déjame secar un poco."* | <span class="xp-badge xp-neg">-10 XP</span> / 30% |
| <span class="badge-state badge-sofocada">SOFOCADA</span> | ☀️🥵 | `(;´д｀)` | Estrés ambiental por temperatura alta o iluminación excesiva. | *"Hace demasiado calor aquí. ¿Podrías ubicarme en un lugar fresco?"* | <span class="xp-badge xp-neg">-10 XP</span> / 35% |
| <span class="badge-state badge-congelada">CONGELADA</span> | ❄️🥶 | `( >_< )` | Estrés térmico por temperatura ambiental baja. | *"¡Qué frío! Mis hojas se están entumeciendo, protégeme del viento."* | <span class="xp-badge xp-neg">-10 XP</span> / 35% |
| <span class="badge-state badge-agradecida">AGRADECIDA</span> | 💚🥰 | `(つ✧ω✧)つ` | Salto súbito de humedad tras riego en tiempo real (> 15% en &lt; 5 min). | *"¡Agua fresca! Justo lo que necesitaba para revivir. ¡Muchas gracias!"* | <span class="xp-badge xp-pos">+50 XP</span> / +30% |
| <span class="badge-state badge-marchita">MARCHITA</span> | 🥀💀 | `(x_x)` | Diagnóstico crítico multisensor con hojas visiblemente decaídas. | *"Mis hojas están decaídas y débiles... Necesito atención urgente."* | <span class="xp-badge xp-neg">-30 XP</span> / 10% |

### 2.2 Progresión por Niveles y Rachas de Días
El sistema incentiva el hábito continuo mediante 5 niveles botánicos bien diferenciados:
- **Nivel 1: Semilla** (0 - 150 XP) — Avatar brotando, respuestas básicas, tutorial inicial.
- **Nivel 2: Plántula** (151 - 450 XP) — Primeras hojas tiernas, desbloqueo de emociones contextuales.
- **Nivel 3: Planta Joven** (451 - 1000 XP) — Follaje robusto, desbloquea consejos de cultivo avanzados.
- **Nivel 4: Planta Florecida** (1001 - 2000 XP) — Flores visibles y resistencia a un descuido leve sin perder racha.
- **Nivel 5: Guardián Botánico** (2000+ XP) — Planta plenamente desarrollada, halo dorado e insignia de cuidador maestro.

*Regla de Racha:* La racha se incrementa en +1 cada 24 horas continuas en estado `SALUDABLE`. En caso de diagnóstico `CRITICO`, la racha cae a 0 para reflejar el descuido, pero la XP histórica nunca decrece por debajo de cero, protegiendo la motivación del alumno.

### 2.3 Personalidad y Diálogos Adaptados por Especie
- **Sansevieria:** Firme, sobria y tolerante a la sequía. Advierte con severidad el exceso de agua: *"Recuerda que soy de clima seco; no acumules agua en mi plato"*.
- **Potos:** Expresiva, sensible a la penumbra. Pide reubicación luminosa si la luxometría permanece baja durante horas.
- **Suculenta:** Almacén hídrico foliar. Entra en alarma temprana si se detecta saturación prolongada.
- **Helecho:** Amante de la humedad constante. Sus mensajes de auxilio hídrico son más inmediatos y expresivos.

---

## 3. Especificación Formal de Requisitos (RF & RNF)

Los requisitos formales garantizan aislamiento arquitectónico, integridad operativa y confiabilidad:

<div class="specs-grid">
    <div class="specs-col rf">
        <h4>Requisitos Funcionales (RF)</h4>
        <ul>
            <li><strong>RF-01 (Cálculo Determinista de Emociones):</strong> Derivar el estado anímico a partir de la telemetría física y el <code>Diagnostico</code> botánico.</li>
            <li><strong>RF-02 (Acumulación de XP y Niveles):</strong> Conceder +10 XP por ciclo en rango saludable y +25 XP en radiante. Subir de nivel según la tabla de 5 etapas.</li>
            <li><strong>RF-03 (Detección Reactiva de Riego):</strong> Identificar incrementos súbitos de humedad (&gt; 15% delta) para detonar estado <code>AGRADECIDA</code> (+50 XP).</li>
            <li><strong>RF-04 (Persistencia de Perfil):</strong> Guardar <code>xp_total</code>, <code>nivel</code>, <code>racha_dias</code>, <code>felicidad</code> y <code>ultimo_animo</code>.</li>
            <li><strong>RF-05 (Notificación WebSocket):</strong> Transmitir payload enriquecido con bloque <code>tamagotchi</code> hacia la sala privada <code>user_{id}</code>.</li>
            <li><strong>RF-06 (Consulta REST):</strong> Exponer <code>GET /api/plantas/{id}/gamificacion</code> asegurado con token JWT.</li>
        </ul>
    </div>
    <div class="specs-col rnf">
        <h4>Requisitos No Funcionales (RNF)</h4>
        <ul>
            <li><strong>RNF-01 (Subdominio en Python Puro - RA4):</strong> Lógica lúdica sin dependencias web (Flask/SocketIO) ni de BD, 100% testeable con dobles en memoria.</li>
            <li><strong>RNF-02 (Separación de Responsabilidades - SRP):</strong> <code>ValidadorDeEstado</code> permanece inmutable e higiénico. Gamificación encapsulada en <code>MotorGamificacion</code>.</li>
            <li><strong>RNF-03 (Degradación Grácil):</strong> Si la persistencia o cálculo lúdico falla, la telemetría biológica y la respuesta HTTP al ESP32 se completan normalmente.</li>
            <li><strong>RNF-04 (Desempeño Ultrarrápido):</strong> Ejecución lúdica en memoria en menos de 5 milisegundos por lectura.</li>
            <li><strong>RNF-05 (Seguridad Multiusuario):</strong> Autorización estricta por pertenencia de planta en JWT.</li>
        </ul>
    </div>
</div>

---

## 4. Arquitectura Hexagonal y Aislamiento Concéntrico

El subdominio de gamificación se acopla limpiamente mediante el patrón de **Puertos y Adaptadores**, preservando el centro del hexágono intacto:

<div class="flow-diagram-5">
    <div style="font-weight: 800; font-size: 7.2pt; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 0.75pt solid #cbd5e1; padding-bottom: 2px;">
        Aislamiento Concéntrico: Adaptadores de Entrada ➔ Dominio Puro ➔ Adaptadores de Salida
    </div>
    <div class="flow-row-5">
        <div class="flow-step-card step-1">
            <h4>Adaptadores Entrada</h4>
            <p><strong>api_dispositivos.py</strong><br>POST telemetría IoT cruda.</p>
            <p style="margin-top:2px;"><strong>api_front.py</strong><br>GET consulta lúdica JWT.</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-3" style="flex: 1.4;">
            <h4>Dominio Puro (Python Puro RA4)</h4>
            <p><strong>Entidades Inmutables:</strong> <code>EstadoAnimico</code>, <code>ExpresionTamagotchi</code>, <code>PerfilGamificacion</code>.</p>
            <p style="margin-top:2px;"><strong>Servicio de Dominio:</strong> <code>MotorGamificacion</code> (evaluación de emoción, deltas de XP y racha).</p>
            <p style="margin-top:2px;"><strong>Puerto de Salida:</strong> <code>GamificacionPort</code> (contrato abstracto agnóstico a SQLite).</p>
        </div>
        <div class="flow-arrow-h">➔</div>
        <div class="flow-step-card step-4">
            <h4>Adaptadores Salida</h4>
            <p><strong>gamificacion_bd.py</strong><br>Persistencia relacional SQLite.</p>
            <p style="margin-top:2px;"><strong>notificador_ws.py</strong><br>SocketIO emit a <code>user_{id}</code>.</p>
        </div>
    </div>
</div>

### 4.1 Dominio Puro (`matera/dominio/`)
- **`gamificacion.py`:** Define las entidades inmutables y el servicio de cálculo de emoción y progresión.
- **`puertos/salida.py`:** Incorpora la interfaz abstracta `GamificacionPort` (`obtener_perfil(planta_id)`, `guardar_perfil(perfil)`, `registrar_evento(evento)`).
- **`casos_uso/registrar_lectura.py`:** Orquesta la validación biológica y la gamificación con cláusula `try/except` de degradación grácil.

### 4.2 Adaptadores de Salida (`matera/adaptadores/salida/`)
- **`gamificacion_bd.py`:** Implementación SQLite del puerto `GamificacionPort`, con mapeo directo de tuplas a dataclasses inmutables.
- **`notificador_ws.py`:** En `notificar_telemetria`, añade la llave `"tamagotchi"` al payload WebSocket emitido.

### 4.3 Adaptadores de Entrada (`matera/adaptadores/entrada/`)
- **`api_front.py`:** Expone el endpoint `GET /api/plantas/<planta_id>/gamificacion` protegido con JWT.

---

## 5. Modelo de Datos Relacional y Persistencia SQL

El diseño relacional es **no destructivo** y garantiza **compatibilidad total** con el esquema existente de la Fase 2 (tablas `plantas`, `usuarios`, `lecturas`), aplicando claves foráneas con `ON DELETE CASCADE`:

```sql
-- data/bd/gamificacion.sql: Esquema relacional no destructivo para gamificación
CREATE TABLE IF NOT EXISTS perfiles_gamificacion (
    planta_id TEXT PRIMARY KEY,
    xp_total INTEGER NOT NULL DEFAULT 0,
    nivel INTEGER NOT NULL DEFAULT 1,
    racha_dias INTEGER NOT NULL DEFAULT 0,
    felicidad INTEGER NOT NULL DEFAULT 100,
    ultimo_animo TEXT NOT NULL DEFAULT 'CONTENTA',
    ultima_actualizacion TEXT NOT NULL,
    FOREIGN KEY (planta_id) REFERENCES plantas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eventos_gamificacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planta_id TEXT NOT NULL,
    tipo_evento TEXT NOT NULL, -- 'RIEGO', 'NIVEL_UP', 'RACHA_DIAS', 'PENALIZACION'
    xp_ganada INTEGER NOT NULL,
    detalle TEXT NOT NULL,
    fecha_evento TEXT NOT NULL,
    FOREIGN KEY (planta_id) REFERENCES plantas(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_eventos_gamif_planta ON eventos_gamificacion(planta_id, fecha_evento DESC);
```

<div class="box-highlight">
    <strong>Garantías de Diseño de Base de Datos:</strong>
    1. <strong>Cero Modificaciones a Tablas Existentes:</strong> Las tablas <code>plantas</code>, <code>lecturas</code> y <code>usuarios</code> no sufren alteración de columnas, blindando los 106 tests existentes.<br>
    2. <strong>Integridad Referencial en Cascada:</strong> Si una planta es eliminada, sus perfiles y eventos lúdicos se limpian automáticamente mediante <code>ON DELETE CASCADE</code>.<br>
    3. <strong>Historial de Auditoría Lúdica:</strong> La tabla <code>eventos_gamificacion</code> registra cronológicamente cada bonificación de XP, permitiendo graficar el historial de cuidados.
</div>

---

## 6. Especificación de Contratos de Código e Interfaces

<div class="keep-together">

### 6.1 Dominio Puro: Entidades Inmutables (`matera/dominio/gamificacion.py`)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EstadoAnimico(str, Enum):
    RADIANTE = "RADIANTE"
    CONTENTA = "CONTENTA"
    SEDIENTA = "SEDIENTA"
    AHOGADA = "AHOGADA"
    SOFOCADA = "SOFOCADA"
    CONGELADA = "CONGELADA"
    AGRADECIDA = "AGRADECIDA"
    MARCHITA = "MARCHITA"

@dataclass(frozen=True)
class ExpresionTamagotchi:
    estado: EstadoAnimico
    emoji: str
    cara_ascii: str
    mensaje: str
    felicidad: int  # Rango determinista 0 a 100

@dataclass(frozen=True)
class PerfilGamificacion:
    planta_id: str
    xp_total: int
    nivel: int
    racha_dias: int
    felicidad: int
    ultimo_animo: EstadoAnimico
    expresion: Optional[ExpresionTamagotchi] = None
```

</div>

<div class="keep-together">

### 6.2 Lógica del Motor de Gamificación (`MotorGamificacion`)

```python
class MotorGamificacion:
    """Reglas puras de gamificación botánica y cálculo de experiencia."""

    @staticmethod
    def derivar_expresion(especie: str, diagnostico, es_riego: bool = False, racha: int = 0) -> ExpresionTamagotchi:
        if es_riego:
            return ExpresionTamagotchi(EstadoAnimico.AGRADECIDA, "💚🥰", "(つ✧ω✧)つ",
                                      "¡Agua fresca! Justo lo que necesitaba para mis raíces.", 100)
        if diagnostico.estado.value == "CRITICO":
            return ExpresionTamagotchi(EstadoAnimico.MARCHITA, "🥀💀", "(x_x)",
                                      "Mis hojas están decaídas y débiles... Necesito atención urgente.", 10)
        for p in diagnostico.parametros:
            if p.nombre == "humedad" and p.estado.value == "BAJO":
                return ExpresionTamagotchi(EstadoAnimico.SEDIENTA, "💧🥺", "( •́︿•̀ )",
                                          "Tengo sed; mi sustrato está seco. ¿Me das un poco de agua?", 40)
            if p.nombre == "humedad" and p.estado.value == "ALTO":
                return ExpresionTamagotchi(EstadoAnimico.AHOGADA, "🌊🤢", "(×_×;)",
                                          "¡Mucha agua! Mis raíces se están asfixiando.", 30)
            if p.nombre == "temperatura" and p.estado.value == "ALTO":
                return ExpresionTamagotchi(EstadoAnimico.SOFOCADA, "☀️🥵", "(;´д｀)",
                                          "Hace demasiado calor aquí. ¿Me trasladas a la sombra?", 35)
            if p.nombre == "temperatura" and p.estado.value == "BAJO":
                return ExpresionTamagotchi(EstadoAnimico.CONGELADA, "❄️🥶", "( >_< )",
                                          "¡Qué frío! Mis hojas se están entumeciendo.", 35)
        if racha >= 3:
            return ExpresionTamagotchi(EstadoAnimico.RADIANTE, "🌸✨", "( ˘ ³˘)♥",
                                      "¡Estoy en mi mejor momento! El sol y el agua están perfectos.", 100)
        return ExpresionTamagotchi(EstadoAnimico.CONTENTA, "🌿😊", "(✿◠‿◠)",
                                  "Me siento muy bien. Gracias por cuidar de mí con constancia.", 85)

    @staticmethod
    def actualizar_perfil(perfil: PerfilGamificacion, exp: ExpresionTamagotchi, es_riego: bool) -> PerfilGamificacion:
        delta_xp = 50 if es_riego else (25 if exp.estado == EstadoAnimico.RADIANTE else (10 if exp.estado == EstadoAnimico.CONTENTA else 0))
        nueva_xp = perfil.xp_total + delta_xp
        nuevo_nivel = min(5, 1 + (nueva_xp // 400))
        nueva_felicidad = int((perfil.felicidad * 0.3) + (exp.felicidad * 0.7))
        return PerfilGamificacion(
            planta_id=perfil.planta_id, xp_total=nueva_xp, nivel=nuevo_nivel,
            racha_dias=perfil.racha_dias, felicidad=nueva_felicidad,
            ultimo_animo=exp.estado, expresion=exp
        )
```

</div>

<div class="keep-together">

### 6.3 Integración Desacoplada en `RegistrarLectura` y WebSocket Streaming

```python
# matera/dominio/casos_uso/registrar_lectura.py
class RegistrarLectura(RegistrarLecturaPort):
    def registrar(self, dispositivo_id: str, valores: Mapping[str, float], marca_tiempo: str = "") -> Diagnostico:
        # 1. Validación biológica y persistencia médica pura (invariable)
        diagnostico = ValidadorDeEstado.evaluar(lectura, especie_entidad)
        self._historial.guardar_lectura(lectura, diagnostico)

        # 2. Subdominio lúdico con cláusula de degradación grácil
        datos_tamagotchi = None
        if self._gamificacion is not None:
            try:
                perfil = self._gamificacion.obtener_perfil(planta.id)
                es_riego = self._detectar_riego(valores, planta.id)
                exp = MotorGamificacion.derivar_expresion(planta.especie, diagnostico, es_riego, perfil.racha_dias)
                perfil = MotorGamificacion.actualizar_perfil(perfil, exp, es_riego)
                self._gamificacion.guardar_perfil(perfil)
                datos_tamagotchi = perfil
            except Exception as err:
                logger.warning("Degradación grácil activada (gamificación): %s", err)

        # 3. Notificación WebSocket con payload enriquecido en < 5ms
        if self._notificador is not None:
            self._notificador.notificar_telemetria(planta, lectura, diagnostico, datos_tamagotchi)
        return diagnostico
```

</div>

<div class="keep-together">

### 6.4 Payload JSON Enriquecido en WebSocket (`telemetria_actualizada`)

```json
{
  "planta_id": "planta-01",
  "planta_nombre": "Mi Monstera Deliciosa",
  "dispositivo_id": "esp32-matera-01",
  "especie": "monstera",
  "valores": { "humedad": 58.2, "temperatura": 22.4, "luz": 620.0 },
  "estado": "SALUDABLE",
  "tamagotchi": {
    "animo": "CONTENTA",
    "emoji": "🌿😊",
    "cara_ascii": "(✿◠‿◠)",
    "mensaje": "Me siento muy bien. Gracias por cuidar de mí con constancia.",
    "felicidad": 85,
    "xp_total": 850,
    "nivel": 5,
    "racha_dias": 12
  }
}
```

</div>

---

## 7. Widget Frontend y Experiencia Interactiva (Vanilla JS)

Siguiendo el principio de **cero dependencias externas en frontend (HTML5/CSS3/Vanilla JS)**, el componente visual se integra armónicamente en el panel de control:

<div class="keep-together">

```html
<!-- Widget Tamagotchi integrado en live-panel (frontend/index.html) -->
<div class="card tamagotchi-card mood-CONTENTA" id="tamagotchi-widget">
    <div class="gotchi-header">
        <span class="gotchi-badge" id="gotchi-mood-tag">CONTENTA</span>
        <span class="gotchi-level-pill" id="gotchi-level-tag">Nivel 5 · Guardián</span>
    </div>
    <div class="gotchi-body">
        <div class="gotchi-avatar-wrap">
            <div class="gotchi-icon" id="gotchi-avatar">🌿</div>
            <div class="gotchi-ascii" id="gotchi-face">(✿◠‿◠)</div>
        </div>
        <div class="gotchi-speech">
            <p id="gotchi-message">"Me siento muy bien. Gracias por cuidar de mí con constancia."</p>
            <div class="gotchi-meters">
                <div class="meter-row">
                    <span>Felicidad: <strong id="gotchi-happy-val">85%</strong></span>
                    <div class="meter-bar"><div class="fill fill-happy" id="gotchi-happy-bar" style="width: 85%;"></div></div>
                </div>
                <div class="meter-row">
                    <span>Experiencia: <strong id="gotchi-xp-val">850 XP</strong></span>
                    <div class="meter-bar"><div class="fill fill-xp" id="gotchi-xp-bar" style="width: 70%;"></div></div>
                </div>
            </div>
        </div>
    </div>
</div>
```

```css
/* Animaciones Reactivas en CSS Puro (frontend/css/style.css) */
.gotchi-icon { font-size: 2.8rem; animation: breathing 3s ease-in-out infinite; }
@keyframes breathing { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-3px) scale(1.05); } }
.mood-SEDIENTA .gotchi-icon, .mood-MARCHITA .gotchi-icon { animation: droop 2s ease-in-out infinite; filter: grayscale(40%); }
@keyframes droop { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(-6deg) translateY(2px); } }
.mood-AGRADECIDA .gotchi-icon, .mood-RADIANTE .gotchi-icon { animation: bounce 0.8s ease-in-out infinite alternate; }
@keyframes bounce { 0% { transform: scale(1); } 100% { transform: scale(1.15) translateY(-5px); } }
```

```javascript
// Renderizado Reactivo en frontend/js/ui.js
renderizarTamagotchi(t) {
    if (!t) return;
    document.getElementById("gotchi-avatar").textContent = t.emoji;
    document.getElementById("gotchi-face").textContent = t.cara_ascii;
    document.getElementById("gotchi-mood-tag").textContent = t.animo;
    document.getElementById("gotchi-message").textContent = `"${t.mensaje}"`;
    document.getElementById("gotchi-happy-val").textContent = `${t.felicidad}%`;
    document.getElementById("gotchi-happy-bar").style.width = `${t.felicidad}%`;
    document.getElementById("gotchi-xp-val").textContent = `${t.xp_total} XP`;
    document.getElementById("gotchi-level-tag").textContent = `Nivel ${t.nivel}`;
    const widget = document.getElementById("tamagotchi-widget");
    widget.className = `card tamagotchi-card mood-${t.animo}`;
}
```

</div>

---

<div style="page-break-before: always;"></div>

## 8. Plan de Implementación (Roadmap de 5 Hitos)

Roadmap estructurado para entrega continua sin riesgo de regresión sobre los 106 tests actuales:

| Hito | Alcance y Tareas Principales | Módulos Modificados / Creados | Criterio de Aceptación y QA |
|:---:|---|---|---|
| **Hito 1** | **Dominio Puro de Gamificación**<br>Entidades `EstadoAnimico`, `PerfilGamificacion` y servicio `MotorGamificacion`. Pruebas unitarias sin dependencias externas. | `matera/dominio/gamificacion.py`<br>`tests/test_gamificacion.py` | 100% tests pasando en `pytest` en &lt; 0.1s. Cobertura completa de matriz de estados. |
| **Hito 2** | **Puertos y Persistencia SQLite**<br>Interfaz abstracta `GamificacionPort`, adaptador `gamificacion_bd.py` y script SQL de migración limpia. | `matera/dominio/puertos/salida.py`<br>`matera/adaptadores/salida/gamificacion_bd.py`<br>`data/bd/gamificacion.sql` | CRUD verificado con `ON DELETE CASCADE`. Cero alteraciones a tablas de Fase 2. |
| **Hito 3** | **Integración en Caso de Uso y WS**<br>Inyección protegida en `RegistrarLectura` y extensión de `SocketIONotificadorAdapter`. | `matera/dominio/casos_uso/registrar_lectura.py`<br>`matera/adaptadores/salida/notificador_ws.py` | Evento WebSocket enriquecido con latencia de cálculo menor a 5 ms. |
| **Hito 4** | **Frontend y Widget Tamagotchi**<br>Maquetación HTML en `#live-panel`, animación reactiva CSS (respiración, marchitamiento, salto) y binding en `ui.js`. | `frontend/index.html`<br>`frontend/css/style.css`<br>`frontend/js/ui.js` | El avatar cambia de emoji, expresión ASCII y color dinámicamente sin refrescar la página. |
| **Hito 5** | **Simulación de Riego y Verificación E2E**<br>Bandera `--regar` en `simulador_esp32.py` para inducir salto &gt; 15% de humedad y pruebas end-to-end. | `simulador_esp32.py`<br>`tests/test_e2e_gamificacion.py` | Reacción inmediata con estado `AGRADECIDA`, +50 XP y feedback visual instantáneo. |

---

## 9. Conclusiones y Sustentación Técnica

<div class="conclusion-grid">
    <div class="conclusion-card c1">
        <h4>1. UX Humanizada</h4>
        <p>Transforma métricas frías en apego afectivo, resolviendo el problema de abandono del cuidado botánico mediante micro-hábitos y retroalimentación inmediata.</p>
    </div>
    <div class="conclusion-card c2">
        <h4>2. Clean Architecture</h4>
        <p>Valida la extensibilidad de los puertos y adaptadores de la Fase 2: el dominio biológico permanece inmaculado y el nuevo subdominio se conecta de forma aislada.</p>
    </div>
    <div class="conclusion-card c3">
        <h4>3. Garantía de Calidad</h4>
        <p>Mantiene el 100% de la suite de 106 pruebas unitarias e integración en verde, garantizando cero regresiones y degradación grácil en fallas.</p>
    </div>
</div>

<div class="box-highlight" style="margin-top: 5px;">
    <strong>Síntesis para Sustentación Oral:</strong>
    <em>"Matera-Gotchi demuestra que la arquitectura de software no es un fin en sí misma, sino el cimiento que permite extender un sistema IoT con computación afectiva y gamificación de forma ágil, segura y sin comprometer el rigor biológico ni la estabilidad de producción."</em>
</div>
