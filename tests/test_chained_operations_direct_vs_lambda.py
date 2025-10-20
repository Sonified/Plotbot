"""
Test to verify whether chained operations work without lambda.

Tests if direct expressions like (br * bt) + density correctly update
for different time ranges.
"""

import numpy as np
import sys

def test_chained_operations_without_lambda():
    """Test if chained operations work WITHOUT lambda across multiple tranges"""
    print("\n" + "="*80)
    print("TEST: Chained operations WITHOUT lambda")
    print("="*80)
    
    import plotbot
    
    # Create chained operation WITHOUT lambda
    print("\n[STEP 1] Creating chained operation WITHOUT lambda...")
    print("   Expression: (br * bt) + density")
    
    chained_no_lambda = plotbot.custom_variable(
        'chained_no_lambda',
        (plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt) + plotbot.proton.density
    )
    print("   ✅ Created")
    
    # First trange
    print("\n[STEP 2] First trange...")
    trange1 = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']
    plotbot.plotbot(trange1, plotbot.mag_rtn_4sa.br, 1, plotbot.chained_no_lambda, 2)
    
    data1 = plotbot.chained_no_lambda.data
    br1 = plotbot.mag_rtn_4sa.br.data
    bt1 = plotbot.mag_rtn_4sa.bt.data
    density1 = plotbot.proton.density.data
    
    print(f"   chained result shape: {data1.shape}")
    print(f"   br shape: {br1.shape}")
    print(f"   bt shape: {bt1.shape}")
    print(f"   density shape: {density1.shape}")
    print(f"   First 3 values: {data1[:3]}")
    
    # Check if shapes match
    if br1.shape == bt1.shape == density1.shape == data1.shape:
        print("   ✅ All shapes match!")
        # Try manual calculation
        expected1 = (br1 * bt1) + density1
        print(f"   Expected first 3: {expected1[:3]}")
        matches1 = np.allclose(data1, expected1, rtol=1e-5)
        print(f"   Matches expected? {matches1}")
    else:
        print("   ❌ SHAPE MISMATCH! Direct expression has wrong data sizes!")
        print("      This means it's mixing accumulated (wrong size) with clipped (right size) data")
        matches1 = False
    
    # Second trange (DIFFERENT)
    print("\n[STEP 3] Second trange (DIFFERENT)...")
    trange2 = ['2023-09-28/08:00:00', '2023-09-28/09:00:00']
    plotbot.plotbot(trange2, plotbot.mag_rtn_4sa.br, 1, plotbot.chained_no_lambda, 2)
    
    data2 = plotbot.chained_no_lambda.data
    br2 = plotbot.mag_rtn_4sa.br.data
    bt2 = plotbot.mag_rtn_4sa.bt.data
    density2 = plotbot.proton.density.data
    
    print(f"   chained result shape: {data2.shape}")
    print(f"   br shape: {br2.shape}")
    print(f"   bt shape: {bt2.shape}")
    print(f"   density shape: {density2.shape}")
    
    # Check if shapes match
    if br2.shape == bt2.shape == density2.shape == data2.shape:
        print("   ✅ All shapes match!")
        expected2 = (br2 * bt2) + density2
        matches2 = np.allclose(data2, expected2, rtol=1e-5)
        print(f"   Matches expected? {matches2}")
    else:
        print("   ❌ SHAPE MISMATCH! Still broken on second trange")
        matches2 = False
    
    if matches1 and matches2:
        print("\n   ✅ PASS: Direct expression works for chained operations!")
        return True
    else:
        print("\n   ❌ FAIL: Direct expression doesn't work correctly")
        return False


def test_chained_operations_with_lambda():
    """Test if chained operations work WITH lambda across multiple tranges"""
    print("\n" + "="*80)
    print("TEST: Chained operations WITH lambda")
    print("="*80)
    
    import plotbot
    
    # Create chained operation WITH lambda
    print("\n[STEP 1] Creating chained operation WITH lambda...")
    print("   Expression: lambda: (br * bt) + density")
    
    chained_lambda = plotbot.custom_variable(
        'chained_lambda',
        lambda: (plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt) + plotbot.proton.density
    )
    print("   ✅ Created")
    
    # First trange
    print("\n[STEP 2] First trange...")
    trange1 = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']
    plotbot.plotbot(trange1, plotbot.mag_rtn_4sa.br, 1, plotbot.chained_lambda, 2)
    
    data1 = plotbot.chained_lambda.data
    br1 = plotbot.mag_rtn_4sa.br.data
    bt1 = plotbot.mag_rtn_4sa.bt.data
    density1 = plotbot.proton.density.data
    
    print(f"   Data shape: {data1.shape}")
    print(f"   First 3 values: {data1[:3]}")
    
    # Manual calculation
    expected1 = (br1 * bt1) + density1
    print(f"   Expected first 3: {expected1[:3]}")
    
    matches1 = np.allclose(data1, expected1, rtol=1e-5)
    print(f"   Matches expected? {matches1}")
    
    # Second trange (DIFFERENT)
    print("\n[STEP 3] Second trange (DIFFERENT)...")
    trange2 = ['2023-09-28/08:00:00', '2023-09-28/09:00:00']
    plotbot.plotbot(trange2, plotbot.mag_rtn_4sa.br, 1, plotbot.chained_lambda, 2)
    
    data2 = plotbot.chained_lambda.data
    br2 = plotbot.mag_rtn_4sa.br.data
    bt2 = plotbot.mag_rtn_4sa.bt.data
    density2 = plotbot.proton.density.data
    
    print(f"   Data shape: {data2.shape}")
    print(f"   First 3 values: {data2[:3]}")
    
    # Manual calculation
    expected2 = (br2 * bt2) + density2
    print(f"   Expected first 3: {expected2[:3]}")
    
    matches2 = np.allclose(data2, expected2, rtol=1e-5)
    print(f"   Matches expected? {matches2}")
    
    if matches1 and matches2:
        print("\n   ✅ PASS: Lambda works correctly!")
        return True
    else:
        print("\n   ❌ FAIL: Lambda doesn't work")
        return False


def main():
    print("\n" + "🔬" * 40)
    print(" CHAINED OPERATIONS: DIRECT vs LAMBDA TEST")
    print("🔬" * 40)
    
    results = []
    
    try:
        results.append(("Without lambda", test_chained_operations_without_lambda()))
        results.append(("With lambda", test_chained_operations_with_lambda()))
    except Exception as e:
        print(f"\n❌ TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} passed")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())

