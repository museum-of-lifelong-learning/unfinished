"""
Slip Data Generation Module
Generates all data needed for receipt printing including figurine images, 
titles, and personalized content.
"""

import logging
import os
import csv
import socket
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any

from content_generation import generate_content_with_gemini
from generate_figurine import generate_figurine
from data_service import DataService, get_prevalent_mindset

logger = logging.getLogger(__name__)

load_dotenv()

# Path to fallback CSV data
FALLBACK_CSV_PATH = Path(__file__).parent.parent / 'assets' / 'slip_content_fallback.csv'


def check_internet_connection() -> bool:
    """Check if internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def load_fallback_data_by_mindset(mindset: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Load fallback slip data from CSV based on mindset.
    
    Args:
        mindset: The prevalent mindset (Explorer, Experiencer, Sensemaker, Strategist)
        
    Returns:
        Dictionary with fallback content or None if not found
    """
    if not FALLBACK_CSV_PATH.exists():
        logger.error(f"[FALLBACK] CSV file not found: {FALLBACK_CSV_PATH}")
        return None
    
    # Default to Explorer if no mindset provided
    target_mindset = mindset if mindset else 'Explorer'
    
    try:
        with open(FALLBACK_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('mindset', '').strip() == target_mindset:
                    logger.info(f"[FALLBACK] Found fallback data for mindset: {target_mindset}")
                    return {
                        'data_id': row.get('data_id', ''),
                        'title': row.get('title', ''),
                        'paragraph1': row.get('paragraph1', ''),
                        'paragraph2': row.get('paragraph2', ''),
                        'resource_tools_inspiration': row.get('resource_tools_inspiration', ''),
                        'resource_anlaufstellen': row.get('resource_anlaufstellen', ''),
                        'resource_programm': row.get('resource_programm', '')
                    }
        
        # If target mindset not found, fall back to first row (Explorer)
        logger.warning(f"[FALLBACK] Mindset '{target_mindset}' not found, using first available")
        with open(FALLBACK_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if row:
                return {
                    'data_id': row.get('data_id', ''),
                    'title': row.get('title', ''),
                    'paragraph1': row.get('paragraph1', ''),
                    'paragraph2': row.get('paragraph2', ''),
                    'resource_tools_inspiration': row.get('resource_tools_inspiration', ''),
                    'resource_anlaufstellen': row.get('resource_anlaufstellen', ''),
                    'resource_programm': row.get('resource_programm', '')
                }
    except Exception as e:
        logger.error(f"[FALLBACK] Error loading fallback CSV: {e}")
    
    return None

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
        - offline_mode: bool (True if using fallback data)
        - data_id: str (from fallback CSV when offline)
    """
    logger.info(f"[DATA_GEN] Generating slip data for #{figurine_id}")
    
    # Extract SVG list and mindset from answers first (needed for both modes)
    svg_list = []
    mindset = None
    
    if answers:
        for ans in answers:
            svg_val = ans.get('svg')
            if svg_val and isinstance(svg_val, str):
                svg_list.append(svg_val)
        
        mindset = get_prevalent_mindset(answers)
        logger.info(f"[DATA_GEN] Prevalent Mindset: {mindset}")
    
    # Check internet connection
    has_internet = check_internet_connection()
    
    if not has_internet:
        logger.warning("[DATA_GEN] No internet connection - using offline fallback mode")
        return _generate_offline_slip_data(figurine_id, mindset, svg_list, data_service)
    
    # Online mode: generate content with AI
    slip_data = {
        'figurine_id': figurine_id,
        'total_unique_ids': data_service.get_total_unique_ids() if data_service else 27000,
        'qr_url': f"https://figurati.ch/${figurine_id}",
        'offline_mode': False
    }
    
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


def _generate_offline_slip_data(
    figurine_id: int,
    mindset: Optional[str],
    svg_list: list,
    data_service: Optional[DataService]
) -> Dict[str, Any]:
    """
    Generate slip data using offline fallback CSV data.
    
    Args:
        figurine_id: The unique ID for this figurine (from user's answers)
        mindset: The prevalent mindset from answers
        svg_list: List of SVG names for figurine generation
        data_service: DataService instance (may be None)
        
    Returns:
        Dictionary containing slip data from fallback CSV
    """
    logger.info(f"[OFFLINE] Generating offline slip data for #{figurine_id} with mindset: {mindset}")
    
    # Load fallback data from CSV based on mindset
    fallback = load_fallback_data_by_mindset(mindset)
    
    if not fallback:
        logger.error("[OFFLINE] Failed to load any fallback data")
        # Last resort fallback
        fallback = {
            'data_id': '4a1ba226-14f6-4b13-89d7-30251d388290',  # Explorer default
            'title': 'Hochgradig resilient',
            'paragraph1': 'Dein neugieriger Blick macht Wandel möglich.',
            'paragraph2': 'Der Wunsch nach Klarheit verbindet dich mit vielen.',
            'resource_tools_inspiration': '',
            'resource_anlaufstellen': '',
            'resource_programm': ''
        }
    
    # Use data_id from CSV (data is already in cloud)
    data_id = fallback.get('data_id', '')
    
    # Build QR URL using the data_id from CSV and user's figure_id
    base_url = "https://museum-of-lifelong-learning.github.io/unfinished/"
    qr_url = f"{base_url}?data_id={data_id}&figure_id={figurine_id}"
    
    slip_data = {
        'figurine_id': figurine_id,
        'total_unique_ids': data_service.get_total_unique_ids() if data_service else 27000,
        'qr_url': qr_url,
        'offline_mode': True,
        'data_id': data_id,
        'mindset': mindset,
        'title_text': fallback.get('title', ''),
        'content': {
            'paragraph1': fallback.get('paragraph1', ''),
            'paragraph2': fallback.get('paragraph2', '')
        },
        'resources': {
            'tool': fallback.get('resource_tools_inspiration', ''),
            'tool_link': None,  # Links already embedded in CSV content as HTML
            'location': fallback.get('resource_anlaufstellen', ''),
            'location_link': None,
            'program': fallback.get('resource_programm', ''),
            'program_link': None
        }
    }
    
    # Still generate figurine image (works offline)
    figurine_path = _generate_figurine_image(
        svg_list,
        figurine_id,
        slip_data['title_text']
    )
    slip_data['figurine_path'] = figurine_path
    
    logger.info(f"[OFFLINE] Slip data generated with data_id: {data_id}")
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
