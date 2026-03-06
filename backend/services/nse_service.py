import httpx
from datetime import datetime
from typing import List, Tuple

from models.schemas import HistoricalPoint


def fetch_stock_data(symbol: str) -> Tuple[float, List[HistoricalPoint]]:
    """
    Fetch current price and ~90-day historical data from Yahoo Finance.

    Args:
        symbol: NSE stock symbol (e.g., 'TATASTEEL', 'RELIANCE', 'HDFCBANK')

    Returns:
        Tuple of (current_price, list of HistoricalPoint sorted oldest-first)
    """
    # Append .NS for NSE stocks on Yahoo Finance
    yf_symbol = f"{symbol.upper()}.NS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?range=100d&interval=1d"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data for symbol '{symbol}' from Yahoo Finance: HTTP {response.status_code}")
            
        data = response.json()
        
    result = data.get("chart", {}).get("result", [])
    if not result:
        raise ValueError(f"No data returned for symbol '{symbol}'")
        
    timestamps = result[0].get("timestamp", [])
    indicators = result[0].get("indicators", {}).get("quote", [{}])[0]
    close_prices = indicators.get("close", [])
    
    if not timestamps or not close_prices:
        raise ValueError(f"Incomplete data returned for symbol '{symbol}'")
        
    historical: List[HistoricalPoint] = []
    
    for ts, close in zip(timestamps, close_prices):
        if close is not None:
            # Convert timestamp to YYYY-MM-DD
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            historical.append(HistoricalPoint(date=date_str, close=float(close)))
            
    # We requested 100d, return up to 90 valid trading days
    historical = historical[-90:]
    
    current_price = historical[-1].close if historical else 0.0
    
    return current_price, historical
