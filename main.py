from fastapi import FastAPI, HTTPException, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
from audio_processor import AudioProcessor
from session_manager import session_manager

app = FastAPI(title="Audio Filter App")

# Crear directorios necesarios
os.makedirs("temp", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Instancia del procesador de audio
processor = AudioProcessor()


class YouTubeRequest(BaseModel):
    url: str
    session_id: Optional[str] = None


class FilterRequest(BaseModel):
    filter_type: str  # "low_pass", "high_pass", "band_pass", "echo"
    cutoff_freq: float = 1000.0  # Frecuencia de corte en Hz
    intensity: float = 1.0  # Intensidad del filtro (0.0 - 1.0)
    session_id: Optional[str] = None


@app.get("/")
async def read_root():
    """Servir la página principal"""
    return FileResponse("static/index.html")


@app.post("/api/create_session")
async def create_session():
    """Crear nueva sesión para el usuario"""
    session_id = session_manager.create_session()
    return JSONResponse({
        "success": True,
        "session_id": session_id
    })


@app.post("/api/download")
async def download_youtube(request: YouTubeRequest):
    """Descargar audio de YouTube"""
    try:
        # Si no hay session_id, crear uno nuevo
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session()

        # Verificar que la sesión existe
        if not session_manager.session_exists(session_id):
            session_id = session_manager.create_session()

        filepath = processor.download_from_youtube(request.url, session_id)

        return JSONResponse({
            "success": True,
            "message": "Audio descargado exitosamente",
            "filename": os.path.basename(filepath),
            "session_id": session_id
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/apply_filter")
async def apply_filter(request: FilterRequest):
    """Aplicar filtro al audio cargado"""
    try:
        session_id = request.session_id
        if not session_id or not session_manager.session_exists(session_id):
            raise HTTPException(status_code=400, detail="Sesión inválida o expirada")

        output_path = processor.apply_filter(
            session_id=session_id,
            filter_type=request.filter_type,
            cutoff_freq=request.cutoff_freq,
            intensity=request.intensity
        )

        return JSONResponse({
            "success": True,
            "message": f"Filtro {request.filter_type} aplicado",
            "filename": os.path.basename(output_path)
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/visualize/{viz_type}")
async def visualize(viz_type: str, session_id: Optional[str] = None):
    """Generar visualización del audio"""
    try:
        if not session_id or not session_manager.session_exists(session_id):
            raise HTTPException(status_code=400, detail="Sesión inválida o expirada")

        image_path = processor.generate_visualization(session_id, viz_type)
        return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """Servir archivo de audio"""
    filepath = os.path.join("temp", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(filepath, media_type="audio/wav")


@app.get("/api/status")
async def get_status(session_id: Optional[str] = None):
    """Obtener estado actual del procesador"""
    if not session_id or not session_manager.session_exists(session_id):
        return JSONResponse({
            "has_audio": False,
            "session_valid": False
        })

    info = processor.get_audio_info(session_id)

    return JSONResponse({
        "has_audio": info is not None,
        "session_valid": True,
        "sample_rate": info["sample_rate"] if info else None,
        "duration": info["duration"] if info else None
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
