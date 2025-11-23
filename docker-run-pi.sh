#!/bin/bash
# Build and run Figurine project in Docker (Raspberry Pi Mode)
set -e

echo "Building Docker image for Raspberry Pi..."
docker build -f Dockerfile.pi -t figurine-pi .

echo ""
echo "Starting container with webcam access (Pi mode)..."

docker run -it --rm \
    --name figurine-pi \
    --device=/dev/video0:/dev/video0 \
    -e FIGURINE_ENV=pi \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/models:/app/models" \
    figurine-pi

echo "Container stopped."
