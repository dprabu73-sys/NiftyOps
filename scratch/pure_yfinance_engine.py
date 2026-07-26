"""
Make Yahoo Finance the primary default engine in main.py for instant, zero-setup extractions!
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the TV fetching in extraction_thread with direct fast yfinance fetch
old_fetch_start = """        # Fetch historical data via pooled TradingView session
        _tv = _get_pooled_tv(username=username, password=password, tv_session=tv_session)
        log_task(task_id, f"Fetching {symbol} historical data ({actual_interval}) for {actual_n_bars} bars via {exchange}...", "info")
        data = safe_get_hist(
            tv=_tv,
            symbol=symbol,
            exchange=exchange,
            interval=actual_interval,
            n_bars=actual_n_bars
        )"""

new_fetch_start = """        # Instant Fast Fetch via yfinance Primary Engine (NSE Real-Time Feed)
        log_task(task_id, f"Fetching {symbol} ({actual_interval}) via Instant Yahoo Finance NSE Feed...", "info")
        data = fetch_yfinance_data(symbol=symbol, interval=actual_interval, n_bars=actual_n_bars)

        if data is None or data.empty:
            log_task(task_id, f"Trying TradingView fallback for {symbol}...", "info")
            _tv = _get_pooled_tv(username=username, password=password, tv_session=tv_session)
            data = safe_get_hist(tv=_tv, symbol=symbol, exchange=exchange, interval=actual_interval, n_bars=actual_n_bars)"""

if old_fetch_start in content:
    content = content.replace(old_fetch_start, new_fetch_start, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully set Yahoo Finance as the PRIMARY default extraction engine in main.py!")
else:
    print("WARNING: Could not find old_fetch_start in main.py")
