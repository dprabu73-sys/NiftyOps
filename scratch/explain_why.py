"""
Test if current active week options vs past expired options return data.
"""
import json, time, datetime
from tvDatafeed import TvDatafeed, Interval

# Load session & JWT
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
ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})
tv._TvDatafeed__ws_headers = ws_headers

# Test 1: NIFTY index (should work)
print("1. Testing NIFTY index:")
try:
    df = tv.get_hist("NIFTY", "NSE", Interval.in_5_minute, 5)
    print(f"   Index result: {len(df) if df is not None else 'None'} bars")
except Exception as e:
    print(f"   Index error: {e}")

# Test 2: Search for NIFTY options directly via TradingView symbol search API
print("\n2. Searching TV for active NFO option symbols:")
import requests
headers = {"User-Agent": "Mozilla/5.0", "Cookie": cookie_str}
url = "https://symbol-search.tradingview.com/symbol_search/?text=NIFTY24&exchange=NFO"
try:
    r = requests.get(url, headers=headers, timeout=10)
    res = r.json()
    print(f"   Search returned {len(res)} items")
    for item in res[:5]:
        print(f"   Symbol: {item.get('symbol')} | Description: {item.get('description')} | Exch: {item.get('exchange')}")
except Exception as e:
    print(f"   Search error: {e}")
