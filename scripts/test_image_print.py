#!/usr/bin/env python3
"""
Test script to print only an image (without text overlay) to the thermal printer.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from printer_controller import PrinterController
from PIL import Image


def main():
    print("=== Image-Only Print Test ===")
    
    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default to generated PNG or fallback to image.png
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        generated_png = os.path.join(assets_dir, 'figurine_generated.png')
        default_png = os.path.join(assets_dir, 'image.png')
        
        if os.path.exists(generated_png):
            image_path = generated_png
        else:
            image_path = default_png
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        print("Usage: python test_image_print.py [path/to/image.png]")
        return
    
    print(f"Using image: {image_path}")
    
    # Initialize printer
    connection_type = 'usb'
    print(f"Initializing printer with connection_type='{connection_type}'")
    printer = PrinterController(connection_type=connection_type)
    
    # Load and resize image to fit paper
    img = Image.open(image_path).convert('RGB')
    paper_width = 512
    
    # Resize to paper width
    if img.width != paper_width:
        ratio = paper_width / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((paper_width, new_height), Image.Resampling.LANCZOS)
    
    # Crop to 50% height (center crop)
    # target_height = img.height // 2
    # top = (img.height - target_height) // 2
    # bottom = top + target_height
    # img = img.crop((0, top, paper_width, bottom))
    
    print(f"Image size after processing: {img.width}x{img.height}px")
    
    # Print
    print("Printing image...")
    printer.printer.image(img)
    printer.printer.cut()
    
    print("Done!")


if __name__ == "__main__":
    main()
