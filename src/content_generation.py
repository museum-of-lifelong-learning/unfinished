import os
import time
import json
import logging
from google import genai
from google.genai import types
from typing import List, Dict
from datetime import datetime
from collections import deque
from pathlib import Path
from dotenv import load_dotenv
from data_service import DataService, get_prevalent_mindset

# Load environment variables from .env file
load_dotenv()


# Ensure logging output is visible during tests and script runs
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
GEMINI_RPM_LIMIT = int(os.getenv('GEMINI_RPM_LIMIT', '15'))
GEMINI_DAILY_LIMIT = int(os.getenv('GEMINI_DAILY_LIMIT', '1500'))

# File path for rate limit persistence
RATE_LIMIT_FILE = '/tmp/gemini_rate_limit.json'


class GeminiRateLimiter:
    """
    Rate limiter to stay within Google Gemini API free tier:
    - 15 requests per minute (RPM)
    - 1500 requests per day
    """
    
    def __init__(self, rpm_limit: int = GEMINI_RPM_LIMIT, daily_limit: int = GEMINI_DAILY_LIMIT):
        self.rpm_limit = rpm_limit
        self.daily_limit = daily_limit
        self.request_times = deque(maxlen=rpm_limit)
        self.daily_count = 0
        self.daily_date = datetime.now().date()
        
        # Load persisted state from file
        self._load_state()
    
    def _load_state(self):
        """Load daily counter from file if it exists and is from today."""
        try:
            if os.path.exists(RATE_LIMIT_FILE):
                with open(RATE_LIMIT_FILE, 'r') as f:
                    data = json.load(f)
                    file_date = datetime.fromisoformat(data.get('date', '')).date()
                    if file_date == self.daily_date:
                        self.daily_count = data.get('count', 0)
                        logger.info(f"[GEMINI] Loaded daily count: {self.daily_count}")
        except Exception as e:
            logger.warning(f"[GEMINI] Could not load rate limit state: {e}")
    
    def _save_state(self):
        """Persist daily counter to file."""
        try:
            with open(RATE_LIMIT_FILE, 'w') as f:
                json.dump({
                    'date': self.daily_date.isoformat(),
                    'count': self.daily_count
                }, f)
        except Exception as e:
            logger.warning(f"[GEMINI] Could not save rate limit state: {e}")
    
    def wait_if_needed(self) -> bool:
        """
        Check rate limits and wait if necessary.
        
        Returns:
            True if request can proceed, False if daily limit exceeded
        """
        # Check if date changed, reset counter
        current_date = datetime.now().date()
        if current_date != self.daily_date:
            self.daily_count = 0
            self.daily_date = current_date
            self._save_state()
            logger.info(f"[GEMINI] Daily counter reset for new day")
        
        # Check daily limit
        if self.daily_count >= self.daily_limit:
            logger.warning(f"[GEMINI] Daily quota exceeded ({self.daily_count}/{self.daily_limit})")
            return False
        
        # RPM limiting (sliding window)
        now = time.time()
        if len(self.request_times) >= self.rpm_limit:
            oldest = self.request_times[0]
            time_since_oldest = now - oldest
            if time_since_oldest < 60:
                sleep_time = 60 - time_since_oldest + 0.1  # Add small buffer
                logger.info(f"[GEMINI] Rate limit: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Record this request
        self.request_times.append(time.time())
        self.daily_count += 1
        self._save_state()
        
        return True


# Global rate limiter instance
_rate_limiter = GeminiRateLimiter()


def generate_content_with_gemini(answers: List[Dict], data_service: DataService, figurine_id: int, model_name: str = GEMINI_MODEL) -> dict:
    """
    Generate personalized two-paragraph content using Google Gemini API based on user answers.
    Falls back to template content if API is unavailable or rate limit is exceeded.
    
    Args:
        answers: List of answer dictionaries from the user's tag selection
        data_service: DataService instance to access the prompt template
        model_name: Gemini model to use for generation (default: gemini-1.5-flash)
        
    Returns:
        Dictionary with 'paragraph1' and 'paragraph2' keys containing the generated text
    """
    logger.info(f"[GEMINI] Starting content generation using model {model_name}...")
    start_time = time.time()
    
    # Default fallback content
    fallback_content = {
        'paragraph1': "Du bringst Bewegung in Räume, in denen andere noch zögern. Dein neugieriger Blick macht Wandel möglich.",
        'paragraph2': "Der Wunsch nach Klarheit ist ein guter Anfang – er verbindet dich mit vielen, die gerade Neues erfinden. Das hier ist für dich:"
    }

    # Prepare output directory from .env or default
    from dotenv import load_dotenv
    load_dotenv()
    output_dir_env = os.getenv('FIGURINE_OUTPUT_DIR')
    if not output_dir_env:
        output_dir_env = str(Path(__file__).parent.parent / 'output')
    output_dir = Path(output_dir_env)
    output_dir.mkdir(exist_ok=True)
    
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_api_key_here':
        logger.warning("[GEMINI] API key not configured, using fallback content")
        return fallback_content
    
    # Check rate limits
    if not _rate_limiter.wait_if_needed():
        logger.warning("[GEMINI] Daily rate limit exceeded, using fallback content")
        return fallback_content
    
    try:
        # Configure Gemini API client
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Load prompt template from file
        prompt_path = Path(__file__).parent.parent / 'assets' / 'prompt_template.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except Exception as e:
            logger.error(f"[GEMINI] Failed to load prompt template from file: {e}")
            return fallback_content

        # Extract relevant information from answers
        mindset = get_prevalent_mindset(answers)
        mindset_line = f"\nPrevalent Mindset: {mindset if mindset else 'Nicht definiert'}\n"

        # Format answers as 'Frage -> Antwort (Kontext)'
        answer_lines = []
        for ans in answers:
            frage = ans.get('frage') or ans.get('Frage') or ''
            antwort = ans.get('antwort') or ans.get('Antwort') or ''
            kontext = ans.get('kontext') or ans.get('Kontext') or ''
            line = f"{frage} -> {antwort} ({kontext})"
            answer_lines.append(line)
        answers_block = '\n'.join(answer_lines)

        # Compose the full prompt
        full_prompt = f"{prompt_template}{mindset_line}\nGeneriere jetzt die beiden Absätze (jeweils max. 400 Zeichen):\n\nAntworten:\n{answers_block}"

        logger.info(f"[GEMINI] User data - Mindset: {mindset}")
        logger.info("[GEMINI] Sending request to Gemini API...")
        
        # Configure generation parameters
        generation_config = types.GenerateContentConfig(
            temperature=0.8,
            top_p=0.9,
            top_k=40,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(
                thinking_budget=1127,
            ),
        )
        
        # Generate content with retry logic
        max_retries = 1
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=generation_config
                )
                elapsed = time.time() - start_time
                logger.info(f"[GEMINI] Response received in {elapsed:.2f} seconds")
                content = response.text.strip()
                # Split into paragraphs (assuming Gemini returns two distinct paragraphs)
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                # Ensure we have exactly 2 paragraphs
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
                    logger.warning("[GEMINI] No valid paragraphs in response, using fallback")
                    return fallback_content
                logger.info(f"[GEMINI] Generated paragraph 1: {len(paragraph1)} chars")
                logger.info(f"[GEMINI] Generated paragraph 2: {len(paragraph2)} chars")
                result = {
                    'paragraph1': paragraph1,
                    'paragraph2': paragraph2
                }
                _save_gemini_output(output_dir, figurine_id, result)
                return result
            except Exception as retry_error:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"[GEMINI] Attempt {attempt + 1} failed: {retry_error}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise on final attempt
        
    except Exception as e:
        logger.error(f"[GEMINI] Failed to generate content: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("[GEMINI] Using fallback content due to error")
        _save_gemini_output(output_dir, figurine_id, fallback_content)
        return fallback_content


# Helper to save output
def _save_gemini_output(output_dir: Path, figurine_id: int, content: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_dir / f"{figurine_id}_{ts}.json"
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        logger.info(f"[GEMINI] Output saved to {fname}")
    except Exception as e:
        logger.warning(f"[GEMINI] Could not save output: {e}")
