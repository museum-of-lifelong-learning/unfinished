#!/usr/bin/env python3
"""
Figurine Service - Main service for handling figurine interactions.
Orchestrates RFID Reader, LED Display, and Thermal Printer.
"""

import sys
import time
import logging
import os
import argparse
from pathlib import Path
from receipt_template import ReceiptData, ReceiptRenderer

# Add rfid module to path
from rfid_reader import auto_detect_rfid, M5StackUHF

from display_controller import auto_detect_display, DisplayController
from printer import auto_detect_printer, ThermalPrinter

# Import refactored modules
from figurine_id import calculate_figurine_id, tags_to_digits
from slip_printing import create_full_receipt
import logging
import data_handler

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

data_handler = data_handler.FigurineDataHandler()

def get_temperature(zone_path: str, name: str) -> float:
    """Read temperature from a thermal zone."""
    try:
        with open(zone_path, "r") as f:
            raw = f.read().strip()
        value = float(raw)
        temp_c = value / 1000.0 if value > 200 else value
        if -30.0 < temp_c < 120.0:
            return temp_c
        logger.debug(f"Discarding out-of-range {name} temp from {zone_path}: {temp_c}C (raw={raw})")
    except Exception as e:
        logger.debug(f"Could not read {name} temperature from {zone_path}: {e}")
    return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Figurine Service')
    parser.add_argument('--no-print', action='store_true', 
                        help='Skip actual printing to save paper (development mode)')
    args = parser.parse_args()
    
    logger.info("=== Figurine Service Starting ===")
    if args.no_print:
        logger.info("*** NO-PRINT MODE: Printing disabled to save paper ***")
    
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
    
    if printer:
        if not args.no_print:
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
                display.set_brightness(3)
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
                
                time.sleep(0.1)
            
            # We have 6 tags!
            logger.info("State: THINKING (Processing tags)")
            if display:
                display.set_brightness(6)
                display.set_pattern("THINKING")
            
            tags_list = list(unique_tags.values())
            
            answers = data_handler.find_answer_by_tags([tag['epc'] for tag in tags_list])
            
            logger.info("Tag Answers:")
            if answers:
                for ans in answers:
                    logger.info(f"  - {ans}")
            else:
                logger.info("  No matching answer found for these tags.")
            
            digits = tags_to_digits(tags_list)
            figurine_id = calculate_figurine_id(digits)
            
            logger.info(f"Tags converted to digits: {digits}")
            logger.info(f"Calculated Figurine ID: {figurine_id}")
            
            # Generate and Print Receipt
            logger.info("State: PRINTING")
            if display:
                display.set_pattern("PRINTING")
            
            receipt_data = create_full_receipt(figurine_id, model_name=OLLAMA_MODEL)
            
            try:
                if args.no_print:
                    logger.info("[NO-PRINT MODE] Skipping receipt printing")
                    logger.info(f"Would have printed receipt for Figurine ID: {figurine_id}")
                else:
                    renderer = ReceiptRenderer()
                    renderer.render_to_printer(printer.printer, receipt_data)

                    logger.info("Receipt printed successfully.")
                
                # Log temperatures
                cpu_temp = get_temperature("/sys/class/thermal/thermal_zone2/temp", "CPU")
                wifi_temp = get_temperature("/sys/class/thermal/thermal_zone1/temp", "WiFi")
                
                if cpu_temp is not None:
                    logger.info(f"CPU Temperature: {cpu_temp:.1f}°C")
                else:
                    logger.info("CPU Temperature: unavailable")
                    
                if wifi_temp is not None:
                    logger.info(f"WiFi Temperature: {wifi_temp:.1f}°C")
                else:
                    logger.info("WiFi Temperature: unavailable")
            except Exception as e:
                logger.error(f"Failed to print receipt: {e}")
                if display:
                    display.set_pattern("ERROR")
            
            # Wait before next scan
            logger.info("State: FINISH (Waiting 20s)")
            if display:
                display.set_speed(8)
                display.set_pattern("FINISH")
            time.sleep(20)
            
            # Ensure tags are removed before restarting cycle
            logger.info("Checking for remaining tags before restarting cycle...")
            if rfid.has_tags_present():
                if display:
                    display.set_pattern("REMOVE_FIGURE")
                logger.info("Tags detected after finish; waiting for removal...")
                time.sleep(0.5)
                
            while rfid.has_tags_present():
                logger.info("Tags detected after finish; waiting for removal...")
                time.sleep(1)
            
            logger.info("No tags present; resuming next cycle.")
            if display:
                display.clear()
                display.set_brightness(5)
                display.set_speed(5)
                time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.exception(f"Service crashed: {e}")
    finally:
        if display:
            display.clear()

if __name__ == "__main__":
    main()
