"""
Test yfinance primary extraction speed
"""
import requests, time

BASE = "http://127.0.0.1:5005"

payload = {
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5 Minutes",
    "n_bars": 500,
    "filename": "Instant_YF_Test",
    "time_filter": "all",
    "strike_offset": 100
}

start = time.time()
r = requests.post(f"{BASE}/api/extract", json=payload).json()
task_id = r.get("task_id")
print("Job started. Task ID:", task_id)

while time.time() - start < 30:
    tr = requests.get(f"{BASE}/api/task/{task_id}").json()
    status = tr.get("status")
    elapsed = round(time.time() - start, 2)
    print(f"[{elapsed}s] Task status: {status}")
    if status == "completed":
        print(f"SUCCESS: Extraction finished in ONLY {elapsed} seconds!")
        break
    time.sleep(1)
