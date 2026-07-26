"""
Test raw TradingView option candle fetching for active upcoming contracts vs expired contracts.
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

print(f"Loaded session: {tv_session[:8]}...")
print(f"Loaded JWT: {tv_jwt[:30]}...")

tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = False
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

# Test upcoming active contract (July 30, 2026 expiry)
upcoming_candidates = [
    ("NIFTY26073023500CE", "NFO"),
    ("NIFTY2673023500CE", "NFO"),
    ("NIFTY26JUL23500CE", "NFO"),
    ("NIFTY260730C23500", "NFO"),
    ("NIFTY26073023500CE", "NSE"),
]

print("\n--- Testing Upcoming Active Contract (Jul 30 Expiry) ---")
for sym, exch in upcoming_candidates:
    time.sleep(1)
    try:
        df = tv.get_hist(sym, exch, Interval.in_5_minute, 10)
        if df is not None and not df.empty:
            print(f"  SUCCESS: {sym} ({exch}) -> {len(df)} bars, last={df['close'].iloc[-1]}")
        else:
            print(f"  EMPTY: {sym} ({exch})")
    except Exception as e:
        print(f"  ERROR: {sym} ({exch}) -> {str(e)[:50]}")

# Test expired contract (July 23, 2026 expiry)
print("\n--- Testing Expired Contract (Jul 23 Expiry - Expired 3 Days Ago) ---")
expired_candidates = [
    ("NIFTY26072323800CE", "NFO"),
    ("NIFTY2672323800CE", "NFO"),
    ("NIFTY26JUL23800CE", "NFO"),
]
for sym, exch in expired_candidates:
    time.sleep(1)
    try:
        df = tv.get_hist(sym, exch, Interval.in_5_minute, 10)
        if df is not None and not df.empty:
            print(f"  SUCCESS: {sym} ({exch}) -> {len(df)} bars, last={df['close'].iloc[-1]}")
        else:
            print(f"  EMPTY (Delisted/Expired): {sym} ({exch})")
    except Exception as e:
        print(f"  ERROR: {sym} ({exch}) -> {str(e)[:50]}")
