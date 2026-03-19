from pydantic import BaseModel
from typing import List


class HistoricalPoint(BaseModel):
    date: str
    close: float


class Fundamentals(BaseModel):
    pe_ratio: float
    sector_pe: float = 0.0
    sector: str
    industry: str


class Analysis(BaseModel):
    sentinel_score: int
    score_category: str
    company_details: str
    fundamental_analysis: str
    trend_summary: str
    headline_impact: str
    market_sentiment: str
    sentiment_consistency: str
    overall_context: str
    recommendation: str


class StockAnalysisResponse(BaseModel):
    status: str = "success"
    data: dict

    @classmethod
    def build(
        cls,
        ticker: str,
        current_price: float,
        historical_5y: List[HistoricalPoint],
        analysis: Analysis,
        fundamentals: Fundamentals,
    ):
        return cls(
            status="success",
            data={
                "ticker": ticker,
                "current_price": current_price,
                "historical_5y": [h.model_dump() for h in historical_5y],
                "fundamentals": fundamentals.model_dump(),
                "analysis": analysis.model_dump(),
            },
        )
