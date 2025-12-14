#!/bin/bash
# Install Figurine project in development mode (Linux notebook)
set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variable for dev mode
export FIGURINE_ENV=dev

echo "\nFigurine project installed in development mode."
echo "Activate your environment with: source venv/bin/activate"
echo "Run: python src/main.py"
