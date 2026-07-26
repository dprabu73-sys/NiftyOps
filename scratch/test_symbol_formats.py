"""
Test exact TradingView NFO option symbol formats using tvDatafeed
"""
import os, json, time
from tvDatafeed import TvDatafeed, Interval

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
tv_session = tv_jwt = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TV_SESSION_ID="): tv_session = line.split("=",1)[1]
        elif line.startswith("TV_JWT_TOKEN="): tv_jwt = line.split("=",1)[1]

print(f"Session: {tv_session[:8]}...")
print(f"JWT: {tv_jwt[:30]}...")

tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = False
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

# Test underlying
print("\n--- Test 1: NIFTY index ---")
df = tv.get_hist("NIFTY", "NSE", Interval.in_5_minute, 5)
print(f"Index result: {len(df) if df is not None else 'None'} bars")

# Test various NFO option symbol candidates
print("\n--- Test 2: NFO option symbol formats ---")
# Current year 2026 / 2024 test candidates
test_candidates = [
    # YYMMDD format
    ("NIFTY260730C23800", "NFO"),
    ("NIFTY260730P23800", "NFO"),
    ("NIFTY26073023800CE", "NFO"),
    ("NIFTY26073023800PE", "NFO"),
    # Month code format
    ("NIFTY2673023800CE", "NFO"),
    ("NIFTY2673023800PE", "NFO"),
    ("NIFTY26730C23800", "NFO"),
    ("NIFTY26730P23800", "NFO"),
    # Monthly 3-letter month format
    ("NIFTY26JUL23800CE", "NFO"),
    ("NIFTY26JUL23800PE", "NFO"),
    ("NIFTY26JULC23800", "NFO"),
    ("NIFTY26JULP23800", "NFO"),
]

for sym, exch in test_candidates:
    time.sleep(1)
    try:
        data = tv.get_hist(sym, exch, Interval.in_5_minute, 5)
        if data is not None and not data.empty:
            print(f"  ✅ SUCCESS: {sym} ({exch}) -> {len(data)} bars, last={data['close'].iloc[-1]}")
        else:
            print(f"  ❌ FAILED: {sym} ({exch}) -> Empty")
    except Exception as e:
        print(f"  ❌ ERROR: {sym} ({exch}) -> {e}")
