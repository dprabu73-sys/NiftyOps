import os
import time
import json
import urllib.request
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Configuration from Environment Variables (or fallback to defaults)
SYMBOL = os.environ.get("SYMBOL", "NIFTY")
EXCHANGE = os.environ.get("EXCHANGE", "NSE")
STRIKE_OFFSET = int(os.environ.get("STRIKE_OFFSET", "100"))
GOOGLE_SHEET_URL = os.environ.get("GOOGLE_SHEET_URL", "https://script.google.com/macros/s/AKfycbzeINdkKQbkx80cqa1n3e4r60aH9A6Ilmf0AQ93QMmLi9E6wNmt9qTakY85LpCqjZH5cw/exec")

def process_data_with_tv():
    print("Connecting to TradingView...")
    tv = TvDatafeed()
    
    # Fetch NIFTY index standard 1-minute data
    # Use 5000 bars to ensure we cover ~13 trading sessions
    print(f"Fetching {SYMBOL} index bars from TradingView...")
    index_data = tv.get_hist(
        symbol=SYMBOL,
        exchange=EXCHANGE,
        interval=Interval.in_1_minute,
        n_bars=5000
    )
    
    if index_data is None or index_data.empty:
        raise Exception(f"Failed to fetch index data for {SYMBOL}.")
        
    index_data = index_data.sort_index()
    index_data.index.name = 'datetime'
    df_temp = index_data.reset_index()
    df_temp['datetime'] = pd.to_datetime(df_temp['datetime'])
    # Convert timezone to IST (UTC+5:30)
    df_temp['ist_date'] = df_temp['datetime'].dt.strftime('%Y-%m-%d')
    df_temp['ist_time'] = df_temp['datetime'].dt.strftime('%H:%M')
    
    unique_dates = sorted(df_temp['ist_date'].unique())
    print(f"Processing {len(unique_dates)} trading sessions found...")
    
    # Helper to compute weekly expiry date (first Thursday on or after a date)
    def get_weekly_expiry(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        days_ahead = 3 - dt.weekday()
        if days_ahead < 0:
            days_ahead += 7
        expiry_dt = dt + timedelta(days=days_ahead)
        return expiry_dt.strftime("%y%m%d")
        
    contract_cache = {}
    
    def fetch_contract_ha(option_symbol):
        if option_symbol in contract_cache:
            return contract_cache[option_symbol]
            
        print(f"Fetching data for Option contract: {option_symbol}...")
        try:
            # Fetch 1500 bars of 15-minute data for this contract to match 15m chart
            opt_data = tv.get_hist(
                symbol=option_symbol,
                exchange=EXCHANGE,
                interval=Interval.in_15_minute,
                n_bars=1500
            )
            if opt_data is None or opt_data.empty:
                print(f"Warning: No data returned for option contract {option_symbol}")
                contract_cache[option_symbol] = None
                return None
                
            opt_data = opt_data.sort_index()
            
            # Calculate Heikin Ashi values for the contract
            ha_close = (opt_data['open'] + opt_data['high'] + opt_data['low'] + opt_data['close']) / 4.0
            ha_open = np.zeros(len(opt_data))
            ha_open[0] = (opt_data['open'].iloc[0] + opt_data['close'].iloc[0]) / 2.0
            for i in range(1, len(opt_data)):
                ha_open[i] = (ha_open[i - 1] + ha_close.iloc[i - 1]) / 2.0
                
            opt_data['ha_open'] = ha_open
            opt_data['ha_close'] = ha_close
            opt_data['ha_high'] = np.maximum(opt_data['high'], np.maximum(opt_data['ha_open'], opt_data['ha_close']))
            opt_data['ha_low'] = np.minimum(opt_data['low'], np.minimum(opt_data['ha_open'], opt_data['ha_close']))
            
            opt_data.index.name = 'datetime'
            opt_df_temp = opt_data.reset_index()
            opt_df_temp['datetime'] = pd.to_datetime(opt_df_temp['datetime'])
            opt_df_temp['ist_date'] = opt_df_temp['datetime'].dt.strftime('%Y-%m-%d')
            opt_df_temp['ist_time'] = opt_df_temp['datetime'].dt.strftime('%H:%M')
            
            contract_cache[option_symbol] = opt_df_temp
            return opt_df_temp
        except Exception as e:
            print(f"Error fetching {option_symbol}: {e}")
            contract_cache[option_symbol] = None
            return None

    daily_rows = []
    for idx, current_date in enumerate(unique_dates):
        prev_date = unique_dates[idx - 1] if idx > 0 else None
        
        day_bars = df_temp[df_temp['ist_date'] == current_date]
        
        # Find 09:28 close bar for option strike calculations
        bar_0928 = day_bars[day_bars['ist_time'] == '09:28']
        if bar_0928.empty:
            continue
            
        close_0928 = bar_0928['close'].iloc[0]
        call_option = ((close_0928 - STRIKE_OFFSET) // STRIKE_OFFSET) * STRIKE_OFFSET
        put_option = np.ceil((close_0928 + STRIKE_OFFSET) / float(STRIKE_OFFSET)) * STRIKE_OFFSET
        
        # Construct Option Symbol names
        expiry_str = get_weekly_expiry(current_date)
        call_sym = f"{SYMBOL}{expiry_str}C{int(call_option)}"
        put_sym = f"{SYMBOL}{expiry_str}P{int(put_option)}"
        
        # Fetch HA dataframes for both contracts
        call_df = fetch_contract_ha(call_sym)
        put_df = fetch_contract_ha(put_sym)
        
        def get_contract_ha_ohlc(contract_df, date_str, time_str):
            if contract_df is not None and not contract_df.empty:
                bar = contract_df[(contract_df['ist_date'] == date_str) & (contract_df['ist_time'] == time_str)]
                if not bar.empty:
                    return [
                        round(float(bar['ha_open'].iloc[0]), 2),
                        round(float(bar['ha_high'].iloc[0]), 2),
                        round(float(bar['ha_low'].iloc[0]), 2),
                        round(float(bar['ha_close'].iloc[0]), 2)
                    ]
            return ["", "", "", ""]
            
        call_1515 = get_contract_ha_ohlc(call_df, prev_date, '15:15') if prev_date else ["", "", "", ""]
        call_0915 = get_contract_ha_ohlc(call_df, current_date, '09:15')
        call_0930 = get_contract_ha_ohlc(call_df, current_date, '09:30')
        call_0945 = get_contract_ha_ohlc(call_df, current_date, '09:45')
        
        put_1515 = get_contract_ha_ohlc(put_df, prev_date, '15:15') if prev_date else ["", "", "", ""]
        put_0915 = get_contract_ha_ohlc(put_df, current_date, '09:15')
        put_0930 = get_contract_ha_ohlc(put_df, current_date, '09:30')
        put_0945 = get_contract_ha_ohlc(put_df, current_date, '09:45')
        
        daily_rows.append({
            'Date': current_date,
            '09:28 Close': round(float(close_0928), 2),
            'Call Strike': int(call_option),
            'Put Strike': int(put_option),
            
            'Call 15:15 HA Open': call_1515[0],
            'Call 15:15 HA High': call_1515[1],
            'Call 15:15 HA Low': call_1515[2],
            'Call 15:15 HA Close': call_1515[3],
            
            'Call 09:15 HA Open': call_0915[0],
            'Call 09:15 HA High': call_0915[1],
            'Call 09:15 HA Low': call_0915[2],
            'Call 09:15 HA Close': call_0915[3],
            
            'Call 09:30 HA Open': call_0930[0],
            'Call 09:30 HA High': call_0930[1],
            'Call 09:30 HA Low': call_0930[2],
            'Call 09:30 HA Close': call_0930[3],
            
            'Call 09:45 HA Open': call_0945[0],
            'Call 09:45 HA High': call_0945[1],
            'Call 09:45 HA Low': call_0945[2],
            'Call 09:45 HA Close': call_0945[3],
            
            'Put 15:15 HA Open': put_1515[0],
            'Put 15:15 HA High': put_1515[1],
            'Put 15:15 HA Low': put_1515[2],
            'Put 15:15 HA Close': put_1515[3],
            
            'Put 09:15 HA Open': put_0915[0],
            'Put 09:15 HA High': put_0915[1],
            'Put 09:15 HA Low': put_0915[2],
            'Put 09:15 HA Close': put_0915[3],
            
            'Put 09:30 HA Open': put_0930[0],
            'Put 09:30 HA High': put_0930[1],
            'Put 09:30 HA Low': put_0930[2],
            'Put 09:30 HA Close': put_0930[3],
            
            'Put 09:45 HA Open': put_0945[0],
            'Put 09:45 HA High': put_0945[1],
            'Put 09:45 HA Low': put_0945[2],
            'Put 09:45 HA Close': put_0945[3]
        })
        
    return daily_rows

def sync_to_google_sheets(records):
    if not GOOGLE_SHEET_URL:
        print("No GOOGLE_SHEET_URL configured. Skipping sync.")
        return
        
    print(f"Syncing {len(records)} records to Google Sheet...")
    payload = json.dumps(records).encode('utf-8')
    req = urllib.request.Request(
        GOOGLE_SHEET_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )
    with urllib.request.urlopen(req) as res:
        res_data = json.loads(res.read().decode('utf-8'))
        if res_data.get("status") == "success":
            print(f"Successfully synced! Added {res_data.get('rows_added', len(records))} rows.")
        else:
            print(f"Sync error: {res_data.get('error')}")

def main():
    try:
        records = process_data_with_tv()
        if records:
            sync_to_google_sheets(records)
        else:
            print("No matching records found to sync.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
