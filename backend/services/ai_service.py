import json
import re
import httpx
from config import settings
from models.schemas import HistoricalPoint
from typing import List

# Primary models
GROQ_MODEL = "llama-3.3-70b-versatile"
HF_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"


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

CRITICAL CONTEXT: Today's date is March 18, 2026. You MUST analyze the provided Recent News Headlines (which reflect the latest 2026 data, including any recent financial performance, product launches, or partnerships) and the stock price data to formulate your insights. Do not use outdated 2024 information.

Analyze the stock {ticker} listed on NSE based on the following data:

RECENT NEWS HEADLINES (Latest 2026 Context):
{news_text}

FUNDAMENTAL VALUATION (Live Metrics):
- Sector & Industry: {fundamentals.get('sector', 'Unknown')} - {fundamentals.get('industry', 'Unknown')}
- P/E Ratio: {fundamentals.get('pe_ratio', 0.0)}
- P/B Ratio: {fundamentals.get('pb_ratio', 0.0)}
- Return on Equity (ROE): {fundamentals.get('roe', 0.0):.2f}%
(CRITICAL: Evaluate the P/E ratio strictly relative to this specific sector and its industry peers instead of fixed thresholds.)

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

    # 1. Primary: Groq
    try:
        if settings.groq_api_key:
             return _call_groq(prompt)
    except Exception as e:
        print(f"Groq failed: {e}. Falling back to Hugging Face.")

    # 2. Secondary: Hugging Face
    try:
        if settings.hf_api_key:
            return _call_hf(prompt)
    except Exception as e:
        print(f"Hugging Face failed: {e}. All models degraded.")

    return _fallback_analysis()


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


def _fallback_analysis() -> dict:
    """Return a neutral fallback if all AIs fail."""
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
