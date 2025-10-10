"""
Test to verify custom variables properly clip to requested time range.

STRESS TEST: Multiple time ranges, variable combinations, and edge cases.
This isolates the issue where custom variables weren't respecting requested_trange,
causing shape mismatches when accessing .data property.
"""

import numpy as np
import plotbot
from plotbot import custom_variable, mag_rtn_4sa
import sys

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
    
    # EDGE CASE: Test switching between ranges rapidly
    print("\n" + "="*70)
    print("EDGE CASE TEST: Rapid time range switching")
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

