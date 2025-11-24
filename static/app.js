// Estado de la aplicación
let state = {
    sessionId: null,
    hasAudio: false,
    selectedFilter: null,
    originalAudioPath: null,
    filteredAudioPath: null
};

// Referencias a elementos del DOM
const elements = {
    youtubeUrl: document.getElementById('youtube-url'),
    downloadBtn: document.getElementById('download-btn'),
    downloadStatus: document.getElementById('download-status'),
    filterSection: document.getElementById('filter-section'),
    filterBtns: document.querySelectorAll('.filter-btn'),
    customControls: document.getElementById('custom-controls'),
    cutoffFreq: document.getElementById('cutoff-freq'),
    cutoffValue: document.getElementById('cutoff-value'),
    intensity: document.getElementById('intensity'),
    intensityValue: document.getElementById('intensity-value'),
    applyFilterBtn: document.getElementById('apply-filter-btn'),
    filterStatus: document.getElementById('filter-status'),
    playbackSection: document.getElementById('playback-section'),
    originalAudio: document.getElementById('original-audio'),
    filteredAudio: document.getElementById('filtered-audio'),
    visualizationSection: document.getElementById('visualization-section'),
    vizBtns: document.querySelectorAll('[data-viz]'),
    vizImage: document.getElementById('viz-image')
};

// Event Listeners
elements.downloadBtn.addEventListener('click', downloadAudio);
elements.filterBtns.forEach(btn => {
    btn.addEventListener('click', () => selectFilter(btn.dataset.filter));
});
elements.cutoffFreq.addEventListener('input', updateCutoffValue);
elements.intensity.addEventListener('input', updateIntensityValue);
elements.applyFilterBtn.addEventListener('click', applyFilter);
elements.vizBtns.forEach(btn => {
    btn.addEventListener('click', () => showVisualization(btn.dataset.viz));
});

// Funciones
async function downloadAudio() {
    const url = elements.youtubeUrl.value.trim();

    if (!url) {
        showStatus(elements.downloadStatus, 'Por favor ingresa una URL de YouTube', 'error');
        return;
    }

    // Validar URL de YouTube básica
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        showStatus(elements.downloadStatus, 'URL de YouTube no válida', 'error');
        return;
    }

    elements.downloadBtn.disabled = true;
    showStatus(elements.downloadStatus, 'Descargando audio de YouTube...', 'loading');

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url,
                session_id: state.sessionId
            })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(elements.downloadStatus, data.message, 'success');

            // Guardar session_id
            state.sessionId = data.session_id;
            state.hasAudio = true;
            state.originalAudioPath = data.filename;

            // Mostrar sección de filtros
            elements.filterSection.style.display = 'block';

            // Cargar audio original en el reproductor
            elements.originalAudio.src = `/api/audio/${data.filename}`;
            elements.playbackSection.style.display = 'block';

            // Mostrar sección de visualización
            elements.visualizationSection.style.display = 'block';
        } else {
            showStatus(elements.downloadStatus, `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(elements.downloadStatus, `Error de conexión: ${error.message}`, 'error');
    } finally {
        elements.downloadBtn.disabled = false;
    }
}

function selectFilter(filterType) {
    state.selectedFilter = filterType;

    // Actualizar UI de botones
    elements.filterBtns.forEach(btn => {
        if (btn.dataset.filter === filterType) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Mostrar controles personalizados solo para filtros low_pass y high_pass
    if (filterType === 'low_pass' || filterType === 'high_pass') {
        elements.customControls.style.display = 'block';
    } else {
        elements.customControls.style.display = 'none';
    }

    // Habilitar botón de aplicar filtro
    elements.applyFilterBtn.disabled = false;
}

function updateCutoffValue() {
    elements.cutoffValue.textContent = `${elements.cutoffFreq.value} Hz`;
}

function updateIntensityValue() {
    elements.intensityValue.textContent = `${elements.intensity.value}%`;
}

async function applyFilter() {
    if (!state.selectedFilter) {
        showStatus(elements.filterStatus, 'Selecciona un filtro primero', 'error');
        return;
    }

    if (!state.sessionId) {
        showStatus(elements.filterStatus, 'Sesión inválida. Por favor recarga la página.', 'error');
        return;
    }

    elements.applyFilterBtn.disabled = true;
    showStatus(elements.filterStatus, 'Aplicando filtro...', 'loading');

    try {
        const cutoffFreq = parseFloat(elements.cutoffFreq.value);
        const intensity = parseFloat(elements.intensity.value) / 100;

        const response = await fetch('/api/apply_filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filter_type: state.selectedFilter,
                cutoff_freq: cutoffFreq,
                intensity: intensity,
                session_id: state.sessionId
            })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(elements.filterStatus, data.message, 'success');
            state.filteredAudioPath = data.filename;

            // Cargar audio filtrado en el reproductor
            elements.filteredAudio.src = `/api/audio/${data.filename}?t=${Date.now()}`;
            elements.playbackSection.style.display = 'block';
        } else {
            showStatus(elements.filterStatus, `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(elements.filterStatus, `Error de conexión: ${error.message}`, 'error');
    } finally {
        elements.applyFilterBtn.disabled = false;
    }
}

async function showVisualization(vizType) {
    if (!state.hasAudio || !state.sessionId) {
        return;
    }

    try {
        // Mostrar indicador de carga
        elements.vizImage.style.display = 'none';

        const response = await fetch(`/api/visualize/${vizType}?session_id=${state.sessionId}`);

        if (response.ok) {
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);

            elements.vizImage.src = imageUrl;
            elements.vizImage.style.display = 'block';
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error de conexión: ${error.message}`);
    }
}

function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

// Auto-rellenar con un ejemplo para pruebas rápidas (comentar en producción)
// elements.youtubeUrl.value = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
