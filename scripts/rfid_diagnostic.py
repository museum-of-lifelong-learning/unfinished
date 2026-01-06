#!/usr/bin/env python3
"""
RFID Tag Diagnostic Scanner
Auto-detects RFID reader and continuously logs tag IDs with RSSI for optimization.
Logs data to both console and file for analysis.
"""

import sys
import time
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rfid_controller import auto_detect_rfid, M5StackUHF

# Setup logging
log_dir = Path('/tmp/rfid_diagnostics')
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"rfid_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
json_file = log_dir / f"rfid_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

# Console logger
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(console_formatter)

# File logger
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console)
logger.addHandler(file_handler)


class RFIDDiagnostics:
    """Diagnostic scanner for RFID tags with RSSI logging"""
    
    def __init__(self, rfid, sample_interval=0.5, log_to_json=True, mode='standard'):
        """
        Initialize diagnostics scanner
        
        Args:
            rfid: M5StackUHF instance
            sample_interval: Time between scans in seconds
            log_to_json: Whether to log to JSON file
            mode: Scanning mode ('standard', 'reliable', 'multi')
        """
        self.rfid = rfid
        self.sample_interval = sample_interval
        self.log_to_json = log_to_json
        self.mode = mode
        self.tag_history = defaultdict(list)  # tag_id -> list of (timestamp, rssi)
        self.scan_count = 0
        self.start_time = time.time()
        
    def run(self, duration=None, max_scans=None):
        """
        Run continuous scanning
        
        Args:
            duration: Run for this many seconds (None = infinite)
            max_scans: Stop after this many scans (None = infinite)
        """
        logger.info("=" * 70)
        logger.info("RFID TAG DIAGNOSTIC SCANNER")
        logger.info("=" * 70)
        logger.info(f"Scanning mode: {self.mode.upper()}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"JSON file: {json_file}")
        logger.info(f"Sample interval: {self.sample_interval}s")
        if duration:
            logger.info(f"Duration: {duration}s")
        if max_scans:
            logger.info(f"Max scans: {max_scans}")
        logger.info("=" * 70)
        logger.info("Starting scan... (Press Ctrl+C to stop)\n")
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - self.start_time) > duration:
                    logger.info(f"Duration limit reached ({duration}s)")
                    break
                
                # Check scan count
                if max_scans and self.scan_count >= max_scans:
                    logger.info(f"Scan limit reached ({max_scans})")
                    break
                
                self.scan_once()
                time.sleep(self.sample_interval)
                
        except KeyboardInterrupt:
            logger.info("\nScan interrupted by user")
        finally:
            self.print_summary()
    
    def scan_once(self):
        """Perform single scan and log results"""
        self.scan_count += 1
        timestamp = datetime.now()
        
        try:
            # Perform scan based on selected mode
            if self.mode == 'multi':
                # Multi-polling: optimized for multiple tags
                tags = self.rfid.read_tags_multi_polling(target_tags=6, max_duration=5)
            elif self.mode == 'reliable':
                # Reliable: exhaustive search
                tags = self.rfid.read_tags_reliable(target_tags=6, max_duration=5)
            else:  # standard
                # Standard: fast polling with attempt limit
                tags = self.rfid.read_tags(target_tags=6, max_attempts=20)
            
            if tags:
                logger.info(f"[Scan {self.scan_count}] Found {len(tags)} tag(s) at {timestamp.strftime('%H:%M:%S.%f')[:-3]}")
                for tag in sorted(tags, key=lambda t: t['rssi'], reverse=True):
                    epc = tag['epc']
                    rssi = tag['rssi']
                    pc = tag['pc']
                    
                    # Log to console
                    logger.info(f"  └─ EPC: {epc} | RSSI: {rssi:3d} | PC: {pc}")
                    
                    # Store in history
                    self.tag_history[epc].append({
                        'timestamp': timestamp.isoformat(),
                        'rssi': rssi,
                        'pc': pc
                    })
                    
                    # Log to JSON file
                    if self.log_to_json:
                        self._log_to_json(timestamp, epc, rssi, pc)
            else:
                logger.debug(f"[Scan {self.scan_count}] No tags detected at {timestamp.strftime('%H:%M:%S.%f')[:-3]}")
                
        except Exception as e:
            logger.error(f"Scan error: {e}")
    
    def _log_to_json(self, timestamp, epc, rssi, pc):
        """Log individual tag detection to JSON file"""
        record = {
            'timestamp': timestamp.isoformat(),
            'scan_number': self.scan_count,
            'epc': epc,
            'rssi': rssi,
            'pc': pc
        }
        with open(json_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def print_summary(self):
        """Print summary statistics"""
        elapsed = time.time() - self.start_time
        
        logger.info("\n" + "=" * 70)
        logger.info("SCAN SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total scans: {self.scan_count}")
        logger.info(f"Elapsed time: {elapsed:.1f}s")
        logger.info(f"Scan rate: {self.scan_count / elapsed:.1f} scans/sec")
        logger.info(f"Unique tags found: {len(self.tag_history)}")
        logger.info("")
        
        if self.tag_history:
            logger.info("TAG STATISTICS:")
            logger.info("-" * 70)
            for epc in sorted(self.tag_history.keys()):
                readings = self.tag_history[epc]
                rssi_values = [r['rssi'] for r in readings]
                
                min_rssi = min(rssi_values)
                max_rssi = max(rssi_values)
                avg_rssi = sum(rssi_values) / len(rssi_values)
                detect_rate = (len(readings) / self.scan_count) * 100
                
                logger.info(f"\nEPC: {epc}")
                logger.info(f"  Detections: {len(readings)}/{self.scan_count} ({detect_rate:.1f}%)")
                logger.info(f"  RSSI - Min: {min_rssi}, Max: {max_rssi}, Avg: {avg_rssi:.1f}")
                logger.info(f"  PC: {readings[0]['pc']}")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"Log files saved:")
        logger.info(f"  Text: {log_file}")
        logger.info(f"  JSON: {json_file}")
        logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='RFID Tag Diagnostic Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run standard mode for 60 seconds
  %(prog)s --duration 60 --mode standard
  
  # Run reliable mode exhaustive search
  %(prog)s --duration 60 --mode reliable
  
  # Run multi-polling mode (optimized for multiple tags)
  %(prog)s --duration 60 --mode multi
  
  # Run 100 scans with multi-polling
  %(prog)s --max-scans 100 --interval 1.0 --mode multi
  
  # Run continuous multi-polling with slow intervals (2 sec)
  %(prog)s --interval 2.0 --mode multi
        """
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        help='Run for this many seconds (default: infinite)'
    )
    parser.add_argument(
        '--max-scans',
        type=int,
        help='Stop after this many scans (default: infinite)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=0.5,
        help='Time between scans in seconds (default: 0.5)'
    )
    parser.add_argument(
        '--mode',
        default='standard',
        choices=['standard', 'reliable', 'multi'],
        help='Scanning mode (default: standard)'
    )
    parser.add_argument(
        '--region',
        default='EU',
        choices=['US', 'EU', 'CN', 'IN', 'JP'],
        help='RFID frequency region (default: EU)'
    )
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Disable JSON logging'
    )
    
    args = parser.parse_args()
    
    # Auto-detect RFID module
    logger.info(f"Auto-detecting RFID reader (Region: {args.region})...")
    rfid = auto_detect_rfid(region=args.region)
    
    if not rfid:
        logger.error("❌ RFID reader not found!")
        logger.error("Checking available serial ports...")
        import glob
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if ports:
            logger.error(f"Available ports: {ports}")
            logger.error("Ensure RFID module is connected")
        else:
            logger.error("No serial ports found!")
        sys.exit(1)
    
    logger.info(f"✓ RFID reader auto-detected successfully (Region: {args.region})")
    
    # Run diagnostics
    try:
        diag = RFIDDiagnostics(
            rfid,
            sample_interval=args.interval,
            log_to_json=not args.no_json,
            mode=args.mode
        )
        diag.run(duration=args.duration, max_scans=args.max_scans)
    finally:
        rfid.close()


if __name__ == '__main__':
    main()
