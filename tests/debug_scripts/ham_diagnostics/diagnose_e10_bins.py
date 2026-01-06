#!/usr/bin/env python3
"""
Check E10 which has backward bins at start AND end.
"""

import json
import os
import numpy as np

json_path = os.path.join(os.path.dirname(__file__),
                         'data', 'psp', 'ham_angular_bins',
                         'ham_bin_data_plus_minus_3_days_corrected.json')

with open(json_path, 'r') as f:
    data = json.load(f)

# E10: 2 at start, 4 at end according to our diagnostic
enc_data = data['E10']
bins = enc_data['bins']

print(f"E10 Perihelion: {enc_data['perihelion']}")
print(f"E10 Number of bins: {len(bins)}")

# Perihelion longitude for E10 - approximate
perihelion_lon = 128.31  # From encounter list

start_lons = np.array([b['start_lon'] for b in bins])
end_lons = np.array([b['end_lon'] for b in bins])

start_degrees = (start_lons - perihelion_lon + 180) % 360 - 180
end_degrees = (end_lons - perihelion_lon + 180) % 360 - 180
bar_centers = (start_lons + end_lons) / 2
degrees_from_peri = (bar_centers - perihelion_lon + 180) % 360 - 180

print()
print("=" * 80)
print("FIRST 5 BINS (should have 2 backward)")
print("=" * 80)
for i in range(min(5, len(bins))):
    delta = end_degrees[i] - start_degrees[i]
    direction = "✓ FORWARD →" if delta > 0 else "✗ BACKWARD ←"
    print(f"Bin {i}: start={start_degrees[i]:7.2f}° → end={end_degrees[i]:7.2f}° | {direction}")

print()
print("=" * 80)
print("LAST 6 BINS (should have 4 backward)")
print("=" * 80)
for i in range(max(0, len(bins)-6), len(bins)):
    delta = end_degrees[i] - start_degrees[i]
    direction = "✓ FORWARD →" if delta > 0 else "✗ BACKWARD ←"
    print(f"Bin {i}: start={start_degrees[i]:7.2f}° → end={end_degrees[i]:7.2f}° | {direction}")

# Apply our filter
keep = end_degrees > start_degrees
print()
print("=" * 80)
print("FILTER RESULTS")
print("=" * 80)
print(f"Total bins: {len(bins)}")
print(f"Kept: {np.sum(keep)}")
print(f"Removed: {np.sum(~keep)}")
print(f"Removed indices: {list(np.where(~keep)[0])}")

print()
print("After filtering:")
kept_degrees = degrees_from_peri[keep]
print(f"Range: {np.min(kept_degrees):.2f}° to {np.max(kept_degrees):.2f}°")
