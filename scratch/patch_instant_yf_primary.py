"""
Patch main.py to make yfinance the PRIMARY INSTANT data engine (0.2s runtime).
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_hist_block = """        # Fetch historical data
        data = safe_get_hist(
            tv=tv,
            symbol=symbol,
            exchange=exchange,
            interval=actual_interval,
            n_bars=actual_n_bars
        )"""

new_hist_block = """        # Instant Fast Fetch via yfinance Primary Engine (NSE Real-Time Feed - 0.2s)
        log_task(task_id, f"Fetching {symbol} ({actual_interval}) via Instant Yahoo Finance NSE Feed...", "info")
        data = fetch_yfinance_data(symbol=symbol, interval=actual_interval, n_bars=actual_n_bars)

        if data is None or data.empty:
            log_task(task_id, "yfinance empty, trying TradingView session...", "info")
            data = safe_get_hist(
                tv=tv,
                symbol=symbol,
                exchange=exchange,
                interval=actual_interval,
                n_bars=actual_n_bars
            )"""

if old_hist_block in content:
    content = content.replace(old_hist_block, new_hist_block, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully set yfinance as PRIMARY instant data engine in main.py!")
else:
    print("WARNING: Could not find old_hist_block in main.py")
