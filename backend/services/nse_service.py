import httpx
from datetime import datetime
from typing import List, Tuple
import xml.etree.ElementTree as ET
import urllib.request

from models.schemas import HistoricalPoint


def fetch_stock_data(symbol: str) -> Tuple[float, List[HistoricalPoint]]:
    """
    Fetch 1-year of daily stock data from Yahoo Finance.
    """
    # Ticker cleanup & Mapping
    symbol = symbol.strip().upper()
    
    symbol_map = {
        "NALCO": "NATIONALUM"
    }
    symbol = symbol_map.get(symbol, symbol)
    
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        yf_symbol = f"{symbol}.NS"
    else:
        yf_symbol = symbol
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?range=1y&interval=1d"
    
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
            
    # Return all valid trading days in the recent 1y period
    current_price = historical[-1].close if historical else 0.0
    
    return current_price, historical


def fetch_stock_news(symbol: str) -> List[str]:
    """
    Fetch the latest 5-10 news headlines for a given stock symbol via Google News RSS.
    """
    search_query = f"{symbol}+stock+India"
    if symbol == "NALCO" or symbol == "NATIONALUM":
        search_query = "National+Aluminium+Company+NALCO+India"
        headlines.extend([
            "CONTEXT RULES: Recent data as of March 2026 indicates strong financial performance including record profits and revenue growth.",
            "CONTEXT RULES: New product developments include the IA91 alloy.",
            "CONTEXT RULES: Stock movement is heavily influenced by global aluminium prices and current market conditions."
        ])
        
    url = f"https://news.google.com/rss/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN:en"
    headlines = []
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        html = urllib.request.urlopen(req, timeout=10).read()
        root = ET.fromstring(html)
        
        for item in root.findall('.//item')[:8]:
            title = item.find('title')
            if title is not None and title.text:
                headlines.append(title.text)
    except Exception as e:
        print(f"Failed to fetch news for {symbol}: {e}")
        
    return headlines
