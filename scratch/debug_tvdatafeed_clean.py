"""
Clean diagnostic script (no emoji prints) inspecting TV WebSocket responses for options.
"""
import os, sys, json, time
from tvDatafeed import TvDatafeed, Interval

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
tv_session = tv_jwt = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TV_SESSION_ID="): tv_session = line.split("=",1)[1]
        elif line.startswith("TV_JWT_TOKEN="): tv_jwt = line.split("=",1)[1]

tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = True
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

test_symbols = [
    ("NSE", "NIFTY"),
    ("NFO", "NIFTY260730C23500"),
    ("NFO", "NIFTY26073023500CE"),
    ("NSE", "NIFTY26073023500CE"),
]

for exch, sym in test_symbols:
    print(f"\n==========================================")
    print(f"Testing: {exch}:{sym}")
    print(f"==========================================")
    try:
        df = tv.get_hist(symbol=sym, exchange=exch, interval=Interval.in_5_minute, n_bars=5)
        if df is not None and not df.empty:
            print(f"SUCCESS: {exch}:{sym} -> {len(df)} bars, last={df['close'].iloc[-1]}")
        else:
            print(f"EMPTY: {exch}:{sym}")
    except Exception as e:
        print(f"ERROR: {exch}:{sym} -> {e}")
    time.sleep(2)
