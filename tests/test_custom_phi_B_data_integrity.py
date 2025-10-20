"""
Test for phi_B custom variable data integrity bug.

Issue reported: phi_B.data is returning br data instead of the calculated 
arctan2(br, bn) angle values.

This test reproduces the exact workflow from the user's notebook.
"""

import numpy as np
import sys

def test_phi_B_is_not_br_data():
    """
    Test that phi_B custom variable returns angle calculations, not br data.
    
    Reproduces the exact workflow from inconsistent-cells-10-20-25.ipynb
    BUT USES LAMBDA (the correct way for complex expressions)
    """
    print("\n" + "="*80)
    print("TEST: phi_B custom variable should NOT return br data")
    print("="*80)
    
    import plotbot
    
    # Step 1: Create the custom variable USING LAMBDA (CORRECT for complex expressions)
    print("\n[STEP 1] Creating phi_B custom variable with LAMBDA...")
    phi_B = plotbot.custom_variable(
        'phi_B',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
    )
    phi_B.y_label = r'$\phi_B \ (\circ)$'
    phi_B.color = 'purple'
    phi_B.plot_type = 'scatter'
    phi_B.marker_style = 'o'
    phi_B.marker_size = 3
    print("   ✅ Created phi_B")
    
    # Step 2: Call plotbot() with a trange (this loads data AND plots)
    print("\n[STEP 2] Calling plotbot() with trange...")
    trange = ['2021-04-01/00:00:00', '2021-04-01/01:00:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                    plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)
    print("   ✅ plotbot() completed")
    
    # Step 3: Access the data and check if phi_B.data equals br.data (THE BUG)
    print("\n[STEP 3] Checking if phi_B.data == br.data...")
    phi_B_data = plotbot.phi_B.data
    br_data = plotbot.mag_rtn_4sa.br.data
    bn_data = plotbot.mag_rtn_4sa.bn.data
    
    print(f"   phi_B.data shape: {phi_B_data.shape}")
    print(f"   br.data shape: {br_data.shape}")
    print(f"   phi_B first 5 values: {phi_B_data[:5]}")
    print(f"   br first 5 values: {br_data[:5]}")
    
    # THE BUG CHECK: Are they identical?
    if np.array_equal(phi_B_data, br_data):
        print("\n   ❌ BUG CONFIRMED: phi_B.data is IDENTICAL to br.data!")
        print("   This means custom variable is returning source data instead of calculated values.")
        return False
    else:
        print("\n   ✅ GOOD: phi_B.data is different from br.data")
    
    # Step 4: Verify phi_B.data matches the expected calculation
    print("\n[STEP 4] Verifying phi_B.data matches expected calculation...")
    expected_phi_B = np.degrees(np.arctan2(br_data, bn_data)) + 180
    print(f"   Expected first 5 values: {expected_phi_B[:5]}")
    
    if np.allclose(phi_B_data, expected_phi_B, rtol=1e-10):
        print("   ✅ PASS: phi_B.data matches expected calculation!")
        return True
    else:
        print("   ❌ FAIL: phi_B.data does NOT match expected calculation")
        max_diff = np.max(np.abs(phi_B_data - expected_phi_B))
        print(f"   Maximum difference: {max_diff}")
        return False


def test_phi_B_redefinition():
    """
    Test that redefining phi_B (without +180) produces different data.
    
    This tests the second part of the notebook where phi_B is redefined.
    USES LAMBDA (the correct way for complex expressions)
    """
    print("\n" + "="*80)
    print("TEST: phi_B redefinition should produce different data")
    print("="*80)
    
    import plotbot
    
    # First definition: with +180 USING LAMBDA
    print("\n[STEP 1] First phi_B definition (with +180)...")
    phi_B_v1 = plotbot.custom_variable(
        'phi_B_v1',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
    )
    
    trange = ['2021-04-01/00:00:00', '2021-04-01/01:00:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.phi_B_v1, 2)
    
    phi_B_v1_data = plotbot.phi_B_v1.data
    print(f"   phi_B_v1 first 5 values: {phi_B_v1_data[:5]}")
    
    # Second definition: without +180 USING LAMBDA
    print("\n[STEP 2] Second phi_B definition (without +180)...")
    phi_B_v2 = plotbot.custom_variable(
        'phi_B_v2',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
    )
    
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.phi_B_v2, 2)
    
    phi_B_v2_data = plotbot.phi_B_v2.data
    print(f"   phi_B_v2 first 5 values: {phi_B_v2_data[:5]}")
    
    # Check they're different
    print("\n[STEP 3] Checking if definitions produced different data...")
    if np.array_equal(phi_B_v1_data, phi_B_v2_data):
        print("   ❌ FAIL: Both definitions produced identical data!")
        return False
    else:
        print("   ✅ GOOD: Definitions produced different data")
    
    # Check the difference is approximately 180
    difference = phi_B_v1_data - phi_B_v2_data
    mean_diff = np.mean(difference)
    print(f"   Mean difference: {mean_diff:.2f} degrees")
    
    if np.allclose(difference, 180.0, rtol=0.01):
        print("   ✅ PASS: Difference is approximately 180 degrees (as expected)")
        return True
    else:
        print(f"   ❌ FAIL: Expected difference of 180, got {mean_diff:.2f}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🔬" * 40)
    print(" PHI_B CUSTOM VARIABLE DATA INTEGRITY TEST")
    print("🔬" * 40)
    print("\nIssue: phi_B.data returning br.data instead of angle calculations")
    print("Source: inconsistent-cells-10-20-25.ipynb")
    
    results = []
    
    try:
        results.append(("phi_B is not br data", test_phi_B_is_not_br_data()))
        results.append(("phi_B redefinition", test_phi_B_redefinition()))
    except Exception as e:
        print(f"\n❌ TEST SUITE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! phi_B is working correctly.")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED! Bug confirmed in phi_B data.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

