import logging
import os
import textwrap
from PIL import Image
from content_generation import generate_content_with_ollama
from generate_figurine import generate_figurine
from data_service import DataService, get_prevalent_mindset

logger = logging.getLogger(__name__)

# Paper width for TM-T88V/TM-T70II profile (80mm paper, 512px at 180dpi)
PAPER_WIDTH_PX = 512
CHAR_WIDTH = 42  # Approximate characters per line for standard font

def print_scaled_image(image_path: str, printer) -> Image.Image:
    """
    Load and resize image to fit paper width.
    Maintains aspect ratio without cropping height.
    """
    img = Image.open(image_path).convert('RGB')
    
    # Resize to paper width while maintaining aspect ratio
    if img.width != PAPER_WIDTH_PX:
        ratio = PAPER_WIDTH_PX / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((PAPER_WIDTH_PX, new_height), Image.Resampling.LANCZOS)
    
    printer.image(img)
    
def print_labeled_section(printer, label: str, text: str):
    """Print a section with a bold label followed by normal text."""
    printer.set(align='left', bold=True)
    printer.text(f"{label} ")
    printer.set(bold=False)
    
    # First line includes label, subsequent lines are full width
    words = text.split()
    first_line = []
    remaining_words = []
    first_line_width = CHAR_WIDTH - len(label) - 1
    
    # Build first line
    current_length = 0
    for i, word in enumerate(words):
        test_length = current_length + len(word) + (1 if current_length > 0 else 0)
        if test_length <= first_line_width:
            first_line.append(word)
            current_length = test_length
        else:
            remaining_words = words[i:]
            break
    
    # Print first line (already on same line as label)
    printer.textln(' '.join(first_line))
    
    # Print remaining lines with full width
    if remaining_words:
        remaining_text = ' '.join(remaining_words)
        wrapped = textwrap.fill(remaining_text, width=CHAR_WIDTH)
        printer.textln(wrapped)


def create_full_receipt(printer, figurine_id: int, answers: list, data_service: DataService, model_name: str = 'qwen2.5:3b'):
    """Generate and print the full receipt directly to the printer."""
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
    if data_service:
        word1 = data_service.get_random_title_word('primo')
        # Use mindset if available, otherwise fallback (e.g. random or default)
        category2 = mindset if mindset else 'Explorer'
        word2 = data_service.get_random_title_word(category2)
        
        if word1 and word2 and word1 != "Unknown" and word2 != "Unknown":
            title_text = f"{word1}\n{word2}."
            logger.info(f"Generated Title: {title_text.replace(chr(10), ' ')}")
    
    # Generate figurine
    figurine_path = generate_figurine(svg_list, title_text=title_text, figurine_id=figurine_id)
    
    # Generate personalized content with Ollama
    content = generate_content_with_ollama(answers, data_service=data_service, model_name=model_name)
    
    # === HEADER: Image ===
    if figurine_path and os.path.exists(figurine_path):
        print_scaled_image(figurine_path, printer)
    printer.ln()
    
    # Figurine number
    printer.set(align='center')
    printer.textln(f"Charakter {figurine_id} / {data_service.get_total_unique_ids()}")
    printer.ln()
    
    
    # === BODY ===
    printer.set(align='left', bold=False)
    
    # Body paragraphs - two personalized paragraphs from Ollama
    if content.get('paragraph1'):
        wrapped = textwrap.fill(content['paragraph1'], width=CHAR_WIDTH)
        printer.textln(wrapped)
        printer.ln()
    
    if content.get('paragraph2'):
        wrapped = textwrap.fill(content['paragraph2'], width=CHAR_WIDTH)
        printer.textln(wrapped)
        printer.ln()
    
    # Labeled sections (bold labels)
    categories = ["Tools & Inspiration", "Anlaufstellen & Angebote", "Programm-Empfehlung"]
    
    for category in categories:
        resource_recommendation = data_service.find_best_resource(
            kategorie=category,
            answers=answers
        )
        print_labeled_section(printer, f"{category}:", resource_recommendation.get('Item'))    
        printer.ln()
    
    
    # === QR CODE ===
    qr_url = f"https://figurati.ch/${figurine_id}"
    printer.set(align='center')
    printer.qr(qr_url, size=6)
    printer.ln()
    
    
    # === FOOTER ===
    printer.set(align='center')
    
    printer.textln("Bleib unfertig.")
    printer.textln("Vielen Dank für deinen Besuch.")    
    printer.ln()
    
    printer.set(align='center', bold=True)
    printer.textln("Unfinished by Design –")
    printer.textln("The Museum of Lifelong Learning")
    printer.ln()
    
    printer.cut()
