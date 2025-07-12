# tests/test_orbit_performance.py
# To run this test from the project root directory and see print output in the console:
# conda run -n plotbot_env python tests/test_orbit_performance.py
# Or using pytest:
# conda run -n plotbot_env python -m pytest tests/test_orbit_performance.py -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

import sys
import os
import pytest

# --- Path Setup --- 
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

"""
PSP Orbit Data Caching Performance Test

PURPOSE:
Tests that psp_orbit data caching is working properly by comparing performance
between first run (loads data) and second run (should use cached data).

HOW TO RUN:
1. Open terminal and navigate to the Plotbot project root directory
2. Run: conda run -n plotbot_env python tests/test_orbit_performance.py

EXPECTED RESULTS:
- First run: ~3-5 seconds (loading and processing data)
- Second run: <1 second (using cached data)
- Speedup: 3x+ faster
- Cache working: YES
- Should see "psp_orbit_data already calculated" messages on second run

WHAT THIS TESTS:
- NPZ data format handling in data_import.py
- Data caching in data_cubby.py
- Variable calculation optimization in psp_orbit.py
- Key mapping consistency in get_data.py

If cache is NOT working, second run will take similar time as first run.
"""

from plotbot import *
import time

# Enable debug output
print_manager.show_status = True
print_manager.show_processing = True  # Enable tracker debug prints
print_manager.show_data_cubby = True # Keep this off for cleaner output unless needed

# --- Test Time Range ---
trange = ['2021-11-20/00:00:00.000', '2021-11-23/00:00:00.000']

# --- mag_rtn_4sa test (Baseline for good performance) ---
print('--- Testing mag_rtn_4sa caching performance (BASELINE) ---')
# First run - should download and cache the data
print('=== Mag First run ===')
start_mag1 = time.time()
plotbot(trange, mag_rtn_4sa.br, 1)
first_time_mag = time.time() - start_mag1
print(f'Mag First run time: {first_time_mag:.2f}s')

# Second run - should use cached data
print('\n=== Mag Second run ===')
start_mag2 = time.time()
plotbot(trange, mag_rtn_4sa.br, 1)
second_time_mag = time.time() - start_mag2
print(f'Mag Second run time: {second_time_mag:.2f}s')
speedup_mag = first_time_mag / second_time_mag if second_time_mag > 0 else 0
print(f'Mag Speedup: {speedup_mag:.1f}x faster')
print('--- End Baseline Test ---\n\n')


# --- psp_orbit test (The one we are investigating) ---
print('--- Testing psp_orbit caching performance ---')
# First run - should load and cache the data (EXACTLY like the mag test)
print('=== Orbit First run ===')
start_orbit1 = time.time()
plotbot(trange, psp_orbit.orbital_speed, 1)
first_time_orbit = time.time() - start_orbit1
print(f'Orbit First run time: {first_time_orbit:.2f}s')

# Second run - should use cached data (this is the key test!)
print('\n=== Orbit Second run ===')
start_orbit2 = time.time()
plotbot(trange, psp_orbit.orbital_speed, 1)
second_time_orbit = time.time() - start_orbit2
print(f'Orbit Second run time: {second_time_orbit:.2f}s')

speedup_orbit = first_time_orbit/second_time_orbit if second_time_orbit > 0 else 0
cache_working = 'YES' if speedup_orbit > 10 else 'NO'
print(f'\nOrbit Speedup: {speedup_orbit:.1f}x faster')
print(f'Orbit Cache working (>10x): {cache_working}') 