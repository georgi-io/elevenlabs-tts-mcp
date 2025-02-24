#!/bin/bash

# Enable verbose output for debugging
set -x

# Ensure the static directory exists before building
echo "Ensuring static directory exists..."
mkdir -p src/backend/static

# Build the frontend
echo "Building frontend..."
cd src/frontend
npm run build

# Check if the build created a dist directory
echo "Checking for dist directory..."
if [ -d "dist" ]; then
    echo "Found dist directory, copying files to static directory..."
    # Copy all files from dist to static
    cp -r dist/* ../backend/static/
else
    echo "ERROR: dist directory not found after build!"
    ls -la
fi

# Verify the files were copied correctly
echo "Verifying files in static directory:"
ls -la ../backend/static/

# Start the backend server
echo "Starting backend server..."
cd ../..
poetry run python -m src.backend

echo "Server is running. Press Ctrl+C to stop." 