from pydantic import BaseModel
from typing import List


class HistoricalPoint(BaseModel):
    date: str
    close: float


class Analysis(BaseModel):
    sentinel_score: int
    score_category: str
    trend_summary: str
    headline_impact: str
    sentiment_consistency: str
    recommendation: str


class StockAnalysisResponse(BaseModel):
    status: str = "success"
    data: dict

    @classmethod
    def build(
        cls,
        ticker: str,
        current_price: float,
        historical_90d: List[HistoricalPoint],
        analysis: Analysis,
    ):
        return cls(
            status="success",
            data={
                "ticker": ticker,
                "current_price": current_price,
                "historical_90d": [h.model_dump() for h in historical_90d],
                "analysis": analysis.model_dump(),
            },
        )
