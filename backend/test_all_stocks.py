import sys, time
sys.path.insert(0, '.')
from services.nse_service import fetch_stock_fundamentals
from services.sentinel_scorer import _score_fundamentals

stocks = ['TATASTEEL', 'COALINDIA', 'NATIONALUM', 'HINDCOPPER', 'HINDZINC']
for sym in stocks:
    t0 = time.time()
    f = fetch_stock_fundamentals(sym)
    score = _score_fundamentals(f)
    print(f"{sym}: PE={f['pe_ratio']}, SectorPE={f['sector_pe']}, Score={score}/100 [{f['sector']}] ({time.time()-t0:.1f}s)")
    print()
