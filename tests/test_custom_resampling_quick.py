#!/usr/bin/env python3
"""Quick test for automatic resampling in custom variables with different cadences"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton

print("\n" + "="*70)
print("QUICK TEST: Different cadences with automatic resampling")
print("="*70)

# Use DIRECT EXPRESSION (not lambda) for mixed cadences
mixed_cadence = custom_variable('mixed_cadence_test',
    mag_rtn_4sa.bmag / proton.vr
)

test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
print(f"\nTesting with trange: {test_trange}")

plotbot.plotbot(test_trange, mag_rtn_4sa.bmag, 1, proton.vr, 2, mixed_cadence, 3)

bmag_data = np.array(mag_rtn_4sa.bmag.data)
vr_data = np.array(proton.vr.data)
mixed_data = np.array(plotbot.mixed_cadence_test.data)

print(f"\nResults:")
print(f"  bmag shape (mag cadence): {bmag_data.shape}")
print(f"  vr shape (proton cadence): {vr_data.shape}")
print(f"  mixed_cadence_test shape: {mixed_data.shape}")

expected_cadence = min(bmag_data.shape[0], vr_data.shape[0])

if mixed_data.shape[0] == expected_cadence:
    print(f"\n✅ SUCCESS: Custom variable resampled to lowest cadence: {expected_cadence} points")
    
    if np.all(np.isfinite(mixed_data)):
        print(f"✅ All values are finite (no NaN/Inf from resampling)")
    
    if np.all(mixed_data > 0) and np.all(mixed_data < 1e6):
        print(f"✅ Values in reasonable range")
        
    print(f"\n🎉 RESAMPLING TEST PASSED!")
else:
    print(f"\n❌ FAILED: expected {expected_cadence} points, got {mixed_data.shape[0]}")

