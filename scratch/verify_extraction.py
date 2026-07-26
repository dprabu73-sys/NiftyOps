"""
Test extraction job with synthetic option fallback engine.
"""
import requests, time, json, openpyxl

BASE = "http://127.0.0.1:5005"

payload = {
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5 Minutes",
    "n_bars": 800,
    "filename": "Verification_Full_Data",
    "time_filter": "last5",
    "strike_offset": 100,
    "baseline_interval": "15 Minutes",
    "signal_interval": "5 Minutes"
}

print("Starting extraction job...")
r = requests.post(f"{BASE}/api/extract", json=payload)
data = r.json()
task_id = data.get("task_id")
print("Task ID:", task_id)

deadline = time.time() + 180
while time.time() < deadline:
    tr = requests.get(f"{BASE}/api/task/{task_id}").json()
    status = tr.get("status")
    print(f"Status: {status}")
    if status in ("completed", "failed"):
        break
    time.sleep(4)

if status == "completed":
    dl = requests.get(f"{BASE}/api/download/{task_id}")
    file_path = "scratch/Verification_Full_Data.xlsx"
    with open(file_path, "wb") as f:
        f.write(dl.content)
    print(f"Excel downloaded successfully! Size: {len(dl.content)} bytes")
    
    wb = openpyxl.load_workbook(file_path)
    print(f"Workbook sheets: {wb.sheetnames}")
    total_cells = 0
    empty_cells = 0
    for name in wb.sheetnames:
        ws = wb[name]
        for row in ws.iter_rows(values_only=True):
            for val in row:
                total_cells += 1
                if val is None or val == "":
                    empty_cells += 1
    print(f"Total cells: {total_cells}, Empty cells: {empty_cells}")
    print("CELL POPULATION RATE:", f"{(1 - empty_cells/total_cells)*100:.2f}%")
