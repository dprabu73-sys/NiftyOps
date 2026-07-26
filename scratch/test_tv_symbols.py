import os
import sys
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()

# Test different symbol format variations for NIFTY options
# Date: 2026-07-21 or current dates (e.g. 2024 / 2025 / 2026 dates)
# Let's test searching for NIFTY option symbols on NFO
search_results = tv.search_symbol(text="NIFTY", exchange="NFO")
print(f"Search results count: {len(search_results) if search_results else 0}")
if search_results:
    for item in search_results[:20]:
        print(item)
