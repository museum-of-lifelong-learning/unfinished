#!/usr/bin/env python3
"""
Test the updated tag lookup logic with individual tag matching.
"""

import sys
from pathlib import Path

# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from data_handler import FigurineDataHandler

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Test tags from the user's output
TEST_TAGS = [
    'E28069150000700B3E03A060',
    'E28069150000600B3E03B060',
    'E28069150000700B3E03AC60',
    'E28069150000600B3E03A460',
    'E28069150000700B3E03B460',
    'E28069150000600B3E03C860'
]

def main():
    print("=" * 80)
    print("Testing Individual Tag Lookup")
    print("=" * 80)
    print()
    
    # Initialize data handler
    handler = FigurineDataHandler(excel_path="assets/Unfinished_data_collection.xlsx")
    print()
    
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
