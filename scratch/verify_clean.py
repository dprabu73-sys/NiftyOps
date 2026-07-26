"""
Self test verification script (No UTF-8 emoji console print errors).
"""
import requests, time, openpyxl, os

BASE = "http://127.0.0.1:5005"
task_id = "65bcfc2a-61c3-41f0-a825-6ce92aa99324"

print("Monitoring Task:", task_id)
start = time.time()
while time.time() - start < 180:
    r = requests.get(f"{BASE}/api/task/{task_id}").json()
    status = r.get("status")
    print(f"[{int(time.time() - start)}s] Task Status: {status}")
    if status in ("completed", "failed"):
        break
    time.sleep(5)

if status == "completed":
    dl = requests.get(f"{BASE}/api/download/{task_id}")
    out_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\temp_exports\SelfTest_Clean_Output.xlsx"
    with open(out_path, "wb") as f:
        f.write(dl.content)
    print(f"SUCCESS: Excel saved to {out_path} ({len(dl.content)} bytes)")
    
    wb = openpyxl.load_workbook(out_path)
    print(f"Total Sheets: {len(wb.sheetnames)}")
    total_cells = 0
    filled_cells = 0
    for s_name in wb.sheetnames:
        ws = wb[s_name]
        s_total = 0
        s_filled = 0
        for row in ws.iter_rows(values_only=True):
            for val in row:
                s_total += 1
                if val is not None and str(val).strip() != "":
                    s_filled += 1
        total_cells += s_total
        filled_cells += s_filled
        rate = (s_filled / s_total * 100) if s_total > 0 else 0
        print(f"  - Sheet '{s_name}': {ws.max_row} rows x {ws.max_column} cols, fill rate: {rate:.1f}%")
        
    overall_rate = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    print(f"\nOVERALL EXCEL FILL RATE: {overall_rate:.2f}% ({filled_cells}/{total_cells} cells)")
else:
    print("Task status is not completed:", status)
