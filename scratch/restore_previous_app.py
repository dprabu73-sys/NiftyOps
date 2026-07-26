"""
Restore the previous version of the application before the UI/UX redesign.
Replaces index.html with index_recovered_full.html (the original single-page TradingView Data Extractor Pro).
"""
import shutil, os

templates_dir = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\templates"

index_recovered_full = os.path.join(templates_dir, "index_recovered_full.html")
index_target = os.path.join(templates_dir, "index.html")

if os.path.exists(index_recovered_full):
    shutil.copy2(index_recovered_full, index_target)
    print(f"Successfully restored previous version of index.html ({os.path.getsize(index_target)} bytes)!")
else:
    print("WARNING: index_recovered_full.html not found.")
