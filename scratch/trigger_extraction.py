import urllib.request
import json
import time

url = "http://127.0.0.1:5001/api/extract"
payload = {
    "username": "brokerworkflowhub",
    "password": "Nithik@20252",
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "1 Minute",
    "n_bars": 2000,
    "filename": "nifty_historical_week.xlsx",
    "time_filter": "all",
    "strike_offset": 100,
    "live_today_only": False
}

headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

try:
    print("Sending POST request to /api/extract...")
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        task_id = res_data.get("task_id")
        print(f"Task successfully started! Task ID: {task_id}")
        
        # Now let's poll the task status
        status_url = f"http://127.0.0.1:5001/api/task/{task_id}"
        print(f"Polling task status from {status_url}...")
        
        while True:
            time.sleep(3)
            try:
                with urllib.request.urlopen(status_url) as status_resp:
                    status_data = json.loads(status_resp.read().decode("utf-8"))
                    status = status_data.get("status")
                    logs = status_data.get("logs", [])
                    if logs:
                        print(f"[*] Last Log: {logs[-1]}")
                        
                    if status == "completed":
                        print("\n[+] Extraction successfully completed!")
                        print(f"Output File: {status_data.get('file_path')}")
                        # Let's save a summary of findings
                        preview = status_data.get("preview_summary", [])
                        print(f"Processed {len(preview)} daily summary rows.")
                        for row in preview:
                            print(f"- Date: {row.get('Date')}, Spot 09:28 Close: {row.get('09:28 Close')}, Call Strike: {row.get('Call Strike')}, Put Strike: {row.get('Put Strike')}")
                        break
                    elif status == "failed":
                        print(f"\n[-] Task failed! Error: {status_data.get('error')}")
                        break
            except Exception as pe:
                print(f"Polling error: {pe}")
                break
except Exception as e:
    print(f"Request failed: {e}")
