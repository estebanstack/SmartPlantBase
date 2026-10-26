/**
 * Orquestación del cliente web (Arquitectura Hexagonal).
 * Gestiona la sesión JWT (R7), el polling periódico (R6) y el formulario manual (R1).
 */

let sesionActual = {
    token: null,
    usuario: null,
    plantaId: null,
};

let intervaloPolling = null;

document.addEventListener('DOMContentLoaded', () => {
    inicializarCatalogo();
    configurarEventosSesion();

    document.getElementById('plant-form').addEventListener('submit', async (evento) => {
        evento.preventDefault();
        await evaluarManual();
    });

    document.getElementById('btn-probar-ajena').addEventListener('click', async () => {
        await probarAccesoPlantaAjena();
    });
});

/** R1: Carga catálogo botánico para el formulario manual. */
async function inicializarCatalogo() {
    try {
        PlantUI.ocultarError();
        const especies = await PlantApi.obtenerEspecies();
        PlantUI.poblarSelector(especies);
        PlantUI.construirCamposDeMedicion(parametrosDe(especies));
    } catch (error) {
        PlantUI.mostrarError('No se pudo cargar el catálogo', error.message);
        PlantUI.deshabilitarFormulario('Catálogo no disponible');
    }
}

function parametrosDe(especies) {
    const vistos = new Map();
    especies.forEach((esp) => {
        Object.entries(esp.rangos || {}).forEach(([nombre, rango]) => {
            if (!vistos.has(nombre)) {
                vistos.set(nombre, { nombre, unidad: rango.unidad });
            }
        });
    });
    return Array.from(vistos.values());
}

/** R1: Envío de medición manual. */
async function evaluarManual() {
    PlantUI.ocultarError();
    const { especie, valores } = PlantUI.leerFormulario();

    if (!especie) {
        PlantUI.mostrarError('Falta la especie', 'Selecciona una especie del catálogo antes de evaluar.');
        return;
    }

    try {
        PlantUI.setCargando(true);
        const diagnostico = await PlantApi.evaluarDiagnostico(especie, valores);
        PlantUI.renderizarDiagnostico(diagnostico);
    } catch (error) {
        PlantUI.mostrarError(tituloDeError(error.codigo), error.message);
        PlantUI.marcarCampo(error.campo);
    } finally {
        PlantUI.setCargando(false);
    }
}

/** R7: Configuración de eventos de inicio y cierre de sesión. */
function configurarEventosSesion() {
    const btnAna = document.getElementById('btn-login-ana');
    const btnCarlos = document.getElementById('btn-login-carlos');
    const btnLogout = document.getElementById('btn-logout');

    btnAna.addEventListener('click', async () => {
        await iniciarSesion('ana@matera.edu.co', 'clave123');
    });

    btnCarlos.addEventListener('click', async () => {
        await iniciarSesion('carlos@matera.edu.co', 'clave123');
    });

    btnLogout.addEventListener('click', () => {
        cerrarSesion();
    });
}

async function iniciarSesion(email, password) {
    try {
        PlantUI.ocultarError();
        const res = await PlantApi.login(email, password);
        sesionActual.token = res.token;
        sesionActual.usuario = res.usuario;

        // Actualizar interfaz
        document.getElementById('user-session-desc').textContent = 
            `Sesión iniciada: ${res.usuario.nombre} (${res.usuario.email}) · Token Bearer activo.`;
        document.getElementById('btn-login-ana').classList.add('hidden');
        document.getElementById('btn-login-carlos').classList.add('hidden');
        document.getElementById('btn-logout').classList.remove('hidden');

        // Cargar plantas del usuario
        const plantas = await PlantApi.obtenerPlantas(res.token);
        if (plantas && plantas.length > 0) {
            sesionActual.plantaId = plantas[0].id;
            iniciarPolling(plantas[0]);
        }
    } catch (err) {
        PlantUI.mostrarError('Error de Autenticación', err.message);
    }
}

