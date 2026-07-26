"""
Deep diagnostic test to find the EXACT symbol format TradingView NFO uses for NIFTY weekly options.
Tests with authenticated session from .env file.
"""
import os
import json
from tvDatafeed import TvDatafeed, Interval

# Load session from .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
tv_session = None
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('TV_SESSION_ID='):
            tv_session = line.split('=', 1)[1].strip()
            break

print(f"Session ID loaded: {tv_session[:8]}..." if tv_session else "NO SESSION FOUND")

# Create authenticated TvDatafeed
tv = TvDatafeed()
if tv_session:
    cookie_str = f"sessionid={tv_session}"
    ws_headers = json.dumps({
        "Origin": "https://data.tradingview.com",
        "Cookie": cookie_str
    })
    tv._TvDatafeed__ws_headers = ws_headers
    tv.token = 'unauthorized_user_token'
    print("Authenticated session injected.")
else:
    print("WARNING: No session, using nologin.")

# Test NIFTY underlying first to confirm auth works
print("\n--- Testing NIFTY underlying ---")
try:
    df = tv.get_hist(symbol="NIFTY", exchange="NSE", interval=Interval.in_5_minute, n_bars=5)
    if df is not None and not df.empty:
        print(f"NIFTY NSE OK: {len(df)} bars, last close: {df['close'].iloc[-1]}")
    else:
        print("NIFTY NSE: EMPTY")
except Exception as e:
    print(f"NIFTY NSE ERROR: {e}")

# Now test NIFTY options with different formats
# Use a recent expiry: July 23, 2026 (Thursday) and strikes near current NIFTY ~24000
print("\n--- Testing NIFTY Options (Jul 23 expiry, Strike 24000) ---")

candidates = [
    # Standard YYMMDD formats
    ("NIFTY26072324000CE", "NFO"),
    ("NIFTY26072324000PE", "NFO"),
    # Single digit month
    ("NIFTY2672324000CE", "NFO"),
    ("NIFTY2672324000PE", "NFO"),
    # Monthly style
    ("NIFTY26JUL24000CE", "NFO"),
    ("NIFTY26JUL24000PE", "NFO"),
    # Try on NSE exchange directly
    ("NIFTY26072324000CE", "NSE"),
    ("NIFTY26072324000PE", "NSE"),
    # Try NIFTY50 format
    ("NIFTY5026072324000CE", "NFO"),
    # Different case
    ("nifty26072324000ce", "NFO"),
    # Older Indian style
    ("NIFTY23JUL26000CE", "NFO"),
]

for sym, exch in candidates:
    try:
        data = tv.get_hist(symbol=sym, exchange=exch, interval=Interval.in_5_minute, n_bars=5)
        if data is not None and not data.empty:
            print(f"SUCCESS: {sym} @ {exch} -> {len(data)} bars, last close: {data['close'].iloc[-1]:.2f}")
        else:
            print(f"FAILED (empty): {sym} @ {exch}")
    except Exception as e:
        print(f"ERROR: {sym} @ {exch} -> {e}")

# Also try search to confirm NFO symbols
print("\n--- Searching for NIFTY symbols on NFO ---")
try:
    results = tv.search_symbol("NIFTY24000", "NFO")
    if results:
        for r in results[:10]:
            print(r)
    else:
        print("No search results")
except Exception as e:
    print(f"Search error: {e}")
