"""
Pytest configuration and fixtures.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import json


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API responses."""
    with patch("elevenlabs.generate") as mock_generate, patch(
        "elevenlabs.voices"
    ) as mock_voices, patch("elevenlabs.Models") as mock_models:
        # Mock generate function
        mock_generate.return_value = b"fake_audio_data"

        # Mock voices
        mock_voices.return_value = [
            MagicMock(voice_id="voice1", name="Test Voice 1"),
            MagicMock(voice_id="voice2", name="Test Voice 2"),
        ]

        # Mock models
        mock_models.return_value = [
            MagicMock(model_id="model1", name="Test Model 1"),
            MagicMock(model_id="model2", name="Test Model 2"),
        ]

        yield {"generate": mock_generate, "voices": mock_voices, "models": mock_models}


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for tests."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Create default config
    config = {
        "default_voice_id": "voice1",
        "default_model_id": "model1",
        "settings": {"auto_play": True, "save_audio": False, "use_streaming": False},
    }

    config_file = temp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for audio playback."""
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        yield mock_popen
