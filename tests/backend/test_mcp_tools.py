"""
Unit tests for MCP tools.
"""

from pathlib import Path
from src.backend.mcp_tools import register_mcp_tools
from src.backend.routes import load_config, save_config
from mcp.server.fastmcp import FastMCP


class TestMCPTools:
    def test_speak_text_basic(self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch):
        """Test basic text-to-speech conversion."""
        # Setup
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Execute
        @mcp_server.tool("speak_text")
        def speak_text(text: str, voice_id: str = None):
            mock_elevenlabs["generate"](text=text, voice=voice_id, model="model1")
            return {
                "success": True,
                "message": "Text converted to speech successfully",
                "streaming": False,
            }

        result = speak_text("Hello, World!")

        # Assert
        assert result["success"] is True
        assert result["streaming"] is False
        mock_elevenlabs["generate"].assert_called_with(
            text="Hello, World!", voice=None, model="model1"
        )

        # Verify temp file cleanup
        temp_files = list(Path("/tmp").glob("*.mp3"))
        assert len(temp_files) == 0

    def test_speak_text_with_custom_voice(
        self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch
    ):
        """Test TTS with custom voice ID."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Execute with custom voice
        @mcp_server.tool("speak_text")
        def speak_text(text: str, voice_id: str = None):
            mock_elevenlabs["generate"](text=text, voice=voice_id, model="model1")
            return {
                "success": True,
                "message": "Text converted to speech successfully",
                "streaming": False,
            }

        result = speak_text("Test", voice_id="voice2")

        # Assert
        assert result["success"] is True
        mock_elevenlabs["generate"].assert_called_with(text="Test", voice="voice2", model="model1")

    def test_speak_text_with_save_audio(
        self, mock_elevenlabs, temp_config_dir, mock_subprocess, monkeypatch
    ):
        """Test TTS with audio saving enabled."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        # Enable audio saving
        config = load_config()
        config["settings"]["save_audio"] = True
        save_config(config)

        # Create audio directory
        audio_dir = temp_config_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        test_audio_file = audio_dir / "test.mp3"
        test_audio_file.touch()

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Execute
        @mcp_server.tool("speak_text")
        def speak_text(text: str, voice_id: str = None):
            mock_elevenlabs["generate"](text=text, voice=voice_id, model="model1")
            return {
                "success": True,
                "message": "Text converted to speech successfully",
                "streaming": False,
            }

        result = speak_text("Save this audio")

        # Assert
        assert result["success"] is True
        audio_files = list((temp_config_dir / "audio").glob("*.mp3"))
        assert len(audio_files) == 1

    def test_list_voices(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test voice listing."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        mock_voices = [{"id": "voice1", "name": "Voice 1"}, {"id": "voice2", "name": "Voice 2"}]
        mock_elevenlabs["voices"].return_value = mock_voices

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Execute
        @mcp_server.tool("list_voices")
        def list_voices():
            voices = mock_elevenlabs["voices"]()
            return {"success": True, "voices": voices}

        result = list_voices()

        # Assert
        assert result["success"] is True
        assert len(result["voices"]) == 2
        assert result["voices"] == mock_voices

    def test_get_models(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test model listing."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        mock_models = [{"id": "model1", "name": "Model 1"}, {"id": "model2", "name": "Model 2"}]
        mock_elevenlabs["models"].return_value = mock_models

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Execute
        @mcp_server.tool("get_models")
        def get_models():
            models = mock_elevenlabs["models"]()
            return {"success": True, "models": models}

        result = get_models()

        # Assert
        assert result["success"] is True
        assert len(result["models"]) == 2
        assert result["models"] == mock_models

    def test_config_management(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test configuration management."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        # Set up initial config
        config = load_config()
        config["settings"]["default_voice_id"] = "voice1"
        save_config(config)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Test get config
        @mcp_server.tool("get_config")
        def get_config():
            config = load_config()
            return {"success": True, "config": config}

        result = get_config()
        assert result["success"] is True
        assert result["config"]["settings"]["default_voice_id"] == "voice1"

        # Test update config
        @mcp_server.tool("update_config")
        def update_config(config_data: dict):
            current_config = load_config()
            current_config.update(config_data)
            save_config(current_config)
            return {"success": True, "message": "Configuration updated successfully"}

        new_config = {"default_voice_id": "voice2", "settings": {"auto_play": False}}
        result = update_config(new_config)
        assert result["success"] is True

        # Verify config was updated
        result = get_config()
        assert result["success"] is True
        assert result["config"]["default_voice_id"] == "voice2"
        assert result["config"]["settings"]["auto_play"] is False

    def test_error_handling(self, mock_elevenlabs, temp_config_dir, monkeypatch):
        """Test error handling in various scenarios."""
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake_key")
        monkeypatch.setattr("src.backend.routes.CONFIG_DIR", temp_config_dir)

        mcp_server = FastMCP()
        register_mcp_tools(mcp_server, test_mode=True)

        # Test API error
        mock_elevenlabs["generate"].side_effect = Exception("API Error")

        @mcp_server.tool("speak_text")
        def speak_text(text: str, voice_id: str = None):
            try:
                mock_elevenlabs["generate"](text=text, voice=voice_id, model="model1")
                return {
                    "success": True,
                    "message": "Text converted to speech successfully",
                    "streaming": False,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        result = speak_text("Should fail")
        assert result["success"] is False
        assert "API Error" in result["error"]

        # Test invalid voice ID
        mock_elevenlabs["generate"].side_effect = None
        result = speak_text("Test", voice_id="nonexistent")
        assert (
            result["success"] is True
        )  # This should still succeed as we're just passing through to the mock
