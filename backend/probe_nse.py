"""Test what NSE quote-equity returns for PB and ROE"""
import httpx, json

headers_nse = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

with httpx.Client(follow_redirects=True, timeout=15.0) as session:
    session.get("https://www.nseindia.com/", headers=headers_nse)
    r = session.get("https://www.nseindia.com/api/quote-equity?symbol=TATASTEEL", headers=headers_nse)
    if r.status_code == 200:
        data = r.json()
        print("=== METADATA ===")
        print(json.dumps(data.get("metadata", {}), indent=2))
        print("\n=== INDUSTRY INFO ===")
        print(json.dumps(data.get("industryInfo", {}), indent=2))
        print("\n=== SECURITY INFO ===")
        print(json.dumps(data.get("securityInfo", {}), indent=2))
        print("\n=== PRICE INFO ===")
        print(json.dumps(data.get("priceInfo", {}), indent=2)[:500])
