import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { MCPServer } from '@modelcontextprotocol/sdk';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;
const mcpPort = process.env.MCP_PORT || 7000;

// Middleware
app.use(cors());
app.use(express.json());

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

// Initialize MCP Server
const mcpServer = new MCPServer({
  port: mcpPort,
});

mcpServer.start().then(() => {
  console.log(`MCP Server is running on port ${mcpPort}`);
}).catch((error) => {
  console.error('Failed to start MCP server:', error);
}); 