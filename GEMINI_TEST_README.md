# Gemini API Testing Guide

## Quick Test

Run the comprehensive test script:

```bash
./test_gemini_api.py
# or
python test_gemini_api.py
```

## What the Test Checks

1. **Environment Variables** - Validates API key and model configuration from `.env`
2. **Library Import** - Ensures `google.genai` is installed correctly
3. **Client Initialization** - Tests API key authentication
4. **Simple API Call** - Makes a basic request to verify connectivity
5. **Full Function Test** - Tests the complete `generate_content_with_gemini()` function with sample data
6. **Rate Limiter** - Shows current rate limit status

## Expected Output

```
============================================================
GEMINI API TEST
============================================================

[1/5] Checking environment variables...
   ✓ API key found: AIzaSy...
   ✓ Model: gemini-2.5-flash

[2/5] Testing Gemini library import...
   ✓ google.genai imported successfully

[3/5] Initializing Gemini client...
   ✓ Client initialized successfully

[4/5] Testing simple API call...
   ✓ API call successful!
   Response: Hello from Gemini!

[5/5] Testing generate_content_with_gemini function...
   ✓ Content generation successful!
   
============================================================
ALL TESTS PASSED! ✓
============================================================
```

## Troubleshooting

### API Key Not Configured
- Edit `.env` file and add your API key: `GEMINI_API_KEY=your_key_here`
- Get key from: https://aistudio.google.com/app/apikey

### Import Error
```bash
pip install google-genai python-dotenv
```

### 404 Model Not Found
- Check `.env` file has correct model: `GEMINI_MODEL=gemini-2.5-flash`
- Run `python list_gemini_models.py` to see available models

### 503 Service Unavailable
- Normal - retry logic will handle it automatically
- API may be temporarily overloaded

## Available Models (as of Jan 2026)

- `gemini-2.5-flash` (recommended - fast, cheap)
- `gemini-2.5-pro` (higher quality, slower)
- `gemini-flash-latest` (always latest flash version)

## Rate Limits (Free Tier)

- **15 requests per minute**
- **1500 requests per day**
- Rate limit state persisted in `/tmp/gemini_rate_limit.json`

## Files

- `test_gemini_api.py` - Main test script
- `list_gemini_models.py` - List all available models
- `.env` - Your API configuration (not in git)
- `.env.example` - Template for configuration
