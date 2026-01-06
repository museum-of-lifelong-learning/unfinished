#!/usr/bin/env python3
"""
Generate PNG images with geometric shapes similar to figurine stacking.
Creates 6 shapes stacked vertically, randomly chosen from a pool of shapes.
"""
from pathlib import Path
import random
import drawsvg as draw


# --- Shape drawing functions using drawsvg ---
# All shapes accept only height value, width is proportional

def draw_semioval(h):
    """Top-half semi-oval using an Arc"""
    w = h * 1.0  # Proportional width
    return draw.Path(fill='white', stroke='black', stroke_width=2).move_to(0, h).arc(w/2, h, w/2, h, 180, 360, cw=False).line_to(w, h).close()

def draw_circle(h):
    """Circle"""
    w = h * 1.0
    return draw.Circle(w/2, h/2, h/2, fill='white', stroke='black', stroke_width=2)

def draw_triangle_up(h):
    """Triangle pointing up"""
    w = h * 1.0
    return draw.Lines(w/2, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)

def draw_triangle_down(h):
    """Triangle pointing down"""
    w = h * 1.0
    return draw.Lines(w/2, h, w, 0, 0, 0, close=True, fill='white', stroke='black', stroke_width=2)

def draw_diamond(h):
    """Square rotated 45 degrees"""
    w = h * 1.0
    return draw.Lines(w/2, 0, w, h/2, w/2, h, 0, h/2, close=True, fill='white', stroke='black', stroke_width=2)

def draw_trapezoid(h):
    """Trapezoid: top width is 60%, bottom is 100%"""
    w = h * 1.0
    return draw.Lines(w*0.2, 0, w*0.8, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)

def draw_trapezoid_wide(h):
    """Trapezoid wider at top"""
    w = h * 1.0
    return draw.Lines(w*0.15, 0, w*0.85, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)

def draw_trapezoid_narrow(h):
    """Trapezoid wider at bottom"""
    w = h * 1.0
    return draw.Lines(w*0.35, 0, w*0.65, 0, w, h, 0, h, close=True, fill='white', stroke='black', stroke_width=2)

def draw_square(h):
    """Square"""
    w = h * 1.0
    size = min(w, h)
    offset_x = (w - size) / 2
    return draw.Rectangle(offset_x, 0, size, h, fill='white', stroke='black', stroke_width=2)

def draw_rectangle_tall(h):
    """Tall rectangle"""
    w = h * 1.0
    width = w * 0.4
    offset_x = (w - width) / 2
    return draw.Rectangle(offset_x, 0, width, h, fill='white', stroke='black', stroke_width=2)

def draw_rectangle_wide(h):
    """Wide rectangle"""
    w = h * 1.0
    return draw.Rectangle(0, 0, w, h, fill='white', stroke='black', stroke_width=2)

def draw_oval_horizontal(h):
    """Horizontal oval/ellipse"""
    w = h * 1.0
    cx, cy = w / 2, h / 2
    rx = w / 2
    ry = h / 3
    return draw.Ellipse(cx - rx, cy - ry, 2*rx, 2*ry, fill='white', stroke='black', stroke_width=2)

def draw_oval_vertical(h):
    """Vertical oval/ellipse"""
    w = h * 1.0
    cx, cy = w / 2, h / 2
    rx = w / 3
    ry = h / 2
    return draw.Ellipse(cx - rx, cy - ry, 2*rx, 2*ry, fill='white', stroke='black', stroke_width=2)


# --- THE MAPPING ---
SHAPE_MENU = {
    "semioval": draw_semioval,
    "circle": draw_circle,
    "triangle_up": draw_triangle_up,
    "triangle_down": draw_triangle_down,
    "diamond": draw_diamond,
    "trapezoid": draw_trapezoid,
    "trapezoid_wide": draw_trapezoid_wide,
    "trapezoid_narrow": draw_trapezoid_narrow,
    "square": draw_square,
    "rectangle_tall": draw_rectangle_tall,
    "rectangle_wide": draw_rectangle_wide,
    "oval_horizontal": draw_oval_horizontal,
    "oval_vertical": draw_oval_vertical,
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
        assets_dir = Path(__file__).parent.parent / 'assets'
        assets_dir.mkdir(exist_ok=True)
        if figurine_id is not None:
            output_path = str(assets_dir / f'figurine_{figurine_id}.png')
        else:
            output_path = str(assets_dir / 'figurine.png')

    # Calculate dimensions based on height
    figurine_width =512
    figurine_height = 600
    
    # Height ratios for each element (based on full figurine)
    token_height_ratios = [1.5, 3, 1, 6, 6, 1.5]
    
    # Calculate proportional heights for available elements
    num_elements = len(shapes)
    used_ratios = token_height_ratios[:num_elements] if num_elements <= len(token_height_ratios) else token_height_ratios
    
    # Calculate figurine width from height (aspect ratio)
    total_ratio = sum(used_ratios)
    token_heights = [int(figurine_height * ratio / total_ratio) for ratio in used_ratios]
    
    # Create drawing with white background
    d = draw.Drawing(figurine_width, figurine_height, origin=(0, 0), displayMode='inline')
    
    # Add white background
    #d.append(draw.Rectangle(0, 0, figurine_width, figurine_height, fill='white'))
    
    # Add each shape
    current_y = 0
    for i, shape_name in enumerate(shapes):
        if shape_name not in SHAPE_MENU:
            print(f"Warning: Shape '{shape_name}' not found in SHAPE_MENU")
            continue
            
        target_height = token_heights[i]
        shape_func = SHAPE_MENU[shape_name]
        
        # Create group for this shape with centering
        shape_width = target_height  # shapes have width = height
        offset_x = (figurine_width - shape_width) / 2
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