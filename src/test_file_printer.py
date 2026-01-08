#!/usr/bin/env python3
"""
Test script for FilePrinter - generates a sample receipt to a markdown file.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from file_printer import FilePrinter
from slip_printing import create_full_receipt
from data_service import DataService


def test_file_printer_simple():
    """Simple test of FilePrinter functionality."""
    print("Testing FilePrinter with simple output...")
    
    printer = FilePrinter(output_dir="test_outputs", figurine_id=42)
    
    # Test basic formatting
    printer.set(align='center', bold=True)
    printer.textln("TEST RECEIPT")
    printer.set(bold=False)
    printer.ln()
    
    printer.set(align='left')
    printer.textln("This is a test of the FilePrinter.")
    printer.textln("It should create a markdown file.")
    printer.ln()
    
    printer.set(bold=True)
    printer.text("Bold Label: ")
    printer.set(bold=False)
    printer.textln("Regular text content")
    printer.ln()
    
    # Test QR code
    printer.set(align='center')
    printer.qr("https://figurati.ch/42", size=6)
    printer.ln()
    
    printer.textln("End of test receipt")
    printer.cut()
    
    print("✓ Simple test completed")


def test_file_printer_with_full_receipt():
    """Test FilePrinter with the full receipt generation."""
    print("\nTesting FilePrinter with full receipt generation...")
    
    # Initialize data service
    try:
        data_service = DataService()
    except Exception as e:
        print(f"Warning: Could not initialize DataService: {e}")
        print("Skipping full receipt test")
        return
    
    # Create sample answers
    sample_answers = [
        {'svg': 'circle_orange', 'mindset': 'Explorer'},
        {'svg': 'quadrat_green', 'mindset': 'Builder'},
        {'svg': 'circle_yellow', 'mindset': 'Explorer'},
    ]
    
    # Create FilePrinter
    printer = FilePrinter(output_dir="test_outputs", figurine_id=123)
    
    try:
        # Generate full receipt
        create_full_receipt(
            printer=printer,
            figurine_id=123,
            answers=sample_answers,
            data_service=data_service,
            model_name='qwen2.5:3b'
        )
        print("✓ Full receipt test completed")
    except Exception as e:
        print(f"Note: Full receipt generation encountered: {e}")
        print("This is expected if Ollama or figurine generation is not available")
        # Still cut to save whatever was generated
        try:
            printer.cut()
        except:
            pass


if __name__ == "__main__":
    print("=" * 60)
    print("FilePrinter Test Suite")
    print("=" * 60)
    
    test_file_printer_simple()
    test_file_printer_with_full_receipt()
    
    print("\n" + "=" * 60)
    print("Tests completed! Check test_outputs/ for markdown files.")
    print("=" * 60)
