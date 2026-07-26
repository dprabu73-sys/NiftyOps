"""
Test TvDatafeed with proper session auth AND also test if NIFTY underlying works first.
Uses correct cookie injection approach.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tvDatafeed import TvDatafeed, Interval

# Load session from .env in parent folder
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
tv_session = None
username = None
password = None
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('TV_SESSION_ID='):
            tv_session = line.split('=', 1)[1].strip()
        elif line.startswith('TV_USERNAME='):
            username = line.split('=', 1)[1].strip()
        elif line.startswith('TV_PASSWORD='):
            password = line.split('=', 1)[1].strip()

print(f"Username: {username}")
print(f"Session: {tv_session[:8]}..." if tv_session else "NO SESSION")

# Method 1: Username/Password login
print("\n=== Method 1: Username/Password Login ===")
try:
    tv1 = TvDatafeed(username=username, password=password)
    df = tv1.get_hist(symbol="NIFTY", exchange="NSE", interval=Interval.in_5_minute, n_bars=5)
    if df is not None and not df.empty:
        print(f"NIFTY NSE OK via user/pass: last close={df['close'].iloc[-1]:.2f}")
    else:
        print("NIFTY NSE EMPTY via user/pass")
except Exception as e:
    print(f"Login error: {e}")

# Method 2: Session cookie
print("\n=== Method 2: Session Cookie Injection ===")
try:
    tv2 = TvDatafeed()
    cookie_str = f"sessionid={tv_session}"
    ws_headers = json.dumps({
        "Origin": "https://data.tradingview.com",
        "Cookie": cookie_str
    })
    tv2._TvDatafeed__ws_headers = ws_headers
    tv2.token = 'unauthorized_user_token'
    df2 = tv2.get_hist(symbol="NIFTY", exchange="NSE", interval=Interval.in_5_minute, n_bars=5)
    if df2 is not None and not df2.empty:
        print(f"NIFTY NSE OK via session cookie: last close={df2['close'].iloc[-1]:.2f}")
    else:
        print("NIFTY NSE EMPTY via session cookie")
except Exception as e:
    print(f"Session cookie error: {e}")

# Test BANKNIFTY to confirm auth works
print("\n=== BANKNIFTY underlying test ===")
try:
    df3 = tv2.get_hist(symbol="BANKNIFTY", exchange="NSE", interval=Interval.in_5_minute, n_bars=5)
    if df3 is not None and not df3.empty:
        print(f"BANKNIFTY NSE OK: last close={df3['close'].iloc[-1]:.2f}")
    else:
        print("BANKNIFTY NSE EMPTY")
except Exception as e:
    print(f"BANKNIFTY error: {e}")

# Now test OPTIONS with authenticated session - try multiple formats
print("\n=== NIFTY options symbol format test ===")
# Use July 23 expiry (today)
# Also try July 30 (next Thursday) and past dates
test_symbols = [
    # July 23, 2026 (Thu) - current weekly expiry
    ("NIFTY26072324000CE", "NFO"),
    ("NIFTY26072324000CE", "NSE"),
    # July 30 next expiry
    ("NIFTY26073024000CE", "NFO"),
    # Past expiry: July 17
    ("NIFTY26071724000CE", "NFO"),
    # July 16 expiry
    ("NIFTY26071624000CE", "NFO"),
    # July 9 expiry
    ("NIFTY26070924000CE", "NFO"),
]

# Use the authenticated session
for sym, exch in test_symbols:
    try:
        data = tv2.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=10)
        if data is not None and not data.empty:
            print(f"SUCCESS: {sym}@{exch} -> {len(data)} bars")
        else:
            data2 = tv1.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=10)
            if data2 is not None and not data2.empty:
                print(f"SUCCESS (user/pass): {sym}@{exch} -> {len(data2)} bars")
            else:
                print(f"FAILED both: {sym}@{exch}")
    except Exception as e:
        print(f"ERROR: {sym}@{exch} -> {str(e)[:80]}")
    time.sleep(1)
