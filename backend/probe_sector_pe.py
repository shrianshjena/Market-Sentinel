import httpx

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

with httpx.Client(follow_redirects=True, timeout=12.0) as s:
    s.get("https://www.nseindia.com/", headers=headers)
    for sym in ["COALINDIA", "TATASTEEL", "NATIONALUM", "HINDCOPPER", "HINDZINC"]:
        r = s.get(f"https://www.nseindia.com/api/quote-equity?symbol={sym}", headers=headers)
        if r.status_code == 200:
            d = r.json()
            meta = d.get("metadata", {})
            ind_info = d.get("industryInfo", {})
            sym_pe = meta.get("pdSymbolPe")
            sec_pe = meta.get("pdSectorPe")
            sec_ind = meta.get("pdSectorInd")
            sector = ind_info.get("sector")
            industry = ind_info.get("industry")
            same = abs((sym_pe or 0) - (sec_pe or 0)) < 0.01
            print(f"{sym}: symbolPE={sym_pe} sectorPE={sec_pe} sectorIdx={sec_ind} | {sector}/{industry} | SAME={same}")
        else:
            print(f"{sym}: HTTP {r.status_code}")
