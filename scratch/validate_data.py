"""
Validation script: Compare Yahoo Finance NIFTY data against what you see on TradingView
"""
import yfinance as yf
import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("NIFTY 50 INDEX DATA VALIDATION (Yahoo Finance vs TradingView)")
print("=" * 80)

# Fetch 1-minute candles
ticker = yf.Ticker("^NSEI")
df = ticker.history(period="5d", interval="1m")

# Convert to IST-friendly format
df.index = df.index.tz_convert('Asia/Kolkata')
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

# Show last trading day's key timestamps
dates = df.index.date
unique_dates = sorted(set(dates))

print(f"\nTrading days found: {[str(d) for d in unique_dates]}")
print()

for dt in unique_dates[-2:]:  # Last 2 days
    day_df = df[df.index.date == dt]
    print(f"--- {dt} ---")
    
    # Show specific timestamps your strategy uses
    key_times = ['09:15', '09:16', '09:17', '09:18', '09:19', '09:20',
                 '09:25', '09:26', '09:27', '09:28', '09:29', '09:30',
                 '15:15', '15:20', '15:25', '15:29']
    
    for t in key_times:
        match = day_df[day_df.index.strftime('%H:%M') == t]
        if not match.empty:
            row = match.iloc[0]
            print(f"  {t} -> Open={row['Open']:.2f}  High={row['High']:.2f}  Low={row['Low']:.2f}  Close={row['Close']:.2f}")
    
    print()

print("=" * 80)
print("HOW TO VALIDATE MANUALLY:")
print("=" * 80)
print("""
1. Open TradingView: https://www.tradingview.com/chart/
2. Type 'NSE:NIFTY' in the symbol search bar
3. Set interval to '1 minute'
4. Hover over the 09:28 candle on July 23 or July 24
5. Compare the Open/High/Low/Close values shown above
   with what TradingView displays - they should MATCH EXACTLY!

NOTE: The NIFTY INDEX prices are 100%% REAL and identical.
      The OPTION PRICES (Call/Put) are COMPUTED from these
      index prices, NOT actual traded option prices.
""")
