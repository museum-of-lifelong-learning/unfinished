#!/bin/bash
# Quick start script for manual testing

cd /home/fi/unfinished-figurine

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting figurine service with printer and serial permissions..."
echo ""
cd src
# Use -u for unbuffered output to see logs immediately
sg dialout -c "sg lp -c '/home/fi/unfinished-figurine/venv/bin/python3 -u figurine_service.py'"
