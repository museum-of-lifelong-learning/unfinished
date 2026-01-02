#!/bin/bash
# Continuously watch tty8 and logs

echo "=== Watching Figurine Service ==="
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "Starting in 2 seconds..."
sleep 2

# Watch both tty8 screen and logs
watch -n 0.5 -t '
echo "=== TTY8 SCREEN ==="
sudo cat /dev/vcs8 2>/dev/null | head -25
echo ""
echo "=== RECENT LOGS ==="
sudo journalctl -u figurine.service -n 8 --no-pager -o cat 2>/dev/null | grep -E "\[MAIN\]|\[OLLAMA\]|\[RECEIPT\]|error|Error" || tail -8 /tmp/figurine_service.log 2>/dev/null || echo "No logs yet"
echo ""
echo "=== SERVICE STATUS ==="
systemctl is-active figurine.service
'
