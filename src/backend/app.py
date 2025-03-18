from fastapi import FastAPI
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
from fastapi import Request

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


# Neue Route für /sse, die direkt zum MCP-Server auf Port 9022 weiterleitet
@app.get("/sse")
async def redirect_to_mcp_sse():
    """Redirect to MCP SSE endpoint."""
    logger.info(f"Redirecting to MCP server at port {MCP_PORT}")
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url=f"http://localhost:{MCP_PORT}/sse")


# Health-Check Route direkt auf Root-Pfad für AWS Health-Checks
@app.get("/health")
async def root_health_check():
    """Health check endpoint für AWS Health-Checks."""
    return {
        "status": "healthy",
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config),
        "mcp_enabled": True,
        "path": "health",
        "base_path": BASE_PATH,
    }


@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """Log all incoming requests for debugging."""
    path = request.url.path
    logger.info(
        f"DEBUG: Incoming request to path: {path}, method: {request.method}, client: {request.client}"
    )

    if path.endswith("/sse"):
        logger.info(f"DEBUG: SSE request detected - BASE_PATH={BASE_PATH}, path={path}")
        # Teste, ob der MCP-Server auf dem erwarteten Port lauscht
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(("localhost", MCP_PORT))
            logger.info(f"DEBUG: MCP server is reachable on port {MCP_PORT}")
            s.close()
        except Exception as e:
            logger.error(f"DEBUG: MCP server is NOT reachable on port {MCP_PORT}: {e}")

        # Versuche zu prüfen, ob MCP_PORT an eine bestimmte Netzwerkschnittstelle gebunden ist
        try:
            import psutil

            for conn in psutil.net_connections():
                if conn.laddr.port == MCP_PORT:
                    logger.info(f"DEBUG: Process using port {MCP_PORT}: {conn}")
        except Exception as e:
            logger.error(f"DEBUG: Could not check processes using port {MCP_PORT}: {e}")

    response = await call_next(request)
    logger.info(f"DEBUG: Response for {path}: {response.status_code}")
    return response
