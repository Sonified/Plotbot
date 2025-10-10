"""
Test to verify custom variables don't have stale reference bugs.

This test reproduces Sam's exact issue:
1. Define custom variable BEFORE data loads (variables are empty)
2. Call plotbot() which creates NEW plot_managers for br, bn
3. Verify custom variable correctly uses the NEW objects, not stale empty ones
4. Verify source variables (br, bn) are NOT corrupted
"""

import numpy as np
import plotbot
import sys

def test_custom_variable_stale_reference():
    """Test that custom variables re-resolve sources correctly after plotbot() updates"""
    
    print("\n" + "="*70)
    print("TEST: Custom Variable Stale Reference Fix")
    print("="*70)
    
    # Step 1: Define custom variable BEFORE data loads (Sam's workflow)
    print("\n[STEP 1] Defining custom variable before data loads...")
    plotbot.custom_variable(
        'phi_B',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
    )
    print(f"  phi_B accessible via: plotbot.phi_B")
    print(f"  phi_B data shape: {plotbot.phi_B.shape}")
    print(f"  br data shape: {plotbot.mag_rtn_4sa.br.shape}")
    print(f"  bn data shape: {plotbot.mag_rtn_4sa.bn.shape}")
    
    # Step 2: Call plotbot() which loads data and creates NEW plot_managers
    print("\n[STEP 2] Calling plotbot() to load data...")
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bn, 2, plotbot.phi_B, 3)
    
    # Step 3: Verify custom variable has correct data
    print("\n[STEP 3] Verifying custom variable data...")
    br_data = np.array(plotbot.mag_rtn_4sa.br.data)
    bn_data = np.array(plotbot.mag_rtn_4sa.bn.data)
    phi_B_data = np.array(plotbot.phi_B.data)
    
    print(f"  br data shape: {br_data.shape}")
    print(f"  bn data shape: {bn_data.shape}")
    print(f"  phi_B data shape: {phi_B_data.shape}")
    
    # Step 4: Calculate what phi_B SHOULD be
    print("\n[STEP 4] Calculating expected phi_B values...")
    expected_phi_B = np.degrees(np.arctan2(br_data, bn_data)) + 180
    print(f"  Expected phi_B shape: {expected_phi_B.shape}")
    
    # Step 5: Verify phi_B matches expected values
    print("\n[STEP 5] Comparing phi_B to expected values...")
    print(f"  br[0]: {br_data[0]:.6f}")
    print(f"  bn[0]: {bn_data[0]:.6f}")
    print(f"  phi_B[0]: {phi_B_data[0]:.6f}")
    print(f"  expected_phi_B[0]: {expected_phi_B[0]:.6f}")
    
    # Check if phi_B equals expected (with tolerance for floating point)
    if np.allclose(phi_B_data, expected_phi_B, rtol=1e-5):
        print("\n✅ TEST PASSED: phi_B has correct values!")
    else:
        print("\n❌ TEST FAILED: phi_B has incorrect values!")
        print(f"  Max difference: {np.max(np.abs(phi_B_data - expected_phi_B))}")
        sys.exit(1)
    
    # Step 6: Verify br is NOT corrupted (doesn't have phi_B's values)
    print("\n[STEP 6] Verifying br is not corrupted...")
    if np.allclose(br_data, phi_B_data):
        print("❌ TEST FAILED: br has been corrupted with phi_B values!")
        sys.exit(1)
    else:
        print("✅ br has its own correct values (not corrupted)")
    
    # Step 7: Verify bn is NOT corrupted
    print("\n[STEP 7] Verifying bn is not corrupted...")
    if np.allclose(bn_data, phi_B_data):
        print("❌ TEST FAILED: bn has been corrupted with phi_B values!")
        sys.exit(1)
    else:
        print("✅ bn has its own correct values (not corrupted)")
    
    # Step 8: Verify plotbot.phi_B always has current data
    print("\n[STEP 8] Verifying plotbot.phi_B always has current data...")
    print(f"  plotbot.phi_B.shape: {plotbot.phi_B.shape}")
    
    # Access .data from global (the ONLY way now)
    try:
        global_data = np.array(plotbot.phi_B.data)
        print(f"  ✅ plotbot.phi_B.data works! Shape: {global_data.shape}")
        if len(global_data) > 0 and np.allclose(global_data, phi_B_data):
            print("  ✅ plotbot.phi_B has correct data!")
        else:
            print("  ❌ plotbot.phi_B has incorrect or empty data!")
            sys.exit(1)
    except Exception as e:
        print(f"  ❌ plotbot.phi_B.data failed: {e}")
        sys.exit(1)
    
    # Test attribute setting on global
    print("\n[STEP 9] Testing attribute setting on plotbot.phi_B...")
    plotbot.phi_B.color = 'purple'
    plotbot.phi_B.y_label = r'$\phi_B$'
    print(f"  ✅ Set color: {plotbot.phi_B.color}")
    print(f"  ✅ Set y_label: {plotbot.phi_B.y_label}")
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED! ✅")
    print("="*70)
    return True

if __name__ == "__main__":
    test_custom_variable_stale_reference()


