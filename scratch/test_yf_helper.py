"""
Helper function to fetch intraday OHLCV candles from yfinance.
"""
import yfinance as yf
import pandas as pd
import numpy as np

def fetch_yfinance_data(symbol, interval="1m", n_bars=500):
    sym_upper = symbol.upper()
    if "BANK" in sym_upper:
        yf_sym = "^NSEBANK"
    elif "FIN" in sym_upper:
        yf_sym = "NIFTY_FIN_SERVICE.NS"
    else:
        yf_sym = "^NSEI"
        
    yf_interval = "5m"
    if "1" in str(interval): yf_interval = "1m"
    elif "15" in str(interval): yf_interval = "15m"
    elif "5" in str(interval): yf_interval = "5m"
    
    # Calculate period based on n_bars
    period = "5d"
    if n_bars > 1500: period = "1mo"
    elif n_bars > 3000: period = "3mo"
    
    try:
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period=period, interval=yf_interval)
        if df is None or df.empty:
            return None
            
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.tail(n_bars)
        return df
    except Exception as e:
        print(f"yfinance fetch error for {symbol}: {e}")
        return None

if __name__ == "__main__":
    df = fetch_yfinance_data("NIFTY", "5m", 10)
    print("Fetched NIFTY via yfinance:")
    print(df)
