# tests/test_orbit_performance.py
# To run this test from the project root directory and see print output in the console:
# conda run -n plotbot_env python tests/test_orbit_performance.py
# Or using pytest:
# conda run -n plotbot_env python -m pytest tests/test_orbit_performance.py -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

import sys
import os
import pytest
from datetime import datetime

# --- Path Setup --- 
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

# --- Auto-save setup ---
class OutputCapture:
    def __init__(self):
        self.output = []
        self.original_stdout = sys.stdout
        
    def write(self, text):
        self.output.append(text)
        self.original_stdout.write(text)
        
    def flush(self):
        self.original_stdout.flush()
        
    def save_output(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_orbit_performance_output_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(''.join(self.output))
        print(f"\n📁 Debug output saved to: {filename}")

# Capture all output
output_capture = OutputCapture()
sys.stdout = output_capture

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
import numpy as np
from plotbot.data_classes.psp_orbit import psp_orbit_class

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
mag_data_length = len(mag_rtn_4sa.br.data) if hasattr(mag_rtn_4sa.br, 'data') and mag_rtn_4sa.br.data is not None else 0
print(f'Mag First run time: {first_time_mag:.2f}s')
print(f'Mag data points: {mag_data_length}')
print(f'Mag processing time per point: {first_time_mag/mag_data_length*1000:.4f}ms/point' if mag_data_length > 0 else 'N/A')

# Second run - should use cached data
print('\n=== Mag Second run ===')
start_mag2 = time.time()
plotbot(trange, mag_rtn_4sa.br, 1)
second_time_mag = time.time() - start_mag2
mag_data_length_2 = len(mag_rtn_4sa.br.data) if hasattr(mag_rtn_4sa.br, 'data') and mag_rtn_4sa.br.data is not None else 0
print(f'Mag Second run time: {second_time_mag:.2f}s')
print(f'Mag data points: {mag_data_length_2}')
print(f'Mag processing time per point: {second_time_mag/mag_data_length_2*1000:.4f}ms/point' if mag_data_length_2 > 0 else 'N/A')
speedup_mag = first_time_mag / second_time_mag if second_time_mag > 0 else 0
print(f'Mag Speedup: {speedup_mag:.1f}x faster')
print(f'Mag Performance Ratio (2nd/1st): {second_time_mag/first_time_mag:.3f}' if first_time_mag > 0 else 'N/A')
print('--- End Baseline Test ---\n\n')


# --- psp_orbit test (The one we are investigating) ---
print('--- Testing psp_orbit caching performance ---')
# First run - should load and cache the data (EXACTLY like the mag test)
print('=== Orbit First run ===')
start_orbit1 = time.time()
plotbot(trange, psp_orbit.orbital_speed, 1)
first_time_orbit = time.time() - start_orbit1
orbit_data_length = len(psp_orbit.orbital_speed.data) if hasattr(psp_orbit.orbital_speed, 'data') and psp_orbit.orbital_speed.data is not None else 0
print(f'Orbit First run time: {first_time_orbit:.2f}s')
print(f'Orbit data points: {orbit_data_length}')
print(f'Orbit processing time per point: {first_time_orbit/orbit_data_length*1000:.4f}ms/point' if orbit_data_length > 0 else 'N/A')

# Second run - should use cached data (this is the key test!)
print('\n=== Orbit Second run ===')
start_orbit2 = time.time()
plotbot(trange, psp_orbit.orbital_speed, 1)
second_time_orbit = time.time() - start_orbit2
orbit_data_length_2 = len(psp_orbit.orbital_speed.data) if hasattr(psp_orbit.orbital_speed, 'data') and psp_orbit.orbital_speed.data is not None else 0
print(f'Orbit Second run time: {second_time_orbit:.2f}s')
print(f'Orbit data points: {orbit_data_length_2}')
print(f'Orbit processing time per point: {second_time_orbit/orbit_data_length_2*1000:.4f}ms/point' if orbit_data_length_2 > 0 else 'N/A')

speedup_orbit = first_time_orbit/second_time_orbit if second_time_orbit > 0 else 0
cache_working = 'YES' if speedup_orbit > 10 else 'NO'
print(f'\nOrbit Speedup: {speedup_orbit:.1f}x faster')
print(f'Orbit Performance Ratio (2nd/1st): {second_time_orbit/first_time_orbit:.3f}' if first_time_orbit > 0 else 'N/A')
print(f'Orbit Cache working (>10x): {cache_working}') 

# --- DETAILED ORBIT BREAKDOWN TEST ---
print('\n--- DETAILED ORBIT BREAKDOWN TEST ---')
print('Testing just the orbital mechanics calculation on 73 points...')

# Test just the calculation part
test_start = time.time()
try:
    # Create test data similar to what orbit class processes
    n_points = 73
    test_r_sun = np.linspace(10, 50, n_points)
    test_icrf_x = np.linspace(-30, 30, n_points) 
    test_icrf_y = np.linspace(-30, 30, n_points)
    test_icrf_z = np.linspace(-5, 5, n_points)
    
    # Test the orbital mechanics calculation directly
    orbit_instance = psp_orbit_class(None)  # Create empty instance
    speed, vx, vy, vz, angular_momentum = orbit_instance._calculate_orbital_mechanics_icrf(
        test_icrf_x, test_icrf_y, test_icrf_z, test_r_sun)
    
    calc_time = time.time() - test_start
    print(f'Pure calculation time for 73 points: {calc_time*1000:.2f}ms')
    print(f'Pure calculation per point: {calc_time/n_points*1000:.4f}ms/point')
    
except Exception as e:
    print(f'Calculation test failed: {e}')

# --- Performance Per Point Comparison ---
print('\n--- PERFORMANCE PER POINT COMPARISON ---')
if mag_data_length > 0 and orbit_data_length > 0:
    mag_1st_per_point = first_time_mag/mag_data_length*1000
    mag_2nd_per_point = second_time_mag/mag_data_length_2*1000
    orbit_1st_per_point = first_time_orbit/orbit_data_length*1000
    orbit_2nd_per_point = second_time_orbit/orbit_data_length_2*1000
    
    print(f'Mag:   {mag_1st_per_point:.4f}ms/point → {mag_2nd_per_point:.4f}ms/point')
    print(f'Orbit: {orbit_1st_per_point:.4f}ms/point → {orbit_2nd_per_point:.4f}ms/point')
    print(f'Orbit is {orbit_1st_per_point/mag_1st_per_point:.1f}x slower per point (1st run)')
    print(f'Orbit is {orbit_2nd_per_point/mag_2nd_per_point:.1f}x slower per point (2nd run)')
else:
    print('Cannot calculate per-point comparison - missing data lengths')

# --- Generate comprehensive timing analysis report ---
print("\n\n" + "="*80)
print("🎯 GENERATING COMPREHENSIVE TIMING ANALYSIS")
print("="*80)

# Import the timing tracker and generate comprehensive report
try:
    from speed_test import timing_tracker
    if hasattr(timing_tracker, 'timings') and timing_tracker.timings:
        timing_tracker.print_comprehensive_report()
    else:
        print("No timing data available in timing_tracker")
except ImportError:
    print("Could not import timing_tracker")
except Exception as e:
    print(f"Error generating timing report: {e}")

# --- Save output automatically ---
sys.stdout = output_capture.original_stdout  # Restore stdout
output_capture.save_output() 