from datetime import date, timedelta, datetime
from typing import List, Tuple

from nselib import capital_market

from models.schemas import HistoricalPoint


def _parse_price(value) -> float:
    """Parse price value, handling comma-separated numbers like '1,389.40'."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value.replace(",", ""))
    return float(value)


def _parse_date(value: str) -> str:
    """Convert NSE date format (dd-Mon-yyyy) to ISO format (yyyy-mm-dd)."""
    for fmt in ("%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    return str(value)


def fetch_stock_data(symbol: str) -> Tuple[float, List[HistoricalPoint]]:
    """
    Fetch current price and 90-day historical data directly from NSE India.

    Args:
        symbol: NSE stock symbol (e.g., 'TATASTEEL', 'RELIANCE', 'HDFCBANK')

    Returns:
        Tuple of (current_price, list of HistoricalPoint sorted oldest-first)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=100)  # Fetch extra to account for holidays

    df = capital_market.price_volume_and_deliverable_position_data(
        symbol=symbol.upper(),
        from_date=start_date.strftime("%d-%m-%Y"),
        to_date=end_date.strftime("%d-%m-%Y"),
    )

    if df is None or df.empty:
        raise ValueError(f"No data returned from NSE for symbol '{symbol}'")

    historical: List[HistoricalPoint] = []
    for _, row in df.iterrows():
        try:
            date_str = _parse_date(str(row["Date"]))
            close_price = _parse_price(row["ClosePrice"])
            historical.append(HistoricalPoint(date=date_str, close=close_price))
        except (ValueError, TypeError, KeyError):
            continue

    # NSE returns newest-first; reverse to oldest-first for charting
    historical.reverse()

    # Trim to ~90 trading days
    historical = historical[-90:]

    # Current price is the most recent close
    current_price = historical[-1].close if historical else 0.0

    return current_price, historical
