"""Test all 3 AI providers with real API keys from .env"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from config import settings

print("=== API KEY SANITY CHECK ===")
print(f"GROQ key loaded: {'YES ('+settings.groq_api_key[:8]+'...)' if settings.groq_api_key and settings.groq_api_key != 'YOUR_NEW_GROQ_KEY' else 'MISSING/PLACEHOLDER'}")
print(f"GEMINI key loaded: {'YES ('+settings.gemini_api_key[:8]+'...)' if settings.gemini_api_key and settings.gemini_api_key != 'YOUR_NEW_GEMINI_KEY' else 'MISSING/PLACEHOLDER'}")
print(f"HF key loaded: {'YES ('+settings.hf_api_key[:8]+'...)' if settings.hf_api_key and settings.hf_api_key != 'YOUR_NEW_HF_KEY' else 'MISSING/PLACEHOLDER'}")
print()

# Test Groq
print("=== TESTING GROQ ===")
try:
    import httpx
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "Reply with just the word: OK"}], "max_tokens": 5}
    r = httpx.post(url, headers=headers, json=data, timeout=10.0)
    print(f"Groq HTTP {r.status_code}: {r.json().get('choices', [{}])[0].get('message', {}).get('content', r.text[:100])}")
except Exception as e:
    print(f"Groq FAILED: {e}")

# Test Gemini
print("\n=== TESTING GEMINI ===")
try:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Reply with just the word: OK")
    print(f"Gemini OK: {response.text.strip()}")
except Exception as e:
    print(f"Gemini FAILED: {e}")
