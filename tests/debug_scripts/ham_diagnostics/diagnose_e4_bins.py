#!/usr/bin/env python3
"""
Deep dive into E4 bins to understand the edge case.
"""

import json
import os
import numpy as np

# Load the JSON
json_path = os.path.join(os.path.dirname(__file__),
                         'data', 'psp', 'ham_angular_bins',
                         'ham_bin_data_plus_minus_3_days_corrected.json')

with open(json_path, 'r') as f:
    data = json.load(f)

enc_data = data['E04']
bins = enc_data['bins']
perihelion_lon = 57.42  # From the notebook for E04 (approximate)

print(f"E04 Perihelion: {enc_data['perihelion']}")
print(f"E04 Number of bins: {len(bins)}")
print()

# Convert to arrays
start_lons = np.array([b['start_lon'] for b in bins])
end_lons = np.array([b['end_lon'] for b in bins])
ham_frac = np.array([b['ham_frac'] for b in bins])

# Calculate bar centers (average of start/end)
bar_centers = (start_lons + end_lons) / 2

# Convert to degrees from perihelion
# Using the perihelion lon from the notebook
perihelion_lon = 57.42  # Approximate - from E04 in your encounter list

degrees_from_peri = (bar_centers - perihelion_lon + 180) % 360 - 180
start_degrees = (start_lons - perihelion_lon + 180) % 360 - 180
end_degrees = (end_lons - perihelion_lon + 180) % 360 - 180

print("=" * 80)
print("FIRST 5 BINS")
print("=" * 80)
for i in range(min(5, len(bins))):
    delta = end_degrees[i] - start_degrees[i]
    direction = "FORWARD →" if delta > 0 else "BACKWARD ←"
    print(f"Bin {i}: start={start_degrees[i]:7.2f}° → end={end_degrees[i]:7.2f}° | delta={delta:+6.2f}° | {direction}")

print()
print("=" * 80)
print("LAST 5 BINS")
print("=" * 80)
for i in range(max(0, len(bins)-5), len(bins)):
    delta = end_degrees[i] - start_degrees[i]
    direction = "FORWARD →" if delta > 0 else "BACKWARD ←"
    print(f"Bin {i}: start={start_degrees[i]:7.2f}° → end={end_degrees[i]:7.2f}° | delta={delta:+6.2f}° | {direction}")

print()
print("=" * 80)
print("OVERALL RANGE")
print("=" * 80)
print(f"Start degrees range: {np.min(start_degrees):.2f}° to {np.max(start_degrees):.2f}°")
print(f"End degrees range: {np.min(end_degrees):.2f}° to {np.max(end_degrees):.2f}°")
print(f"Bar centers range: {np.min(degrees_from_peri):.2f}° to {np.max(degrees_from_peri):.2f}°")

# Check for any backward bins
backward_mask = end_degrees < start_degrees
print(f"\nBackward bins (end < start): {np.sum(backward_mask)}")
if np.sum(backward_mask) > 0:
    print(f"  Indices: {np.where(backward_mask)[0]}")

# Check for bins that span across 0 (perihelion)
crosses_zero = (start_degrees < 0) & (end_degrees > 0) | (start_degrees > 0) & (end_degrees < 0)
print(f"\nBins crossing 0° (perihelion): {np.sum(crosses_zero)}")
if np.sum(crosses_zero) > 0:
    print(f"  Indices: {np.where(crosses_zero)[0]}")
    for idx in np.where(crosses_zero)[0]:
        print(f"    Bin {idx}: {start_degrees[idx]:.2f}° → {end_degrees[idx]:.2f}°")

# Check the wrap-around issue
print()
print("=" * 80)
print("RAW LONGITUDE CHECK (before wrap adjustment)")
print("=" * 80)
for i in range(min(5, len(bins))):
    raw_delta = end_lons[i] - start_lons[i]
    print(f"Bin {i}: {start_lons[i]:7.2f}° → {end_lons[i]:7.2f}° | raw_delta={raw_delta:+6.2f}°")

print("...")
for i in range(max(0, len(bins)-5), len(bins)):
    raw_delta = end_lons[i] - start_lons[i]
    print(f"Bin {i}: {start_lons[i]:7.2f}° → {end_lons[i]:7.2f}° | raw_delta={raw_delta:+6.2f}°")

# What's the actual x-axis range being plotted?
print()
print("=" * 80)
print("WHAT WOULD BE PLOTTED")
print("=" * 80)
keep = end_degrees > start_degrees
print(f"Bins kept with 'end > start' filter: {np.sum(keep)}/{len(keep)}")
print(f"Bins removed: {np.sum(~keep)}")
if np.sum(~keep) > 0:
    print(f"  Removed indices: {np.where(~keep)[0]}")

kept_degrees = degrees_from_peri[keep]
print(f"\nKept degrees range: {np.min(kept_degrees):.2f}° to {np.max(kept_degrees):.2f}°")
