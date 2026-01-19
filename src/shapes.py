#!/usr/bin/env python3
"""
Shape drawing library for figurine generation.
All shapes accept only height value, width is proportional.

To add a new shape:
1. Create a function `draw_<shape_name>(h)` that returns a drawsvg element
2. Add the shape name and function to SHAPE_MENU
3. Add the width ratio to SHAPE_WIDTH_RATIOS
"""
import drawsvg as draw
from pathlib import Path
import math


# =============================================================================
# SHAPE DRAWING FUNCTIONS
# =============================================================================

# --- Original Reference Shapes ---

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


# --- Stacked & Composite Shapes ---

def draw_stepped_block(h):
    """The stepped/notched base shape"""
    w = h * 2.2
    indent = w * 0.15
    group = draw.Group()
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    path.M(indent, 0).L(w-indent, 0).L(w-indent, h/2)
    path.L(w, h/2).L(w, h).L(0, h).L(0, h/2).L(indent, h/2).Z()
    group.append(path)
    return group


def draw_sphere_circle(h):
    """A perfect circle/sphere shape"""
    r = h / 2
    # Circle centered at (r, r) means bounding box is (0, 0) to (h, h)
    return draw.Circle(r, r, r, fill='white', stroke='black', stroke_width=2)


# --- Flat/Wide Shapes ---

def draw_flat_pyramid(h):
    """Very flat pyramid (wide base, very low height)"""
    w = h * 4.0
    return draw.Lines(0, h, w, h, w/2, 0, close=True, fill='white', stroke='black', stroke_width=2)


def draw_flat_rectangle(h):
    """Very flat, wide rectangle"""
    w = h * 6.0
    return draw.Rectangle(0, 0, w, h, fill='white', stroke='black', stroke_width=2)


def draw_flat_pressed_oval(h):
    """Very flat, wide oval"""
    w = h * 4.0
    # Ellipse centered at (w/2, h/2) means bounding box is (0, 0) to (w, h)
    return draw.Ellipse(w/2, h/2, w/2, h/2, fill='white', stroke='black', stroke_width=2)


def draw_flat_trapezoid(h):
    """Very flat trapezoid, top slightly narrower than bottom"""
    w = h * 4.0
    top_w = w * 0.7
    left_top_x = (w - top_w) / 2
    right_top_x = left_top_x + top_w
    return draw.Lines(0, h, w, h, right_top_x, 0, left_top_x, 0, close=True, fill='white', stroke='black', stroke_width=2)


# --- Tall/Narrow Shapes ---

def draw_tall_pyramid(h):
    """Pyramid with base 2/3 of the height"""
    w = h * (2/3)
    # Draw from (0,0) origin - pyramid tip at (w/2, 0)
    return draw.Lines(0, h, w, h, w/2, 0, close=True, fill='white', stroke='black', stroke_width=2)


def draw_rhombus_udlr(h):
    """Rhombus with corners up, down, left, right. Width at center is 2/3 of height."""
    w = h * (2/3)
    # Draw from (0,0) origin - center at (w/2, h/2)
    cx = w / 2
    cy = h / 2
    return draw.Lines(cx, 0, w, cy, cx, h, 0, cy, close=True, fill='white', stroke='black', stroke_width=2)


def draw_stacked_circles(h):
    """Two circles stacked vertically, slightly overlapping - snowman/figure-8 shape."""
    # Calculate radius so total height = h with overlap
    # Total height: 2r (top) + 2r (bottom) - overlap = 4r - overlap
    # If overlap = 0.5r: 4r - 0.5r = 3.5r = h, so r = 2h/7
    r = (2 * h) / 7  # Each circle radius
    overlap = r * 0.5  # Overlap amount
    
    # Width is the diameter of one circle
    w = 2 * r
    
    # Centers (vertically aligned at center of width)
    cx = r  # Center x at radius (so shape spans 0 to 2r)
    top_cy = r  # Top circle center at radius from top (so top edge is at 0)
    bottom_cy = top_cy + 2*r - overlap  # Bottom circle overlaps (bottom edge at h)
    
    # Distance between centers
    d = bottom_cy - top_cy
    
    # Calculate intersection points (circles overlap vertically)
    # Intersection y is midway between centers
    mid_y = (top_cy + bottom_cy) / 2
    # Intersection x offset from center: sqrt(r² - (d/2)²)
    dx = math.sqrt(r*r - (d/2)*(d/2))
    
    left_x = cx - dx
    right_x = cx + dx
    
    # Draw figure-8 outline: top arc of upper circle + bottom arc of lower circle
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    
    # Start at left intersection point
    path.M(left_x, mid_y)
    # Arc over the top of upper circle to right intersection (large arc, sweep clockwise)
    path.A(r, r, 0, 1, 1, right_x, mid_y)
    # Arc under the bottom of lower circle back to left intersection (large arc, sweep clockwise)
    path.A(r, r, 0, 1, 1, left_x, mid_y)
    path.Z()
    
    return path


