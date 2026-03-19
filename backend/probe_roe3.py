"""Test fc.yahoo.com consent cookie + crumb approach for P/B and ROE"""
import httpx, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

with httpx.Client(follow_redirects=True, timeout=15.0) as session:
    # Step 1: Get consent cookie from fc.yahoo.com
    session.get("https://fc.yahoo.com", headers=headers)
    
    # Step 2: Get crumb using query1 (not query2)
    r_crumb = session.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers={**headers, "Accept": "*/*"})
    crumb = r_crumb.text.strip()
    print(f"Crumb: {repr(crumb)} (status {r_crumb.status_code})")
    
    if crumb and r_crumb.status_code == 200:
        # Step 3: Fetch fundamentals  
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/TATASTEEL.NS?modules=defaultKeyStatistics,financialData,summaryProfile&crumb={crumb}"
        r3 = session.get(url, headers=headers)
        print(f"Fundamentals status: {r3.status_code}")
        if r3.status_code == 200:
            data = r3.json()
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            stats = result.get("defaultKeyStatistics", {})
            fin = result.get("financialData", {})
            prof = result.get("summaryProfile", {})
            print("priceToBook:", stats.get("priceToBook"))
            print("returnOnEquity:", fin.get("returnOnEquity"))
            print("trailingPE:", stats.get("trailingPE"))
            print("sector:", prof.get("sector"))
        else:
            print("Error:", r3.text[:300])
