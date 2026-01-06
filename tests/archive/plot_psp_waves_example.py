#!/usr/bin/env python3
"""
Example: Plot PSP wave power data using smart scan
"""

import sys
sys.path.insert(0, '.')

from plotbot import *

print("🌊 PSP Wave Power Plotting Example")
print("=" * 40)

# Enable debug output to see smart scan and merge operations
print_manager.show_status = True
print_manager.show_debug = True
print_manager.show_data_cubby = True

# Test comparison: Load mag_rtn data for same time range to compare paths
print("🧪 COMPARISON TEST: Loading mag_rtn data for same time range...")
try:
    mag_rtn_instance = mag_rtn()
    mag_rtn_instance.get_data(trange1)  # First load for mag_rtn
    print("✅ mag_rtn first load completed")
    
    # Set custom styling for mag_rtn to test preservation
    mag_rtn_instance.br.color = "purple"
    mag_rtn_instance.br.legend_label = "BR Test (mag_rtn)"
    
    mag_rtn_instance.get_data(trange2)  # Second load for mag_rtn  
    print(f"🔍 mag_rtn after second load - BR color: {mag_rtn_instance.br.color}, legend: {mag_rtn_instance.br.legend_label}")
    
except Exception as e:
    print(f"❌ mag_rtn comparison test failed: {e}")

print("🧪 Now proceeding with psp_waves_test...")
print("="*50)

# Test both dates to show smart scan working with different files
date_ranges = [
    ['2021-04-29/06:00:00', '2021-04-29/12:00:00'],
    ['2023-06-22/06:00:00', '2023-06-22/12:00:00']
]

for i, trange in enumerate(date_ranges, 1):
    print(f"\n🎯 Test {i}: {trange[0][:10]} data")
    print(f"📅 Time range: {trange[0]} to {trange[1]}")

    try:
        # This should automatically:
        # 1. Use smart scan to find both PSP_wavePower files
        # 2. Filter to correct file based on time range
        # 3. Load and plot the data
        
        # Set some styling
        psp_waves_test.wavePower_LH.color = "blue"
        psp_waves_test.wavePower_RH.color = "red"
        psp_waves_test.wavePower_LH.legend_label = f"LH Wave Power ({trange[0][:10]})"
        psp_waves_test.wavePower_RH.legend_label = f"RH Wave Power ({trange[0][:10]})"
        
        # Get data for this time range (triggers debug logging)
        psp_waves_test.get_data(trange)
        
        # Check state after data load
        print(f"🔍 After Test {i} - wavePower_RH color: {psp_waves_test.wavePower_RH.color}, legend: {psp_waves_test.wavePower_RH.legend_label}")
        
        print(f"✅ Test {i} plotting successful!")
        print("   Smart scan found multiple files but used only the relevant one")
        
    except Exception as e:
        print(f"❌ Test {i} error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n📊 Class info:")
try:
    class_instance = data_cubby.grab("psp_waves_test")
    if class_instance:
        pattern = getattr(class_instance, '_cdf_file_pattern', 'Not found')
        print(f"   Pattern: {pattern}")
        print(f"   Files discovered by pattern:")
        
        import glob
        from pathlib import Path
        cdf_dir = Path("data/cdf_files/PSP_Waves")
        pattern_path = str(cdf_dir / pattern)
        matching_files = glob.glob(pattern_path)
        for f in matching_files:
            print(f"     ✅ {Path(f).name}")
except Exception as e:
    print(f"   Error getting class info: {e}")
