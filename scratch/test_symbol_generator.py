from datetime import datetime, timedelta

def get_weekly_expiry_dt(date_str, symbol):
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
    expiry_dt = dt + timedelta(days=days_ahead)
    return expiry_dt

def generate_option_symbol_candidates(symbol, date_str, strike, opt_type):
    """
    Generates a prioritized list of candidate TradingView symbol strings for NSE/NFO options.
    opt_type should be 'CE' or 'PE'.
    """
    expiry_dt = get_weekly_expiry_dt(date_str, symbol)
    strike_int = int(strike)
    opt_type = opt_type.upper()
    
    candidates = []
    
    # 1. YYMMDD format: e.g. NIFTY26072324300PE
    sym1 = f"{symbol}{expiry_dt.strftime('%y%m%d')}{strike_int}{opt_type}"
    candidates.append(sym1)
    
    # 2. Single-digit month format (NSE weekly style): e.g. NIFTY2672324300PE
    # Month code: 1-9 for Jan-Sep, O, N, D for Oct-Dec
    m = expiry_dt.month
    m_code = str(m) if m <= 9 else ('O' if m == 10 else ('N' if m == 11 else 'D'))
    sym2 = f"{symbol}{expiry_dt.strftime('%y')}{m_code}{expiry_dt.strftime('%d')}{strike_int}{opt_type}"
    if sym2 not in candidates:
        candidates.append(sym2)
        
    # 3. Monthly expiry style (3-letter month): e.g. NIFTY26JUL24300PE
    sym3 = f"{symbol}{expiry_dt.strftime('%y%b').upper()}{strike_int}{opt_type}"
    if sym3 not in candidates:
        candidates.append(sym3)
        
    return candidates

# Test run
print("NIFTY test candidates for 2026-07-21, Strike 24300 PE:")
print(generate_option_symbol_candidates("NIFTY", "2026-07-21", 24300, "PE"))

print("\nBANKNIFTY test candidates for 2026-07-21, Strike 52000 CE:")
print(generate_option_symbol_candidates("BANKNIFTY", "2026-07-21", 52000, "CE"))
