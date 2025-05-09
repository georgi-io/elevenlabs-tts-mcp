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
ROOT_PATH = os.getenv("ROOT_PATH", "")
MCP_PORT = int(os.getenv("MCP_PORT", 9022))

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Normalisiere ROOT_PATH
if ROOT_PATH:
    # Mit / beginnen
    if not ROOT_PATH.startswith("/"):
        ROOT_PATH = f"/{ROOT_PATH}"

    # Nicht mit / enden
    if ROOT_PATH.endswith("/"):
        ROOT_PATH = ROOT_PATH[:-1]

    logger.info(f"Using ROOT_PATH: {ROOT_PATH}")

app = FastAPI(
    title="Jessica TTS MCP",
    description="Text-to-Speech service using ElevenLabs API",
    version="0.1.0",
    root_path=ROOT_PATH,
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)

"""
Path Rewriting Concept

This service uses a path-rewriting middleware to handle both direct ALB access 
and API Gateway access with a ROOT_PATH prefix.

The middleware strips the ROOT_PATH prefix from incoming requests before they're processed,
allowing FastAPI to use its built-in root_path parameter correctly and eliminating the need
for duplicate routes.

For example:
- External request to /jessica-service/api/v1/tts
- Middleware rewrites to /api/v1/tts
- FastAPI processes the request using its normal routing
- FastAPI adds ROOT_PATH in generated URLs (docs, redirects, etc.)

This approach simplifies the codebase and ensures consistency between local development
and production environments.
"""


# Path rewriting middleware - MUST be first in the middleware chain
@app.middleware("http")
async def rewrite_path_middleware(request: Request, call_next):
    """
    Middleware that rewrites incoming request paths by removing the ROOT_PATH prefix.

    This allows FastAPI to handle both direct requests and requests coming through
    API Gateway or ALB with a path prefix.
    """
    original_path = request.url.path

    # Debug output of original path
    logger.debug(f"Original path: {original_path}")

    # Check for double service paths (e.g. /jessica-service/jessica-service/)
    double_prefix = False
    if ROOT_PATH and original_path.startswith(ROOT_PATH):
        remaining_path = original_path[len(ROOT_PATH) :]
        if remaining_path.startswith(ROOT_PATH):
            # We found a double prefix
            double_prefix = True
            logger.debug(f"Detected double prefix: {original_path}")
            # Remove both instances of the prefix
            new_path = remaining_path[len(ROOT_PATH) :]
            # Ensure the path starts with /
            if not new_path.startswith("/"):
                new_path = "/" + new_path

            # Update the request scope
            request.scope["path"] = new_path
            request.scope["root_path"] = ROOT_PATH

            logger.debug(
                f"Path rewritten (double prefix): {original_path} -> {new_path} (root_path={ROOT_PATH})"
            )
            return await call_next(request)

    # Only rewrite if ROOT_PATH is set and path starts with it
    if ROOT_PATH and original_path.startswith(ROOT_PATH) and not double_prefix:
        # Remove the ROOT_PATH prefix from the path
        new_path = original_path[len(ROOT_PATH) :]
        # Ensure the path starts with a slash
        if not new_path.startswith("/"):
            new_path = "/" + new_path

        # Create modified request scope with new path
        request.scope["path"] = new_path

        # Update the root_path in the scope
        request.scope["root_path"] = ROOT_PATH

        logger.debug(f"Path rewritten: {original_path} -> {new_path} (root_path={ROOT_PATH})")

    # Process the request with the rewritten path
    return await call_next(request)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging middleware (after path rewriting)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log information about all incoming requests."""
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"ROOT_PATH: {ROOT_PATH}")

    response = await call_next(request)

    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


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
    logger.info(f"Backend server listening on {HOST}:{PORT}{ROOT_PATH}")
    logger.info(f"MCP server integrated on {ROOT_PATH}/sse")


@app.get("/health")
async def jessica_service_health_check():
    return {
        "status": "ok",
        "service": "jessica-service",
        "root_path": ROOT_PATH,
        "elevenlabs_api_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "config_loaded": bool(config),
        "mcp_enabled": True,
    }


# Catch-all Route erst danach definieren
@app.get("/{path:path}")
async def catch_all(path: str, request: Request):
    """
    Catch-all route for debugging and redirecting misrouted requests.

    This route helps with debugging path issues that might occur with various
    proxy configurations and ROOT_PATH settings.
    """
    logger.error(f"DEBUG-CATCHALL: Received request for path: /{path}, full URL: {request.url}")
    logger.error(f"DEBUG-CATCHALL: Headers: {request.headers}")

    # API documentation should be available at /docs when ROOT_PATH is handled correctly
    if path == "docs" or path == "redoc" or path == "openapi.json":
        logger.error(
            f"Documentation URL accessed incorrectly as /{path} - should be at {ROOT_PATH}/docs"
        )

    return {"message": f"Received request for /{path}"}
