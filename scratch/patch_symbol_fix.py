import sys
import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace get_weekly_expiry definition and fetch_contract_data in extraction_thread
old_expiry_block = """        # Helper to compute weekly expiry date (Thursday for NIFTY, Wednesday for BANKNIFTY, Tuesday for FINNIFTY)
        def get_weekly_expiry(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            target_weekday = 1 # Default to Tuesday (NIFTY weekly expiry in 2026)
            sym_upper = symbol.upper()
            if "FINNIFTY" in sym_upper:
                target_weekday = 1 # Tuesday
            elif "BANKNIFTY" in sym_upper or "NIFTYBANK" in sym_upper:
                target_weekday = 2 # Wednesday (BankNifty weekly)
                
            days_ahead = target_weekday - dt.weekday()
            if days_ahead < 0:
                days_ahead += 7
            expiry_dt = dt + timedelta(days=days_ahead)
            
            # Format: YYMMDD (always 2 digits for month and day on TradingView)
            return expiry_dt.strftime("%y%m%d")"""

new_expiry_block = """        # Helper to compute weekly expiry date (Thursday for NIFTY, Wednesday for BANKNIFTY, Tuesday for FINNIFTY)
        def get_weekly_expiry_dt(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            sym_upper = symbol.upper()
            if "FINNIFTY" in sym_upper:
                target_weekday = 1 # Tuesday
            elif "BANKNIFTY" in sym_upper or "NIFTYBANK" in sym_upper:
                target_weekday = 2 # Wednesday (BankNifty weekly)
            else:
                target_weekday = 3 # Thursday (Nifty weekly)
                
            days_ahead = target_weekday - dt.weekday()
            if days_ahead < 0:
                days_ahead += 7
            expiry_dt = dt + timedelta(days=days_ahead)
            return expiry_dt

        def get_weekly_expiry(date_str):
            return get_weekly_expiry_dt(date_str).strftime("%y%m%d")"""

if old_expiry_block in content:
    content = content.replace(old_expiry_block, new_expiry_block)
    print("Replaced get_weekly_expiry_dt block successfully.")
else:
    print("WARNING: old_expiry_block not found precisely.")

# Replace fetch_contract_data block
old_fetch_block = """        def fetch_contract_data(option_symbol, interval, calculate_ha=True):
            cache_key = (option_symbol, interval, calculate_ha)
            if cache_key in contract_cache:
                return contract_cache[cache_key]

            # NSE derivatives are under NFO on TradingView; try NSE directly if NFO is known to fail
            nfo_exchange = 'NFO' if exchange.upper() == 'NSE' else exchange
            preferred = _working_exchange.get('preferred', nfo_exchange)
            fallback  = exchange if preferred == nfo_exchange else nfo_exchange

            log_task(task_id, f"Fetching {option_symbol} ({interval}) via {preferred}...", "info")
            # Use a pooled tv instance per thread to avoid WebSocket contention
            _tv = _get_pooled_tv(username=username, password=password, tv_session=tv_session)
            opt_data = safe_get_hist(tv=_tv, symbol=option_symbol, exchange=preferred,
                                     interval=interval, n_bars=1500)

            if (opt_data is None or opt_data.empty) and fallback != preferred:
                log_task(task_id, f"{preferred} empty, trying {fallback}...", "info")
                opt_data = safe_get_hist(tv=_tv, symbol=option_symbol, exchange=fallback,
                                         interval=interval, n_bars=1500)
                if opt_data is not None and not opt_data.empty:
                    _working_exchange['preferred'] = fallback  # remember winner
            elif opt_data is not None and not opt_data.empty:
                _working_exchange['preferred'] = preferred

            if opt_data is None or opt_data.empty:
                log_task(task_id, f"Warning: No data for {option_symbol} ({interval})", "warn")
                contract_cache[cache_key] = None
                return None

            # Sanity check: option premiums are typically <5000
            median_close = float(opt_data['close'].median())
            log_task(task_id, f"Contract {option_symbol} ({interval}): {len(opt_data)} bars, median={median_close:.2f}", "info")
            if median_close > 5000:
                log_task(task_id, f"WARNING: {option_symbol} looks like index data (median {median_close:.2f}). Skipping.", "warn")
                contract_cache[cache_key] = None
                return None"""

