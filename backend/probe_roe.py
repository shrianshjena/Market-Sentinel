"""Probe NSE endpoints for ROE and P/B data"""
import httpx, json

nse_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

with httpx.Client(follow_redirects=True, timeout=20.0) as session:
    session.get("https://www.nseindia.com/", headers=nse_headers)

    # Test NSE financial results endpoint
    print("=== NSE Financial Results ===")
    r1 = session.get("https://www.nseindia.com/api/quote-equity?symbol=TATASTEEL&section=financial_results", headers=nse_headers)
    print(f"Status: {r1.status_code}")
    if r1.status_code == 200:
        print(r1.text[:800])

    # Test NSE fundamentals/key-stats
    print("\n=== NSE Key Stats ===")
    r2 = session.get("https://www.nseindia.com/api/quote-equity?symbol=TATASTEEL&section=trade_info", headers=nse_headers)
    print(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        data = r2.json()
        print(json.dumps(data, indent=2)[:1000])

    # Screener.in API
    print("\n=== Screener.in ===")
    r3 = session.get("https://www.screener.in/api/company/TATASTEEL/?format=json", headers={**nse_headers, "Referer": "https://www.screener.in/"})
    print(f"Status: {r3.status_code} - {r3.text[:300]}")
