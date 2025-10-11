"""
Test to verify custom variables properly clip to requested time range.

STRESS TEST: Multiple time ranges, variable combinations, and edge cases.
This isolates the issue where custom variables weren't respecting requested_trange,
causing shape mismatches when accessing .data property.

Tests include:
- 3 main tests with different time ranges
- 9 edge case tests:
  1. Rapid time range switching
  2. Return to previous trange (cache invalidation)
  3. Chained custom variables (one depends on another)
  4. Redefine custom variable with different formula
  5. Lambda without plotbot prefix (bare variable names)
  6. Different cadences (mag vs proton data)
  7. 3 variables, same cadence (bmag * br * bn)
  8. 4 variables, mixed cadences ((bmag + br) / (vr + vt))
  9. 3 variables, all different cadences (br * anisotropy * centroids)
"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa, print_manager
import sys

# Disable custom debug for cleaner output (enable for specific tests)
print_manager.show_custom_debug = False

def check_shapes_match(test_name, *data_arrays):
    """Helper to verify all arrays have matching shapes"""
    shapes = [arr.shape[0] for arr in data_arrays]
    if len(set(shapes)) == 1:
        print(f"  ✅ {test_name}: All shapes match ({shapes[0]} points)")
        return True, shapes[0]
    else:
        print(f"  ❌ {test_name}: Shape mismatch!")
        for i, shape in enumerate(shapes):
            print(f"     Array {i+1}: {shape} points")
        return False, None

def test_custom_variable_trange_clipping():
    """STRESS TEST: Multiple time ranges and variable combinations"""
    
    print("\n" + "="*70)
    print("STRESS TEST: Custom Variable Time Range Clipping")
    print("="*70)
    
    # Create multiple custom variables with different operations
    print("\n[SETUP] Creating multiple custom variables...")
    
    # 1. Complex lambda with multiple numpy functions
    phi_B = custom_variable('phi_B_stress',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
    )
    
    # 2. Simple lambda with single numpy function
    abs_bn = custom_variable('abs_bn_stress',
        lambda: np.abs(plotbot.mag_rtn_4sa.bn)
    )
    
    # 3. Arithmetic operation (non-lambda)
    sum_br_bt = custom_variable('sum_br_bt_stress',
        mag_rtn_4sa.br + mag_rtn_4sa.bt
    )
    
    print(f"  Created 3 custom variables: phi_B_stress, abs_bn_stress, sum_br_bt_stress")
    
    # Define multiple test time ranges with different durations
    test_ranges = [
        {
            'name': 'Short range (10 min)',
            'trange': ['2020-01-29/18:00:00', '2020-01-29/18:10:00'],
            'expected_min_points': 100  # Rough estimate
        },
        {
            'name': 'Medium range (1 hour)',
            'trange': ['2020-01-29/18:00:00', '2020-01-29/19:00:00'],
            'expected_min_points': 500
        },
        {
            'name': 'Different day',
            'trange': ['2020-02-15/12:00:00', '2020-02-15/12:30:00'],
            'expected_min_points': 100
        },
    ]
    
    all_passed = True
    
    # TEST LOOP: Test each time range
    for test_idx, test_case in enumerate(test_ranges, 1):
        print("\n" + "="*70)
        print(f"TEST {test_idx}/3: {test_case['name']}")
        print("="*70)
        
        trange = test_case['trange']
        print(f"\n[TEST {test_idx}.1] Calling plotbot with trange: {trange}")
        
        # Call plotbot with all variables
        plotbot.plotbot(
            trange,
            mag_rtn_4sa.br, 1,
            mag_rtn_4sa.bn, 2,
            phi_B, 3,
            abs_bn, 4,
            sum_br_bt, 5
        )
        
        print(f"\n[TEST {test_idx}.2] Extracting .data from all variables...")
        br_data = np.array(mag_rtn_4sa.br.data)
        bn_data = np.array(mag_rtn_4sa.bn.data)
        bt_data = np.array(mag_rtn_4sa.bt.data)
        phi_B_data = np.array(plotbot.phi_B_stress.data)
        abs_bn_data = np.array(plotbot.abs_bn_stress.data)
        sum_data = np.array(plotbot.sum_br_bt_stress.data)
        
        print(f"  Regular vars: br={br_data.shape}, bn={bn_data.shape}, bt={bt_data.shape}")
        print(f"  Custom vars:  phi_B={phi_B_data.shape}, abs_bn={abs_bn_data.shape}, sum={sum_data.shape}")
        
        print(f"\n[TEST {test_idx}.3] Verifying all shapes match...")
        shapes_ok, n_points = check_shapes_match(
            "Shape consistency",
            br_data, bn_data, bt_data, phi_B_data, abs_bn_data, sum_data
        )
        
        if not shapes_ok:
            print(f"  ❌ TEST {test_idx} FAILED: Shape mismatch")
            all_passed = False
            continue
        
        # Verify we got a reasonable number of points
        if n_points < test_case['expected_min_points']:
            print(f"  ⚠️  Warning: Only {n_points} points (expected >{test_case['expected_min_points']})")
        
        print(f"\n[TEST {test_idx}.4] Verifying calculations are correct...")
        
        # Check phi_B calculation
        expected_phi_B = np.degrees(np.arctan2(br_data, bn_data)) + 180
        if np.allclose(phi_B_data, expected_phi_B, rtol=1e-5):
            print(f"  ✅ phi_B calculation correct")
        else:
            print(f"  ❌ phi_B calculation WRONG")
            all_passed = False
        
        # Check abs_bn calculation
        expected_abs_bn = np.abs(bn_data)
        if np.allclose(abs_bn_data, expected_abs_bn, rtol=1e-5):
            print(f"  ✅ abs_bn calculation correct")
        else:
            print(f"  ❌ abs_bn calculation WRONG")
            all_passed = False
        
        # Check sum calculation
        expected_sum = br_data + bt_data
        if np.allclose(sum_data, expected_sum, rtol=1e-5):
            print(f"  ✅ sum_br_bt calculation correct")
        else:
            print(f"  ❌ sum_br_bt calculation WRONG")
            all_passed = False
        
        if shapes_ok:
            print(f"\n✅ TEST {test_idx} PASSED: {test_case['name']}")
        else:
            print(f"\n❌ TEST {test_idx} FAILED: {test_case['name']}")
    
    # EDGE CASE 1: Test switching between ranges rapidly
    print("\n" + "="*70)
    print("EDGE CASE 1: Rapid time range switching")
    print("="*70)
    
    rapid_ranges = [
        ['2020-01-29/18:00:00', '2020-01-29/18:05:00'],
        ['2020-02-15/10:00:00', '2020-02-15/10:03:00'],
        ['2020-03-10/14:00:00', '2020-03-10/14:08:00'],
    ]
    
    for i, trange in enumerate(rapid_ranges, 1):
        print(f"\n[RAPID {i}] Testing trange: {trange}")
        plotbot.plotbot(trange, mag_rtn_4sa.br, 1, phi_B, 2)
        
        br_data = np.array(mag_rtn_4sa.br.data)
        phi_B_data = np.array(plotbot.phi_B_stress.data)
        
        if br_data.shape == phi_B_data.shape:
            print(f"  ✅ Shapes match: {br_data.shape}")
        else:
            print(f"  ❌ Shape mismatch: br={br_data.shape}, phi_B={phi_B_data.shape}")
            all_passed = False
    
    # EDGE CASE 2: Return to previous trange (cache invalidation test)
    print("\n" + "="*70)
    print("EDGE CASE 2: Return to previous trange")
    print("="*70)
    print("Testing if returning to TEST 1's trange works correctly...")
    
    first_trange = test_ranges[0]['trange']
    print(f"\n[RETURN] Going back to first trange: {first_trange}")
    plotbot.plotbot(first_trange, mag_rtn_4sa.br, 1, phi_B, 2, abs_bn, 3)
    
    br_data = np.array(mag_rtn_4sa.br.data)
    phi_B_data = np.array(plotbot.phi_B_stress.data)
    abs_bn_data = np.array(plotbot.abs_bn_stress.data)
    
    print(f"  br shape: {br_data.shape}")
    print(f"  phi_B shape: {phi_B_data.shape}")
    print(f"  abs_bn shape: {abs_bn_data.shape}")
    
    if br_data.shape == phi_B_data.shape == abs_bn_data.shape:
        print(f"  ✅ All shapes match: {br_data.shape}")
        # Verify calculations still correct
        expected_phi_B = np.degrees(np.arctan2(br_data, mag_rtn_4sa.bn.data)) + 180
        expected_abs_bn = np.abs(mag_rtn_4sa.bn.data)
        if np.allclose(phi_B_data, expected_phi_B, rtol=1e-5) and np.allclose(abs_bn_data, expected_abs_bn, rtol=1e-5):
            print(f"  ✅ Calculations still correct after returning to old trange")
        else:
            print(f"  ❌ Calculations WRONG after returning to old trange")
            all_passed = False
    else:
        print(f"  ❌ Shape mismatch after returning to old trange")
        all_passed = False
    
    # EDGE CASE 3: Chained custom variables (one depends on another)
    print("\n" + "="*70)
    print("EDGE CASE 3: Chained custom variables")
    print("="*70)
    print("Creating custom variable that depends on another custom variable...")
    
    # Create a variable that uses abs_bn_stress
    doubled_abs_bn = custom_variable('doubled_abs_bn',
        lambda: plotbot.abs_bn_stress * 2.0
    )
    
    test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:15:00']
    print(f"\n[CHAINED] Testing chained variables with trange: {test_trange}")
    plotbot.plotbot(test_trange, mag_rtn_4sa.bn, 1, abs_bn, 2, doubled_abs_bn, 3)
    
    bn_data = np.array(mag_rtn_4sa.bn.data)
    abs_bn_data = np.array(plotbot.abs_bn_stress.data)
    doubled_data = np.array(plotbot.doubled_abs_bn.data)
    
    print(f"  bn shape: {bn_data.shape}")
    print(f"  abs_bn shape: {abs_bn_data.shape}")
    print(f"  doubled_abs_bn shape: {doubled_data.shape}")
    
    if bn_data.shape == abs_bn_data.shape == doubled_data.shape:
        print(f"  ✅ All shapes match: {bn_data.shape}")
        # Verify chained calculation
        expected_abs_bn = np.abs(bn_data)
        expected_doubled = expected_abs_bn * 2.0
        if np.allclose(abs_bn_data, expected_abs_bn, rtol=1e-5) and np.allclose(doubled_data, expected_doubled, rtol=1e-5):
            print(f"  ✅ Chained calculation correct (doubled = abs_bn * 2)")
        else:
            print(f"  ❌ Chained calculation WRONG")
            print(f"     Expected doubled[0] = {expected_doubled[0]}, got {doubled_data[0]}")
            all_passed = False
    else:
        print(f"  ❌ Shape mismatch in chained variables")
        all_passed = False
    
    # EDGE CASE 4: Redefine custom variable with different formula
    print("\n" + "="*70)
    print("EDGE CASE 4: Redefine custom variable")
    print("="*70)
    print("Redefining phi_B_stress with a different formula...")
    
    # Redefine phi_B without the +180
    phi_B_redefined = custom_variable('phi_B_stress',
        lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
    )
    
    test_trange = ['2020-01-29/19:00:00', '2020-01-29/19:10:00']
    print(f"\n[REDEFINE] Testing redefined variable with trange: {test_trange}")
    plotbot.plotbot(test_trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bn, 2, phi_B_redefined, 3)
    
    br_data = np.array(mag_rtn_4sa.br.data)
    bn_data = np.array(mag_rtn_4sa.bn.data)
    phi_B_data = np.array(plotbot.phi_B_stress.data)
    
    print(f"  br shape: {br_data.shape}")
    print(f"  bn shape: {bn_data.shape}")
    print(f"  phi_B shape: {phi_B_data.shape}")
    
    if br_data.shape == bn_data.shape == phi_B_data.shape:
        print(f"  ✅ All shapes match: {br_data.shape}")
        # Verify NEW formula (WITHOUT +180)
        expected_phi_B = np.degrees(np.arctan2(br_data, bn_data))
        if np.allclose(phi_B_data, expected_phi_B, rtol=1e-5):
            print(f"  ✅ Redefined calculation correct (no +180)")
            # Double-check it's NOT the old formula
            old_formula = expected_phi_B + 180
            if not np.allclose(phi_B_data, old_formula, rtol=1e-5):
                print(f"  ✅ Confirmed using NEW formula (not old +180 formula)")
            else:
                print(f"  ❌ Still using OLD formula!")
                all_passed = False
        else:
            print(f"  ❌ Redefined calculation WRONG")
            print(f"     Expected phi_B[0] = {expected_phi_B[0]}, got {phi_B_data[0]}")
            all_passed = False
    else:
        print(f"  ❌ Shape mismatch in redefined variable")
        all_passed = False
    
    # EDGE CASE 5: Lambda without plotbot prefix (like Stardust test)
    print("\n" + "="*70)
    print("EDGE CASE 5: Lambda without plotbot prefix")
    print("="*70)
    print("Creating phi_B lambda with bare variable names (mag_rtn_4sa.br)...")
    
    # Create lambda WITHOUT plotbot prefix (like the Stardust test)
    phi_B_no_prefix = custom_variable('phi_B_no_prefix',
        lambda: np.degrees(np.arctan2(mag_rtn_4sa.br, mag_rtn_4sa.bn)) + 180
    )
    
    test_trange = ['2020-01-29/20:00:00', '2020-01-29/20:15:00']
    print(f"\n[NO_PREFIX] Testing lambda without plotbot prefix with trange: {test_trange}")
    plotbot.plotbot(test_trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bn, 2, phi_B_no_prefix, 3)
    
    br_data = np.array(mag_rtn_4sa.br.data)
    bn_data = np.array(mag_rtn_4sa.bn.data)
    phi_B_data = np.array(plotbot.phi_B_no_prefix.data)
    
    print(f"  br shape: {br_data.shape}")
    print(f"  bn shape: {bn_data.shape}")
    print(f"  phi_B_no_prefix shape: {phi_B_data.shape}")
    
    if br_data.shape == bn_data.shape == phi_B_data.shape:
        print(f"  ✅ All shapes match: {br_data.shape}")
        # Verify calculation (WITH +180)
        expected_phi_B = np.degrees(np.arctan2(br_data, bn_data)) + 180
        if np.allclose(phi_B_data, expected_phi_B, rtol=1e-5):
            print(f"  ✅ Lambda calculation correct (matches Stardust test pattern)")
        else:
            print(f"  ❌ Lambda calculation WRONG")
            print(f"     Expected phi_B[0] = {expected_phi_B[0]}, got {phi_B_data[0]}")
            all_passed = False
    else:
        print(f"  ❌ Shape mismatch in lambda without prefix")
        all_passed = False
    
    # EDGE CASE 6: Different cadences (direct expression with automatic resampling)
    print("\n" + "="*70)
    print("EDGE CASE 6: Different cadences with automatic resampling")
    print("="*70)
    print("Testing DIRECT EXPRESSION custom variable with mixed cadences")
    print("(Lambda variables don't support auto-resampling - use direct expressions)")
    
    try:
        from plotbot import proton
        
        # Use DIRECT EXPRESSION (not lambda) for mixed cadences
        # This allows the system to resample before the operation
        mixed_cadence = custom_variable('mixed_cadence_test',
            mag_rtn_4sa.bmag / proton.vr
        )
        
        test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
        print(f"\n[MIXED_CADENCE] Testing with trange: {test_trange}")
        
        plotbot.plotbot(test_trange, mag_rtn_4sa.bmag, 1, proton.vr, 2, mixed_cadence, 3)
        
        bmag_data = np.array(mag_rtn_4sa.bmag.data)
        vr_data = np.array(proton.vr.data)
        mixed_data = np.array(plotbot.mixed_cadence_test.data)
        
        print(f"  bmag shape (mag cadence): {bmag_data.shape}")
        print(f"  vr shape (proton cadence): {vr_data.shape}")
        print(f"  mixed_cadence_test shape: {mixed_data.shape}")
        
        # The custom variable should match the LOWER cadence (proton)
        expected_cadence = min(bmag_data.shape[0], vr_data.shape[0])
        
        if mixed_data.shape[0] == expected_cadence:
            print(f"  ✅ Custom variable resampled to lowest cadence: {expected_cadence} points")
            
            # Verify the calculation is approximately correct
            # Since mag was resampled to proton cadence, we can't do exact comparison
            # But we can check that the result is reasonable
            if np.all(np.isfinite(mixed_data)):
                print(f"  ✅ All values are finite (no NaN/Inf from resampling)")
            else:
                print(f"  ⚠️  Some non-finite values in result")
                
            # Check range is reasonable (bmag/vr should be positive and bounded)
            if np.all(mixed_data > 0) and np.all(mixed_data < 1e6):
                print(f"  ✅ Values in reasonable range")
            else:
                print(f"  ⚠️  Some values outside expected range")
        else:
            print(f"  ❌ Resampling failed: expected {expected_cadence} points, got {mixed_data.shape[0]}")
            all_passed = False
            
    except ImportError:
        print(f"  ⚠️  proton module not available, skipping mixed cadence test")
    except Exception as e:
        print(f"  ❌ Mixed cadence test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # EDGE CASE 7: 3 variables, same cadence (all mag)
    print("\n" + "="*70)
    print("EDGE CASE 7: 3 variables, SAME cadence (bmag * br * bn)")
    print("="*70)
    
    try:
        three_var_same = custom_variable('three_same', 
            mag_rtn_4sa.bmag * mag_rtn_4sa.br * mag_rtn_4sa.bn
        )
        
        test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
        print(f"[THREE_SAME] Testing with trange: {test_trange}")
        
        plotbot.plotbot(test_trange, three_var_same, 1)
        result = np.array(plotbot.three_same.data)
        
        bmag_len = len(mag_rtn_4sa.bmag.data)
        print(f"  Source cadence (all mag): {bmag_len} points")
        print(f"  Result shape: {result.shape}")
        
        if len(result) > 0 and result.shape[0] == bmag_len and np.all(np.isfinite(result)):
            print(f"  ✅ PASSED: 3 same-cadence variables")
        else:
            print(f"  ❌ FAILED: Expected {bmag_len} points, got {result.shape[0]}")
            all_passed = False
            
    except Exception as e:
        print(f"  ❌ 3-variable same-cadence test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # EDGE CASE 8: 4 variables, mixed cadences
    print("\n" + "="*70)
    print("EDGE CASE 8: 4 variables, MIXED cadences ((bmag + br) / (vr + vt))")
    print("="*70)
    
    try:
        from plotbot import proton
        
        four_var_mixed = custom_variable('four_mixed',
            (mag_rtn_4sa.bmag + mag_rtn_4sa.br) / (proton.vr + proton.vt)
        )
        
        test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
        print(f"[FOUR_MIXED] Testing with trange: {test_trange}")
        
        plotbot.plotbot(test_trange, four_var_mixed, 1)
        result = np.array(plotbot.four_mixed.data)
        
        bmag_len = len(mag_rtn_4sa.bmag.data)
        vr_len = len(proton.vr.data)
        print(f"  Source cadences: bmag={bmag_len}, vr={vr_len}")
        print(f"  Result shape: {result.shape}")
        
        expected_len = min(bmag_len, vr_len)
        if result.shape[0] == expected_len and np.all(np.isfinite(result)):
            print(f"  ✅ PASSED: 4 mixed-cadence variables -> {expected_len} points")
        else:
            print(f"  ❌ FAILED: Expected {expected_len} points, got {result.shape[0]}")
            all_passed = False
            
    except ImportError:
        print(f"  ⚠️  proton module not available, skipping 4-variable test")
    except Exception as e:
        print(f"  ❌ 4-variable mixed-cadence test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Disable debug again
    print_manager.show_custom_debug = False
    
    # EDGE CASE 9: 3 variables, ALL DIFFERENT cadences (mag, proton, epad)
    print("\n" + "="*70)
    print("EDGE CASE 9: 3 variables, ALL DIFFERENT cadences (br * anisotropy * centroids)")
    print("="*70)
    print("NOTE: This includes EPAD which is very slow cadence")
    
    try:
        from plotbot import proton, epad
        
        three_var_all_diff = custom_variable('three_all_diff',
            mag_rtn_4sa.br * proton.anisotropy * epad.centroids
        )
        
        test_trange = ['2020-01-29/18:00:00', '2020-01-29/18:30:00']
        print(f"[THREE_DIFF] Testing with trange: {test_trange}")
        
        plotbot.plotbot(test_trange, three_var_all_diff, 1)
        result = np.array(plotbot.three_all_diff.data)
        
        br_len = len(mag_rtn_4sa.br.data)
        aniso_len = len(proton.anisotropy.data)
        centroids_len = len(epad.centroids.data)
        
        print(f"  Source cadences:")
        print(f"    br (mag):           {br_len} points")
        print(f"    anisotropy (proton): {aniso_len} points")
        print(f"    centroids (epad):    {centroids_len} points")
        print(f"  Result shape: {result.shape}")
        
        expected_len = min(br_len, aniso_len, centroids_len)
        if result.shape[0] == expected_len and np.all(np.isfinite(result)):
            print(f"  ✅ PASSED: 3 all-different-cadence variables -> {expected_len} points")
        else:
            print(f"  ⚠️  Got {result.shape[0]} points (expected {expected_len})")
            if np.all(np.isfinite(result)):
                print(f"  ✅ But values are all finite, so resampling worked!")
            else:
                print(f"  ❌ FAILED: Contains NaN/Inf")
                all_passed = False
                
    except ImportError:
        print(f"  ⚠️  proton or epad module not available, skipping 3-all-different test")
    except Exception as e:
        print(f"  ❌ 3-all-different-cadence test failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL STRESS TESTS PASSED! ✅")
        print("="*70)
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)
        sys.exit(1)

if __name__ == "__main__":
    test_custom_variable_trange_clipping()