new_fetch_block = """        def generate_option_candidates(option_symbol, date_str=None, strike=None, opt_type=None):
            if not date_str or strike is None or not opt_type:
                return [option_symbol]
            expiry_dt = get_weekly_expiry_dt(date_str)
            strike_int = int(strike)
            opt_kind = opt_type.upper()
            cands = []
            # Candidate 1: Primary YYMMDD + STRIKE + CE/PE (e.g. NIFTY26072324300PE)
            cands.append(f"{symbol}{expiry_dt.strftime('%y%m%d')}{strike_int}{opt_kind}")
            # Candidate 2: Single-digit month (NSE weekly format): e.g. NIFTY2672324300PE
            m = expiry_dt.month
            m_code = str(m) if m <= 9 else ('O' if m == 10 else ('N' if m == 11 else 'D'))
            cands.append(f"{symbol}{expiry_dt.strftime('%y')}{m_code}{expiry_dt.strftime('%d')}{strike_int}{opt_kind}")
            # Candidate 3: Monthly expiry 3-letter month: e.g. NIFTY26JUL24300PE
            cands.append(f"{symbol}{expiry_dt.strftime('%y%b').upper()}{strike_int}{opt_kind}")
            # Candidate 4: Same day expiry if trade date IS expiry date
            dt_curr = datetime.strptime(date_str, "%Y-%m-%d")
            cands.append(f"{symbol}{dt_curr.strftime('%y%m%d')}{strike_int}{opt_kind}")
            cands.append(f"{symbol}{dt_curr.strftime('%y')}{m_code}{dt_curr.strftime('%d')}{strike_int}{opt_kind}")
            cands.append(option_symbol)

            seen = set()
            res = []
            for c in cands:
                if c not in seen:
                    seen.add(c)
                    res.append(c)
            return res

        def fetch_contract_data(option_symbol, interval, calculate_ha=True, date_str=None, strike=None, opt_type=None):
            cache_key = (option_symbol, interval, calculate_ha)
            if cache_key in contract_cache:
                return contract_cache[cache_key]

            candidates = generate_option_candidates(option_symbol, date_str, strike, opt_type)
            nfo_exchange = 'NFO' if exchange.upper() == 'NSE' else exchange

            opt_data = None
            winning_symbol = None

            _tv = _get_pooled_tv(username=username, password=password, tv_session=tv_session)

            for cand_sym in candidates:
                preferred = _working_exchange.get('preferred', nfo_exchange)
                fallback  = exchange if preferred == nfo_exchange else nfo_exchange
                log_task(task_id, f"Fetching {cand_sym} ({interval}) via {preferred}...", "info")
                opt_data = safe_get_hist(tv=_tv, symbol=cand_sym, exchange=preferred, interval=interval, n_bars=1500)

                if (opt_data is None or opt_data.empty) and fallback != preferred:
                    log_task(task_id, f"{preferred} empty for {cand_sym}, trying {fallback}...", "info")
                    opt_data = safe_get_hist(tv=_tv, symbol=cand_sym, exchange=fallback, interval=interval, n_bars=1500)
                    if opt_data is not None and not opt_data.empty:
                        _working_exchange['preferred'] = fallback

                elif opt_data is not None and not opt_data.empty:
                    _working_exchange['preferred'] = preferred

                if opt_data is not None and not opt_data.empty:
                    median_close = float(opt_data['close'].median())
                    if median_close <= 5000:
                        winning_symbol = cand_sym
                        break
                    else:
                        log_task(task_id, f"WARNING: {cand_sym} looks like index data (median {median_close:.2f}). Skipping.", "warn")
                        opt_data = None

            if opt_data is None or opt_data.empty:
                log_task(task_id, f"Warning: No data for {option_symbol} ({interval}) across candidates {candidates}", "warn")
                contract_cache[cache_key] = None
                return None

            log_task(task_id, f"Contract {winning_symbol} ({interval}): {len(opt_data)} bars, median={float(opt_data['close'].median()):.2f}", "info")"""

if old_fetch_block in content:
    content = content.replace(old_fetch_block, new_fetch_block)
    print("Replaced fetch_contract_data block successfully.")
else:
    print("WARNING: old_fetch_block not found precisely.")

# Replace call_sym and put_sym generation
old_sym_gen = """            call_sym = f"{symbol}{expiry_str}C{int(call_option)}"
            put_sym  = f"{symbol}{expiry_str}P{int(put_option)}\""""

new_sym_gen = """            call_sym = f"{symbol}{expiry_str}{int(call_option)}CE"
            put_sym  = f"{symbol}{expiry_str}{int(put_option)}PE\""""

if old_sym_gen in content:
    content = content.replace(old_sym_gen, new_sym_gen)
    print("Replaced call_sym/put_sym generation successfully.")
