from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List, Dict
from .elevenlabs_client import ElevenLabsClient

router = APIRouter(prefix="/api/v1")
client = ElevenLabsClient()

class TTSRequest(BaseModel):
    text: str
    voice_id: str
    model_id: Optional[str] = "eleven_monolingual_v1"

@router.get("/voices")
async def get_voices() -> List[Dict]:
    """Get all available voices."""
    return await client.get_voices()

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