# ElevenLabs Text-to-Speech MCP Integration

A Cursor MCP (Machine Control Protocol) application that converts text output into spoken words using the ElevenLabs Text-to-Speech API.

## Features

- FastAPI backend with MCP integration
- Real-time text-to-speech conversion
- WebSocket-based communication
- Voice selection and preview
- Cursor MCP integration

## Requirements

- Python 3.11+
- Poetry for dependency management
- ElevenLabs API key

## Installation

```bash
# Install dependencies
poetry install

# Create .env file and add your ElevenLabs API key
echo "ELEVENLABS_API_KEY=your-api-key-here" > .env
```

## Development

```bash
# Run the backend server
poetry run uvicorn src.backend.main:app --reload

# Run MCP binary
poetry run elevenlabs-mcp
```

## License

MIT 