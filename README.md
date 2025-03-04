# ElevenLabs Text-to-Speech MCP

This project integrates ElevenLabs Text-to-Speech capabilities with Cursor through the Model Context Protocol (MCP).

## Features

- Text-to-Speech conversion using ElevenLabs API
- Voice selection and management
- MCP integration for Cursor
- Web interface for testing and configuration
- Pre-commit hooks for code quality
- Automatic code formatting and linting

## Requirements

- Python 3.11+
- Poetry (for dependency management)
- Node.js 18+ (for frontend development)
- Cursor (for MCP integration)

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/elevenlabs-mcp.git
cd elevenlabs-mcp

# Install backend dependencies
poetry install

# Install frontend dependencies
cd src/frontend
npm install
cd ../..

# Create and configure your .env file
cp .env.example .env
# Edit .env with your ElevenLabs API key

# Install pre-commit hooks
poetry run pre-commit install
```

## Development

### Starting the Services

```bash
# Start the backend (in one terminal)
python -m src.backend

# Start the frontend (in another terminal)
cd src/frontend
npm run dev
```

- Backend: http://localhost:9020
- Frontend: http://localhost:5173
- MCP Server: http://localhost:9022
- WebSocket: ws://localhost:9021

### Code Quality Tools

This project uses several tools to maintain code quality:

#### Pre-commit Hooks

The following hooks run automatically before each commit:

1. **Ruff Check**: Lints and fixes Python code
2. **Ruff Format**: Formats Python code
3. **Pytest**: Runs unit tests

You can run these manually:

```bash
# Run all hooks
poetry run pre-commit run --all-files

# Run specific hooks
poetry run pre-commit run ruff --all-files
poetry run pre-commit run ruff-format --all-files
poetry run pre-commit run pytest --all-files
```

#### Direct Tool Usage

For more control, you can use the tools directly:

```bash
# Show linting errors
poetry run ruff check .

# Fix linting errors automatically
poetry run ruff check --fix .

# Format code
poetry run ruff format .
```

### Configuration

Environment variables (`.env`):
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `PORT`: Backend server port (default: 9020)
- `WS_PORT`: WebSocket port (default: 9021)
- `MCP_PORT`: MCP server port (default: 9022)
- `DEFAULT_VOICE_ID`: Default voice ID

## Usage

### MCP Integration with Cursor

1. Start the backend server
2. In Cursor settings, add new MCP server:
   - Name: ElevenLabs TTS
   - Type: SSE
   - URL: http://localhost:9022/sse

### Web Interface

Access http://localhost:5173 to:
- Test text-to-speech conversion
- Configure default voice and model
- Adjust settings like auto-play

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Error: "Invalid API key"
   - Solution: Check `.env` file

2. **Connection Problems**
   - Error: "Cannot connect to MCP server"
   - Solution: Verify backend is running and MCP URL is correct

3. **Port Conflicts**
   - Error: "Address already in use"
   - Solution: Change ports in `.env`

4. **No Audio Output**
   - Issue: Text processed but no audio
   - Solution: Check auto-play settings

For additional help, please open an issue on GitHub.

## License

MIT 
