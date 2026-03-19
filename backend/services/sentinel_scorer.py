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
    """Score based on P/E relative to actual NSE sector P/E benchmark, P/B, and ROE."""
    score = 50
    pe = funds.get("pe_ratio", 0.0)
    pb = funds.get("pb_ratio", 0.0)
    roe = funds.get("roe", 0.0)
    sector_pe = funds.get("sector_pe", 0.0)

    # --- P/E Scoring: relative to actual NSE sector benchmark ---
    if pe > 0 and sector_pe > 0:
        # Compare stock P/E to sector benchmark P/E
        pe_ratio_to_sector = pe / sector_pe
        if pe_ratio_to_sector <= 0.8:       score += 20   # Trading at >20% discount — undervalued
        elif pe_ratio_to_sector <= 1.0:     score += 12   # Trading at or below sector average
        elif pe_ratio_to_sector <= 1.3:     score += 4    # Modest premium (within acceptable range)
        elif pe_ratio_to_sector <= 1.7:     score -= 5    # Notable premium — watch for overvaluation
        else:                               score -= 15   # Significantly overvalued vs sector
    elif pe > 0:
        # Fallback: use dynamic sector-type ideals if sector_pe unavailable
        sector = funds.get("sector", "").lower()
        ideal_pe = 40 if "tech" in sector or "software" in sector else \
                   15 if "material" in sector or "metal" in sector or "mining" in sector else \
                   20 if "bank" in sector or "financ" in sector else 25
        if 0 < pe <= ideal_pe:          score += 15
        elif pe <= ideal_pe * 1.5:      score += 5
        elif pe > ideal_pe * 2:         score -= 10

    # --- P/B Scoring (Lower is better, ideal < 3) ---
    if 0 < pb <= 1.5:     score += 15   # Excellent value
    elif pb <= 3.0:       score += 8    # Good value
    elif pb <= 6.0:       score += 2    # Moderate
    elif pb > 10:         score -= 10   # Very expensive

    # --- ROE Scoring (Higher is better) ---
    if roe >= 20:         score += 20   # Excellent
    elif roe >= 15:       score += 14
    elif roe >= 8:        score += 7
    elif roe < 0:         score -= 15   # Losing money on equity

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
