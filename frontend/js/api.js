/**
 * Capa de acceso a la API (cliente HTTP).
 * Única parte del front que sabe que existe HTTP: construye las peticiones,
 * interpreta los códigos de estado y devuelve datos ya normalizados.
 * No toca el DOM ni conoce ningún elemento de la página.
 */

/** Error normalizado de la API. La capa de presentación no ve códigos HTTP. */
class ApiError extends Error {
    constructor(codigo, mensaje, campo = null) {
        super(mensaje);
        this.codigo = codigo;
        this.campo = campo;
    }
}

const PlantApi = {
    /** RF5: catálogo de especies soportadas con sus rangos de referencia. */
    async obtenerEspecies() {
        const respuesta = await this._pedir(`${CONFIG.API_BASE}/especies`);
        return respuesta;
    },

    /** RF1-RF4: envía una medición y devuelve el diagnóstico. */
    async evaluarDiagnostico(especie, valores) {
        return this._pedir(`${CONFIG.API_BASE}/diagnosticos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ especie, ...valores }),
        });
    },

    /**
     * Ejecuta la petición y traduce cualquier fallo a un ApiError.
     * Los cuerpos de error de RF6 llegan con la forma {error, mensaje, detalle}.
     */
    async _pedir(url, opciones = {}) {
        let respuesta;
        try {
            respuesta = await fetch(url, opciones);
        } catch (fallo) {
            throw new ApiError(
                'SIN_CONEXION',
                `No fue posible comunicarse con el servicio en ${CONFIG.API_BASE}. Verifica que el backend esté en ejecución.`
            );
        }

        const datos = await respuesta.json().catch(() => null);

        if (!respuesta.ok) {
            const codigo = (datos && datos.error) || 'ERROR_DESCONOCIDO';
            const mensaje = (datos && datos.mensaje) || 'La solicitud no pudo ser procesada.';
            const campo = (datos && datos.detalle && (datos.detalle.campo || datos.detalle.especie)) || null;
            throw new ApiError(codigo, mensaje, campo);
        }

        return datos;
    },
};
