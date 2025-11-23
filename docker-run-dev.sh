#!/bin/bash
# Build and run Figurine project in Docker (Development Mode)
set -e

echo "Building Docker image for development..."
docker build -t figurine-dev .

echo ""
echo "Starting container with webcam access..."

# Allow X11 forwarding for GUI (optional, for debug window)
xhost +local:docker 2>/dev/null || echo "Note: X11 forwarding not available"

docker run -it --rm \
    --name figurine-dev \
    --device=/dev/video0:/dev/video0 \
    -e DISPLAY=$DISPLAY \
    -e FIGURINE_ENV=dev \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$(pwd)/src:/app/src" \
    -v "$(pwd)/config:/app/config" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/models:/app/models" \
    figurine-dev \
    /bin/bash

echo "Container stopped."
