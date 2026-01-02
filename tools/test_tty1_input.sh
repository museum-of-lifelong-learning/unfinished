#!/bin/bash
# Send test input to tty1

echo "Sending test digits to tty1..."
echo "1" > /dev/tty1
sleep 0.5
echo "2" > /dev/tty1
sleep 0.5
echo "3" > /dev/tty1
sleep 0.5
echo "4" > /dev/tty1
sleep 0.5
echo "5" > /dev/tty1
sleep 0.5
echo "6" > /dev/tty1

echo "Test digits sent! Check tty1 output:"
sleep 2
sudo cat /dev/vcs1 | head -30
