"""
MCP Tools for ElevenLabs TTS

This module defines the MCP tools that will be exposed to Cursor.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from .elevenlabs_client import ElevenLabsClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Default voice ID
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "elevenlabs-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Create config directory if it doesn't exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Initialize ElevenLabs client
client = ElevenLabsClient()

def register_mcp_tools(mcp_server):
    """Register MCP tools with the server."""
    
    @mcp_server.tool()
    async def speak_text(text: str, voice_id: str = None) -> Dict:
        """Convert text to speech using ElevenLabs.
        
        Args:
            text: The text to convert to speech
            voice_id: Optional voice ID to use (defaults to configured voice)
        
        Returns:
            A dictionary with the result of the operation
        """
        try:
            if not voice_id:
                voice_id = DEFAULT_VOICE_ID
                
            # Convert text to speech
            audio_content = await client.text_to_speech(
                text=text,
                voice_id=voice_id
            )
            
            # Save audio to temporary file
            temp_dir = Path.home() / ".cache" / "elevenlabs-mcp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            audio_file = temp_dir / "last_tts.mp3"
            with open(audio_file, "wb") as f:
                f.write(audio_content)
                
            logger.info(f"Saved audio to {audio_file}")
            
            # Play audio if on macOS
            if os.name == "posix" and os.uname().sysname == "Darwin":
                os.system(f"afplay {audio_file}")
            
            return {
                "success": True,
                "message": "Text converted to speech",
                "text": text,
                "voice_id": voice_id
            }
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            return {
                "success": False,
                "message": f"Failed to convert text to speech: {str(e)}"
            }
    
    @mcp_server.tool()
    async def list_voices() -> Dict:
        """List available voices from ElevenLabs.
        
        Returns:
            A dictionary containing the list of available voices
        """
        try:
            voices = await client.get_voices()
            return {
                "success": True,
                "voices": voices
            }
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch voices: {str(e)}",
                "voices": []
            }
    
    @mcp_server.tool()
    async def get_models() -> Dict:
        """Get available TTS models from ElevenLabs.
        
        Returns:
            A dictionary containing the list of available models
        """
        try:
            models = await client.get_models()
            return {
                "success": True,
                "models": models
            }
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch models: {str(e)}",
                "models": []
            }
    
    logger.info("MCP tools registered successfully") 