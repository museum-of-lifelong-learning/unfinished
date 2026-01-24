#!/usr/bin/env python3
"""
Export individual shape SVGs for browser-side composition.
Each shape is exported at a standardized height of 100px with proper viewBox.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import drawsvg as draw
from shapes import SHAPE_MENU, SHAPE_WIDTH_RATIOS

# Standardized height for all exported shapes
STANDARD_HEIGHT = 100

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'docs' / 'assets' / 'shapes'


def export_shape(name: str, draw_func, width_ratio: float, output_dir: Path) -> str:
    """
    Export a single shape as an SVG file.
    
    Args:
        name: Shape name
        draw_func: Drawing function that takes height and returns a drawsvg element
        width_ratio: Width = height * ratio
        output_dir: Directory to save the SVG file
        
    Returns:
        Path to saved file
    """
    height = STANDARD_HEIGHT
    width = height * width_ratio
    
    # Create drawing with tight viewBox
    d = draw.Drawing(width, height, origin=(0, 0))
    d.set_pixel_scale(1)
    
    # Draw the shape
    shape_element = draw_func(height)
    d.append(shape_element)
    
    # Save SVG
    filepath = output_dir / f"{name}.svg"
    d.save_svg(str(filepath))
    
    return str(filepath)


def export_all_shapes():
    """Export all shapes to individual SVG files."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting {len(SHAPE_MENU)} shapes to {OUTPUT_DIR}")
    print(f"Standard height: {STANDARD_HEIGHT}px")
    print()
    
    for name, draw_func in SHAPE_MENU.items():
        width_ratio = SHAPE_WIDTH_RATIOS.get(name, 2.5)
        filepath = export_shape(name, draw_func, width_ratio, OUTPUT_DIR)
        width = STANDARD_HEIGHT * width_ratio
        print(f"  ✓ {name}.svg ({width:.1f}x{STANDARD_HEIGHT})")
    
    print()
    print(f"Done! Exported {len(SHAPE_MENU)} shape SVGs.")


def generate_shape_metadata():
    """Generate a JSON-compatible metadata object for JavaScript."""
    metadata = {}
    for name in SHAPE_MENU.keys():
        width_ratio = SHAPE_WIDTH_RATIOS.get(name, 2.5)
        metadata[name] = {
            "widthRatio": width_ratio,
            "standardHeight": STANDARD_HEIGHT
        }
    return metadata


if __name__ == "__main__":
    export_all_shapes()
    
    # Print metadata for JavaScript
    print("\n--- Shape Metadata (for JavaScript) ---")
    metadata = generate_shape_metadata()
    print("const SHAPE_METADATA = {")
    for name, data in metadata.items():
        print(f'    "{name}": {{ widthRatio: {data["widthRatio"]}, standardHeight: {data["standardHeight"]} }},')
    print("};")
