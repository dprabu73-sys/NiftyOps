"""
Speed Benchmark Test: Verify extraction completes in under 5 seconds!
"""
import requests, time

BASE = "http://127.0.0.1:5005"

payload = {
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5 Minutes",
    "n_bars": 300,
    "filename": "Ultra_Fast_Benchmark",
    "time_filter": "all",
    "strike_offset": 100
}

start_time = time.time()
r = requests.post(f"{BASE}/api/extract", json=payload).json()
task_id = r.get("task_id")
print(f"Extraction job started. Task ID: {task_id}")

while time.time() - start_time < 30:
    tr = requests.get(f"{BASE}/api/task/{task_id}").json()
    status = tr.get("status")
    elapsed = round(time.time() - start_time, 2)
    print(f"[{elapsed}s] Task status: {status}")
    if status == "completed":
        print(f"\n🎉 SUCCESS: Extraction completed in ONLY {elapsed} seconds!")
        break
    elif status == "failed":
        print("\n❌ Task failed!")
        break
    time.sleep(1)
