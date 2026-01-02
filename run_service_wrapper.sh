#!/bin/bash
# Wrapper script to run figurine service

# Change to service directory
cd /home/fi/unfinished-figurine/src

# Run as user fi with lp group for printer access
# Use exec to replace shell process (so signals work properly)
exec sudo -u fi sg lp -c '/home/fi/unfinished-figurine/venv/bin/python3 /home/fi/unfinished-figurine/src/figurine_service.py'
