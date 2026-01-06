#!/usr/bin/env python3
"""
Test script for resource query functionality.
Tests the find_best_resource function from DataService.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_service import DataService

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Test resource query functionality."""
    print("=" * 80)
    print("Testing Resource Query Functionality")
    print("=" * 80)
    
    # Initialize data service
    data_service = DataService(excel_path="../assets/Unfinished_data_collection.xlsx")
    
    if data_service.resources_df is None:
        print("ERROR: Failed to load resources data")
        return
    
    print(f"\nLoaded {len(data_service.resources_df)} resources")
    print(f"Categories: {data_service.resources_df['Kategorie'].unique().tolist()}")
    
    # Test 1: Query with specific RFID tags
    print("\n" + "=" * 80)
    print("TEST 1: Query with specific RFID tags")
    print("=" * 80)
    
    # These are example tag IDs - replace with actual ones from your dataset
    test_tags = ['E280116060000209DD1A2D7F', 'E28011606000020A17A82DC7', 
                 'E28011606000020A17A82DC8', 'E28011606000020A17A82DC9',
                 'E28011606000020A17A82DCA', 'E28011606000020A17A82DCB']
    
    print(f"Looking up tags: {test_tags[:2]}... (total {len(test_tags)})")
    answers = data_service.find_answer_by_tags(test_tags)
    
    if not answers:
        print("WARNING: No answers found for test tags. Using manual test data...")
        # Create mock answer data for testing
        answers = [
            {'Frage_ID': 'F01', 'Antwort_ID': 'A01', 'Antwort': 'Test 1', 'Mindsets': 'Explorer, Sensemaker'},
            {'Frage_ID': 'F02', 'Antwort_ID': 'A07', 'Antwort': 'Test 2', 'Mindsets': 'Explorer, Strategist'},
            {'Frage_ID': 'F03', 'Antwort_ID': 'A12', 'Antwort': 'Test 3', 'Mindsets': 'Experiencer'},
            {'Frage_ID': 'F04', 'Antwort_ID': 'A17', 'Antwort': 'Test 4', 'Mindsets': None},
            {'Frage_ID': 'F05', 'Antwort_ID': 'A25', 'Antwort': 'Orientierung', 'Mindsets': None},
            {'Frage_ID': 'F06', 'Antwort_ID': 'A29', 'Antwort': 'Am Anfang', 'Mindsets': None},
        ]
    
    print(f"\nFound {len(answers)} answers")
    for ans in answers:
        print(f"  {ans.get('Frage_ID')}: {ans.get('Antwort')} (Mindsets: {ans.get('Mindsets')})")
    
    # Test with each category
    categories = data_service.resources_df['Kategorie'].unique()
    
    for kategorie in categories:
        print(f"\n{'-' * 80}")
        print(f"Testing kategorie: {kategorie}")
        print('-' * 80)
        
        # Test with default weights
        print("\nWith default weights (1.0, 1.0, 1.0):")
        resource = data_service.find_best_resource(
            kategorie=kategorie,
            answers=answers
        )
        
        if resource:
            print(f"  ✓ Found: {resource.get('Item')}")
            print(f"    Link: {resource.get('Link')}")
            print(f"    Mindsets: {resource.get('Mindsets')}")
            print(f"    Bedürfnisse: {resource.get('Bedürfnisse')}")
            print(f"    Situation: {resource.get('Situation')}")
        else:
            print("  ✗ No resource found")
    
    # Test 2: Different weight configurations
    print("\n" + "=" * 80)
    print("TEST 2: Testing different weight configurations")
    print("=" * 80)
    
    kategorie = categories[0] if len(categories) > 0 else 'Tools & Inspiration'
    
    weight_configs = [
        (2.0, 1.0, 1.0, "High mindset weight"),
        (1.0, 2.0, 1.0, "High F05 weight"),
        (1.0, 1.0, 2.0, "High F06 weight"),
        (0.0, 1.0, 1.0, "No mindset weight"),
        (1.0, 0.0, 0.0, "Mindset only"),
    ]
    
    for mindset_w, f05_w, f06_w, description in weight_configs:
        print(f"\n{description} ({mindset_w}, {f05_w}, {f06_w}):")
        resource = data_service.find_best_resource(
            kategorie=kategorie,
            answers=answers,
            mindset_weight=mindset_w,
            f05_weight=f05_w,
            f06_weight=f06_w
        )
        
        if resource:
            print(f"  ✓ {resource.get('Item')}")
        else:
            print("  ✗ No resource found")
    
    print("\n" + "=" * 80)
    print("Tests completed!")
    print("=" * 80)

if __name__ == '__main__':
    main()
