#!/usr/bin/env python3
"""
Debug script to compare how mag_rtn and psp_waves_test classes 
handle has_existing_data evaluation differently.
"""

from plotbot import *

# Enable plot display!
ploptions.display_figure = True

# Enable status output only (cleaner than debug)
print_manager.show_status = True
print_manager.show_debug = False  
print_manager.show_data_cubby = False
print_manager.show_style_preservation = True  # Enable style preservation debugging

print("🧪 DEBUG PATH COMPARISON TEST")
print("=" * 5)

# Test with mag_rtn class
print("\n📊 TEST 1: mag_rtn class behavior")
print("-" * 5)

try:
    # First load for mag_rtn
    print("🔄 mag_rtn - First load...")
    mag_rtn_vars = plotbot(['2021-04-29/06:00:00', '2021-04-29/08:00:00'], 
                          mag_rtn.br, 1)
    print("✅ mag_rtn first load completed")
    
    # Second load for mag_rtn  
    print("\n🔄 mag_rtn - Second load...")
    mag_rtn_vars2 = plotbot(['2021-04-29/10:00:00', '2021-04-29/12:00:00'], 
                           mag_rtn.br, 1)
    print("✅ mag_rtn second load completed")
    
except Exception as e:
    print(f"❌ mag_rtn test failed: {e}")
    import traceback
    traceback.print_exc()

# Additional mag_rtn tests to confirm anomaly
print("\n📊 TEST 2: mag_rtn class (additional loads to confirm anomaly)")
print("-" * 30)

try:
    # Third load for mag_rtn
    print("🔄 mag_rtn - Third load...")
    mag_rtn_vars3 = plotbot(['2021-04-29/14:00:00', '2021-04-29/16:00:00'], 
                           mag_rtn.br, 1)
    print("✅ mag_rtn third load completed")
    
except Exception as e:
    print(f"❌ mag_rtn additional test failed: {e}")
    import traceback
    traceback.print_exc()

# Test with mag_rtn_4sa class  
print("\n📊 TEST 3: mag_rtn_4sa class behavior")
print("-" * 30)

try:
    # First load for mag_rtn_4sa
    print("🔄 mag_rtn_4sa - First load...")
    mag_rtn_4sa_vars = plotbot(['2021-04-29/06:00:00', '2021-04-29/08:00:00'], 
                              mag_rtn_4sa.br, 1)
    print("✅ mag_rtn_4sa first load completed")
    
    # Second load for mag_rtn_4sa  
    print("\n🔄 mag_rtn_4sa - Second load...")
    mag_rtn_4sa_vars2 = plotbot(['2021-04-29/10:00:00', '2021-04-29/12:00:00'], 
                               mag_rtn_4sa.br, 1)
    print("✅ mag_rtn_4sa second load completed")
    
except Exception as e:
    print(f"❌ mag_rtn_4sa test failed: {e}")
    import traceback
    traceback.print_exc()

# Test with mag_sc_4sa class  
print("\n📊 TEST 4: mag_sc_4sa class behavior")
print("-" * 30)

try:
    # First load for mag_sc_4sa
    print("🔄 mag_sc_4sa - First load...")
    mag_sc_4sa_vars = plotbot(['2021-04-29/06:00:00', '2021-04-29/08:00:00'], 
                             mag_sc_4sa.bx, 1)
    print("✅ mag_sc_4sa first load completed")
    
    # Second load for mag_sc_4sa  
    print("\n🔄 mag_sc_4sa - Second load...")
    mag_sc_4sa_vars2 = plotbot(['2021-04-29/10:00:00', '2021-04-29/12:00:00'], 
                              mag_sc_4sa.bx, 1)
    print("✅ mag_sc_4sa second load completed")
    
except Exception as e:
    print(f"❌ mag_sc_4sa test failed: {e}")
    import traceback
    traceback.print_exc()

# Test with proton.anisotropy class
print("\n📊 TEST 5: proton.anisotropy class behavior")
print("-" * 30)

try:
    # Test all time regions with proton.anisotropy
    time_regions = [
        ['2021-04-29/06:00:00', '2021-04-29/08:00:00'],
        ['2021-04-29/10:00:00', '2021-04-29/12:00:00']
    ]
    
    for i, trange in enumerate(time_regions, 1):
        print(f"\n🔄 proton.anisotropy - Load {i} ({trange[0][:10]})...")
        proton_vars = plotbot(trange, proton.anisotropy, 1)
        print(f"✅ proton.anisotropy load {i} completed")
    
except Exception as e:
    print(f"❌ proton.anisotropy test failed: {e}")
    import traceback
    traceback.print_exc()

# Test with psp_waves_test class
print("\n📊 TEST 6: psp_waves_test class behavior")
print("-" * 30)

try:
    # First load for psp_waves_test (both variables)
    print("🔄 psp_waves_test - First load...")
    waves_vars = plotbot(['2021-04-29/06:00:00', '2021-04-29/08:00:00'], 
                        psp_waves_test.wavePower_LH, 1,
                        psp_waves_test.wavePower_RH, 2)
    print("✅ psp_waves_test first load completed")
    
    # Second load for psp_waves_test (both variables)
    print("\n🔄 psp_waves_test - Second load...")
    waves_vars2 = plotbot(['2021-04-29/10:00:00', '2021-04-29/12:00:00'], 
                         psp_waves_test.wavePower_LH, 1,
                         psp_waves_test.wavePower_RH, 2)
    print("✅ psp_waves_test second load completed")
    
except Exception as e:
    print(f"❌ psp_waves_test test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Debug comparison test completed")