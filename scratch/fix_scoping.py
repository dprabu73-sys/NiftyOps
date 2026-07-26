"""
Fix NameError in fetch_contract_data: replace candles_df with df_temp.
"""

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("if candles_df is not None and not candles_df.empty:", "if df_temp is not None and not df_temp.empty:")
content = content.replace("synth_df = candles_df.copy()", "synth_df = df_temp.copy()")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully replaced candles_df with df_temp!")
