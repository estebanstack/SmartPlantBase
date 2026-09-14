/**
 * Frontend Asíncrono Desacoplado (RA2)
 * Consume la API REST expuesta en el backend (/api/v1) sin recargar la página.
 * Maneja el ciclo de vida de la petición: carga dinámica de especies (RF5),
 * evaluación (RF1-RF4) y visualización de errores (RF6).
 */

document.addEventListener('DOMContentLoaded', () => {
    // Configuración del endpoint de la API
    // Por defecto apunta al backend Flask en el puerto 5000 (Cross-Origin / RA7)
    const API_BASE = 'http://127.0.0.1:5000/api/v1';

    // Elementos del DOM
    const form = document.getElementById('plant-form');
    const selectEspecie = document.getElementById('especie');
    const emptyState = document.getElementById('empty-state');
    const resultContent = document.getElementById('result-content');
    const resultCard = document.getElementById('resultado-container');
    const btnSubmit = document.getElementById('btn-evaluar');

    // Elementos de error visible (RF6)
    const errorBanner = document.getElementById('error-banner');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');

    // Elementos del diagnóstico
    const statusIcon = document.getElementById('status-icon');
    const statusBadge = document.getElementById('status-badge');
    const statusTitle = document.getElementById('status-title');
    const statusSummary = document.getElementById('status-summary');
    const observationsList = document.getElementById('observations-list');
    const rangesGrid = document.getElementById('ranges-grid');

    // Catálogo en memoria para consultar rangos al renderizar
    let catalogoEspecies = {};

    // 1. Cargar especies de forma asíncrona desde la API (RF5)
    cargarEspecies();

    async function cargarEspecies() {
        try {
            ocultarError();
            const respuesta = await fetch(`${API_BASE}/especies`);
            if (!respuesta.ok) {
                throw new Error(`Error HTTP ${respuesta.status} al consultar especies.`);
            }

            const especies = await respuesta.json();

            // Limpiar selector y poblar dinámicamente desde el backend
            selectEspecie.innerHTML = '<option value="" disabled selected>Selecciona una especie...</option>';
            catalogoEspecies = {};

            especies.forEach(esp => {
                catalogoEspecies[esp.nombre] = esp.rangos;
                const option = document.createElement('option');
                option.value = esp.nombre;
                // Capitalizar primera letra para visualización
                option.textContent = esp.nombre.charAt(0).toUpperCase() + esp.nombre.slice(1);
                selectEspecie.appendChild(option);
            });
        } catch (error) {
            console.error('Error cargando especies:', error);
            mostrarError(
                'Error de Conexión',
                `No fue posible comunicarse con el backend en ${API_BASE}. Asegúrate de que el servidor Flask esté corriendo.`
            );
            selectEspecie.innerHTML = '<option value="" disabled>Error cargando catálogo</option>';
        }
    }

    // 2. Manejo de envío del formulario de manera ASÍNCRONA (RA2)
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // RA2: Prevenir recarga de la página
        ocultarError();

        const especieVal = selectEspecie.value;
        const tempRaw = document.getElementById('temperatura').value;
        const humRaw = document.getElementById('humedad').value;
        const luzRaw = document.getElementById('luz').value;

        // Validación preventiva en cliente
        if (!especieVal) {
            mostrarError('Campo Incompleto', 'Por favor selecciona una especie botánica del catálogo.');
            return;
        }

        const payload = {
            especie: especieVal,
            temperatura: parseFloat(tempRaw),
            humedad: parseFloat(humRaw),
            luz: parseFloat(luzRaw),
        };

        try {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<span>Evaluando...</span>';

            // Petición asíncrona POST al backend REST (RF1)
            const respuesta = await fetch(`${API_BASE}/diagnosticos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const datos = await respuesta.json();

            if (respuesta.ok) {
                // 200 OK: Renderizar el diagnóstico
                renderizarDiagnostico(datos);
            } else {
                // 400 Bad Request o 404 Not Found (RF6)
                const mensajeDetallado = datos.mensaje || 'Error al procesar la solicitud.';
                const detalleInfo = datos.detalle ? JSON.stringify(datos.detalle) : '';
                mostrarError(
                    `Error [${datos.error || 'DESCONOCIDO'}]`,
                    `${mensajeDetallado} ${detalleInfo ? `(Detalle: ${detalleInfo})` : ''}`
                );
            }
        } catch (error) {
            console.error('Error en fetch:', error);
            mostrarError(
                'Error de Red',
                'No se pudo establecer comunicación con el servicio de diagnóstico.'
            );
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = `
                <span>Evaluar Diagnóstico</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
            `;
        }
    });

    /**
     * Renderiza los resultados del diagnóstico en la interfaz (RF2, RF3, RF4).
     */
    function renderizarDiagnostico(diagnostico) {
        // Remover clases previas
        resultCard.classList.remove('state-saludable', 'state-en_riesgo', 'state-critico', 'state-advertencia');

        let icono = '🌱';
        let clase = 'state-saludable';
        let titulo = 'Planta en Condiciones Ideales';

        if (diagnostico.estado === 'SALUDABLE') {
            icono = '🌿';
            clase = 'state-saludable';
            titulo = 'Estado: Saludable';
        } else if (diagnostico.estado === 'EN_RIESGO') {
            icono = '⚠️';
            clase = 'state-en_riesgo';
            titulo = 'Estado: En Riesgo';
        } else {
            icono = '🥀';
            clase = 'state-critico';
            titulo = 'Estado: Crítico';
        }

        resultCard.classList.add(clase);
        statusIcon.textContent = icono;
        statusBadge.textContent = diagnostico.estado;
        statusTitle.textContent = titulo;
        statusSummary.textContent = `Diagnóstico para especie ${diagnostico.especie.toUpperCase()}`;

        // Renderizar lista de recomendaciones (RF4)
        observationsList.innerHTML = '';
        if (diagnostico.recomendaciones.length === 0) {
            const li = document.createElement('li');
            li.className = 'obs-OK';
            li.textContent = '✓ Todos los parámetros se encuentran dentro de los rangos óptimos. No se requieren ajustes.';
            observationsList.appendChild(li);
        } else {
            diagnostico.recomendaciones.forEach(rec => {
                const li = document.createElement('li');
                li.className = 'obs-BAJO';
                li.textContent = `• ${rec}`;
                observationsList.appendChild(li);
            });
        }

        // Renderizar comparación de parámetros evaluados (RF2)
        rangesGrid.innerHTML = '';
        diagnostico.parametros.forEach(param => {
            const item = document.createElement('div');
            item.className = 'range-item';
            item.innerHTML = `
                <span class="range-label">${param.nombre.toUpperCase()} (${param.unidad})</span>
                <span class="range-val">${param.valor} ${param.unidad}</span>
                <span class="status-badge obs-${param.estado}" style="margin-top:0.3rem; display:inline-block;">${param.estado}</span>
                <span class="range-label" style="font-size:0.7rem; margin-top:0.2rem;">Óptimo: ${param.rangoOptimo[0]} - ${param.rangoOptimo[1]}</span>
            `;
            rangesGrid.appendChild(item);
        });

        // Mostrar sección de resultados
        emptyState.classList.add('hidden');
        resultContent.classList.remove('hidden');
    }

    function mostrarError(titulo, mensaje) {
        errorTitle.textContent = `⚠️ ${titulo}`;
        errorMessage.textContent = mensaje;
        errorBanner.classList.remove('hidden');
    }

    function ocultarError() {
        errorBanner.classList.add('hidden');
    }
});
