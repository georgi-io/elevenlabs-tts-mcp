# ElevenLabs Text-to-Speech MCP

This project integrates ElevenLabs Text-to-Speech capabilities with Cursor through the Model Context Protocol (MCP).

## To-Do

- [ ] Implement streaming audio support using the official ElevenLabs Python SDK
  - Replace current implementation with `convert_as_stream` method
  - Update backend to stream audio chunks to the client
  - Modify frontend to handle streaming audio playback
  - Reduce latency and improve user experience with real-time audio

## Quick Start

For the fastest way to get up and running:

```bash
# Clone the repository
git clone https://github.com/yourusername/elevenlabs-mcp.git
cd elevenlabs-mcp

# Create and configure your .env file
cp .env.example .env
# Edit .env file with your ElevenLabs API key
```

### Starting the Backend

```bash
# Start the backend server using the start script
chmod +x start.sh
./start.sh
```

The `start.sh` script will:
1. Build the frontend (but note: this is for production use only)
2. Start the backend server
3. Make the MCP server available at http://localhost:9022 for Cursor integration

### Starting the Frontend for Configuration

For configuration and testing, you should run the frontend development server separately:

```bash
# In a new terminal window
cd src/frontend
npm install
npm run dev
```

This will start the frontend development server at http://localhost:5173, which you can use to:
- Configure your ElevenLabs settings
- Test text-to-speech conversion
- Change default voices and models

After configuring through the frontend, you can use the MCP integration with Cursor as described below.

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

<img width="532" alt="image" src="https://github.com/user-attachments/assets/29f2666a-63e8-41a4-b7b5-414cb42dbc54" />


### Using MCP Tools in Cursor

Once connected, you can use the following MCP tools in Cursor:

1. Select text you want to convert to speech
2. Open the command palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows/Linux)
3. Type "MCP" to see available tools
4. Select "speak_text" to convert the selected text to speech
5. You can also use "list_voices" to see available voices and "get_models" to see available models

## Web Interface

The project includes a web interface for easy configuration and testing:

1. Start the frontend development server:
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

2. Access the web interface at http://localhost:5173

3. The web interface allows you to:
   - Test text-to-speech conversion directly in your browser
   - Change the default voice and model
   - Adjust settings like auto-play and audio saving
   - View and manage your ElevenLabs configuration

*Note: The backend server must be running for the web interface to function properly. The frontend will connect to the backend API at http://localhost:9020.*

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

4. **Frontend Development Server Issues**
   - Error: "Failed to start frontend development server"
   - Solution: Make sure Node.js is installed and run `npm install` in the frontend directory before running `npm run dev`

5. **Frontend Cannot Connect to Backend**
   - Error: "Failed to fetch" or "Network Error" in the frontend
   - Solution: Ensure the backend server is running at http://localhost:9020 and check that the CORS settings allow connections from the frontend

6. **No Audio Output**
   - Issue: Text is processed but no audio plays
   - Solution: Check your browser's audio settings and ensure auto-play is enabled in the configuration

For additional help, please open an issue on the GitHub repository.

## License

MIT 

## Development Setup

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. The hooks will:
1. Run code linting (ruff check)
2. Format code (ruff format)
3. Run unit tests (pytest)

To set up the pre-commit hooks:

```bash
# Install dependencies including dev dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

#### How the hooks work:

- **Ruff Check (with --fix)**: 
  - Runs before commit
  - Automatically fixes simple issues
  - If fixes are made, the files need to be staged again
  - You'll see "Files were modified by this hook" message

- **Ruff Format**:
  - Runs after ruff check
  - Formats your code according to the project's style
  - If files are reformatted, they need to be staged again

- **Pytest**:
  - Runs all unit tests
  - Commit will be blocked if tests fail

If any hook modifies files or fails:
1. The commit will be aborted
2. Review the changes made by the hooks
3. Stage the modified files (`git add .`)
4. Try committing again

You can also run the hooks manually:
```bash
# Run all hooks on all files
poetry run pre-commit run --all-files

# Run specific hook
poetry run pre-commit run ruff --all-files
poetry run pre-commit run ruff-format --all-files
poetry run pre-commit run pytest --all-files
``` 
