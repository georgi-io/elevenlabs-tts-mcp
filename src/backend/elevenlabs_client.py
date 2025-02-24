from typing import Optional, Dict, List
import httpx
import os
from fastapi import HTTPException
import logging
from dotenv import load_dotenv

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
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch voices from ElevenLabs API: {error_detail}"
                    )
                
                return response.json()["voices"]
            except httpx.RequestError as e:
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

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Text-to-speech conversion failed: {error_detail}"
                    )

                return response.content
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def get_models(self) -> List[Dict]:
        """Fetch available models from ElevenLabs API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch models from ElevenLabs API: {error_detail}"
                    )
                
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                ) 