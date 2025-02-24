#!/bin/bash

# Build the frontend
echo "Building frontend..."
cd src/frontend
npm run build

# Start the backend server
echo "Starting backend server..."
cd ../..
poetry run python -m src.backend

echo "Server is running. Press Ctrl+C to stop." 