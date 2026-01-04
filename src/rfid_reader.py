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
    """M5Stack U107 UHF RFID Reader Interface - Optimized for EU region and multi-polling"""
    
    # Region configurations (frequency bands in MHz)
    REGIONS = {
        'US': 0x01,   # 902-928 MHz
        'EU': 0x02,   # 865-868 MHz (European standard)
        'CN': 0x03,   # 920-925 MHz
        'IN': 0x04,   # 865-867 MHz
        'JP': 0x05,   # 916-921 MHz
    }
    
    def __init__(self, port, baud=115200, region='EU'):
        """
        Initialize UART connection to RFID module
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0')
            baud: Baud rate (default: 115200)
            region: Region code ('US', 'EU', 'CN', 'IN', 'JP') - default: 'EU'
        """
        logger.info(f"Initializing RFID on {port} (Region: {region})...")
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.buffer = bytearray()
        self.region = region
        time.sleep(0.5)  # Allow module to initialize
        
        # Set region first (affects frequency band)
        self._set_region(region)
        
        # Set power to 26dBm (maximum for EU/most regions)
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
    
    def _set_region(self, region='EU'):
        """
        Set frequency region for RFID reader
        
        Args:
            region: Region code string ('US', 'EU', 'CN', 'IN', 'JP')
            
        Returns:
            True if successful, False otherwise
        """
        if region not in self.REGIONS:
            logger.error(f"Unknown region: {region}. Valid options: {list(self.REGIONS.keys())}")
            return False
        
        region_code = self.REGIONS[region]
        cmd = bytearray([0xBB, 0x00, 0xB8, 0x00, 0x01, region_code])
        cmd.append(self._checksum(cmd))
        cmd.append(0x7E)
        
        logger.info(f"Setting region to {region} (code: {region_code:#04x})")
        self._send_command(cmd)
        success = self._wait_response()
        
        if success:
            logger.info(f"Region set to {region}")
            self.region = region
        else:
            logger.warning(f"Failed to set region to {region}")
        
        return success
    
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
    
    def read_tags_reliable(self, target_tags=6, max_duration=60, poll_interval=0.05):
        """
        Read RFID tags with maximum reliability (exhaustive search).
        Continues polling until target_tags found OR max_duration exceeded.
        Optimized for 100% detection - time is not a constraint.
        
        Args:
            target_tags: Number of unique tags to find (default: 6)
            max_duration: Maximum time to scan in seconds (default: 60)
            poll_interval: Time between polls in seconds (default: 0.05)
            
        Returns:
            List of tag dictionaries with 'epc', 'rssi', 'pc' fields
        """
        unique_tags = {}
        start_time = time.time()
        poll_count = 0
        
        logger.info(f"Starting reliable scan for {target_tags} tags (max {max_duration}s)...")
        
        while time.time() - start_time < max_duration:
            poll_count += 1
            tags = self._polling_once()
            
            for tag in tags:
                epc = tag['epc']
                if epc not in unique_tags:
                    unique_tags[epc] = tag
                    logger.info(f"Found tag {epc} (RSSI: {tag['rssi']}) - {len(unique_tags)}/{target_tags}")
                elif tag['rssi'] > unique_tags[epc]['rssi']:
                    # Update with better RSSI reading
                    unique_tags[epc] = tag
            
            # Exit early if we have all tags
            if len(unique_tags) >= target_tags:
                elapsed = time.time() - start_time
                logger.info(f"All {target_tags} tags found in {elapsed:.2f}s ({poll_count} polls)")
                break
            
            time.sleep(poll_interval)
        
        elapsed = time.time() - start_time
        logger.info(f"Scan completed: Found {len(unique_tags)} tags in {elapsed:.2f}s ({poll_count} polls)")
        
        return list(unique_tags.values())
    
    def read_tags_multi_polling(self, target_tags=6, max_duration=60, poll_interval=0.03):
        """
        Read RFID tags using multi-polling for higher tag detection efficiency.
        Uses 0x27 command which optimizes for reading multiple tags per cycle.
        
        Args:
            target_tags: Number of unique tags to find (default: 6)
            max_duration: Maximum time to scan in seconds (default: 60)
            poll_interval: Time between polls in seconds (default: 0.03 for faster multi-polling)
            
        Returns:
            List of tag dictionaries with 'epc', 'rssi', 'pc' fields
        """
        unique_tags = {}
        start_time = time.time()
        poll_count = 0
        
        logger.info(f"Starting multi-polling scan for {target_tags} tags (max {max_duration}s)...")
        
        while time.time() - start_time < max_duration:
            poll_count += 1
            # Use multi-polling mode (0x27 command)
            tags = self._polling_once(use_multi_polling=True)
            
            for tag in tags:
                epc = tag['epc']
                if epc not in unique_tags:
                    unique_tags[epc] = tag
                    logger.info(f"Found tag {epc} (RSSI: {tag['rssi']}) - {len(unique_tags)}/{target_tags}")
                elif tag['rssi'] > unique_tags[epc]['rssi']:
                    # Update with better RSSI reading
                    unique_tags[epc] = tag
            
            # Exit early if we have all tags
            if len(unique_tags) >= target_tags:
                elapsed = time.time() - start_time
                logger.info(f"All {target_tags} tags found via multi-polling in {elapsed:.2f}s ({poll_count} polls)")
                break
            
            time.sleep(poll_interval)
        
        elapsed = time.time() - start_time
        logger.info(f"Multi-polling scan completed: Found {len(unique_tags)} tags in {elapsed:.2f}s ({poll_count} polls)")
        
        return list(unique_tags.values())
    
    def _polling_once(self, use_multi_polling=False):
        """
        Single polling cycle - reads nearby tags
        
        Args:
            use_multi_polling: If True, uses multi-polling command for better tag detection
            
        Returns:
            List of detected tags with RSSI and EPC
        """
        if use_multi_polling:
            # Multi-polling command: more efficient for reading multiple tags
            # Command 0x27: allows multiple tag readings in one cycle
            cmd = [0xBB, 0x00, 0x27, 0x00, 0x00, 0x27, 0x7E]
        else:
            # Standard single-polling command
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
        
        # Check for additional responses (multi-polling allows more)
        while self._wait_response(timeout=0.1):
            if len(self.buffer) >= 24 and self.buffer[0] == 0xBB and self.buffer[1] == 0x02:
                tag = {
                    'rssi': self.buffer[5],
                    'pc': self.buffer[6:8].hex().upper(),
                    'epc': self.buffer[8:20].hex().upper(),
                }
                tags.append(tag)
        
        return tags
    
    def has_tags_present(self, confirmation_reads=2):
        """
        Check if any RFID tags are currently present.
        
        Args:
            confirmation_reads: Number of consecutive reads to confirm (default: 2)
            
        Returns:
            True if tags detected, False otherwise
        """
        for _ in range(confirmation_reads):
            tags = self._polling_once()
            if tags:
                return True
            time.sleep(0.05)
        return False
    
    def close(self):
        """Close serial connection"""
        if self.ser.is_open:
            self.ser.close()


