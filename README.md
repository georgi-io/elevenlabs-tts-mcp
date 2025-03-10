# Project Jessica (ElevenLabs TTS MCP)

This project integrates ElevenLabs Text-to-Speech capabilities with Cursor through the Model Context Protocol (MCP). It consists of a FastAPI backend service and a React frontend application.

## Features

- Text-to-Speech conversion using ElevenLabs API
- Voice selection and management
- MCP integration for Cursor
- Modern React frontend interface
- WebSocket real-time communication
- Pre-commit hooks for code quality
- Automatic code formatting and linting

## Project Structure

```
jessica/
├── src/
│   ├── backend/          # FastAPI backend service
│   └── frontend/         # React frontend application
├── terraform/            # Infrastructure as Code
├── tests/               # Test suites
└── docs/                # Documentation
```

## Requirements

- Python 3.11+
- Poetry (for backend dependency management)
- Node.js 18+ (for frontend)
- Cursor (for MCP integration)

## Local Development Setup

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/georgi-io/jessica.git
cd jessica

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your ElevenLabs API key

# Install pre-commit hooks
poetry run pre-commit install
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install
```

## Development Servers

### Starting the Backend

```bash
# Activate virtual environment if not active
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start the backend
python -m src.backend
```

The backend provides:
- REST API: http://localhost:9020
- WebSocket: ws://localhost:9020/ws
- MCP Server: http://localhost:9022

### Starting the Frontend

```bash
# In src/frontend directory
npm run dev
```

Frontend development server:
- http://localhost:5173

## Environment Configuration

### Backend (.env)
```env
# ElevenLabs API
ELEVENLABS_API_KEY=your-api-key

# Server Configuration
HOST=127.0.0.1
PORT=9020
MCP_PORT=9022

# Development Settings
DEBUG=false
RELOAD=true
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:9020
VITE_WS_URL=ws://localhost:9020/ws
```

## Code Quality Tools

### Backend

```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run specific tools
poetry run ruff check .
poetry run ruff format .
poetry run pytest
```

### Frontend

```bash
# Lint
npm run lint

# Type check
npm run type-check

# Test
npm run test
```

## Production Deployment

See [deployment-architecture.md](docs/deployment-architecture.md) for detailed deployment information.

### Quick Overview

- Frontend: Served from S3 via CloudFront at jessica.georgi.io
- Backend API: Available at api.georgi.io/jessica
- WebSocket: Connects to api.georgi.io/jessica/ws
- Infrastructure: Managed via Terraform in georgi-io-infrastructure repository

## MCP Integration with Cursor

1. Start the backend server
2. In Cursor settings, add new MCP server:
   - Name: Jessica TTS
   - Type: SSE
   - URL: http://localhost:9022/sse

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Error: "Invalid API key"
   - Solution: Check `.env` file

2. **Connection Problems**
   - Error: "Cannot connect to MCP server"
   - Solution: Verify backend is running and ports are correct

3. **Port Conflicts**
   - Error: "Address already in use"
   - Solution: Change ports in `.env`

4. **WebSocket Connection Failed**
   - Error: "WebSocket connection failed"
   - Solution: Ensure backend is running and WebSocket URL is correct

For additional help, please open an issue on GitHub.

## License

MIT 
