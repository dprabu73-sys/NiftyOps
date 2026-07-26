import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import altair as alt

# Page Configuration
st.set_page_config(
    page_title="Nifty Intraday CALL Option Backtest Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode Glassmorphic Trading Dashboard)
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #151c2c;
        border-right: 1px solid #243049;
    }
    
    /* Glassmorphic Cards */
    .dashboard-card {
        background-color: #151c2c;
        border: 1px solid #243049;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 20px;
    }
    
    .card-title {
        font-size: 16px;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metrics Layout */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }
    
    .metric-box {
        background-color: #1a233a;
        border: 1px solid #243049;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-label {
        font-size: 11px;
        color: #94a3b8;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Status styling */
    .status-win { color: #10b981; }
    .status-loss { color: #ef4444; }
    .status-open { color: #f59e0b; }
    
    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background-color: #0b0f19;
    }
    
    th {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        padding: 10px 12px !important;
    }
    
    td {
        padding: 8px 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02) !important;
    }
    
    /* Highlight Classes */
    .row-breakout {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b;
    }
    .row-entry {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid #10b981;
    }
    .row-target {
        background-color: rgba(79, 70, 229, 0.2) !important;
        border-left: 4px solid #818cf8;
    }
    .row-stop {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444;
    }

    /* Checklist Badge */
    .checklist-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
    }
    .checklist-success { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .checklist-pending { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
</style>
""", unsafe_allow_html=True)

# App Title
st.title("📈 Nifty Intraday CALL Option Strategy Analyzer")
st.markdown("Analyze intraday options trades using 15m Heikin Ashi levels and 5m standard candle breakouts.")

# Sidebar Configuration Controls
st.sidebar.header("⚙️ Core Configuration")
data_mode = st.sidebar.radio("Data Input Mode", ["Excel Upload Mode", "Manual Entry Mode"])
target_points = st.sidebar.number_input("Target Points (default 25)", min_value=1.0, value=25.0, step=1.0)

# Overrides Expanders in Sidebar
st.sidebar.subheader("✏️ Manual Overrides")
use_overrides = st.sidebar.checkbox("Enable Logic Overrides")

override_base = None
override_breakout = None
override_entry_val = None
override_entry_time = None
override_sl_val = None
override_force_exit_val = None
override_force_exit_time = None

if use_overrides:
    override_base = st.sidebar.number_input("Override Base Comparison Value", min_value=0.0, value=0.0, step=0.05)
    override_breakout = st.sidebar.number_input("Override Initial Breakout Value", min_value=0.0, value=0.0, step=0.05)
    override_entry_val = st.sidebar.number_input("Override Entry Value", min_value=0.0, value=0.0, step=0.05)
    override_entry_time = st.sidebar.text_input("Override Entry Time", placeholder="e.g. 09:30")
    override_sl_val = st.sidebar.number_input("Override Stop-Loss Value", min_value=0.0, value=0.0, step=0.05)
    override_force_exit_val = st.sidebar.number_input("Manual Force-Exit Price", min_value=0.0, value=0.0, step=0.05)
    override_force_exit_time = st.sidebar.text_input("Manual Force-Exit Time", placeholder="e.g. 15:20")

# Input Data Processing
prev_1515_close_ha = 0.0
today_0915_close_ha = 0.0
today_0930_close_ha = 0.0
today_0945_open_ha = 0.0
candles_df = pd.DataFrame()

if data_mode == "Excel Upload Mode":
    uploaded_file = st.file_uploader("Upload Nifty Options Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            if "Strategy_Summary" in xls.sheet_names and "5m_Live_Candles" in xls.sheet_names:
                df_summary = pd.read_excel(xls, "Strategy_Summary")
                df_candles = pd.read_excel(xls, "5m_Live_Candles")
                
                # Extract summary levels (from last row)
                if not df_summary.empty:
                    last_row = df_summary.iloc[-1]
                    prev_1515_close_ha = float(last_row.get("Call Prev 15:15 Close (15m HA)", 0.0))
                    today_0915_close_ha = float(last_row.get("Call 09:15 Close (15m HA)", 0.0))
                    today_0930_close_ha = float(last_row.get("Call 09:30 Close (15m HA)", 0.0))
                    today_0945_open_ha = float(last_row.get("Call 09:45 Open (15m HA)", 0.0))
                
                # Extract 5m candles
                if not df_candles.empty:
                    candles_df = df_candles[["Time (IST)", "Call Open", "Call High", "Call Low", "Call Close"]].copy()
                    candles_df.columns = ["Time", "Open", "High", "Low", "Close"]
                    
                    # Convert to numeric
                    for col in ["Open", "High", "Low", "Close"]:
                        candles_df[col] = pd.to_numeric(candles_df[col], errors='coerce')
                    candles_df = candles_df.dropna(subset=["Time", "Open", "High", "Low", "Close"])
            else:
                st.error("Excel file must contain sheets named 'Strategy_Summary' and '5m_Live_Candles'.")
        except Exception as e:
            st.error(f"Error parsing Excel: {e}")
            
else:
    # Manual Entry Mode
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="dashboard-card"><div class="card-title">15m Heikin Ashi Levels</div>', unsafe_allow_html=True)
        prev_1515_close_ha = st.number_input("Call Prev 15:15 Close (15m HA)", min_value=0.0, value=0.0, step=0.05)
        today_0915_close_ha = st.number_input("Call 09:15 Close (15m HA)", min_value=0.0, value=0.0, step=0.05)
        today_0930_close_ha = st.number_input("Call 09:30 Close (15m HA)", min_value=0.0, value=0.0, step=0.05)
        today_0945_open_ha = st.number_input("Call 09:45 Open (15m HA)", min_value=0.0, value=0.0, step=0.05)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="dashboard-card"><div class="card-title">5m Candles Form Input</div>', unsafe_allow_html=True)
        manual_candles_json = st.text_area(
            "Paste 5m candles in JSON format",
            value='[\n  {"Time": "09:15", "Open": 230.50, "High": 234.10, "Low": 229.00, "Close": 232.00},\n  {"Time": "09:20", "Open": 232.00, "High": 233.80, "Low": 231.10, "Close": 233.55},\n  {"Time": "09:25", "Open": 233.55, "High": 236.40, "Low": 232.50, "Close": 235.10}\n]',
            height=180
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if manual_candles_json.strip():
            try:
                candles_df = pd.DataFrame(json.loads(manual_candles_json))
                for col in ["Open", "High", "Low", "Close"]:
                    candles_df[col] = pd.to_numeric(candles_df[col], errors='coerce')
            except Exception as e:
                st.error(f"Error parsing JSON candles list: {e}")

# Proceed if candles dataframe is not empty
if not candles_df.empty:
    
    # ---------------------------------------------
    # CORE STRATEGY ANALYSIS ENGINE
    # ---------------------------------------------
    
    # 1. Base comparison value calculation
    calculated_base_val = max(prev_1515_close_ha, today_0915_close_ha)
    base_val = override_base if (use_overrides and override_base > 0) else calculated_base_val
    
    # 2. Sequential entry detection
    first_breach_idx = None
    entry_idx = None
    entry_val = 0.0
    entry_time = ""
    breakout_ref_val = 0.0
    breakout_time = ""
    entry_branch = "Next-row maximum fallback"
    
    # Scan sequentially for first breach (breakout row)
    for idx, row in candles_df.iterrows():
        o, h, l, c = row["Open"], row["High"], row["Low"], row["Close"]
        if max(o, h, l, c) > base_val:
            first_breach_idx = idx
            breakout_ref_val = max(o, h, l, c)
            breakout_time = row["Time"]
            break
            
    # Check the next interval candle for Entry started confirmation
    if first_breach_idx is not None:
        next_idx = first_breach_idx + 1
        if next_idx < len(candles_df):
            next_row = candles_df.iloc[next_idx]
            n_o, n_h, n_l, n_c = next_row["Open"], next_row["High"], next_row["Low"], next_row["Close"]
            
            # Check if any values in next row exceed breakout_ref_val
            exceeding_vals = [v for v in [n_o, n_h, n_l, n_c] if v > breakout_ref_val]
            
            if exceeding_vals:
                entry_branch = "Found greater value"
                entry_val = max(exceeding_vals)
            else:
                entry_branch = "Next-row maximum fallback"
                entry_val = max(n_o, n_h, n_l, n_c)
                
            entry_idx = next_idx
            entry_time = next_row["Time"]
        else:
            # Fallback if no next row exists
            entry_branch = "Next-row maximum fallback"
            entry_val = breakout_ref_val
            entry_idx = first_breach_idx
            entry_time = breakout_time
            
    # Apply Overrides
    if use_overrides:
        if override_breakout > 0:
            breakout_ref_val = override_breakout
        if override_entry_val > 0:
            entry_val = override_entry_val
            entry_branch = "Override applied"
        if override_entry_time:
            entry_time = override_entry_time
            # Try to match index
            matched = candles_df[candles_df["Time"] == entry_time]
            if not matched.empty:
                entry_idx = matched.index[0]
                
    # 3. Target value calculation
    calculated_target_val = entry_val + target_points
    target_val = override_force_exit_val if (use_overrides and override_force_exit_val > 0) else calculated_target_val
    
    # 4. Stop-loss reference value
    calculated_sl_val = base_val
    sl_val = override_sl_val if (use_overrides and override_sl_val > 0) else calculated_sl_val
    
    # 5. Scan forward from entry candle to check hits
    target_hit_idx = None
    target_hit_time = "—"
    target_hit_candle = None
    
    sl_hit_idx = None
    sl_hit_time = "—"
    sl_exit_price = 0.0
    sl_hit_candle = None
    
    if entry_idx is not None:
        # Check starting from the ENTRY CANDLE itself
        for idx in range(entry_idx, len(candles_df)):
            row = candles_df.iloc[idx]
            r_time = row["Time"]
            r_o, r_h, r_l, r_c = row["Open"], row["High"], row["Low"], row["Close"]
            
            # Check Stop Loss trigger (at least one of the 4 values below sl_val)
            if sl_hit_idx is None:
                if any(v < sl_val for v in [r_o, r_h, r_l, r_c]):
                    sl_hit_idx = idx
                    sl_hit_time = r_time
                    sl_exit_price = min(r_o, r_h, r_l, r_c)
                    sl_hit_candle = row
                    
            # Check Target Hit trigger
            if target_hit_idx is None:
                if r_h >= target_val:
                    target_hit_idx = idx
                    target_hit_time = r_time
                    target_hit_candle = row
                    
    # Force override exit time if specified
    if use_overrides and override_force_exit_time:
        matched = candles_df[candles_df["Time"] == override_force_exit_time]
        if not matched.empty:
            force_idx = matched.index[0]
            force_row = candles_df.iloc[force_idx]
            
            # Apply force exit priority
            target_hit_idx = force_idx
            target_hit_time = override_force_exit_time
            target_val = override_force_exit_val if override_force_exit_val > 0 else force_row["Close"]
            target_hit_candle = force_row
            
    # 6. Final outcome compilation
    exit_reason = "OPEN TRADE / NO EXIT"
    exit_time = "—"
    exit_price = 0.0
    pnl = 0.0
    
    if target_hit_idx is not None and sl_hit_idx is not None:
        if target_hit_idx < sl_hit_idx:
            exit_reason = "TARGET HIT EXIT"
            exit_time = target_hit_time
            exit_price = target_val
        else:
            exit_reason = "STOP LOSS EXIT"
            exit_time = sl_hit_time
            exit_price = sl_exit_price
    elif target_hit_idx is not None:
        exit_reason = "TARGET HIT EXIT"
        exit_time = target_hit_time
        exit_price = target_val
    elif sl_hit_idx is not None:
        exit_reason = "STOP LOSS EXIT"
        exit_time = sl_hit_time
        exit_price = sl_exit_price
        
    if exit_reason != "OPEN TRADE / NO EXIT" and entry_val > 0:
        pnl = exit_price - entry_val
        
    # Decision logs compilation
    decision_steps = [
        f"1. Base comparison value selected: {base_val:.2f} (Calculated from max({prev_1515_close_ha:.2f}, {today_0915_close_ha:.2f}))",
        f"2. Breakout reference candle detected at time {breakout_time or '—'} with reference value {breakout_ref_val:.2f}",
        f"3. Entry point selected using branch '{entry_branch}' at time {entry_time or '—'} with Entry started value {entry_val:.2f}",
        f"4. Target calculated as Entry ({entry_val:.2f}) + {target_points:.2f} pts = {target_val:.2f}",
        f"5. Stop-loss reference value set at {sl_val:.2f}",
    ]
    
    if sl_hit_idx is not None:
        decision_steps.append(f"6. Stop-loss triggered at {sl_hit_time} (at least one of 4 candle values was below stop-loss value {sl_val:.2f}). Stop-loss exit price calculated as min(OHLC) = {sl_exit_price:.2f}.")
    else:
        decision_steps.append("6. Stop-loss was never triggered during this session.")
        
    if target_hit_idx is not None:
        decision_steps.append(f"7. Target hit at {target_hit_time} (high reached {target_hit_candle['High']:.2f} >= target value {target_val:.2f}).")
    else:
        decision_steps.append("7. Target was never hit during this session.")
        
    decision_steps.append(f"8. Final Trade Outcome: {exit_reason} at {exit_time} (Exit Price: {exit_price:.2f}, total P&L: {pnl:+.2f} points).")
    
    # ---------------------------------------------
    # RENDER STRATEGY FLOW CHECKLIST (Dashboard Help)
    # ---------------------------------------------
    st.markdown('<div class="dashboard-card"><div class="card-title">📈 Strategy Flow Status</div>', unsafe_allow_html=True)
    c_cols = st.columns(4)
    with c_cols[0]:
        st.markdown(f'<span class="checklist-badge checklist-success">STEP 1</span> Baseline Set: **{base_val:.2f}**', unsafe_allow_html=True)
    with c_cols[1]:
        if first_breach_idx is not None:
            st.markdown(f'<span class="checklist-badge checklist-success">STEP 2</span> Breakout Ref: **{breakout_ref_val:.2f}** at **{breakout_time}**', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="checklist-badge checklist-pending">STEP 2</span> Waiting for Breakout...', unsafe_allow_html=True)
    with c_cols[2]:
        if entry_idx is not None:
            st.markdown(f'<span class="checklist-badge checklist-success">STEP 3</span> Entry confirmed: **{entry_val:.2f}** ({entry_branch})', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="checklist-badge checklist-pending">STEP 3</span> Waiting for Entry...', unsafe_allow_html=True)
    with c_cols[3]:
        if exit_reason != "OPEN TRADE / NO EXIT":
            status_cls = "checklist-success"
            st.markdown(f'<span class="checklist-badge {status_cls}">STEP 4</span> Trade Closed: **{exit_reason}**', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="checklist-badge checklist-pending">STEP 4</span> Trade Active (Open)', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------
    # RENDER METRICS BOARD
    # ---------------------------------------------
    st.markdown('<div class="dashboard-card"><div class="card-title">🏆 Strategy Trade Summary</div>', unsafe_allow_html=True)
    
    pnl_class = "status-win" if pnl > 0 else ("status-loss" if pnl < 0 else "status-open")
    pnl_sign = "+" if pnl > 0 else ""
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Entry Price / Time</div><div class="metric-value">{entry_val:.2f} <span style="font-size:11px;color:#94a3b8;">({entry_time})</span></div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Target / SL Levels</div><div class="metric-value" style="font-size:14px;line-height:1.4;">Tgt: {target_val:.2f}<br>SL: {sl_val:.2f}</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Exit Reason / Time</div><div class="metric-value">{exit_reason}<br><span style="font-size:11px;color:#94a3b8;">({exit_time})</span></div></div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Strategy P&L</div><div class="metric-value {pnl_class}">{pnl_sign}{pnl:.2f} pts</div></div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------------------------------------------
    # RENDER ALTAIR Price Chart
    # ---------------------------------------------
    st.markdown('<div class="dashboard-card"><div class="card-title">📉 Option Price Chart & Strategy Levels</div>', unsafe_allow_html=True)
    
    # Add horizontal levels to data
    chart_df = candles_df.copy()
    chart_df['Baseline'] = base_val
    if entry_val > 0:
        chart_df['Entry Price'] = entry_val
        chart_df['Target Price'] = target_val
        chart_df['Stop Loss Price'] = sl_val
        
    # Plotly/Altair chart setup
    chart_data_melted = chart_df.melt(id_vars=['Time'], value_vars=['Close', 'Baseline', 'Entry Price', 'Target Price', 'Stop Loss Price'], var_name='Metric', value_name='Price')
    
    chart = alt.Chart(chart_data_melted).mark_line().encode(
        x=alt.X('Time:N', title='Time (IST)', sort=None),
        y=alt.Y('Price:Q', title='Price (INR)', scale=alt.Scale(zero=False)),
        color=alt.Color('Metric:N', scale=alt.Scale(
            domain=['Close', 'Baseline', 'Entry Price', 'Target Price', 'Stop Loss Price'],
            range=['#4f46e5', '#f59e0b', '#10b981', '#818cf8', '#ef4444']
        )),
        strokeDash=alt.condition(
            alt.datum.Metric != 'Close',
            alt.value([4, 4]), # Dashed lines for levels
            alt.value([0])     # Solid line for close price
        )
    ).properties(height=350, width='container')
    
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Summary dataframe for export
    summary_data = {
        "Metric": [
            "Base comparison value",
            "Initial breakout reference value",
            "Entry branch used",
            "Entry time",
            "Entry price",
            "Target price",
            "Target hit time",
            "Stop-loss reference",
            "Stop-loss hit time",
            "Stop-loss exit price",
            "Final exit type",
            "Final exit time",
            "Profit/Loss points"
        ],
        "Value": [
            f"{base_val:.2f}",
            f"{breakout_ref_val:.2f}",
            entry_branch,
            entry_time,
            f"{entry_val:.2f}",
            f"{target_val:.2f}",
            target_hit_time,
            f"{sl_val:.2f}",
            sl_hit_time,
            f"{sl_exit_price:.2f}" if sl_exit_price > 0 else "—",
            exit_reason,
            exit_time,
            f"{pnl:+.2f} pts"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # ---------------------------------------------
    # RENDER 5m CANDLE LOG TABLE WITH HIGHLIGHTING
    # ---------------------------------------------
    st.markdown('<div class="dashboard-card"><div class="card-title">📊 5m Candle Database Log</div>', unsafe_allow_html=True)
    
    # Construct rows with styles
    html_rows = []
    for idx, row in candles_df.iterrows():
        row_class = ""
        badge = ""
        
        # Determine highlighting class based on index matches
        if idx == first_breach_idx:
            row_class = "row-breakout"
            badge = '<span style="background-color:#d97706;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;">BREAKOUT</span>'
        elif idx == entry_idx:
            row_class = "row-entry"
            badge = f'<span style="background-color:#10b981;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;">ENTRY ({entry_branch})</span>'
        elif idx == target_hit_idx and exit_reason == "TARGET HIT EXIT":
            row_class = "row-target"
            badge = '<span style="background-color:#4f46e5;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;">TARGET HIT</span>'
        elif idx == sl_hit_idx and exit_reason == "STOP LOSS EXIT":
            row_class = "row-stop"
            badge = '<span style="background-color:#ef4444;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;">SL HIT</span>'
            
        html_rows.append(f"""
        <tr class="{row_class}">
            <td>{row['Time']}</td>
            <td>{row['Open']:.2f}</td>
            <td style="font-weight:600;">{row['High']:.2f}</td>
            <td>{row['Low']:.2f}</td>
            <td>{row['Close']:.2f}</td>
            <td style="color:#94a3b8;">{base_val:.2f}</td>
            <td>{badge}</td>
        </tr>
        """)
        
    table_html = f"""
    <div style="max-height:450px; overflow-y:auto; border:1px solid #243049; border-radius:8px;">
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Open</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                    <th>Baseline Reference</th>
                    <th>Status Event</th>
                </tr>
            </thead>
            <tbody>
                {''.join(html_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------------------------------------------
    # DECISION LOG PANEL & EXPORTS
    # ---------------------------------------------
    st.markdown('<div class="dashboard-card"><div class="card-title">📝 Strategy Decision Log</div>', unsafe_allow_html=True)
    for step in decision_steps:
        st.markdown(f"🔹 {step}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Options Section
    st.subheader("📥 Export Outputs & Summaries")
    col1, col2, col3 = st.columns(3)
    
    # 1. Export CSV of Trade Summary
    with col1:
        csv_summary = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Trade Summary CSV",
            data=csv_summary,
            file_name=f"trade_summary_{entry_time or 'session'}.csv",
            mime="text/csv"
        )
        
    # 2. Export CSV of decision log
    with col2:
        log_text = "\n".join(decision_steps)
        st.download_button(
            label="📥 Export Decision Log TXT",
            data=log_text,
            file_name=f"decision_log_{entry_time or 'session'}.txt",
            mime="text/plain"
        )
        
    # 3. Export full candles sheet
    with col3:
        # Prepare table with events column
        export_candles = candles_df.copy()
        export_candles["Event"] = ""
        if first_breach_idx is not None:
            export_candles.at[first_breach_idx, "Event"] = "Breakout Reference"
        if entry_idx is not None:
            export_candles.at[entry_idx, "Event"] = f"Entry ({entry_branch})"
        if target_hit_idx is not None:
            export_candles.at[target_hit_idx, "Event"] = "Target Hit"
        if sl_hit_idx is not None:
            export_candles.at[sl_hit_idx, "Event"] = "Stop Loss Hit"
            
        csv_candles = export_candles.to_csv(index=False)
        st.download_button(
            label="📥 Export Full Candles CSV",
            data=csv_candles,
            file_name=f"candles_log_{entry_time or 'session'}.csv",
            mime="text/csv"
        )
else:
    st.warning("Please upload an Excel workbook or input manual candle records to run strategy simulation.")
