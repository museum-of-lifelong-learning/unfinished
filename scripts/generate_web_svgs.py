#!/usr/bin/env python3
"""
Generate individual SVG files for all 27,000 figurines for the website.
Each SVG contains just the figurine stack without labels or extra padding.

This script uses DataService to read shape mappings directly from Excel,
ensuring consistency between the web SVGs and the figurine service.

Usage:
    python generate_web_svgs.py                    # Generate all figures
    python generate_web_svgs.py --single 12345    # Generate just figure 12345
    python generate_web_svgs.py --start 1000 --end 2000  # Generate range
    python generate_web_svgs.py --workers 8       # Use 8 parallel workers
"""
import sys
import argparse
from pathlib import Path
from multiprocessing import Pool
import time
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import drawsvg as draw
from shapes import get_shape, get_shape_width

# Visual constants for figurine rendering
TOKEN_HEIGHT_RATIOS = [1.5, 3, 1, 6, 6, 1.5]  # Height ratios for levels 1-6
FIGURINE_HEIGHT = 240  # Total height for each figurine stack

# Output configuration
OUTPUT_DIR = Path(__file__).parent / 'docs' / 'assets' / 'figures'


def get_data_service():
    """
    Get a DataService instance. Used for multiprocessing initialization.
    Returns a new instance each time (for process safety).
    """
    from data_service import DataService
    return DataService()


# Module-level cache for single-process use
_data_service = None


def get_cached_data_service():
    """Get or create a cached DataService instance for single-process use."""
    global _data_service
    if _data_service is None:
        _data_service = get_data_service()
    return _data_service


def id_to_shapes(figure_id: int, data_service=None) -> Optional[List[str]]:
    """
    Convert a figure ID to its shape combination using DataService.
    
    Args:
        figure_id: ID from 1 to total_unique_ids
        data_service: Optional DataService instance (creates one if not provided)
        
    Returns:
        List of 6 shape names in visual order (top to bottom),
        or None if conversion fails.
    """
    if data_service is None:
        data_service = get_cached_data_service()
    return data_service.id_to_shapes(figure_id)


def get_total_combinations(data_service=None) -> int:
    """
    Get total number of unique figure combinations.
    
    Args:
        data_service: Optional DataService instance
        
    Returns:
        Total number of unique combinations (e.g., 27000)
    """
    if data_service is None:
        data_service = get_cached_data_service()
    return data_service.get_total_unique_ids()


def generate_figurine_svg(shapes: List[str]) -> str:
    """
    Generate SVG content for a figurine with the given shapes.
    
    Args:
        shapes: List of 6 shape names in visual order (top to bottom)
        
    Returns:
        SVG content as string
    """
    # Calculate individual shape heights using token_height_ratios
    total_ratio = sum(TOKEN_HEIGHT_RATIOS)
    shape_heights = [FIGURINE_HEIGHT * ratio / total_ratio for ratio in TOKEN_HEIGHT_RATIOS]
    
    # Calculate max width needed for any shape in this figurine
    max_width = 0
    for i, shape_name in enumerate(shapes):
        shape_width = get_shape_width(shape_name, shape_heights[i])
        max_width = max(max_width, shape_width)
    
    # Calculate exact content dimensions
    total_height = sum(shape_heights)
    content_width = max_width
    
    # Add minimal padding
    padding = 2
    view_width = content_width + 2 * padding
    view_height = total_height + 2 * padding
    
    # Create drawing with tight viewBox
    d = draw.Drawing(
        view_width, view_height,
        origin=(0, 0)
    )
    d.set_pixel_scale(1)
    
    # Draw shapes from top to bottom (level 1 at top, level 6 at bottom)
    current_y = padding
    for i, shape_name in enumerate(shapes):
        target_height = shape_heights[i]
        shape_element = get_shape(shape_name, target_height)
        shape_width = get_shape_width(shape_name, target_height)
        
        # Center horizontally
        shape_x = (view_width - shape_width) / 2
        
        # Create a group for this shape and position it
        shape_group = draw.Group(transform=f"translate({shape_x}, {current_y})")
        shape_group.append(shape_element)
        d.append(shape_group)
        
        current_y += target_height
    
    # Generate minimal SVG string
    return d.as_svg()


