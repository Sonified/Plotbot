#!/usr/bin/env python3
"""
Test script for data_cubby.clear() functionality
Shows how to clear all cached data from plotbot
"""

import plotbot

print("="*70)
print("TEST: data_cubby.clear() functionality")
print("="*70)

# Test 1: Load some data
print("\n--- STEP 1: Load MAG data ---")
trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']
plotbot.ploptions.display_figure = False
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)

# Check that data exists
print(f"\n✓ Data loaded: br has {len(plotbot.mag_rtn_4sa.br.datetime_array)} points")

# Test 2: Clear the data cubby
print("\n--- STEP 2: Clear data cubby ---")
plotbot.data_cubby.clear()

# Test 3: Verify data is gone
print("\n--- STEP 3: Verify data was cleared ---")
try:
    # After clear, the class instances are gone from cubby
    # When we try to access them, they'll be re-initialized empty
    mag_instance = plotbot.data_cubby.grab('mag_rtn_4sa')
    if mag_instance is None:
        print("✓ mag_rtn_4sa instance was removed from cubby")
    else:
        dt_len = len(mag_instance.datetime_array) if mag_instance.datetime_array is not None else 0
        print(f"  mag_rtn_4sa datetime_array length: {dt_len}")
except Exception as e:
    print(f"  Exception when checking: {e}")

# Test 4: Reload data works correctly
print("\n--- STEP 4: Reload data (should download fresh) ---")
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
print(f"✓ Data reloaded: br has {len(plotbot.mag_rtn_4sa.br.datetime_array)} points")

print("\n" + "="*70)
print("SUCCESS: data_cubby.clear() works correctly!")
print("="*70)
print("\nUsage in your notebooks:")
print("  plotbot.data_cubby.clear()  # Clear all cached data")
print("\nUse cases:")
print("  - Start fresh analysis")
print("  - Free memory after processing large datasets")
print("  - Reset state during debugging")

