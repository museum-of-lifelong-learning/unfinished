#!/bin/bash
# Run the test service with necessary group permissions (dialout for serial, lp for printer)
# This ensures the user has access to USB/Serial devices.

echo "Running test_service.py with 'dialout' and 'lp' group permissions..."
sg dialout -c "sg lp -c './venv/bin/python3 test_service.py'"
