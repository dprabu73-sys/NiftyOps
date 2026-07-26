"""
Fix real option data fetching in main.py:
1. Remove global nfo_disabled flag so EVERY contract queries TradingView for real candles!
2. Try all generated symbol candidates across NFO and NSE exchanges with proper retries.
3. Only use synthetic fallback as absolute last resort when TV returns empty.
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_fetch_block = """            # Ultra-Fast Option Fetch: Skip 10x retries if NFO WebSocket is restricted
            if _working_exchange.get('nfo_disabled', False):
                opt_data = None
            else:
                for cand_sym in candidates[:2]:  # Try top 2 candidates max
                    preferred = _working_exchange.get('preferred', nfo_exchange)
                    log_task(task_id, f"Fetching {cand_sym} ({interval}) via {preferred}...", "info")
                    opt_data = safe_get_hist(tv=_tv, symbol=cand_sym, exchange=preferred, interval=interval, n_bars=1500, retries=1, delay=0.2)

                    if opt_data is not None and not opt_data.empty:
                        median_close = float(opt_data['close'].median())
                        if median_close <= 5000:
                            winning_symbol = cand_sym
                            _working_exchange['preferred'] = preferred
                            break
                        else:
                            opt_data = None

                if opt_data is None or opt_data.empty:
                    # Flag NFO as restricted for this extraction job to make remaining options instant!
                    _working_exchange['nfo_disabled'] = True"""

new_fetch_block = """            # Always query TradingView for real option candles for every contract!
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

if old_fetch_block in content:
    content = content.replace(old_fetch_block, new_fetch_block, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched main.py to ALWAYS fetch real TradingView option data!")
else:
    print("WARNING: Could not find old_fetch_block in main.py")
