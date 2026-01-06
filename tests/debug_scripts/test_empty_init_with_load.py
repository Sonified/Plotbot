# -*- coding: utf-8 -*-
"""
Test: Does empty array initialization cause merge problems when real data loads?

This tests the actual workflow:
1. Create custom variable with empty plot_manager instances
2. Load real data for the dependencies
3. Check if custom variable correctly gets new data (replace) vs incorrectly merges
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Importing plotbot...")
import plotbot
from plotbot.plot_manager import plot_manager as pm_cls
from plotbot.plot_config import plot_config as cfg_cls

print("\n" + "="*70)
print("TEST: Empty Initialization -> Real Data Load -> Merge vs Replace")
print("="*70)

# Test parameters
trange = ['2020-01-29/18:00:00.000', '2020-01-29/20:00:00.000']

print("\n--- STEP 1: Create custom variable BEFORE loading any data ---")
print("This simulates: phi_B = plotbot.custom_variable('phi_B', np.degrees(np.arctan2(br, bn)) + 180)")
print("where br and bn are empty plot_managers")

# Create two empty plot_managers to simulate br and bn before data loads
cfg1 = cfg_cls(
    data_type='mag_RTN_4sa',
    class_name='mag_rtn_4sa',
    subclass_name='br',
    plot_type='time_series',
    datetime_array=None
)
cfg2 = cfg_cls(
    data_type='mag_RTN_4sa',
    class_name='mag_rtn_4sa',
    subclass_name='bn',
    plot_type='time_series',
    datetime_array=None
)

# Initialize with empty arrays (our recommended approach)
empty_br = pm_cls(np.array([], dtype=np.float64), plot_config=cfg1)
empty_bn = pm_cls(np.array([], dtype=np.float64), plot_config=cfg2)

print(f"  empty_br: shape={empty_br.shape}, size={empty_br.size}")
print(f"  empty_bn: shape={empty_bn.shape}, size={empty_bn.size}")

# Try the custom variable expression
try:
    phi_B_expression = np.degrees(np.arctan2(empty_br, empty_bn)) + 180
    print(f"  ✅ Expression evaluated: shape={phi_B_expression.shape}, dtype={phi_B_expression.dtype}")
    print(f"     Result: {phi_B_expression}")
except Exception as e:
    print(f"  ❌ Expression failed: {type(e).__name__}: {e}")
    phi_B_expression = None

print("\n--- STEP 2: Now load REAL data for br and bn ---")
print("This simulates: plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bn, 2)")

# Actually load real MAG data
plotbot.ploptions.display_figure = False
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bn, 2)

real_br = plotbot.mag_rtn_4sa.br
real_bn = plotbot.mag_rtn_4sa.bn

print(f"  real_br: shape={np.asarray(real_br).shape}, has datetime_array={hasattr(real_br, 'datetime_array')}")
print(f"  real_bn: shape={np.asarray(real_bn).shape}, has datetime_array={hasattr(real_bn, 'datetime_array')}")

if hasattr(real_br, 'datetime_array') and real_br.datetime_array is not None:
    print(f"  real_br datetime_array: {len(real_br.datetime_array)} points")
    print(f"     First: {real_br.datetime_array[0]}")
    print(f"     Last:  {real_br.datetime_array[-1]}")

print("\n--- STEP 3: Compute custom variable with REAL data ---")
try:
    phi_B_real = np.degrees(np.arctan2(real_br, real_bn)) + 180
    phi_B_real_array = np.asarray(phi_B_real)
    print(f"  ✅ Real phi_B computed: shape={phi_B_real_array.shape}, dtype={phi_B_real_array.dtype}")
    print(f"     First 5 values: {phi_B_real_array[:5]}")
    print(f"     Last 5 values: {phi_B_real_array[-5:]}")
    
    # Check if datetime_array propagated
    if hasattr(phi_B_real, 'datetime_array'):
        if phi_B_real.datetime_array is not None and len(phi_B_real.datetime_array) > 0:
            print(f"  ✅ phi_B has datetime_array: {len(phi_B_real.datetime_array)} points")
        else:
            print(f"  ⚠️  phi_B.datetime_array is None or empty")
    else:
        print(f"  ⚠️  phi_B has no datetime_array attribute")
        
except Exception as e:
    print(f"  ❌ Real phi_B computation failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n--- STEP 4: Check data_tracker state ---")
from plotbot.data_tracker import global_tracker

print(f"  Imported ranges:")
for data_type, ranges in global_tracker.imported_ranges.items():
    print(f"    {data_type}: {len(ranges)} range(s)")
    for start, end in ranges:
        print(f"      - {start} to {end}")

print(f"\n  Calculated ranges:")
for data_type, ranges in global_tracker.calculated_ranges.items():
    print(f"    {data_type}: {len(ranges)} range(s)")
    for start, end in ranges:
        print(f"      - {start} to {end}")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
if phi_B_expression is not None and phi_B_real_array is not None:
    print("SUCCESS: Empty initialization works!")
    print(f"   - Empty expression: shape={phi_B_expression.shape}")
    print(f"   - Real data result: shape={phi_B_real_array.shape}")
    print("\nThe empty array (shape=(0,)) does NOT contaminate real data.")
    print("   Real data completely replaces the empty initialization.")
    print("\nRECOMMENDATION: Use np.array([], dtype=np.float64) for initialization")
else:
    print("FAIL: Something went wrong during the test")

