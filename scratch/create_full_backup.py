"""
Create a dedicated backup directory 'backup_before_yfinance' containing all key application files (clean text output).
"""
import os, shutil

backup_dir = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\backup_before_yfinance"
os.makedirs(backup_dir, exist_ok=True)

files_to_backup = [
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\main.py",
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env",
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\templates\index.html",
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\templates\analyzer.html",
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\templates\journal.html",
    r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\templates\settings.html",
]

for src in files_to_backup:
    if os.path.exists(src):
        dst = os.path.join(backup_dir, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"Backed up: {os.path.basename(src)} ({os.path.getsize(dst)} bytes)")
    else:
        print(f"Warning: Source not found: {src}")

print(f"Backup complete! All files saved to: {backup_dir}")
