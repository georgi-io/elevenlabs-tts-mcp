from typing import Optional, Dict, List, Any, AsyncGenerator
import httpx
import os
from fastapi import HTTPException
import logging
from dotenv import load_dotenv
import elevenlabs
from elevenlabs import generate, stream, Voice, VoiceSettings
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }

    async def get_voices(self) -> List[Dict]:
        """Fetch available voices from ElevenLabs API."""
        async with httpx.AsyncClient() as client:
            try:
                logger.info("Fetching voices from ElevenLabs API")
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    logger.error(f"Failed to fetch voices: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch voices from ElevenLabs API: {error_detail}"
                    )
                
                data = response.json()
                logger.info(f"Successfully fetched {len(data['voices'])} voices")
                return data["voices"]
            except httpx.RequestError as e:
                logger.error(f"Connection error when fetching voices: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def text_to_speech(
        self,
        text: str,
        voice_id: str,
        model_id: Optional[str] = "eleven_monolingual_v1"
    ) -> bytes:
        """Convert text to speech using ElevenLabs API."""
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        logger.info(f"Converting text to speech with voice_id={voice_id}, model_id={model_id}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    logger.error(f"Text-to-speech conversion failed: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Text-to-speech conversion failed: {error_detail}"
                    )

                logger.info("Successfully converted text to speech")
                return response.content
            except httpx.RequestError as e:
                logger.error(f"Connection error during text-to-speech: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def get_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from ElevenLabs API."""
        async with httpx.AsyncClient() as client:
            try:
                logger.info("Fetching models from ElevenLabs API")
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    logger.error(f"Failed to fetch models: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch models from ElevenLabs API: {error_detail}"
                    )
                
                data = response.json()
                # Transform the response to match our expected format
                models = []
                for model in data:
                    models.append({
                        "model_id": model.get("model_id", ""),
                        "name": model.get("name", "")
                    })
                
                logger.info(f"Successfully fetched {len(models)} models")
                return models
            except httpx.RequestError as e:
                logger.error(f"Connection error when fetching models: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def text_to_speech_stream(
        self,
        text: str,
        voice_id: str,
        model_id: Optional[str] = "eleven_monolingual_v1"
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to speech using ElevenLabs API with streaming support."""
        logger.info(f"Converting text to speech with streaming: voice_id={voice_id}, model_id={model_id}")
        
        # Setze den API-Key
        elevenlabs.set_api_key(self.api_key)
        
        try:
            # Verwende die stream-Funktion für Streaming
            audio_stream = stream(
                text=text,
                voice=voice_id,
                model=model_id,
                stream=True,
                latency=3  # Optimiere für niedrige Latenz
            )
            
            # Stream audio chunks zurück
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    yield chunk
                    # Small delay to avoid overwhelming the client
                    await asyncio.sleep(0.01)
                    
            logger.info("Successfully streamed text to speech")
        except Exception as e:
            logger.error(f"Error during text-to-speech streaming: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stream text to speech: {str(e)}"
            ) 