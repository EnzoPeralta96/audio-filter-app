import os
import uuid
import time
from pathlib import Path
from typing import Dict, Optional
import threading

class SessionManager:
    """Gestor de sesiones para manejar archivos temporales por usuario"""

    def __init__(self, temp_dir: str = "temp", cleanup_interval: int = 300, max_age: int = 1800):
        """
        Args:
            temp_dir: Directorio temporal
            cleanup_interval: Intervalo de limpieza en segundos (default: 5 minutos)
            max_age: Edad máxima de archivos en segundos (default: 30 minutos)
        """
        self.temp_dir = temp_dir
        self.cleanup_interval = cleanup_interval
        self.max_age = max_age
        self.sessions: Dict[str, float] = {}  # session_id: last_access_time
        self._lock = threading.Lock()

        # Crear directorio temporal
        os.makedirs(temp_dir, exist_ok=True)

        # Iniciar hilo de limpieza
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def create_session(self) -> str:
        """Crear nueva sesión y retornar ID único"""
        session_id = str(uuid.uuid4())
        with self._lock:
            self.sessions[session_id] = time.time()
        return session_id

    def update_session(self, session_id: str):
        """Actualizar timestamp de última actividad de sesión"""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id] = time.time()

    def get_session_path(self, session_id: str, filename: str) -> str:
        """Obtener ruta completa de archivo para una sesión"""
        self.update_session(session_id)
        return os.path.join(self.temp_dir, f"{session_id}_{filename}")

    def session_exists(self, session_id: str) -> bool:
        """Verificar si existe una sesión"""
        with self._lock:
            return session_id in self.sessions

    def cleanup_session(self, session_id: str):
        """Limpiar archivos de una sesión específica"""
        pattern = f"{session_id}_*"
        for filepath in Path(self.temp_dir).glob(pattern):
            try:
                filepath.unlink()
            except Exception:
                pass

        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

    def _cleanup_worker(self):
        """Hilo de limpieza que corre en background"""
        while True:
            time.sleep(self.cleanup_interval)
            self._cleanup_old_files()

    def _cleanup_old_files(self):
        """Limpiar archivos y sesiones antiguas"""
        current_time = time.time()
        expired_sessions = []

        # Identificar sesiones expiradas
        with self._lock:
            for session_id, last_access in self.sessions.items():
                if current_time - last_access > self.max_age:
                    expired_sessions.append(session_id)

        # Limpiar sesiones expiradas
        for session_id in expired_sessions:
            self.cleanup_session(session_id)

        # Limpiar archivos huérfanos (sin sesión)
        try:
            for filepath in Path(self.temp_dir).iterdir():
                if filepath.is_file():
                    # Si el archivo tiene más de max_age, eliminarlo
                    if current_time - filepath.stat().st_mtime > self.max_age:
                        try:
                            filepath.unlink()
                        except Exception:
                            pass
        except Exception:
            pass

# Instancia global
session_manager = SessionManager()