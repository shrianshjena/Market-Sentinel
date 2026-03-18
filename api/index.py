import sys
import os

# Add backend directory to Python path so existing modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.nse_service import fetch_stock_data, fetch_stock_news
from services.ai_service import analyze_stock
from services.sentinel_scorer import compute_sentinel_score, classify
from models.schemas import Analysis, StockAnalysisResponse

app = FastAPI(title="Market Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://marketsentinel-gamma.vercel.app", "http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/analyze/{ticker}")
async def analyze(ticker: str):
    ticker = ticker.upper()

    try:
        current_price, historical = fetch_stock_data(ticker)
        news_context = fetch_stock_news(ticker)
        ai_result = analyze_stock(ticker, current_price, historical, news_context)
        score = compute_sentinel_score(historical, ai_result)
        category = classify(score)

        analysis = Analysis(
            sentinel_score=score,
            score_category=category,
            company_details=ai_result.get("company_details", ""),
            trend_summary=ai_result.get("trend_summary", ""),
            headline_impact=ai_result.get("headline_impact", ""),
            market_sentiment=ai_result.get("market_sentiment", ""),
            sentiment_consistency=ai_result.get("sentiment_consistency", ""),
            overall_context=ai_result.get("overall_context", ""),
            recommendation=ai_result.get("recommendation", ""),
        )

        return StockAnalysisResponse.build(
            ticker=ticker,
            current_price=current_price,
            historical_5y=historical,
            analysis=analysis,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"The Intelligence Engine encountered an error: {str(e)}",
        )


@app.get("/api/featured")
async def featured_tickers():
    return {
        "tickers": settings.FEATURED_TICKERS,
        "labels": settings.TICKER_LABELS,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Market Sentinel API"}
