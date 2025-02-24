from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yaml
import os
from dotenv import load_dotenv
from pathlib import Path
from .routes import router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="ElevenLabs TTS MCP",
    description="Text-to-Speech service using ElevenLabs API",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
def load_config():
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {"voices": {}, "settings": {}}

config = load_config()

# Include our API routes
app.include_router(router)

# Create static directory if it doesn't exist
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

@app.get("/")
async def root():
    # Check if index.html exists in static directory
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"status": "ok", "service": "elevenlabs-tts-mcp"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config)
    }

# Catch-all route to serve the frontend for any non-API routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Skip API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other routes (SPA support)
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # If frontend is not built yet
    return {"status": "frontend_not_built", "message": "Frontend has not been built yet"} 