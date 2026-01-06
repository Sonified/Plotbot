#!/usr/bin/env python3
"""
Debug datetime_array syncing with full debugging enabled
"""

import sys
sys.path.insert(0, '.')

from plotbot import *

print("🔍 Debugging DateTime Array Syncing")
print("=" * 50)

# Enable ALL relevant debugging
print_manager.show_debug = True
print_manager.show_data_cubby = True  
print_manager.show_dependency_management = True
print_manager.show_processing = True
print_manager.show_status = True

print("\n🎯 Test 1: 2021-04-29 data (should work)")
print("-" * 30)

trange1 = ['2021-04-29/06:00:00', '2021-04-29/12:00:00']
try:
    # Clear any existing data first
    print("📥 Loading 2021 data...")
    plotbot(trange1, psp_waves_test.wavePower_LH, 1)
    print("✅ 2021 test completed successfully")
except Exception as e:
    print(f"❌ 2021 test failed: {e}")

print("\n" + "="*50)
print("🎯 Test 2: 2023-06-22 data (problematic)")
print("-" * 30)

trange2 = ['2023-06-22/06:00:00', '2023-06-22/12:00:00']  
try:
    print("📥 Loading 2023 data...")
    plotbot(trange2, psp_waves_test.wavePower_LH, 1)
    print("✅ 2023 test completed")
except Exception as e:
    print(f"❌ 2023 test failed: {e}")

print("\n" + "="*50)
print("🧪 COMPARISON: mag_rtn_4sa (proven working class)")
print("-" * 30)

def check_class_state(class_name, variable_names):
    """Check the state of a class and its variables"""
    print(f"\n📊 {class_name.upper()} STATE:")
    class_instance = data_cubby.grab(class_name)
    if class_instance:
        dt_array = class_instance.datetime_array
        print(f"   Class datetime_array: {type(dt_array)} length={len(dt_array) if dt_array is not None else 'None'}")
        if dt_array is not None and len(dt_array) > 0:
            print(f"   Time range: {dt_array[0]} to {dt_array[-1]}")
        
        for var_name in variable_names:
            if hasattr(class_instance, var_name):
                var_manager = getattr(class_instance, var_name)
                if hasattr(var_manager, 'plot_config'):
                    var_dt_array = var_manager.plot_config.datetime_array
                    print(f"   {var_name}.plot_config.datetime_array: {type(var_dt_array)} length={len(var_dt_array) if var_dt_array is not None else 'None'}")

print("📥 Testing mag_rtn_4sa - First load...")
try:
    plotbot(['2021-04-29/06:00:00', '2021-04-29/12:00:00'], mag_rtn_4sa.br, 1)
    print("✅ mag_rtn_4sa first load completed")
    check_class_state("mag_rtn_4sa", ["br", "bt", "bn"])
except Exception as e:
    print(f"❌ mag_rtn_4sa first load failed: {e}")

print("\n📥 Testing mag_rtn_4sa - Second load...")
try:
    plotbot(['2021-04-30/06:00:00', '2021-04-30/12:00:00'], mag_rtn_4sa.br, 1)
    print("✅ mag_rtn_4sa second load completed")
    check_class_state("mag_rtn_4sa", ["br", "bt", "bn"])
except Exception as e:
    print(f"❌ mag_rtn_4sa second load failed: {e}")

print("\n" + "="*50)
print("🎨 STYLING PERSISTENCE TEST:")
print("-" * 30)

def check_styling(label):
    """Check current styling"""
    print(f"\n🎨 {label}")
    try:
        lh_color = psp_waves_test.wavePower_LH.color
        rh_color = psp_waves_test.wavePower_RH.color
        lh_legend = psp_waves_test.wavePower_LH.legend_label
        rh_legend = psp_waves_test.wavePower_RH.legend_label
        print(f"   LH: color={lh_color}, legend='{lh_legend[:30]}...'")
        print(f"   RH: color={rh_color}, legend='{rh_legend[:30]}...'")
    except Exception as e:
        print(f"   ❌ Error checking styling: {e}")

check_styling("After 2023 data load")

print("\n🎨 Setting custom styling...")
psp_waves_test.wavePower_LH.color = "blue"
psp_waves_test.wavePower_RH.color = "red"
psp_waves_test.wavePower_LH.legend_label = "LH Custom Legend"
psp_waves_test.wavePower_RH.legend_label = "RH Custom Legend"
check_styling("After setting custom styling")

print("\n📥 Testing if styling survives another data load...")
plotbot(['2021-04-29/08:00:00', '2021-04-29/10:00:00'], psp_waves_test.wavePower_LH, 1)
check_styling("After additional data load - STYLING SHOULD BE PRESERVED!")

print("\n" + "="*50)
print("🔍 FINAL COMPARISON:")
print("-" * 30)
print("CDF Class (psp_waves_test):")
check_class_state("psp_waves_test", ["wavePower_LH", "wavePower_RH"])
print("\nProven Class (mag_rtn_4sa):")
check_class_state("mag_rtn_4sa", ["br", "bt", "bn"])
