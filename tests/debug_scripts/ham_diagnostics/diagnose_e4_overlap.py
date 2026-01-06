#!/usr/bin/env python3
"""
Check E4 for OVERLAPPING bins - bins that extend past each other or past data range.
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
perihelion_lon = 57.42

print(f"E04: {len(bins)} bins")
print()

start_lons = np.array([b['start_lon'] for b in bins])
end_lons = np.array([b['end_lon'] for b in bins])

start_degrees = (start_lons - perihelion_lon + 180) % 360 - 180
end_degrees = (end_lons - perihelion_lon + 180) % 360 - 180

# Check for adjacent bins that overlap
print("=" * 80)
print("CHECKING FOR ADJACENT BIN OVERLAP")
print("=" * 80)
overlaps = []
for i in range(len(bins) - 1):
    # Does bin i's end extend past bin i+1's start?
    if end_degrees[i] > start_degrees[i+1] + 0.01:  # small tolerance
        overlaps.append((i, i+1))
        print(f"OVERLAP: Bin {i} end ({end_degrees[i]:.2f}°) > Bin {i+1} start ({start_degrees[i+1]:.2f}°)")

if not overlaps:
    print("No adjacent bin overlaps found")

# Check for gaps between bins
print()
print("=" * 80)
print("CHECKING FOR GAPS BETWEEN BINS")
print("=" * 80)
gaps = []
for i in range(len(bins) - 1):
    gap = start_degrees[i+1] - end_degrees[i]
    if abs(gap) > 0.1:  # significant gap
        gaps.append((i, gap))
        print(f"GAP: Between bin {i} and {i+1}: {gap:.2f}°")

if not gaps:
    print("No significant gaps found (bins are contiguous)")

# Check first and last bins
print()
print("=" * 80)
print("FIRST AND LAST BINS")
print("=" * 80)
print(f"FIRST bin (0): start={start_degrees[0]:.2f}° end={end_degrees[0]:.2f}°")
print(f"LAST bin ({len(bins)-1}): start={start_degrees[-1]:.2f}° end={end_degrees[-1]:.2f}°")

# What's the full span?
print()
print(f"Data spans: {start_degrees[0]:.2f}° to {end_degrees[-1]:.2f}°")
print(f"Total coverage: {end_degrees[-1] - start_degrees[0]:.2f}°")

# Is the LAST bin tiny? (potential edge artifact)
print()
print("=" * 80)
print("BIN WIDTHS (checking for anomalies)")
print("=" * 80)
widths = end_degrees - start_degrees
print(f"Average width: {np.mean(widths):.2f}°")
print(f"Min width: {np.min(widths):.2f}° (bin {np.argmin(widths)})")
print(f"Max width: {np.max(widths):.2f}° (bin {np.argmax(widths)})")

# Show first few and last few widths
print()
print("First 3 widths:", [f"{w:.2f}°" for w in widths[:3]])
print("Last 3 widths:", [f"{w:.2f}°" for w in widths[-3:]])

# The last bin is tiny!
if widths[-1] < 0.5:
    print()
    print("⚠️  LAST BIN IS VERY NARROW!")
    print(f"   Bin {len(bins)-1}: width = {widths[-1]:.2f}° (vs avg {np.mean(widths):.2f}°)")

# Check if E4 has bins on BOTH sides of perihelion
print()
print("=" * 80)
print("BINS RELATIVE TO PERIHELION (0°)")
print("=" * 80)
negative_bins = np.sum(start_degrees < 0)
positive_bins = np.sum(start_degrees >= 0)
print(f"Bins starting BEFORE perihelion (negative degrees): {negative_bins}")
print(f"Bins starting AFTER perihelion (positive degrees): {positive_bins}")

# Check if any bins CROSS perihelion
crosses_peri = (start_degrees < 0) & (end_degrees > 0)
print(f"Bins crossing perihelion: {np.sum(crosses_peri)}")

# Show the range
print()
print(f"All bins are on the POSITIVE side (after perihelion)")
print(f"First bin starts at: {start_degrees[0]:.2f}° from perihelion")
print(f"Last bin ends at: {end_degrees[-1]:.2f}° from perihelion")
