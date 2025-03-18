from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
import threading
from dotenv import load_dotenv
from pathlib import Path
from .routes import router
from .websocket import websocket_endpoint
from mcp.server.fastmcp import FastMCP
import logging
from .mcp_tools import register_mcp_tools

# Load environment variables
load_dotenv()

# Get port configurations from environment variables
PORT = int(os.getenv("PORT", 9020))
MCP_PORT = int(os.getenv("MCP_PORT", 9022))
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
# Configure MCP server to use the port from environment variables
mcp_server.settings.port = MCP_PORT
register_mcp_tools(mcp_server)


# Start MCP server in a separate thread
def start_mcp_server():
    mcp_server.run(transport="sse")


# Start the MCP server in a background thread when the app starts
@app.on_event("startup")
async def startup_event():
    # Start MCP server in a separate thread
    threading.Thread(target=start_mcp_server, daemon=True).start()
    # Log the server URLs
    logger.info(f"Backend server running at http://localhost:{PORT}")
    logger.info(f"MCP server running at http://localhost:{MCP_PORT}/sse")


# Neue Route für /jessica-service/health
@app.get("/jessica-service/health")
async def jessica_service_health_check():
    return {
        "status": "healthy",
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config),
        "mcp_enabled": True,
        "path": "jessica-service/health",
        "base_path": BASE_PATH,
    }


# Direkte Route für MCP/SSE auf dem Hauptanwendungspfad
@app.get("/mcp/sse")
async def direct_mcp_sse(request: Request):
    """MCP SSE endpoint für Cursor integration direkt auf der Hauptanwendung."""
    return await mcp_server.run_sse(request)
