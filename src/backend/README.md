# Jessica Backend Service

FastAPI-based backend service for the Jessica Text-to-Speech application with ElevenLabs API integration and MCP (Message Control Protocol).

## Configuration

The service can be configured via environment variables or a `.env` file.

### Main Settings

| Variable | Default Value | Description |
|----------|--------------|--------------|
| ELEVENLABS_API_KEY | - | API key for ElevenLabs |
| HOST | 127.0.0.1 | Host address (0.0.0.0 for containers) |
| PORT | 9020 | HTTP port |
| LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| MCP_PORT | 9022 | MCP port |

### Path Routing with ROOT_PATH

The service supports running behind API Gateway or Application Load Balancer with path prefix.

| Variable | Default Value | Description |
|----------|--------------|--------------|
| ROOT_PATH | "" | Path prefix for API Gateway/ALB integration |

#### How it works:

1. **Local Development**: In local development, `ROOT_PATH` remains empty (""), making the API accessible at `http://localhost:9020/`.

2. **Production**: In an AWS environment, ROOT_PATH can be set to e.g. `/jessica-backend`. The middleware ensures that:
   - Requests to `/jessica-backend/health` are processed internally as `/health`
   - The FastAPI documentation and all links contain the correct path
   - The middleware layer automatically removes the ROOT_PATH prefix

3. **Middleware**: The path-rewriting middleware ensures that incoming paths with the ROOT_PATH prefix are automatically rewritten.

### Example Configuration

```env
# Local
ROOT_PATH=

# Production with API Gateway/ALB
ROOT_PATH=/jessica-backend
```

## API Endpoints

The main API is available under `/api`, making endpoints with ROOT_PATH accessible as follows:

- Local: `http://localhost:9020/api/...`
- Production: `https://example.com/jessica-backend/api/...`

### Health Check

The health check endpoint is always available at `/health`:

```
GET /health
```

This also provides information about the configured ROOT_PATH. 