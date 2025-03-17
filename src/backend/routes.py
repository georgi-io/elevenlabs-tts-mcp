from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import base64
from pathlib import Path
from .elevenlabs_client import ElevenLabsClient
from .websocket import manager
from fastapi.responses import StreamingResponse

# Change the prefix to match the frontend API calls
router = APIRouter(prefix="/api")
client = ElevenLabsClient()

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "elevenlabs-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Create config directory if it doesn't exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "default_voice_id": "cgSgspJ2msm6clMCkdW9",  # Jessica's voice ID
    "default_model_id": "eleven_flash_v2_5",
    "settings": {
        "auto_play": True,
    },
}


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = None


class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any]


class ConfigRequest(BaseModel):
    default_voice_id: Optional[str] = None
    default_model_id: Optional[str] = None
    settings: Optional[Dict] = None


class Voice(BaseModel):
    voice_id: str
    name: str


class Model(BaseModel):
    model_id: str
    name: str


def load_config() -> Dict[str, Any]:
    """Load configuration from file or return default."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG
    else:
        # Save default config if it doesn't exist
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


@router.get("/voices", response_model=List[Voice])
async def get_voices():
    """Get all available voices."""
    try:
        voices_data = await client.get_voices()
        return [Voice(voice_id=v["voice_id"], name=v["name"]) for v in voices_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")


@router.get("/models", response_model=List[Model])
async def get_models():
    """Get all available models."""
    try:
        models_data = await client.get_models()
        return [Model(model_id=m["model_id"], name=m["name"]) for m in models_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech."""
    try:
        # Load configuration
        config = load_config()

        # Use provided voice_id/model_id or default from config
        voice_id = request.voice_id or config["default_voice_id"]
        model_id = request.model_id or config["default_model_id"]

        # Generate audio using our client
        audio = await client.text_to_speech(text=request.text, voice_id=voice_id, model_id=model_id)

        # Send audio via WebSocket to all connected clients
        encoded_audio = base64.b64encode(audio).decode("utf-8")
        await manager.broadcast_to_clients(
            {
                "type": "audio_data",
                "text": request.text,
                "voice_id": voice_id,
                "data": encoded_audio,
            }
        )

        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert text to speech: {str(e)}")


@router.post("/tts/stream")
async def text_to_speech_stream(request: TTSRequest):
    """Stream text to speech conversion."""
    try:
        # Load configuration
        config = load_config()

        # Use provided voice_id/model_id or default from config
        voice_id = request.voice_id or config["default_voice_id"]
        model_id = request.model_id or config["default_model_id"]

        # Generate audio stream using our client
        audio_stream = client.text_to_speech_stream(
            text=request.text, voice_id=voice_id, model_id=model_id
        )

        # Return audio as streaming response
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Cache-Control": "no-cache",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stream text to speech: {str(e)}")


@router.post("/mcp")
async def handle_mcp_request(request: MCPRequest) -> Dict:
    """Handle MCP requests from the frontend."""
    try:
        if request.command == "speak-text":
            # Send a message to the MCP binary via WebSocket
            await manager.send_to_mcp(
                {
                    "type": "tts_request",
                    "text": request.params.get("text", ""),
                    "voice_id": request.params.get("voice_id"),
                }
            )
            return {"status": "request_sent"}

        elif request.command == "list-voices":
            # Get voices from ElevenLabs API
            voices = await client.get_voices()
            formatted_voices = [
                {"voice_id": voice["voice_id"], "name": voice["name"]} for voice in voices
            ]

            # Send voice list to MCP binary
            await manager.send_to_mcp({"type": "voice_list", "voices": formatted_voices})

            return {"status": "success", "voices": formatted_voices}

        elif request.command == "get-mcp-status":
            # Check if MCP is connected
            return {"status": "success", "mcp_connected": manager.mcp_connection is not None}

        else:
            # Forward other commands to MCP binary
            await manager.send_to_mcp(
                {"type": "command", "command": request.command, "params": request.params}
            )
            return {"status": "command_sent"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config():
    """Get current configuration."""
    try:
        config = load_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


@router.post("/config")
async def update_config(request: ConfigRequest):
    """Update configuration."""
    try:
        current_config = load_config()

        # Update configuration with provided data
        if request.default_voice_id is not None:
            current_config["default_voice_id"] = request.default_voice_id

        if request.default_model_id is not None:
            current_config["default_model_id"] = request.default_model_id

        if request.settings is not None:
            if "auto_play" in request.settings:
                current_config["settings"]["auto_play"] = request.settings["auto_play"]

        # Save updated configuration
        save_config(current_config)

        # Notify MCP about config changes
        await manager.send_to_mcp({"type": "config_update", "config": current_config})

        return current_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.get("/mcp/sse")
async def mcp_sse(request: Request):
    """MCP SSE endpoint for Cursor integration."""
    from .app import mcp_server

    return await mcp_server.run_sse(request)
