"""
Search TradingView for exact symbol ticker for NIFTY July 30, 2026 options
"""
from tvDatafeed import TvDatafeed, Interval
import os

tv = TvDatafeed()

test_syms = [
    ("NSE", "NIFTY260730C23500"),
    ("NSE", "NIFTY260730C23550"),
    ("NSE", "NIFTY26730C23500"),
    ("NFO", "NIFTY260730C23500"),
    ("NFO", "NIFTY26073023500CE"),
    ("NFO", "NIFTY2673023500CE"),
    ("NFO", "NIFTY26JUL23500CE"),
    ("NSE", "NIFTY26JUL23500CE"),
]

print("Testing exact option symbol queries on TradingView...")
for exch, sym in test_syms:
    try:
        df = tv.get_hist(symbol=sym, exchange=exch, interval=Interval.in_15_minute, n_bars=10)
        if df is not None and not df.empty:
            print(f"FOUND MATCH! Exch: {exch} | Sym: {sym} | Bars: {len(df)} | Close: {df['close'].iloc[-1]}")
        else:
            print(f"No match: {exch}:{sym}")
    except Exception as e:
        print(f"Error for {exch}:{sym} -> {e}")
