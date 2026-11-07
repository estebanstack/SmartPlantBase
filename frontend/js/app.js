/**
 * Orquestación del cliente web.
 * Une los eventos de la página con la API REST (api.js), el canal WebSocket en
 * tiempo real (Socket.IO) y la presentación (ui.js):
 * - Sesión de usuario con JWT (R7).
 * - Vinculación de dispositivos vía sesión QR en sala WebSocket 'qr_{session_id}'.
 * - Telemetría y alertas botánicas en vivo mediante sala WebSocket 'user_{usuario_id}' (R5, R6).
 * - Diagnóstico manual de la fase anterior (R1).
 */

const sesion = { token: null, usuario: null };
let plantas = [];
let socket = null;
let sesionQRActual = null;
let historialActual = [];

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
    document.getElementById('btn-qr-dispositivo').addEventListener('click', iniciarVinculacionQRDispositivo);
    document.getElementById('btn-autorizar-qr').addEventListener('click', autorizarVinculacionQRDispositivo);
    document.getElementById('btn-copiar-comando').addEventListener('click', () => copiar('qr-comando'));
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
// Sesión y Canal WebSocket Post-Auth (R7)
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
    conectarWebSocketUsuario();
    cargarPlantas();
}

function cerrarSesion(mensaje) {
    desconectarWebSocket();
    sesion.token = null;
    sesion.usuario = null;
    plantas = [];
    sesionQRActual = null;
    historialActual = [];
    guardarSesion();
    PlantUI.mostrarSinSesion();
    if (mensaje) PlantUI.mostrarError('Sesión cerrada', mensaje);
}

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
// Conexión WebSocket Dual: Sala QR (qr_{id}) y Sala Usuario (user_{id})
// ---------------------------------------------------------------------------

function conectarWebSocketUsuario() {
    desconectarWebSocket();
    if (typeof io === 'undefined' || !sesion.usuario) {
        return;
    }

    socket = io(urlBackend(), { transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        socket.emit(
            'unirse_canal_usuario',
            { usuario_id: sesion.usuario.id, token_usuario: sesion.token },
            () => {
                PlantUI.mostrarEstadoPolling('Sincronización en vivo activa', true);
            }
        );
        if (sesionQRActual && sesionQRActual.id) {
            socket.emit('unirse_sesion_qr', { session_id: sesionQRActual.id });
        }
    });

    socket.on('disconnect', () => {
        PlantUI.mostrarEstadoPolling('Reconectando...', false);
    });

    socket.on('qr_autorizado', (datos) => {
        if (sesionQRActual && datos && datos.id === sesionQRActual.id) {
            sesionQRActual = datos;
            PlantUI.actualizarEstadoQR('AUTORIZADA');
            PlantUI.mostrarAviso(
                `Dispositivo '${datos.dispositivo_id || datos.id}' vinculado correctamente.`
            );
        }
    });

    socket.on('telemetria_actualizada', (payload) => {
        const seleccionadaId = PlantUI.plantaSeleccionada();
        if (!payload || (payload.planta_id && payload.planta_id !== seleccionadaId)) {
            return;
        }
        const planta = plantas.find((p) => p.id === seleccionadaId);
        if (!planta) return;

        if (payload.ultima_lectura && payload.diagnostico) {
            PlantUI.renderizarEstadoEnVivo({
                planta,
                ultima_lectura: payload.ultima_lectura,
                diagnostico: payload.diagnostico,
            });
            const nuevoRegistro = {
                ...payload.ultima_lectura,
                estado_planta: payload.estado,
            };
            historialActual = [nuevoRegistro, ...historialActual].slice(0, CONFIG.LECTURAS_EN_HISTORIAL);
            PlantUI.renderizarHistorial(historialActual);
            PlantUI.mostrarEstadoPolling(
                `Actualizado a las ${new Date().toLocaleTimeString()}`,
                true
            );
        } else {
            cargarEstadoEHistorialInicial(seleccionadaId);
        }
    });

    socket.on('alerta_planta', (alerta) => {
        if (!alerta) return;
        const nombrePlanta = alerta.planta_nombre || alerta.especie || 'Planta';
        const rec = (alerta.recomendaciones && alerta.recomendaciones[0]) || 'Revisa los parámetros ambientales.';
        PlantUI.mostrarError(`Atención en ${nombrePlanta} (${alerta.estado})`, rec);
    });
}

function desconectarWebSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
}

