#!/usr/bin/env python3
"""
Manual Flow Test
Simulates the service flow but allows manual injection of "tags" to test the logic
without needing physical RFID tags.
"""

import sys
import time
import logging
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Mock modules
from printer import ThermalPrinter
from display_controller import DisplayController
from figurine_service import calculate_figurine_id, print_full_receipt

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def mock_tags():
    """Generate 6 random mock tags"""
    tags = []
    for i in range(6):
        # Generate random hex EPC
        epc = "".join([random.choice("0123456789ABCDEF") for _ in range(24)])
        tags.append({'epc': epc, 'rssi': -60})
    return tags

def main():
    print("=== Manual Flow Test (Simulation) ===")
    print("This script simulates the service flow with MOCK RFID data.")
    print("It WILL use the real Printer and Display if connected.")
    print("=====================================\n")

    # 1. Connect to real output devices
    print("Connecting to Printer...")
    try:
        printer = ThermalPrinter(connection_type='usb', idVendor=0x04b8, idProduct=0x0202)
        if hasattr(printer, 'printer') and isinstance(printer.printer, type(None)):
             printer = ThermalPrinter(connection_type='dummy')
    except:
        printer = ThermalPrinter(connection_type='dummy')
        
    print("Connecting to Display...")
    # We'll try to find the display port manually or just skip
    import glob
    display = None
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    for port in ports:
        try:
            d = DisplayController(port)
            if d.set_pattern("BORED"):
                display = d
                print(f"✓ Display found on {port}")
                break
            d.close()
        except:
            pass
            
    if not display:
        print("! Display not found (simulating)")

    # 2. Loop
    while True:
        print("\n--- STATE: BORED ---")
        if display: display.set_pattern("BORED")
        
        input("\nPress ENTER to simulate scanning 6 tags...")
        
        print("\n--- STATE: THINKING ---")
        if display: display.set_pattern("THINKING")
        
        tags = mock_tags()
        print(f"Scanned 6 mock tags: {[t['epc'][-4:] for t in tags]}")
        
        # Logic from service
        from figurine_service import tags_to_digits
        digits = tags_to_digits(tags)
        figurine_id = calculate_figurine_id(digits)
        print(f"Calculated ID: {figurine_id}")
        
        print("Generating content and printing...")
        print_full_receipt(printer, figurine_id)
        
        print("\n--- STATE: FINISH ---")
        if display: display.set_pattern("FINISH")
        
        print("Waiting 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    main()
