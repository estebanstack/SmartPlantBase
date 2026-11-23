/**
 * Configuración del cliente web.
 * Único lugar del front que conoce la dirección de la API.
 *
 * Si la página la sirve el propio backend (http://<ip-del-portátil>:5000/), la API está en el
 * mismo origen: así funciona igual desde el portátil y desde el celular sin cambiar nada.
 * Solo si se abre el archivo directamente (file://) se usa la dirección local por defecto.
 */
const CONFIG = {
    API_BASE: window.location.protocol.startsWith('http')
        ? `${window.location.origin}/api`
        : 'http://127.0.0.1:5000/api',
    INTERVALO_POLLING_MS: 3000,
    LECTURAS_EN_HISTORIAL: 10,
};
