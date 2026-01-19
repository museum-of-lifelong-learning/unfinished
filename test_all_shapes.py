#!/usr/bin/env python3
"""
Comprehensive test to generate multiple figurines with all shapes in different positions.
This creates a variety of combinations to test centering and rendering of all shapes.
Respects level-specific shape constraints (level 1 = bottom, level 6 = top).
"""
import sys
from pathlib import Path
import random
import itertools

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_figurine import generate_figurine, SHAPE_MENU, SHAPE_WIDTH_RATIOS

# Level-specific shape assignments (level 1 = top, level 6 = bottom)
LEVEL_SHAPES = {
    1: ["capsule_pill", "semioval", "flat_pyramid_sockel", "stepped_block", "wide_rectangle"],
    2: ["sphere_circle","sphere_circle","sphere_circle","sphere_circle","sphere_circle","sphere_circle"],
    3: ["flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle"],
    4: ["stepped_block_3", "stacked_circles_custom", "rhombus_udlr", "tall_trapezoid", "facing_bowls"],
    5: ["tall_pyramid", "rhombus_udlr", "stacked_circles","stacked_circles",  "double_upright_pill"],
    6: ["semioval", "wide_rectangle","wide_rectangle", "capsule_pill", "flat_pyramid", "flat_trapezoid"]
}

def get_random_shape_for_level(level):
    """Get a random shape valid for the given level (1-6)."""
    return random.choice(LEVEL_SHAPES[level])

def get_random_shapes_stack():
    """Generate a random stack of 6 shapes respecting level constraints."""
    return [get_random_shape_for_level(level) for level in range(1, 7)]

