"""
MCP Tools for ElevenLabs TTS

This module defines the MCP tools that will be exposed to Cursor.
"""

import logging
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
from .elevenlabs_client import ElevenLabsClient
from mcp.server.fastmcp import FastMCP
from .websocket import manager
import tempfile
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "elevenlabs-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Create config directory if it doesn't exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "default_voice_id": "21m00Tcm4TlvDq8ikWAM",
    "default_model_id": "eleven_monolingual_v1",
    "settings": {
        "auto_play": True,
    },
}

# Initialize ElevenLabs client
client = None  # We'll initialize this when registering tools


def load_config() -> Dict:
    """Load configuration from file or create default if it doesn't exist."""
    try:
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if not CONFIG_FILE.exists():
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            return DEFAULT_CONFIG

        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Ensure all default keys exist
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG


def save_config(config: Dict) -> Dict:
    """Save configuration to file."""
    try:
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

        return config
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return config


def register_mcp_tools(mcp_server: FastMCP, test_mode: bool = False) -> None:
    """Register MCP tools with the server."""
    global client
    client = ElevenLabsClient(test_mode=test_mode)

    @mcp_server.tool("speak_text")
    async def speak_text(text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech using ElevenLabs.

        Args:
            text: The text to convert to speech
            voice_id: Optional voice ID to use (defaults to configured voice)

        Returns:
            A dictionary with the result of the operation
        """
        try:
            # Load configuration
            config = load_config()

            # Use provided voice_id or default from config
            selected_voice_id = voice_id or config["default_voice_id"]
            selected_model_id = config["default_model_id"]

            logger.info(
                f"Converting text to speech with voice ID: {selected_voice_id} and model ID: {selected_model_id}"
            )

            # Generate audio using our client instance
            audio = await client.text_to_speech(text, selected_voice_id, selected_model_id)

            if config["settings"]["auto_play"] and os.name == "posix":
                # Create temporary file for playback
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_file.write(audio)
                    temp_path = temp_file.name

                try:
                    # Play the audio
                    subprocess.Popen(["afplay", temp_path])
                    logger.info("Playing audio...")

                    # Schedule file deletion after estimated playback time
                    # Assuming ~1 second per 20 characters of text
                    playback_time = len(text) / 20 + 1  # +1 second buffer

                    def cleanup_temp_file():
                        try:
                            os.unlink(temp_path)
                            logger.info("Temporary audio file cleaned up")
                        except Exception as e:
                            logger.error(f"Error cleaning up temporary file: {e}")

                    # Schedule cleanup
                    timer = threading.Timer(playback_time, cleanup_temp_file)
                    timer.start()
                except Exception as e:
                    # Clean up if playback fails
                    os.unlink(temp_path)
                    logger.error(f"Error playing audio: {e}")

            return {
                "success": True,
                "message": "Text converted to speech successfully",
                "streaming": False,
            }
        except Exception as e:
            logger.error(f"Error in speak_text: {e}")
            return {"success": False, "error": str(e)}

    async def stream_text_to_speech(text: str, voice_id: str, model_id: str, config: Dict):
        """Stream text to speech using ElevenLabs API."""
        try:
            # Create output directory if it doesn't exist
            output_dir = CONFIG_DIR / "audio"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate a filename
            text_preview = text[:10] if len(text) > 10 else text
            voice_id_short = voice_id[-6:] if len(voice_id) > 6 else voice_id
            output_file = output_dir / f"speech_{text_preview}_{voice_id_short}.mp3"

            # Stream to clients via WebSocket
            await manager.stream_audio_to_clients(
                audio_stream=client.text_to_speech_stream(text, voice_id, model_id),
                text=text,
                voice_id=voice_id,
            )

            # If save_audio is enabled, also save the complete file
            if config["settings"]["save_audio"]:
                # We need to get the audio again since the stream was consumed
                audio = await client.text_to_speech(text, voice_id, model_id)

                with open(output_file, "wb") as f:
                    f.write(audio)

                logger.info(f"Audio saved to {output_file}")

                # Auto-play on macOS if enabled
                if config["settings"]["auto_play"] and os.name == "posix":
                    try:
                        subprocess.Popen(["afplay", str(output_file)])
                        logger.info("Playing audio...")
                    except Exception as e:
                        logger.error(f"Error playing audio: {e}")

            logger.info("Successfully streamed text to speech")
        except Exception as e:
            logger.error(f"Error streaming text to speech: {e}")
            await manager.broadcast_to_clients(
                {"type": "error", "message": f"Error streaming text to speech: {str(e)}"}
            )

    @mcp_server.tool("list_voices")
    async def list_voices(random_string: str = "") -> Dict[str, Any]:
        """List available voices from ElevenLabs.

        Returns:
            A dictionary containing the list of available voices
        """
        try:
            available_voices = await client.get_voices()
            return {"success": True, "voices": available_voices}
        except Exception as e:
            logger.error(f"Error in list_voices: {e}")
            return {"success": False, "error": str(e)}

    @mcp_server.tool("get_models")
    async def get_models(random_string: str = "") -> Dict[str, Any]:
        """Get available TTS models from ElevenLabs.

        Returns:
            A dictionary containing the list of available models
        """
        try:
            available_models = await client.get_models()
            return {"success": True, "models": available_models}
        except Exception as e:
            logger.error(f"Error in get_models: {e}")
            return {"success": False, "error": str(e)}

    @mcp_server.tool("get_config")
    def get_config(random_string: str = "") -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            A dictionary containing the current configuration
        """
        try:
            config = load_config()
            return {"success": True, "config": config}
        except Exception as e:
            logger.error(f"Error in get_config: {e}")
            return {"success": False, "error": str(e)}

    @mcp_server.tool("update_config")
    def update_config(config_data: Dict) -> Dict[str, Any]:
        """Update configuration.

        Args:
            config_data: Dictionary containing configuration updates

        Returns:
            A dictionary containing the updated configuration
        """
        try:
            current_config = load_config()

            # Update configuration with provided data
            if "default_voice_id" in config_data:
                current_config["default_voice_id"] = config_data["default_voice_id"]

            if "default_model_id" in config_data:
                current_config["default_model_id"] = config_data["default_model_id"]

            if "settings" in config_data:
                # Ensure all settings exist
                if "settings" not in current_config:
                    current_config["settings"] = {}

                # Initialize missing settings with defaults
                for key in DEFAULT_CONFIG["settings"]:
                    if key not in current_config["settings"]:
                        current_config["settings"][key] = DEFAULT_CONFIG["settings"][key]

                # Update provided settings
                for key, value in config_data["settings"].items():
                    current_config["settings"][key] = value

            # Save updated configuration
            updated_config = save_config(current_config)

            return {"success": True, "config": updated_config}
        except Exception as e:
            logger.error(f"Error in update_config: {e}")
            return {"success": False, "error": str(e)}

    logger.info("MCP tools registered successfully")
