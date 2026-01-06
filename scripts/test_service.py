#!/usr/bin/env python3
"""
Quick test script to verify the figurine service components.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'rfid'))

print("=== Figurine Service Test ===\n")

test_results = {}

# Test 1: Import dependencies
print("1. Testing imports...")
try:
    from printer_controller import PrinterController, auto_detect_printer
    from slip_printing import ReceiptRenderer
    from display_controller import auto_detect_display
    from rfid_controller import auto_detect_rfid
    import ollama
    print("   ✓ All imports successful")
    test_results["Imports"] = "OK"
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    test_results["Imports"] = "FAIL"
    sys.exit(1)

# Test 2: Device Detection
print("\n2. Detecting Devices...")

# RFID
print("   Checking RFID Reader...")
rfid = auto_detect_rfid()
if rfid:
    print("   ✓ RFID Reader detected")
    test_results["RFID Reader"] = "CONNECTED"
    rfid.close()
else:
    print("   ✗ RFID Reader NOT detected")
    test_results["RFID Reader"] = "MISSING"

# Display
print("   Checking Display...")
display = auto_detect_display()
if display:
    print("   ✓ Display detected")
    test_results["Display"] = "CONNECTED"
    display.close()
else:
    print("   ✗ Display NOT detected")
    test_results["Display"] = "MISSING"

# Printer
print("   Checking Printer...")
printer = auto_detect_printer()
if printer:
    print("   ✓ Printer detected")
    test_results["Printer"] = "CONNECTED"
else:
    print("   ⚠ Printer NOT detected, using Dummy")
    test_results["Printer"] = "DUMMY"
    printer = PrinterController(connection_type='dummy')

# Test 3: Calculate figurine ID
print("\n3. Testing figurine ID calculation...")
try:
    from src.figurine_service import calculate_figurine_id
    test_cases = [
        ([1, 1, 1, 1, 1, 1], 1),
        ([6, 6, 6, 6, 6, 6], 46656),
        ([1, 2, 3, 4, 5, 6], 1866),
    ]
    all_passed = True
    for digits, expected in test_cases:
        result = calculate_figurine_id(digits)
        if result != expected:
            all_passed = False
            print(f"   ✗ {digits} -> {result} (expected {expected})")
        else:
            print(f"   ✓ {digits} -> {result}")
    
    test_results["Logic"] = "OK" if all_passed else "FAIL"

except Exception as e:
    print(f"   ✗ Logic test failed: {e}")
    test_results["Logic"] = "ERROR"

# Test 4: Ollama connection
print("\n4. Testing Ollama connection...")
try:
    response = ollama.chat(
        model='qwen2.5:3b',
        messages=[{'role': 'user', 'content': 'Say "test" and nothing else.'}]
    )
    print(f"   ✓ Ollama responded: {response['message']['content'][:50]}...")
    test_results["AI (Ollama)"] = "OK"
except Exception as e:
    print(f"   ✗ Ollama failed: {e}")
    test_results["AI (Ollama)"] = "FAIL"

# Test 5: Print test slip
print("\n5. Testing printer output...")
try:
    print("   Printing test slip with results:")
    for k, v in test_results.items():
        print(f"     {k}: {v}")
        
    printer.print_test_slip(test_results)
    print("   ✓ Test slip printed (check printer)")
except Exception as e:
    print(f"   ✗ Print failed: {e}")

print("\n=== Test Complete ===")
print("\nIf all tests passed, you can:")
print("  1. Run the service manually: cd src && python3 figurine_service.py")
print("  2. Install as system service: ./setup_service.sh")
