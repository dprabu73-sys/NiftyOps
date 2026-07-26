"""
Clean JWT auth test - no nologin interference.
"""
import os, json, base64, time, sys
import logging
logging.disable(logging.CRITICAL)  # suppress all tvDatafeed logs during test

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
tv_session = tv_jwt = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TV_SESSION_ID="): tv_session = line.split("=",1)[1]
        elif line.startswith("TV_JWT_TOKEN="): tv_jwt = line.split("=",1)[1]

print(f"Session loaded: {tv_session[:8]}...")
print(f"JWT loaded: {tv_jwt[:40]}...")

# Decode JWT
parts = tv_jwt.split(".")
padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
payload = json.loads(base64.urlsafe_b64decode(padded))
import datetime
exp = datetime.datetime.fromtimestamp(payload.get('exp', 0))
print(f"\nJWT plan='{payload.get('plan','')}' perm='{payload.get('perm','')}' expires={exp}")

from tvDatafeed import TvDatafeed, Interval

# Build authenticated instance
tv = TvDatafeed.__new__(TvDatafeed)
tv.ws_debug = False
tv.token = tv_jwt
tv.ws = None
import string, random
tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))

cookie_str = f"sessionid={tv_session}"
ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})
tv._TvDatafeed__ws_headers = ws_headers

print("\nTesting NIFTY NSE (underlying)...")
try:
    df = tv.get_hist("NIFTY", "NSE", Interval.in_5_minute, 5)
    if df is not None and not df.empty:
        print(f"  OK: {len(df)} bars, last close={df['close'].iloc[-1]:.2f}")
    else:
        print("  FAILED (empty)")
except Exception as e:
    print(f"  ERROR: {e}")

print("\nTesting NIFTY options on NFO...")
options = ["NIFTY26072324000CE", "NIFTY26072323800CE", "NIFTY26072323800PE"]
for sym in options:
    time.sleep(2)
    try:
        df2 = tv.get_hist(sym, "NFO", Interval.in_15_minute, 10)
        if df2 is not None and not df2.empty:
            print(f"  SUCCESS: {sym} -> {len(df2)} bars, last={df2['close'].iloc[-1]:.2f}")
        else:
            print(f"  EMPTY: {sym}")
    except Exception as e:
        print(f"  ERROR: {sym} -> {str(e)[:80]}")

print("\nDone.")
