import serial
import time
import glob
import logging

logger = logging.getLogger(__name__)

class DisplayController:
    def __init__(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2) # Wait for ESP32 reset
        self.clear_buffer()

    def clear_buffer(self):
        self.ser.reset_input_buffer()

    def send_command(self, cmd):
        if not self.ser.is_open:
            return False
        try:
            full_cmd = f"{cmd}\n".encode('utf-8')
            self.ser.write(full_cmd)
            return True
        except Exception as e:
            logger.error(f"Display send error: {e}")
            return False

    def read_response(self, timeout=1.0):
        if not self.ser.is_open:
            return None
        
        start = time.time()
        response = ""
        while time.time() - start < timeout:
            if self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        return line
                except Exception:
                    pass
            time.sleep(0.01)
        return None

    def set_pattern(self, pattern):
        """
        Set display pattern: SNAKE, THINKING, FINISH, PRINTING, ERROR, REMOVE_FIGURE
        """
        # Allow more patterns as per service usage
        if pattern not in ["SNAKE", "THINKING", "FINISH", "PRINTING", "ERROR", "REMOVE_FIGURE", "TEXT"]:
            logger.warning(f"Unknown pattern requested: {pattern}")
        
        self.send_command(f"PATTERN {pattern}")
        resp = self.read_response()
        return resp == "OK"
    
    def set_text(self, text, direction=None):
        """
        Display custom text with optional scrolling direction.
        
        Args:
            text (str): Text to display (max 64 characters)
            direction (str): Optional scrolling direction: 'LEFT', 'RIGHT', or None for centered
        
        Returns:
            bool: True if command was acknowledged
        """
        if len(text) > 64:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 64")
            text = text[:64]
        
        if direction and direction.upper() in ['LEFT', 'RIGHT', 'CENTER']:
            cmd = f"TEXT {text} {direction.upper()}"
        else:
            cmd = f"TEXT {text}"
        
        self.send_command(cmd)
        resp = self.read_response()
        return resp == "OK"
    
    def set_brightness(self, level):
        """
        Set brightness level (0-15).
        """
        level = max(0, min(15, level))
        self.send_command(f"BRIGHT {level}")
        resp = self.read_response()
        return resp == "OK"
    
    def set_speed(self, speed):
        """
        Set animation speed (1-10).
        """
        speed = max(1, min(10, speed))
        self.send_command(f"SPEED {speed}")
        resp = self.read_response()
        return resp == "OK"

    def clear(self):
        """
        Clear the display or reset to default state.
        """
        self.send_command("CLEAR")
        return True

    def close(self):
        if self.ser.is_open:
            self.ser.close()

def auto_detect_display():
    """
    Auto-detect the LED Display ESP32 on available serial ports.
    Sends 'STATUS' and expects 'OK PATTERN=...'
    """
    # Try ACM ports first (ESP32 is typically on ttyACM*)
    ports = sorted(glob.glob('/dev/ttyACM*')) + sorted(glob.glob('/dev/ttyUSB*'))
    
    if not ports:
        return None
    
    for port in ports:
        try:
            # Try to open serial port
            ser = serial.Serial(port, 115200, timeout=2)
            time.sleep(2) # Wait for boot
            
            # Clear buffer
            ser.reset_input_buffer()
            
            # Send STATUS command
            ser.write(b"STATUS\n")
            
            # Check response
            start = time.time()
            found = False
            while time.time() - start < 2.0:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if "OK PATTERN=" in line:
                        found = True
                        break
                time.sleep(0.05)
            
            ser.close()
            
            if found:
                return DisplayController(port)
                
        except Exception as e:
            # logger.debug(f"Probe failed for {port}: {e}")
            pass
    
    return None
