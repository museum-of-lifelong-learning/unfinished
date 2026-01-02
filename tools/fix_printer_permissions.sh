#!/bin/bash
# Fix printer permissions

echo "=== Fixing Printer Permissions ==="
echo ""

# Add user to lp group
echo "Adding user to 'lp' group..."
sudo usermod -a -G lp $USER

echo ""
echo "✓ User added to lp group"
echo ""
echo "IMPORTANT: You need to log out and log back in for changes to take effect."
echo "Or run: newgrp lp"
echo ""
echo "To verify: groups (should show 'lp' in the list)"
echo ""
echo "After logging back in, run: ./test_service.py"
