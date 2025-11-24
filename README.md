# Audio Filter App - Procesamiento de Señales

Aplicación web para procesamiento de señales de audio utilizando convolución, correlación y filtros digitales.

## Características

- 📥 **Descarga de audio desde YouTube**
- 🎛️ **Filtros de frecuencia**:
  - Solo Graves (Bajo + Bombo): 20-250 Hz
  - Solo Medios (Guitarra + Voz): 250-5000 Hz
  - Solo Agudos (Platillos): 5000-20000 Hz
  - Filtro Pasa-Bajos personalizable
  - Filtro Pasa-Altos personalizable
  - Efecto de Eco (convolución)
- 📊 **Visualizaciones**:
  - Forma de onda
  - Espectrograma (STFT)
  - Espectro de frecuencias (FFT)
- 🎵 **Reproducción** de audio original vs filtrado

## Conceptos de Procesamiento de Señales

### Convolución
La convolución se utiliza para aplicar el efecto de eco. Se convoluciona la señal original con una respuesta al impulso que contiene el impulso directo y ecos atenuados.

### Filtros Butterworth
Se implementan filtros digitales Butterworth de diferentes tipos:
- **Pasa-Bajos**: Permite el paso de frecuencias bajas
- **Pasa-Altos**: Permite el paso de frecuencias altas
- **Pasa-Banda**: Permite el paso de un rango específico de frecuencias

### FFT (Fast Fourier Transform)
Utilizada para convertir la señal del dominio del tiempo al dominio de la frecuencia, permitiendo visualizar el espectro.

### STFT (Short-Time Fourier Transform)
Utilizada para generar el espectrograma, mostrando cómo cambia el contenido espectral a lo largo del tiempo.

## Instalación

### Requisitos previos
- Python 3.8 o superior
- FFmpeg (necesario para yt-dlp)

#### Instalar FFmpeg:

**Windows:**
```bash
# Usando Chocolatey
choco install ffmpeg

# O descarga desde: https://ffmpeg.org/download.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Instalación de dependencias de Python

```bash
# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### 1. Iniciar el servidor

```bash
python main.py
```

O alternativamente:

```bash
uvicorn main:app --reload
```

### 2. Abrir la aplicación

Abre tu navegador y ve a: `http://localhost:8000`

### 3. Usar la aplicación

1. **Cargar Audio**: Pega la URL de un video de YouTube en el campo de texto y haz clic en "Descargar Audio"
2. **Seleccionar Filtro**: Elige uno de los filtros disponibles (graves, medios, agudos, etc.)
3. **Ajustar Parámetros**: Modifica la intensidad del filtro y, si es necesario, la frecuencia de corte
4. **Aplicar Filtro**: Haz clic en "Aplicar Filtro" y espera el procesamiento
5. **Reproducir**: Compara el audio original con el filtrado
6. **Visualizar**: Explora las diferentes visualizaciones (forma de onda, espectrograma, FFT)

## Estructura del Proyecto

```
Proyecto/
│
├── main.py                 # Servidor FastAPI
├── audio_processor.py      # Lógica de procesamiento de audio
├── eco.py                  # Script original de eco
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
│
├── static/                # Archivos web
│   ├── index.html         # Interfaz HTML
│   ├── styles.css         # Estilos
│   └── app.js             # Lógica JavaScript
│
└── temp/                  # Archivos temporales (generado automáticamente)
    ├── downloaded_audio.wav
    ├── filtered_*.wav
    └── *.png              # Visualizaciones
```

## API Endpoints

- `GET /` - Página principal
- `POST /api/download` - Descargar audio de YouTube
- `POST /api/apply_filter` - Aplicar filtro al audio
- `GET /api/visualize/{viz_type}` - Generar visualización
- `GET /api/audio/{filename}` - Servir archivo de audio
- `GET /api/status` - Estado del procesador

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python
- **Procesamiento de Audio**: librosa, scipy, numpy
- **Descarga de YouTube**: yt-dlp
- **Visualización**: matplotlib
- **Frontend**: HTML5, CSS3, JavaScript vanilla

## Deploy Online (Producción)

La aplicación puede ser desplegada en varias plataformas cloud. FFmpeg se instala automáticamente en el servidor.

### Opción 1: Railway (Recomendada)

1. Crea cuenta en https://railway.app
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente `railway.json` y `nixpacks.toml`
4. Deploy automático - FFmpeg se instala automáticamente

### Opción 2: Render

1. Crea cuenta en https://render.com
2. Conecta tu repositorio
3. Render detectará automáticamente `render.yaml`
4. Deploy automático - FFmpeg se instala automáticamente

### Opción 3: Docker (Cualquier plataforma)

```bash
# Construir imagen
docker build -t audio-filter-app .

# Ejecutar contenedor
docker run -p 8000:8000 audio-filter-app
```

### Opción 4: Heroku

```bash
# Agregar buildpack de FFmpeg
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# Deploy
git push heroku main
```

**Nota**: Para desarrollo local, necesitas instalar FFmpeg en tu PC. Para producción, FFmpeg se instala automáticamente en el servidor.

## Notas

- Los archivos de audio descargados se guardan en la carpeta `temp/`
- El audio se procesa en mono a 22050 Hz para mayor eficiencia
- Las visualizaciones se generan dinámicamente al solicitarlas
- La aplicación soporta múltiples formatos de URL de YouTube
- FFmpeg es necesario solo en el servidor, no en el navegador del usuario

## Posibles Mejoras Futuras

- [ ] Separación de fuentes con machine learning (Spleeter, Demucs)
- [ ] Más efectos de audio (reverberación, chorus, compresión)
- [ ] Exportación de audio procesado
- [ ] Historial de filtros aplicados
- [ ] Soporte para archivos de audio locales
- [ ] Ecualizador de múltiples bandas
- [ ] Detección automática de tempo/BPM

## Autor

Proyecto de Procesamiento de Señales - Métodos Numéricos 2

## Licencia

MIT
