from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
from audio_processor import AudioProcessor

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


class FilterRequest(BaseModel):
    filter_type: str  # "low_pass", "high_pass", "band_pass", "echo"
    cutoff_freq: float = 1000.0  # Frecuencia de corte en Hz
    intensity: float = 1.0  # Intensidad del filtro (0.0 - 1.0)


@app.get("/")
async def read_root():
    """Servir la página principal"""
    return FileResponse("static/index.html")


@app.post("/api/download")
async def download_youtube(request: YouTubeRequest):
    """Descargar audio de YouTube"""
    try:
        filepath = processor.download_from_youtube(request.url)
        return JSONResponse({
            "success": True,
            "message": "Audio descargado exitosamente",
            "filename": os.path.basename(filepath)
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/apply_filter")
async def apply_filter(request: FilterRequest):
    """Aplicar filtro al audio cargado"""
    try:
        if not processor.has_audio():
            raise HTTPException(status_code=400, detail="No hay audio cargado")

        output_path = processor.apply_filter(
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
async def visualize(viz_type: str):
    """Generar visualización del audio"""
    try:
        if not processor.has_audio():
            raise HTTPException(status_code=400, detail="No hay audio cargado")

        image_path = processor.generate_visualization(viz_type)
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
async def get_status():
    """Obtener estado actual del procesador"""
    return JSONResponse({
        "has_audio": processor.has_audio(),
        "sample_rate": processor.sr if processor.has_audio() else None,
        "duration": len(processor.audio) / processor.sr if processor.has_audio() else None
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)