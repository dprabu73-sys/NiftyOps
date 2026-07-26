"""
Test yfinance fetching for NIFTY & BANKNIFTY
"""
import yfinance as yf

print("Testing yfinance for NIFTY 50 (^NSEI)...")
ticker = yf.Ticker("^NSEI")
df = ticker.history(period="5d", interval="5m")
print(f"Retrieved {len(df)} candles for NIFTY 50:")
print(df.tail(3))

print("\nTesting yfinance for BANKNIFTY (^NSEBANK)...")
ticker_bank = yf.Ticker("^NSEBANK")
df_bank = ticker_bank.history(period="5d", interval="5m")
print(f"Retrieved {len(df_bank)} candles for BANKNIFTY:")
print(df_bank.tail(3))
