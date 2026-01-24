"""
Slip Data Generation Module
Generates all data needed for receipt printing including figurine images, 
titles, and personalized content.
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any

from content_generation import generate_content_with_gemini
from generate_figurine import generate_figurine
from data_service import DataService, get_prevalent_mindset

logger = logging.getLogger(__name__)

load_dotenv()

def generate_slip_data(
    figurine_id: int,
    answers: list,
    data_service: DataService,
    model_name: str = 'gemini-2.5-flash'
) -> Dict[str, Any]:
    """
    Generate all data needed for receipt printing.
    
    Args:
        figurine_id: The unique ID for this figurine
        answers: List of answer dictionaries from RFID tags
        data_service: DataService instance for resource lookups
        model_name: AI model to use for content generation
        
    Returns:
        Dictionary containing all generated data:
        - figurine_id: int
        - figurine_path: str (path to generated image)
        - title_text: str (two-line title)
        - content: dict (paragraph1, paragraph2 from AI)
        - resources: dict (tool, location, program recommendations)
        - total_unique_ids: int
        - mindset: str (prevalent mindset from answers)
        - qr_url: str
    """
    logger.info(f"[DATA_GEN] Generating slip data for #{figurine_id}")
    
    slip_data = {
        'figurine_id': figurine_id,
        'total_unique_ids': data_service.get_total_unique_ids() if data_service else 27000,
        'qr_url': f"https://figurati.ch/${figurine_id}"
    }
    
    # Extract SVG list and mindset from answers
    svg_list = []
    mindset = None
    
    if answers:
        for ans in answers:
            svg_val = ans.get('svg')
            if svg_val and isinstance(svg_val, str):
                svg_list.append(svg_val)
        
        mindset = get_prevalent_mindset(answers)
        logger.info(f"[DATA_GEN] Prevalent Mindset: {mindset}")
    
    slip_data['mindset'] = mindset
    
    # Generate title text
    title_text = _generate_title(data_service, mindset)
    slip_data['title_text'] = title_text
    
    # Generate figurine image
    figurine_path = _generate_figurine_image(
        svg_list,
        figurine_id,
        title_text
    )
    slip_data['figurine_path'] = figurine_path
    
    # Generate personalized content with AI
    content = generate_content_with_gemini(
        answers,
        data_service=data_service,
        figurine_id=figurine_id,
        model_name=model_name
    )
    slip_data['content'] = content
    
    # Generate resource recommendations
    resources = _generate_resource_recommendations(data_service, answers)
    slip_data['resources'] = resources
    
    logger.info(f"[DATA_GEN] Slip data generation complete for #{figurine_id}")
    return slip_data


def _generate_title(data_service: Optional[DataService], mindset: Optional[str]) -> Optional[str]:
    """Generate a two-line title from word lists."""
    if not data_service:
        return None
    
    word1 = data_service.get_random_title_word('primo')
    # Use mindset if available, otherwise fallback
    category2 = mindset if mindset else 'Explorer'
    word2 = data_service.get_random_title_word(category2)
    
    if word1 and word2 and word1 != "Unknown" and word2 != "Unknown":
        title_text = f"{word1}\n{word2}"
        logger.info(f"[DATA_GEN] Generated Title: {title_text.replace(chr(10), ' ')}")
        return title_text
    
    return None


def _generate_figurine_image(
    svg_list: list,
    figurine_id: int,
    title_text: Optional[str]
) -> Optional[str]:
    """Generate the figurine image and return its path."""
    figurine_output_dir = os.getenv('FIGURINE_OUTPUT_DIR')
    if not figurine_output_dir:
        figurine_output_dir = str(Path(__file__).parent.parent / 'output')
    
    figurine_path = generate_figurine(
        svg_list,
        output_path=str(Path(figurine_output_dir) / f'figurine_{figurine_id}.png'),
        title_text=title_text,
        figurine_id=figurine_id
    )
    
    logger.info(f"[DATA_GEN] Figurine image generated: {figurine_path}")
    return figurine_path


def _generate_resource_recommendations(
    data_service: Optional[DataService],
    answers: list
) -> Dict[str, Any]:
    """
    Generate resource recommendations for all categories.
    Includes both item text and optional link for each resource.
    """
    if not data_service:
        return {
            'tool': 'No recommendations available',
            'tool_link': None,
            'location': 'No recommendations available',
            'location_link': None,
            'program': 'No recommendations available',
            'program_link': None
        }
    
    categories = {
        'tool': "Tools & Inspiration",
        'location': "Anlaufstellen & Angebote",
        'program': "Programm-Empfehlung"
    }
    
    resources = {}
    for key, category in categories.items():
        resource_recommendation = data_service.find_best_resource(
            kategorie=category,
            answers=answers
        )
        resources[key] = resource_recommendation.get('Item', f'No {category} available')
        # Also get the link if it exists in the resource data
        link = resource_recommendation.get('Link') or resource_recommendation.get('link')
        # Check if link is valid (not NaN or empty)
        if link and isinstance(link, str) and link.strip():
            resources[f'{key}_link'] = link.strip()
        else:
            resources[f'{key}_link'] = None
        logger.info(f"[DATA_GEN] {category}: {resources[key][:50]}... (link: {resources.get(f'{key}_link', 'None')})")
    
    return resources
