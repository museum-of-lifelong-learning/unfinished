#!/usr/bin/env python3
"""
RFID Diagnostic Data Analyzer
Analyzes log files from rfid_diagnostic.py to help optimize tag detection.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import statistics


def analyze_log_file(json_file):
    """
    Analyze RFID scan data from JSON log file
    
    Args:
        json_file: Path to .jsonl file from rfid_diagnostic.py
    """
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    # Load data
    records = []
    with open(json_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if not records:
        print("Error: No data in log file")
        sys.exit(1)
    
    # Group by EPC
    by_epc = defaultdict(list)
    for record in records:
        by_epc[record['epc']].append(record)
    
    # Print summary
    print("\n" + "=" * 80)
    print("RFID DIAGNOSTIC ANALYSIS")
    print("=" * 80)
    print(f"File: {json_file}")
    print(f"Total records: {len(records)}")
    print(f"Total scans: {max(r['scan_number'] for r in records) if records else 0}")
    print(f"Unique tags: {len(by_epc)}")
    print("=" * 80)
    
    # Analyze each tag
    for epc in sorted(by_epc.keys()):
        detections = by_epc[epc]
        rssi_values = [d['rssi'] for d in detections]
        pc = detections[0]['pc']
        
        # Calculate statistics
        min_rssi = min(rssi_values)
        max_rssi = max(rssi_values)
        avg_rssi = statistics.mean(rssi_values)
        stdev_rssi = statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0
        
        total_scans = max(r['scan_number'] for r in records)
        detection_rate = (len(detections) / total_scans) * 100
        
        print(f"\n📍 EPC: {epc}")
        print(f"   PC: {pc}")
        print(f"   Detections: {len(detections)}/{total_scans} ({detection_rate:.1f}%)")
        print(f"   RSSI Stats:")
        print(f"     • Min:    {min_rssi}")
        print(f"     • Max:    {max_rssi}")
        print(f"     • Avg:    {avg_rssi:.1f}")
        print(f"     • StdDev: {stdev_rssi:.1f}")
        
        # Detection quality assessment
        if detection_rate >= 95:
            quality = "✓ Excellent"
        elif detection_rate >= 80:
            quality = "◐ Good"
        elif detection_rate >= 60:
            quality = "△ Fair"
        else:
            quality = "✗ Poor"
        
        print(f"   Quality: {quality}")
        
        # RSSI signal quality
        if avg_rssi >= 200:
            signal = "Strong (≥200)"
        elif avg_rssi >= 150:
            signal = "Medium (150-200)"
        elif avg_rssi >= 100:
            signal = "Weak (100-150)"
        else:
            signal = "Very Weak (<100)"
        
        print(f"   Signal: {signal}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    # Analyze overall quality
    avg_detection_rate = sum(
        (len(detections) / max(r['scan_number'] for r in records)) * 100
        for detections in by_epc.values()
    ) / len(by_epc)
    
    if avg_detection_rate < 80:
        print("⚠ Low detection rate detected")
        print("  • Check RFID module antenna connection")
        print("  • Ensure tags are properly placed")
        print("  • Check for RF interference")
        print("  • Try adjusting TX power (currently at 26dBm)")
        print("  • Ensure tags are within antenna range")
    
    # Check RSSI levels
    all_rssi = [d['rssi'] for dets in by_epc.values() for d in dets]
    if statistics.mean(all_rssi) < 150:
        print("\n⚠ Low average RSSI detected")
        print("  • Increase antenna gain if available")
        print("  • Bring tags closer to reader")
        print("  • Check for metallic/conductive interference nearby")
    
    print("\n" + "=" * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze RFID diagnostic logs')
    parser.add_argument('logfile', help='JSON log file from rfid_diagnostic.py')
    
    args = parser.parse_args()
    
    analyze_log_file(args.logfile)


if __name__ == '__main__':
    main()
