"""
Test EXACT TradingView symbol format from user screenshot:
NSE:NIFTY{YYMMDD}{C/P}{STRIKE} e.g. NSE:NIFTY260728C23550 or NSE:NIFTY260723C23800
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

# Exact screenshot symbols
test_symbols = [
    ("NSE", "NIFTY260728C23550"),
    ("NSE", "NIFTY260728P23550"),
    ("NSE", "NIFTY260723C23800"),
    ("NSE", "NIFTY260723P24100"),
    ("NSE", "NIFTY260730C23500"),
    ("NSE", "NIFTY260730P23800"),
]

print("\n--- Testing EXACT Screenshot Symbol Formats ---")
for exch, sym in test_symbols:
    time.sleep(1)
    try:
        df = tv.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=10)
        if df is not None and not df.empty:
            print(f"SUCCESS: {exch}:{sym} -> {len(df)} bars, last close={df['close'].iloc[-1]:.2f}")
        else:
            print(f"EMPTY: {exch}:{sym}")
    except Exception as e:
        print(f"ERROR: {exch}:{sym} -> {e}")