def draw_stacked_circles_custom(h):
    """Two stacked circles (small on top, large on bottom), slightly overlapping."""
    # Calculate radii so total height = h with overlap, maintaining 1.5:5 ratio
    # With ratio 1.5:5 and overlap = 0.5*upper_r:
    # upper_r = 6h/49, lower_r = 20h/49 makes total height exactly h
    upper_r = (6 * h) / 49
    lower_r = (20 * h) / 49
    
    overlap = upper_r * 0.5  # Overlap amount
    
    # Width is determined by the larger circle (lower_r)
    w = 2 * lower_r
    
    # Centers (both circles centered horizontally at lower_r)
    cx = lower_r  # Center x at larger radius
    top_cy = upper_r  # Top circle center (so top edge is at 0)
    bottom_cy = h - lower_r  # Bottom circle center (so bottom edge is at h)
    
    # For different sized circles, intersection calculation is more complex
    # Distance between centers
    d = bottom_cy - top_cy
    
    # Intersection points for two circles with different radii
    # Using formula for circle-circle intersection
    # x = (d² + r1² - r2²) / (2d) gives distance from center1 to intersection line
    a = (d*d + upper_r*upper_r - lower_r*lower_r) / (2*d)
    h_intersect = math.sqrt(upper_r*upper_r - a*a)  # Half-width at intersection
    
    # Intersection y-coordinate (from top circle center)
    intersect_y = top_cy + a
    
    left_x = cx - h_intersect
    right_x = cx + h_intersect
    
    # Draw figure-8 outline
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    
    # Start at left intersection point
    path.M(left_x, intersect_y)
    # Arc over the top of upper circle to right intersection (large arc for smaller circle)
    path.A(upper_r, upper_r, 0, 1, 1, right_x, intersect_y)
    # Arc under the bottom of lower circle back to left intersection (large arc for bigger circle)
    path.A(lower_r, lower_r, 0, 1, 1, left_x, intersect_y)
    path.Z()
    
    return path
    return group


def draw_upright_pill(h):
    """Pill standing upright, height 6 units, circumference 4 units."""
    width = 10 / math.pi
    w = h * (width / 6)
    return draw.Rectangle(0, 0, w, h, rx=w/2, ry=w/2, fill='white', stroke='black', stroke_width=2)


# --- New Custom Shapes ---

def draw_flat_pyramid_sockel(h):
    """Flat pyramid with a rectangular base (sockel) that is 1/5 of total height."""
    w = h * 4.0  # Same width ratio as flat_pyramid
    sockel_h = h / 5
    pyramid_h = h - sockel_h
    
    # Draw as single path to avoid internal line
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    # Start at bottom-left, go clockwise
    path.M(0, h)  # Bottom left
    path.L(w, h)  # Bottom right
    path.L(w, pyramid_h)  # Right side up to pyramid base
    path.L(w/2, 0)  # Pyramid right slope to tip
    path.L(0, pyramid_h)  # Pyramid left slope down
    path.Z()  # Close back to start
    
    return path


def draw_tall_trapezoid(h):
    """Tall trapezoid similar to tall_pyramid, top is 1/3 of bottom width."""
    w = h * (2/3)  # Same width ratio as tall_pyramid
    top_w = w / 3
    left_top_x = (w - top_w) / 2
    right_top_x = left_top_x + top_w
    return draw.Lines(0, h, w, h, right_top_x, 0, left_top_x, 0, close=True, fill='white', stroke='black', stroke_width=2)

