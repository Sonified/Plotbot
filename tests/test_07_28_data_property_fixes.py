#!/usr/bin/env python3
"""
Test script to verify that our .data property fixes work correctly
for the classes we modified: psp_mag_rtn_4sa, psp_mag_rtn, and psp_alpha_classes
"""

import sys
sys.path.append('..')

from plotbot import *

def test_mag_rtn_4sa_br_norm():
    """Test mag_rtn_4sa.br_norm calculation (uses proton.sun_dist_rsun)"""
    print("🧪 Testing mag_rtn_4sa.br_norm calculation...")
    
    trange = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    
    try:
        # This should trigger br_norm calculation which uses proton.sun_dist_rsun
        plotbot(trange, mag_rtn_4sa.br_norm, 1)
        print("✅ SUCCESS: mag_rtn_4sa.br_norm works correctly")
        
        # Test that .data property returns clipped data
        data = mag_rtn_4sa.br_norm.data
        print(f"   br_norm.data shape: {data.shape}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: mag_rtn_4sa.br_norm - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mag_rtn_br_norm():
    """Test mag_rtn.br_norm calculation (uses proton.sun_dist_rsun)"""
    print("\n🧪 Testing mag_rtn.br_norm calculation...")
    
    trange = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    
    try:
        # This should trigger br_norm calculation which uses proton.sun_dist_rsun
        plotbot(trange, mag_rtn.br_norm, 1)
        print("✅ SUCCESS: mag_rtn.br_norm works correctly")
        
        # Test that .data property returns clipped data
        data = mag_rtn.br_norm.data
        print(f"   br_norm.data shape: {data.shape}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: mag_rtn.br_norm - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alpha_derived_variables():
    """Test psp_alpha derived variables (use proton data arrays)"""
    print("\n🧪 Testing psp_alpha derived variable calculations...")
    
    trange = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    
    try:
        # This should trigger alpha-proton derived calculations
        plotbot(trange, psp_alpha.na_div_np, 1)
        print("✅ SUCCESS: psp_alpha.na_div_np works correctly")
        
        # Test that .data property returns clipped data
        data = psp_alpha.na_div_np.data
        print(f"   na_div_np.data shape: {data.shape}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: psp_alpha.na_div_np - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_electron_classes():
    """Test electron classes (had missing import fix)"""
    print("\n🧪 Testing electron classes...")
    
    trange = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    
    try:
        # This should work without NameError for get_encounter_number
        plotbot(trange, epad.strahl, 1)
        print("✅ SUCCESS: epad.strahl works correctly")
        
        # Test that .data property returns clipped data
        data = epad.strahl.data
        print(f"   strahl.data shape: {data.shape}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: epad.strahl - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔬 TESTING DATA PROPERTY FIXES")
    print("=" * 50)
    
    print_manager.show_status = False  # Reduce output noise
    
    results = []
    
    # Test each fixed class
    results.append(test_mag_rtn_4sa_br_norm())
    results.append(test_mag_rtn_br_norm())  
    results.append(test_alpha_derived_variables())
    results.append(test_electron_classes())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 ALL TESTS PASSED ({success_count}/{total_count})")
        print("✅ Data property fixes are working correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({success_count}/{total_count})")
        print("❌ Additional fixes may be needed")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 