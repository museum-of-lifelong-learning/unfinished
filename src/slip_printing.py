import logging
import random
from printer import ThermalPrinter
from receipt_template import ReceiptData, ReceiptRenderer
from content_generation import generate_content_with_ollama
from figure_generation import generate_random_figurine

logger = logging.getLogger(__name__)

def print_full_receipt(printer: ThermalPrinter, figurine_id: int, model_name: str = 'qwen2.5:3b'):
    """Generate and print the full receipt."""
    logger.info(f"[RECEIPT] Generating receipt for #{figurine_id}")
    
    figurine_path = generate_random_figurine(figurine_id)
    content = generate_content_with_ollama(figurine_id, model_name=model_name)
    
    quotes = [
        ("Der Weg ist das Ziel.", "Konfuzius"),
        ("Sei du selbst die Veränderung.", "Mahatma Gandhi"),
        ("Courage, dear heart!", "C.S. Lewis"),
    ]
    quote, author = random.choice(quotes)
    
    receipt_data = ReceiptData(
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
    
    renderer = ReceiptRenderer()
    renderer.render_to_printer(printer.printer, receipt_data)
