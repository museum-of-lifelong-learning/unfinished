#!/usr/bin/env python3
"""
Generate PNG images with geometric shapes similar to figurine stacking.
Creates shapes stacked vertically using the shapes library.
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import drawsvg as draw

# Import shapes from the shapes module
from shapes import SHAPE_MENU, SHAPE_WIDTH_RATIOS

# Load environment variables from .env file
load_dotenv()

# Get output directory for figurines from .env or default to 'output'
FIGURINE_OUTPUT_DIR = os.getenv('FIGURINE_OUTPUT_DIR')
if not FIGURINE_OUTPUT_DIR:
    FIGURINE_OUTPUT_DIR = str(Path(__file__).parent.parent / 'output')
output_dir_path = Path(FIGURINE_OUTPUT_DIR)
output_dir_path.mkdir(exist_ok=True)

def generate_figurine(shapes: list, output_path: str = None, title_text: str = None, figurine_id: int = None):
    """
    Generate a PNG by combining multiple shapes vertically using drawsvg.
    Text overlays the figurine.
    
    Args:
        shapes: List of shape names (e.g. ["circle", "square", "triangle"])
        output_path: Path to save the PNG file (if None, creates one in assets/)
        title_text: Optional text to display overlaid on the figurine
        figurine_id: Optional ID for automatic path generation
    
    Returns:
        str: Path to the generated PNG file
    """
    if not shapes:
        print("No shapes provided.")
        return None
    
    # Create output path if not provided
    if output_path is None:
        if figurine_id is not None:
            output_path = str(output_dir_path / f'figurine_{figurine_id}.png')
        else:
            output_path = str(output_dir_path / 'figurine.png')

    # Calculate dimensions based on height
    figurine_width =512
    figurine_height = 600
    
    # Height ratios for each element (based on full figurine)
    token_height_ratios = [1.5, 3, 1, 6, 6, 1.5]
    
    # Calculate proportional heights for available elements
    num_elements = len(shapes)
    
    # Extend ratios if we have more shapes than predefined ratios
    if num_elements > len(token_height_ratios):
        # Repeat the pattern or use equal distribution
        used_ratios = []
        for i in range(num_elements):
            used_ratios.append(token_height_ratios[i % len(token_height_ratios)])
    else:
        used_ratios = token_height_ratios[:num_elements]
    
    # Calculate figurine width from height (aspect ratio)
    total_ratio = sum(used_ratios)
    token_heights = [int(figurine_height * ratio / total_ratio) for ratio in used_ratios]
    
    # Create drawing with white background
    d = draw.Drawing(figurine_width, figurine_height, origin=(0, 0), displayMode='inline')
    
    # Add white background
    d.append(draw.Rectangle(0, 0, figurine_width, figurine_height, fill='white'))
    
    # Add each shape
    current_y = 0
    for i, shape_name in enumerate(shapes):
        if shape_name not in SHAPE_MENU:
            print(f"Warning: Shape '{shape_name}' not found in SHAPE_MENU")
            continue
            
        target_height = token_heights[i]
        shape_func = SHAPE_MENU[shape_name]
        
        # Calculate actual width for this shape
        width_ratio = SHAPE_WIDTH_RATIOS.get(shape_name, 2.5)
        shape_width = target_height * width_ratio
        offset_x = (figurine_width - shape_width) / 2
        
        # Create group for this shape with centering
        group = draw.Group(transform=f'translate({offset_x}, {current_y})')
        shape = shape_func(target_height)
        group.append(shape)
        d.append(group)
        
        current_y += target_height
    
    # Add title overlay if provided (on top of figurine)
    if title_text:
        lines = title_text.strip().split('\n')
        for i, line in enumerate(lines):
            y_pos = 250 + (i * 50)
            d.append(draw.Text(line, 40, figurine_width/2, y_pos, text_anchor='middle', 
                             font_family='Noto Sans', font_weight='bold', fill='black'))
    
    # Save to SVG first
    svg_output_path = Path(output_path).with_suffix('.svg')
    try:
        d.save_svg(str(svg_output_path))
        print(f"Generated SVG: {svg_output_path}")
    except Exception as e:
        print(f"Error saving SVG: {e}")
    
    # Convert SVG to PNG
    try:
        d.save_png(output_path)
        print(f"Generated PNG: {output_path}")
    except Exception as e:
        print(f"Error converting to PNG: {e}")
        print("Note: Install 'cairosvg' for PNG export: pip install cairosvg")
    
    return output_path