#!/bin/bash
# Simulation script for testing the figurine service
# This script sends test inputs to the service

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           FIGURINE SERVICE - TEST SIMULATOR                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will send test sequences to the service."
echo "Make sure the service is running first!"
echo ""
echo "Test sequences:"
echo "  1) 1-1-1-1-1-1 → Figurine #1"
echo "  2) 6-6-6-6-6-6 → Figurine #46656"
echo "  3) 1-2-3-4-5-6 → Figurine #1865"
echo "  4) 3-3-3-3-3-3 → Figurine #15850"
echo "  5) Custom input"
echo ""

read -p "Select test (1-5): " choice

case $choice in
  1)
    echo "Sending: 1-1-1-1-1-1"
    echo -e "1\n1\n1\n1\n1\n1"
    ;;
  2)
    echo "Sending: 6-6-6-6-6-6"
    echo -e "6\n6\n6\n6\n6\n6"
    ;;
  3)
    echo "Sending: 1-2-3-4-5-6"
    echo -e "1\n2\n3\n4\n5\n6"
    ;;
  4)
    echo "Sending: 3-3-3-3-3-3"
    echo -e "3\n3\n3\n3\n3\n3"
    ;;
  5)
    echo "Enter 6 digits (1-6):"
    read -p "  Digit 1: " d1
    read -p "  Digit 2: " d2
    read -p "  Digit 3: " d3
    read -p "  Digit 4: " d4
    read -p "  Digit 5: " d5
    read -p "  Digit 6: " d6
    echo "Sending: $d1-$d2-$d3-$d4-$d5-$d6"
    echo -e "$d1\n$d2\n$d3\n$d4\n$d5\n$d6"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "Note: This just shows what would be sent."
echo "To actually send it, pipe this script to the service or enter manually."
