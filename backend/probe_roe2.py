"""Test Yahoo Finance v7 quoteSummary for P/B and ROE"""
import httpx, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Test Yahoo Finance v7 quoteSummary (older endpoint, sometimes doesn't need crumb)
print("=== Yahoo v7 quoteSummary ===")
r1 = httpx.get(
    "https://query1.finance.yahoo.com/v10/finance/quoteSummary/TATASTEEL.NS?modules=defaultKeyStatistics,financialData,summaryProfile,defaultKeyStatistics",
    headers=headers, timeout=10.0
)
print(f"Status: {r1.status_code}")
if r1.status_code == 200:
    data = r1.json()
    result = data.get("quoteSummary", {}).get("result", [{}])[0]
    stats = result.get("defaultKeyStatistics", {})
    fin = result.get("financialData", {})
    print("priceToBook:", stats.get("priceToBook"))
    print("returnOnEquity:", fin.get("returnOnEquity"))
    print("trailingPE:", stats.get("trailingPE"))

# Alternatively test the NSE with a different crumb approach - using cookie from their CDN
print("\n=== Yahoo Finance with cookie ===")
with httpx.Client(follow_redirects=True, timeout=12.0) as s:
    # Get consent cookie
    r2 = s.get("https://fc.yahoo.com", headers=headers)
    print("yahoo consent status:", r2.status_code, "cookies:", dict(s.cookies))
    
    r3 = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers={**headers, "Accept": "*/*"})
    print("crumb status:", r3.status_code, "crumb:", r3.text[:50])
