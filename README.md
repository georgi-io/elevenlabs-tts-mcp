# ElevenLabs Text-to-Speech MCP

This project integrates ElevenLabs Text-to-Speech capabilities with Cursor through the Model Context Protocol (MCP).

## Quick Start

For the fastest way to get up and running:

```bash
# Clone the repository
git clone https://github.com/yourusername/elevenlabs-mcp.git
cd elevenlabs-mcp

# Create and configure your .env file
cp .env.example .env
# Edit .env file with your ElevenLabs API key

# Install dependencies and start the application
chmod +x start.sh
./start.sh
```

The `start.sh` script will:
1. Build the frontend
2. Start the backend server
3. Make the application available at http://localhost:9020 (web interface) and http://localhost:9022 (MCP server)

After starting, follow the "MCP Integration with Cursor" section below to connect to Cursor.

## Features

- Text-to-Speech conversion using ElevenLabs API
- Voice selection and management
- MCP integration for Cursor
- Web interface for testing and configuration

## Requirements

- Python 3.11+
- Poetry (for dependency management)
- Node.js 18+ (for frontend development)
- Cursor (for MCP integration)

## Installation

### Backend

```bash
# Install dependencies
poetry install

# Create .env file
cp .env.example .env
# Edit .env file with your ElevenLabs API key
```

### Frontend

```bash
# Install dependencies
cd frontend
npm install
```

## Development

### Running the backend server

```bash
# Start the backend server
python -m src.backend
```

The backend server will start on http://localhost:9020 and the MCP server will start on http://localhost:9022.

### Running the frontend server

```bash
# Start the frontend server
cd frontend
npm run dev
```

The frontend server will start on http://localhost:5173.

## MCP Integration with Cursor

To connect the MCP server to Cursor:

1. Make sure the backend server is running with `python -m src.backend`
2. Open Cursor and go to Settings (gear icon or Cmd+, on Mac, Ctrl+, on Windows/Linux)
3. Navigate to the "MCP" section
4. Add a new MCP server with:
   - Name: ElevenLabs TTS
   - Type: SSE
   - URL: http://localhost:9022/sse

5. Save the configuration
6. You should see a green checkmark indicating a successful connection

### Using MCP Tools in Cursor

Once connected, you can use the following MCP tools in Cursor:

1. Select text you want to convert to speech
2. Open the command palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows/Linux)
3. Type "MCP" to see available tools
4. Select "speak_text" to convert the selected text to speech
5. You can also use "list_voices" to see available voices and "get_models" to see available models

## Web Interface

The project includes a web interface for easy configuration and testing:

1. Access the web interface at http://localhost:9020 after starting the server
2. The web interface allows you to:
   - Test text-to-speech conversion directly in your browser
   - Change the default voice and model
   - Adjust settings like auto-play and audio saving
   - View and manage your ElevenLabs configuration

*Note: Screenshots of the web interface will be added to this README.*

## Configuration

You can configure the following settings in the `.env` file:

- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `PORT`: Port for the main backend server (default: 9020)
- `WS_PORT`: Port for WebSocket connections (default: 9021)
- `MCP_PORT`: Port for the MCP server (default: 9022)
- `DEFAULT_VOICE_ID`: Default voice ID to use for text-to-speech

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Error: "Invalid API key"
   - Solution: Ensure your ElevenLabs API key is correctly set in the `.env` file

2. **Connection Problems**
   - Error: "Cannot connect to MCP server"
   - Solution: Make sure the backend server is running and the MCP URL in Cursor settings is correct (http://localhost:9022/sse)

3. **Port Conflicts**
   - Error: "Address already in use"
   - Solution: Change the ports in the `.env` file if they conflict with other applications

4. **Frontend Build Failures**
   - Error: "Failed to build frontend"
   - Solution: Make sure Node.js is installed and run `npm install` in the frontend directory before building

5. **No Audio Output**
   - Issue: Text is processed but no audio plays
   - Solution: Check your browser's audio settings and ensure auto-play is enabled in the configuration

For additional help, please open an issue on the GitHub repository.

## License

MIT 