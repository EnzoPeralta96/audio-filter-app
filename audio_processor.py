import numpy as np
import librosa
import soundfile as sf
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
from scipy import signal
import os
import yt_dlp
from session_manager import session_manager

class AudioProcessor:
    """Procesador de audio sin estado - usa sesiones para manejar múltiples usuarios"""

    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_from_youtube(self, url: str, session_id: str):
        """Descargar audio de YouTube usando yt-dlp"""
        output_base = session_manager.get_session_path(session_id, "downloaded_audio")
        output_path = output_base + ".wav"

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': output_base,
            'quiet': True,
            'no_warnings': True,
            # Opciones para evitar bloqueo 403
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return output_path
        except Exception as e:
            raise Exception(f"Error descargando de YouTube: {str(e)}")

    def _load_audio(self, session_id: str):
        """Cargar audio de sesión"""
        audio_path = session_manager.get_session_path(session_id, "downloaded_audio.wav")
        if not os.path.exists(audio_path):
            raise Exception("No hay audio cargado para esta sesión")

        audio, sr = librosa.load(audio_path, sr=22050, mono=True)
        return audio, sr

    def design_lowpass_filter(self, sr, cutoff_freq, order=5):
        """Diseñar filtro pasa-bajos usando Butterworth"""
        nyquist = 0.5 * sr
        normal_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def design_highpass_filter(self, sr, cutoff_freq, order=5):
        """Diseñar filtro pasa-altos usando Butterworth"""
        nyquist = 0.5 * sr
        normal_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def design_bandpass_filter(self, sr, low_freq, high_freq, order=5):
        """Diseñar filtro pasa-banda usando Butterworth"""
        nyquist = 0.5 * sr
        low = low_freq / nyquist
        high = high_freq / nyquist
        b, a = signal.butter(order, [low, high], btype='band', analog=False)
        return b, a

    def apply_echo_effect(self, audio, sr, delay_seconds=0.3, decay=0.5):
        """Aplicar efecto de eco usando convolución"""
        delay_samples = int(delay_seconds * sr)

        # Crear respuesta al impulso
        h = np.zeros(delay_samples * 2)
        h[0] = 1.0  # Impulso directo
        h[delay_samples] = decay  # Eco atenuado

        # Convolución
        audio_with_echo = np.convolve(audio, h, mode='same')

        # Normalizar
        audio_with_echo = audio_with_echo / (np.max(np.abs(audio_with_echo)) + 1e-12)

        return audio_with_echo

    def apply_filter(self, session_id: str, filter_type: str, cutoff_freq: float = 1000.0, intensity: float = 1.0):
        """
        Aplicar filtro al audio

        filter_type: "low_pass", "high_pass", "band_pass_bass", "band_pass_mids", "band_pass_treble", "echo"
        cutoff_freq: Frecuencia de corte en Hz
        intensity: Intensidad del filtro (0.0 = original, 1.0 = filtro completo)
        """
        # Cargar audio original
        audio, sr = self._load_audio(session_id)

        # Aplicar el filtro correspondiente
        if filter_type == "low_pass":
            # Filtro pasa-bajos (graves: bajo, bombo)
            b, a = self.design_lowpass_filter(sr, cutoff_freq)
            filtered_audio = signal.filtfilt(b, a, audio)

        elif filter_type == "high_pass":
            # Filtro pasa-altos (agudos: platillos, hi-hat)
            b, a = self.design_highpass_filter(sr, cutoff_freq)
            filtered_audio = signal.filtfilt(b, a, audio)

        elif filter_type == "band_pass_bass":
            # Rango de graves (20-250 Hz) - bajo y bombo
            b, a = self.design_bandpass_filter(sr, 20, 250)
            filtered_audio = signal.filtfilt(b, a, audio)

        elif filter_type == "band_pass_mids":
            # Rango de medios (250-5000 Hz) - guitarra, voz
            b, a = self.design_bandpass_filter(sr, 250, 5000)
            filtered_audio = signal.filtfilt(b, a, audio)

        elif filter_type == "band_pass_treble":
            # Rango de agudos (5000-20000 Hz) - platillos
            b, a = self.design_bandpass_filter(sr, 5000, 20000)
            filtered_audio = signal.filtfilt(b, a, audio)

        elif filter_type == "echo":
            # Efecto de eco
            filtered_audio = self.apply_echo_effect(audio, sr, delay_seconds=0.3, decay=intensity * 0.6)

        else:
            raise Exception(f"Tipo de filtro no soportado: {filter_type}")

        # Mezclar con audio original según intensidad
        if filter_type != "echo":  # El eco ya se mezcla internamente
            final_audio = (1 - intensity) * audio + intensity * filtered_audio
        else:
            final_audio = filtered_audio

        # Normalizar para evitar clipping
        final_audio = final_audio / (np.max(np.abs(final_audio)) + 1e-12)

        # Guardar resultado
        output_path = session_manager.get_session_path(session_id, f"filtered_{filter_type}.wav")
        sf.write(output_path, final_audio, sr)

        return output_path

    def generate_visualization(self, session_id: str, viz_type: str):
        """
        Generar visualización del audio

        viz_type: "waveform", "spectrogram", "spectrum"
        """
        # Cargar audio
        audio, sr = self._load_audio(session_id)

        output_path = session_manager.get_session_path(session_id, f"{viz_type}.png")

        plt.figure(figsize=(12, 6))

        if viz_type == "waveform":
            # Forma de onda
            time = np.linspace(0, len(audio) / sr, len(audio))
            plt.plot(time, audio, linewidth=0.5)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')
            plt.title('Forma de Onda')
            plt.grid(True, alpha=0.3)

        elif viz_type == "spectrogram":
            # Espectrograma
            D = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
            librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Espectrograma')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Frecuencia (Hz)')

        elif viz_type == "spectrum":
            # Espectro de frecuencias (FFT)
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            magnitude = np.abs(fft)

            # Solo frecuencias positivas
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]

            plt.plot(positive_freqs, positive_magnitude)
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Magnitud')
            plt.title('Espectro de Frecuencias (FFT)')
            plt.xlim(0, 10000)  # Mostrar solo hasta 10 kHz
            plt.grid(True, alpha=0.3)

        else:
            raise Exception(f"Tipo de visualización no soportado: {viz_type}")

        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()

        return output_path

    def get_audio_info(self, session_id: str):
        """Obtener información del audio"""
        try:
            audio, sr = self._load_audio(session_id)
            return {
                "sample_rate": sr,
                "duration": len(audio) / sr,
                "samples": len(audio),
                "channels": 1  # Siempre mono
            }
        except:
            return None
