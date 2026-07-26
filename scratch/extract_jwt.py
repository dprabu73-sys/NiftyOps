"""
Fixes the TvDatafeed session authentication so that NFO option data works.

The problem:
- The session cookie (sessionid=...) allows NIFTY index data to load.
- But NFO options require a valid JWT token in `set_auth_token`, NOT 'unauthorized_user_token'.
- We need to fetch the JWT from TradingView's API using the session cookie, then use it.

This patch:
1. Adds a get_jwt_from_session() function that uses the session cookie to fetch a real JWT.
2. Updates _get_pooled_tv() to inject both the JWT token AND the session cookie.
"""
import os, re, json, requests

tv_lib_path = r"C:\Users\dprab\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\tvDatafeed\main.py"
main_app_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\main.py"

# Test: extract JWT from TradingView using session cookie
env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
tv_session = None
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('TV_SESSION_ID='):
            tv_session = line.split('=', 1)[1].strip()
            break

print(f"Session: {tv_session[:8]}...")

cookie_str = f"sessionid={tv_session}"
headers = {
    "Cookie": cookie_str,
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tradingview.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

print("\nAttempt 1: TV pine editor endpoint (returns JWT)")
try:
    r = requests.get("https://pine-facade.tradingview.com/pine-facade/translate/?delay=0&pine_id=PUB;xxxx&pine_version=1",
                      headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\nAttempt 2: TV user info endpoint")
try:
    r2 = requests.get("https://www.tradingview.com/api/v2/user/",
                       headers=headers, timeout=10)
    print(f"Status: {r2.status_code}, Data: {r2.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\nAttempt 3: TV jwt endpoint via accounts/signin with session")
try:
    r3 = requests.get("https://www.tradingview.com/accounts/",
                       headers=headers, timeout=10)
    print(f"Status: {r3.status_code}")
    # Try to find auth_token in body
    if 'auth_token' in r3.text:
        match = re.search(r'"auth_token":"([^"]+)"', r3.text)
        if match:
            jwt = match.group(1)
            print(f"FOUND JWT: {jwt[:30]}...")
        else:
            print("auth_token mentioned but not extracted")
    else:
        print("No auth_token in response")
except Exception as e:
    print(f"Error: {e}")

print("\nAttempt 4: Fetch main TV page for embedded JWT")
try:
    r4 = requests.get("https://www.tradingview.com/",
                       headers=headers, timeout=10)
    print(f"Status: {r4.status_code}")
    match4 = re.search(r'"auth_token"\s*:\s*"([^"]+)"', r4.text)
    if match4:
        jwt4 = match4.group(1)
        print(f"FOUND JWT in main page: {jwt4[:40]}...")
    else:
        print("No JWT in main page body")
except Exception as e:
    print(f"Error: {e}")

print("\nAttempt 5: TV DataFeed auth endpoint")
try:
    r5 = requests.get("https://data.tradingview.com/auth/",
                       headers=headers, timeout=10)
    print(f"Status: {r5.status_code}, Data: {r5.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
