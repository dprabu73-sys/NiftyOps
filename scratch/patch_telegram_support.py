"""
Patch main.py to integrate Telegram Bot push alert triggers and endpoints.
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

telegram_helper_code = """
# ── Telegram Push Alert Engine ────────────────────────────────────────────────
def send_telegram_alert(message, bot_token=None, chat_id=None):
    import os, requests
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
    cid = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not cid:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": cid,
            "text": message,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram alert error: {e}")
        return False
"""

if "def send_telegram_alert" not in content:
    content = telegram_helper_code + "\n" + content

telegram_endpoints = """
@app.route('/api/test-telegram', methods=['POST'])
def test_telegram():
    data = request.get_json() or {}
    token = data.get('bot_token') or os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = data.get('chat_id') or os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not token or not chat_id:
        return jsonify({'status': 'error', 'message': 'Missing Telegram Bot Token or Chat ID'}), 400
        
    msg = "🔔 *NiftyOps Test Notification*\\n\\nYour Telegram Bot alerts are connected and working 100% cleanly on 4G/5G!"
    success = send_telegram_alert(msg, bot_token=token, chat_id=chat_id)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Test alert sent successfully to Telegram!'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send Telegram alert. Check Token & Chat ID.'}), 400
"""

if "/api/test-telegram" not in content:
    content = content + "\n" + telegram_endpoints

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully integrated Telegram Bot Alert engine into main.py!")
