#!/usr/bin/env python3
"""
Test script for the LED Display states.
Allows interactive testing of all display patterns.
"""

import sys
import time
import glob
import serial

def get_serial_port():
    """Auto-detect or ask for serial port."""
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    if not ports:
        print("No serial ports found!")
        return None
    
    print("Available ports:")
    for i, p in enumerate(ports):
        print(f"{i+1}: {p}")
    
    if len(ports) == 1:
        return ports[0]
        
    try:
        idx = int(input("Select port (number): ")) - 1
        return ports[idx]
    except:
        return None

def main():
    print("=== Display State Tester ===")
    port = get_serial_port()
    if not port:
        sys.exit(1)
        
    print(f"Connecting to {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2) # Wait for reset
    except Exception as e:
        print(f"Error opening port: {e}")
        sys.exit(1)
        
    print("\nConnected!")
    print("Commands:")
    print("1: BORED (Snake)")
    print("2: THINKING")
    print("3: FINISH")
    print("4: REMOVE FIGURE")
    print("5: CLEAR")
    print("6: Set Brightness (0-15)")
    print("q: Quit")
    
    while True:
        cmd = input("\nSelect command: ").strip().lower()
        
        if cmd == 'q':
            break
        elif cmd == '1':
            ser.write(b"PATTERN BORED\n")
            print("Sent: PATTERN BORED")
        elif cmd == '2':
            ser.write(b"PATTERN THINKING\n")
            print("Sent: PATTERN THINKING")
        elif cmd == '3':
            ser.write(b"PATTERN FINISH\n")
            print("Sent: PATTERN FINISH")
        elif cmd == '4':
            ser.write(b"PATTERN REMOVE_FIGURE\n")
            print("Sent: PATTERN REMOVE_FIGURE")
        elif cmd == '5':
            ser.write(b"CLEAR\n")
            print("Sent: CLEAR")
        elif cmd == '6':
            try:
                val = int(input("Brightness (0-15): "))
                ser.write(f"BRIGHT {val}\n".encode())
                print(f"Sent: BRIGHT {val}")
            except:
                print("Invalid number")
        
        # Read response
        time.sleep(0.1)
        while ser.in_waiting:
            print(f"RX: {ser.readline().decode().strip()}")

    ser.close()

if __name__ == "__main__":
    main()
