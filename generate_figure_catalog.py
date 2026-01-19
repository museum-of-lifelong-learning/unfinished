#!/usr/bin/env python3
"""
Generate a catalog of all possible figurine combinations.
Creates a large canvas with figures arranged in a grid.
Canvas aspect ratio is 1:√2 (A-series paper format).
"""
import sys
import math
import argparse
import itertools
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import drawsvg as draw
from shapes import get_shape, get_shape_width

# Level-specific shape assignments (same as test_all_shapes.py)
LEVEL_SHAPES = {
    1: ["capsule_pill", "semioval", "flat_pyramid_sockel", "stepped_block", "wide_rectangle"],
    2: ["sphere_circle","sphere_circle","sphere_circle","sphere_circle","sphere_circle","sphere_circle"],
    3: ["flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle","flat_rectangle"],
    4: ["stepped_block_3", "stacked_circles_custom", "rhombus_udlr", "tall_trapezoid", "facing_bowls"],
    5: ["tall_pyramid", "rhombus_udlr", "stacked_circles",  "double_upright_pill","stacked_circles"],
    6: ["semioval","wide_rectangle", "capsule_pill", "flat_pyramid", "wide_rectangle", "flat_trapezoid"]
}

# Visual constants
# Height ratios for each element (same as generate_figurine.py)
TOKEN_HEIGHT_RATIOS = [1.5, 3, 1, 6, 6, 1.5]
FIGURINE_HEIGHT = 120  # Total height for each figurine stack
CELL_PADDING = 20  # Padding around each figure in its cell
LABEL_HEIGHT = 20  # Height reserved for number label
LABEL_FONT_SIZE = 12


def get_answers_per_question():
    """Get the number of answer options per level."""
    return [len(LEVEL_SHAPES[i]) for i in range(1, 7)]


def get_total_combinations():
    """Calculate total number of unique combinations."""
    counts = get_answers_per_question()
    total = 1
    for count in counts:
        total *= count
    return total


def id_to_shape_combination(figure_id):
    """
    Convert a figure ID (1 to 27000) to a shape combination.
    Reverse of calculate_answer_set_id from data_service.py.
    
    Args:
        figure_id: ID from 1 to total_combinations
        
    Returns:
        List of 6 shape names (level 1 to 6, top to bottom)
    """
    if figure_id < 1 or figure_id > get_total_combinations():
        raise ValueError(f"ID must be between 1 and {get_total_combinations()}")
    
    # Convert to 0-indexed
    id_value = figure_id - 1
    
    # Get answers per question
    answers_per_question = get_answers_per_question()
    
    # Decode using mixed-radix system (reverse of encoding)
    indices = []
    for i in range(5, -1, -1):  # Right to left (level 6 to level 1)
        if i == 5:
            # Rightmost position
            indices.insert(0, id_value % answers_per_question[i])
            id_value //= answers_per_question[i]
        else:
            indices.insert(0, id_value % answers_per_question[i])
            id_value //= answers_per_question[i]
    
    # Convert indices to shapes
    shapes = []
    for level in range(1, 7):
        level_idx = level - 1
        shape_idx = indices[level_idx]
        shapes.append(LEVEL_SHAPES[level][shape_idx])
    
    return shapes


def calculate_grid_dimensions(num_figures, aspect_ratio=1/math.sqrt(2)):
    """
    Calculate optimal grid dimensions for given number of figures.
    Tries to maintain aspect_ratio (width:height) close to 1:√2.
    
    Args:
        num_figures: Total number of figures to display
        aspect_ratio: Target width/height ratio (default 1/√2 for A-series)
    
    Returns:
        (columns, rows) tuple
    """
    # Start with square root and adjust
    sqrt_n = math.sqrt(num_figures)
    
    # For 1:√2 aspect, if we have sqrt(n) rows, we need sqrt(n) * (1/√2) columns
    # But columns * rows >= num_figures
    # Let's try different configurations
    
    best_cols = int(sqrt_n)
    best_rows = int(math.ceil(num_figures / best_cols))
    best_diff = float('inf')
    
    # Try different column counts around the estimate
    for cols in range(max(1, int(sqrt_n * aspect_ratio) - 5), 
                     int(sqrt_n * aspect_ratio) + 10):
        rows = math.ceil(num_figures / cols)
        actual_ratio = cols / rows if rows > 0 else 0
        diff = abs(actual_ratio - aspect_ratio)
        
        if diff < best_diff:
            best_diff = diff
            best_cols = cols
            best_rows = rows
    
    return best_cols, best_rows


