import asyncio
import json
import logging
import base64
from typing import Dict, List, Optional, Set, AsyncGenerator
import os
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
WS_HOST = os.getenv("WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("WS_PORT", "9021"))

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.mcp_connection: Optional[WebSocket] = None
        logger.info(f"WebSocket manager initialized on {WS_HOST}:{WS_PORT}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection: {websocket}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        if self.mcp_connection == websocket:
            self.mcp_connection = None
            logger.info("MCP connection disconnected")
        logger.info(f"WebSocket disconnected: {websocket}")

    async def register_mcp(self, websocket: WebSocket):
        """Register a connection as the MCP binary connection"""
        self.mcp_connection = websocket
        logger.info(f"MCP binary registered: {websocket}")
        await self.broadcast_to_clients({"type": "mcp_status", "connected": True})

    async def send_to_mcp(self, message: Dict):
        """Send a message to the MCP binary"""
        if self.mcp_connection:
            await self.mcp_connection.send_text(json.dumps(message))
            logger.debug(f"Message sent to MCP: {message}")
        else:
            logger.warning("Attempted to send message to MCP, but no MCP connection is available")

    async def broadcast_to_clients(self, message: Dict):
        """Broadcast a message to all connected clients except MCP"""
        for connection in self.active_connections:
            if connection != self.mcp_connection:
                await connection.send_text(json.dumps(message))
        logger.debug(f"Broadcast message to {len(self.active_connections) - (1 if self.mcp_connection else 0)} clients")

    async def handle_mcp_message(self, message: Dict):
        """Handle a message from the MCP binary"""
        message_type = message.get("type")
        
        if message_type == "tts_result":
            # Forward TTS result to all clients
            await self.broadcast_to_clients(message)
        elif message_type == "voice_list":
            # Forward voice list to all clients
            await self.broadcast_to_clients(message)
        elif message_type == "audio_chunk":
            # Forward audio chunk to all clients
            await self.broadcast_to_clients(message)
        elif message_type == "audio_complete":
            # Forward audio complete message to all clients
            await self.broadcast_to_clients(message)
        elif message_type == "error":
            # Forward error to all clients
            await self.broadcast_to_clients(message)
        else:
            logger.warning(f"Unknown message type from MCP: {message_type}")

    async def stream_audio_to_clients(self, audio_stream: AsyncGenerator[bytes, None], text: str, voice_id: str):
        """Stream audio chunks to all connected clients."""
        try:
            # Send start message
            await self.broadcast_to_clients({
                "type": "audio_start",
                "text": text,
                "voice_id": voice_id
            })
            
            # Stream audio chunks
            chunk_count = 0
            async for chunk in audio_stream:
                chunk_count += 1
                # Encode chunk as base64 for JSON transmission
                encoded_chunk = base64.b64encode(chunk).decode('utf-8')
                
                # Send chunk to all clients
                await self.broadcast_to_clients({
                    "type": "audio_chunk",
                    "chunk_index": chunk_count,
                    "data": encoded_chunk
                })
                
                # Small delay to avoid overwhelming clients
                await asyncio.sleep(0.01)
            
            # Send completion message
            await self.broadcast_to_clients({
                "type": "audio_complete",
                "total_chunks": chunk_count
            })
            
            logger.info(f"Successfully streamed {chunk_count} audio chunks to clients")
        except Exception as e:
            logger.error(f"Error streaming audio to clients: {str(e)}")
            await self.broadcast_to_clients({
                "type": "error",
                "message": f"Audio streaming error: {str(e)}"
            })

# Create a singleton instance
manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Check if this is an MCP registration message
            if message.get("type") == "register" and message.get("client") == "mcp":
                await manager.register_mcp(websocket)
                continue
                
            # If this is the MCP connection, handle its messages
            if websocket == manager.mcp_connection:
                await manager.handle_mcp_message(message)
            else:
                # This is a regular client, forward to MCP if needed
                if message.get("type") == "tts_request":
                    await manager.send_to_mcp(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket) 