def generate_figurine_svg_by_id(figure_id: int, data_service=None) -> Optional[str]:
    """
    Generate SVG content for a figurine by its ID.
    
    Args:
        figure_id: Figure ID (1 to total_combinations)
        data_service: Optional DataService instance
        
    Returns:
        SVG content as string, or None if ID is invalid
    """
    shapes = id_to_shapes(figure_id, data_service)
    if shapes is None:
        return None
    return generate_figurine_svg(shapes)


def save_figurine_svg(figure_id: int, output_dir: Path = OUTPUT_DIR, data_service=None) -> Optional[str]:
    """
    Generate and save a single figurine SVG file.
    
    Args:
        figure_id: Figure ID (1 to total_combinations)
        output_dir: Directory to save the SVG file
        data_service: Optional DataService instance
        
    Returns:
        Path to saved file, or None if generation failed
    """
    # Generate SVG content
    svg_content = generate_figurine_svg_by_id(figure_id, data_service)
    if svg_content is None:
        return None
    
    # Create filename with zero-padded ID
    filename = f"figure-{figure_id:05d}.svg"
    filepath = output_dir / filename
    
    # Write file
    with open(filepath, 'w') as f:
        f.write(svg_content)
    
    return str(filepath)


# Global cache for multiprocessing worker initialization
_worker_shapes_cache = None
_worker_answers_per_question = None


def _init_worker(shapes_by_question, answers_per_question):
    """Initialize worker process with pre-loaded shape data."""
    global _worker_shapes_cache, _worker_answers_per_question
    _worker_shapes_cache = shapes_by_question
    _worker_answers_per_question = answers_per_question


def _id_to_shapes_cached(figure_id: int) -> Optional[List[str]]:
    """Convert figure ID to shapes using cached data (for workers)."""
    global _worker_shapes_cache, _worker_answers_per_question
    
    total = 1
    for count in _worker_answers_per_question:
        total *= count
    
    if figure_id < 1 or figure_id > total:
        return None
    
    # Convert to 0-indexed
    id_value = figure_id - 1
    
    # Decode using mixed-radix system
    question_indices = [0] * 6
    for i in range(5, -1, -1):
        question_indices[i] = id_value % _worker_answers_per_question[i]
        id_value //= _worker_answers_per_question[i]
    
    # Convert to shapes in visual order (top=F06 to bottom=F01)
    shapes = []
    for level in range(1, 7):
        question_idx = 6 - level
        question_key = f'F{question_idx + 1:02d}'
        shape_idx = question_indices[question_idx]
        shapes.append(_worker_shapes_cache[question_key][shape_idx])
    
    return shapes


# Worker function for multiprocessing
def _worker_generate(args):
    """Worker function for multiprocessing."""
    figure_id, output_dir = args
    try:
        # Use cached shapes instead of loading Excel each time
        shapes = _id_to_shapes_cached(figure_id)
        if shapes is None:
            return (figure_id, False, "Invalid figure ID")
        
        svg_content = generate_figurine_svg(shapes)
        
        # Save to file
        filename = f"figure-{figure_id:05d}.svg"
        filepath = Path(output_dir) / filename
        with open(filepath, 'w') as f:
            f.write(svg_content)
        
        return (figure_id, True, None)
    except Exception as e:
        return (figure_id, False, str(e))


