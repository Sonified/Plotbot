#!/usr/bin/env python3
"""
Debug why 2023 data isn't loading properly
"""

import sys
sys.path.insert(0, '.')

from plotbot import *

print("🔍 Debugging 2023 Data Loading")
print("=" * 40)

# Enable debug output
print_manager.show_debug = True

# Test 2023 time range specifically
trange = ['2023-06-22/06:00:00', '2023-06-22/12:00:00']
print(f"📅 Testing time range: {trange[0]} to {trange[1]}")

# Check what files the pattern finds
import glob
from pathlib import Path

cdf_dir = Path("data/cdf_files/PSP_Waves")
pattern = "PSP_wavePower_*_v*.cdf"
pattern_path = str(cdf_dir / pattern)
matching_files = glob.glob(pattern_path)

print(f"\n🔍 Pattern search results:")
print(f"   Pattern: {pattern}")
print(f"   Search path: {pattern_path}")
print(f"   Files found: {len(matching_files)}")
for f in matching_files:
    print(f"     📄 {Path(f).name}")

# Check class metadata
try:
    class_instance = data_cubby.grab("psp_waves_test")
    if class_instance:
        print(f"\n📋 Class metadata:")
        print(f"   Original file: {getattr(class_instance, '_original_cdf_file_path', 'Not found')}")
        print(f"   Pattern: {getattr(class_instance, '_cdf_file_pattern', 'Not found')}")
except Exception as e:
    print(f"❌ Error getting class: {e}")

# Try to trigger data loading with debug
print(f"\n🚀 Attempting data load for 2023...")
try:
    var = psp_waves_test.get_subclass('wavePower_LH')
    if var:
        print(f"✅ Got variable: {type(var)}")
        
        # Force get_data call
        get_data(trange, var)
        
        # Check if data was actually loaded
        print(f"\n📊 Data check after loading:")
        print(f"   Class datetime_array: {type(getattr(class_instance, 'datetime_array', None))}")
        if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
            print(f"   Datetime array length: {len(class_instance.datetime_array)}")
        else:
            print(f"   ❌ No datetime_array found")
            
    else:
        print("❌ Could not get variable")
        
except Exception as e:
    print(f"❌ Error during data loading: {e}")
    import traceback
    traceback.print_exc()
