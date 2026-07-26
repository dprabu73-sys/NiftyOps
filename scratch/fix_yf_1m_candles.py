"""
Fix yfinance 1-minute candles fetching in main.py
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_yf_code = """def fetch_yfinance_data(symbol, interval="1m", n_bars=500):
    sym_upper = symbol.upper()
    if "BANK" in sym_upper:
        yf_sym = "^NSEBANK"
    elif "FIN" in sym_upper:
        yf_sym = "NIFTY_FIN_SERVICE.NS"
    else:
        yf_sym = "^NSEI"
        
    yf_interval = "5m"
    str_int = str(interval).lower()
    if "1m" in str_int or "1 minute" in str_int: yf_interval = "1m"
    elif "15" in str_int: yf_interval = "15m"
    elif "5" in str_int: yf_interval = "5m"
    
    period = "5d"
    if n_bars > 1500: period = "1mo"
    elif n_bars > 3000: period = "3mo"
    
    try:
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period=period, interval=yf_interval)"""

new_yf_code = """def fetch_yfinance_data(symbol, interval="1m", n_bars=500):
    sym_upper = symbol.upper()
    if "BANK" in sym_upper:
        yf_sym = "^NSEBANK"
    elif "FIN" in sym_upper:
        yf_sym = "NIFTY_FIN_SERVICE.NS"
    else:
        yf_sym = "^NSEI"
        
    yf_interval = "1m"  # Enforce 1m for HA 09:28 candle matching
    period = "7d"       # yfinance max for 1m intraday data
    
    try:
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period=period, interval=yf_interval)"""

if old_yf_code in content:
    content = content.replace(old_yf_code, new_yf_code, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated fetch_yfinance_data to enforce 1m interval!")
else:
    print("WARNING: Could not find old_yf_code in main.py")
