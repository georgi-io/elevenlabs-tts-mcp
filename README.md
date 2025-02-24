# ElevenLabs Text-to-Speech MCP Integration

A Cursor MCP (Machine Control Protocol) application that converts text output into spoken words using the ElevenLabs Text-to-Speech API.

## Features

- FastAPI backend with MCP integration
- React + TypeScript frontend with TailwindCSS
- Real-time text-to-speech conversion
- Voice selection and preview
- Cursor MCP integration

## Requirements

- Python 3.11+
- Poetry for dependency management
- Node.js 18+ and npm for frontend development
- ElevenLabs API key

## Installation

```bash
# Install backend dependencies
poetry install

# Create .env file and add your ElevenLabs API key
echo "ELEVENLABS_API_KEY=your-api-key-here" > .env

# Install frontend dependencies
cd src/frontend
npm install
```

## Development

The project can be developed in two different ways:

### Development Mode (Separate Servers)

In this mode, frontend and backend run as separate servers:

#### Backend

```bash
# Run the backend server
poetry run uvicorn src.backend.app:app --reload
```

The backend server runs on the port configured in the `.env` file (default is 9020).

#### Frontend

```bash
# Run the frontend development server
cd src/frontend
npm run dev
```

The frontend development server runs on its own port (default is 5173) and forwards API requests to the backend server through a proxy. This enables hot-reloading and other development tools.

### Production Mode (All-in-One)

For production or testing purposes, the entire project can be started with a single command:

```bash
# Build and start the entire application
./start.sh
```

This script builds the frontend and copies it to the backend directory, then starts the backend server which serves both the API as well as the static frontend files.

### Manual Build

```bash
# Build the frontend
cd src/frontend
npm run build

# Start the server
cd ../..
poetry run uvicorn src.backend.app:app
```

### MCP Binary

```bash
# Run MCP binary
poetry run elevenlabs-mcp
```

## Configuration

The application is configured through the `.env` file:

```
# ElevenLabs API Configuration
ELEVENLABS_API_KEY=your-api-key-here

# Server Configuration
HOST=127.0.0.1
PORT=9020
LOG_LEVEL=INFO

# WebSocket Configuration
WS_HOST=127.0.0.1
WS_PORT=9021

# Development Settings
DEBUG=false
RELOAD=true

# MCP Configuration
MCP_PORT=9022
```

## License

MIT 