def draw_stepped_block_3(h):
    """3-layer stepped block: bottom narrowest, middle widest, top medium."""
    # Based on screenshot: bottom ~0.5w, middle ~1.0w (widest), top ~0.6w
    base_w = h * 1  # Reference width (middle layer is 1.0)
    
    # Heights: bottom ~1/5, middle ~2/5, top ~2/5
    bottom_h = h / 6
    middle_h = h * 3 / 6
    top_h = h * 2 / 6
    
    # Widths: bottom narrow
    # est, middle widest, top medium
    bottom_w = base_w * 0.7
    middle_w = base_w * 1
    top_w = base_w * 0.5
    
    # Calculate x offsets to center each layer relative to middle (widest)
    bottom_x = (middle_w - bottom_w) / 2
    top_x = (middle_w - top_w) / 2
    
    # Y positions
    y_bottom = h
    y_mid_bottom = h - bottom_h
    y_mid_top = top_h
    y_top = 0
    
    # Draw as single path to avoid internal lines
    path = draw.Path(fill='white', stroke='black', stroke_width=2)
    
    # Start from bottom-left of bottom layer (narrowest), go clockwise
    path.M(bottom_x, y_bottom)
    path.L(bottom_x + bottom_w, y_bottom)  # Bottom edge
    path.L(bottom_x + bottom_w, y_mid_bottom)  # Right side up
    path.L(middle_w, y_mid_bottom)  # Step OUT to middle layer right
    path.L(middle_w, y_mid_top)  # Middle right side up
    path.L(top_x + top_w, y_mid_top)  # Step IN to top layer right
    path.L(top_x + top_w, y_top)  # Top right side up
    path.L(top_x, y_top)  # Top edge
    path.L(top_x, y_mid_top)  # Top left side down
    path.L(0, y_mid_top)  # Step OUT to middle layer left
    path.L(0, y_mid_bottom)  # Middle left side down
    path.L(bottom_x, y_mid_bottom)  # Step IN to bottom layer left
    path.Z()
    
    return path


def draw_double_upright_pill(height):
    # Proportions: roughly 2:3 ratio based on the image
    width = height * 0.7
    half_w = width / 2
    half_h = height / 2
    
    # Radius for the rounded ends (the "bumps" on top and bottom)
    # Using width/4 creates two distinct rounded humps
    r = half_w / 2
    
    path = draw.Path(stroke='black', stroke_width=2, fill='none')

    # 1. Start at the top-left side (just below the curve) - shifted to (0,0) origin
    path.M(0, r)
    
    # 2. Top-Left Arc (Sweep 1 for outward curve)
    path.A(r, r, 0, 0, 1, half_w, r)
    
    # 3. Top-Right Arc
    path.A(r, r, 0, 0, 1, width, r)
    
    # 4. Line down the right side
    path.L(width, height - r)
    
    # 5. Bottom-Right Arc (Sweep 1 for outward curve)
    path.A(r, r, 0, 0, 1, half_w, height - r)
    
    # 6. Bottom-Left Arc
    path.A(r, r, 0, 0, 1, 0, height - r)
    
    # 7. Line up the left side back to start
    path.L(0, r)
    
    path.Z()
    return path

def draw_facing_bowls(height):
    # Proportions
    width = height * 0.7
    waist_width = width * 0.3
    half_h = height / 2
    
    # Side arc radius - higher number = flatter curve
    r_side = height * 0.8 

    path = draw.Path(stroke='black', stroke_width=2, fill='none')

    # --- START TOP LEFT - shifted to (0,0) origin ---
    path.M(0, 0)
    
    # 1. To Waist Left (Inward)
    path.A(r_side, r_side, 0, 0, 0, (width - waist_width)/2, half_h)
    
    # 2. To Bottom Left (Inward)
    path.A(r_side, r_side, 0, 0, 0, 0, height)
    
    # 3. Line to Bottom Right
    path.L(width, height)
    
    # 4. To Waist Right (Inward)
    path.A(r_side, r_side, 0, 0, 0, (width + waist_width)/2, half_h)
    
    # 5. To Top Right (Inward)
    path.A(r_side, r_side, 0, 0, 0, width, 0)
    
    # 6. Close the top
    path.L(0, 0)
    
    path.Z()
    return path

# =============================================================================
# SHAPE REGISTRY
# =============================================================================

