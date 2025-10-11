#!/usr/bin/env python3
"""Compare lambda vs direct expression resampling"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton

print("\n" + "="*70)
print("COMPARISON: Lambda vs Direct Expression for mixed cadences")
print("="*70)

# Test with LAMBDA
lambda_var = custom_variable('lambda_test', lambda: mag_rtn_4sa.bmag / proton.vr)

# Test with DIRECT EXPRESSION
direct_var = custom_variable('direct_test', mag_rtn_4sa.bmag / proton.vr)

test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']

print(f"\n1️⃣  Testing LAMBDA...")
plotbot.plotbot(test_trange, lambda_var, 1)
lambda_result = np.array(plotbot.lambda_test.data)
print(f"   Lambda result shape: {lambda_result.shape}")
print(f"   Lambda sample: {lambda_result[:3]}")

print(f"\n2️⃣  Testing DIRECT EXPRESSION...")
plotbot.plotbot(test_trange, direct_var, 1)
direct_result = np.array(plotbot.direct_test.data)
print(f"   Direct result shape: {direct_result.shape}")
print(f"   Direct sample: {direct_result[:3]}")

print(f"\n3️⃣  Comparing results...")
if lambda_result.shape == direct_result.shape:
    print(f"   ✅ Same shape: {lambda_result.shape}")
    
    if np.allclose(lambda_result, direct_result, rtol=1e-5):
        print(f"   ✅ Values match (within tolerance)")
        print(f"\n🎉 BOTH METHODS WORK AND PRODUCE IDENTICAL RESULTS!")
        print(f"\n💡 Conclusion:")
        print(f"   - Lambda: Uses plot_manager.align_variables() during division")
        print(f"   - Direct: Uses custom_variables.update() resampling")
        print(f"   - Both produce the same result!")
    else:
        max_diff = np.max(np.abs(lambda_result - direct_result))
        print(f"   ⚠️  Values differ! Max difference: {max_diff}")
else:
    print(f"   ❌ Different shapes: lambda={lambda_result.shape}, direct={direct_result.shape}")

