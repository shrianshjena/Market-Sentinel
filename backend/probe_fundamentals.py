"""Test NSE API and Yahoo Finance v8 modules for fundamental data"""
import httpx, json

headers_nse = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

# 1 - Test NSE API (needs Referer + session)
print("=== NSE quote-equity ===")
with httpx.Client(follow_redirects=True, timeout=15.0) as session:
    # Must first hit the main page to get cookies
    session.get("https://www.nseindia.com/", headers=headers_nse)
    r = session.get("https://www.nseindia.com/api/quote-equity?symbol=TATASTEEL", headers=headers_nse)
    print("NSE Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        info = data.get("industryInfo", {})
        metadata = data.get("metadata", {})
        print("sector:", info.get("sector"))
        print("industry:", info.get("industry"))
        print("pe:", metadata.get("pdSymbolPe"))
        print("priceToBook:", data.get("securityInfo", {}).get("faceValue"))
        print(json.dumps(metadata, indent=2)[:500])
    else:
        print("NSE response:", r.text[:300])

# 2 - Test Yahoo Finance v8 with modules
print("\n=== Yahoo v8 with modules ===")
r2 = httpx.get(
    "https://query1.finance.yahoo.com/v8/finance/chart/TATASTEEL.NS?range=1d&interval=1d&modules=financialData,defaultKeyStatistics,summaryProfile",
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=10.0
)
print("Yahoo v8 Status:", r2.status_code)
if r2.status_code == 200:
    data2 = r2.json()
    meta = data2.get("chart", {}).get("result", [{}])[0].get("meta", {})
    print("keys in meta:", list(meta.keys())[:20])
