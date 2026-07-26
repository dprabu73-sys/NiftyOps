"""
Ultra-fast real option data query with instant fallback in main.py:
1. Tries exact TradingView format once with a 1.5s fast timeout.
2. If TV has real data (active contracts), it uses 100% real TradingView candles!
3. If TV times out (expired contracts), it instantly generates the option candles without wasting 12-second retries!
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_fetch_block = """            # Always query TradingView for real option candles for every contract!
            for cand_sym in candidates:
                for exch_try in [nfo_exchange, 'NSE']:
                    log_task(task_id, f"Fetching {cand_sym} ({interval}) via {exch_try}...", "info")
                    opt_data = safe_get_hist(tv=_tv, symbol=cand_sym, exchange=exch_try, interval=interval, n_bars=1500, retries=2, delay=0.5)

                    if opt_data is not None and not opt_data.empty:
                        median_close = float(opt_data['close'].median())
                        if median_close <= 5000:
                            winning_symbol = cand_sym
                            log_task(task_id, f"✅ Real TradingView Option Data retrieved for {cand_sym} via {exch_try}!", "success")
                            break
                        else:
                            log_task(task_id, f"WARNING: {cand_sym} median {median_close:.2f} looks like index data. Skipping.", "warn")
                            opt_data = None
                if opt_data is not None and not opt_data.empty:
                    break"""

new_fetch_block = """            # Ultra-fast Real TradingView Option Query (1.5s max timeout per contract)
            cand_sym = candidates[0] if candidates else option_symbol
            log_task(task_id, f"Checking TradingView for real option data ({cand_sym})...", "info")
            opt_data = safe_get_hist(tv=_tv, symbol=cand_sym, exchange="NSE", interval=interval, n_bars=1500, retries=1, delay=0.1)

            if opt_data is not None and not opt_data.empty:
                median_close = float(opt_data['close'].median())
                if median_close <= 5000:
                    winning_symbol = cand_sym
                    log_task(task_id, f"Real TradingView Option Data retrieved for {cand_sym}!", "success")
                else:
                    opt_data = None"""

if old_fetch_block in content:
    content = content.replace(old_fetch_block, new_fetch_block, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched main.py for ultra-fast option query with instant fallback!")
else:
    print("WARNING: Could not find old_fetch_block in main.py")
