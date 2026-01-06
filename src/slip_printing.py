import logging
import random
from pathlib import Path
from collections import Counter
from receipt_template import ReceiptData
from content_generation import generate_content_with_ollama
from figure_generation import generate_figurine

logger = logging.getLogger(__name__)

def get_prevalent_mindset(answers):
    """Calculate the most prevalent mindset from answers."""
    all_mindsets = []
    if not answers:
        return None
    for ans in answers:
        # Check for 'Mindsets' key (case sensitive matching Excel column)
        m_str = ans.get('Mindsets')
        if m_str and isinstance(m_str, str):
            # Split by comma and strip whitespace
            parts = [m.strip() for m in m_str.split(',')]
            all_mindsets.extend(parts)
            
    if not all_mindsets:
        return None
        
    # specific logic: if multiple mindsets have same count, pick one? most_common handles it (picks first)
    counts = Counter(all_mindsets)
    if not counts:
        return None
    return counts.most_common(1)[0][0]

def create_full_receipt(figurine_id: int, answers: list = None, data_handler_obj=None, model_name: str = 'qwen2.5:3b'):
    """Generate and print the full receipt."""
    logger.info(f"[RECEIPT] Generating receipt for #{figurine_id}")
    
    svg_list = []
    mindset = None
    
    if answers:
        for ans in answers:
            svg_val = ans.get('svg')
            if svg_val and isinstance(svg_val, str):
                svg_list.append(svg_val)
        
        mindset = get_prevalent_mindset(answers)
        logger.info(f"Prevalent Mindset: {mindset}")

    # Generate Title
    title_text = None
    if data_handler_obj:
        word1 = data_handler_obj.get_random_title_word('primo')
        # Use mindset if available, otherwise fallback (e.g. random or default)
        category2 = mindset if mindset else 'Explorer'
        word2 = data_handler_obj.get_random_title_word(category2)
        
        if word1 and word2 and word1 != "Unknown" and word2 != "Unknown":
            title_text = f"{word1}\n{word2}."
            logger.info(f"Generated Title: {title_text.replace(chr(10), ' ')}")
    
    # Generate figurine
    figurine_path = generate_figurine(svg_list, title_text=title_text, figurine_id=figurine_id)
    
    content = generate_content_with_ollama(figurine_id, model_name=model_name)
    
    quotes = [
        ("Der Weg ist das Ziel.", "Konfuzius"),
        ("Sei du selbst die Veränderung.", "Mahatma Gandhi"),
        ("Courage, dear heart!", "C.S. Lewis"),
    ]
    quote, author = random.choice(quotes)
    
    return ReceiptData(
        image_path=figurine_path,
        image_overlay_text="",
        figurine_number=str(figurine_id),
        total_count="46 656",
        body_paragraphs=[content['description']],
        mighty_question=content['question'],
        informal_opportunity=content['opportunity'],
        official_offer=content['offer'],
        inspiration=content['inspiration'],
        next_step=content['step'],
        qr_url="https://figurati.ch",
        footer_quote=quote,
        footer_quote_author=author,
        footer_thanks=["Vielen Dank!", "Figurati!"]
    )