def main():
    # Create output directory
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Get all unique shapes across all levels
    all_shapes = set()
    for shapes in LEVEL_SHAPES.values():
        all_shapes.update(shapes)
    all_shapes = sorted(all_shapes)
    
    print(f"Level-specific shapes:")
    for level in range(1, 7):
        print(f"  Level {level}: {LEVEL_SHAPES[level]}")
    print(f"\nTotal unique shapes: {len(all_shapes)}\n")
    
    test_cases = []
    
    # Test 1: Each shape in its valid levels
    print("=== Test 1: Individual Shapes in Valid Levels ===")
    for shape in all_shapes:
        # Find which levels this shape can appear in
        valid_levels = [level for level, shapes in LEVEL_SHAPES.items() if shape in shapes]
        
        # Create a stack with this shape where it's valid, random elsewhere
        shapes_stack = []
        for level in range(1, 7):
            if level in valid_levels:
                shapes_stack.append(shape)
            else:
                shapes_stack.append(get_random_shape_for_level(level))
        
        test_cases.append({
            'name': f"feature_{shape}",
            'shapes': shapes_stack,
            'title': f"{shape}\nLvls:{','.join(map(str, valid_levels))}"
        })
    
    # Test 2: Random 6-shape combinations (100 variations) - respecting levels
    print("=== Test 2: Random 6-Shape Combinations (Level-Aware) ===")
    random.seed(42)  # For reproducibility
    for i in range(100):
        random_shapes = get_random_shapes_stack()
        test_cases.append({
            'name': f"random_6stack_{i+1:03d}",
            'shapes': random_shapes,
            'title': f"Random\n#{i+1}"
        })
    
    # Test 3: Each level showcasing all its available shapes
    print("=== Test 3: Level-Specific Showcases ===")
    for level in range(1, 7):
        level_shapes = LEVEL_SHAPES[level]
        for i, shape in enumerate(level_shapes):
            # Create a stack with this shape at its level
            shapes_stack = []
            for curr_level in range(1, 7):
                if curr_level == level:
                    shapes_stack.append(shape)
                else:
                    shapes_stack.append(get_random_shape_for_level(curr_level))
            
            test_cases.append({
                'name': f"level{level}_{shape}",
                'shapes': shapes_stack,
                'title': f"L{level}:\n{shape}"
            })
    
    # Test 4: Width variation patterns (level-aware)
    print("=== Test 4: Width-based Patterns (Level-Aware) ===")
    for i in range(20):
        random.seed(200 + i)
        # Sort shapes at each level by width
        shapes_stack = []
        for level in range(1, 7):
            level_shapes = LEVEL_SHAPES[level]
            sorted_level = sorted(level_shapes, key=lambda s: SHAPE_WIDTH_RATIOS.get(s, 2.0), reverse=(i % 2 == 0))
            shapes_stack.append(random.choice(sorted_level[:max(1, len(sorted_level)//2)]))
        
        test_cases.append({
            'name': f"width_pattern_{i+1:02d}",
            'shapes': shapes_stack,
            'title': f"Width\n#{i+1}"
        })
    
    # Test 5: Repeating patterns where shapes appear in multiple levels
    print("=== Test 5: Multi-Level Shapes ===")
    # Find shapes that appear in multiple levels
    multi_level_shapes = []
    for shape in all_shapes:
        valid_levels = [level for level, shapes in LEVEL_SHAPES.items() if shape in shapes]
        if len(valid_levels) > 1:
            multi_level_shapes.append((shape, valid_levels))
    
    for shape, valid_levels in multi_level_shapes:
        # Use this shape in all its valid levels
        shapes_stack = []
        for level in range(1, 7):
            if level in valid_levels:
                shapes_stack.append(shape)
            else:
                shapes_stack.append(get_random_shape_for_level(level))
        
        test_cases.append({
            'name': f"multilevel_{shape}",
            'shapes': shapes_stack,
            'title': f"{shape}\nAll Levels"
        })
    
    # Test 6: Consistent choice patterns
    print("=== Test 6: Consistent Patterns ===")
    for i in range(30):
        random.seed(300 + i)
        # Pick first available shape at each level
        shapes_stack = [LEVEL_SHAPES[level][i % len(LEVEL_SHAPES[level])] for level in range(1, 7)]
        test_cases.append({
            'name': f"consistent_{i+1:02d}",
            'shapes': shapes_stack,
            'title': f"Pattern\n#{i+1}"
        })
    
    # Test 7: Specific interesting patterns (level-aware)
    print("=== Test 7: Specific Patterns ===")
    random.seed(400)
    test_cases.extend([
        {
            'name': "all_circles",
            'shapes': [
                random.choice(LEVEL_SHAPES[1]),  # Level 1
                random.choice(LEVEL_SHAPES[2]),  # Level 2
                random.choice(LEVEL_SHAPES[3]),  # Level 3
                "flat_rectangle",                 # Level 4 (only option)
                "sphere_circle",                  # Level 5 (circles!)
                random.choice(LEVEL_SHAPES[6])   # Level 6
            ],
            'title': "Circle\nL5"
        },
        {
            'name': "capsule_bookends",
            'shapes': [
                "capsule_pill",      # Level 1 (available)
                get_random_shape_for_level(2),
                get_random_shape_for_level(3),
                "flat_rectangle",    # Level 4
                "sphere_circle",     # Level 5
                "capsule_pill"       # Level 6 (available)
            ],
            'title': "Capsule\nBookends"
        },
        {
            'name': "semioval_bookends",
            'shapes': [
                "semioval",          # Level 1 (available)
                get_random_shape_for_level(2),
                get_random_shape_for_level(3),
                "flat_rectangle",    # Level 4
                "sphere_circle",     # Level 5
                "semioval"           # Level 6 (available)
            ],
            'title': "Semioval\nBookends"
        },
        {
            'name': "rhombus_repeat",
            'shapes': [
                get_random_shape_for_level(1),
                "rhombus_udlr",      # Level 2 (available)
                "rhombus_udlr",      # Level 3 (available)
                "flat_rectangle",    # Level 4
                "sphere_circle",     # Level 5
                get_random_shape_for_level(6)
            ],
            'title': "Rhombus\nL2+L3"
        },
        {
            'name': "pyramid_variety",
            'shapes': [
                "flat_pyramid",      # Level 1 (available)
                "tall_pyramid",      # Level 2 (available)
                get_random_shape_for_level(3),
                "flat_rectangle",    # Level 4
                "sphere_circle",     # Level 5
                "flat_pyramid_sockel" # Level 6 (available)
            ],
            'title': "Pyramid\nVariety"
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
