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


# Maps NSE industryInfo.sector -> NIFTY sectoral index symbol
_SECTOR_INDEX_MAP = {
    "Metals & Mining": "NIFTY METAL",
    "Oil Gas & Consumable Fuels": "NIFTY ENERGY",
    "Information Technology": "NIFTY IT",
    "Financial Services": "NIFTY BANK",
    "Consumer Goods": "NIFTY FMCG",
    "Fast Moving Consumer Goods": "NIFTY FMCG",
    "Pharmaceuticals & Biotech": "NIFTY PHARMA",
    "Healthcare": "NIFTY HEALTHCARE",
    "Realty": "NIFTY REALTY",
    "Automobiles & Auto Components": "NIFTY AUTO",
    "Telecom": "NIFTY IT",
    "Services": "NIFTY SERV SECTOR",
    "Capital Goods": "NIFTY INFRA",
    "Construction": "NIFTY INFRA",
    "Power": "NIFTY ENERGY",
    "Chemicals": "NIFTY CHEMICALS",
    "Media Entertainment & Publication": "NIFTY MEDIA",
    "Textiles": "NIFTY COMMODITIES",
    "Diversified": "NIFTY 500",
}

# ── Persistent NSE session ────────────────────────────────────────────────────
# NSE requires a browser-like session: visit the homepage first to receive
# cookies (especially `nsit` and `nseappid`), then all API calls within the
# same session are accepted. Re-creating the client on every request discards
# these cookies, making the second+ call unreliable.
_NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

_nse_session: httpx.Client | None = None


def _get_nse_session() -> httpx.Client:
    """
    Return a primed httpx.Client with live NSE session cookies.
    Creates a new client (and re-primes it) only when the existing one is closed
    or un-initialised.
    """
    global _nse_session
    if _nse_session is None or _nse_session.is_closed:
        client = httpx.Client(follow_redirects=True, timeout=15.0)
        try:
            client.get("https://www.nseindia.com/", headers=_NSE_HEADERS)
        except Exception as e:
            print(f"NSE session priming failed: {e}")
        _nse_session = client
    return _nse_session


def fetch_stock_fundamentals(symbol: str) -> dict:
    """
    Fetch fundamental data from NSE's official APIs:
    1. quote-equity → stock P/E, sector name, industry
    2. allIndices   → true NIFTY sectoral index P/E (the real benchmark)

    The sectoral index P/E (NIFTY METAL, NIFTY ENERGY, etc.) is the correct
    peer comparison — not pdSectorPe, which is the stock's own benchmark index P/E
    and can equal the stock's P/E when the stock dominates that index.

    A persistent session is used so NSE cookies survive across multiple calls.
    """
    symbol = symbol.strip().upper()
    nse_symbol = symbol.replace(".NS", "").replace(".BO", "")

    fundamentals = {
        "pe_ratio": 0.0,
        "sector_pe": 0.0,
        "sector": "Unknown",
        "industry": "Unknown",
    }

    try:
        session = _get_nse_session()

        # Step 1: Fetch stock quote for P/E, sector, industry
        r_quote = session.get(
            f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}",
            headers=_NSE_HEADERS,
        )

        # If NSE rejects us (session expired), reprime once and retry
        if r_quote.status_code in (401, 403, 429):
            print(f"NSE session rejected ({r_quote.status_code}) — re-priming session.")
            global _nse_session
            _nse_session = None
            session = _get_nse_session()
            r_quote = session.get(
                f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}",
                headers=_NSE_HEADERS,
            )

        if r_quote.status_code == 200:
            data = r_quote.json()
            meta = data.get("metadata", {})
            ind = data.get("industryInfo", {})
            pe = meta.get("pdSymbolPe")
            sector = str(ind.get("sector") or "Unknown")
            industry = str(ind.get("industry") or ind.get("basicIndustry") or "Unknown")
            if pe:
                fundamentals["pe_ratio"] = float(pe)
            fundamentals["sector"] = sector
            fundamentals["industry"] = industry
        else:
            print(f"NSE quote-equity returned HTTP {r_quote.status_code} for {nse_symbol}")

        # Step 2: Fetch all NSE indices and look up the sector's index P/E
        r_idx = session.get(
            "https://www.nseindia.com/api/allIndices",
            headers=_NSE_HEADERS,
        )
        if r_idx.status_code == 200:
            sector = fundamentals["sector"]
            target_index = _SECTOR_INDEX_MAP.get(sector)
            if target_index:
                for idx in r_idx.json().get("data", []):
                    if idx.get("indexSymbol") == target_index:
                        idx_pe = idx.get("pe", 0)
                        if idx_pe and float(idx_pe) > 0:
                            fundamentals["sector_pe"] = float(idx_pe)
                            print(f"NSE: PE={fundamentals['pe_ratio']}, SectorPE={fundamentals['sector_pe']} ({target_index})")
                        break

        if fundamentals["sector_pe"] == 0.0:
            print(f"NSE: PE={fundamentals['pe_ratio']}, SectorPE=N/A for sector '{fundamentals['sector']}'")

    except Exception as e:
        print(f"NSE fundamentals fetch failed: {e}")
        # Invalidate the session so the next call re-primes it
        _nse_session = None

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