// ---------------------------------------------------------------------------
// Plantas y Vinculación QR por WebSocket (R7)
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
    const planta = plantas.find((p) => p.id === plantaId);
    if (!planta) return;
    PlantUI.prepararPanelEnVivo(planta);
    cargarEstadoEHistorialInicial(planta.id);
}

async function cargarEstadoEHistorialInicial(plantaId) {
    if (!sesion.token) return;
    try {
        const [estado, historial] = await Promise.all([
            PlantApi.obtenerEstadoPlanta(sesion.token, plantaId),
            PlantApi.obtenerHistorialPlanta(sesion.token, plantaId, CONFIG.LECTURAS_EN_HISTORIAL),
        ]);
        historialActual = historial;
        PlantUI.renderizarEstadoEnVivo(estado);
        PlantUI.renderizarHistorial(historial);
        PlantUI.mostrarEstadoPolling(
            `Actualizado a las ${new Date().toLocaleTimeString()}`,
            true
        );
    } catch (error) {
        if (error.status === 401) {
            cerrarSesion('Tu sesión expiró. Inicia sesión otra vez.');
        } else {
            PlantUI.mostrarEstadoPolling(`No se pudo actualizar: ${error.message}`, false);
        }
    }
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
        await cargarPlantas(respuesta.planta.id);
        await abrirSesionQRParaPlanta(respuesta.planta);
        PlantUI.mostrarAviso(
            `Planta "${respuesta.planta.nombre}" registrada. Confirma la vinculación de su dispositivo.`
        );
    } catch (error) {
        manejarError(error);
    }
}

async function iniciarVinculacionQRDispositivo() {
    const plantaId = PlantUI.plantaSeleccionada();
    const planta = plantas.find((p) => p.id === plantaId);
    if (!planta) return;
    try {
        await abrirSesionQRParaPlanta(planta);
    } catch (error) {
        manejarError(error);
    }
}

async function abrirSesionQRParaPlanta(planta) {
    const sesionQR = await PlantApi.generarSesionQR(
        planta.dispositivo_id,
        planta.dispositivo_id,
        planta.id
    );
    sesionQRActual = sesionQR;
    if (socket && socket.connected) {
        socket.emit('unirse_sesion_qr', { session_id: sesionQR.id });
    }
    PlantUI.mostrarSesionQRDispositivo(planta.dispositivo_id, sesionQR, urlBackend());
}

async function autorizarVinculacionQRDispositivo() {
    if (!sesionQRActual) return;
    const plantaId = sesionQRActual.planta_id || PlantUI.plantaSeleccionada();
    if (!plantaId) return;

    if (socket && socket.connected) {
        socket.emit(
            'autorizar_qr',
            {
                session_id: sesionQRActual.id,
                planta_id: plantaId,
                token_usuario: sesion.token,
            },
            (ack) => {
                if (ack && ack.status === 'ok' && ack.sesion) {
                    sesionQRActual = ack.sesion;
                    PlantUI.actualizarEstadoQR('AUTORIZADA');
                    PlantUI.mostrarAviso(
                        `Dispositivo '${ack.sesion.dispositivo_id}' vinculado correctamente.`
                    );
                } else if (ack && ack.error) {
                    PlantUI.mostrarError('No se pudo vincular el dispositivo', ack.mensaje || ack.error);
                }
            }
        );
        return;
    }

    try {
        const autorizada = await PlantApi.autorizarSesionQR(sesion.token, sesionQRActual.id, plantaId);
        sesionQRActual = autorizada;
        PlantUI.actualizarEstadoQR(autorizada.estado);
        PlantUI.mostrarAviso(`Dispositivo '${autorizada.dispositivo_id}' vinculado correctamente.`);
    } catch (error) {
        manejarError(error);
    }
}

/** El simulador y Socket.IO necesitan la URL del backend sin el sufijo /api. */
function urlBackend() {
    return CONFIG.API_BASE.replace(/\/api\/?$/, '');
}

async function copiar(idCampo) {
    const campo = document.getElementById(idCampo);
    try {
        await navigator.clipboard.writeText(campo.value);
        PlantUI.mostrarAviso('Comando copiado al portapapeles.');
    } catch (_) {
        campo.select();
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
        SESION_QR_NO_ENCONTRADA: 'Sesión QR no encontrada',
        SESION_QR_INVALIDA: 'Sesión QR expirada o ya utilizada',
        ACCESO_DENEGADO: 'Acceso denegado (403): esa planta no es tuya',
        SIN_CONEXION: 'Sin conexión con el servicio',
    };
    return titulos[error.codigo] || `Error en la solicitud (${error.status || '?'})`;
}
