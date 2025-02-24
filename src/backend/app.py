from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
async def root():
    return {"status": "ok", "service": "elevenlabs-tts-mcp"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config)
    } 