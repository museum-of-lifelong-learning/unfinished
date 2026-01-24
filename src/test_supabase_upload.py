"""
Test script for Supabase upload functionality.
Run this to verify your Supabase setup is working correctly.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_upload import get_supabase_client, upload_slip_data, build_qr_url

def test_connection():
    """Test basic Supabase connection."""
    print("Testing Supabase connection...")
    client = get_supabase_client()
    
    if client:
        print("✓ Successfully connected to Supabase!")
        return True
    else:
        print("✗ Failed to connect to Supabase")
        print("  Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in your .env file")
        return False


def test_upload():
    """Test uploading sample data."""
    print("\nTesting data upload...")
    
    # Sample slip data
    test_data = {
        'figurine_id': 99999,  # Use a high number for testing
        'title_text': 'Test\nFigurine',
        'content': {
            'paragraph1': 'This is a test paragraph one.',
            'paragraph2': 'This is a test paragraph two.'
        },
        'resources': {
            'tool': 'Test Tool. A useful tool for testing.',
            'tool_link': 'https://example.com/tool',
            'location': 'Test Location. A place to test things.',
            'location_link': 'https://example.com/location',
            'program': 'Test Program. A program for testing.',
            'program_link': 'https://example.com/program'
        }
    }
    
    data_id = upload_slip_data(test_data)
    
    if data_id:
        print(f"✓ Successfully uploaded test data!")
        print(f"  data_id: {data_id}")
        
        # Build QR URL
        qr_url = build_qr_url(data_id, test_data['figurine_id'])
        print(f"  QR URL: {qr_url}")
        return data_id
    else:
        print("✗ Failed to upload test data")
        return None


def test_read(data_id: str):
    """Test reading data back from Supabase."""
    print("\nTesting data read...")
    
    client = get_supabase_client()
    if not client:
        print("✗ Could not get Supabase client")
        return False
    
    try:
        result = client.table('slips').select('*').eq('data_id', data_id).execute()
        
        if result.data and len(result.data) > 0:
            print("✓ Successfully read data back!")
            print(f"  Retrieved record: {result.data[0]}")
            return True
        else:
            print("✗ No data found for data_id:", data_id)
            return False
    except Exception as e:
        print(f"✗ Error reading data: {e}")
        return False


def test_delete(data_id: str):
    """Clean up test data."""
    print("\nCleaning up test data...")
    
    client = get_supabase_client()
    if not client:
        print("✗ Could not get Supabase client")
        return False
    
    try:
        result = client.table('slips').delete().eq('data_id', data_id).execute()
        print(f"✓ Deleted test record with data_id: {data_id}")
        return True
    except Exception as e:
        print(f"✗ Error deleting data: {e}")
        return False


def main():
    print("=" * 60)
    print("Supabase Upload Test Script")
    print("=" * 60)
    
    # Check environment variables
    print("\nChecking environment variables...")
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not url:
        print("✗ SUPABASE_URL is not set")
    else:
        print(f"✓ SUPABASE_URL is set: {url[:30]}...")
    
    if not key:
        print("✗ SUPABASE_SERVICE_KEY is not set")
    else:
        print(f"✓ SUPABASE_SERVICE_KEY is set: {key[:20]}...")
    
    if not url or not key:
        print("\n⚠ Please set the required environment variables and try again.")
        return
    
    # Run tests
    if not test_connection():
        return
    
    data_id = test_upload()
    if not data_id:
        return
    
    test_read(data_id)
    
    # Ask before deleting
    response = input("\nDelete test record? (y/n): ").strip().lower()
    if response == 'y':
        test_delete(data_id)
    else:
        print(f"Test record kept. data_id: {data_id}")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