def draw_figurine_in_cell(shapes, x_offset, y_offset, cell_width, cell_height, figure_number):
    """
    Draw a single figurine in a cell with number label.
    
    Args:
        shapes: List of 6 shape names (level 1 to 6, top to bottom)
        x_offset: X position of cell
        y_offset: Y position of cell
        cell_width: Width of the cell
        cell_height: Height of the cell (includes label area)
        figure_number: Number to display below figure
    
    Returns:
        drawsvg.Group containing the figurine and label
    """
    group = draw.Group()
    
    # Calculate available height for the figure (excluding label)
    figure_height = cell_height - LABEL_HEIGHT
    
    # Calculate individual shape heights using token_height_ratios
    total_ratio = sum(TOKEN_HEIGHT_RATIOS)
    shape_heights = [FIGURINE_HEIGHT * ratio / total_ratio for ratio in TOKEN_HEIGHT_RATIOS]
    
    # Center the stack vertically in available space
    start_y = y_offset + (figure_height - FIGURINE_HEIGHT) / 2
    
    # Draw shapes from top to bottom (level 1 at top, level 6 at bottom)
    current_y = start_y
    for i, shape_name in enumerate(shapes):
        # Get the shape element
        target_height = shape_heights[i]
        shape_element = get_shape(shape_name, target_height)
        shape_width = get_shape_width(shape_name, target_height)
        
        # Center horizontally in cell
        shape_x = x_offset + (cell_width - shape_width) / 2
        
        # Create a group for this shape and position it
        shape_group = draw.Group(transform=f"translate({shape_x}, {current_y})")
        shape_group.append(shape_element)
        group.append(shape_group)
        
        current_y += target_height
    
    # Add number label below the figure (formatted as #00012)
    label_y = y_offset + figure_height + LABEL_HEIGHT / 2
    label_text = f"#{figure_number:05d}"  # Format with leading zeros, 5 digits
    label = draw.Text(
        label_text,
        LABEL_FONT_SIZE,
        x_offset + cell_width / 2,
        label_y,
        text_anchor='middle',
        dominant_baseline='middle',
        fill='black',
        font_family='Arial, sans-serif'
    )
    group.append(label)
    
    return group


def generate_all_combinations():
    """Generate all possible combinations of shapes."""
    # Get shape options for each level
    level_options = [LEVEL_SHAPES[i] for i in range(1, 7)]
    
    # Generate all combinations
    all_combinations = list(itertools.product(*level_options))
    
    return all_combinations


def generate_random_unique_ids(count, seed=None):
    """
    Generate random unique figure IDs without duplication.
    
    Args:
        count: Number of unique IDs to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of unique figure IDs
    """
    if seed is not None:
        random.seed(seed)
    
    total = get_total_combinations()
    if count > total:
        raise ValueError(f"Cannot generate {count} unique IDs from {total} total combinations")
    
    # Generate random sample without replacement
    return random.sample(range(1, total + 1), count)


