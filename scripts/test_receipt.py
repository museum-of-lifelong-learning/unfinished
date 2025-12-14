#!/usr/bin/env python3
"""
Test script for the receipt template system.
Prints a full receipt with image overlay, body text, QR code, and footer.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from printer import ThermalPrinter
from receipt_template import ReceiptData, ReceiptRenderer


def main():
    print("=== Receipt Template Test ===")
    
    # Use the figurine shapes image
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    image_path = os.path.join(assets_dir, 'image.png')
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        return
    
    print(f"Using image: {image_path}")
    
    # Create receipt data based on the example template
    data = ReceiptData(
        image_path=image_path,
        image_overlay_text="Die Antwort ist schon da.",
        figurine_number="5678",
        total_count="27 000",
        body_paragraphs=[
            "Wenn andere schon am Verzweifeln sind, blühst du erst richtig auf. In jeder Erfahrung siehst du eine Chance und schreckst nicht davor zurück, dich Neuem zu stellen und in unbekanntes Gelände vorzudringen. Allerdings muss da schon etwas für dich rausschauen. Ein bisschen Spass, mindestens. Das ist dein Antrieb – nutze ihn weise und inspiriere auch andere damit.",
            "Das einzige, was dir schlaflose Nächte bereitet, ist die Fülle an Möglichkeiten. Wie bloss soll man da die Nadel im Heuhaufen finden? Die gute Nachricht: Auch wenn sich das manchmal sehr einsam anfühlt – du bist in bester Gesellschaft. Das hier ist für dich."
        ],
        mighty_question="Wie treffe ich die richtige Entscheidung?",
        informal_opportunity="Wer kennt dich am besten? Sprich mit dieser Person. Auch wenn du nicht immer hören willst, was sie zu sagen hat. Aber oft sind genau sie unser wichtigster Spiegel.",
        official_offer="viamia, berufliche Standortbestimmung für Menschen ab 40. Ein Angebot des Bundes.",
        inspiration="Beginners, Tom Vanderbilt (Buch)",
        next_step="Peer-Workshop für Aufsteiger*innen",
        qr_url="https://youtu.be/dQw4w9WgXcQ?si=NYSaJdGjv3GCtNGD&t=9",
        footer_quote="Courage, dear heart!",
        footer_quote_author="C.S. Lewis",
        footer_thanks=[
            "Vielen Dank, dass du",
            "den Status quo hinterfragst.",
            "Figurati!"
        ]
    )
    
    # Initialize printer (USB for real hardware, 'dummy' for testing)
    connection_type = 'usb'
    print(f"Initializing printer with connection_type='{connection_type}'")
    printer = ThermalPrinter(connection_type=connection_type)
    
    # Initialize renderer
    renderer = ReceiptRenderer()
    
    # Print!
    print("Rendering receipt...")
    renderer.render_to_printer(printer.printer, data)
    
    print("Done!")


if __name__ == "__main__":
    main()
