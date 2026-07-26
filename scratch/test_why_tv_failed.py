"""
Test why TradingView query returned empty for NIFTY260730C23500
"""
from tvDatafeed import TvDatafeed, Interval
import os
from dotenv import load_dotenv

load_dotenv()
tv_session = os.getenv("TV_SESSION_ID", "")
tv_jwt = os.getenv("TV_JWT_TOKEN", "")

print("1. Testing with clean guest TvDatafeed()...")
tv_guest = TvDatafeed()
df1 = tv_guest.get_hist(symbol="NIFTY260730C23500", exchange="NSE", interval=Interval.in_15_minute, n_bars=100)
print("Guest session result for NSE:NIFTY260730C23500:")
print(df1 if df1 is not None else "None")

print("\n2. Testing with session token...")
if tv_session:
    if tv_session.startswith("sessionid="):
        t_val = tv_session[len("sessionid="):]
    else:
        t_val = tv_session
    tv_auth = TvDatafeed(username=t_val, password="") # or session
    df2 = tv_auth.get_hist(symbol="NIFTY260730C23500", exchange="NSE", interval=Interval.in_15_minute, n_bars=100)
    print("Auth session result for NSE:NIFTY260730C23500:")
    print(df2 if df2 is not None else "None")

print("\n3. Testing alternative symbol candidates...")
cands = [
    ("NSE", "NIFTY260730C23500"),
    ("NSE", "NIFTY260730C23500"),
    ("NSE", "NIFTY26073023500CE"),
    ("NFO", "NIFTY26073023500CE"),
    ("NFO", "NIFTY2673023500CE"),
]

for exch, sym in cands:
    df_c = tv_guest.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=50)
    if df_c is not None and not df_c.empty:
        print(f"✅ SUCCESS: {exch}:{sym} returned {len(df_c)} bars!")
    else:
        print(f"❌ FAILED: {exch}:{sym} returned None")
