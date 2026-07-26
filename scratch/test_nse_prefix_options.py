"""
Test fetching options using exchange="NSE" (since TV catalogs both equities & options under NSE)
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

tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = False
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

test_symbols = [
    "NIFTY26073023500CE",
    "NIFTY260730C23500",
    "NIFTY2673023500CE",
    "NIFTY26JUL23500CE",
    "NIFTY26073023800PE",
    "NIFTY260730P23800"
]

print("--- Testing Options with exchange='NSE' ---")
for sym in test_symbols:
    time.sleep(1)
    try:
        df = tv.get_hist(symbol=sym, exchange="NSE", interval=Interval.in_5_minute, n_bars=10)
        if df is not None and not df.empty:
            print(f"SUCCESS: NSE:{sym} -> {len(df)} bars, last={df['close'].iloc[-1]}")
        else:
            print(f"EMPTY: NSE:{sym}")
    except Exception as e:
        print(f"ERROR: NSE:{sym} -> {str(e)[:60]}")
