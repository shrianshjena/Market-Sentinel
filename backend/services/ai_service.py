import json
import re
import httpx
# NOTE: No google.generativeai import — calls Gemini REST API directly via httpx to avoid grpcio (60MB)
from config import settings
from models.schemas import HistoricalPoint
from typing import List

# Primary models
GEMINI_MODEL = "gemini-1.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"


def analyze_stock(
    ticker: str,
    current_price: float,
    price_history: List[HistoricalPoint],
    news_context: List[str],
    fundamentals: dict,
) -> dict:
    """
    Generate comprehensive insights using Groq -> Hugging Face fallback.
    Injects dynamic 2026 news to ground the LLM's knowledge.
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

    news_text = "\n".join([f"- {n}" for n in news_context]) if news_context else "No recent news found."

    prompt = f"""You are a Senior Equity Research Analyst specializing in Indian markets (NSE).

CRITICAL CONTEXT: Today's date is March 19, 2026. You MUST analyze the provided Recent News Headlines (which reflect the latest 2026 data, including any recent financial performance, product launches, or partnerships) and the stock price data to formulate your insights. Do not use outdated 2024 information.

Analyze the stock {ticker} listed on NSE based on the following data:

RECENT NEWS HEADLINES (Latest 2026 Context):
{news_text}

FUNDAMENTAL VALUATION (Live Metrics from NSE):
- Sector & Industry: {fundamentals.get('sector', 'Unknown')} - {fundamentals.get('industry', 'Unknown')}
- Stock P/E Ratio: {fundamentals.get('pe_ratio', 0.0)}
- Sector Benchmark P/E: {fundamentals.get('sector_pe', 0.0)} (NSE sector average)
- P/B Ratio: {fundamentals.get('pb_ratio', 0.0)}
(CRITICAL: Evaluate the stock P/E strictly relative to the Sector Benchmark P/E above. A stock trading at a premium/discount to its sector P/E has important valuation implications. Use P/B to assess whether the market values the stock above or below its book value.)

HISTORICAL PRICE DATA (5-year window):
- Current Price: INR {current_price:.2f}
- 5-Year Price Range: INR {price_min:.2f} to INR {price_max:.2f}
- 5-Year Return: {pct_change:+.2f}%
- Recent 5-day prices: {[round(p, 2) for p in last_5]}
- Total data points: {len(prices)}

Provide your analysis in the following STRICT JSON format (no markdown code blocks, no explanatory text, return ONLY valid json):

{{
  "company_details": "1-2 sentences on what the company does and its sector position.",
  "overall_context": "2-3 sentences on the broader market conditions or macroeconomic factors impacting this stock.",
  "fundamental_analysis": "1-2 sentences contextualizing the stock's fundamental financial metrics (P/E, P/B, ROE) relative to its sector peers.",
  "trend_summary": "2-3 sentence analysis of the 5-year price trend. Is it in recovery, consolidation, or downtrend?",
  "headline_impact": "2-3 sentences analyzing the provided RECENT NEWS HEADLINES and how they affect the stock outlook.",
  "market_sentiment": "1-2 sentences detailing how institutional and retail investors are perceiving the stock based on the news.",
  "sentiment_consistency": "1-2 sentences on whether market sentiment is consistently bullish, bearish, or mixed.",
  "recommendation": "One clear recommendation sentence (e.g., 'High Confidence Buy' or 'Hold with caution')."
}}

IMPORTANT: Respond ONLY with the JSON object. Do not include introductory text, markdown code blocks, or explanations."""

    last_error = "No API keys configured."

    # 1. Primary: Groq
    try:
        if settings.groq_api_key:
             return _call_groq(prompt)
    except Exception as e:
        last_error = str(e)
        print(f"Groq Error: {last_error}")

    # 2. Secondary: Hugging Face
    try:
        if settings.hf_api_key:
            return _call_hf(prompt)
    except Exception as e:
        last_error = str(e)
        print(f"HF Error: {last_error}")

    # 3. Tertiary: Gemini
    try:
        if settings.gemini_api_key:
             return _call_gemini(prompt)
    except Exception as e:
        last_error = str(e)
        print(f"Gemini Error: {last_error}")

    return _fallback_analysis(last_error)


def _call_gemini(prompt: str) -> dict:
    """Call Gemini 1.5 Flash via REST API directly (no grpcio dependency)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_response(text)


def _call_groq(prompt: str) -> dict:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        return _parse_response(text)


def _call_hf(prompt: str) -> dict:
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {settings.hf_api_key}",
        "Content-Type": "application/json"
    }
    
    # Mistral format
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"
    
    data = {
        "inputs": formatted_prompt,
        "parameters": {"max_new_tokens": 1024, "return_full_text": False}
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        res_json = response.json()
        if isinstance(res_json, list) and len(res_json) > 0:
            text = res_json[0].get("generated_text", "")
        else:
            text = str(res_json)
        return _parse_response(text)


def _parse_response(text: str) -> dict:
    """Parse output text into a dict, handling various markdown formats."""
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

    raise ValueError("Failed to parse AI output into valid JSON")


def _fallback_analysis(last_error: str = "Unknown error") -> dict:
    """Return a neutral fallback if all AIs fail."""
    print(f"All AI providers failed. Last error: {last_error}")
    return {
        "company_details": "Company details unavailable.",
        "overall_context": "Macro-economic context unavailable.",
        "fundamental_analysis": "Fundamental valuation data is currently unavailable.",
        "trend_summary": "Unable to retrieve trend analysis at this time. The Intelligence Engine is recalibrating.",
        "headline_impact": "No recent headlines could be analyzed. Please try again shortly.",
        "market_sentiment": "Sentiment data cannot be computed.",
        "sentiment_consistency": "Sentiment consistency unavailable.",
        "recommendation": "Insufficient data for a recommendation. Please retry.",
    }
