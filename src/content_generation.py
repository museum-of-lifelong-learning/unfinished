import time
import logging
import ollama

logger = logging.getLogger(__name__)

OLLAMA_MODEL = 'qwen2.5:3b'

def generate_content_with_ollama(figurine_id: int, model_name: str = OLLAMA_MODEL) -> dict:
    """
    Generate complete receipt content using Ollama.
    Returns dict with all fields for the receipt.
    """
    logger.info(f"[OLLAMA] Starting content generation for figurine {figurine_id} using model {model_name}...")
    start_time = time.time()
    
    try:
        # Optimized prompt for faster generation
        prompt = f"""Erstelle einen kurzen, inspirierenden deutschen Text für Figurine #{figurine_id}.

Format (genau diese Struktur):
BESCHREIBUNG: [2-3 kurze Sätze über Persönlichkeit und Stärken]
FRAGE: [Eine tiefgründige Frage]
CHANCE: [Ein informeller Vorschlag]
ANGEBOT: [Ein offizielles Angebot/Programm]
INSPIRATION: [Buch, Film oder Zitat]
SCHRITT: [Konkreter nächster Schritt]

Kurz und prägnant!"""

        logger.info("[OLLAMA] Sending request to Ollama API...")
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.7,
                'num_predict': 150,
                'top_k': 20,
                'top_p': 0.8,
                'num_ctx': 512,
            }
        )
        
        elapsed = time.time() - start_time
        logger.info(f"[OLLAMA] Response received in {elapsed:.2f} seconds")
        
        content = response['message']['content'].strip()
        
        # Parse the response
        lines = content.split('\n')
        parsed = {
            'description': '',
            'question': '',
            'opportunity': '',
            'offer': '',
            'inspiration': '',
            'step': ''
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('BESCHREIBUNG:'):
                parsed['description'] = line.replace('BESCHREIBUNG:', '').strip()
            elif line.startswith('FRAGE:'):
                parsed['question'] = line.replace('FRAGE:', '').strip()
            elif line.startswith('CHANCE:'):
                parsed['opportunity'] = line.replace('CHANCE:', '').strip()
            elif line.startswith('ANGEBOT:'):
                parsed['offer'] = line.replace('ANGEBOT:', '').strip()
            elif line.startswith('INSPIRATION:'):
                parsed['inspiration'] = line.replace('INSPIRATION:', '').strip()
            elif line.startswith('SCHRITT:'):
                parsed['step'] = line.replace('SCHRITT:', '').strip()
        
        # Fill defaults
        if not parsed['description']: parsed['description'] = "Du bist einzigartig."
        if not parsed['question']: parsed['question'] = "Was ist dein Ziel?"
        if not parsed['opportunity']: parsed['opportunity'] = "Sprich mit Freunden."
        if not parsed['offer']: parsed['offer'] = "Besuche figurati.ch"
        if not parsed['inspiration']: parsed['inspiration'] = "Carpe Diem"
        if not parsed['step']: parsed['step'] = "Atme tief durch."
        
        return parsed
        
    except Exception as e:
        logger.error(f"[OLLAMA] Failed to generate content: {e}")
        return {
            'description': "Die Zukunft gehört denen, die an ihre Träume glauben.",
            'question': "Was ist dein nächster Schritt?",
            'opportunity': "Teile deine Vision.",
            'offer': "Beratung bei figurati.ch",
            'inspiration': "Der Alchemist",
            'step': "Sei dankbar."
        }
