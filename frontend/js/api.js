/**
 * Capa de acceso a la API (cliente HTTP).
 * Arma las peticiones fetch, agrega el token Bearer cuando hace falta
 * y convierte cualquier error en un ApiError uniforme. No toca el DOM.
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
    // --- Catálogo (público) ---------------------------------------------
    /** R1: especies soportadas con sus rangos de referencia. */
    obtenerEspecies() {
        return this._pedir('/v1/especies');
    },

    // --- Sesión (R7) ----------------------------------------------------
    registrarUsuario(nombre, email, password) {
        return this._pedir('/auth/registro', { metodo: 'POST', cuerpo: { nombre, email, password } });
    },

    iniciarSesion(email, password) {
        return this._pedir('/auth/login', { metodo: 'POST', cuerpo: { email, password } });
    },

    // --- Diagnóstico manual (R1, exige sesión) --------------------------
    evaluarDiagnostico(token, especie, valores) {
        return this._pedir('/v1/diagnosticos', { metodo: 'POST', token, cuerpo: { especie, ...valores } });
    },

    // --- Plantas (R5, R6, R7) -------------------------------------------
    obtenerPlantas(token) {
        return this._pedir('/plantas', { token });
    },

    registrarPlanta(token, nombre, especie, dispositivoId) {
        return this._pedir('/plantas', {
            metodo: 'POST',
            token,
            cuerpo: { nombre, especie, dispositivo_id: dispositivoId },
        });
    },

    obtenerTokenDispositivo(token, plantaId) {
        return this._pedir(`/plantas/${encodeURIComponent(plantaId)}/token-dispositivo`, { metodo: 'POST', token });
    },

    obtenerEstadoPlanta(token, plantaId) {
        return this._pedir(`/plantas/${encodeURIComponent(plantaId)}/estado`, { token });
    },

    obtenerHistorialPlanta(token, plantaId, limite) {
        return this._pedir(`/plantas/${encodeURIComponent(plantaId)}/historial?limite=${limite}`, { token });
    },

    // --- Petición genérica ----------------------------------------------
    async _pedir(ruta, { metodo = 'GET', token = null, cuerpo = null } = {}) {
        const cabeceras = {};
        if (cuerpo !== null) cabeceras['Content-Type'] = 'application/json';
        if (token) cabeceras.Authorization = `Bearer ${token}`;

        let respuesta;
        try {
            respuesta = await fetch(`${CONFIG.API_BASE}${ruta}`, {
                method: metodo,
                headers: cabeceras,
                body: cuerpo !== null ? JSON.stringify(cuerpo) : undefined,
            });
        } catch (fallo) {
            throw new ApiError(
                'SIN_CONEXION',
                `No fue posible comunicarse con el backend en ${CONFIG.API_BASE}. Verifica que app.py esté corriendo.`
            );
        }

        const datos = await respuesta.json().catch(() => null);
        if (!respuesta.ok) {
            const detalle = (datos && datos.detalle) || {};
            throw new ApiError(
                (datos && datos.error) || 'ERROR_DESCONOCIDO',
                (datos && datos.mensaje) || `Error HTTP ${respuesta.status}`,
                detalle.campo || null,
                respuesta.status
            );
        }
        return datos;
    },
};
