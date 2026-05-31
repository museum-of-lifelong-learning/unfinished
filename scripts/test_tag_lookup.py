#!/usr/bin/env python3
"""
Test the updated tag lookup logic with individual tag matching.
"""

import sys
from pathlib import Path

# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from data_service import DataService

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Test tags from the active entries (A01, A02, A03)
TEST_TAGS = [
    'E28069150000600B3E03F860',
    'E28069150000700B3E03E860',
    'E28069150000600B3E03F460',
    'E28069150000600B3E03D060'
]

def main():
    print("=" * 80)
    print("Testing Individual Tag Lookup")
    print("=" * 80)
    print()
    
    # Initialize data handler
    handler = DataService(excel_path="assets/Unfinished_data_collection.xlsx")
    print()
    
    # Let's dynamically add a comma-separated tag to Answer A01 for testing multi-tag features
    if handler.answers_df is not None:
        idx_list = handler.answers_df[handler.answers_df['Antwort_ID'] == 'A01'].index
        if len(idx_list) > 0:
            row_idx = idx_list[0]
            orig_tag = handler.answers_df.loc[row_idx, 'RFID_Tag_ID']
            test_tags_combined = f"{orig_tag}, TEST_EXTRA_TAG_1, TEST_EXTRA_TAG_2"
            handler.answers_df.loc[row_idx, 'RFID_Tag_ID'] = test_tags_combined
            print(f"🧬 In-memory modification for testing: Assigned '{test_tags_combined}' to A01")
            
            # Add these test extra tags to our search list
            TEST_TAGS.extend(['TEST_EXTRA_TAG_1', 'test_extra_tag_2'])
    
    # Search for tags
    print(f"Searching for {len(TEST_TAGS)} tags:")
    for tag in TEST_TAGS:
        print(f"  - {tag}")
    print()
    print("-" * 80)
    print()
    
    results = handler.find_answer_by_tags(TEST_TAGS)
    
    print()
    print("=" * 80)
    print(f"Results: Found {len(results)}/{len(TEST_TAGS)} answers")
    print("=" * 80)
    print()
    
    if results:
        for i, answer in enumerate(results, 1):
            print(f"Answer {i}:")
            for key, value in answer.items():
                if not (key.startswith('_') or pd.isna(value)):
                    print(f"  {key}: {value}")
            print()
    else:
        print("No answers found")
    

if __name__ == "__main__":
    import pandas as pd
    main()
