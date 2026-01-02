#!/usr/bin/env python3
"""
Figurine Service - Main service for handling figurine interactions.
Orchestrates RFID Reader, LED Display, and Thermal Printer.
"""

import sys
import time
import logging
import random
import os
from typing import List
from pathlib import Path
import ollama

# Add rfid module to path
sys.path.append(str(Path(__file__).parent.parent / 'rfid'))
from rfid_reader import auto_detect_rfid, M5StackUHF

from display_controller import auto_detect_display, DisplayController
from printer import auto_detect_printer, ThermalPrinter
from receipt_template import ReceiptData, ReceiptRenderer

# Import figurine generation
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from generate_figurine_png import generate_figurine_png

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

def calculate_figurine_id(digits: List[int]) -> int:
    """
    Convert 6-digit base-6 input to decimal ID.
    Each digit can be 1-6, converting to 0-5 for base-6 calculation.
    Returns value from 1 to 46656 (6^6).
    """
    if len(digits) != 6:
        raise ValueError("Must provide exactly 6 digits")
    
    if not all(1 <= d <= 6 for d in digits):
        raise ValueError("All digits must be between 1 and 6")
    
    # Convert to base-6 (0-5)
    base6_digits = [d - 1 for d in digits]
    
    # Calculate decimal value
    result = 0
    for i, digit in enumerate(base6_digits):
        result += digit * (6 ** (5 - i))
    
    # Return 1-indexed (1 to 46656 instead of 0 to 46655)
    return result + 1

def tags_to_digits(tags: List[dict]) -> List[int]:
    """
    Convert 6 RFID tags to 6 digits (1-6).
    Uses the last byte of the EPC to generate a digit.
    """
    digits = []
    # Sort tags by EPC to ensure deterministic order for the same set of tags
    sorted_tags = sorted(tags, key=lambda x: x['epc'])
    
    for tag in sorted_tags:
        # Get last byte of EPC (hex string)
        epc = tag['epc']
        try:
            last_byte = int(epc[-2:], 16)
            digit = (last_byte % 6) + 1
            digits.append(digit)
        except:
            digits.append(random.randint(1, 6))
            
    return digits

