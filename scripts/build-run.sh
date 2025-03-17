#!/bin/bash
set -e

# Konfigurierbare Variablen
IMAGE_NAME="jessica-backend"
TAG=${TAG:-"latest"}

# Docker-Image bauen
echo "Docker-Image wird gebaut: ${IMAGE_NAME}:${TAG}"
docker build -t ${IMAGE_NAME}:${TAG} .

# Lokales Testen wenn --run Parameter angegeben
if [ "$1" = "--run" ]; then
    echo "Container wird gestartet..."
    docker run -it --rm \
        -p 9020:9020 \
        -p 9022:9022 \
        -e ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY:-"your-api-key-here"} \
        ${IMAGE_NAME}:${TAG}
else
    echo "Image erfolgreich gebaut: ${IMAGE_NAME}:${TAG}"
    echo "Verwende --run um den Container lokal zu starten"
    echo "Beispiel: ./scripts/build-run.sh --run"
fi 