#!/usr/bin/env python3
"""
Test script for the receipt printing system.
Prints a full receipt using slip_printing module.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from printer_controller import PrinterController
from slip_printing import ReceiptRenderer
from PIL import Image
import textwrap


def main():
    print("=== Receipt Test ===")
    
    # Use the figurine shapes image
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    image_path = os.path.join(assets_dir, 'image.png')
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        return
    
    print(f"Using image: {image_path}")
    
    # Initialize printer (USB for real hardware, 'dummy' for testing)
    connection_type = 'usb'
    print(f"Initializing printer with connection_type='{connection_type}'")
    printer = PrinterController(connection_type=connection_type)
    
    # Initialize renderer
    renderer = ReceiptRenderer()
    
    # Print receipt manually
    print("Rendering receipt...")
    
    # Load and print image
    img = renderer.load_and_scale_image(image_path)
    printer.printer.image(img)
    
    printer.printer.set(align='center')
    printer.printer.ln()
    
    # Figurine number
    printer.printer.textln("Figurina Nr. 5678 / 27 000")
    printer.printer.ln()
    
    # Body
    printer.printer.set(align='left')
    for para in [
        "Wenn andere schon am Verzweifeln sind, blühst du erst richtig auf. In jeder Erfahrung siehst du eine Chance und schreckst nicht davor zurück, dich Neuem zu stellen und in unbekanntes Gelände vorzudringen.",
        "Das einzige, was dir schlaflose Nächte bereitet, ist die Fülle an Möglichkeiten. Wie bloss soll man da die Nadel im Heuhaufen finden?"
    ]:
        wrapped = textwrap.fill(para, width=42)
        printer.printer.textln(wrapped)
        printer.printer.ln()
    
    # Labeled sections
    renderer._print_labeled_section(printer.printer, "Mächtige Frage:", "Wie treffe ich die richtige Entscheidung?")
    renderer._print_labeled_section(printer.printer, "Informal Opportunity:", "Wer kennt dich am besten? Sprich mit dieser Person.")
    renderer._print_labeled_section(printer.printer, "Offizielles Angebot:", "viamia, berufliche Standortbestimmung für Menschen ab 40.")
    renderer._print_labeled_section(printer.printer, "Inspiration:", "Beginners, Tom Vanderbilt (Buch)")
    renderer._print_labeled_section(printer.printer, "Nächster Schritt:", "Peer-Workshop für Aufsteiger*innen")
    
    printer.printer.ln()
    
    # QR Code
    printer.printer.set(align='center')
    printer.printer.qr("https://figurati.ch", size=6)
    printer.printer.ln()
    
    # Footer
    printer.printer.textln("«Courage, dear heart!»")
    printer.printer.textln("C.S. Lewis")
    printer.printer.ln()
    
    for line in ["Vielen Dank!", "Figurati!"]:
        printer.printer.textln(line)
    
    printer.printer.cut()
    
    print("Done!")


if __name__ == "__main__":
    main()
