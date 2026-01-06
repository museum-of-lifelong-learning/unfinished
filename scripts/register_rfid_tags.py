#!/usr/bin/env python3
"""
RFID Tag Registration Tool
Reads RFID tags and registers them in the Excel Antworten sheet.
"""

import sys
import time
from pathlib import Path

# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rfid_controller import auto_detect_rfid
import pandas as pd

# Excel file path
EXCEL_FILE = Path(__file__).parent.parent / 'assets' / 'Unfinished_data_collection.xlsx'


def load_answers():
    """Load Antworten sheet from Excel."""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='Antworten')
        return df
    except Exception as e:
        print(f"✗ Error loading Excel file: {e}")
        return None


def save_answers(df):
    """Save updated Antworten sheet back to Excel."""
    try:
        # Read all sheets
        with pd.ExcelFile(EXCEL_FILE) as xls:
            sheets = {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}
        
        # Update Antworten sheet
        sheets['Antworten'] = df
        
        # Write all sheets back
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            for sheet_name, sheet_df in sheets.items():
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✓ Excel file updated: {EXCEL_FILE}")
        return True
    except Exception as e:
        print(f"✗ Error saving Excel file: {e}")
        return False


def main():
    print("=" * 60)
    print("RFID Tag Registration Tool - Excel Edition")
    print("=" * 60)
    print()
    
    # Load Excel data
    print("Loading Excel file...")
    df = load_answers()
    if df is None:
        sys.exit(1)
    
    print(f"✓ Loaded {len(df)} answers from Excel")
    print()
    
    # Show available answers
    if 'Antwort_ID' in df.columns:
        answer_ids = df['Antwort_ID'].dropna().tolist()
        print(f"Available Answer IDs: {', '.join(map(str, answer_ids))}")
    print()
    
    # Auto-detect RFID reader
    print("Detecting RFID reader...")
    rfid = auto_detect_rfid()
    
    if not rfid:
        print("✗ Error: Could not detect RFID reader")
        print("  Make sure the reader is connected and you have permissions.")
        sys.exit(1)
    
    print("✓ RFID reader detected")
    print()
    
    print("Instructions:")
    print("  1. Place an RFID tag near the reader")
    print("  2. Enter the Answer ID (e.g., A01, A07)")
    print("  3. Tag will be registered to that answer")
    print("  4. Press Ctrl+C to save and exit")
    print()
    print("-" * 60)
    print()
    
    modified = False
    
    try:
        while True:
            print("Scanning for RFID tag... (place tag near reader)")
            
            # Wait for a tag
            tags = []
            while not tags:
                tags = rfid.read_tags(target_tags=1, max_attempts=5)
                if not tags:
                    time.sleep(0.2)
            
            # Get the strongest signal tag
            tag = max(tags, key=lambda t: t['rssi'])
            tag_id = tag['epc']
            rssi = tag['rssi']
            
            print(f"\n✓ Tag detected: {tag_id} (RSSI: {rssi})")
            
            # Check if tag already exists in Excel
            existing_rows = df[df['RFID_Tag_ID'] == tag_id]
            if not existing_rows.empty:
                existing_answer = existing_rows.iloc[0]['Antwort_ID']
                print(f"  ⚠ This tag is already assigned to: {existing_answer}")
                overwrite = input("  Reassign? (y/N): ").strip().lower()
                if overwrite != 'y':
                    print("  Skipped.\n")
                    print("-" * 60)
                    continue
                else:
                    # Clear existing assignment
                    df.loc[df['RFID_Tag_ID'] == tag_id, 'RFID_Tag_ID'] = None
            
            # Get answer ID from user
            answer_id = input("Enter Answer ID (e.g., A01): ").strip().upper()
            
            if not answer_id:
                print("  ✗ Empty Answer ID, skipping...\n")
                print("-" * 60)
                continue
            
            # Find row with this answer ID
            answer_rows = df[df['Antwort_ID'] == answer_id]
            
            if answer_rows.empty:
                print(f"  ✗ Answer ID '{answer_id}' not found in Excel")
                print(f"  Available: {', '.join(map(str, df['Antwort_ID'].dropna().tolist()))}")
                print()
                print("-" * 60)
                continue
            
            # Check if this answer already has a tag
            row_idx = answer_rows.index[0]
            existing_tag = df.loc[row_idx, 'RFID_Tag_ID']
            
            if pd.notna(existing_tag):
                print(f"  ⚠ Answer '{answer_id}' already has tag: {existing_tag}")
                replace = input("  Replace? (y/N): ").strip().lower()
                if replace != 'y':
                    print("  Skipped.\n")
                    print("-" * 60)
                    continue
            
            # Assign tag to answer
            df.loc[row_idx, 'RFID_Tag_ID'] = tag_id
            modified = True
            
            # Show the answer details
            answer_text = df.loc[row_idx, 'Antwort'] if 'Antwort' in df.columns else 'N/A'
            print(f"\n✓ Registered:")
            print(f"  Tag:    {tag_id}")
            print(f"  Answer: {answer_id}")
            print(f"  Text:   {answer_text}")
            print()
            
            # Count how many tags are registered
            registered_count = df['RFID_Tag_ID'].notna().sum()
            total_count = len(df)
            print(f"  Progress: {registered_count}/{total_count} answers have tags")
            print()
            print("-" * 60)
            print()
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        
        if modified:
            print("Saving changes to Excel...")
            if save_answers(df):
                registered_count = df['RFID_Tag_ID'].notna().sum()
                print(f"✓ Saved! {registered_count} answers now have RFID tags")
            else:
                print("✗ Failed to save changes")
        else:
            print("No changes made")
        
        print("=" * 60)
    finally:
        rfid.close()


if __name__ == "__main__":
    main()
