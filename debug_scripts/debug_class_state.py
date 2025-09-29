#!/usr/bin/env python3
"""
Debug class state management between different time ranges
"""

import sys
sys.path.insert(0, '.')

from plotbot import *
import numpy as np

print("🔍 Debugging Class State Management")
print("=" * 50)

# Enable debug output
print_manager.show_debug = True

def check_class_state(label, trange=None):
    """Check the current state of the class"""
    print(f"\n📊 {label}")
    print("-" * 30)
    
    if trange:
        print(f"📅 Time range: {trange[0]} to {trange[1]}")
    
    try:
        class_instance = data_cubby.grab("psp_waves_test")
        if class_instance:
            # Check datetime_array
            dt_array = getattr(class_instance, 'datetime_array', None)
            print(f"   datetime_array: {type(dt_array)}")
            if dt_array is not None and hasattr(dt_array, '__len__'):
                print(f"   datetime_array length: {len(dt_array)}")
                if len(dt_array) > 0:
                    print(f"   datetime range: {dt_array[0]} to {dt_array[-1]}")
            
            # Check raw_data
            raw_data = getattr(class_instance, 'raw_data', {})
            print(f"   raw_data keys: {list(raw_data.keys())}")
            for key, value in raw_data.items():
                if value is not None:
                    print(f"   {key}: {type(value)} shape={getattr(value, 'shape', 'N/A')}")
                else:
                    print(f"   {key}: None")
            
            # Check variables
            var_lh = class_instance.get_subclass('wavePower_LH')
            var_rh = class_instance.get_subclass('wavePower_RH')
            
            if var_lh:
                print(f"   wavePower_LH var: {type(var_lh)}")
                print(f"   wavePower_LH data: {type(getattr(var_lh, 'data', None))}")
                print(f"   wavePower_LH datetime_array: {type(getattr(var_lh, 'datetime_array', None))}")
                
        else:
            print("   ❌ Class instance not found")
            
    except Exception as e:
        print(f"   ❌ Error checking state: {e}")

# Check initial state
check_class_state("Initial State")

# Test sequence: 2021 -> 2023 -> check states
test_ranges = [
    ['2021-04-29/06:00:00', '2021-04-29/12:00:00'],
    ['2023-06-22/06:00:00', '2023-06-22/12:00:00']
]

for i, trange in enumerate(test_ranges, 1):
    print(f"\n🎯 Loading data for Test {i}: {trange[0][:10]}")
    
    try:
        # Force data loading
        get_data(trange, psp_waves_test.wavePower_LH)
        
        # Check state after loading
        check_class_state(f"After Loading Test {i} Data", trange)
        
        # Try to access the variable and see if it has the right data
        var = psp_waves_test.get_subclass('wavePower_LH')
        if var:
            print(f"   Variable access: {type(var)}")
            # Check if the variable has the right datetime range
            var_dt = getattr(var, 'datetime_array', None)
            if var_dt is not None and hasattr(var_dt, '__len__') and len(var_dt) > 0:
                print(f"   Variable datetime range: {var_dt[0]} to {var_dt[-1]}")
            else:
                print(f"   Variable datetime_array: {type(var_dt)}")
                
    except Exception as e:
        print(f"❌ Error in test {i}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n🎯 Testing actual plotting...")

# Now test plotting to see where the issue occurs
for i, trange in enumerate(test_ranges, 1):
    print(f"\n📈 Plot Test {i}: {trange[0][:10]}")
    try:
        # Set labels
        psp_waves_test.wavePower_LH.legend_label = f"LH Power {trange[0][:10]}"
        psp_waves_test.wavePower_RH.legend_label = f"RH Power {trange[0][:10]}"
        
        # Try plotting
        plotbot(trange, psp_waves_test.wavePower_LH, 1, psp_waves_test.wavePower_RH, 2)
        print(f"✅ Plot {i} successful")
        
    except Exception as e:
        print(f"❌ Plot {i} failed: {e}")
        import traceback
        traceback.print_exc()
