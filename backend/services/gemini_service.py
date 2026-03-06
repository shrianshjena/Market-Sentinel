import json
import re
import time

from google import genai
from google.genai import types

from config import settings
from models.schemas import HistoricalPoint
from typing import List

# Model priority list - tries each in order if rate-limited
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]

_client = None


def _get_client():
    global _client
    if _client is None:
        if not settings.google_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


def analyze_stock(
    ticker: str,
    current_price: float,
    price_history: List[HistoricalPoint],
) -> dict:
    """
    Send ticker context and price data to Gemini 2.0 Flash with Google Search
    Grounding enabled. Returns structured analysis as a dict.
    """
    prices = [p.close for p in price_history]
    if not prices:
        return _fallback_analysis()

    price_start = prices[0]
    price_end = prices[-1]
    pct_change = ((price_end - price_start) / price_start * 100) if price_start else 0
    price_min = min(prices)
    price_max = max(prices)
    last_5 = prices[-5:] if len(prices) >= 5 else prices

    prompt = f"""You are a Senior Equity Research Analyst specializing in Indian markets (NSE/BSE).

Analyze the stock {ticker} listed on NSE based on the following data:

HISTORICAL DATA (90-day window):
- Current Price: INR {current_price:.2f}
- 90-day Price Range: INR {price_min:.2f} to INR {price_max:.2f}
- 90-day Return: {pct_change:+.2f}%
- Recent 5-day prices: {[round(p, 2) for p in last_5]}
- Total data points: {len(prices)}

Using your grounded web search, find the latest financial news and market sentiment for {ticker} on NSE India.

Provide your analysis in the following STRICT JSON format (no markdown, no extra text):
{{
  "trend_summary": "2-3 sentence analysis of the 90-day price trend. Is it in recovery, consolidation, or downtrend?",
  "headline_impact": "2-3 sentences on the most impactful recent news headlines for this stock and how they affect the outlook.",
  "sentiment_consistency": "1-2 sentences on whether market sentiment is consistently bullish, bearish, or mixed.",
  "recommendation": "One clear recommendation sentence (e.g., 'High Confidence' or 'Hold with caution')."
}}

IMPORTANT: Respond ONLY with the JSON object. No markdown code fences, no explanatory text."""

    client = _get_client()

    # Try each model in priority order; retry once on rate limit
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                    ),
                )
                return _parse_response(response.text)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    if attempt == 0:
                        time.sleep(5)
                        continue
                    print(f"Rate limited on {model_name}, trying next model...")
                    break
                else:
                    print(f"Gemini API error ({model_name}): {e}")
                    return _fallback_analysis()

    print("All Gemini models rate-limited")
    return _fallback_analysis()


def _parse_response(text: str) -> dict:
    """Parse Gemini's response text into a dict, handling various formats."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return _fallback_analysis()


def _fallback_analysis() -> dict:
    """Return a neutral fallback if Gemini fails."""
    return {
        "trend_summary": "Unable to retrieve trend analysis at this time. The Intelligence Engine is recalibrating.",
        "headline_impact": "No recent headlines could be analyzed. Please try again shortly.",
        "sentiment_consistency": "Sentiment data unavailable.",
        "recommendation": "Insufficient data for a recommendation. Please retry.",
    }
