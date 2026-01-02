#!/bin/bash
# Quick verification after permission fix

echo "=== Verifying Setup ==="
echo ""

echo "1. Checking user groups..."
groups_output=$(groups)
if [[ $groups_output == *"lp"* ]]; then
    echo "   ✓ User is in 'lp' group"
else
    echo "   ✗ User is NOT in 'lp' group"
    echo "   → Run: ./fix_printer_permissions.sh"
    echo "   → Then log out and log back in (or run: newgrp lp)"
    exit 1
fi

echo ""
echo "2. Checking Ollama model..."
if ollama list | grep -q "qwen2.5:7b"; then
    echo "   ✓ qwen2.5:7b model is available"
else
    echo "   ✗ qwen2.5:7b model NOT found"
    echo "   → Available models:"
    ollama list
    exit 1
fi

echo ""
echo "3. Checking printer device..."
if [ -e /dev/usb/lp0 ]; then
    echo "   ✓ Printer device exists: /dev/usb/lp0"
    ls -la /dev/usb/lp0
else
    echo "   ✗ Printer device not found"
    echo "   → Check USB connection: lsusb | grep Epson"
    exit 1
fi

echo ""
echo "=== All Checks Passed! ==="
echo ""
echo "You can now run: ./test_service.py"
