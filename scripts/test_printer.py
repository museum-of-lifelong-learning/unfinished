import sys
import os

# Add src to path so we can import printer
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from printer import ThermalPrinter

def main():
    print("Testing Thermal Printer Setup...")
    
    # Try to connect to a real printer if possible, otherwise dummy
    # You can change this to 'usb', 'serial', or 'network' to test real hardware
    connection_type = 'usb' 
    
    print(f"Initializing printer with connection_type='{connection_type}'")
    printer = ThermalPrinter(connection_type=connection_type)
    
    print("Printing test slip...")
    printer.print_test_slip()
    
    # Test Image Printing
    image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fig1.jpeg')
    if os.path.exists(image_path):
        print(f"Printing test image: {image_path}")
        printer.print_image(image_path)
    else:
        print(f"Test image not found at {image_path}")

    print("Test complete.")

if __name__ == "__main__":
    main()
