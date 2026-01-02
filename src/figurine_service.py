#!/usr/bin/env python3
"""
Figurine Service - Main service for handling figurine interactions.
Orchestrates RFID Reader, LED Display, and Thermal Printer.
"""

import sys
import time
import logging
import os
from pathlib import Path

# Add rfid module to path
from rfid_reader import auto_detect_rfid, M5StackUHF

from display_controller import auto_detect_display, DisplayController
from printer import auto_detect_printer, ThermalPrinter

# Import refactored modules
from figurine_id import calculate_figurine_id, tags_to_digits
from slip_printing import print_full_receipt

# Setup logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
if root_logger.hasHandlers():
    root_logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler('/tmp/figurine_service.log')
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Console handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)

OLLAMA_MODEL = 'qwen2.5:3b'

def get_cpu_temperature() -> float:
    """Read the CPU temperature from the system."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read().strip()) / 1000.0
        return temp
    except Exception as e:
        logger.warning(f"Could not read CPU temperature: {e}")
        return 0.0

def main():
    logger.info("=== Figurine Service Starting ===")
    
    # 1. Auto-detect devices
    logger.info("Detecting devices...")
    
    # RFID
    rfid = auto_detect_rfid()
    if rfid:
        logger.info("✓ RFID Reader detected")
    else:
        logger.error("✗ RFID Reader NOT detected")
        
    # Display
    display = auto_detect_display()
    if display:
        logger.info("✓ Display detected")
    else:
        logger.error("✗ Display NOT detected")
        
    # Printer
    printer = auto_detect_printer()
    if printer:
        logger.info("✓ Printer detected")
    else:
        logger.info("! Printer not detected, using Dummy")
        printer = ThermalPrinter(connection_type='dummy')

    # Print status to console/log
    rfid_status = 'CONNECTED' if rfid else 'MISSING'
    display_status = 'CONNECTED' if display else 'MISSING'
    printer_status = 'CONNECTED' if not isinstance(printer.printer, type(None)) else 'DUMMY'

    status_msg = f"""
=== SERVICE STATUS ===
RFID Reader: {rfid_status}
Display:     {display_status}
Printer:     {printer_status}
AI Model:    {OLLAMA_MODEL}
======================
"""
    logger.info(status_msg)
    print(status_msg)
    
    if printer:
        printer.print_test_slip({
            "RFID Reader": rfid_status,
            "Display": display_status,
            "Printer": printer_status,
            "AI Model": OLLAMA_MODEL
        })
        logger.info("Test slip printed.")

    if not rfid:
        logger.error("Cannot proceed without RFID reader. Exiting.")
        sys.exit(1)

    # 2. Main Loop
    try:
        while True:
            # State: BORED / SCANNING
            logger.info("State: BORED (Scanning for 6 tags)")
            if display:
                display.set_pattern("BORED")
            
            # Scan for tags
            unique_tags = {}
            logger.info("Scanning... (Need 6 unique tags)")
            
            while len(unique_tags) < 6:
                # Read a batch of tags
                current_tags = rfid.read_tags(target_tags=6, max_attempts=5)
                
                if current_tags:
                    for tag in current_tags:
                        unique_tags[tag['epc']] = tag
                    
                    logger.info(f"Found {len(unique_tags)} unique tags so far...")
                    
                    # Update display with progress
                    if display:
                        display.set_progress(len(unique_tags), 6)
                
                time.sleep(0.1)
            
            # We have 6 tags!
            logger.info("State: THINKING (Processing tags)")
            if display:
                display.set_pattern("THINKING")
            
            tags_list = list(unique_tags.values())
            digits = tags_to_digits(tags_list)
            figurine_id = calculate_figurine_id(digits)
            
            logger.info(f"Tags converted to digits: {digits}")
            logger.info(f"Calculated Figurine ID: {figurine_id}")
            
            # Generate and Print Receipt
            logger.info("State: PRINTING")
            if display:
                display.set_pattern("PRINTING")
            
            try:
                print_full_receipt(printer, figurine_id, model_name=OLLAMA_MODEL)
                logger.info("Receipt printed successfully.")
                
                # Log temperature
                cpu_temp = get_cpu_temperature()
                logger.info(f"CPU Temperature: {cpu_temp:.1f}°C")
            except Exception as e:
                logger.error(f"Failed to print receipt: {e}")
                if display:
                    display.set_pattern("ERROR")
            
            # Wait before next scan
            logger.info("State: FINISHED (Waiting 10s)")
            if display:
                display.set_pattern("FINISHED")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.exception(f"Service crashed: {e}")
    finally:
        if display:
            display.clear()

if __name__ == "__main__":
    main()
