#!/usr/bin/env python3
"""
Test the simplified custom variable architecture - REAL USER WORKFLOW.
"""

import sys
import numpy as np
import plotbot as pb
from plotbot import plotbot, mag_rtn_4sa, custom_variable, print_manager

# Enable debug output
print_manager.show_status = True
print_manager.show_custom_debug = True

def test_basic_workflow():
    """Test exactly how a user would use custom variables"""
    print("\n" + "="*80)
    print("TEST: Real User Workflow")
    print("="*80)
    
    # User creates a custom variable
    custom_variable('abs_bn', lambda: np.abs(pb.mag_rtn_4sa.bn))
    
    # User plots it - first time range
    trange1 = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    print(f"\n📊 First plot: {trange1}")
    fig1 = plotbot(trange1, mag_rtn_4sa.bn, 1, pb.abs_bn, 2)
    
    # Check data exists
    bn_len1 = len(mag_rtn_4sa.bn.data)
    abs_bn_len1 = len(pb.abs_bn.data)
    print(f"✅ bn: {bn_len1} points (ID:{id(mag_rtn_4sa.bn)})")
    print(f"✅ abs_bn: {abs_bn_len1} points (ID:{id(pb.abs_bn)})")
    print(f"✅ Match: {bn_len1 == abs_bn_len1}")
    
    # User plots again - DIFFERENT time range
    trange2 = ['2020-01-29/19:00:00', '2020-01-29/19:20:00']
    print(f"\n📊 Second plot: {trange2}")
    fig2 = plotbot(trange2, mag_rtn_4sa.bn, 1, pb.abs_bn, 2)
    
    # Check data is correct for NEW time range (not accumulated)
    bn_len2 = len(mag_rtn_4sa.bn.data)
    abs_bn_len2 = len(pb.abs_bn.data)
    print(f"✅ bn: {bn_len2} points (ID:{id(mag_rtn_4sa.bn)})")
    print(f"✅ abs_bn: {abs_bn_len2} points (ID:{id(pb.abs_bn)})")
    print(f"✅ Match: {bn_len2 == abs_bn_len2}")
    
    # Check that the second call REPLACED data (not accumulated)
    print(f"\n🔍 Data accumulation check:")
    print(f"   If accumulated: {abs_bn_len1 + bn_len2} points")
    print(f"   Actually got: {abs_bn_len2} points")
    
    if abs_bn_len2 == abs_bn_len1 + bn_len2:
        print("❌ FAIL: Data accumulated!")
        return False
    elif abs_bn_len2 == bn_len2:
        print("✅ PASS: Data replaced correctly!")
        return True
    else:
        print(f"⚠️  Unexpected length: {abs_bn_len2}")
        return False

if __name__ == '__main__':
    try:
        print("\n🚀 Testing Simplified Custom Variable Architecture")
        print("This test mimics EXACTLY what a real user would do.\n")
        
        success = test_basic_workflow()
        
        if success:
            print("\n" + "="*80)
            print("🎉 SUCCESS! Simplification works!")
            print("="*80)
            sys.exit(0)
        else:
            print("\n" + "="*80)
            print("❌ TEST FAILED")
            print("="*80)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
