from escpos.printer import Usb, Serial, Network, Dummy
from PIL import Image
import time

class ThermalPrinter:
    def __init__(self, connection_type='dummy', **kwargs):
        """
        Initialize the printer.
        connection_type: 'usb', 'serial', 'network', or 'dummy'
        kwargs: arguments for the specific connection type
            - usb: idVendor, idProduct
            - serial: dev, baudrate
            - network: host, port
        """
        self.printer = None
        self.connection_type = connection_type
        
        try:
            if connection_type == 'usb':
                # Epson TM-T70II: idVendor=0x04b8, idProduct=0x0202
                # Using TM-T88V profile (similar thermal printer)
                self.printer = Usb(
                    kwargs.get('idVendor', 0x04b8), 
                    kwargs.get('idProduct', 0x0202),
                    profile='TM-T88V'
                )
            elif connection_type == 'serial':
                self.printer = Serial(kwargs.get('dev', '/dev/ttyUSB0'), 
                                      baudrate=kwargs.get('baudrate', 9600))
            elif connection_type == 'network':
                self.printer = Network(kwargs.get('host', '192.168.1.100'), 
                                       port=kwargs.get('port', 9100))
            else:
                self.printer = Dummy()
                print("Initialized Dummy Printer (Output to stdout)")

        except Exception as e:
            print(f"Failed to connect to printer: {e}")
            print("Falling back to Dummy printer")
            self.printer = Dummy()

    def print_test_slip(self):
        """
        Prints a test slip to verify functionality.
        """
        if not self.printer:
            print("Printer not initialized.")
            return

        print("Printing test slip...")
        
        self.printer.text("--------------------------------\n")
        self.printer.text("      FIGURINE INTERACTION      \n")
        self.printer.text("--------------------------------\n")
        self.printer.text("\n")
        self.printer.text("Test Slip\n")
        self.printer.text(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.printer.text("\n")
        self.printer.text("Items Detected: 6\n")
        self.printer.text("Status: OK\n")
        self.printer.text("\n")
        self.printer.text("--------------------------------\n")
        self.printer.cut()
        
        if isinstance(self.printer, Dummy):
            print(self.printer.output.decode('utf-8'))

    def print_text(self, text: str):
        if not self.printer:
            return
        self.printer.text(text)
        self.printer.cut()
        if isinstance(self.printer, Dummy):
            print(self.printer.output.decode('utf-8'))

    def print_image(self, image_path: str):
        """
        Prints an image.
        """
        if not self.printer:
            return
        
        print(f"Printing image: {image_path}")
        try:
            # Open and resize image to fit standard thermal paper (approx 512px width)
            img = Image.open(image_path)
            max_width = 512
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            self.printer.image(img)
            self.printer.cut()
        except Exception as e:
            print(f"Failed to print image: {e}")

        if isinstance(self.printer, Dummy):
            print(f"[Image Content from {image_path}]")
            # Dummy printer output might not show image binary data well, but we can see the cut command
            print(self.printer.output.decode('utf-8', errors='ignore'))

if __name__ == "__main__":
    # Test with Dummy printer
    printer = ThermalPrinter(connection_type='dummy')
    printer.print_test_slip()
