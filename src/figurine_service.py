#!/usr/bin/env python3
"""
Figurine Service - Main service for handling figurine interactions.
Orchestrates RFID Reader, LED Display, and Thermal Printer.
"""

import sys
import time
import logging
import argparse
from temperature_service import log_temperatures

# Add rfid module to path
from rfid_controller import auto_detect_rfid
from display_controller import auto_detect_display
from printer_controller import auto_detect_printer, PrinterController

# Import refactored modules
from slip_printing import create_full_receipt
import logging
import data_service

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

data_service = data_service.DataService()

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
        printer = PrinterController(connection_type='dummy')

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
            
            # Scan for tags with maximum reliability using multi-polling
            logger.info("Scanning for 6 tags (multi-polling mode - optimized)...")
            
            # Use multi-polling scanning method for efficient 100% detection
            # Multi-polling (0x27 command) is more efficient at reading multiple tags
            # Continues until all 6 tags found or 120 second timeout
            tags_list = rfid.read_tags_multi_polling(target_tags=6, max_duration=120)
            
            # We have 6 tags!
            logger.info("State: THINKING (Processing tags)")
            if display:
                display.set_brightness(6)
                display.set_pattern("THINKING")
            
            answers = data_service.find_answer_by_tags([tag['epc'] for tag in tags_list])
            
            logger.info("Tag Answers:")
            if answers:
                for ans in answers:
                    answer_id = ans.get('Antwort_ID', 'Unknown')
                    question_id = ans.get('Frage_ID', 'Unknown')
                    logger.info(f"  - {question_id}: {answer_id}")
            else:
                logger.info("  No matching answer found for these tags.")
            
            # Calculate unique figurine ID based on answer set
            figurine_id = data_service.calculate_answer_set_id(answers)
            
            if figurine_id is None:
                logger.error("Failed to calculate figurine ID, using fallback")
                # Fallback to random ID if calculation fails
                import random
                figurine_id = random.randint(1, 27000)
            
            logger.info(f"Calculated Figurine ID: {figurine_id}")
            total_possible = data_service.get_total_unique_ids()
            logger.info(f"Total possible unique IDs: {total_possible}")
            
            # Generate and Print Receipt
            logger.info("State: PRINTING")
            if display:
                display.set_pattern("PRINTING")
            
            try:
                if args.no_print:
                    logger.info("[NO-PRINT MODE] Skipping receipt printing")
                    logger.info(f"Would have printed receipt for Figurine ID: {figurine_id}")
                else:
                    create_full_receipt(printer.printer, figurine_id, answers=answers, data_service=data_service, model_name=OLLAMA_MODEL)
                    logger.info("Receipt printed successfully.")
                    
                    log_temperatures()                

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
