# ElevenLabs Text-to-Speech MCP Integration

## Project Overview
A Cursor MCP (Machine Control Protocol) application that converts text output into spoken words using the ElevenLabs Text-to-Speech API. The system consists of three main components: a backend service, a web interface, and an MCP binary for Cursor integration.

## Core Components

### 1. Backend Service
- Node.js based application
- MCP SDK integration (@modelcontextprotocol/sdk v1.6.0)
- Environment configuration management (`.env` support)
- Configuration file handling for persistent settings
- API endpoint for Text-to-Speech conversion
- Event routing between components

### 2. Web Interface
- Standalone web UI
- Text-to-Speech testing functionality
- Voice selection and preview capabilities
- Real-time display of TTS responses
- Event listener for MCP commands

### 3. MCP Binary
- Standalone Node.js binary
- MCP command integration for Cursor
- Communication with backend service
- Text-to-Speech command handling

## System Architecture
- Backend intercepts and routes TTS responses to Web UI
- Web UI runs independently in browser
- MCP Binary acts as bridge between Cursor and backend
- Event-driven communication between components
- Asynchronous TTS processing

## Technical Requirements
- Node.js runtime environment
- ElevenLabs API key configuration
- Browser compatibility for Web UI
- Cursor MCP protocol support
- Local configuration persistence 