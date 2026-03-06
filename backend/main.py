from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.nse_service import fetch_stock_data
from services.gemini_service import analyze_stock
from services.sentinel_scorer import compute_sentinel_score, classify
from models.schemas import Analysis, StockAnalysisResponse

app = FastAPI(title="Market Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/analyze/{ticker}")
async def analyze(ticker: str):
    ticker = ticker.upper()

    try:
        # Step 1: Fetch 90-day price data from NSE India
        current_price, historical = fetch_stock_data(ticker)

        # Step 2: Get Gemini analysis with live news via Search Grounding
        gemini_result = analyze_stock(ticker, current_price, historical)

        # Step 3: Compute the Sentinel Score (40/40/20 weighted)
        score = compute_sentinel_score(historical, gemini_result)
        category = classify(score)

        # Step 4: Build standardized response
        analysis = Analysis(
            sentinel_score=score,
            score_category=category,
            trend_summary=gemini_result.get("trend_summary", ""),
            headline_impact=gemini_result.get("headline_impact", ""),
            sentiment_consistency=gemini_result.get("sentiment_consistency", ""),
            recommendation=gemini_result.get("recommendation", ""),
        )

        return StockAnalysisResponse.build(
            ticker=ticker,
            current_price=current_price,
            historical_90d=historical,
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
    """Return the list of featured tickers for the landing page."""
    return {
        "tickers": settings.FEATURED_TICKERS,
        "labels": settings.TICKER_LABELS,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Market Sentinel API"}
