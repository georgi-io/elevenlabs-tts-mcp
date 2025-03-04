"""
Unit tests for MCP tools.
"""

import pytest
from pathlib import Path
import json
import os
from src.backend.mcp_tools import register_mcp_tools, load_config, save_config
from mcp.server.fastmcp import FastMCP


class TestMCPTools:
    def test_speak_text_basic(self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch):
        """Test basic text-to-speech conversion."""
        # Setup
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Execute
        result = mcp_server.tools["speak_text"]("Hello, World!")

        # Assert
        assert result["success"] is True
        assert "streaming" in result
        assert result["streaming"] is False
        mock_elevenlabs["generate"].assert_called_once()

        # Verify temp file cleanup
        temp_files = list(Path("/tmp").glob("*.mp3"))
        assert len(temp_files) == 0

    def test_speak_text_with_custom_voice(
        self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch
    ):
        """Test TTS with custom voice ID."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Execute with custom voice
        result = mcp_server.tools["speak_text"]("Test", voice_id="voice2")

        # Assert
        assert result["success"] is True
        mock_elevenlabs["generate"].assert_called_with(text="Test", voice="voice2", model="model1")

    def test_speak_text_with_save_audio(
        self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch
    ):
        """Test TTS with audio saving enabled."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        # Enable audio saving
        config = load_config()
        config["settings"]["save_audio"] = True
        save_config(config)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Execute
        result = mcp_server.tools["speak_text"]("Save this audio")

        # Assert
        assert result["success"] is True
        audio_files = list((temp_config_dir / "audio").glob("*.mp3"))
        assert len(audio_files) == 1

    def test_list_voices(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test voice listing."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Execute
        result = mcp_server.tools["list_voices"]()

        # Assert
        assert result["success"] is True
        assert len(result["voices"]) == 2
        assert result["voices"][0]["voice_id"] == "voice1"
        assert result["voices"][1]["name"] == "Test Voice 2"

    def test_get_models(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test model listing."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Execute
        result = mcp_server.tools["get_models"]()

        # Assert
        assert result["success"] is True
        assert len(result["models"]) == 2
        assert result["models"][0]["model_id"] == "model1"
        assert result["models"][1]["name"] == "Test Model 2"

    def test_config_management(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test configuration management."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Test get config
        result = mcp_server.tools["get_config"]()
        assert result["success"] is True
        assert result["config"]["default_voice_id"] == "voice1"

        # Test update config
        new_config = {"default_voice_id": "voice2", "settings": {"auto_play": False}}
        result = mcp_server.tools["update_config"](new_config)
        assert result["success"] is True
        assert result["config"]["default_voice_id"] == "voice2"
        assert result["config"]["settings"]["auto_play"] is False

        # Verify persistence
        saved_config = load_config()
        assert saved_config["default_voice_id"] == "voice2"
        assert saved_config["settings"]["auto_play"] is False

    def test_error_handling(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test error handling in various scenarios."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.mcp_tools.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server)

        # Test API error
        mock_elevenlabs["generate"].side_effect = Exception("API Error")
        result = mcp_server.tools["speak_text"]("Should fail")
        assert result["success"] is False
        assert "error" in result

        # Test invalid voice ID
        result = mcp_server.tools["speak_text"]("Test", voice_id="nonexistent")
        assert result["success"] is False

        # Test config file corruption
        with open(temp_config_dir / "config.json", "w") as f:
            f.write("invalid json")

        result = mcp_server.tools["get_config"]()
        assert result["success"] is True  # Should return default config
        assert "default_voice_id" in result["config"]
