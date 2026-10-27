/**
 * Orquestación del cliente web.
 * Une los eventos de la página con la API (api.js) y la presentación (ui.js):
 * sesión con JWT (R7), plantas del usuario, polling periódico del estado e
 * historial (R5, R6) y el diagnóstico manual de la fase anterior (R1).
 */

const sesion = { token: null, usuario: null };
let plantas = [];
let intervaloPolling = null;
let consultaEnCurso = false;

document.addEventListener('DOMContentLoaded', () => {
    conectarEventos();
    cargarCatalogo();
    restaurarSesion();
});

function conectarEventos() {
    document.getElementById('tab-login').addEventListener('click', () => PlantUI.mostrarPestanaAuth('login'));
    document.getElementById('tab-registro').addEventListener('click', () => PlantUI.mostrarPestanaAuth('registro'));
    alEnviar('form-login', iniciarSesion);
    alEnviar('form-registro', registrarUsuario);
    alEnviar('form-planta', registrarPlanta);
    alEnviar('form-diagnostico', evaluarManual);
    alEnviar('form-ajena', probarPlantaAjena);
    document.getElementById('btn-logout').addEventListener('click', () => cerrarSesion());
    document.getElementById('planta-select').addEventListener('change', () => seleccionarPlanta(PlantUI.plantaSeleccionada()));
    document.getElementById('btn-token-dispositivo').addEventListener('click', pedirTokenDispositivo);
    document.getElementById('btn-copiar-comando').addEventListener('click', () => copiar('token-comando'));
    document.getElementById('btn-copiar-token').addEventListener('click', () => copiar('token-valor'));
}

/** Evita que el formulario recargue la página (RA2) y llama a la acción. */
function alEnviar(idFormulario, accion) {
    document.getElementById(idFormulario).addEventListener('submit', async (evento) => {
        evento.preventDefault();
        PlantUI.ocultarMensajes();
        await accion();
    });
}

// ---------------------------------------------------------------------------
// Catálogo (R1)
// ---------------------------------------------------------------------------

async function cargarCatalogo() {
    try {
        const especies = await PlantApi.obtenerEspecies();
        PlantUI.poblarEspecies(especies);
        PlantUI.construirCamposDeMedicion(parametrosDe(especies));
    } catch (error) {
        PlantUI.mostrarError('No se pudo cargar el catálogo', error.message);
        PlantUI.deshabilitarCatalogo('Catálogo no disponible');
    }
}

function parametrosDe(especies) {
    const vistos = new Map();
    especies.forEach((esp) => {
        Object.entries(esp.rangos || {}).forEach(([nombre, rango]) => {
            if (!vistos.has(nombre)) vistos.set(nombre, { nombre, unidad: rango.unidad });
        });
    });
    return Array.from(vistos.values());
}

// ---------------------------------------------------------------------------
// Sesión (R7)
// ---------------------------------------------------------------------------

async function iniciarSesion() {
    const { email, password } = PlantUI.leerLogin();
    try {
        abrirSesion(await PlantApi.iniciarSesion(email, password));
    } catch (error) {
        manejarError(error);
    }
}

async function registrarUsuario() {
    const { nombre, email, password } = PlantUI.leerRegistro();
    try {
        abrirSesion(await PlantApi.registrarUsuario(nombre, email, password));
        PlantUI.mostrarAviso('Cuenta creada. Ahora registra tu primera planta.');
    } catch (error) {
        manejarError(error);
    }
}

function abrirSesion({ token, usuario }) {
    sesion.token = token;
    sesion.usuario = usuario;
    guardarSesion();
    PlantUI.mostrarSesion(usuario);
    cargarPlantas();
}

function cerrarSesion(mensaje) {
    detenerPolling();
    sesion.token = null;
    sesion.usuario = null;
    plantas = [];
    guardarSesion();
    PlantUI.mostrarSinSesion();
    if (mensaje) PlantUI.mostrarError('Sesión cerrada', mensaje);
}

/** La sesión se guarda solo en esta pestaña (sessionStorage) para no perderla al recargar. */
function guardarSesion() {
    try {
        if (sesion.token) sessionStorage.setItem('matera-sesion', JSON.stringify(sesion));
        else sessionStorage.removeItem('matera-sesion');
    } catch (_) {
        /* sin almacenamiento disponible: la sesión vive solo en memoria */
    }
}

function restaurarSesion() {
    try {
        const guardada = JSON.parse(sessionStorage.getItem('matera-sesion') || 'null');
        if (guardada && guardada.token) {
            abrirSesion(guardada);
            return;
        }
    } catch (_) {
        /* ignorar */
    }
    PlantUI.mostrarSinSesion();
}

// ---------------------------------------------------------------------------
// Plantas y token del dispositivo (R7)
// ---------------------------------------------------------------------------

async function cargarPlantas(seleccionarId = null) {
    try {
        plantas = await PlantApi.obtenerPlantas(sesion.token);
        const elegida = seleccionarId || (plantas[0] && plantas[0].id) || null;
        PlantUI.poblarPlantas(plantas, elegida);
        seleccionarPlanta(elegida);
    } catch (error) {
        manejarError(error);
    }
}

function seleccionarPlanta(plantaId) {
    detenerPolling();
    const planta = plantas.find((p) => p.id === plantaId);
    if (!planta) return;
    PlantUI.prepararPanelEnVivo(planta);
    iniciarPolling(planta.id);
}

