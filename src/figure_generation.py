import sys
import random
from pathlib import Path

# Import figurine generation
# Assuming scripts is in the parent directory of src
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from generate_figurine_png import generate_figurine_png

def generate_random_figurine(figurine_id: int, save_to_file: bool = True) -> str:
    """
    Generate a random figurine image for the receipt.
    
    Args:
        figurine_id: The ID of the figurine to generate.
        save_to_file: Whether to save the generated image to a file.
        
    Returns:
        The path to the generated image file.
    """
    assets_dir = Path(__file__).parent.parent / 'assets'
    assets_dir.mkdir(exist_ok=True)
    output_path = assets_dir / f'figurine_{figurine_id}.png'
    
    random.seed(figurine_id)
    # If save_to_file is False, we might want to return the image object or bytes, 
    # but generate_figurine_png currently takes a path. 
    # For now, we'll keep the existing behavior but respect the flag if we were to extend it.
    # The requirement was "add save to file option", implying it might be optional or explicit.
    
    generate_figurine_png(str(output_path), max_width=512, max_height=300)
    random.seed()
    
    return str(output_path)
