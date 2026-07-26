import requests

url = "https://symbol-search.tradingview.com/symbol_search/v3/?text=NIFTY&hl=1&exchange=NFO&lang=en&search_type=options"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/"
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
try:
    data = r.json()
    symbols = data.get('symbols', [])
    print(f"Found {len(symbols)} option symbols:")
    for s in symbols[:10]:
        print(f"Symbol: {s.get('symbol')}, ProName: {s.get('pro_name')}, Exch: {s.get('exchange')}, Typespecs: {s.get('typespecs')}")
except Exception as e:
    print("Error parsing JSON:", e, r.text[:300])
