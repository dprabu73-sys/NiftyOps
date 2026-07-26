import requests

url = "http://127.0.0.1:5005/api/preview_symbols"
payload = {
    "symbol": "NIFTY",
    "exchange": "NSE",
    "n_bars": 2000,
    "strike_offset": 100
}

try:
    res = requests.post(url, json=payload, timeout=30)
    print("Status code:", res.status_code)
    data = res.json()
    if "symbols" in data:
        print(f"Generated {len(data['symbols'])} symbol previews:")
        for s in data["symbols"][:5]:
            print(s)
    else:
        print("Response:", data)
except Exception as e:
    print("Error testing preview_symbols endpoint:", e)
