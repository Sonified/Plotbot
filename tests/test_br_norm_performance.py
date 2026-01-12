# tests/test_br_norm_performance.py
# Test that br_norm property doesn't trigger redundant get_data() calls
# To run: conda run -n plotbot_env python tests/test_br_norm_performance.py

"""
Tests the fix for br_norm performance issue.
Previously, br_norm property getter called _calculate_br_norm() on EVERY access,
which called get_data(proton.sun_dist_rsun) even if already calculated for current trange.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot as pb
import time

print("=" * 60)
print("Testing br_norm property caching with TimeRangeTracker")
print("=" * 60)

# Test with 2 panels, 1 day each (short time range for speed)
print("\nCreating 2-panel multiplot with br_norm (1 day each)")
print("With the fix, we should see:")
print("  - Panel 1: get_data(proton.sun_dist_rsun) called ONCE")
print("  - Panel 2: get_data(proton.sun_dist_rsun) called ONCE")
print("  - Total: 2 calls (one per panel)")
print()

start_time = time.time()

# 2 panels, 1 day each
trange_list = [
    ['2025-01-17/00:00:00', '2025-01-18/00:00:00'],
    ['2025-01-18/00:00:00', '2025-01-19/00:00:00']
]

plot_data = [(trange, pb.mag_rtn_4sa.br_norm) for trange in trange_list]

pb.multiplot(plot_data)

elapsed = time.time() - start_time
print("\n" + "=" * 60)
print(f"✅ Test completed in {elapsed:.1f} seconds")
print("=" * 60)
print("\nIf you see 5+ 'spi_sf00_l3_mom' lines per panel, the bug is NOT fixed.")
print("If you see only 2 'spi_sf00_l3_mom' lines total (1 per panel), the bug IS fixed!")