def generate_content_with_ollama(figurine_id: int) -> dict:
    """
    Generate complete receipt content using Ollama.
    Returns dict with all fields for the receipt.
    """
    logger.info(f"[OLLAMA] Starting content generation for figurine {figurine_id}...")
    start_time = time.time()
    
    try:
        # Optimized prompt for faster generation
        prompt = f"""Erstelle einen kurzen, inspirierenden deutschen Text für Figurine #{figurine_id}.

Format (genau diese Struktur):
BESCHREIBUNG: [2-3 kurze Sätze über Persönlichkeit und Stärken]
FRAGE: [Eine tiefgründige Frage]
CHANCE: [Ein informeller Vorschlag]
ANGEBOT: [Ein offizielles Angebot/Programm]
INSPIRATION: [Buch, Film oder Zitat]
SCHRITT: [Konkreter nächster Schritt]

Kurz und prägnant!"""

        logger.info("[OLLAMA] Sending request to Ollama API...")
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.7,
                'num_predict': 150,
                'top_k': 20,
                'top_p': 0.8,
                'num_ctx': 512,
            }
        )
        
        elapsed = time.time() - start_time
        logger.info(f"[OLLAMA] Response received in {elapsed:.2f} seconds")
        
        content = response['message']['content'].strip()
        
        # Parse the response
        lines = content.split('\n')
        parsed = {
            'description': '',
            'question': '',
            'opportunity': '',
            'offer': '',
            'inspiration': '',
            'step': ''
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('BESCHREIBUNG:'):
                parsed['description'] = line.replace('BESCHREIBUNG:', '').strip()
            elif line.startswith('FRAGE:'):
                parsed['question'] = line.replace('FRAGE:', '').strip()
            elif line.startswith('CHANCE:'):
                parsed['opportunity'] = line.replace('CHANCE:', '').strip()
            elif line.startswith('ANGEBOT:'):
                parsed['offer'] = line.replace('ANGEBOT:', '').strip()
            elif line.startswith('INSPIRATION:'):
                parsed['inspiration'] = line.replace('INSPIRATION:', '').strip()
            elif line.startswith('SCHRITT:'):
                parsed['step'] = line.replace('SCHRITT:', '').strip()
        
        # Fill defaults
        if not parsed['description']: parsed['description'] = "Du bist einzigartig."
        if not parsed['question']: parsed['question'] = "Was ist dein Ziel?"
        if not parsed['opportunity']: parsed['opportunity'] = "Sprich mit Freunden."
        if not parsed['offer']: parsed['offer'] = "Besuche figurati.ch"
        if not parsed['inspiration']: parsed['inspiration'] = "Carpe Diem"
        if not parsed['step']: parsed['step'] = "Atme tief durch."
        
        return parsed
        
    except Exception as e:
        logger.error(f"[OLLAMA] Failed to generate content: {e}")
        return {
            'description': "Die Zukunft gehört denen, die an ihre Träume glauben.",
            'question': "Was ist dein nächster Schritt?",
            'opportunity': "Teile deine Vision.",
            'offer': "Beratung bei figurati.ch",
            'inspiration': "Der Alchemist",
            'step': "Sei dankbar."
        }

def generate_random_figurine(figurine_id: int) -> str:
    """Generate a random figurine image for the receipt."""
    assets_dir = Path(__file__).parent.parent / 'assets'
    assets_dir.mkdir(exist_ok=True)
    output_path = assets_dir / f'figurine_{figurine_id}.png'
    
    random.seed(figurine_id)
    generate_figurine_png(str(output_path), max_width=512, max_height=300)
    random.seed()
    
    return str(output_path)

def print_full_receipt(printer: ThermalPrinter, figurine_id: int):
    """Generate and print the full receipt."""
    logger.info(f"[RECEIPT] Generating receipt for #{figurine_id}")
    
    figurine_path = generate_random_figurine(figurine_id)
    content = generate_content_with_ollama(figurine_id)
    
    quotes = [
        ("Der Weg ist das Ziel.", "Konfuzius"),
        ("Sei du selbst die Veränderung.", "Mahatma Gandhi"),
        ("Courage, dear heart!", "C.S. Lewis"),
    ]
    quote, author = random.choice(quotes)
    
    receipt_data = ReceiptData(
        image_path=figurine_path,
        image_overlay_text="",
        figurine_number=str(figurine_id),
        total_count="46 656",
        body_paragraphs=[content['description']],
        mighty_question=content['question'],
        informal_opportunity=content['opportunity'],
        official_offer=content['offer'],
        inspiration=content['inspiration'],
        next_step=content['step'],
        qr_url="https://figurati.ch",
        footer_quote=quote,
        footer_quote_author=author,
        footer_thanks=["Vielen Dank!", "Figurati!"]
    )
    
    renderer = ReceiptRenderer()
    renderer.render_to_printer(printer.printer, receipt_data)

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
                    logger.debug(f"Scan saw {len(current_tags)} tags. Processing...")
                else:
                    logger.debug("Scan saw 0 tags.")

                # Accumulate unique tags
                for tag in current_tags:
                    epc = tag['epc']
                    if epc not in unique_tags:
                        unique_tags[epc] = tag
                        logger.info(f"New tag found: {epc} (RSSI: {tag['rssi']}) - Total: {len(unique_tags)}/6")
                    elif tag['rssi'] > unique_tags[epc]['rssi']:
                        # Update if we get a better signal
                        unique_tags[epc] = tag
                
                if len(unique_tags) < 6:
                    time.sleep(0.2)
            
            tags = list(unique_tags.values())[:6]
            
            # State: THINKING
            logger.info(f"State: THINKING (Found 6 tags: {[t['epc'] for t in tags]})")
            if display:
                display.set_pattern("THINKING")
            
            # Generate ID
            digits = tags_to_digits(tags)
            figurine_id = calculate_figurine_id(digits)
            logger.info(f"Generated Digits: {digits} -> ID: {figurine_id}")
            
            # Generate and Print
            print_full_receipt(printer, figurine_id)
            
            # State: FINISH
            logger.info("State: FINISH")
            if display:
                display.set_pattern("FINISH")
            
            # Wait before resetting
            time.sleep(10)
            
            # Loop repeats -> BORED
            
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    finally:
        if rfid: rfid.close()
        if display: display.close()

if __name__ == "__main__":
    main()
