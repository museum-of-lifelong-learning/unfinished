#!/usr/bin/env python3
"""
Figurine Service - Main service for handling figurine interactions.
Orchestrates RFID Reader, LED Display, and Thermal Printer.
"""

import sys
import time
import logging
import argparse
import subprocess
import socket

from temperature_service import log_temperatures
from rfid_controller import auto_detect_rfid
from display_controller import auto_detect_display
from printer_controller import auto_detect_printer, PrinterController


from slip_data_generation import generate_slip_data
from slip_printing import create_full_receipt
from supabase_upload import upload_slip_data, build_qr_url
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

# Import Gemini configuration
from content_generation import GEMINI_MODEL

data_service = data_service.DataService()

def check_internet_connection():
    """Check if internet connection is available by trying to reach Google DNS."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def get_wifi_ssid():
    """Get the current WiFi SSID if connected."""
    try:
        # Try iwgetid first (most common on Linux)
        result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        # Fallback: try nmcli
        result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('yes:'):
                    return line.split(':', 1)[1]
        
        return "Not connected"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "Unknown"

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
    
    # Display
    display = auto_detect_display()
    if display:
        logger.info("✓ Display detected")
    else:
        logger.error("✗ Display NOT detected")    
    
    # RFID
    rfid = auto_detect_rfid()
    if rfid:
        logger.info("✓ RFID Reader detected")
    else:
        logger.error("✗ RFID Reader NOT detected")
        

    # Printer
    printer = auto_detect_printer()
    if printer:
        logger.info("✓ Printer detected")
    else:
        logger.info("! Printer not detected, using Dummy")
        printer = PrinterController(connection_type='dummy')

    # Check system status
    logger.info("Checking system status...")
    internet_status = "✓ Online" if check_internet_connection() else "✗ Offline"
    wifi_ssid = get_wifi_ssid()
    
    # Print status to console/log
    rfid_status = '✓ Online' if rfid else '✗ Offline'
    display_status = '✓ Online' if display else '✗ Offline'
    printer_status = '✓ Online' if not isinstance(printer.printer, type(None)) else '⚠ Dummy Mode'

    status_msg = f"""
╔════════════════════════════════════════╗
║        FIGURINE SERVICE STATUS         ║
╠════════════════════════════════════════╣
║ RFID Reader: {rfid_status:<25} ║
║ Printer:     {printer_status:<25} ║
║ Display:     {display_status:<25} ║
║ Internet:    {internet_status:<25} ║
║ WiFi:        {wifi_ssid:<25} ║
║ AI Model:    {GEMINI_MODEL:<25} ║
╚════════════════════════════════════════╝
"""
    print(status_msg)
    logger.info("Service status check complete")
    
    if not rfid:
        logger.error("Cannot proceed without RFID reader. Exiting.")
        sys.exit(1)

    # 2. Main Loop
    try:
        while True:
            # State: BORED / SCANNING
            logger.info("State: BORED (Scanning for 6 tags)")
            if display:
                display.set_brightness(2)
                display.set_pattern("BORED")
            
            # Scan for tags with maximum reliability using multi-polling
            # logger.info("Scanning for 6 tags (multi-polling mode - optimized)...")
            
            # Use multi-polling scanning method for efficient 100% detection
            # Multi-polling (0x27 command) is more efficient at reading multiple tags
            # Continues until all 6 tags found or 120 second timeout
            
            while not rfid.has_tags_present():
                time.sleep(0.5)
                
            try:
                tags_list = rfid.read_tags(target_tags=6, max_attempts=240, use_anti_collision=True)
            except Exception as e:
                logger.error(f"Error during tag reading: {e}")
                continue
            
            # We have 6 tags!
            logger.info("State: THINKING (Processing tags)")
            if display:
                display.set_brightness(6)
                display.set_pattern("THINKING")
            
            answers = data_service.find_answer_by_tags([tag['epc'] for tag in tags_list])
            
            # sort the answers by Frage_ID to have consistent order
            answers.sort(key=lambda x: x.get('Frage_ID', 0), reverse=True)
            
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
                    # Generate all slip data first
                    logger.info("Generating slip data...")
                    slip_data = generate_slip_data(
                        figurine_id=figurine_id,
                        answers=answers,
                        data_service=data_service,
                        model_name=GEMINI_MODEL
                    )
                    
                    # Check if we're in offline mode (slip_data generation handles this)
                    if slip_data.get('offline_mode', False):
                        logger.info("[OFFLINE MODE] Using fallback data from CSV - skipping upload")
                        logger.info(f"[OFFLINE MODE] Using data_id from CSV: {slip_data.get('data_id')}")
                    else:
                        # Online mode: Upload to Supabase and get data_id
                        logger.info("Uploading slip data to Supabase...")
                        data_id = upload_slip_data(slip_data)
                        
                        if data_id:
                            # Update QR URL with actual data_id
                            slip_data['qr_url'] = build_qr_url(data_id, figurine_id)
                            slip_data['data_id'] = data_id
                            logger.info(f"Upload successful. data_id: {data_id}")
                        else:
                            logger.warning("Upload failed, using fallback QR URL")
                            # Fallback URL without data_id
                            slip_data['qr_url'] = f"https://museum-of-lifelong-learning.github.io/unfinished/?figure_id={figurine_id}"
                    
                    # Print the receipt with generated data
                    logger.info("Printing slip...")
                    create_full_receipt(printer.printer, slip_data)
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
