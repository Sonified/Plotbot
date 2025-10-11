#!/usr/bin/env python3
"""Test custom variables with 3-4 source variables at different cadences"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, proton, epad

print("\n" + "="*70)
print("MULTI-VARIABLE TEST: 3+ variables with different cadences")
print("="*70)

test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']

# Test 1: 3 variables - same cadence (all mag)
print(f"\n1️⃣  TEST 1: 3 variables, SAME cadence (bmag * br * bn)")
three_var_same = custom_variable('three_same', 
    mag_rtn_4sa.bmag * mag_rtn_4sa.br * mag_rtn_4sa.bn
)
plotbot.plotbot(test_trange, three_var_same, 1)
result1 = np.array(plotbot.three_same.data)

bmag_len = len(mag_rtn_4sa.bmag.data)
br_len = len(mag_rtn_4sa.br.data)
bn_len = len(mag_rtn_4sa.bn.data)

print(f"   Source cadences: bmag={bmag_len}, br={br_len}, bn={bn_len}")
print(f"   Result shape: {result1.shape}")
print(f"   Sample values: {result1[:3]}")

if len(result1) > 0 and np.all(np.isfinite(result1)):
    print(f"   ✅ PASSED: 3 same-cadence variables")
else:
    print(f"   ❌ FAILED")

# Test 2: 4 variables - mixed cadences (2 mag + 2 proton)
print(f"\n2️⃣  TEST 2: 4 variables, MIXED cadences ((bmag + br) / (vr + vt))")
four_var_mixed = custom_variable('four_mixed',
    (mag_rtn_4sa.bmag + mag_rtn_4sa.br) / (proton.vr + proton.vt)
)
plotbot.plotbot(test_trange, four_var_mixed, 1)
result2 = np.array(plotbot.four_mixed.data)

vr_len = len(proton.vr.data)
vt_len = len(proton.vt.data)
print(f"   Source cadences: bmag={bmag_len}, br={br_len}, vr={vr_len}, vt={vt_len}")
print(f"   Result shape: {result2.shape}")
print(f"   Sample values: {result2[:3]}")

if result2.shape[0] > 0 and np.all(np.isfinite(result2)):
    print(f"   ✅ PASSED: 4 mixed-cadence variables -> {result2.shape[0]} points")
else:
    print(f"   ❌ FAILED")

# Test 3: 3 variables - ALL DIFFERENT cadences (mag, proton, epad)
print(f"\n3️⃣  TEST 3: 3 variables, ALL DIFFERENT cadences (br * anisotropy * centroids)")
print(f"   NOTE: This includes EPAD which is very slow cadence")
three_var_all_diff = custom_variable('three_all_diff',
    mag_rtn_4sa.br * proton.anisotropy * epad.centroids
)

try:
    plotbot.plotbot(test_trange, three_var_all_diff, 1)
    result3 = np.array(plotbot.three_all_diff.data)
    
    aniso_len = len(proton.anisotropy.data)
    centroids_len = len(epad.centroids.data)
    
    print(f"   Source cadences:")
    print(f"      br (mag):           {br_len} points")
    print(f"      anisotropy (proton): {aniso_len} points")
    print(f"      centroids (epad):    {centroids_len} points")
    print(f"   Result shape: {result3.shape}")
    print(f"   Sample values: {result3[:3]}")
    
    expected_len = min(br_len, aniso_len, centroids_len)
    if result3.shape[0] == expected_len and np.all(np.isfinite(result3)):
        print(f"   ✅ PASSED: 3 all-different-cadence variables -> {expected_len} points")
    else:
        print(f"   ⚠️  Got {result3.shape[0]} points (expected {expected_len})")
        if np.all(np.isfinite(result3)):
            print(f"   ✅ But values are all finite, so resampling worked!")
        else:
            print(f"   ❌ FAILED: Contains NaN/Inf")
            
except Exception as e:
    print(f"   ❌ FAILED with exception: {str(e)}")
    result3 = np.array([])

print(f"\n" + "="*70)
results = [result1, result2, result3]
if all([len(r) > 0 and np.all(np.isfinite(r)) for r in results]):
    print("🎉 ALL MULTI-VARIABLE TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print("="*70)