# All available shapes mapped to their drawing functions
SHAPE_MENU = {
    "semioval": draw_wide_semioval,
    "wide_rectangle": draw_wide_rectangle,
    "capsule_pill": draw_capsule_pill,
    "tapered_trapezoid": draw_tapered_trapezoid,
    "blocky_trapezoid": draw_blocky_trapezoid,
    "stepped_block": draw_stepped_block,
    "sphere_circle": draw_sphere_circle,
    "flat_pyramid": draw_flat_pyramid,
    "flat_rectangle": draw_flat_rectangle,
    "flat_pressed_oval": draw_flat_pressed_oval,
    "flat_trapezoid": draw_flat_trapezoid,
    "tall_pyramid": draw_tall_pyramid,
    "rhombus_udlr": draw_rhombus_udlr,
    "stacked_circles": draw_stacked_circles,
    "stacked_circles_custom": draw_stacked_circles_custom,
    "upright_pill": draw_upright_pill,
    "flat_pyramid_sockel": draw_flat_pyramid_sockel,
    "tall_trapezoid": draw_tall_trapezoid,
    "stepped_block_3": draw_stepped_block_3,
    "double_upright_pill": draw_double_upright_pill,
    "facing_bowls": draw_facing_bowls,
}

# Width ratios for each shape (width = height * ratio)
SHAPE_WIDTH_RATIOS = {
    "semioval": 2.5,
    "wide_rectangle": 2.2,
    "capsule_pill": 2.5,
    "tapered_trapezoid": 2.5,
    "blocky_trapezoid": 2.0,
    "stepped_block": 2.2,
    "sphere_circle": 1.0,
    "flat_pyramid": 4.0,
    "flat_rectangle": 6.0,
    "flat_pressed_oval": 4.0,
    "flat_trapezoid": 4.0,
    "tall_pyramid": 2/3,
    "rhombus_udlr": 2/3,
    "stacked_circles": 4/7,  # 2*r where r = 2h/7
    "stacked_circles_custom": 40/49,  # 2*lower_r where lower_r = 20h/49
    "upright_pill": 10/(math.pi * 6),
    "flat_pyramid_sockel": 4.0,
    "tall_trapezoid": 2/3,
    "stepped_block_3": 1.0,
    "double_upright_pill": 2/3,
    "facing_bowls": 0.7,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_shape(name: str, height: float):
    """
    Get a shape element by name.
    
    Args:
        name: Shape name from SHAPE_MENU
        height: Height of the shape
        
    Returns:
        drawsvg element or None if shape not found
    """
    if name not in SHAPE_MENU:
        print(f"Warning: Shape '{name}' not found in SHAPE_MENU")
        return None
    return SHAPE_MENU[name](height)


def get_shape_width(name: str, height: float) -> float:
    """
    Calculate the width of a shape given its height.
    
    Args:
        name: Shape name from SHAPE_MENU
        height: Height of the shape
        
    Returns:
        Width of the shape
    """
    ratio = SHAPE_WIDTH_RATIOS.get(name, 2.5)
    return height * ratio


def list_shapes() -> list:
    """Return a list of all available shape names."""
    return list(SHAPE_MENU.keys())


def register_shape(name: str, draw_func, width_ratio: float):
    """
    Register a new shape dynamically.
    
    Args:
        name: Unique name for the shape
        draw_func: Function that takes height and returns a drawsvg element
        width_ratio: Width = height * width_ratio
        
    Example:
        def draw_my_shape(h):
            return draw.Circle(h/2, h/2, h/2, fill='white', stroke='black', stroke_width=2)
        
        register_shape("my_shape", draw_my_shape, 1.0)
    """
    SHAPE_MENU[name] = draw_func
    SHAPE_WIDTH_RATIOS[name] = width_ratio
    print(f"Registered shape: {name}")


# =============================================================================
# GRID VISUALIZATION / TESTING
# =============================================================================

def generate_shape_catalog(
    output_path: str = None,
    cell_width: int = 200,
    cell_height: int = 150,
    columns: int = 4,
    shape_height: int = 80,
    padding: int = 20,
    font_size: int = 14
):
    """
    Generate a grid visualization of all shapes with labels.
    Useful for testing and documentation.
    
    Args:
        output_path: Path to save the output files (SVG and PNG)
        cell_width: Width of each grid cell
        cell_height: Height of each grid cell
        columns: Number of columns in the grid
        shape_height: Height to render each shape
        padding: Padding inside each cell
        font_size: Font size for labels
        
    Returns:
        str: Path to the generated PNG file
    """
    shapes = list_shapes()
    num_shapes = len(shapes)
    rows = math.ceil(num_shapes / columns)
    
    # Calculate canvas size
    canvas_width = columns * cell_width
    canvas_height = rows * cell_height + 60  # Extra space for title
    
    # Create drawing
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    d.append(draw.Rectangle(0, 0, canvas_width, canvas_height, fill='#f5f5f5'))
    
    # Add title
    d.append(draw.Text(
        f"Shape Catalog ({num_shapes} shapes)",
        24, canvas_width/2, 35,
        text_anchor='middle',
        font_family='sans-serif',
        font_weight='bold',
        fill='#333'
    ))
    
    # Draw grid of shapes
    for idx, shape_name in enumerate(shapes):
        row = idx // columns
        col = idx % columns
        
        # Cell position
        cell_x = col * cell_width
        cell_y = row * cell_height + 60  # Offset for title
        
        # Draw cell background
        d.append(draw.Rectangle(
            cell_x + 2, cell_y + 2,
            cell_width - 4, cell_height - 4,
            fill='white',
            stroke='#ddd',
            stroke_width=1,
            rx=5, ry=5
        ))
        
        # Add centerlines for alignment reference
        # Vertical centerline
        center_x = cell_x + cell_width / 2
        shape_area_height = cell_height - 30  # Reserve space for label
        d.append(draw.Line(
            center_x, cell_y + 2,
            center_x, cell_y + shape_area_height,
            stroke='#e0e0e0',
            stroke_width=1,
            stroke_dasharray='3,3'
        ))
        # Horizontal centerline
        center_y = cell_y + shape_area_height / 2
        d.append(draw.Line(
            cell_x + 2, center_y,
            cell_x + cell_width - 2, center_y,
            stroke='#e0e0e0',
            stroke_width=1,
            stroke_dasharray='3,3'
        ))
        
        # Get shape dimensions
        width_ratio = SHAPE_WIDTH_RATIOS.get(shape_name, 2.5)
        shape_width = shape_height * width_ratio
        
        # Scale down if shape is too wide for cell
        max_shape_width = cell_width - 2 * padding
        if shape_width > max_shape_width:
            scale = max_shape_width / shape_width
            actual_height = shape_height * scale
        else:
            scale = 1.0
            actual_height = shape_height
        
        actual_width = actual_height * width_ratio
        
        # Center shape in cell (leave room for label at bottom)
        shape_area_height = cell_height - 30  # Reserve space for label
        offset_x = cell_x + (cell_width - actual_width) / 2
        offset_y = cell_y + (shape_area_height - actual_height) / 2
        
        # Create and add shape
        group = draw.Group(transform=f'translate({offset_x}, {offset_y})')
        try:
            shape = SHAPE_MENU[shape_name](actual_height)
            group.append(shape)
            d.append(group)
        except Exception as e:
            # Draw error placeholder
            d.append(draw.Text(
                "ERROR",
                12, cell_x + cell_width/2, cell_y + shape_area_height/2,
                text_anchor='middle',
                fill='red'
            ))
            print(f"Error drawing {shape_name}: {e}")
        
        # Add label
        d.append(draw.Text(
            shape_name,
            font_size,
            cell_x + cell_width/2,
            cell_y + cell_height - 10,
            text_anchor='middle',
            font_family='monospace',
            fill='#555'
        ))
    
    # Default output path
    if output_path is None:
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / 'shape_catalog.png')
    
    # Save SVG
    svg_path = str(Path(output_path).with_suffix('.svg'))
    try:
        d.save_svg(svg_path)
        print(f"Generated SVG catalog: {svg_path}")
    except Exception as e:
        print(f"Error saving SVG: {e}")
    
    # Save PNG
    try:
        d.save_png(output_path)
        print(f"Generated PNG catalog: {output_path}")
    except Exception as e:
        print(f"Error converting to PNG: {e}")
        print("Note: Install 'cairosvg' for PNG export: pip install cairosvg")
    
    return output_path


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Shape library for figurine generation")
    parser.add_argument("--catalog", "-c", action="store_true", 
                        help="Generate a catalog of all shapes")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output path for the catalog")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all available shapes")
    parser.add_argument("--columns", type=int, default=4,
                        help="Number of columns in catalog grid (default: 4)")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available shapes:")
        for name in list_shapes():
            ratio = SHAPE_WIDTH_RATIOS.get(name, 2.5)
            print(f"  - {name} (width ratio: {ratio:.2f})")
    elif args.catalog:
        generate_shape_catalog(output_path=args.output, columns=args.columns)
    else:
        parser.print_help()
