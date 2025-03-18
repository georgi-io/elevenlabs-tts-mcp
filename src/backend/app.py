from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
from dotenv import load_dotenv
from pathlib import Path
from .routes import router
from .websocket import websocket_endpoint
from mcp.server.fastmcp import FastMCP
import mcp.server.sse
import logging
from .mcp_tools import register_mcp_tools
from fastapi import Request

# Load environment variables
load_dotenv()

# Get port configurations from environment variables
PORT = int(os.getenv("PORT", 9020))
HOST = os.getenv("HOST", "localhost")
BASE_PATH = os.getenv("BASE_PATH", "")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ElevenLabs TTS MCP",
    description="Text-to-Speech service using ElevenLabs API",
    version="0.1.0",
    root_path=BASE_PATH,
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

# Initialize MCP server
mcp_server = FastMCP("Jessica MCP Service")
register_mcp_tools(mcp_server)

# Wir starten keinen eigenen FastMCP-Server mehr in einem eigenen Thread,
# sondern integrieren die SSE-Endpunkte direkt in unsere FastAPI-App

# Erstelle die SSE-Transportschicht
sse_transport = mcp.server.sse.SseServerTransport("/messages/")


@app.get("/sse")
async def handle_sse(request: Request):
    """Der SSE-Endpunkt für MCP-Kommunikation"""
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server._mcp_server.run(
            streams[0],
            streams[1],
            mcp_server._mcp_server.create_initialization_options(),
        )


@app.post("/messages/{path:path}")
async def handle_messages(request: Request, path: str):
    """Weiterleitung der Messages an den SSE-Transport"""
    return await sse_transport.handle_post_message(request.scope, request.receive, request._send)


# Start the FastAPI server in a background thread when the app starts
@app.on_event("startup")
async def startup_event():
    # Log the server URLs
    logger.info(f"Backend server listening on {HOST}:{PORT}{BASE_PATH}")
    logger.info(f"MCP server integrated on {BASE_PATH}/sse")


@app.get("/health")
async def jessica_service_health_check():
    return {
        "status": "healthy",
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config),
        "mcp_enabled": True,
        "path": f"{BASE_PATH}/health",
        "base_path": BASE_PATH,
    }


# Catch-all Route erst danach definieren
@app.get("/{path:path}")
async def catch_all(path: str, request: Request):
    """Catch-all route for debugging."""
    logger.error(f"DEBUG-CATCHALL: Received request for path: /{path}, full URL: {request.url}")
    logger.error(f"DEBUG-CATCHALL: Headers: {request.headers}")
    return {"message": f"Received request for /{path}"}
