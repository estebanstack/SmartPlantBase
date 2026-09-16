/**
 * Orquestación del cliente web (RA2).
 * Une las dos capas del front: pide datos a PlantApi y se los entrega a PlantUI.
 * No contiene reglas de diagnóstico ni conoce URLs ni selectores del DOM.
 */
document.addEventListener('DOMContentLoaded', () => {
    inicializar();

    document.getElementById('plant-form').addEventListener('submit', async (evento) => {
        evento.preventDefault(); // RA2: la página no se recarga
        await evaluar();
    });
});

/** Carga el catálogo (RF5) y arma el formulario a partir de lo que declara la API. */
async function inicializar() {
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

/**
 * Deriva la lista de parámetros medibles del catálogo de especies.
 * El front no tiene la lista escrita: si el backend agrega una variable,
 * el formulario la incorpora sin modificar este archivo.
 */
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

/** Envía la medición y muestra el diagnóstico o el error (RF6). */
async function evaluar() {
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

/** Título legible para cada código de error uniforme de RF6. */
function tituloDeError(codigo) {
    const titulos = {
        ESPECIE_NO_SOPORTADA: 'Especie no soportada',
        PARAMETRO_INVALIDO: 'Dato inválido',
        SIN_CONEXION: 'Sin conexión con el servicio',
    };
    return titulos[codigo] || 'Error en la solicitud';
}
