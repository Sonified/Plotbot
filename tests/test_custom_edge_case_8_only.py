#!/usr/bin/env python3
"""Test only EDGE CASE 8 to debug the issue"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton
from plotbot.print_manager import print_manager

# Enable debug
print_manager.custom_debug_enabled = True

print("\n" + "="*70)
print("EDGE CASE 8: 4 variables, MIXED cadences ((bmag + br) / (vr + vt))")
print("="*70)

# Load some initial data first (to mimic comprehensive test conditions)
print("\n[SETUP] Loading initial data...")
trange_setup = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange_setup, mag_rtn_4sa.bmag, 1, proton.vr, 2)
print(f"  Setup complete")

# Now create the custom variable
print("\n[TEST] Creating custom variable...")
four_var_mixed = custom_variable('four_mixed',
    (mag_rtn_4sa.bmag + mag_rtn_4sa.br) / (proton.vr + proton.vt)
)

test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
print(f"\n[TEST] Testing with trange: {test_trange}")

try:
    plotbot.plotbot(test_trange, four_var_mixed, 1)
    result = np.array(plotbot.four_mixed.data)
    
    bmag_len = len(mag_rtn_4sa.bmag.data)
    vr_len = len(proton.vr.data)
    print(f"\n  Result shape: {result.shape}")
    print(f"  Source cadences: bmag={bmag_len}, vr={vr_len}")
    
    expected_len = min(bmag_len, vr_len)
    if result.shape[0] == expected_len and np.all(np.isfinite(result)):
        print(f"  ✅ PASSED: 4 mixed-cadence variables -> {expected_len} points")
    else:
        print(f"  ❌ FAILED: Expected {expected_len}, got {result.shape[0]}")
        
except Exception as e:
    print(f"  ❌ FAILED: {str(e)[:200]}")
    import traceback
    traceback.print_exc()

