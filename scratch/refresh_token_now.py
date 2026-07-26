"""
Refresh token script: run Selenium login to fetch fresh JWT token.
"""
import os, time, json, base64, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"

opts = ChromeOptions()
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
opts.add_argument("--window-size=1100,900")
opts.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=opts)
try:
    driver.get("https://www.tradingview.com/accounts/signin/")
    time.sleep(3)

    try:
        email_btn = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Email']"))
        )
        ActionChains(driver).move_to_element(email_btn).pause(0.3).click().perform()
        time.sleep(2)
    except Exception:
        pass

    try:
        u_input = WebDriverWait(driver, 8).until(
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
        print("Login submitted.")
    except Exception as e:
        print("Login form note:", e)

    new_sid = None
    new_jwt = None
    start = time.time()
    while time.time() - start < 45:
        for ck in driver.get_cookies():
            if ck.get('name') == 'sessionid' and 'tradingview.com' in ck.get('domain', ''):
                new_sid = ck['value']
                break

        try:
            val = driver.execute_script("return window.localStorage.getItem('auth_token') || (JSON.parse(window.localStorage.getItem('tv_user_logged_in_data')||'{}')).auth_token || '';")
            if val and str(val).startswith('eyJ'):
                new_jwt = str(val).strip()
        except Exception:
            pass

        if not new_jwt:
            m = re.search(r'"auth_token"\s*:\s*"(eyJ[A-Za-z0-9_\-\.]+)"', driver.page_source)
            if m:
                new_jwt = m.group(1)

        if new_sid and new_jwt:
            break

        time.sleep(2)

    driver.quit()

    if new_sid and new_jwt:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            lines = [l for l in lines if not l.startswith('TV_SESSION_ID=') and not l.startswith('TV_JWT_TOKEN=')]
        lines.append(f"TV_SESSION_ID={new_sid}\n")
        lines.append(f"TV_JWT_TOKEN={new_jwt}\n")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        parts = new_jwt.split(".")
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        print("Refreshed Token Payload:")
        print(f"  plan: '{payload.get('plan','')}'")
        print(f"  perm: '{payload.get('perm','')}'")
        print(f"  prostatus: '{payload.get('prostatus')}'")
    else:
        print("Could not capture new token.")

except Exception as e:
    print("Refresh error:", e)
    try: driver.quit()
    except: pass
