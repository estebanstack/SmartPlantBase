/**
 * Capa de presentación del cliente web.
 * Construye y actualiza el DOM. No sabe que existe HTTP: recibe datos ya
 * resueltos y devuelve lo que el usuario escribió. No conoce URLs ni fetch.
 */
const PlantUI = {
    _el(id) {
        return document.getElementById(id);
    },

    /** Etiqueta legible de un parámetro a partir de su nombre y unidad. */
    _etiqueta(nombre, unidad) {
        const titulo = nombre.charAt(0).toUpperCase() + nombre.slice(1);
        return unidad ? `${titulo} (${unidad})` : titulo;
    },

    /** RF5: llena el selector de especies con el catálogo recibido. */
    poblarSelector(especies) {
        const select = this._el('especie');
        select.innerHTML = '';

        const inicial = document.createElement('option');
        inicial.value = '';
        inicial.disabled = true;
        inicial.selected = true;
        inicial.textContent = 'Selecciona una especie...';
        select.appendChild(inicial);

        especies.forEach((esp) => {
            const option = document.createElement('option');
            option.value = esp.nombre;
            option.textContent = esp.nombre.charAt(0).toUpperCase() + esp.nombre.slice(1);
            select.appendChild(option);
        });
    },

    /**
     * Genera un campo numérico por cada parámetro que la API declara.
     * El front no tiene escrita la lista de variables: la recibe de RF5.
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
            input.required = true;
            input.placeholder = `Valor en ${unidad || 'unidades'}`;

            grupo.appendChild(label);
            grupo.appendChild(input);
            contenedor.appendChild(grupo);
        });
    },

    /** Devuelve lo que el usuario escribió: {especie, valores}. */
    leerFormulario() {
        const valores = {};
        this._el('campos-medicion')
            .querySelectorAll('input[data-parametro]')
            .forEach((input) => {
                const crudo = input.value.trim();
                valores[input.dataset.parametro] = crudo === '' ? null : Number(crudo);
            });

        return { especie: this._el('especie').value, valores };
    },

    /** Resalta el campo señalado por el backend en un error de RF6. */
    marcarCampo(nombre) {
        this._el('campos-medicion')
            .querySelectorAll('input[data-parametro]')
            .forEach((input) => input.classList.remove('campo-invalido'));

        if (!nombre) return;
        const input = this._el(`param-${nombre}`);
        if (input) {
            input.classList.add('campo-invalido');
            input.focus();
        }
    },

    /** RF2, RF3, RF4: pinta el diagnóstico devuelto por el servicio. */
    renderizarDiagnostico(diagnostico) {
        const tarjeta = this._el('resultado-container');
        tarjeta.classList.remove('state-saludable', 'state-en_riesgo', 'state-critico');

        const presentacion = this._presentacionDeEstado(diagnostico.estado);
        tarjeta.classList.add(presentacion.clase);
        this._el('status-icon').textContent = presentacion.icono;
        this._el('status-badge').textContent = diagnostico.estado;
        this._el('status-title').textContent = presentacion.titulo;
        this._el('status-summary').textContent =
            `Diagnóstico para la especie ${diagnostico.especie.toUpperCase()}`;

        this._renderRecomendaciones(diagnostico.recomendaciones);
        this._renderParametros(diagnostico.parametros);

        this._el('empty-state').classList.add('hidden');
        this._el('result-content').classList.remove('hidden');
    },

    /**
     * Traduce un estado del dominio a su representación visual.
     * El caso por defecto evita que un estado nuevo se muestre como CRITICO.
     */
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

    _renderRecomendaciones(recomendaciones) {
        const lista = this._el('observations-list');
        lista.innerHTML = '';

        if (!recomendaciones || recomendaciones.length === 0) {
            const li = document.createElement('li');
            li.className = 'obs-OK';
            li.textContent = '✓ Todos los parámetros están dentro del rango óptimo. No se requieren ajustes.';
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
            estado.className = `status-badge obs-${param.estado}`;
            estado.style.cssText = 'margin-top:0.3rem; display:inline-block;';
            estado.textContent = param.estado;

            const optimo = document.createElement('span');
            optimo.className = 'range-label';
            optimo.style.cssText = 'font-size:0.7rem; margin-top:0.2rem;';
            optimo.textContent = `Óptimo: ${param.rangoOptimo[0]} - ${param.rangoOptimo[1]}`;

            [etiqueta, valor, estado, optimo].forEach((n) => item.appendChild(n));
            grid.appendChild(item);
        });
    },

    /** RF6: muestra el error de forma visible, sin volcar JSON en pantalla. */
    mostrarError(titulo, mensaje) {
        this._el('error-title').textContent = `⚠️ ${titulo}`;
        this._el('error-message').textContent = mensaje;
        this._el('error-banner').classList.remove('hidden');
    },

    ocultarError() {
        this._el('error-banner').classList.add('hidden');
        this.marcarCampo(null);
    },

    /** Estado de carga del botón, sin reconstruir su contenido. */
    setCargando(cargando) {
        const boton = this._el('btn-evaluar');
        const texto = this._el('btn-evaluar-texto');
        boton.disabled = cargando;
        texto.textContent = cargando ? 'Evaluando...' : 'Evaluar diagnóstico';
    },

    deshabilitarFormulario(mensaje) {
        const select = this._el('especie');
        select.innerHTML = `<option value="" disabled selected>${mensaje}</option>`;
        this._el('btn-evaluar').disabled = true;
    },
};
