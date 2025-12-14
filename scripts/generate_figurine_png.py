#!/usr/bin/env python3
"""
Generate PNG images with geometric shapes similar to figurine stacking.
Creates 6 shapes stacked vertically, randomly chosen from a pool of 20 shapes.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import random


def draw_small_circle(draw, center_x, y_top, line_width, target_height=None):
    """Small circle"""
    if target_height:
        r = target_height // 2
    else:
        r = 30
    y_center = y_top + r
    draw.ellipse([center_x - r, y_center - r, center_x + r, y_center + r], 
                 outline='black', width=line_width)
    return y_center + r  # Return bottom y position


def draw_large_circle(draw, center_x, y_top, line_width, target_height=None):
    """Large circle"""
    if target_height:
        r = target_height // 2
    else:
        r = 80
    y_center = y_top + r
    draw.ellipse([center_x - r, y_center - r, center_x + r, y_center + r], 
                 outline='black', width=line_width)
    return y_center + r


def draw_trapezoid_wide(draw, center_x, y_top, line_width, target_height=None):
    """Trapezoid wider at top"""
    height = target_height if target_height else 60
    trap_top = int(height * 2.3)
    trap_bottom = int(height * 1.7)
    points = [
        (center_x - trap_top//2, y_top),
        (center_x + trap_top//2, y_top),
        (center_x + trap_bottom//2, y_top + height),
        (center_x - trap_bottom//2, y_top + height)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_trapezoid_narrow(draw, center_x, y_top, line_width, target_height=None):
    """Trapezoid wider at bottom"""
    height = target_height if target_height else 60
    trap_top = int(height * 1.7)
    trap_bottom = int(height * 2.3)
    points = [
        (center_x - trap_top//2, y_top),
        (center_x + trap_top//2, y_top),
        (center_x + trap_bottom//2, y_top + height),
        (center_x - trap_bottom//2, y_top + height)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_diamond(draw, center_x, y_top, line_width, target_height=None):
    """Diamond"""
    size = (target_height // 2) if target_height else 70
    y_center = y_top + size
    points = [
        (center_x, y_top),
        (center_x + size, y_center),
        (center_x, y_center + size),
        (center_x - size, y_center)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_center + size


def draw_triangle_up(draw, center_x, y_top, line_width, target_height=None):
    """Triangle pointing up"""
    height = target_height if target_height else 80
    width = int(height * 1.5)
    points = [
        (center_x, y_top),
        (center_x - width//2, y_top + height),
        (center_x + width//2, y_top + height)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_triangle_down(draw, center_x, y_top, line_width, target_height=None):
    """Triangle pointing down"""
    height = target_height if target_height else 80
    width = int(height * 1.5)
    points = [
        (center_x, y_top + height),
        (center_x - width//2, y_top),
        (center_x + width//2, y_top)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_square(draw, center_x, y_top, line_width, target_height=None):
    """Square"""
    size = target_height if target_height else 90
    draw.rectangle([center_x - size//2, y_top,
                    center_x + size//2, y_top + size],
                   outline='black', width=line_width)
    return y_top + size


def draw_rectangle_tall(draw, center_x, y_top, line_width, target_height=None):
    """Tall rectangle"""
    height = target_height if target_height else 100
    width = int(height * 0.6)
    draw.rectangle([center_x - width//2, y_top,
                    center_x + width//2, y_top + height],
                   outline='black', width=line_width)
    return y_top + height


def draw_rectangle_wide(draw, center_x, y_top, line_width, target_height=None):
    """Wide rectangle"""
    height = target_height if target_height else 50
    width = int(height * 2.6)
    draw.rectangle([center_x - width//2, y_top,
                    center_x + width//2, y_top + height],
                   outline='black', width=line_width)
    return y_top + height


def draw_hexagon(draw, center_x, y_top, line_width, target_height=None):
    """Hexagon"""
    height = target_height if target_height else 100
    width = int(height * 0.6)
    points = [
        (center_x, y_top),
        (center_x + width//2, y_top + height//4),
        (center_x + width//2, y_top + 3*height//4),
        (center_x, y_top + height),
        (center_x - width//2, y_top + 3*height//4),
        (center_x - width//2, y_top + height//4)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_pentagon(draw, center_x, y_top, line_width, target_height=None):
    """Pentagon"""
    height = target_height if target_height else 90
    size = int(height * 0.56)
    points = [
        (center_x, y_top),
        (center_x + size, y_top + height//3),
        (center_x + size//2, y_top + height),
        (center_x - size//2, y_top + height),
        (center_x - size, y_top + height//3)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + height


def draw_oval_horizontal(draw, center_x, y_top, line_width, target_height=None):
    """Horizontal oval"""
    height = target_height if target_height else 60
    width = int(height * 1.67)
    draw.ellipse([center_x - width//2, y_top,
                  center_x + width//2, y_top + height],
                 outline='black', width=line_width)
    return y_top + height


def draw_oval_vertical(draw, center_x, y_top, line_width, target_height=None):
    """Vertical oval"""
    height = target_height if target_height else 120
    width = int(height * 0.5)
    draw.ellipse([center_x - width//2, y_top,
                  center_x + width//2, y_top + height],
                 outline='black', width=line_width)
    return y_top + height


def draw_star(draw, center_x, y_top, line_width, target_height=None):
    """Star"""
    size = (target_height // 2) if target_height else 45
    y_center = y_top + size
    points = []
    import math
    for i in range(10):
        angle = math.pi/2 + i * 2 * math.pi / 10
        r = size if i % 2 == 0 else size // 2
        x = center_x + r * math.cos(angle)
        y = y_center + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, outline='black', width=line_width)
    return y_center + size


def draw_cross(draw, center_x, y_top, line_width, target_height=None):
    """Cross shape"""
    size = target_height if target_height else 90
    bar_width = size // 3
    # Vertical bar
    draw.rectangle([center_x - bar_width//2, y_top,
                    center_x + bar_width//2, y_top + size],
                   outline='black', width=line_width)
    # Horizontal bar
    y_center = y_top + size//2
    draw.rectangle([center_x - size//2, y_center - bar_width//2,
                    center_x + size//2, y_center + bar_width//2],
                   outline='black', width=line_width)
    return y_top + size


def draw_arrow_up(draw, center_x, y_top, line_width, target_height=None):
    """Arrow pointing up"""
    height = target_height if target_height else 100
    width = int(height * 0.8)
    shaft_width = int(height * 0.3)
    # Arrow head (triangle)
    head_height = int(height * 0.4)
    points_head = [
        (center_x, y_top),
        (center_x - width//2, y_top + head_height),
        (center_x + width//2, y_top + head_height)
    ]
    draw.polygon(points_head, outline='black', width=line_width)
    # Arrow shaft
    draw.rectangle([center_x - shaft_width//2, y_top + head_height,
                    center_x + shaft_width//2, y_top + height],
                   outline='black', width=line_width)
    return y_top + height


def draw_arrow_down(draw, center_x, y_top, line_width, target_height=None):
    """Arrow pointing down"""
    height = target_height if target_height else 100
    width = int(height * 0.8)
    shaft_width = int(height * 0.3)
    # Arrow shaft
    shaft_height = int(height * 0.6)
    draw.rectangle([center_x - shaft_width//2, y_top,
                    center_x + shaft_width//2, y_top + shaft_height],
                   outline='black', width=line_width)
    # Arrow head (triangle)
    points_head = [
        (center_x, y_top + height),
        (center_x - width//2, y_top + shaft_height),
        (center_x + width//2, y_top + shaft_height)
    ]
    draw.polygon(points_head, outline='black', width=line_width)
    return y_top + height


def draw_house(draw, center_x, y_top, line_width, target_height=None):
    """House shape"""
    total_height = target_height if target_height else 110
    width = int(total_height * 0.91)
    roof_height = int(total_height * 0.45)
    house_height = total_height - roof_height
    # Roof (triangle)
    points_roof = [
        (center_x, y_top),
        (center_x - width//2, y_top + roof_height),
        (center_x + width//2, y_top + roof_height)
    ]
    draw.polygon(points_roof, outline='black', width=line_width)
    # House body (rectangle)
    draw.rectangle([center_x - width//2, y_top + roof_height,
                    center_x + width//2, y_top + roof_height + house_height],
                   outline='black', width=line_width)
    return y_top + roof_height + house_height


def draw_heart(draw, center_x, y_top, line_width, target_height=None):
    """Heart shape"""
    size = (target_height // 2) if target_height else 45
    # Simplified heart using circles and triangle
    y_center = y_top + size//2
    # Left circle
    draw.ellipse([center_x - size, y_center - size//2,
                  center_x, y_center + size//2],
                 outline='black', width=line_width)
    # Right circle
    draw.ellipse([center_x, y_center - size//2,
                  center_x + size, y_center + size//2],
                 outline='black', width=line_width)
    # Bottom triangle
    points = [
        (center_x, y_top + 2*size),
        (center_x - size + 10, y_center),
        (center_x + size - 10, y_center)
    ]
    draw.polygon(points, outline='black', width=line_width)
    return y_top + 2*size


# List of all shape drawing functions
SHAPE_FUNCTIONS = [
    draw_small_circle,
    draw_large_circle,
 
    draw_trapezoid_narrow,
    draw_diamond,
    draw_triangle_up,
    draw_triangle_down,
    draw_square,
    draw_rectangle_tall,
   
    draw_hexagon,
    draw_pentagon,
    draw_oval_horizontal,
    draw_oval_vertical,
]


def generate_figurine_png(output_path: str, max_width: int = 400, max_height: int = 600):
    """
    Generate a PNG with 6 geometric shapes stacked vertically.
    Shapes are randomly chosen from a pool of 20 different shapes.
    Height ratios are [1.5, 3, 1, 6, 6, 1.5] from top to bottom.
    
    Args:
        output_path: Path to save the PNG file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
    """
    # Create white canvas
    img = Image.new('RGB', (max_width, max_height), 'white')
    draw = ImageDraw.Draw(img)
    
    center_x = max_width // 2
    line_width = 6
    shapes_count = 6
    
    # Height ratios for each shape position (top to bottom)
    height_ratios = [1.5, 3, 1, 6, 6, 1.5]
    total_ratio = sum(height_ratios)
    
    # Calculate actual heights for each position
    target_heights = [int(max_height * ratio / total_ratio) for ratio in height_ratios]
    
    # Randomly select 6 shapes
    selected_shapes = random.sample(SHAPE_FUNCTIONS, shapes_count)
    
    # Draw shapes stacked vertically with specified height constraints
    current_y = 0
    for i, shape_func in enumerate(selected_shapes):
        target_height = target_heights[i]
        # Draw shape with target height and get its bottom position
        shape_bottom = shape_func(draw, center_x, current_y, line_width, target_height)
        # Next shape starts where this one ends
        current_y = shape_bottom
    
    # Save PNG
    img.save(output_path)
    print(f"Generated PNG: {output_path}")


def main():
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'assets'
    output_dir.mkdir(exist_ok=True)
    
    # Generate the figurine PNG
    output_path = output_dir / 'figurine_generated.png'
    generate_figurine_png(str(output_path), max_width=400, max_height=600)
    
    print("Done! Use this PNG for header images without overlay text.")


if __name__ == "__main__":
    main()
