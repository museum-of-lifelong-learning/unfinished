#!/usr/bin/env python3
"""
RFID Reader Test Script - Different Detection Modes
Tests various RFID tag detection strategies with detailed logging.
"""

import argparse
import logging
import time
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from rfid_controller import auto_detect_rfid


def setup_logging(verbose=False):
    """Configure logging with detailed output"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def run_standard_mode(rfid, target_tags=6, max_attempts=100, use_anti_collision=False):
    """
    Run standard tag detection mode
    
    Args:
        rfid: M5StackUHF instance
        target_tags: Number of tags to find
        max_attempts: Maximum polling attempts
        use_anti_collision: If True, silence tags after reading
    """
    mode_label = "STANDARD (ANTI-COLLISION)" if use_anti_collision else "STANDARD"
    logging.info("=" * 70)
    logging.info(f"{mode_label} MODE: target={target_tags} tags, max_attempts={max_attempts}")
    logging.info("=" * 70)
    
    start_time = time.time()
    tags = rfid.read_tags(target_tags=target_tags, max_attempts=max_attempts, use_anti_collision=use_anti_collision)
    elapsed = time.time() - start_time
    
    logging.info(f"Scan completed in {elapsed:.3f}s")
    logging.info(f"Tags found: {len(tags)}/{target_tags}")
    
    return tags, elapsed


def run_multi_polling_mode(rfid, target_tags=6, max_duration=60, poll_interval=0.03):
    """
    Run multi-polling tag detection mode
    
    Args:
        rfid: M5StackUHF instance
        target_tags: Number of tags to find
        max_duration: Maximum scan duration in seconds
        poll_interval: Time between polls
    """
    logging.info("=" * 70)
    logging.info(f"MULTI-POLLING MODE: target={target_tags} tags, max_duration={max_duration}s, interval={poll_interval}s")
    logging.info("=" * 70)
    
    start_time = time.time()
    tags = rfid.read_tags_multi_polling(
        target_tags=target_tags,
        max_duration=max_duration,
        poll_interval=poll_interval
    )
    elapsed = time.time() - start_time
    
    logging.info(f"Scan completed in {elapsed:.3f}s")
    logging.info(f"Tags found: {len(tags)}/{target_tags}")
    
    return tags, elapsed


def run_reliable_mode(rfid, target_tags=6, max_duration=60, poll_interval=0.05):
    """
    Run reliable tag detection mode (exhaustive search)
    
    Args:
        rfid: M5StackUHF instance
        target_tags: Number of tags to find
        max_duration: Maximum scan duration in seconds
        poll_interval: Time between polls
    """
    logging.info("=" * 70)
    logging.info(f"RELIABLE MODE: target={target_tags} tags, max_duration={max_duration}s, interval={poll_interval}s")
    logging.info("=" * 70)
    
    start_time = time.time()
    tags = rfid.read_tags_reliable(
        target_tags=target_tags,
        max_duration=max_duration,
        poll_interval=poll_interval
    )
    elapsed = time.time() - start_time
    
    logging.info(f"Scan completed in {elapsed:.3f}s")
    logging.info(f"Tags found: {len(tags)}/{target_tags}")
    
    return tags, elapsed


def display_tags(tags, mode_name):
    """
    Display detected tags in a formatted table
    
    Args:
        tags: List of tag dictionaries
        mode_name: Name of the detection mode used
    """
    print("\n" + "=" * 70)
    print(f"RESULTS - {mode_name}")
    print("=" * 70)
    
    if not tags:
        print("No tags detected")
        print("=" * 70)
        return
    
    # Sort by RSSI (strongest first)
    sorted_tags = sorted(tags, key=lambda t: t['rssi'], reverse=True)
    
    print(f"Total tags detected: {len(sorted_tags)}")
    print("-" * 70)
    print(f"{'#':<4} {'EPC':<26} {'RSSI':<6} {'PC':<6}")
    print("-" * 70)
    
    for idx, tag in enumerate(sorted_tags, 1):
        print(f"{idx:<4} {tag['epc']:<26} {tag['rssi']:<6} {tag['pc']:<6}")
    
    print("=" * 70)
    
    # Calculate statistics
    rssi_values = [tag['rssi'] for tag in tags]
    avg_rssi = sum(rssi_values) / len(rssi_values)
    min_rssi = min(rssi_values)
    max_rssi = max(rssi_values)
    
    print(f"RSSI Statistics: min={min_rssi}, max={max_rssi}, avg={avg_rssi:.1f}")
    print("=" * 70 + "\n")


def run_continuous_mode(rfid, mode, target_tags=6, use_anti_collision=False):
    """
    Run continuous tag detection with periodic scans
    
    Args:
        rfid: M5StackUHF instance
        mode: Detection mode to use
        target_tags: Number of tags to find per scan
        use_anti_collision: If True, use anti-collision for standard mode
    """
    mode_label = mode.upper()
    if mode == 'standard' and use_anti_collision:
        mode_label += " (ANTI-COLLISION)"
    
    logging.info("=" * 70)
    logging.info(f"CONTINUOUS MODE: {mode_label}, target={target_tags} tags")
    logging.info("Press Ctrl+C to stop")
    logging.info("=" * 70)
    
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            print(f"\n--- Scan #{scan_count} ---")
            
            if mode == 'standard':
                tags, elapsed = run_standard_mode(rfid, target_tags=target_tags, max_attempts=20, use_anti_collision=use_anti_collision)
            elif mode == 'multi':
                tags, elapsed = run_multi_polling_mode(rfid, target_tags=target_tags, max_duration=10)
            elif mode == 'reliable':
                tags, elapsed = run_reliable_mode(rfid, target_tags=target_tags, max_duration=10)
            
            display_tags(tags, f"{mode_label} - Scan #{scan_count}")
            
            time.sleep(1)  # Pause between scans
            
    except KeyboardInterrupt:
        print(f"\n\nStopped after {scan_count} scans")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RFID Reader Test Script - Test different detection modes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard mode, single scan
  python test_rfid_detection.py --mode standard --target 6

  # Multi-polling mode, single scan
  python test_rfid_detection.py --mode multi --target 6

  # Reliable mode with custom duration
  python test_rfid_detection.py --mode reliable --target 6 --duration 30

  # Continuous scanning
  python test_rfid_detection.py --mode standard --continuous

  # Use anti-collision (silence tags after reading)
  python test_rfid_detection.py --mode standard --target 6 --anti-collision

  # Verbose logging
  python test_rfid_detection.py --mode multi --target 6 --verbose
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['standard', 'multi', 'reliable'],
        default='standard',
        help='Detection mode: standard (quick), multi (multi-polling), reliable (exhaustive)'
    )
    
    parser.add_argument(
        '--target',
        type=int,
        default=6,
        help='Number of tags to detect (default: 6)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Maximum scan duration in seconds for multi/reliable modes (default: 60)'
    )
    
    parser.add_argument(
        '--region',
        choices=['US', 'EU', 'CN', 'IN', 'JP'],
        default='EU',
        help='Frequency region (default: EU)'
    )
    
    parser.add_argument(
        '--anti-collision',
        action='store_true',
        help='Use anti-collision mode (silence tags after reading) - standard mode only'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuous scanning (Ctrl+C to stop)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    mode_label = args.mode.upper()
    if args.mode == 'standard' and args.anti_collision:
        mode_label += " (ANTI-COLLISION)"
    
    print("\n" + "=" * 70)
    print("RFID Reader Test Script")
    print("=" * 70)
    print(f"Mode: {mode_label}")
    print(f"Region: {args.region}")
    print(f"Target tags: {args.target}")
    if args.mode in ['multi', 'reliable']:
        print(f"Max duration: {args.duration}s")
    if args.mode == 'standard' and args.anti_collision:
        print(f"Anti-collision: Enabled")
    print(f"Continuous: {'Yes' if args.continuous else 'No'}")
    print("=" * 70 + "\n")
    
    # Auto-detect RFID reader
    logging.info(f"Auto-detecting RFID reader (region: {args.region})...")
    rfid = auto_detect_rfid(region=args.region)
    
    if not rfid:
        logging.error("Failed to detect RFID reader")
        logging.error("Check connections and available serial ports")
        sys.exit(1)
    
    logging.info(f"✓ RFID reader detected (Region: {args.region}, Power: 26dBm)")
    
    try:
        if args.continuous:
            # Run continuous mode
            run_continuous_mode(rfid, args.mode, target_tags=args.target, use_anti_collision=args.anti_collision)
        else:
            # Run single scan
            if args.mode == 'standard':
                tags, elapsed = run_standard_mode(rfid, target_tags=args.target, use_anti_collision=args.anti_collision)
            elif args.mode == 'multi':
                tags, elapsed = run_multi_polling_mode(
                    rfid,
                    target_tags=args.target,
                    max_duration=args.duration
                )
            elif args.mode == 'reliable':
                tags, elapsed = run_reliable_mode(
                    rfid,
                    target_tags=args.target,
                    max_duration=args.duration
                )
            
            # Display results
            mode_label = args.mode.upper()
            if args.mode == 'standard' and args.anti_collision:
                mode_label += " (ANTI-COLLISION)"
            display_tags(tags, mode_label)
            print(f"Total scan time: {elapsed:.3f}s\n")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    except Exception as e:
        logging.error(f"Error during scan: {e}", exc_info=args.verbose)
        sys.exit(1)
    
    finally:
        logging.info("Closing RFID reader connection")
        rfid.close()
        logging.info("Done")


if __name__ == "__main__":
    main()
