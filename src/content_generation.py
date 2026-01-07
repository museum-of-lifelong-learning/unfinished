import time
import logging
import ollama
from typing import List, Dict
from data_service import DataService, get_prevalent_mindset

logger = logging.getLogger(__name__)

OLLAMA_MODEL = 'qwen2.5:3b'

def generate_content_with_ollama(answers: List[Dict], data_service: DataService, model_name: str = OLLAMA_MODEL) -> dict:
    """
    Generate personalized two-paragraph content using Ollama based on user answers.
    
    Args:
        answers: List of answer dictionaries from the user's tag selection
        data_service: DataService instance to access the prompt template
        model_name: Ollama model to use for generation
        
    Returns:
        Dictionary with 'paragraph1' and 'paragraph2' keys containing the generated text
    """
    logger.info(f"[OLLAMA] Starting content generation using model {model_name}...")
    start_time = time.time()
    
    try:
        # Get the prompt template from data service
        prompt_template = data_service.get_prompt()
        
        if not prompt_template:
            logger.error("[OLLAMA] Failed to load prompt template")
            raise ValueError("Prompt template not available")
        
        # Extract relevant information from answers
        mindset = get_prevalent_mindset(answers)
        need = None  # F05 - Bedürfnisse
        context = None  # F06 - Situation
        
        for answer in answers:
            frage_id = answer.get('Frage_ID')
            antwort = answer.get('Antwort')
            
            if frage_id == 'F05':
                need = antwort
            elif frage_id == 'F06':
                context = antwort
        
        # Build the complete prompt with user data
        user_input = f"""
<Mindset>: {mindset if mindset else 'Nicht definiert'}
<Need>: {need if need else 'Nicht definiert'}
<Context>: {context if context else 'Nicht definiert'}
"""
        
        full_prompt = f"""{prompt_template}

{user_input}

Generiere jetzt die beiden Absätze (jeweils max. 400 Zeichen):"""
        
        logger.info(f"[OLLAMA] User data - Mindset: {mindset}, Need: {need}, Context: {context}")
        logger.info("[OLLAMA] Sending request to Ollama API...")
        
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': full_prompt}],
            options={
                'temperature': 0.8,
                'num_predict': 512,
                'top_k': 40,
                'top_p': 0.9,
                'num_ctx': 8192,
            }
        )
        
        elapsed = time.time() - start_time
        logger.info(f"[OLLAMA] Response received in {elapsed:.2f} seconds")
        
        content = response['message']['content'].strip()
        
        # Split into paragraphs (assuming Ollama returns two distinct paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Ensure we have exactly 2 paragraphs, use fallback if needed
        if len(paragraphs) >= 2:
            paragraph1 = paragraphs[0]
            paragraph2 = paragraphs[1]
        elif len(paragraphs) == 1:
            # Try splitting by single newline if double newline didn't work
            parts = [p.strip() for p in paragraphs[0].split('\n') if p.strip()]
            if len(parts) >= 2:
                paragraph1 = parts[0]
                paragraph2 = ' '.join(parts[1:])
            else:
                paragraph1 = paragraphs[0]
                paragraph2 = "Das hier ist für dich:"
        else:
            logger.warning("[OLLAMA] No valid paragraphs in response, using fallback")
            paragraph1 = "Du bringst Bewegung in Räume. Dein Blick macht Wandel möglich."
            paragraph2 = "Vielleicht ist da was für dich dabei."
        
        logger.info(f"[OLLAMA] Generated paragraph 1: {len(paragraph1)} chars")
        logger.info(f"[OLLAMA] Generated paragraph 2: {len(paragraph2)} chars")
        
        return {
            'paragraph1': paragraph1,
            'paragraph2': paragraph2
        }
        
    except Exception as e:
        logger.error(f"[OLLAMA] Failed to generate content: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return fallback content
        return {
            'paragraph1': "Du bringst Bewegung in Räume, in denen andere noch zögern. Dein neugieriger Blick macht Wandel möglich.",
            'paragraph2': "Der Wunsch nach Klarheit ist ein guter Anfang – er verbindet dich mit vielen, die gerade Neues erfinden. Das hier ist für dich:"
        }
