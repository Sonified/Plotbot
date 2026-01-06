#!/usr/bin/env python3
"""
Check E4 RAW longitude data for wrap-around issues.
"""

import json
import os
import numpy as np

json_path = os.path.join(os.path.dirname(__file__),
                         'data', 'psp', 'ham_angular_bins',
                         'ham_bin_data_plus_minus_3_days_corrected.json')

with open(json_path, 'r') as f:
    data = json.load(f)

enc_data = data['E04']
bins = enc_data['bins']

print(f"E04 Perihelion timestamp: {enc_data['perihelion']}")
print(f"Number of bins: {len(bins)}")
print()

# Show ALL bins with raw longitudes
print("=" * 90)
print("ALL BINS - RAW LONGITUDES")
print("=" * 90)
print(f"{'Bin':>4} | {'start_lon':>10} | {'end_lon':>10} | {'delta':>8} | {'ham_frac':>8}")
print("-" * 90)

for i, b in enumerate(bins):
    delta = b['end_lon'] - b['start_lon']
    direction = "→" if delta > 0 else "←"
    print(f"{i:4} | {b['start_lon']:10.2f} | {b['end_lon']:10.2f} | {delta:+8.2f} {direction} | {b['ham_frac']:8.3f}")

# Check for wrap-around (crossing 360/0)
print()
print("=" * 90)
print("CHECKING FOR 360° WRAP-AROUND")
print("=" * 90)
for i, b in enumerate(bins):
    start = b['start_lon']
    end = b['end_lon']
    # Check if either crosses 360
    if start > 350 or end > 350:
        print(f"Bin {i}: start={start:.2f}°, end={end:.2f}° - NEAR 360°!")
    if start < 10 or end < 10:
        print(f"Bin {i}: start={start:.2f}°, end={end:.2f}° - NEAR 0°!")

# What's the full range?
start_lons = [b['start_lon'] for b in bins]
end_lons = [b['end_lon'] for b in bins]
print()
print(f"Start longitude range: {min(start_lons):.2f}° to {max(start_lons):.2f}°")
print(f"End longitude range: {min(end_lons):.2f}° to {max(end_lons):.2f}°")
