"""Probe NSE's index list API and fetch sectoral index P/E values"""
import httpx, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

# NSE Sectoral indices we care about
SECTOR_INDEX_MAP = {
    "Metals & Mining": "NIFTY METAL",
    "Oil Gas & Consumable Fuels": "NIFTY ENERGY",
    "Information Technology": "NIFTY IT",
    "Financial Services": "NIFTY BANK",
    "Consumer Goods": "NIFTY FMCG",
    "Pharmaceuticals & Biotech": "NIFTY PHARMA",
    "Realty": "NIFTY REALTY",
    "Automobiles & Auto Components": "NIFTY AUTO",
    "Media Entertainment & Publication": "NIFTY MEDIA",
    "Textiles": "NIFTY TEXTILE",
    "Capital Goods": "NIFTY CPSE",
}

with httpx.Client(follow_redirects=True, timeout=12.0) as s:
    s.get("https://www.nseindia.com/", headers=headers)

    # Try NSE index data for each sectoral index
    for sector, index_name in SECTOR_INDEX_MAP.items():
        symbol = index_name.replace(" ", "%20")
        r = s.get(f"https://www.nseindia.com/api/allIndices", headers=headers)
        if r.status_code == 200:
            indices = r.json().get("data", [])
            for idx in indices:
                if idx.get("indexSymbol") == index_name or index_name in (idx.get("indexSymbol") or ""):
                    print(f"{sector}: {idx.get('indexSymbol')} -> PE={idx.get('pe')}")
            break  # Only need to fetch once

    # Get all indices to see the PE field structure
    print("\n=== All indices with PE ===")
    r2 = s.get("https://www.nseindia.com/api/allIndices", headers=headers)
    if r2.status_code == 200:
        for idx in r2.json().get("data", []):
            if idx.get("pe") and "NIFTY" in (idx.get("indexSymbol") or ""):
                print(f"  {idx.get('indexSymbol')}: PE={idx.get('pe')}")
