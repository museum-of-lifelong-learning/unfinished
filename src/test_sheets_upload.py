#!/usr/bin/env python3
"""
Test script for Google Sheets upload functionality.
Run this to verify the service account connection works.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sheets_upload import get_sheets_client, upload_slip_data, build_qr_url, SPREADSHEET_ID

def test_connection():
    """Test basic connection to Google Sheets."""
    print("Testing Google Sheets connection...")
    print("-" * 40)
    
    client = get_sheets_client()
    if client:
        print("✓ Authentication successful!")
        try:
            sheet = client.open_by_key(SPREADSHEET_ID)
            print(f"✓ Successfully opened sheet: {sheet.title}")
            worksheet = sheet.sheet1
            print(f"✓ First worksheet: {worksheet.title}")
            print(f"✓ Rows: {worksheet.row_count}, Cols: {worksheet.col_count}")
            
            # Get header row
            headers = worksheet.row_values(1)
            print(f"✓ Headers: {headers}")
            return True
        except Exception as e:
            print(f"✗ Error accessing sheet: {e}")
            return False
    else:
        print("✗ Authentication failed!")
        print("Check your environment variables or service account file.")
        return False

def test_upload():
    """Test uploading a sample row."""
    print("\nTesting data upload...")
    print("-" * 40)
    
    # Create sample slip data
    sample_data = {
        'figurine_id': 99999,  # Test ID
        'title_text': 'Testender\nEntdecker',
        'content': {
            'paragraph1': 'Dies ist ein Testparagraph. Er dient nur zur Überprüfung der Upload-Funktion.',
            'paragraph2': 'Ein zweiter Testparagraph mit weiteren Informationen zum Testen.'
        },
        'resources': {
            'tool': 'Test Tool. Eine Beschreibung des Test-Tools.',
            'tool_link': 'https://example.com/tool',
            'location': 'Testort. Ein Ort zum Testen ohne Link.',
            'location_link': None,
            'program': 'Testprogramm. Mit Link zum Programm.',
            'program_link': 'https://example.com/program'
        }
    }
    
    data_id = upload_slip_data(sample_data)
    
    if data_id:
        print(f"✓ Upload successful!")
        print(f"✓ data_id: {data_id}")
        print(f"✓ QR URL: {build_qr_url(data_id, sample_data['figurine_id'])}")
        return True
    else:
        print("✗ Upload failed!")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Google Sheets Upload Test")
    print("=" * 50)
    
    conn_ok = test_connection()
    
    if conn_ok:
        # Ask before uploading test data
        response = input("\nDo you want to upload a test row? (y/n): ").strip().lower()
        if response == 'y':
            test_upload()
        else:
            print("Skipping upload test.")
    
    print("\n" + "=" * 50)
    print("Test complete")
    print("=" * 50)
