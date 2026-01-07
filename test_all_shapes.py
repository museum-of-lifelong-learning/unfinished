#!/usr/bin/env python3
"""
Comprehensive test to generate multiple figurines with all shapes in different positions.
This creates a variety of combinations to test centering and rendering of all shapes.
"""
import sys
from pathlib import Path
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_figurine import generate_figurine, SHAPE_MENU

def main():
    # Create output directory
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    all_shapes = list(SHAPE_MENU.keys())
    print(f"Available shapes: {all_shapes}")
    print(f"Total shapes: {len(all_shapes)}\n")
    
    test_cases = []
    
    # Test 1: Each shape individually (to verify centering)
    print("=== Test 1: Individual Shapes ===")
    for shape in all_shapes:
        test_cases.append({
            'name': f"single_{shape}",
            'shapes': [shape] * 6,  # Same shape repeated 6 times
            'title': f"Single\n{shape}"
        })
    
    # Test 2: All shapes in order
    print("=== Test 2: All Shapes in Sequence ===")
    test_cases.append({
        'name': "all_shapes_sequence",
        'shapes': all_shapes,
        'title': "All Shapes\nSequence"
    })
    
    # Test 3: Reverse order
    test_cases.append({
        'name': "all_shapes_reverse",
        'shapes': all_shapes[::-1],
        'title': "Reverse\nOrder"
    })
    
    # Test 4: Widest to narrowest
    print("=== Test 3: Width-based Ordering ===")
    from generate_figurine import SHAPE_WIDTH_RATIOS
    sorted_by_width = sorted(all_shapes, key=lambda s: SHAPE_WIDTH_RATIOS.get(s, 2.0), reverse=True)
    test_cases.append({
        'name': "widest_to_narrowest",
        'shapes': sorted_by_width,
        'title': "Wide→Narrow"
    })
    
    # Narrowest to widest
    test_cases.append({
        'name': "narrowest_to_widest",
        'shapes': sorted_by_width[::-1],
        'title': "Narrow→Wide"
    })
    
    # Test 5: Random combinations (10 variations)
    print("=== Test 4: Random Combinations ===")
    random.seed(42)  # For reproducibility
    for i in range(10):
        num_shapes = random.randint(4, 9)
        random_shapes = random.choices(all_shapes, k=num_shapes)
        test_cases.append({
            'name': f"random_{i+1:02d}",
            'shapes': random_shapes,
            'title': f"Random\n#{i+1}"
        })
    
    # Test 6: Alternating patterns
    print("=== Test 5: Alternating Patterns ===")
    # Wide/Narrow alternation
    wide_shapes = [s for s in all_shapes if SHAPE_WIDTH_RATIOS.get(s, 2.0) > 2.0]
    narrow_shapes = [s for s in all_shapes if SHAPE_WIDTH_RATIOS.get(s, 2.0) <= 2.0]
    
    alternating = []
    for i in range(6):
        if i % 2 == 0 and wide_shapes:
            alternating.append(wide_shapes[i % len(wide_shapes)])
        elif narrow_shapes:
            alternating.append(narrow_shapes[i % len(narrow_shapes)])
    
    test_cases.append({
        'name': "alternating_wide_narrow",
        'shapes': alternating,
        'title': "Alternating\nWide/Narrow"
    })
    
    # Test 7: Specific known combinations
    print("=== Test 6: Specific Patterns ===")
    test_cases.extend([
        {
            'name': "level1_reference",
            'shapes': ["semioval", "wide_rectangle", "capsule_pill", 
                      "tapered_trapezoid", "wide_rectangle", "blocky_trapezoid"],
            'title': "Level 1\nReference"
        },
        {
            'name': "diamond_sandwich",
            'shapes': ["wide_rectangle", "solid_diamond", "wide_rectangle", 
                      "solid_diamond", "wide_rectangle"],
            'title': "Diamond\nSandwich"
        },
        {
            'name': "circle_tower",
            'shapes': ["sphere_circle"] * 8,
            'title': "Circle\nTower"
        },
        {
            'name': "mixed_geometry",
            'shapes': ["sphere_circle", "solid_diamond", "capsule_pill", 
                      "stepped_block", "stacked_rectangles", "semioval"],
            'title': "Mixed\nGeometry"
        }
    ])
    
    # Generate all test cases
    print(f"\n{'='*60}")
    print(f"Generating {len(test_cases)} test figurines...")
    print(f"{'='*60}\n")
    
    success_count = 0
    fail_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        name = test_case['name']
        shapes = test_case['shapes']
        title = test_case['title']
        
        output_path = output_dir / f"{i:03d}_{name}.png"
        
        try:
            result = generate_figurine(shapes, str(output_path), title)
            if result:
                print(f"✓ [{i:3d}/{len(test_cases)}] {name:30s} - {len(shapes)} shapes")
                success_count += 1
            else:
                print(f"✗ [{i:3d}/{len(test_cases)}] {name:30s} - FAILED")
                fail_count += 1
        except Exception as e:
            print(f"✗ [{i:3d}/{len(test_cases)}] {name:30s} - ERROR: {e}")
            fail_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests:     {len(test_cases)}")
    print(f"Successful:      {success_count}")
    print(f"Failed:          {fail_count}")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"{'='*60}\n")
    
    # List all generated files
    files = sorted(output_dir.glob("*.png"))
    print(f"Generated {len(files)} PNG files:")
    for f in files[:10]:  # Show first 10
        print(f"  - {f.name}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

if __name__ == "__main__":
    main()
