"""
Quick test: use the JWT + session from .env and try fetching a NIFTY option directly.
Also decode JWT to check what permissions it has.
"""
import os, json, base64, time
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

# Decode JWT payload (middle part)
try:
    parts = tv_jwt.split(".")
    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))
    print(f"\nJWT Payload:")
    print(f"  plan: '{payload.get('plan','')}'")
    print(f"  perm: '{payload.get('perm','')}'")
    print(f"  prostatus: {payload.get('prostatus')}")
    print(f"  exp: {payload.get('exp')} (unix)")
    import datetime
    exp_dt = datetime.datetime.fromtimestamp(payload.get('exp', 0))
    print(f"  expires: {exp_dt}")
    print(f"  max_charts: {payload.get('max_charts')}")
    print(f"  fields_permissions: {payload.get('fields_permissions')}")
except Exception as e:
    print(f"JWT decode error: {e}")

# Build authenticated TvDatafeed
print("\n--- Building authenticated TV instance ---")
tv = TvDatafeed()
cookie_str = f"sessionid={tv_session}"
ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})
tv._TvDatafeed__ws_headers = ws_headers
tv.token = tv_jwt
print(f"Token set (len={len(tv_jwt)})")

# Test NIFTY underlying
print("\n--- Test 1: NIFTY NSE underlying ---")
df = tv.get_hist("NIFTY", "NSE", Interval.in_5_minute, 5)
if df is not None and not df.empty:
    print(f"NIFTY NSE OK: {len(df)} bars, last={df['close'].iloc[-1]:.2f}")
else:
    print("NIFTY NSE FAILED")

# Test NFO options
print("\n--- Test 2: NIFTY options on NFO ---")
test_syms = [
    "NIFTY26072324000CE",
    "NIFTY26072323800CE",
    "NIFTY26072324200CE",
]
for sym in test_syms:
    try:
        time.sleep(1)
        df2 = tv.get_hist(sym, "NFO", Interval.in_15_minute, 10)
        if df2 is not None and not df2.empty:
            print(f"  SUCCESS: {sym} -> {len(df2)} bars, last={df2['close'].iloc[-1]:.2f}")
        else:
            print(f"  FAILED (empty): {sym}")
    except Exception as e:
        print(f"  ERROR: {sym} -> {str(e)[:60]}")
