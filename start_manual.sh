#!/bin/bash
# Quick start script for manual testing

cd /home/fi/unfinished-figurine

echo "Activating virtual environment..."
source venv/bin/activate

# Check for --no-print flag
ARGS=""
if [[ "$1" == "--no-print" ]]; then
    echo "Starting figurine service (NO PRINTING MODE - saves paper)..."
    ARGS="--no-print"
else
    echo "Starting figurine service with printer and serial permissions..."
fi

echo ""
cd src
# Use -u for unbuffered output to see logs immediately
sg dialout -c "sg lp -c '/home/fi/unfinished-figurine/venv/bin/python3 -u figurine_service.py $ARGS'"
