"""
Refresh token script:
1. Clears old cached token from .env
2. Runs Selenium login to capture the NEW Essential plan session & JWT from TradingView
3. Tests NFO option fetching with the new token
"""
import os, time, json, base64, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

print("=== 1. Clearing old cached token from .env ===")
env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = [l for l in lines if not l.startswith("TV_SESSION_ID=") and not l.startswith("TV_JWT_TOKEN=")]
with open(env_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(".env cleaned.")

print("\n=== 2. Launching Chrome to capture NEW session & JWT ===")
opts = ChromeOptions()
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
opts.add_argument("--window-size=1100,900")
opts.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=opts)
try:
    driver.get("https://www.tradingview.com/accounts/signin/")
    time.sleep(3)

    # Click Email button if present
    try:
        email_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Email']"))
        )
        ActionChains(driver).move_to_element(email_btn).pause(0.3).click().perform()
        time.sleep(2)
    except Exception:
        pass

    # Enter username & password
    try:
        u_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "id_username"))
        )
        u_input.clear()
        u_input.send_keys("brokerworkflowhub")
        time.sleep(0.5)

        p_input = driver.find_element(By.NAME, "id_password")
        p_input.clear()
        p_input.send_keys("Nithik@20252")
        time.sleep(0.5)
        p_input.send_keys(Keys.RETURN)
        print("Credentials submitted. Waiting for login completion...")
    except Exception as e:
        print(f"Form submission note: {e}")

    # Poll for sessionid & JWT for up to 60 seconds
    new_sid = None
    new_jwt = None
    start = time.time()
    while time.time() - start < 60:
        for ck in driver.get_cookies():
            if ck.get('name') == 'sessionid' and 'tradingview.com' in ck.get('domain', ''):
                new_sid = ck['value']
                break

        # Check localStorage for JWT
        try:
            val = driver.execute_script("return window.localStorage.getItem('auth_token') || (JSON.parse(window.localStorage.getItem('tv_user_logged_in_data')||'{}')).auth_token || '';")
            if val and str(val).startswith('eyJ'):
                new_jwt = str(val).strip()
        except Exception:
            pass

        if not new_jwt:
            # Scrape from page source
            m = re.search(r'"auth_token"\s*:\s*"(eyJ[A-Za-z0-9_\-\.]+)"', driver.page_source)
            if m:
                new_jwt = m.group(1)

        if new_sid and new_jwt:
            print("Successfully captured NEW sessionid and NEW JWT!")
            break

        time.sleep(2)

    driver.quit()

    if new_sid and new_jwt:
        # Save to .env
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write(f"TV_SESSION_ID={new_sid}\n")
            f.write(f"TV_JWT_TOKEN={new_jwt}\n")
        print("NEW credentials saved to .env!")

        # Decode JWT to check permissions
        parts = new_jwt.split(".")
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        print(f"\nNEW JWT Payload:")
        print(f"  plan: '{payload.get('plan','')}'")
        print(f"  perm: '{payload.get('perm','')}'")
        print(f"  prostatus: {payload.get('prostatus')}")

        # Test fetching option
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed.__new__(TvDatafeed)
        tv.ws_debug = False
        tv.token = new_jwt
        tv.ws = None
        import string, random
        tv.session = "qs_" + "".join(random.choices(string.ascii_lowercase, k=12))
        tv.chart_session = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
        cookie_str = f"sessionid={new_sid}"
        tv._TvDatafeed__ws_headers = json.dumps({"Origin": "https://data.tradingview.com", "Cookie": cookie_str})

        print("\n=== Testing Option Fetch with NEW Essential Token ===")
        df = tv.get_hist("NIFTY26072324100CE", "NFO", Interval.in_15_minute, 10)
        if df is not None and not df.empty:
            print(f"SUCCESS! NIFTY26072324100CE -> {len(df)} bars fetched cleanly!")
        else:
            print("Option fetch returned empty.")
    else:
        print(f"Failed to capture both. sid={bool(new_sid)}, jwt={bool(new_jwt)}")

except Exception as e:
    print(f"Error during refresh: {e}")
    try: driver.quit()
    except: pass