async function registrarPlanta() {
    const { nombre, especie, dispositivoId } = PlantUI.leerNuevaPlanta();
    if (!especie) {
        PlantUI.mostrarError('Falta la especie', 'Selecciona la especie de la planta.');
        return;
    }
    try {
        const respuesta = await PlantApi.registrarPlanta(sesion.token, nombre, especie, dispositivoId);
        PlantUI.limpiarNuevaPlanta();
        PlantUI.mostrarAviso(`Planta "${respuesta.planta.nombre}" registrada. Copia el token para su dispositivo.`);
        PlantUI.mostrarTokenDispositivo(respuesta.planta.dispositivo_id, respuesta.token_dispositivo, urlBackend());
        await cargarPlantas(respuesta.planta.id);
    } catch (error) {
        manejarError(error);
    }
}

async function pedirTokenDispositivo() {
    const plantaId = PlantUI.plantaSeleccionada();
    const planta = plantas.find((p) => p.id === plantaId);
    if (!planta) return;
    try {
        const respuesta = await PlantApi.obtenerTokenDispositivo(sesion.token, planta.id);
        PlantUI.mostrarTokenDispositivo(planta.dispositivo_id, respuesta.token_dispositivo, urlBackend());
    } catch (error) {
        manejarError(error);
    }
}

/** El simulador necesita la URL del backend sin el sufijo /api. */
function urlBackend() {
    return CONFIG.API_BASE.replace(/\/api\/?$/, '');
}

async function copiar(idCampo) {
    const campo = document.getElementById(idCampo);
    try {
        await navigator.clipboard.writeText(campo.value);
        PlantUI.mostrarAviso('Copiado al portapapeles.');
    } catch (_) {
        campo.select(); // si el navegador no deja copiar, al menos queda seleccionado
    }
}

// ---------------------------------------------------------------------------
// Polling del estado y el historial (R5, R6)
// ---------------------------------------------------------------------------

function iniciarPolling(plantaId) {
    actualizarPanel(plantaId);
    intervaloPolling = setInterval(() => actualizarPanel(plantaId), CONFIG.INTERVALO_POLLING_MS);
}

function detenerPolling() {
    if (intervaloPolling) clearInterval(intervaloPolling);
    intervaloPolling = null;
}

async function actualizarPanel(plantaId) {
    if (!sesion.token || consultaEnCurso) return;
    consultaEnCurso = true;
    try {
        const [estado, historial] = await Promise.all([
            PlantApi.obtenerEstadoPlanta(sesion.token, plantaId),
            PlantApi.obtenerHistorialPlanta(sesion.token, plantaId, CONFIG.LECTURAS_EN_HISTORIAL),
        ]);
        PlantUI.renderizarEstadoEnVivo(estado);
        PlantUI.renderizarHistorial(historial);
        PlantUI.mostrarEstadoPolling(
            `Actualizado ${new Date().toLocaleTimeString()} · se consulta cada ${CONFIG.INTERVALO_POLLING_MS / 1000} s`,
            true
        );
    } catch (error) {
        if (error.status === 401) {
            cerrarSesion('Tu sesión expiró. Inicia sesión otra vez.');
        } else if (error.codigo === 'SIN_CONEXION') {
            PlantUI.mostrarEstadoPolling('Sin conexión con el backend. Reintentando...', false);
        } else {
            detenerPolling();
            PlantUI.mostrarEstadoPolling(`Consulta detenida: ${error.message}`, false);
        }
    } finally {
        consultaEnCurso = false;
    }
}

// ---------------------------------------------------------------------------
// Intento de acceso a una planta ajena (demostración de R7)
// ---------------------------------------------------------------------------

async function probarPlantaAjena() {
    const plantaId = document.getElementById('ajena-id').value.trim();
    if (!plantaId) return;
    try {
        await PlantApi.obtenerEstadoPlanta(sesion.token, plantaId);
        PlantUI.mostrarAviso(`La planta ${plantaId} es tuya, por eso sí puedes verla.`);
    } catch (error) {
        manejarError(error);
    }
}

// ---------------------------------------------------------------------------
// Diagnóstico manual (R1)
// ---------------------------------------------------------------------------

async function evaluarManual() {
    const { especie, valores } = PlantUI.leerFormularioDiagnostico();
    if (!especie) {
        PlantUI.mostrarError('Falta la especie', 'Selecciona una especie del catálogo antes de evaluar.');
        return;
    }
    try {
        PlantUI.setCargandoDiagnostico(true);
        PlantUI.renderizarDiagnostico(await PlantApi.evaluarDiagnostico(sesion.token, especie, valores));
    } catch (error) {
        manejarError(error);
    } finally {
        PlantUI.setCargandoDiagnostico(false);
    }
}

// ---------------------------------------------------------------------------
// Errores (RF6): todos se muestran igual, con un título según el código
// ---------------------------------------------------------------------------

function manejarError(error) {
    if (error.status === 401 && sesion.token) {
        cerrarSesion('Tu sesión expiró. Inicia sesión otra vez.');
        return;
    }
    PlantUI.mostrarError(tituloDeError(error), error.message);
    PlantUI.marcarCampo(error.campo);
}

function tituloDeError(error) {
    const titulos = {
        ESPECIE_NO_SOPORTADA: 'Especie no soportada',
        PARAMETRO_INVALIDO: 'Dato inválido',
        CREDENCIALES_INVALIDAS: 'Correo o contraseña incorrectos',
        USUARIO_YA_EXISTE: 'Ese correo ya tiene cuenta',
        DISPOSITIVO_YA_VINCULADO: 'Dispositivo ocupado',
        PLANTA_NO_ENCONTRADA: 'Planta no encontrada',
        ACCESO_DENEGADO: 'Acceso denegado (403): esa planta no es tuya',
        SIN_CONEXION: 'Sin conexión con el servicio',
    };
    return titulos[error.codigo] || `Error en la solicitud (${error.status || '?'})`;
}
