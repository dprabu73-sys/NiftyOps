import sys
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()

# Let's test a few common dates and strikes on NFO to see which symbol format succeeds
# For example, NIFTY options around current index price (~24000-24500)
# Let's test July 2024, July 2025, or recent exps like July 2026 / July 2024
# Examples of potential TV NFO symbol formats:
candidates = [
    # Format 1: NIFTY24JUL24300CE (Monthly)
    ("NIFTY24JUL24300CE", "NFO"),
    ("NIFTY24JUL24300PE", "NFO"),
    # Format 2: NIFTY2472524300CE (Weekly 25-Jul-2024)
    ("NIFTY2472524300CE", "NFO"),
    ("NIFTY2472524300PE", "NFO"),
    # Format 3: YYMMDD format: NIFTY24072524300CE
    ("NIFTY24072524300CE", "NFO"),
    # Format 4: 2026 formats
    ("NIFTY26JUL24300CE", "NFO"),
    ("NIFTY2672324300CE", "NFO"),
    ("NIFTY2672124300CE", "NFO"),
    ("NIFTY26072124300CE", "NFO"),
    ("NIFTY260721P24300", "NFO"),
]

for sym, exch in candidates:
    try:
        data = tv.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=10)
        if data is not None and not data.empty:
            print(f"SUCCESS: {sym} ({exch}) returned {len(data)} bars!")
        else:
            print(f"FAILED (Empty): {sym} ({exch})")
    except Exception as e:
        print(f"ERROR: {sym} ({exch}) -> {e}")
