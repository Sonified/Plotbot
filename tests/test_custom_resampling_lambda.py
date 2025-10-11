#!/usr/bin/env python3
"""Test if resampling works with LAMBDA custom variables"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton

print("\n" + "="*70)
print("TEST: Different cadences with LAMBDA (expected to fail)")
print("="*70)

# Try with LAMBDA - this should fail
mixed_cadence = custom_variable('mixed_cadence_lambda',
    lambda: mag_rtn_4sa.bmag / proton.vr
)

test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
print(f"\nTesting LAMBDA with trange: {test_trange}")

try:
    plotbot.plotbot(test_trange, mag_rtn_4sa.bmag, 1, proton.vr, 2, mixed_cadence, 3)
    
    mixed_data = np.array(plotbot.mixed_cadence_lambda.data)
    
    if len(mixed_data) == 0:
        print(f"\n✅ EXPECTED: Lambda failed silently, got empty array: {mixed_data.shape}")
        print(f"   Lambda cannot auto-resample mixed cadences")
    else:
        print(f"\n⚠️  UNEXPECTED: Lambda worked! Got {mixed_data.shape[0]} points")
        print(f"   Values: min={mixed_data.min():.2f}, max={mixed_data.max():.2f}")
    
except Exception as e:
    print(f"\n✅ EXPECTED FAILURE: Lambda cannot auto-resample")
    print(f"   Error: {str(e)[:100]}")

print(f"\n💡 Solution: Use direct expressions for mixed cadences:")
print(f"   custom_variable('mixed', mag_rtn_4sa.bmag / proton.vr)")
print(f"   NOT: lambda: mag_rtn_4sa.bmag / proton.vr")

