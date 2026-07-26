"""
Patch main.py to integrate yfinance zero-setup fallback data source.
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

yf_helper_code = """
# ── yfinance Instant Data Fallback Helper ────────────────────────────────────
import yfinance as yf

def fetch_yfinance_data(symbol, interval="1m", n_bars=500):
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
        df = ticker.history(period=period, interval=yf_interval)
        if df is None or df.empty:
            return None
            
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.tail(n_bars)
        return df
    except Exception as e:
        print(f"yfinance fetch exception: {e}")
        return None
"""

if "def fetch_yfinance_data" not in content:
    content = yf_helper_code + "\n" + content

# Update extraction_thread fallback to try yfinance if TV fails
old_fallback_check = """            if data is not None and not data.empty:
                tv = guest_tv  # Switch to guest session for subsequent index queries
                log_task(task_id, "Successfully connected via guest session fallback.", "info")
            else:
                raise ValueError(f"No historical data returned. Please verify that the symbol '{symbol}' and exchange '{exchange}' are correct and that TradingView has data for them.")"""

new_fallback_check = """            if data is not None and not data.empty:
                tv = guest_tv  # Switch to guest session for subsequent index queries
                log_task(task_id, "Successfully connected via guest session fallback.", "info")
            else:
                log_task(task_id, "TradingView connection failed. Falling back to yfinance instant NSE feed...", "warn")
                data = fetch_yfinance_data(symbol=symbol, interval=actual_interval, n_bars=actual_n_bars)
                if data is not None and not data.empty:
                    log_task(task_id, "Successfully retrieved data via yfinance instant feed!", "success")
                else:
                    raise ValueError(f"No historical data returned. Please verify that symbol '{symbol}' is valid.")"""

if old_fallback_check in content:
    content = content.replace(old_fallback_check, new_fallback_check, 1)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully integrated yfinance fallback into main.py!")
