"""
Direct fast test of screenshot symbol format
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

tv = TvDatafeed()
cookie_str = f"sessionid={tv_session}"
tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})
tv.token = tv_jwt

sym = "NIFTY260728C23550"
exch = "NSE"

print(f"Testing direct query for {exch}:{sym}...")
try:
    df = tv.get_hist(sym, exch, Interval.in_15_minute, 10)
    if df is not None and not df.empty:
        print("SUCCESS! Data retrieved:")
        print(df.tail())
    else:
        print("Empty dataframe returned.")
except Exception as e:
    print("Error:", e)
