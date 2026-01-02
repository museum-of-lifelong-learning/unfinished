from typing import List
import random

def calculate_figurine_id(digits: List[int]) -> int:
    """
    Convert 6-digit base-6 input to decimal ID.
    Each digit can be 1-6, converting to 0-5 for base-6 calculation.
    Returns value from 1 to 46656 (6^6).
    """
    if len(digits) != 6:
        raise ValueError("Must provide exactly 6 digits")
    
    if not all(1 <= d <= 6 for d in digits):
        raise ValueError("All digits must be between 1 and 6")
    
    # Convert to base-6 (0-5)
    base6_digits = [d - 1 for d in digits]
    
    # Calculate decimal value
    result = 0
    for i, digit in enumerate(base6_digits):
        result += digit * (6 ** (5 - i))
    
    # Return 1-indexed (1 to 46656 instead of 0 to 46655)
    return result + 1

def tags_to_digits(tags: List[dict]) -> List[int]:
    """
    Convert 6 RFID tags to 6 digits (1-6).
    Uses the last byte of the EPC to generate a digit.
    """
    digits = []
    # Sort tags by EPC to ensure deterministic order for the same set of tags
    sorted_tags = sorted(tags, key=lambda x: x['epc'])
    
    for tag in sorted_tags:
        # Get last byte of EPC (hex string)
        epc = tag['epc']
        try:
            last_byte = int(epc[-2:], 16)
            digit = (last_byte % 6) + 1
            digits.append(digit)
        except:
            digits.append(random.randint(1, 6))
            
    return digits
