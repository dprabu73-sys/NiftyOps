import re

with open("main.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "@app.route" in line or "def start" in line or "def run" in line or "def extract" in line:
            print(f"Line {idx}: {line.strip()}")
