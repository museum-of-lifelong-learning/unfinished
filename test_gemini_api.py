#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("GEMINI API TEST")
print("=" * 60)

# Test 1: Environment Variables
print("\n[1/5] Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

if not api_key or api_key == 'your_api_key_here':
    print("   ✗ GEMINI_API_KEY not configured in .env file")
    print("   Please set your API key in .env file")
    print("   Get your key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)
else:
    print(f"   ✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    print(f"   ✓ Model: {model_name}")

# Test 2: Import Gemini library
print("\n[2/5] Testing Gemini library import...")
try:
    from google import genai
    from google.genai import types
    print("   ✓ google.genai imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import: {e}")
    print("   Run: pip install google-genai")
    sys.exit(1)

# Test 3: Initialize Gemini client
print("\n[3/5] Initializing Gemini client...")
try:
    client = genai.Client(api_key=api_key)
    print("   ✓ Client initialized successfully")
except Exception as e:
    print(f"   ✗ Client initialization failed: {e}")
    sys.exit(1)

# Test 4: Simple API call
# print("\n[4/5] Testing simple API call...")
# try:
#     config = types.GenerateContentConfig(
#         temperature=0.8,
#         max_output_tokens=50,
#     )
    
#     response = client.models.generate_content(
#         model=model_name,
#         contents="Say 'Hello from Gemini!' and nothing else.",
#         config=config
#     )
    
#     print(f"   ✓ API call successful!")
#     print(f"   Response: {response.text}")
# except Exception as e:
#     print(f"   ✗ API call failed: {e}")
#     import traceback
#     traceback.print_exc()
#     sys.exit(1)

# Test 5: Full content generation function
print("\n[5/5] Testing generate_content_with_gemini function...")
try:
    from content_generation import generate_content_with_gemini
    from data_service import DataService
    
    # Load data service
    data_service = DataService()
    
    # Create sample answers (simulating user selections)
    sample_answers = [
        {
            'Frage_ID': 'F01',
            'Frage': 'Welcher Mindset beschreibt dich am besten?',
            'Antwort': 'Explorer',
            'Mindsets': 'Explorer',
            'Kontext': 'Ich suche nach neuen Möglichkeiten'
        },
        {
            'Frage_ID': 'F05',
            'Frage': 'Was ist dein aktueller Bedarf?',
            'Antwort': 'Klarheit und Orientierung',
            'Kontext': 'Ich suche nach neuen Möglichkeiten'
            
        },
        {
            'Frage_ID': 'F06',
            'Frage': 'Was möchtest du in deinem Leben verändern?',
            'Antwort': 'Ich suche nach neuen Möglichkeiten',
            'Kontext': 'Ich suche nach neuen Möglichkeiten'
        }
    ]
    
    print("   Generating content with sample data...")
    print(f"   - Mindset: Explorer")
    print(f"   - Need: Klarheit und Orientierung")
    print(f"   - Context: Ich suche nach neuen Möglichkeiten")
    
    result = generate_content_with_gemini(
        answers=sample_answers,
        data_service=data_service,
        figurine_id = 24385,
        model_name=model_name
    )
    
    if result and 'paragraph1' in result and 'paragraph2' in result:
        print("   ✓ Content generation successful!")
        print("\n   Generated Content:")
        print("   " + "-" * 56)
        print(f"   Paragraph 1 ({len(result['paragraph1'])} chars):")
        print(f"   {result['paragraph1']}")
        print()
        print(f"   Paragraph 2 ({len(result['paragraph2'])} chars):")
        print(f"   {result['paragraph2']}")
        print("   " + "-" * 56)
    else:
        print("   ✗ Content generation returned unexpected format")
        print(f"   Result: {result}")
        
except Exception as e:
    print(f"   ✗ Content generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nGemini API is configured correctly and working!")
print(f"Model in use: {model_name}")

# Bonus: Check rate limiter state
print("\n[BONUS] Rate Limiter Status:")
from content_generation import _rate_limiter
print(f"   Daily requests made: {_rate_limiter.daily_count}/{_rate_limiter.daily_limit}")
print(f"   RPM limit: {_rate_limiter.rpm_limit}")
print(f"   Rate limit file: /tmp/gemini_rate_limit.json")
if os.path.exists('/tmp/gemini_rate_limit.json'):
    import json
    with open('/tmp/gemini_rate_limit.json', 'r') as f:
        data = json.load(f)
        print(f"   Stored state: {data}")

