"""
Slip Printing Module
Handles the physical printing of receipts using pre-generated data.
"""

import logging
import os
import textwrap
from typing import Dict, Any
from PIL import Image

logger = logging.getLogger(__name__)

# Paper width for TM-T88V/TM-T70II profile (80mm paper, 512px at 180dpi)
PAPER_WIDTH_PX = 512
CHAR_WIDTH = 42  # Approximate characters per line for standard font

def print_scaled_image(image_path: str, printer) -> Image.Image:
    """
    Load and resize image to fit paper width.
    Maintains aspect ratio without cropping height.
    """
    img = Image.open(image_path).convert('RGB')
    
    # Resize to paper width while maintaining aspect ratio
    if img.width != PAPER_WIDTH_PX:
        ratio = PAPER_WIDTH_PX / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((PAPER_WIDTH_PX, new_height), Image.Resampling.LANCZOS)
    
    printer.image(img)
    
def print_labeled_section(printer, label: str, text: str):
    """Print a section with a bold label followed by normal text."""
    printer.set(align='left', bold=True)
    printer.text(f"{label} ")
    printer.set(bold=False)
    
    # First line includes label, subsequent lines are full width
    words = text.split()
    first_line = []
    remaining_words = []
    first_line_width = CHAR_WIDTH - len(label) - 1
    
    # Build first line
    current_length = 0
    for i, word in enumerate(words):
        test_length = current_length + len(word) + (1 if current_length > 0 else 0)
        if test_length <= first_line_width:
            first_line.append(word)
            current_length = test_length
        else:
            remaining_words = words[i:]
            break
    
    # Print first line (already on same line as label)
    printer.textln(' '.join(first_line))
    
    # Print remaining lines with full width
    if remaining_words:
        remaining_text = ' '.join(remaining_words)
        wrapped = textwrap.fill(remaining_text, width=CHAR_WIDTH)
        printer.textln(wrapped)


def create_full_receipt(printer, slip_data: Dict[str, Any]):
    """
    Print the full receipt using pre-generated data.
    
    Args:
        printer: Printer instance to print to
        slip_data: Dictionary containing all generated data from slip_data_generation
    """
    figurine_id = slip_data.get('figurine_id', 0)
    logger.info(f"[PRINT] Printing receipt for #{figurine_id}")
    
    figurine_path = slip_data.get('figurine_path')
    content = slip_data.get('content', {})
    resources = slip_data.get('resources', {})
    total_unique_ids = slip_data.get('total_unique_ids', 27000)
    qr_url = slip_data.get('qr_url', f"https://figurati.ch/${figurine_id}")
    
    # === HEADER: Image ===
    if figurine_path and os.path.exists(figurine_path):
        print_scaled_image(figurine_path, printer)
    printer.ln()
    
    # Figurine number
    printer.set(align='center')
    printer.textln(f"Lerncharakter {figurine_id} / {total_unique_ids}")
    printer.ln()
    
    
    # === BODY ===
    printer.set(align='left', bold=False)
    
    # Body paragraphs - two personalized paragraphs from Ollama
    if content.get('paragraph1'):
        wrapped = textwrap.fill(content['paragraph1'], width=CHAR_WIDTH)
        printer.textln(wrapped)
        printer.ln()
    
    if content.get('paragraph2'):
        wrapped = textwrap.fill(content['paragraph2'], width=CHAR_WIDTH)
        printer.textln(wrapped)
        printer.ln()
    
    # Labeled sections (bold labels)
    categories = {
        'tool': "Tools & Inspiration",
        'location': "Anlaufstellen & Angebote",
        'program': "Programm-Empfehlung"
    }
    
    for key, label in categories.items():
        resource_text = resources.get(key, f'No {label} available')
        print_labeled_section(printer, f"{label}:", resource_text)    
        printer.ln()
    
    
    # === QR CODE ===
    printer.set(align='center')
    printer.qr(qr_url, size=6)
    printer.ln()
    
    
    # === FOOTER ===
    printer.set(align='center')
    
    printer.textln("Bleib unfertig.")
    printer.textln("Vielen Dank für deinen Besuch.")    
    printer.ln()
    
    printer.set(align='center', bold=True)
    printer.textln("Unfinished")
    printer.textln("The Museum of Lifelong Learning")
    printer.ln()
    
    printer.cut()
