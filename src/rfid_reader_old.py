import time
import random
from typing import List

class RFIDReader:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        print(f"Initializing RFID Reader on {self.port} at {self.baudrate} baud...")

    def connect(self):
        """
        Simulate connecting to the RFID reader.
        """
        print("Connecting to RFID Reader...")
        time.sleep(1)
        self.connected = True
        print("RFID Reader connected (SIMULATION).")

    def read_tags(self, timeout: int = 5) -> List[str]:
        """
        Simulate reading RFID tags.
        Returns a list of tag IDs.
        """
        if not self.connected:
            print("Error: Reader not connected.")
            return []

        print(f"Scanning for tags (timeout={timeout}s)...")
        time.sleep(2) # Simulate scanning time
        
        # Simulate finding 6 tags
        # In a real scenario, this would read from the serial port
        mock_tags = [
            "E200001D34120131198056B9",
            "E200001D34120131198056BA",
            "E200001D34120131198056BB",
            "E200001D34120131198056BC",
            "E200001D34120131198056BD",
            "E200001D34120131198056BE"
        ]
        
        # Randomly return fewer tags to simulate partial reads sometimes
        if random.random() < 0.1:
             return mock_tags[:4]
        
        return mock_tags

    def disconnect(self):
        self.connected = False
        print("RFID Reader disconnected.")

if __name__ == "__main__":
    reader = RFIDReader()
    reader.connect()
    tags = reader.read_tags()
    print(f"Tags found: {tags}")
    reader.disconnect()
