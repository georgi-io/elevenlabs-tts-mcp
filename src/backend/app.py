from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yaml
import os
import threading
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from .routes import router
from .websocket import websocket_endpoint
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response
import logging
from .mcp_tools import register_mcp_tools

# Load environment variables
load_dotenv()

# Get port configurations from environment variables
PORT = int(os.getenv("PORT", 9020))
WS_PORT = int(os.getenv("WS_PORT", 9021))
MCP_PORT = int(os.getenv("MCP_PORT", 9022))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Log the static directory path for debugging
logger.info(f"Static directory path: {static_dir.absolute()}")

# List files in the static directory
if static_dir.exists():
    logger.info(f"Files in static directory: {[f.name for f in static_dir.iterdir()]}")
else:
    logger.warning(f"Static directory does not exist: {static_dir.absolute()}")

# Create assets directory if it doesn't exist
assets_dir = static_dir / "assets"
assets_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
# Mount the entire static directory to serve all static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize MCP server
mcp_server = FastMCP("ElevenLabs TTS")
# Configure MCP server to use the port from environment variables
mcp_server.settings.port = MCP_PORT
register_mcp_tools(mcp_server)

# Start MCP server in a separate thread
def start_mcp_server():
    mcp_server.run(transport='sse')

# Start the MCP server in a background thread when the app starts
@app.on_event("startup")
async def startup_event():
    # Start MCP server in a separate thread
    threading.Thread(target=start_mcp_server, daemon=True).start()
    # Log the server URLs
    logger.info(f"Backend server running at http://localhost:{PORT}")
    logger.info(f"WebSocket server running at ws://localhost:{WS_PORT}")
    logger.info(f"MCP server running at http://localhost:{MCP_PORT}/sse")

@app.get("/")
async def root():
    # Check if index.html exists in static directory
    index_path = static_dir / "index.html"
    logger.info(f"Checking for index.html at: {index_path.absolute()}")
    if index_path.exists():
        logger.info(f"Serving index.html from {index_path}")
        return FileResponse(str(index_path))
    logger.warning("index.html not found in static directory")
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
        logger.info(f"Serving index.html for path: {full_path}")
        return FileResponse(str(index_path))
    
    # If frontend is not built yet
    logger.warning(f"Frontend not built yet, requested path: {full_path}")
    return {"status": "frontend_not_built", "message": "Frontend has not been built yet"} 