def generate_range(start_id: int, end_id: int, num_workers: int = 4, output_dir: Path = OUTPUT_DIR):
    """
    Generate SVG files for a range of figure IDs using multiprocessing.
    
    Args:
        start_id: Starting figure ID (inclusive)
        end_id: Ending figure ID (inclusive)
        num_workers: Number of parallel workers
        output_dir: Directory to save SVG files
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total = end_id - start_id + 1
    print(f"Generating {total} SVG files (#{start_id:05d} to #{end_id:05d})")
    print(f"Output directory: {output_dir}")
    print(f"Using {num_workers} workers")
    print()
    
    # Pre-load shape data from DataService for all workers
    ds = get_cached_data_service()
    shapes_by_question = ds.get_shapes_by_question()
    answers_per_question = ds.get_answers_per_question()
    
    # Prepare arguments for workers
    work_items = [(i, output_dir) for i in range(start_id, end_id + 1)]
    
    start_time = time.time()
    completed = 0
    errors = []
    
    # Use multiprocessing pool with initializer to share shape data
    with Pool(
        processes=num_workers,
        initializer=_init_worker,
        initargs=(shapes_by_question, answers_per_question)
    ) as pool:
        for result in pool.imap_unordered(_worker_generate, work_items, chunksize=50):
            figure_id, success, error = result
            completed += 1
            
            if not success:
                errors.append((figure_id, error))
            
            # Progress report every 100 figures
            if completed % 100 == 0 or completed == total:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                print(f"Progress: {completed:,}/{total:,} ({100*completed/total:.1f}%) "
                      f"- {rate:.1f} fig/s - ETA: {eta:.0f}s")
    
    # Final summary
    elapsed = time.time() - start_time
    print()
    print(f"Completed in {elapsed:.1f} seconds")
    print(f"Generated {completed - len(errors):,} files successfully")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for figure_id, error in errors[:10]:  # Show first 10 errors
            print(f"  Figure #{figure_id:05d}: {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")


def main():
    parser = argparse.ArgumentParser(
        description="Generate individual SVG files for all figurines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_web_svgs.py                    # Generate all figures
    python generate_web_svgs.py --single 12345    # Generate just figure 12345
    python generate_web_svgs.py --start 1000 --end 2000  # Generate range
    python generate_web_svgs.py --workers 8       # Use 8 parallel workers
        """
    )
    
    # Get total combinations from DataService
    ds = get_cached_data_service()
    total_combinations = ds.get_total_unique_ids()
    
    parser.add_argument(
        '--start', type=int, default=1,
        help='Start from this figure ID (default: 1)'
    )
    parser.add_argument(
        '--end', type=int, default=total_combinations,
        help=f'End at this figure ID (default: {total_combinations})'
    )
    parser.add_argument(
        '--single', type=int, default=None,
        help='Generate just one figure with this ID'
    )
    parser.add_argument(
        '--workers', type=int, default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    
    args = parser.parse_args()
    
    # Determine output directory
    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    
    # Validate arguments
    if args.single is not None:
        if args.single < 1 or args.single > total_combinations:
            print(f"Error: --single must be between 1 and {total_combinations}")
            sys.exit(1)
        
        # Generate single figure
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Generating figure #{args.single:05d}...")
        filepath = save_figurine_svg(args.single, output_dir, ds)
        if filepath:
            print(f"Saved: {filepath}")
            
            # Also print the shape combination
            shapes = id_to_shapes(args.single, ds)
            print(f"\nShape combination:")
            for i, shape in enumerate(shapes, 1):
                print(f"  Level {i}: {shape}")
        else:
            print(f"Error: Failed to generate figure #{args.single}")
            sys.exit(1)
    else:
        # Validate range
        if args.start < 1:
            print("Error: --start must be at least 1")
            sys.exit(1)
        if args.end > total_combinations:
            print(f"Error: --end must be at most {total_combinations}")
            sys.exit(1)
        if args.start > args.end:
            print("Error: --start must be less than or equal to --end")
            sys.exit(1)
        if args.workers < 1:
            print("Error: --workers must be at least 1")
            sys.exit(1)
        
        # Generate range
        generate_range(args.start, args.end, args.workers, output_dir)


if __name__ == "__main__":
    main()
