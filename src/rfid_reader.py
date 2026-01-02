#!/usr/bin/env python3
"""
M5Stack U107 UHF RFID Reader - Optimized Application Interface
Uses single_power_26dbm strategy for optimal performance.
"""

import serial
import time
import glob
import logging

# Setup logging only if running standalone
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class M5StackUHF:
    """M5Stack U107 UHF RFID Reader Interface - Optimized for 26dBm single polling"""
    
    def __init__(self, port, baud=115200):
        """Initialize UART connection to RFID module at 26dBm power"""
        logger.info(f"Initializing RFID on {port}...")
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.buffer = bytearray()
        time.sleep(0.5)  # Allow module to initialize
        
        # Set power to 26dBm (optimal based on testing)
        self._set_tx_power(2600)
        
    def _checksum(self, data):
        """Calculate checksum (sum of bytes from index 1 to n-2)"""
        return sum(data[1:-2]) & 0xFF
    
    def _send_command(self, cmd):
        """Send command to RFID module"""
        # logger.debug(f"Sending: {bytes(cmd).hex().upper()}")
        self.ser.write(bytes(cmd))
        
    def _wait_response(self, timeout=0.5):
        """Wait for response frame (0xBB...0x7E)"""
        start = time.time()
        self.buffer = bytearray()
        
        while time.time() - start < timeout:
            if self.ser.in_waiting:
                try:
                    byte = self.ser.read(1)
                    if len(byte) == 0:
                        continue
                    byte = byte[0]
                    self.buffer.append(byte)
                    if byte == 0x7E and len(self.buffer) > 0 and self.buffer[0] == 0xBB:
                        # logger.debug(f"Received: {self.buffer.hex().upper()}")
                        return True
                except Exception as e:
                    logger.error(f"Read error: {e}")
                    return False
            else:
                time.sleep(0.001)
        return False
    
    def _get_hardware_version(self):
        """Get hardware version (used for auto-detection)"""
        cmd = [0xBB, 0x00, 0x03, 0x00, 0x01, 0x00, 0x04, 0x7E]
        self._send_command(cmd)
        return self._wait_response()
    
    def _set_tx_power(self, db_centidecibels):
        """Set transmit power (2600 = 26dB)"""
        cmd = bytearray([0xBB, 0x00, 0xB6, 0x00, 0x02,
                        (db_centidecibels >> 8) & 0xFF,
                        db_centidecibels & 0xFF])
        cmd.append(self._checksum(cmd))
        cmd.append(0x7E)
        self._send_command(cmd)
        return self._wait_response()
    
    def read_tags(self, target_tags=6, max_attempts=20):
        """
        Read RFID tags using optimized single_power_26dbm strategy.
        
        Args:
            target_tags: Number of unique tags to find (default: 6)
            max_attempts: Maximum polling attempts (default: 20)
            
        Returns:
            List of tag dictionaries with 'epc', 'rssi', 'pc' fields
        """
        unique_tags = {}
        attempt = 0
        
        while len(unique_tags) < target_tags and attempt < max_attempts:
            attempt += 1
            tags = self._polling_once()
            
            for tag in tags:
                epc = tag['epc']
                if epc not in unique_tags:
                    unique_tags[epc] = tag
                elif tag['rssi'] > unique_tags[epc]['rssi']:
                    unique_tags[epc] = tag
            
            if len(unique_tags) < target_tags and attempt < max_attempts:
                time.sleep(0.05)
        
        return list(unique_tags.values())
    
    def _polling_once(self):
        """Single polling - reads nearby tags"""
        cmd = [0xBB, 0x00, 0x22, 0x00, 0x00, 0x22, 0x7E]
        self._send_command(cmd)
        
        tags = []
        if not self._wait_response(timeout=0.5):
            return tags
        
        # Process first response
        if len(self.buffer) >= 24 and self.buffer[0] == 0xBB and self.buffer[1] == 0x02:
            tag = {
                'rssi': self.buffer[5],
                'pc': self.buffer[6:8].hex().upper(),
                'epc': self.buffer[8:20].hex().upper(),
            }
            tags.append(tag)
        
        # Check for additional responses
        while self._wait_response(timeout=0.1):
            if len(self.buffer) >= 24 and self.buffer[0] == 0xBB and self.buffer[1] == 0x02:
                tag = {
                    'rssi': self.buffer[5],
                    'pc': self.buffer[6:8].hex().upper(),
                    'epc': self.buffer[8:20].hex().upper(),
                }
                tags.append(tag)
        
        return tags
    
    def close(self):
        """Close serial connection"""
        if self.ser.is_open:
            self.ser.close()


def auto_detect_rfid():
    """
    Auto-detect the M5Stack UHF RFID module on available serial ports.
    
    Returns:
        M5StackUHF instance if found, None otherwise
    """
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        return None
    
    for port in ports:
        try:
            logger.info(f"Probing {port} for RFID...")
            rfid = M5StackUHF(port)
            if rfid._get_hardware_version():
                logger.info(f"RFID found on {port}")
                return rfid
            rfid.close()
        except Exception as e:
            logger.debug(f"Probe failed for {port}: {e}")
            pass
    
    return None


# Example usage
if __name__ == "__main__":
    """Example: Read RFID tags continuously"""
    print("M5Stack U107 UHF RFID Reader - Optimized (26dBm)")
    print("=" * 60)
    
    rfid = auto_detect_rfid()
    if not rfid:
        print("Error: Could not detect RFID module")
        exit(1)
    
    print("✓ RFID module connected at 26dBm")
    print("Reading tags (Ctrl+C to stop)...\n")
    
    try:
        while True:
            tags = rfid.read_tags(target_tags=6, max_attempts=20)
            timestamp = time.strftime('%H:%M:%S')
            
            if tags:
                print(f"[{timestamp}] Found {len(tags)} tag(s):")
                for tag in sorted(tags, key=lambda t: t['rssi'], reverse=True):
                    print(f"  EPC: {tag['epc']}, RSSI: {tag['rssi']}")
            else:
                print(f"[{timestamp}] No tags detected")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Stopped")
    finally:
        rfid.close()
