#!/bin/bash
# Install udev rules for printer USB access

echo "=== Installing Printer USB Access Rules ==="
echo ""

# Copy udev rule
echo "Installing udev rule..."
sudo cp /home/fi/unfinished-figurine/99-epson-printer.rules /etc/udev/rules.d/

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "Checking printer device..."
lsusb | grep -i epson

echo ""
echo "✓ Udev rules installed!"
echo ""
echo "Now unplug and replug the printer, or run:"
echo "  sudo udevadm trigger"
echo ""
echo "Then test with: ./run_test_with_permissions.sh"
