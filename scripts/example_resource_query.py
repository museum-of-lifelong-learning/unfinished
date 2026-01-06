#!/usr/bin/env python3
"""
Example usage of the resource query functionality.
Shows how to use find_best_resource() from DataService.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_service import DataService

def example_usage():
    """Example of how to use the find_best_resource function."""
    
    # Initialize data service
    data_service = DataService(excel_path="../assets/Unfinished_data_collection.xlsx")
    
    # Example 1: Get answers from RFID tags
    print("Example 1: Finding resource based on RFID tags")
    print("-" * 60)
    
    # Replace these with actual RFID tag IDs from your system
    tag_ids = ['YOUR_TAG_1', 'YOUR_TAG_2', 'YOUR_TAG_3', 
               'YOUR_TAG_4', 'YOUR_TAG_5', 'YOUR_TAG_6']
    
    # Find answers for these tags
    answers = data_service.find_answer_by_tags(tag_ids)
    
    if answers and len(answers) == 6:
        # Query for a resource in the "Tools & Inspiration" category
        resource = data_service.find_best_resource(
            kategorie='Tools & Inspiration',
            answers=answers
        )
        
        if resource:
            print(f"Found resource: {resource['Item']}")
            print(f"Link: {resource['Link']}")
        else:
            print("No matching resource found")
    else:
        print("Could not find all 6 answers for the given tags")
    
    print("\n")
    
    # Example 2: Using custom weights
    print("Example 2: Custom weights (prioritize mindsets)")
    print("-" * 60)
    
    # Create sample answers manually for demonstration
    sample_answers = [
        {'Frage_ID': 'F01', 'Antwort': 'Answer 1', 'Mindsets': 'Explorer, Sensemaker'},
        {'Frage_ID': 'F02', 'Antwort': 'Answer 2', 'Mindsets': 'Strategist'},
        {'Frage_ID': 'F03', 'Antwort': 'Answer 3', 'Mindsets': 'Experiencer'},
        {'Frage_ID': 'F04', 'Antwort': 'Answer 4', 'Mindsets': None},
        {'Frage_ID': 'F05', 'Antwort': 'Orientierung', 'Mindsets': None},  # This maps to Bedürfnisse
        {'Frage_ID': 'F06', 'Antwort': 'Am Anfang', 'Mindsets': None},     # This maps to Situation
    ]
    
    # Find resource with high mindset weight
    resource = data_service.find_best_resource(
        kategorie='Anlaufstellen & Angebote',
        answers=sample_answers,
        mindset_weight=2.0,  # Prioritize mindset matching
        f05_weight=1.0,
        f06_weight=1.0
    )
    
    if resource:
        print(f"Found resource: {resource['Item']}")
        print(f"Mindsets: {resource['Mindsets']}")
        print(f"Bedürfnisse: {resource['Bedürfnisse']}")
        print(f"Situation: {resource['Situation']}")
    
    print("\n")
    
    # Example 3: Different category
    print("Example 3: Programm-Empfehlung category")
    print("-" * 60)
    
    resource = data_service.find_best_resource(
        kategorie='Programm-Empfehlung',
        answers=sample_answers,
        mindset_weight=1.0,
        f05_weight=2.0,  # Prioritize F05 (Bedürfnisse) matching
        f06_weight=1.0
    )
    
    if resource:
        print(f"Found resource: {resource['Item']}")
    
    print("\n")
    
    # Show available categories
    print("Available categories:")
    print("-" * 60)
    if data_service.resources_df is not None:
        categories = data_service.resources_df['Kategorie'].unique()
        for cat in categories:
            count = len(data_service.resources_df[data_service.resources_df['Kategorie'] == cat])
            print(f"  - {cat} ({count} resources)")

if __name__ == '__main__':
    example_usage()
