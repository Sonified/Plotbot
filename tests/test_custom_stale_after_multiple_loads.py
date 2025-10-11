#!/usr/bin/env python3
"""
Test custom variable creation AFTER loading data with MULTIPLE different tranges.

This mimics what happens in the comprehensive test where EDGE CASE 8 and 9 fail.
The issue is that raw_data accumulates from multiple tranges, but datetime_array
only shows the most recent trange. When a direct expression evaluates at definition
time, the mismatched datetime arrays cause interpolation errors.
"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton
from plotbot.print_manager import print_manager

# Enable debug output
print_manager.custom_debug_enabled = True

print("\n" + "="*70)
print("STALE DATA TEST: Multiple trange loads before custom variable")
print("="*70)

# Step 1: Load data with trange A
print("\n[STEP 1] Load trange A (10 min)...")
trange_A = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange_A, mag_rtn_4sa.bmag, 1, proton.vr, 2)
print(f"  bmag: raw={len(mag_rtn_4sa.raw_data.get('bmag', []))}, data={len(mag_rtn_4sa.bmag.data)}, dt={len(mag_rtn_4sa.bmag.datetime_array) if hasattr(mag_rtn_4sa.bmag, 'datetime_array') and mag_rtn_4sa.bmag.datetime_array is not None else 0}")
print(f"  vr:   raw={len(proton.raw_data.get('vr', []))}, data={len(proton.vr.data)}, dt={len(proton.vr.datetime_array) if hasattr(proton.vr, 'datetime_array') and proton.vr.datetime_array is not None else 0}")

# Step 2: Load data with trange B (1 hour - ACCUMULATES)
print("\n[STEP 2] Load trange B (1 hour)...")
trange_B = ['2020-01-29/18:00:00', '2020-01-29/19:00:00']
plotbot.plotbot(trange_B, mag_rtn_4sa.bmag, 1, proton.vr, 2)
print(f"  bmag: raw={len(mag_rtn_4sa.raw_data.get('bmag', []))}, data={len(mag_rtn_4sa.bmag.data)}, dt={len(mag_rtn_4sa.bmag.datetime_array) if hasattr(mag_rtn_4sa.bmag, 'datetime_array') and mag_rtn_4sa.bmag.datetime_array is not None else 0}")
print(f"  vr:   raw={len(proton.raw_data.get('vr', []))}, data={len(proton.vr.data)}, dt={len(proton.vr.datetime_array) if hasattr(proton.vr, 'datetime_array') and proton.vr.datetime_array is not None else 0}")

# Step 3: Load data with trange C (different day - ACCUMULATES MORE)
print("\n[STEP 3] Load trange C (different day)...")
trange_C = ['2020-02-15/12:00:00', '2020-02-15/12:30:00']
plotbot.plotbot(trange_C, mag_rtn_4sa.bmag, 1, proton.vr, 2)
print(f"  bmag: raw={len(mag_rtn_4sa.raw_data.get('bmag', []))}, data={len(mag_rtn_4sa.bmag.data)}, dt={len(mag_rtn_4sa.bmag.datetime_array) if hasattr(mag_rtn_4sa.bmag, 'datetime_array') and mag_rtn_4sa.bmag.datetime_array is not None else 0}")
print(f"  vr:   raw={len(proton.raw_data.get('vr', []))}, data={len(proton.vr.data)}, dt={len(proton.vr.datetime_array) if hasattr(proton.vr, 'datetime_array') and proton.vr.datetime_array is not None else 0}")

# Step 4: Load more variables (br, vt) for the first time
print("\n[STEP 4] Load br and vt with trange C...")
plotbot.plotbot(trange_C, mag_rtn_4sa.br, 1, proton.vt, 2)
print(f"  br:   raw={len(mag_rtn_4sa.raw_data.get('br', []))}, data={len(mag_rtn_4sa.br.data)}, dt={len(mag_rtn_4sa.br.datetime_array) if hasattr(mag_rtn_4sa.br, 'datetime_array') and mag_rtn_4sa.br.datetime_array is not None else 0}")
print(f"  vt:   raw={len(proton.raw_data.get('vt', []))}, data={len(proton.vt.data)}, dt={len(proton.vt.datetime_array) if hasattr(proton.vt, 'datetime_array') and proton.vt.datetime_array is not None else 0}")

# Step 5: NOW create custom variable with direct expression
# This is where the problem happens - the variables have mismatched datetime arrays!
print("\n[STEP 5] Create custom variable with direct expression...")
print("  NOTE: This evaluates IMMEDIATELY using current stale data!")
print(f"  bmag datetime_array: {len(mag_rtn_4sa.bmag.datetime_array) if hasattr(mag_rtn_4sa.bmag, 'datetime_array') and mag_rtn_4sa.bmag.datetime_array is not None else 0} points")
print(f"  br datetime_array:   {len(mag_rtn_4sa.br.datetime_array) if hasattr(mag_rtn_4sa.br, 'datetime_array') and mag_rtn_4sa.br.datetime_array is not None else 0} points")
print(f"  vr datetime_array:   {len(proton.vr.datetime_array) if hasattr(proton.vr, 'datetime_array') and proton.vr.datetime_array is not None else 0} points")
print(f"  vt datetime_array:   {len(proton.vt.datetime_array) if hasattr(proton.vt, 'datetime_array') and proton.vt.datetime_array is not None else 0} points")

try:
    # This mimics EDGE CASE 8
    test_var = custom_variable('test_stale_multi',
        (mag_rtn_4sa.bmag + mag_rtn_4sa.br) / (proton.vr + proton.vt)
    )
    print(f"  ✅ Custom variable created successfully")
except Exception as e:
    print(f"  ❌ Failed at definition time: {str(e)[:150]}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70)
    print("❌ TEST FAILED: Cannot handle stale data from multiple tranges")
    print("="*70)
    exit(1)

# Step 6: Try to use it with a NEW trange D
print("\n[STEP 6] Use custom variable with NEW trange D...")
trange_D = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']

try:
    plotbot.plotbot(trange_D, test_var, 1)
    result = np.array(plotbot.test_stale_multi.data)
    
    print(f"  Result shape: {result.shape}")
    if len(result) > 0 and np.all(np.isfinite(result)):
        print(f"  ✅ SUCCESS!")
    else:
        print(f"  ❌ Result is empty or contains NaN/Inf")
        exit(1)
        
except Exception as e:
    print(f"  ❌ Failed at evaluation time: {str(e)[:150]}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*70)
print("✅ TEST PASSED: Handles stale data from multiple tranges")
print("="*70)

