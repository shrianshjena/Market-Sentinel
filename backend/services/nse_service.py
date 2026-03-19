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

def fetch_stock_fundamentals(symbol: str) -> dict:
    """
    Dual-source fundamental data fetcher:
    - NSE official API: P/E ratio, Sector P/E benchmark, Sector, Industry
    - Yahoo Finance (fc.yahoo.com crumb): P/B ratio, ROE
    """
    symbol = symbol.strip().upper()
    nse_symbol = symbol.replace(".NS", "").replace(".BO", "")
    yf_symbol = f"{nse_symbol}.NS"

    fundamentals = {
        "pe_ratio": 0.0,
        "pb_ratio": 0.0,
        "roe": 0.0,
        "sector_pe": 0.0,
        "sector": "Unknown",
        "industry": "Unknown",
    }

    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # ── Source 1: NSE API for P/E and Sector data ──────────────────────────
    try:
        nse_headers = {**base_headers, "Referer": "https://www.nseindia.com/"}
        with httpx.Client(follow_redirects=True, timeout=20.0) as session:
            session.get("https://www.nseindia.com/", headers=nse_headers)
            url = f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}"
            response = session.get(url, headers=nse_headers)
            if response.status_code == 200:
                data = response.json()
                metadata = data.get("metadata", {})
                industry_info = data.get("industryInfo", {})
                pe = metadata.get("pdSymbolPe", 0.0)
                sector_pe = metadata.get("pdSectorPe", 0.0)
                sector = industry_info.get("sector", "Unknown")
                industry = industry_info.get("industry", industry_info.get("basicIndustry", "Unknown"))
                fundamentals["pe_ratio"] = float(pe) if pe else 0.0
                fundamentals["sector_pe"] = float(sector_pe) if sector_pe else 0.0
                fundamentals["sector"] = str(sector or "Unknown")
                fundamentals["industry"] = str(industry or "Unknown")
                print(f"NSE: PE={pe}, SectorPE={sector_pe}, Sector={sector}")
    except Exception as e:
        print(f"NSE fetch failed: {e}")

    # ── Source 2: Yahoo Finance for P/B and ROE (via fc.yahoo.com crumb) ───
    try:
        yf_headers = {**base_headers, "Accept": "*/*"}
        with httpx.Client(follow_redirects=True, timeout=15.0) as session:
            # Acquire Yahoo consent cookie + crumb
            session.get("https://fc.yahoo.com", headers=yf_headers)
            r_crumb = session.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=yf_headers)
            if r_crumb.status_code == 200:
                crumb = r_crumb.text.strip()
                url = (
                    f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{yf_symbol}"
                    f"?modules=defaultKeyStatistics,financialData&crumb={crumb}"
                )
                r = session.get(url, headers={**yf_headers, "Accept": "application/json"})
                if r.status_code == 200:
                    result = r.json().get("quoteSummary", {}).get("result", [{}])[0]
                    stats = result.get("defaultKeyStatistics", {})
                    fin = result.get("financialData", {})
                    pb = (stats.get("priceToBook") or {}).get("raw", 0.0)
                    roe_raw = (fin.get("returnOnEquity") or {}).get("raw", 0.0)
                    if pb:
                        fundamentals["pb_ratio"] = float(pb)
                    if roe_raw:
                        fundamentals["roe"] = float(roe_raw) * 100
                    print(f"Yahoo: PB={pb}, ROE={roe_raw}")
    except Exception as e:
        print(f"Yahoo fetch failed: {e}")

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
