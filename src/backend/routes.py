from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .elevenlabs_client import ElevenLabsClient
from .websocket import manager

# Change the prefix to match the frontend API calls
router = APIRouter(prefix="/api")
client = ElevenLabsClient()

class TTSRequest(BaseModel):
    text: str
    voice_id: str
    model_id: Optional[str] = "eleven_monolingual_v1"

class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any]

@router.get("/voices")
async def get_voices() -> List[Dict]:
    """Get all available voices."""
    try:
        voices = await client.get_voices()
        # Format the response to match the frontend expectations
        return [{"voice_id": voice["voice_id"], "name": voice["name"]} for voice in voices]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/models")
async def get_models() -> List[Dict]:
    """Get all available models."""
    return await client.get_models()

@router.post("/tts")
async def text_to_speech(request: TTSRequest) -> Response:
    """Convert text to speech."""
    try:
        audio_content = await client.text_to_speech(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id
        )
        return Response(
            content=audio_content,
            media_type="audio/mpeg"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/mcp")
async def handle_mcp_request(request: MCPRequest) -> Dict:
    """Handle MCP requests from the frontend."""
    try:
        if request.command == "speak-text":
            # Send a message to the MCP binary via WebSocket
            await manager.send_to_mcp({
                "type": "tts_request",
                "text": request.params.get("text", ""),
                "voice_id": request.params.get("voice_id")
            })
            return {"status": "request_sent"}
        
        elif request.command == "list-voices":
            # Get voices from ElevenLabs API
            voices = await client.get_voices()
            formatted_voices = [{"voice_id": voice["voice_id"], "name": voice["name"]} for voice in voices]
            
            # Send voice list to MCP binary
            await manager.send_to_mcp({
                "type": "voice_list",
                "voices": formatted_voices
            })
            
            return {"status": "success", "voices": formatted_voices}
        
        elif request.command == "get-mcp-status":
            # Check if MCP is connected
            return {
                "status": "success", 
                "mcp_connected": manager.mcp_connection is not None
            }
        
        else:
            # Forward other commands to MCP binary
            await manager.send_to_mcp({
                "type": "command",
                "command": request.command,
                "params": request.params
            })
            return {"status": "command_sent"}
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 