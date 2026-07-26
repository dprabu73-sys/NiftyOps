"""
Test: Use TvDatafeed with user/pass login (which now works via user/pass for index)
AND find what token is actually used to see if we can get option data.
"""
import os, json, re, requests
from tvDatafeed import TvDatafeed, Interval

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
username = password = tv_session = None
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('TV_USERNAME='): username = line.split('=',1)[1]
        elif line.startswith('TV_PASSWORD='): password = line.split('=',1)[1]
        elif line.startswith('TV_SESSION_ID='): tv_session = line.split('=',1)[1]

# We know username/password works for NIFTY underlying.
# Check what token is returned from user/pass and try using it for NFO options.
print("=== Checking TV auth flow ===")
sign_in_url = 'https://www.tradingview.com/accounts/signin/'
signin_headers = {'Referer': 'https://www.tradingview.com'}
data = {"username": username, "password": password, "remember": "on"}
try:
    r = requests.post(url=sign_in_url, data=data, headers=signin_headers, timeout=15)
    print(f"Login status: {r.status_code}")
    resp_text = r.text[:500]
    print(f"Response (truncated): {resp_text}")
    print(f"Cookies: {dict(r.cookies)}")

    # Try to extract token
    resp_json = {}
    try:
        resp_json = r.json()
        print(f"JSON keys: {list(resp_json.keys())}")
        if 'user' in resp_json:
            print(f"User keys: {list(resp_json['user'].keys())}")
            if 'auth_token' in resp_json['user']:
                jwt = resp_json['user']['auth_token']
                print(f"JWT from user.auth_token: {jwt[:40]}...")
    except Exception as je:
        print(f"JSON parse error: {je}")

    # Check for JWT in cookies
    cookie_sessionid = r.cookies.get('sessionid')
    if cookie_sessionid:
        print(f"Session cookie from login: {cookie_sessionid[:10]}...")
    
    # Check auth_token in cookies
    cookie_auth = r.cookies.get('auth_token')
    if cookie_auth:
        print(f"Auth token cookie: {cookie_auth[:20]}...")

except Exception as e:
    print(f"Login error: {e}")

print("\n=== Testing Option with user/pass TvDatafeed (token check) ===")
tv = TvDatafeed(username=username, password=password)
print(f"TV token: {str(tv.token)[:40]}...")

# Enable debug to see WS messages
tv.ws_debug = True
try:
    df = tv.get_hist(symbol="NIFTY26072324000CE", exchange="NFO", interval=Interval.in_5_minute, n_bars=5)
    if df is not None and not df.empty:
        print(f"SUCCESS: NIFTY26072324000CE NFO: {len(df)} bars")
    else:
        print("EMPTY: No data returned for option")
except Exception as e:
    print(f"Error: {e}")