else:
    print("WARNING: old_sym_gen not found precisely.")

# Replace fetch calls
old_fetch_calls = """            call_df_15m = fetch_contract_data(call_sym, baseline_interval, True)
            call_df_5m  = fetch_contract_data(call_sym, signal_interval,  False)
            put_df_15m  = fetch_contract_data(put_sym,  baseline_interval, True)
            put_df_5m   = fetch_contract_data(put_sym,  signal_interval,  False)"""

new_fetch_calls = """            call_df_15m = fetch_contract_data(call_sym, baseline_interval, True, current_date, call_option, 'CE')
            call_df_5m  = fetch_contract_data(call_sym, signal_interval,  False, current_date, call_option, 'CE')
            put_df_15m  = fetch_contract_data(put_sym,  baseline_interval, True, current_date, put_option, 'PE')
            put_df_5m   = fetch_contract_data(put_sym,  signal_interval,  False, current_date, put_option, 'PE')"""

if old_fetch_calls in content:
    content = content.replace(old_fetch_calls, new_fetch_calls)
    print("Replaced fetch calls successfully.")
else:
    print("WARNING: old_fetch_calls not found precisely.")

# Replace preview_symbols route
old_preview_block = """        def weekly_expiry(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            target_weekday = 1 # Default to Tuesday (NIFTY weekly expiry in 2026)
            sym_upper = symbol.upper()
            if "FINNIFTY" in sym_upper:
                target_weekday = 1 # Tuesday
            elif "BANKNIFTY" in sym_upper or "NIFTYBANK" in sym_upper:
                target_weekday = 2 # Wednesday
                
            days_ahead = target_weekday - dt.weekday()
            if days_ahead < 0:
                days_ahead += 7
            exp = dt + timedelta(days=days_ahead)
            
            return exp.strftime("%y%m%d"), exp.strftime("%d %b %Y")

        rows = []
        for current_date in sorted(df['ist_date'].unique()):
            bar = df[(df['ist_date'] == current_date) & (df['ist_time'] == '09:28')]
            if bar.empty:
                continue
            close = float(bar['close'].iloc[0])
            call_strike = int(((close - strike_offset) // strike_offset) * strike_offset)
            put_strike  = int(np.ceil((close + strike_offset) / float(strike_offset)) * strike_offset)
            exp_str, exp_label = weekly_expiry(current_date)
            rows.append({
                'date':         current_date,
                'close_0928':   round(close, 2),
                'expiry':       exp_str,
                'expiry_label': exp_label,
                'call_strike':  call_strike,
                'put_strike':   put_strike,
                'call_sym':     f"{symbol}{exp_str}C{call_strike}",
                'put_sym':      f"{symbol}{exp_str}P{put_strike}"
            })"""

new_preview_block = """        def weekly_expiry(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            sym_upper = symbol.upper()
            if "FINNIFTY" in sym_upper:
                target_weekday = 1 # Tuesday
            elif "BANKNIFTY" in sym_upper or "NIFTYBANK" in sym_upper:
                target_weekday = 2 # Wednesday
            else:
                target_weekday = 3 # Thursday for NIFTY
                
            days_ahead = target_weekday - dt.weekday()
            if days_ahead < 0:
                days_ahead += 7
            exp = dt + timedelta(days=days_ahead)
            
            return exp.strftime("%y%m%d"), exp.strftime("%d %b %Y")

        rows = []
        for current_date in sorted(df['ist_date'].unique()):
            bar = df[(df['ist_date'] == current_date) & (df['ist_time'] == '09:28')]
            if bar.empty:
                continue
            close = float(bar['close'].iloc[0])
            call_strike = int(((close - strike_offset) // strike_offset) * strike_offset)
            put_strike  = int(np.ceil((close + strike_offset) / float(strike_offset)) * strike_offset)
            exp_str, exp_label = weekly_expiry(current_date)
            rows.append({
                'date':         current_date,
                'close_0928':   round(close, 2),
                'expiry':       exp_str,
                'expiry_label': exp_label,
                'call_strike':  call_strike,
                'put_strike':   put_strike,
                'call_sym':     f"{symbol}{exp_str}{call_strike}CE",
                'put_sym':      f"{symbol}{exp_str}{put_strike}PE"
            })"""

if old_preview_block in content:
    content = content.replace(old_preview_block, new_preview_block)
    print("Replaced preview_symbols block successfully.")
else:
    print("WARNING: old_preview_block not found precisely.")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py successfully!")
