"""
Deep diagnostic script: inspect tvDatafeed symbol lookup & WebSocket messages for NFO options.
"""
import os, sys, json, time

# Find tvDatafeed package path
import tvDatafeed
tv_path = tvDatafeed.__file__
print(f"tvDatafeed file location: {tv_path}")

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
tv_session = tv_jwt = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TV_SESSION_ID="): tv_session = line.split("=",1)[1]
        elif line.startswith("TV_JWT_TOKEN="): tv_jwt = line.split("=",1)[1]

from tvDatafeed import TvDatafeed, Interval

# Create TvDatafeed instance with debug enabled
tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = True  # Enable verbose WebSocket debug logging to see exact TV messages!
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

print("\n--- Testing Symbol Resolving over WebSocket ---")
test_symbols = [
    ("NSE:NIFTY", "NIFTY underlying"),
    ("NFO:NIFTY260730C23500", "NFO option C format"),
    ("NFO:NIFTY26073023500CE", "NFO option CE format"),
    ("NSE:NIFTY26073023500CE", "NSE option CE format"),
]

for sym_full, desc in test_symbols:
    print(f"\n==========================================")
    print(f"Testing: {sym_full} ({desc})")
    print(f"==========================================")
    parts = sym_full.split(":")
    ex = parts[0]
    sy = parts[1]
    try:
        df = tv.get_hist(symbol=sy, exchange=ex, interval=Interval.in_5_minute, n_bars=5)
        if df is not None and not df.empty:
            print(f"✅ SUCCESS: {sym_full} -> {len(df)} bars")
            print(df.tail(2))
        else:
            print(f"❌ EMPTY: {sym_full}")
    except Exception as e:
        print(f"❌ ERROR: {sym_full} -> {e}")
    time.sleep(2)
