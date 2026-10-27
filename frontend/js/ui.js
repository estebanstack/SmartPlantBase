/**
 * Capa de presentación del cliente web.
 * Construye y actualiza el DOM. No sabe que existe HTTP: recibe datos ya
 * resueltos y devuelve lo que el usuario escribió. No conoce URLs ni fetch.
 */
const PlantUI = {
    _el(id) {
        return document.getElementById(id);
    },

    _capitalizar(texto) {
        return texto ? texto.charAt(0).toUpperCase() + texto.slice(1) : '';
    },

    /** Etiqueta legible de un parámetro a partir de su nombre y unidad. */
    _etiqueta(nombre, unidad) {
        const titulo = this._capitalizar(nombre);
        return unidad ? `${titulo} (${unidad})` : titulo;
    },

    _mostrar(id, visible) {
        this._el(id).classList.toggle('hidden', !visible);
    },

    // ------------------------------------------------------------------
    // Avisos y errores (RF6)
    // ------------------------------------------------------------------

    /** Muestra un error de forma visible, sin volcar JSON en pantalla. */
    mostrarError(titulo, mensaje) {
        this._mostrar('aviso-banner', false);
        this._el('error-title').textContent = `⚠️ ${titulo}`;
        this._el('error-message').textContent = mensaje;
        this._mostrar('error-banner', true);
    },

    mostrarAviso(mensaje) {
        this._mostrar('error-banner', false);
        this._el('aviso-message').textContent = mensaje;
        this._mostrar('aviso-banner', true);
    },

    ocultarMensajes() {
        this._mostrar('error-banner', false);
        this._mostrar('aviso-banner', false);
        this.marcarCampo(null);
    },

    /** Resalta el campo que el backend señaló en el error. */
    marcarCampo(nombre) {
        document.querySelectorAll('.campo-invalido').forEach((n) => n.classList.remove('campo-invalido'));
        if (!nombre) return;
        const candidato = document.querySelector(
            `#param-${nombre}, form:not(.hidden) [name="${nombre}"]`
        );
        if (candidato) {
            candidato.classList.add('campo-invalido');
            candidato.focus();
        }
    },

    // ------------------------------------------------------------------
    // Sesión (R7)
    // ------------------------------------------------------------------

    mostrarPestanaAuth(pestana) {
        const esLogin = pestana === 'login';
        this._mostrar('form-login', esLogin);
        this._mostrar('form-registro', !esLogin);
        this._el('tab-login').classList.toggle('activa', esLogin);
        this._el('tab-registro').classList.toggle('activa', !esLogin);
    },

    leerLogin() {
        return {
            email: this._el('login-email').value.trim(),
            password: this._el('login-password').value,
        };
    },

    leerRegistro() {
        return {
            nombre: this._el('registro-nombre').value.trim(),
            email: this._el('registro-email').value.trim(),
            password: this._el('registro-password').value,
        };
    },

    mostrarSesion(usuario) {
        this._el('sesion-usuario').textContent = `${usuario.nombre} · ${usuario.email}`;
        this._mostrar('auth-panel', false);
        ['sesion-bar', 'plantas-panel'].forEach((id) => this._mostrar(id, true));
        this._el('form-login').reset();
        this._el('form-registro').reset();
        this.habilitarDiagnostico(true);
    },

    mostrarSinSesion() {
        this._mostrar('auth-panel', true);
        ['sesion-bar', 'plantas-panel', 'live-panel', 'token-box'].forEach((id) => this._mostrar(id, false));
        this.habilitarDiagnostico(false);
    },

    // ------------------------------------------------------------------
    // Catálogo y diagnóstico manual (R1)
    // ------------------------------------------------------------------

    /** RF5: llena los selectores de especie con el catálogo recibido. */
    poblarEspecies(especies) {
        ['especie', 'planta-especie'].forEach((id) => {
            const select = this._el(id);
            select.innerHTML = '';
            const inicial = new Option('Selecciona una especie...', '', true, true);
            inicial.disabled = true;
            select.appendChild(inicial);
            especies.forEach((esp) => select.appendChild(new Option(this._capitalizar(esp.nombre), esp.nombre)));
        });
    },

    /**
     * Genera un campo numérico por cada parámetro que declara la API.
     * El front no tiene escrita la lista de variables: la recibe del catálogo.
     */
    construirCamposDeMedicion(parametros) {
        const contenedor = this._el('campos-medicion');
        contenedor.innerHTML = '';
        parametros.forEach(({ nombre, unidad }) => {
            const grupo = document.createElement('div');
            grupo.className = 'form-group';

            const label = document.createElement('label');
            label.htmlFor = `param-${nombre}`;
            label.textContent = this._etiqueta(nombre, unidad);

            const input = document.createElement('input');
            input.type = 'number';
            input.id = `param-${nombre}`;
            input.dataset.parametro = nombre;
            input.step = 'any';
            input.placeholder = `Valor en ${unidad || 'unidades'}`;

            grupo.append(label, input);
            contenedor.appendChild(grupo);
        });
    },

    leerFormularioDiagnostico() {
        const valores = {};
        this._el('campos-medicion').querySelectorAll('input[data-parametro]').forEach((input) => {
            const crudo = input.value.trim();
            valores[input.dataset.parametro] = crudo === '' ? null : Number(crudo);
        });
        return { especie: this._el('especie').value, valores };
    },

    habilitarDiagnostico(habilitado) {
        this._el('btn-evaluar').disabled = !habilitado;
        this._el('btn-evaluar-texto').textContent = habilitado
            ? 'Evaluar lectura manual'
            : 'Inicia sesión para evaluar';
    },

    setCargandoDiagnostico(cargando) {
        this._el('btn-evaluar').disabled = cargando;
        this._el('btn-evaluar-texto').textContent = cargando ? 'Evaluando...' : 'Evaluar lectura manual';
    },

    deshabilitarCatalogo(mensaje) {
        ['especie', 'planta-especie'].forEach((id) => {
            this._el(id).innerHTML = `<option value="" disabled selected>${mensaje}</option>`;
        });
    },

    /** RF2, RF3, RF4: pinta el diagnóstico manual. */
    renderizarDiagnostico(diagnostico) {
        const tarjeta = this._el('resultado-container');
        tarjeta.classList.remove('state-saludable', 'state-en_riesgo', 'state-critico');

        const presentacion = this._presentacionDeEstado(diagnostico.estado);
        if (presentacion.clase) tarjeta.classList.add(presentacion.clase);
        this._el('status-icon').textContent = presentacion.icono;
        this._el('status-badge').textContent = diagnostico.estado;
        this._el('status-title').textContent = presentacion.titulo;
        this._el('status-summary').textContent = `Diagnóstico para la especie ${diagnostico.especie.toUpperCase()}`;

        this._renderRecomendaciones(this._el('observations-list'), diagnostico.recomendaciones);
        this._renderParametros(diagnostico.parametros);

        this._mostrar('empty-state', false);
        this._mostrar('result-content', true);
    },

    /** Traduce un estado del dominio a su representación visual. */
    _presentacionDeEstado(estado) {
        switch (estado) {
            case 'SALUDABLE':
                return { icono: '🌿', clase: 'state-saludable', titulo: 'Estado: Saludable' };
            case 'EN_RIESGO':
                return { icono: '⚠️', clase: 'state-en_riesgo', titulo: 'Estado: En riesgo' };
            case 'CRITICO':
                return { icono: '🥀', clase: 'state-critico', titulo: 'Estado: Crítico' };
            default:
                return { icono: '🪴', clase: '', titulo: `Estado: ${estado}` };
        }
    },

    _renderRecomendaciones(lista, recomendaciones) {
        lista.innerHTML = '';
        if (!recomendaciones || recomendaciones.length === 0) {
            const li = document.createElement('li');
            li.className = 'obs-OK';
            li.textContent = '✓ Todos los parámetros están dentro del rango óptimo.';
            lista.appendChild(li);
            return;
        }
        recomendaciones.forEach((texto) => {
            const li = document.createElement('li');
            li.className = 'obs-BAJO';
            li.textContent = texto;
            lista.appendChild(li);
        });
    },

    _renderParametros(parametros) {
        const grid = this._el('ranges-grid');
        grid.innerHTML = '';
        parametros.forEach((param) => {
            const item = document.createElement('div');
            item.className = 'range-item';

            const etiqueta = document.createElement('span');
            etiqueta.className = 'range-label';
            etiqueta.textContent = this._etiqueta(param.nombre, param.unidad);

            const valor = document.createElement('span');
            valor.className = 'range-val';
            valor.textContent = `${param.valor} ${param.unidad}`;

            const estado = document.createElement('span');
            estado.className = `chip chip-${param.estado}`;
            estado.textContent = param.estado;

            const optimo = document.createElement('span');
            optimo.className = 'range-label pequeno';
            optimo.textContent = `Óptimo: ${param.rango_optimo[0]} - ${param.rango_optimo[1]}`;

            item.append(etiqueta, valor, estado, optimo);
            grid.appendChild(item);
        });
    },

    // ------------------------------------------------------------------
    // Plantas del usuario y token del dispositivo (R7)
    // ------------------------------------------------------------------

    poblarPlantas(plantas, seleccionadaId) {
        const select = this._el('planta-select');
        select.innerHTML = '';
        if (plantas.length === 0) {
            select.appendChild(new Option('Aún no tienes plantas: registra una', '', true, true));
            select.disabled = true;
            this._el('btn-token-dispositivo').disabled = true;
            return;
        }
        select.disabled = false;
        this._el('btn-token-dispositivo').disabled = false;
        plantas.forEach((p) => {
            const texto = `${p.nombre} · ${this._capitalizar(p.especie)} · ${p.dispositivo_id}`;
            select.appendChild(new Option(texto, p.id, false, p.id === seleccionadaId));
        });
    },

    plantaSeleccionada() {
        return this._el('planta-select').value || null;
    },

    leerNuevaPlanta() {
        return {
            nombre: this._el('planta-nombre').value.trim(),
            especie: this._el('planta-especie').value,
            dispositivoId: this._el('planta-dispositivo').value.trim(),
        };
    },

    limpiarNuevaPlanta() {
        this._el('form-planta').reset();
    },

    /** Muestra el token del dispositivo y el comando listo para el simulador. */
    mostrarTokenDispositivo(dispositivoId, token, urlBackend) {
        this._el('token-dispositivo-id').textContent = dispositivoId;
        this._el('token-valor').value = token;
        this._el('token-comando').value =
            `python simulador_esp32.py --url ${urlBackend} --dispositivo-id ${dispositivoId} --token ${token}`;
        this._mostrar('token-box', true);
    },

    // ------------------------------------------------------------------
    // Panel en vivo e historial (R5, R6)
    // ------------------------------------------------------------------

    prepararPanelEnVivo(planta) {
        this._el('live-plant-title').textContent = `🌿 ${planta.nombre} (${this._capitalizar(planta.especie)})`;
        this._el('live-dispositivo').textContent = `Dispositivo: ${planta.dispositivo_id}`;
        this._el('live-status').textContent = 'Consultando...';
        this._el('live-status').className = 'metric-valor';
        ['live-humedad', 'live-luz', 'live-temperatura'].forEach((id) => (this._el(id).textContent = '--'));
        this._el('live-marca').textContent = 'Última lectura: --';
        this._el('live-recs').innerHTML = '';
        this._el('historial-body').innerHTML = '';
        this._mostrar('live-panel', true);
    },

    renderizarEstadoEnVivo(estado) {
        const status = this._el('live-status');
        if (!estado.ultima_lectura) {
            status.textContent = 'SIN LECTURAS AÚN';
            status.className = 'metric-valor';
            this._el('live-recs').innerHTML = '';
            const li = document.createElement('li');
            li.className = 'obs-OK';
            li.textContent = 'Arranca el simulador con el token del dispositivo para ver lecturas aquí.';
            this._el('live-recs').appendChild(li);
            return;
        }

        const v = estado.ultima_lectura.valores || {};
        this._el('live-humedad').textContent = `${v.humedad ?? '--'} %`;
        this._el('live-luz').textContent = `${v.luz ?? '--'} lux`;
        this._el('live-temperatura').textContent = `${v.temperatura ?? '--'} °C`;
        this._el('live-marca').textContent = `Última lectura: ${this._formatearFecha(estado.ultima_lectura.marca_tiempo)}`;

        if (estado.diagnostico) {
            status.textContent = estado.diagnostico.estado;
            status.className = `metric-valor texto-${estado.diagnostico.estado}`;
            this._renderRecomendaciones(this._el('live-recs'), estado.diagnostico.recomendaciones);
        }
    },

    renderizarHistorial(registros) {
        const cuerpo = this._el('historial-body');
        cuerpo.innerHTML = '';
        if (registros.length === 0) {
            const fila = cuerpo.insertRow();
            const celda = fila.insertCell();
            celda.colSpan = 5;
            celda.className = 'tabla-vacia';
            celda.textContent = 'Todavía no hay lecturas guardadas.';
            return;
        }
        registros.forEach((r) => {
            const fila = cuerpo.insertRow();
            const v = r.valores || {};
            [this._formatearFecha(r.marca_tiempo), v.humedad, v.luz, v.temperatura].forEach((dato) => {
                fila.insertCell().textContent = dato ?? '--';
            });
            const chip = document.createElement('span');
            chip.className = `chip chip-${r.estado_planta}`;
            chip.textContent = r.estado_planta;
            fila.insertCell().appendChild(chip);
        });
    },

    /** Línea de estado del polling: así un fallo de red se ve en pantalla, no solo en consola. */
    mostrarEstadoPolling(texto, ok) {
        const linea = this._el('poll-status');
        linea.textContent = texto;
        linea.classList.toggle('poll-error', !ok);
    },

    _formatearFecha(iso) {
        if (!iso) return '--';
        const fecha = new Date(iso);
        return Number.isNaN(fecha.getTime()) ? iso : fecha.toLocaleString();
    },
};