def auto_detect_rfid(region='EU'):
    """
    Auto-detect the M5Stack UHF RFID module on available serial ports.
    
    Args:
        region: Region code ('US', 'EU', 'CN', 'IN', 'JP') - default: 'EU'
    
    Returns:
        M5StackUHF instance if found, None otherwise
    """
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        return None
    
    for port in ports:
        try:
            logger.info(f"Probing {port} for RFID...")
            rfid = M5StackUHF(port, region=region)
            if rfid._get_hardware_version():
                logger.info(f"RFID found on {port} with region {region}")
                return rfid
            rfid.close()
        except Exception as e:
            logger.debug(f"Probe failed for {port}: {e}")
            pass
    
    return None


# Example usage
if __name__ == "__main__":
    """Example: Read RFID tags continuously"""
    import argparse
    
    parser = argparse.ArgumentParser(description='M5Stack U107 RFID Reader')
    parser.add_argument('--region', default='EU', choices=['US', 'EU', 'CN', 'IN', 'JP'],
                        help='Frequency region (default: EU)')
    parser.add_argument('--mode', default='standard', choices=['standard', 'reliable', 'multi'],
                        help='Scan mode (default: standard)')
    args = parser.parse_args()
    
    print(f"M5Stack U107 UHF RFID Reader - Region: {args.region}, Mode: {args.mode}")
    print("=" * 60)
    
    rfid = auto_detect_rfid(region=args.region)
    if not rfid:
        print("Error: Could not detect RFID module")
        exit(1)
    
    print(f"✓ RFID module connected (Region: {args.region}, Power: 26dBm)")
    print("Reading tags (Ctrl+C to stop)...\n")
    
    try:
        while True:
            if args.mode == 'multi':
                tags = rfid.read_tags_multi_polling(target_tags=6, max_duration=10)
            elif args.mode == 'reliable':
                tags = rfid.read_tags_reliable(target_tags=6, max_duration=10)
            else:  # standard
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
    finally:
        rfid.close()
