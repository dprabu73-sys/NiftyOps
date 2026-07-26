"""
Patch main.py generate_option_candidates to put TradingView's exact symbol format FIRST:
{SYMBOL}{YYMMDD}{C/P}{STRIKE} on exchange NSE
e.g. NSE:NIFTY260728C23550 / NSE:NIFTY260728P23550
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_cand_block = """            # Candidate 1: Primary YYMMDD + STRIKE + CE/PE (e.g. NIFTY26072324300PE)
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
            cands.append(option_symbol)"""

new_cand_block = """            c_or_p = 'C' if 'C' in opt_kind else 'P'
            # Candidate 1: Exact TradingView Format: SYMBOL + YYMMDD + C/P + STRIKE (e.g. NIFTY260728C23550)
            cands.append(f"{symbol}{expiry_dt.strftime('%y%m%d')}{c_or_p}{strike_int}")
            # Candidate 2: Standard NSE format: SYMBOL + YYMMDD + STRIKE + CE/PE (e.g. NIFTY26072823550CE)
            cands.append(f"{symbol}{expiry_dt.strftime('%y%m%d')}{strike_int}{opt_kind}")
            # Candidate 3: Single-digit month format (e.g. NIFTY26728C23550)
            m = expiry_dt.month
            m_code = str(m) if m <= 9 else ('O' if m == 10 else ('N' if m == 11 else 'D'))
            cands.append(f"{symbol}{expiry_dt.strftime('%y')}{m_code}{expiry_dt.strftime('%d')}{c_or_p}{strike_int}")
            cands.append(f"{symbol}{expiry_dt.strftime('%y')}{m_code}{expiry_dt.strftime('%d')}{strike_int}{opt_kind}")
            # Candidate 4: Monthly 3-letter month (e.g. NIFTY26JULC23550)
            cands.append(f"{symbol}{expiry_dt.strftime('%y%b').upper()}{c_or_p}{strike_int}")
            cands.append(f"{symbol}{expiry_dt.strftime('%y%b').upper()}{strike_int}{opt_kind}")
            cands.append(option_symbol)"""

if old_cand_block in content:
    content = content.replace(old_cand_block, new_cand_block, 1)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated generate_option_candidates with TradingView's exact screenshot symbol format!")
else:
    print("WARNING: Could not find old_cand_block in main.py")
