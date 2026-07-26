"""Patch: add /api/set-jwt endpoint and fix /api/set-session to flush JWT cache."""
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the end of set_session function and add the new endpoint after it
# Also patch set_session to clear cached JWT and flush pool

old_session_end = """    msg = 'Session saved! Full options access enabled.' if session_token else 'Session cleared.'
    resp = jsonify({'ok': True, 'message': msg})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp"""

new_session_end = """    # Remove cached JWT so a fresh one is auto-fetched for the new session
    lines = [l for l in lines if not l.startswith('TV_JWT_TOKEN=')]
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    _flush_tv_pool()  # Force fresh TV connection with new session
    msg = 'Session saved! Full options access enabled.' if session_token else 'Session cleared.'
    resp = jsonify({'ok': True, 'message': msg})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp"""

# Make sure we only replace inside set_session (not elsewhere)
if old_session_end in content:
    # Replace only first occurrence (inside set_session)
    content = content.replace(old_session_end, new_session_end, 1)
    print("Patched set_session to clear JWT cache on session change.")
else:
    print("WARNING: Could not find old_session_end text.")

# Add /api/set-jwt endpoint right after set_session
set_jwt_endpoint = '''

@app.route('/api/set-jwt', methods=['POST', 'OPTIONS'])
def set_jwt_token():
    """Save a TradingView JWT auth token to .env for NFO options data access.

    How to get your JWT token:
    1. Open TradingView.com in Chrome (logged in)
    2. Press F12 > Network tab > filter by "tradingview.com"
    3. Reload the page, find any authenticated XHR request
    4. Look for the 'Authorization: Bearer eyJ...' header value
       OR open Application > Local Storage > tradingview.com > find auth_token key
    5. Copy the JWT (starts with eyJ) and paste it here.
    """
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    data = request.get_json(force=True) or {}
    jwt_token = (data.get('jwt_token') or data.get('token') or '').strip()

    if not jwt_token:
        return jsonify({'ok': False, 'error': 'No JWT token provided'}), 400

    # Basic JWT validation: must start with eyJ (base64 encoded JSON header)
    if not jwt_token.startswith('eyJ'):
        return jsonify({'ok': False, 'error': 'Invalid JWT format. Token must start with eyJ...'}), 400

    import os as _os
    env_path = _os.path.join(_os.path.dirname(__file__), '.env')
    lines = []
    found = False
    if _os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('TV_JWT_TOKEN='):
                lines[i] = f'TV_JWT_TOKEN={jwt_token}\\n'
                found = True
                break
    if not found:
        lines.append(f'TV_JWT_TOKEN={jwt_token}\\n')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    _flush_tv_pool()  # Force fresh TV connection with new JWT
    resp = jsonify({'ok': True, 'message': f'JWT token saved (length={len(jwt_token)}). NFO options access enabled!'})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

'''

# Insert right after set_session function
marker = "@app.route('/api/session-status'"
if marker in content and "def set_jwt_token" not in content:
    content = content.replace(marker, set_jwt_endpoint + marker, 1)
    print("Added /api/set-jwt endpoint.")
elif "def set_jwt_token" in content:
    print("set_jwt_token already exists.")
else:
    print("WARNING: Could not find insertion point for set_jwt_token.")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("main.py updated.")