function cerrarSesion() {
    if (intervaloPolling) {
        clearInterval(intervaloPolling);
        intervaloPolling = null;
    }
    sesionActual = { token: null, usuario: null, plantaId: null };

    document.getElementById('user-session-desc').textContent = 
        'No hay sesión activa. Inicia sesión para ver tu planta y activar el polling.';
    document.getElementById('btn-login-ana').classList.remove('hidden');
    document.getElementById('btn-login-carlos').classList.remove('hidden');
    document.getElementById('btn-logout').classList.add('hidden');
    document.getElementById('live-panel').style.display = 'none';
}

/** R6: Polling periódico cada 3 segundos. */
function iniciarPolling(planta) {
    const livePanel = document.getElementById('live-panel');
    livePanel.style.display = 'block';
    document.getElementById('live-plant-title').textContent = 
        `🌿 ${planta.nombre} (${planta.especie.toUpperCase()})`;
    document.getElementById('live-dispositivo').textContent = 
        `Dispositivo sensor: ${planta.dispositivo_id}`;

    // Consulta inmediata
    consultarTelemetria(planta.id);

    // Consulta periódica cada 3s
    if (intervaloPolling) clearInterval(intervaloPolling);
    intervaloPolling = setInterval(() => {
        consultarTelemetria(planta.id);
    }, 3000);
}

async function consultarTelemetria(plantaId) {
    if (!sesionActual.token) return;
    try {
        const data = await PlantApi.obtenerEstadoPlanta(plantaId, sesionActual.token);
        actualizarTelemetriaUI(data);
    } catch (err) {
        console.error('Error en polling de telemetría:', err);
    }
}

function actualizarTelemetriaUI(data) {
    const statusEl = document.getElementById('live-status');
    const humEl = document.getElementById('live-humedad');
    const luzEl = document.getElementById('live-luz');
    const tempEl = document.getElementById('live-temperatura');
    const marcaEl = document.getElementById('live-marca');
    const recsEl = document.getElementById('live-recs');

    if (!data.ultima_lectura) {
        statusEl.textContent = 'SIN LECTURAS AÚN';
        statusEl.style.color = '#9ca3af';
        return;
    }

    const valores = data.ultima_lectura.valores || {};
    humEl.textContent = `${valores.humedad ?? '--'} %`;
    luzEl.textContent = `${valores.luz ?? '--'} lux`;
    tempEl.textContent = `${valores.temperatura ?? '--'} °C`;
    marcaEl.textContent = `Última lectura: ${data.ultima_lectura.marca_tiempo || '--'}`;

    if (data.diagnostico) {
        const st = data.diagnostico.estado;
        statusEl.textContent = st;
        if (st === 'SALUDABLE') statusEl.style.color = '#10b981';
        else if (st === 'EN_RIESGO') statusEl.style.color = '#f59e0b';
        else statusEl.style.color = '#ef4444';

        const recs = data.diagnostico.recomendaciones || [];
        recsEl.textContent = recs.length > 0 ? `⚠️ ${recs.join(' | ')}` : '✅ Condiciones ambientales óptimas.';
    }
}

/** Demostración en vivo: Intento de acceso a planta ajena (R7 / Sección 7). */
async function probarAccesoPlantaAjena() {
    if (!sesionActual.token) {
        PlantUI.mostrarError('Acceso Denegado', 'Inicia sesión primero (ej. como Carlos).');
        return;
    }

    try {
        // Intenta consultar planta-01 (pertenece a Ana)
        await PlantApi.obtenerEstadoPlanta('planta-01', sesionActual.token);
        PlantUI.mostrarError('Acceso Inesperado', 'La consulta fue permitida.');
    } catch (err) {
        // Demostración exitosa de regla de negocio de dominio
        PlantUI.mostrarError(
            `🛡️ Regla de Propiedad Verificada (HTTP ${err.status} - ${err.codigo})`,
            `El dominio rechazó la consulta: ${err.message}`
        );
    }
}

function tituloDeError(codigo) {
    const titulos = {
        ESPECIE_NO_SOPORTADA: 'Especie no soportada',
        PARAMETRO_INVALIDO: 'Dato inválido',
        ACCESO_DENEGADO: 'Acceso Denegado (403)',
        SIN_CONEXION: 'Sin conexión con el servicio',
    };
    return titulos[codigo] || 'Error en la solicitud';
}