def generate_catalog(num_figures=100, output_path="figure_catalog.svg", random_mode=False, seed=None):
    """
    Generate a catalog of figurine combinations.
    
    Args:
        num_figures: Number of figures to include (default 100)
        output_path: Path to save the SVG file
        random_mode: If True, generate random unique IDs; if False, sequential
        seed: Random seed for reproducibility (only used if random_mode=True)
    """
    total_available = get_total_combinations()
    
    print(f"Total possible combinations: {total_available}")
    
    # Limit to requested number
    num_figures = min(num_figures, total_available)
    
    # Generate figure IDs
    if random_mode:
        print(f"Generating {num_figures} random unique figures...")
        figure_ids = generate_random_unique_ids(num_figures, seed=seed)
        # Keep random order, don't sort
    else:
        print(f"Generating catalog with first {num_figures} figures...")
        figure_ids = list(range(1, num_figures + 1))
    
    # Convert IDs to shape combinations
    combinations = []
    for fig_id in figure_ids:
        shapes = id_to_shape_combination(fig_id)
        combinations.append((fig_id, shapes))
    
    # Calculate grid dimensions
    cols, rows = calculate_grid_dimensions(num_figures)
    print(f"Grid layout: {cols} columns × {rows} rows")
    
    # Calculate cell dimensions
    # Each cell needs to fit a figurine stack (using height ratios) plus label
    cell_height = FIGURINE_HEIGHT + LABEL_HEIGHT + CELL_PADDING * 2
    
    # Width needs to accommodate widest possible shape at its designated height
    # Calculate max width considering the token_height_ratios
    total_ratio = sum(TOKEN_HEIGHT_RATIOS)
    max_cell_width = 0
    for i, ratio in enumerate(TOKEN_HEIGHT_RATIOS):
        shape_height = FIGURINE_HEIGHT * ratio / total_ratio
        # flat_rectangle is widest at 6.0 ratio
        max_shape_width = shape_height * 6.0
        max_cell_width = max(max_cell_width, max_shape_width)
    
    cell_width = max_cell_width + CELL_PADDING * 2
    
    # Calculate canvas size
    canvas_width = cell_width * cols
    canvas_height = cell_height * rows
    
    print(f"Canvas size: {canvas_width:.0f} × {canvas_height:.0f} pixels")
    print(f"Aspect ratio: {canvas_width/canvas_height:.3f} (target: {1/math.sqrt(2):.3f})")
    
    # Create canvas
    canvas = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    canvas.append(draw.Rectangle(0, 0, canvas_width, canvas_height, fill='white'))
    
    # Draw each figure
    for idx, (fig_id, shapes) in enumerate(combinations):
        row = idx // cols
        col = idx % cols
        
        x_offset = col * cell_width + CELL_PADDING
        y_offset = row * cell_height + CELL_PADDING
        
        figure_group = draw_figurine_in_cell(
            shapes,
            x_offset,
            y_offset,
            cell_width - CELL_PADDING * 2,
            cell_height - CELL_PADDING * 2,
            fig_id  # Use the actual figure ID
        )
        canvas.append(figure_group)
        
        if (idx + 1) % 100 == 0 or idx + 1 == num_figures:
            print(f"  Progress: {idx + 1}/{num_figures} figures")
    
    # Save the SVG
    canvas.save_svg(output_path)
    print(f"\n✓ Catalog saved to: {output_path}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate a catalog of all possible figurine combinations.'
    )
    parser.add_argument(
        'count',
        type=int,
        nargs='?',
        default=100,
        help='Number of figures to generate (default: 100, max: 27000)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='figure_catalog.svg',
        help='Output SVG file path (default: figure_catalog.svg)'
    )
    parser.add_argument(
        '-r', '--random',
        action='store_true',
        help='Generate random unique figures instead of sequential'
    )
    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (only used with --random)'
    )
    
    args = parser.parse_args()
    
    # Validate count
    if args.count < 1:
        print("Error: Count must be at least 1")
        sys.exit(1)
    
    total_max = get_total_combinations()
    if args.count > total_max:
        print(f"Warning: Requested {args.count} figures, but maximum is {total_max}")
        args.count = total_max
    
    # Generate catalog
    generate_catalog(args.count, args.output, random_mode=args.random, seed=args.seed)


if __name__ == "__main__":
    main()
