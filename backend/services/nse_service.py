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
    Dual-source fundamental data fetcher (runs in parallel):
    - NSE official API: P/E ratio, Sector P/E benchmark, Sector, Industry
    - Yahoo Finance (fc.yahoo.com crumb): P/B ratio
    Both sources run concurrently to keep total latency under 10s.
    """
    import concurrent.futures

    symbol = symbol.strip().upper()
    nse_symbol = symbol.replace(".NS", "").replace(".BO", "")
    yf_symbol = f"{nse_symbol}.NS"

    fundamentals = {
        "pe_ratio": 0.0,
        "pb_ratio": 0.0,
        "sector_pe": 0.0,
        "sector": "Unknown",
        "industry": "Unknown",
    }

    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _fetch_nse():
        result = {}
        try:
            headers = {"User-Agent": UA, "Accept": "application/json", "Referer": "https://www.nseindia.com/"}
            with httpx.Client(follow_redirects=True, timeout=8.0) as s:
                s.get("https://www.nseindia.com/", headers=headers)
                r = s.get(f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}", headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    meta = data.get("metadata", {})
                    ind = data.get("industryInfo", {})
                    result["pe_ratio"] = float(meta.get("pdSymbolPe") or 0.0)
                    result["sector_pe"] = float(meta.get("pdSectorPe") or 0.0)
                    result["sector"] = str(ind.get("sector") or "Unknown")
                    result["industry"] = str(ind.get("industry") or ind.get("basicIndustry") or "Unknown")
                    print(f"NSE: PE={result['pe_ratio']}, SectorPE={result['sector_pe']}")
        except Exception as e:
            print(f"NSE fetch failed: {e}")
        return result

    def _fetch_yahoo_pb():
        result = {}
        try:
            headers = {"User-Agent": UA, "Accept": "*/*"}
            with httpx.Client(follow_redirects=True, timeout=8.0) as s:
                s.get("https://fc.yahoo.com", headers=headers)
                r_crumb = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=headers)
                if r_crumb.status_code == 200:
                    crumb = r_crumb.text.strip()
                    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{yf_symbol}?modules=defaultKeyStatistics&crumb={crumb}"
                    r = s.get(url, headers={**headers, "Accept": "application/json"})
                    if r.status_code == 200:
                        stats = r.json().get("quoteSummary", {}).get("result", [{}])[0].get("defaultKeyStatistics", {})
                        pb = (stats.get("priceToBook") or {}).get("raw", 0.0)
                        if pb:
                            result["pb_ratio"] = float(pb)
                            print(f"Yahoo: PB={pb}")
        except Exception as e:
            print(f"Yahoo fetch failed: {e}")
        return result

    # Run both sources in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_nse = executor.submit(_fetch_nse)
        fut_yf = executor.submit(_fetch_yahoo_pb)
        nse_data = fut_nse.result(timeout=12)
        yf_data = fut_yf.result(timeout=12)

    fundamentals.update(nse_data)
    fundamentals.update(yf_data)
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
