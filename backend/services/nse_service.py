import httpx
from datetime import datetime
from typing import List, Tuple
import xml.etree.ElementTree as ET
import urllib.request

from models.schemas import HistoricalPoint


def fetch_stock_data(symbol: str) -> Tuple[float, List[HistoricalPoint]]:
    """
    Fetch 5-years of daily stock data from Yahoo Finance.
    """
    # Ticker cleanup
    symbol = symbol.strip().upper()
    
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        yf_symbol = f"{symbol}.NS"
    else:
        yf_symbol = symbol
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?range=5y&interval=1d"
    
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
            
    # Return all valid trading days in the recent 5y period
    current_price = historical[-1].close if historical else 0.0
    
    return current_price, historical


def _fetch_rss_helper(url: str, limit: int = 5) -> List[str]:
    headlines = []
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urllib.request.urlopen(req, timeout=10).read()
        root = ET.fromstring(html)
        for item in root.findall('.//item')[:limit]:
            title = item.find('title')
            if title is not None and title.text:
                headlines.append(title.text)
    except Exception as e:
        print(f"Failed to fetch RSS from {url}: {e}")
    return headlines

def _get_yahoo_crumb_and_cookies() -> tuple:
    """Fetch Yahoo Finance session cookies and crumb for authenticated API calls."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session = httpx.Client(follow_redirects=True, timeout=15.0)
    try:
        session.get("https://finance.yahoo.com/", headers=headers)
        r = session.get("https://query2.finance.yahoo.com/v1/test/getcrumb", headers={**headers, "Accept": "application/json"})
        if r.status_code == 200 and "Too Many" not in r.text:
            return r.text.strip(), session
    except Exception:
        pass
    return None, session


def fetch_stock_fundamentals(symbol: str) -> dict:
    """Fetch Key Statistics and Financial Data from Yahoo Finance using session+crumb."""
    symbol = symbol.strip().upper()
    yf_symbol = f"{symbol}.NS" if not symbol.endswith(('.NS', '.BO')) else symbol

    fundamentals = {"pe_ratio": 0.0, "pb_ratio": 0.0, "roe": 0.0, "sector": "Unknown", "industry": "Unknown"}

    try:
        crumb, session = _get_yahoo_crumb_and_cookies()
        if not crumb:
            return fundamentals

        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{yf_symbol}?modules=defaultKeyStatistics,financialData,summaryProfile&crumb={crumb}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Accept": "application/json",
        }
        response = session.get(url, headers=headers, timeout=10.0)
        session.close()

        if response.status_code == 200:
            data = response.json()
            res = data.get("quoteSummary", {}).get("result", [])
            if res:
                stats = res[0].get("defaultKeyStatistics", {})
                fin = res[0].get("financialData", {})
                prof = res[0].get("summaryProfile", {})

                pe = (stats.get("trailingPE") or {}).get("raw") or (stats.get("forwardPE") or {}).get("raw") or 0.0
                pb = (stats.get("priceToBook") or {}).get("raw") or 0.0
                roe_raw = (fin.get("returnOnEquity") or {}).get("raw") or 0.0

                fundamentals["pe_ratio"] = float(pe)
                fundamentals["pb_ratio"] = float(pb)
                fundamentals["roe"] = float(roe_raw) * 100
                fundamentals["sector"] = str(prof.get("sector") or "Unknown")
                fundamentals["industry"] = str(prof.get("industry") or "Unknown")
    except Exception as e:
        print(f"Failed to fetch fundamentals: {e}")

    return fundamentals


def fetch_stock_news(symbol: str) -> List[str]:
    """
    Fetch the latest news headlines from Google News, Economic Times, and Livemint RSS.
    """
    search_query = f"{symbol}+stock+India"
    headlines = []
    google_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN:en"
    et_url = f"https://news.google.com/rss/search?q={search_query}+site:economictimes.indiatimes.com&hl=en-IN&gl=IN&ceid=IN:en"
    mint_url = f"https://news.google.com/rss/search?q={search_query}+site:livemint.com&hl=en-IN&gl=IN&ceid=IN:en"
    
    headlines.extend(_fetch_rss_helper(google_url, 4))
    headlines.extend(_fetch_rss_helper(et_url, 3))
    headlines.extend(_fetch_rss_helper(mint_url, 3))
        
    return headlines
