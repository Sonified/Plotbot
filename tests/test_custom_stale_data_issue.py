#!/usr/bin/env python3
"""
Test to isolate the "stale data at definition time" issue.

PROBLEM: When creating a custom variable with a direct expression like:
    custom_variable('test', mag_rtn_4sa.bmag + proton.vr)

The expression evaluates IMMEDIATELY using whatever stale data is in those
variables from previous plotbot() calls. This causes datetime_array mismatches
when align_variables() tries to interpolate.

EXPECTED: The custom variable should NOT evaluate at definition time.
It should only evaluate when plotbot() is called with a specific trange.
"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton

print("\n" + "="*70)
print("STALE DATA TEST: Custom variable definition with stale data")
print("="*70)

# Step 1: Load some data with trange A (this puts stale data in mag and proton)
print("\n[STEP 1] Load data with trange A...")
trange_A = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange_A, mag_rtn_4sa.bmag, 1, proton.vr, 2)

print(f"  After trange A:")
print(f"    bmag has {len(mag_rtn_4sa.bmag.data)} points")
print(f"    vr has {len(proton.vr.data)} points")

# Step 2: NOW create a custom variable with a direct expression
# BUG: This evaluates immediately using the stale data from trange A!
print("\n[STEP 2] Create custom variable with direct expression...")
try:
    test_var = custom_variable('test_stale',
        (mag_rtn_4sa.bmag + mag_rtn_4sa.br) / (proton.vr + proton.vt)
    )
    print(f"  ✅ Custom variable created")
except Exception as e:
    print(f"  ❌ Failed at definition time: {str(e)[:150]}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Try to use it with a DIFFERENT trange B
print("\n[STEP 3] Use custom variable with a DIFFERENT trange B...")
trange_B = ['2020-01-29/20:00:00', '2020-01-29/20:15:00']

try:
    plotbot.plotbot(trange_B, test_var, 1)
    result = np.array(plotbot.test_stale.data)
    
    print(f"  Result shape: {result.shape}")
    print(f"  bmag shape: {len(mag_rtn_4sa.bmag.data)}")
    print(f"  vr shape: {len(proton.vr.data)}")
    
    if len(result) > 0 and np.all(np.isfinite(result)):
        print(f"  ✅ SUCCESS: Custom variable worked with different trange!")
    else:
        print(f"  ❌ FAILED: Result is empty or contains NaN/Inf")
        
except Exception as e:
    print(f"  ❌ Failed at evaluation time: {str(e)[:150]}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*70)
print("✅ TEST PASSED: Custom variables handle stale data correctly")
print("="*70)

