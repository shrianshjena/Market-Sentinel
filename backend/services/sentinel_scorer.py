from models.schemas import HistoricalPoint
from typing import List

CATEGORIES = [
    (81, 100, "Strong Catalyst"),
    (61, 80, "Bullish Lean"),
    (41, 60, "Neutral"),
    (21, 40, "Cautionary"),
    (0, 20, "Distressed"),
]


def classify(score: int) -> str:
    """Map a 0-100 score to its category label."""
    for low, high, label in CATEGORIES:
        if low <= score <= high:
            return label
    return "Neutral"


def compute_sentinel_score(
    price_history: List[HistoricalPoint],
    gemini_analysis: dict,
    fundamentals: dict = None
) -> int:
    """
    Compute the Sentinel Score using evenly weighted 5 factors:
    - 20% Price Trend (Historical 300% Capped)
    - 20% Headline Impact (Live News)
    - 20% Sentiment Consistency
    - 20% Macro Context
    - 20% Fundamental Valuation
    """
    price_trend_score = _score_price_trend(price_history)
    headline_score = _score_headline_impact(
        gemini_analysis.get("headline_impact", "")
    )
    sentiment_score = _score_sentiment(
        gemini_analysis.get("sentiment_consistency", "")
    )
    macro_score = _score_macro_context(
        gemini_analysis.get("overall_context", "")
    )
    
    fundamentals = fundamentals or {}
    fundamental_score = _score_fundamentals(fundamentals)

    final = int(
        0.2 * price_trend_score
        + 0.2 * headline_score
        + 0.2 * sentiment_score
        + 0.2 * macro_score
        + 0.2 * fundamental_score
    )
    return max(0, min(100, final))


def _score_price_trend(history: List[HistoricalPoint]) -> int:
    """Score based on 5-year return and recent momentum."""
    if len(history) < 2:
        return 50

    prices = [h.close for h in history]
    total_return = (prices[-1] - prices[0]) / prices[0] * 100

    # Recent momentum: compare last 10 days avg to prior 10 days avg
    if len(prices) >= 20:
        recent_avg = sum(prices[-10:]) / 10
        prior_avg = sum(prices[-20:-10]) / 10
        momentum = (recent_avg - prior_avg) / prior_avg * 100
    else:
        momentum = 0

    # Map total_return to 0-100 scale (-300% -> 0, +300% -> 100 on 5-year scale)
    trend_score = max(0, min(100, int(50 + (total_return / 6))))
    momentum_bonus = max(-15, min(15, int(momentum * 3)))

    return max(0, min(100, trend_score + momentum_bonus))

def _score_fundamentals(funds: dict) -> int:
    """Score mathematically based on P/E, P/B, and ROE metrics."""
    score = 50
    pe = funds.get("pe_ratio", 0.0)
    pb = funds.get("pb_ratio", 0.0)
    roe = funds.get("roe", 0.0)
    
    # PE Contribution (Lower is better, ideal 10-25)
    if 0 < pe <= 20: score += 15
    elif 20 < pe <= 35: score += 5
    elif pe > 40: score -= 10
    
    # PB Contribution (Lower is better, ideal < 3)
    if 0 < pb <= 3: score += 15
    elif 3 < pb <= 6: score += 5
    elif pb > 10: score -= 10
    
    # ROE Contribution (Higher is better, ideal > 15)
    if roe >= 15: score += 20
    elif roe >= 8: score += 10
    elif roe < 0: score -= 15
    
    return max(0, min(100, score))


def _score_headline_impact(headline_text: str) -> int:
    """Score headlines via keyword analysis."""
    text = headline_text.lower()

    positive_keywords = [
        "growth", "surge", "upgrade", "expansion", "profit",
        "record", "bullish", "outperform", "beat", "strong",
        "positive", "gains", "rally", "infrastructure", "contract",
        "dividend", "acquisition",
    ]
    negative_keywords = [
        "decline", "loss", "downgrade", "risk", "weak",
        "crash", "concern", "debt", "probe", "scandal",
        "negative", "sell", "layoff", "warning", "penalty",
        "investigation", "slowdown",
    ]

    pos_count = sum(1 for kw in positive_keywords if kw in text)
    neg_count = sum(1 for kw in negative_keywords if kw in text)

    net = pos_count - neg_count
    return max(0, min(100, 50 + net * 10))


def _score_sentiment(sentiment_text: str) -> int:
    """Score sentiment consistency from Gemini's analysis."""
    text = sentiment_text.lower()

    if "bullish" in text and ("consistent" in text or "strong" in text):
        return 85
    elif "bullish" in text:
        return 70
    elif "mixed" in text:
        return 50
    elif "bearish" in text and ("consistent" in text or "strong" in text):
        return 15
    elif "bearish" in text:
        return 30
    elif "positive" in text:
        return 65
    elif "negative" in text:
        return 35
    return 50

def _score_macro_context(context_text: str) -> int:
    """Score macro-environmental factors from analysis."""
    text = context_text.lower()
    
    positive_keywords = ["growth", "expansion", "supportive", "tailwinds", "favorable", "cut", "demand", "recovery", "resilient"]
    negative_keywords = ["inflation", "recession", "headwinds", "rate hike", "slowdown", "weakness", "concern", "risk", "pressure"]
    
    pos_count = sum(1 for kw in positive_keywords if kw in text)
    neg_count = sum(1 for kw in negative_keywords if kw in text)
    
    net = pos_count - neg_count
    return max(0, min(100, 50 + net * 15))
