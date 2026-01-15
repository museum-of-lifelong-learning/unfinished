#!/usr/bin/env python3
"""
Generate PNG images with geometric shapes similar to figurine stacking.
Creates 6 shapes stacked vertically, randomly chosen from a pool of shapes.
"""
from pathlib import Path
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get output directory for figurines from .env or default to 'output'
FIGURINE_OUTPUT_DIR = os.getenv('FIGURINE_OUTPUT_DIR')
if not FIGURINE_OUTPUT_DIR:
    FIGURINE_OUTPUT_DIR = str(Path(__file__).parent.parent / 'output')
output_dir_path = Path(FIGURINE_OUTPUT_DIR)
output_dir_path.mkdir(exist_ok=True)
import drawsvg as draw


# --- Shape drawing functions using drawsvg ---
# All shapes accept only height value, width is proportional

# --- Image: Level1_Fuss_side.png (Original Reference) ---

def draw_wide_semioval(h):
    """Shape 1: Squashed top-half semi-oval"""
    w = h * 2.5
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    path.M(0, h).A(w/2, h, 0, 0, 1, w, h).L(w, h).Z()
    return path

def draw_wide_rectangle(h):
    """Shape 2 & 5: Standard wide rectangle block"""
    w = h * 2.2
    return draw.Rectangle(0, 0, w, h, fill='white', stroke='black', stroke_width=2)

def draw_capsule_pill(h):
    """Shape 3: Flat-sided pill shape (capsule)"""
    w = h * 2.5
    return draw.Rectangle(0, 0, w, h, rx=h/2, ry=h/2, fill='white', stroke='black', stroke_width=2)

def draw_tapered_trapezoid(h):
    """Shape 4: Narrow-top trapezoid"""
    w = h * 2.5
    return draw.Lines(w*0.35, 0, w*0.65, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)

def draw_blocky_trapezoid(h):
    """Shape 6: Steep-walled trapezoid"""
    w = h * 2.0
    return draw.Lines(w*0.1, 0, w*0.9, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)


# --- Image: New Reference (Stacked & Rounded Elements) ---

def draw_stacked_rectangles(h):
    """Image 2: A narrow rectangle sitting on a wider rectangle base"""
    w_base = h * 2.2
    w_top = w_base * 0.75
    offset = (w_base - w_top) / 2
    group = draw.Group()
    # Bottom part (half height)
    group.append(draw.Rectangle(0, h/2, w_base, h/2, fill='white', stroke='black', stroke_width=2))
    # Top part (half height)
    group.append(draw.Rectangle(offset, 0, w_top, h/2, fill='white', stroke='black', stroke_width=2))
    return group

def draw_solid_diamond(h):
    """Image 3 & 4: The dark charcoal diamond shapes"""
    w = h * 1.2 # Diamonds are slightly taller/narrower than the blocks
    return draw.Lines(w/2, 0, w, h/2, w/2, h, 0, h/2, close=True, fill='white', stroke='black', stroke_width=2)

def draw_stepped_block(h):
    """Image 5: The dark stepped base shape"""
    w = h * 2.2
    indent = w * 0.15
    group = draw.Group()
    # Draws the 'notched' look seen in the dark grey shape
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    path.M(indent, 0).L(w-indent, 0).L(w-indent, h/2)
    path.L(w, h/2).L(w, h).L(0, h).L(0, h/2).L(indent, h/2).Z()
    group.append(path)
    return group

def draw_sphere_circle(h):
    """Image 6: The light green spherical shape"""
    # Note: In your image this is a perfect circle, but it sits slightly above the floor
    r = h / 2
    return draw.Circle(r, r, r, fill='white', stroke='black', stroke_width=2)


# --- THE MAPPING ---
SHAPE_MENU = {
    "semioval": draw_wide_semioval,
    "wide_rectangle": draw_wide_rectangle,
    "capsule_pill": draw_capsule_pill,
    "tapered_trapezoid": draw_tapered_trapezoid,
    "blocky_trapezoid": draw_blocky_trapezoid,  
    "stacked_rectangles": draw_stacked_rectangles,
    "solid_diamond": draw_solid_diamond,
    "stepped_block": draw_stepped_block,
    "sphere_circle": draw_sphere_circle,
}

# Width ratios for each shape (width = height * ratio)
SHAPE_WIDTH_RATIOS = {
    "semioval": 2.5,
    "wide_rectangle": 2.2,
    "capsule_pill": 2.5,
    "tapered_trapezoid": 2.5,
    "blocky_trapezoid": 2.0,
    "stacked_rectangles": 2.2,
    "solid_diamond": 1.2,
    "stepped_block": 2.2,
    "sphere_circle": 1.0,  # diameter = height
}

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