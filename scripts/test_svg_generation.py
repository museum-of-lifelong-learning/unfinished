import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_figurine import generate_figurine

def main():
    # Test with shapes identified from Level1_Fuss_side.png
    # Shapes: semioval, wide_rectangle, capsule_pill, tapered_trapezoid, wide_rectangle, blocky_trapezoid
    
    shapes_test = [
        "semioval",
        "wide_rectangle",
        "capsule_pill",
        "tapered_trapezoid",
        "wide_rectangle",
        "blocky_trapezoid"
    ]
    
    print(f"Testing SVG generation with {len(shapes_test)} shapes...")
    print(f"Shapes: {shapes_test}")
    
    output_path = "test_figurine_svg.png"
    result = generate_figurine(shapes_test, output_path, "Test\nFigurine")
    
    if result:
        print(f"✓ Successfully generated figurine at: {result}")
    else:
        print("✗ Failed to generate figurine")

if __name__ == "__main__":
    main()
