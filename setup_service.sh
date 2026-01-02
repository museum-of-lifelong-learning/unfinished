#!/bin/bash
# Setup script for Figurine Service

echo "=== Figurine Service Setup ==="
echo ""
echo "This will configure the service to run on tty8 (/dev/tty8)"
echo "You can interact with it by switching to tty8 (Ctrl+Alt+F8)"
echo ""
echo "Alternatively, run manually with: ./start_manual.sh"
echo ""
read -p "Continue with systemd installation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled. Use './start_manual.sh' to run the service."
    exit 0
fi
echo ""

# Add user to lp group for printer access
echo "Adding user to 'lp' group for printer access..."
sudo usermod -a -G lp fi

# Install udev rules
echo "Installing udev rules for printer..."
if [ -f /home/fi/unfinished-figurine/install_udev_rules.sh ]; then
    ./install_udev_rules.sh
fi

# Copy service file to systemd
echo "Installing systemd service..."
sudo cp /home/fi/unfinished-figurine/figurine.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service to start on boot
echo "Enabling service to start on boot..."
sudo systemctl enable figurine.service

echo ""
echo "=== Setup Complete ==="
echo ""
echo "The service is configured to run on /dev/tty8 (virtual console 8)"
echo ""
echo "To interact with the service:"
echo "  - Physical console: Press Ctrl+Alt+F8"
echo "  - Return to GUI: Press Ctrl+Alt+F7 (or F1/F2)"
echo "  - Via SSH: sudo cat /dev/vcs8 (to view) or ./connect_to_tty8.sh"
echo ""
echo "Service commands:"
echo "  Start service:   sudo systemctl start figurine.service"
echo "  Stop service:    sudo systemctl stop figurine.service"
echo "  Check status:    sudo systemctl status figurine.service"
echo "  View logs:       journalctl -u figurine.service -f"
echo ""
echo "Or run manually: ./start_manual.sh"
echo ""
echo "NOTE: You may need to log out and log back in for group changes to take effect."
echo "      Or run: newgrp lp"
