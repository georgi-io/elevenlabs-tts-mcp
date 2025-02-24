#!/bin/bash

# Build the frontend
echo "Building frontend..."
npm run build

# Create static directory in backend if it doesn't exist
mkdir -p ../backend/static

# Copy the build output to the backend static directory
echo "Copying build files to backend/static..."
cp -r dist/* ../backend/static/

echo "Frontend build complete!" 