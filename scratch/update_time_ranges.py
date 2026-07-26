"""
Update backtest_range dropdown options in templates/index.html and main.py
to support clear Day-wise and Week-wise extractions.
"""

# 1. Update templates/index.html
with open("templates/index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

old_select_block = """                                    <select id="backtest_range" onchange="onBacktestRangeChange(this)">
                                        <option value="today">Today Only (Live)</option>
                                        <option value="2days">2 Trading Days</option>
                                        <option value="3days" selected>3 Trading Days</option>
                                        <option value="1week">1 Week (5 Trading Days)</option>
                                        <option value="custom">Custom (Specify Bars)</option>
                                    </select>"""

new_select_block = """                                    <select id="backtest_range" onchange="onBacktestRangeChange(this)">
                                        <optgroup label="📅 Day-wise Extractions">
                                            <option value="today">1 Day (Today / Live Session)</option>
                                            <option value="2days">2 Trading Days</option>
                                            <option value="3days" selected>3 Trading Days</option>
                                            <option value="4days">4 Trading Days</option>
                                        </optgroup>
                                        <optgroup label="📆 Week-wise Extractions">
                                            <option value="1week">1 Week (5 Trading Days)</option>
                                            <option value="2weeks">2 Weeks (10 Trading Days)</option>
                                            <option value="3weeks">3 Weeks (15 Trading Days)</option>
                                            <option value="1month">4 Weeks / 1 Month (20 Trading Days)</option>
                                        </optgroup>
                                        <optgroup label="⚙️ Custom Range">
                                            <option value="custom">Custom (Specify Exact Bars)</option>
                                        </optgroup>
                                    </select>"""

if old_select_block in html_content:
    html_content = html_content.replace(old_select_block, new_select_block, 1)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html dropdown updated with Day-wise & Week-wise options!")
else:
    print("WARNING: Could not find old_select_block in index.html")

# 2. Update n_bars calculation in templates/index.html JS
old_bars_js = """            if (rangeVal === 'today') n_bars = 100;
            else if (rangeVal === '2days') n_bars = 300;
            else if (rangeVal === '3days') n_bars = 500;
            else if (rangeVal === '1week') n_bars = 800;"""

new_bars_js = """            if (rangeVal === 'today') n_bars = 100;
            else if (rangeVal === '2days') n_bars = 250;
            else if (rangeVal === '3days') n_bars = 400;
            else if (rangeVal === '4days') n_bars = 550;
            else if (rangeVal === '1week') n_bars = 750;
            else if (rangeVal === '2weeks') n_bars = 1500;
            else if (rangeVal === '3weeks') n_bars = 2250;
            else if (rangeVal === '1month') n_bars = 3000;"""

if old_bars_js in html_content:
    html_content = html_content.replace(old_bars_js, new_bars_js, 1)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html JS updated with Day-wise & Week-wise bar mappings!")
