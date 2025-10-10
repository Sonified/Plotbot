"""
Minimal test to isolate the bn replacement bug.

ISSUE: When custom variables use bn, the bn variable in plot arguments
gets replaced by the custom variable in subsequent plotbot() calls.
"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa
from plotbot.print_manager import print_manager

def test_bn_replacement_bug():
    # Enable custom debug output
    print_manager.custom_debug_enabled = True
    """Test that bn doesn't get replaced by custom variables that use it"""
    
    print("\n" + "="*70)
    print("TEST: bn Replacement Bug")
    print("="*70)
    
    trange1 = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    trange2 = ['2020-02-15/12:00:00', '2020-02-15/12:30:00']
    
    # Step 1: Create a custom variable that uses bn
    print("\n[STEP 1] Creating custom variable that uses bn...")
    abs_bn = custom_variable('abs_bn_test', lambda: np.abs(plotbot.mag_rtn_4sa.bn))
    print(f"  Created abs_bn_test")
    
    # Step 2: First plot - bn should work fine
    print("\n[STEP 2] First plotbot() call with bn...")
    print(f"  Calling plotbot({trange1}, bn, 1, abs_bn, 2)")
    plotbot.plotbot(trange1, mag_rtn_4sa.bn, 1, abs_bn, 2)
    
    bn_data_1 = np.array(mag_rtn_4sa.bn.data)
    print(f"  ✅ bn.data shape after first call: {bn_data_1.shape}")
    print(f"  🔍 mag_rtn_4sa.bn ID: {id(mag_rtn_4sa.bn)}, class: {mag_rtn_4sa.bn.class_name}.{mag_rtn_4sa.bn.subclass_name}")
    
    # Step 3: Second plot with DIFFERENT trange - bn should still work
    print("\n[STEP 3] Second plotbot() call with bn (different trange)...")
    print(f"  🔍 BEFORE second call - mag_rtn_4sa.bn ID: {id(mag_rtn_4sa.bn)}, class: {mag_rtn_4sa.bn.class_name}.{mag_rtn_4sa.bn.subclass_name}")
    print(f"  Calling plotbot({trange2}, bn, 1, abs_bn, 2)")
    plotbot.plotbot(trange2, mag_rtn_4sa.bn, 1, abs_bn, 2)
    
    bn_data_2 = np.array(mag_rtn_4sa.bn.data)
    abs_bn_data_2 = np.array(plotbot.abs_bn_test.data)
    
    print(f"  bn.data shape after second call: {bn_data_2.shape}")
    print(f"  abs_bn_test.data shape: {abs_bn_data_2.shape}")
    
    # Step 4: Verify shapes match
    print("\n[STEP 4] Verifying shapes match...")
    if bn_data_2.shape == abs_bn_data_2.shape:
        print(f"  ✅ PASS: Shapes match ({bn_data_2.shape})")
        print(f"  ✅ bn was NOT replaced by abs_bn!")
    else:
        print(f"  ❌ FAIL: Shape mismatch!")
        print(f"     bn.data: {bn_data_2.shape}")
        print(f"     abs_bn_test.data: {abs_bn_data_2.shape}")
        print(f"  ❌ bn appears to have been replaced or has wrong data!")
        raise AssertionError("bn variable has wrong data shape")
    
    # Step 5: Verify calculation is correct
    print("\n[STEP 5] Verifying calculation...")
    expected = np.abs(bn_data_2)
    if np.allclose(abs_bn_data_2, expected):
        print(f"  ✅ PASS: abs_bn calculation is correct")
    else:
        print(f"  ❌ FAIL: abs_bn calculation is wrong")
        raise AssertionError("abs_bn calculation doesn't match expected")
    
    print("\n" + "="*70)
    print("ALL CHECKS PASSED! ✅")
    print("="*70)
    return True

if __name__ == "__main__":
    test_bn_replacement_bug()

