/**
 * Capa de acceso a la API (cliente HTTP).
 * Construye las peticiones asíncronas con cabeceras Bearer cuando se requiere.
 * No toca el DOM ni conoce ningún elemento visual.
 */

class ApiError extends Error {
    constructor(codigo, mensaje, campo = null, status = 0) {
        super(mensaje);
        this.codigo = codigo;
        this.campo = campo;
        this.status = status;
    }
}

const PlantApi = {
    /** R1: catálogo de especies soportadas con sus rangos de referencia. */
    async obtenerEspecies() {
        return this._pedir(`${CONFIG.API_BASE}/v1/especies`);
    },

    /** R1: envía una medición manual y devuelve el diagnóstico. */
    async evaluarDiagnostico(especie, valores) {
        return this._pedir(`${CONFIG.API_BASE}/v1/diagnosticos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ especie, ...valores }),
        });
    },

    /** R7: inicio de sesión y obtención de JWT. */
    async login(email, password) {
        return this._pedir(`${CONFIG.API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
    },

    /** R7: listar plantas del usuario autenticado. */
    async obtenerPlantas(token) {
        return this._pedir(`${CONFIG.API_BASE}/plantas`, {
            headers: { Authorization: `Bearer ${token}` },
        });
    },

    /** R5, R6: consultar estado en vivo y última lectura de una planta. */
    async obtenerEstadoPlanta(plantaId, token) {
        return this._pedir(`${CONFIG.API_BASE}/plantas/${plantaId}/estado`, {
            headers: { Authorization: `Bearer ${token}` },
        });
    },

    /** R5: consultar lecturas históricas de una planta. */
    async obtenerHistorialPlanta(plantaId, token, limite = 10) {
        return this._pedir(`${CONFIG.API_BASE}/plantas/${plantaId}/historial?limite=${limite}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
    },

    /** Petición genérica con traducción uniforme de errores. */
    async _pedir(url, opciones = {}) {
        let respuesta;
        try {
            respuesta = await fetch(url, opciones);
        } catch (fallo) {
            throw new ApiError(
                'SIN_CONEXION',
                `No fue posible comunicarse con el backend en ${CONFIG.API_BASE}. Verifica que app.py esté corriendo.`,
                null,
                0
            );
        }

        const datos = await respuesta.json().catch(() => null);

        if (!respuesta.ok) {
            const codigo = (datos && datos.error) || 'ERROR_DESCONOCIDO';
            const mensaje = (datos && datos.mensaje) || `Error HTTP ${respuesta.status}`;
            const campo = (datos && datos.detalle && (datos.detalle.campo || datos.detalle.especie)) || null;
            throw new ApiError(codigo, mensaje, campo, respuesta.status);
        }

        return datos;
    },
};
