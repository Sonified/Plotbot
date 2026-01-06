#!/usr/bin/env python3
"""
Check E4 bar CENTER positions - that's what matplotlib plots.
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

start_lons = np.array([b['start_lon'] for b in bins])
end_lons = np.array([b['end_lon'] for b in bins])

# This is how multiplot.py calculates bar centers
bar_centers_abs = (start_lons + end_lons) / 2
degrees_from_peri = bar_centers_abs - perihelion_lon
degrees_from_peri = (degrees_from_peri + 180) % 360 - 180

print("=" * 80)
print("LAST 10 BINS - Center positions (what gets plotted)")
print("=" * 80)
for i in range(len(bins)-10, len(bins)):
    print(f"Bin {i}: center={degrees_from_peri[i]:7.2f}° | raw_center={bar_centers_abs[i]:7.2f}°")

print()
print("=" * 80)
print("CHECK FOR DUPLICATE/CLOSE CENTERS")
print("=" * 80)
# Check if any two bins have very close centers
for i in range(len(degrees_from_peri)):
    for j in range(i+1, len(degrees_from_peri)):
        diff = abs(degrees_from_peri[i] - degrees_from_peri[j])
        if diff < 0.5:  # Very close
            print(f"CLOSE! Bin {i} ({degrees_from_peri[i]:.2f}°) and Bin {j} ({degrees_from_peri[j]:.2f}°) diff={diff:.3f}°")

print()
print("=" * 80)
print("CHECK WRAP-AROUND ISSUE")
print("=" * 80)
# Maybe the wrap brings something to the same position?
print(f"Min center: {np.min(degrees_from_peri):.2f}° at bin {np.argmin(degrees_from_peri)}")
print(f"Max center: {np.max(degrees_from_peri):.2f}° at bin {np.argmax(degrees_from_peri)}")

# Check if any centers wrapped to negative
negative_centers = degrees_from_peri < 0
print(f"Negative centers: {np.sum(negative_centers)}")
if np.any(negative_centers):
    print(f"  Indices: {np.where(negative_centers)[0]}")
    for idx in np.where(negative_centers)[0]:
        print(f"    Bin {idx}: center={degrees_from_peri[idx]:.2f}°, raw={bar_centers_abs[idx]:.2f}°")
