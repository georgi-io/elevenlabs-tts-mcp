from typing import Optional, Dict, List, AsyncGenerator
import httpx
import os
from fastapi import HTTPException
import logging
import elevenlabs
from elevenlabs import stream, generate, voices
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElevenLabsClient:
    def __init__(self, test_mode: bool = False):
        """Initialize the ElevenLabs client.

        Args:
            test_mode: If True, use mock responses for testing
        """
        self.test_mode = test_mode

        if test_mode:
            self.api_key = "test_key"
        else:
            self.api_key = os.getenv("ELEVENLABS_API_KEY")
            if not self.api_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

            # Set the API key for the elevenlabs library as well
            elevenlabs.set_api_key(self.api_key)

        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {"Accept": "application/json", "xi-api-key": self.api_key}

    def _get_mock_audio(self, text: str) -> bytes:
        """Generate mock audio data for testing."""
        return f"Mock audio for: {text}".encode()

    def _get_mock_voices(self) -> List[Dict]:
        """Return mock voices for testing."""
        return [
            {"voice_id": "mock_voice_1", "name": "Mock Voice 1"},
            {"voice_id": "mock_voice_2", "name": "Mock Voice 2"},
        ]

    def _get_mock_models(self) -> List[Dict]:
        """Return mock models for testing."""
        return [
            {"model_id": "mock_model_1", "name": "Mock Model 1"},
            {"model_id": "mock_model_2", "name": "Mock Model 2"},
        ]

    async def text_to_speech(
        self, text: str, voice_id: str, model_id: Optional[str] = None
    ) -> bytes:
        """Convert text to speech."""
        if self.test_mode:
            return self._get_mock_audio(text)

        try:
            # Use the elevenlabs library directly for better compatibility
            audio = generate(text=text, voice=voice_id, model=model_id or "eleven_monolingual_v1")
            return audio
        except Exception as e:
            logger.error(f"Text-to-speech conversion failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Text-to-speech conversion failed: {str(e)}",
            )

    async def get_voices(self) -> List[Dict]:
        """Fetch available voices."""
        if self.test_mode:
            return self._get_mock_voices()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/voices", headers=self.headers)
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    logger.error(f"Failed to fetch voices: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch voices from ElevenLabs API: {error_detail}",
                    )
                data = response.json()
                return data["voices"]
            except httpx.RequestError as e:
                logger.error(f"Connection error when fetching voices: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def get_models(self) -> List[Dict]:
        """Fetch available models."""
        if self.test_mode:
            return self._get_mock_models()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/models", headers=self.headers)
                if response.status_code != 200:
                    error_detail = response.json() if response.content else "No error details"
                    logger.error(f"Failed to fetch models: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch models from ElevenLabs API: {error_detail}",
                    )
                data = response.json()
                models = []
                for model in data:
                    models.append(
                        {"model_id": model.get("model_id", ""), "name": model.get("name", "")}
                    )
                return models
            except httpx.RequestError as e:
                logger.error(f"Connection error when fetching models: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to connect to ElevenLabs API: {str(e)}"
                )

    async def text_to_speech_stream(
        self, text: str, voice_id: str, model_id: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream text to speech conversion."""
        if self.test_mode:
            # In test mode, yield mock audio in chunks
            mock_audio = self._get_mock_audio(text)
            chunk_size = 1024
            for i in range(0, len(mock_audio), chunk_size):
                yield mock_audio[i : i + chunk_size]
                await asyncio.sleep(0.1)  # Simulate streaming delay
            return

        # Use the elevenlabs library for streaming in production
        if not self.api_key:
            raise ValueError("API key is required for streaming")

        elevenlabs.set_api_key(self.api_key)
        try:
            audio_stream = stream(
                text=text,
                voice=voice_id,
                model=model_id or "eleven_monolingual_v1",
                stream=True,
                latency=3,
            )

            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    yield chunk
                    await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error during text-to-speech streaming: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to stream text to speech: {str(e)}"
            )

    def generate_speech(self, text: str, voice_id: str = None) -> bytes:
        """Generate speech from text using ElevenLabs API."""
        return generate(text=text, voice=voice_id)

    def list_voices(self):
        """List available voices from ElevenLabs API."""
        return voices()
