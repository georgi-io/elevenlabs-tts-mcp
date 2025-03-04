"""
MCP Tools for ElevenLabs TTS

This module defines the MCP tools that will be exposed to Cursor.
"""

import logging
import base64
from typing import Dict, Any
from .elevenlabs_client import ElevenLabsClient
from mcp.server.fastmcp import FastMCP
from .websocket import manager
from .routes import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ElevenLabs client
client = None  # We'll initialize this when registering tools


def register_mcp_tools(mcp_server: FastMCP, test_mode: bool = False) -> None:
    """Register MCP tools with the server."""
    global client
    client = ElevenLabsClient(test_mode=test_mode)

    @mcp_server.tool("speak_text")
    async def speak_text(text: str) -> Dict[str, Any]:
        """Convert text to speech using ElevenLabs.

        Args:
            text: The text to convert to speech

        Returns:
            A dictionary with the result of the operation
        """
        try:
            # Load current configuration
            config = load_config()
            voice_id = config["default_voice_id"]
            model_id = config["default_model_id"]

            logger.info(
                f"Converting text to speech with voice ID: {voice_id} and model ID: {model_id}"
            )

            # Generate audio using our client instance
            audio = await client.text_to_speech(text, voice_id, model_id)

            # Encode audio data as base64
            encoded_audio = base64.b64encode(audio).decode("utf-8")

            # Send to all connected clients via WebSocket
            await manager.broadcast_to_clients(
                {
                    "type": "audio_data",
                    "text": text,
                    "voice_id": voice_id,
                    "data": encoded_audio,
                }
            )

            return {
                "success": True,
                "message": "Text converted to speech and sent to clients",
                "streaming": False,
            }
        except Exception as e:
            logger.error(f"Error in speak_text: {e}")
            return {"success": False, "error": str(e)}
