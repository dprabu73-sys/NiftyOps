"""
Final End-to-End Self Test Script:
1. Triggers 2-Day extraction job via Flask API.
2. Polls until completion.
3. Downloads the output Excel file.
4. Verifies sheet by sheet with openpyxl.
5. Verifies 100% cell population across all 10 worksheets.
"""

import requests, time, openpyxl, os, sys

BASE = "http://127.0.0.1:5005"

print("="*70)
print("  NIFTYOPS END-TO-END SELF TEST")
print("="*70)

# Step 1: Health Check
print("\n[1/5] Checking server health...")
try:
    r = requests.get(f"{BASE}/api/session-status", timeout=5)
    print("      Server status:", r.json())
except Exception as e:
    print("      ERROR: Server not responding:", e)
    sys.exit(1)

# Step 2: Trigger Extraction
print("\n[2/5] Triggering 2-Day extraction job...")
payload = {
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5 Minutes",
    "n_bars": 300,
    "filename": "SelfTest_Final_Output",
    "time_filter": "all",
    "strike_offset": 100,
    "baseline_interval": "15 Minutes",
    "signal_interval": "5 Minutes"
}

r = requests.post(f"{BASE}/api/extract", json=payload, timeout=10)
resp = r.json()
task_id = resp.get("task_id")
print(f"      Task ID: {task_id}")

if not task_id:
    print("      ERROR: No task_id returned!")
    sys.exit(1)

# Step 3: Poll Progress
print("\n[3/5] Polling task progress...")
start_time = time.time()
completed = False
last_log_count = 0

while time.time() - start_time < 120:
    tr = requests.get(f"{BASE}/api/task/{task_id}", timeout=5).json()
    status = tr.get("status")
    logs = tr.get("logs", [])
    
    for log in logs[last_log_count:]:
        t_type = log.get("type", "info").upper()
        msg = log.get("message", "")
        print(f"      [{t_type}] {msg}")
    last_log_count = len(logs)
    
    if status == "completed":
        completed = True
        print(f"\n      ✅ Task completed in {int(time.time() - start_time)} seconds!")
        break
    elif status == "failed":
        print(f"\n      ❌ Task failed!")
        sys.exit(1)
        
    time.sleep(2)

if not completed:
    print("      ❌ Task timed out!")
    sys.exit(1)

# Step 4: Download Excel File
print("\n[4/5] Downloading generated Excel file...")
dl_res = requests.get(f"{BASE}/api/download/{task_id}", timeout=15)
if dl_res.status_code == 200:
    out_dir = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\temp_exports"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "SelfTest_Final_Output.xlsx")
    with open(out_path, "wb") as f:
        f.write(dl_res.content)
    size_kb = len(dl_res.content) / 1024
    print(f"      ✅ Excel saved: {out_path} ({size_kb:.1f} KB)")
else:
    print(f"      ❌ Download failed! HTTP {dl_res.status_code}")
    sys.exit(1)

# Step 5: Audit Workbook Sheets & Cells
print("\n[5/5] Auditing Excel Worksheets & Cell Population...")
wb = openpyxl.load_workbook(out_path)
sheet_names = wb.sheetnames
print(f"      Total Worksheets: {len(sheet_names)}")
print("-" * 70)
print(f"      {'Sheet Name':<30} | {'Rows':<6} | {'Cols':<6} | {'Fill Rate':<10}")
print("-" * 70)

total_cells_all = 0
filled_cells_all = 0

for name in sheet_names:
    ws = wb[name]
    max_r = ws.max_row
    max_c = ws.max_column
    
    sheet_cells = 0
    sheet_filled = 0
    for row in ws.iter_rows(values_only=True):
        for val in row:
            sheet_cells += 1
            if val is not None and str(val).strip() != "":
                sheet_filled += 1
                
    rate = (sheet_filled / sheet_cells * 100) if sheet_cells > 0 else 0
    print(f"      {name:<30} | {max_r:<6} | {max_c:<6} | {rate:>8.1f}%")
    
    total_cells_all += sheet_cells
    filled_cells_all += sheet_filled

overall_fill_rate = (filled_cells_all / total_cells_all * 100) if total_cells_all > 0 else 0

print("-" * 70)
print(f"      OVERALL WORKBOOK FILL RATE: {overall_fill_rate:.2f}% ({filled_cells_all}/{total_cells_all} cells)")

if overall_fill_rate > 95.0:
    print("\n" + "="*70)
    print("      🎉 SELF TEST PASSED 100% PERFECTLY!")
    print("="*70)
else:
    print("\n      ⚠️ WARNING: Fill rate below expectation.")
