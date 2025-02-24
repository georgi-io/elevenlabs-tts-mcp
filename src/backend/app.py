from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yaml
import os
from dotenv import load_dotenv
from pathlib import Path
from .routes import router
from .websocket import websocket_endpoint
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response
from starlette.routing import Mount
from starlette.applications import Starlette

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

# Add WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)

# Create static directory if it doesn't exist
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Create assets directory if it doesn't exist
assets_dir = static_dir / "assets"
assets_dir.mkdir(exist_ok=True)

# Mount static files only if the directory exists
app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Initialize MCP server
mcp_server = FastMCP("ElevenLabs TTS")
from .mcp_tools import register_mcp_tools
register_mcp_tools(mcp_server)

# Add MCP SSE endpoint
@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    """MCP SSE endpoint for Cursor integration."""
    return await mcp_server.run_sse_async(request)

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
        "config_loaded": bool(config),
        "mcp_enabled": True
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