#!/usr/bin/env python3
"""
Debug script to test CDF class generation from PSP_Waves files
and verify that data from multiple dates (2021-04-29 and 2023-06-22) 
is properly loaded and merged with correct metadata.

Tests:
1. Generate CDF class from PSP_Waves directory
2. Load data from first date (2021-04-29)
3. Load data from second date (2023-06-22)
4. Verify both datasets are properly loaded
5. Check metadata persistence (styling, labels)
6. Verify datetime_array syncing
"""

from plotbot import *
import os

print("🧪 CDF MULTI-FILE DEBUG TEST")
print("=" * 60)

# Enable comprehensive debugging
print_manager.show_status = True
print_manager.show_debug = True
print_manager.show_data_cubby = True
print_manager.show_style_preservation = True

# ============================================================================
# STEP 1: Generate CDF classes from PSP_Waves directory
# ============================================================================
print("\n📂 STEP 1: Generating CDF classes from PSP_Waves directory")
print("-" * 60)

cdf_dir = "/Users/robertalexander/GitHub/Plotbot/data/cdf_files/PSP_Waves"
print(f"📁 CDF Directory: {cdf_dir}")

# List files in directory
if os.path.exists(cdf_dir):
    files = [f for f in os.listdir(cdf_dir) if f.endswith('.cdf')]
    print(f"📄 Found {len(files)} CDF files:")
    for f in sorted(files):
        print(f"   - {f}")
else:
    print(f"❌ Directory not found: {cdf_dir}")
    exit(1)

try:
    # Generate classes
    print("\n🔧 Generating classes...")
    scan_cdf_directory(cdf_dir)
    print("✅ Class generation completed")
except Exception as e:
    print(f"❌ Class generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# STEP 2: Verify generated class exists
# ============================================================================
print("\n📊 STEP 2: Verifying generated class")
print("-" * 60)

try:
    # Check if psp_waves_test class exists
    test_class = data_cubby.grab("psp_waves_test")
    if test_class:
        print("✅ psp_waves_test class found in data_cubby")
        print(f"   Class type: {type(test_class)}")
        
        # Check available variables
        if hasattr(test_class, 'wavePower_LH'):
            print("   ✅ wavePower_LH variable available")
        if hasattr(test_class, 'wavePower_RH'):
            print("   ✅ wavePower_RH variable available")
    else:
        print("❌ psp_waves_test class not found")
        exit(1)
except Exception as e:
    print(f"❌ Class verification failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# STEP 3: Load data from first date (2021-04-29)
# ============================================================================
print("\n📅 STEP 3: Loading data from first date (2021-04-29)")
print("-" * 60)

trange1 = ['2021-04-29/06:00:00', '2021-04-29/12:00:00']
print(f"🕐 Time range: {trange1[0]} to {trange1[1]}")

try:
    # Set custom styling BEFORE first load
    print("\n🎨 Setting custom styling BEFORE first load...")
    psp_waves_test.wavePower_LH.color = "blue"
    psp_waves_test.wavePower_RH.color = "red"
    psp_waves_test.wavePower_LH.legend_label = "LH Power (2021) - Custom Blue"
    psp_waves_test.wavePower_RH.legend_label = "RH Power (2021) - Custom Red"
    print(f"   LH: color=blue, label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: color=red, label='{psp_waves_test.wavePower_RH.legend_label}'")
    
    # Plot first date
    print("\n📈 Plotting first date...")
    plotbot(trange1, psp_waves_test.wavePower_LH, 1, psp_waves_test.wavePower_RH, 2)
    print("✅ First plot completed")
    
    # Check class state after first load
    print("\n📊 Class state after first load:")
    class_instance = data_cubby.grab("psp_waves_test")
    if class_instance:
        dt_array = getattr(class_instance, 'datetime_array', None)
        if dt_array is not None and len(dt_array) > 0:
            print(f"   datetime_array: {len(dt_array)} points")
            print(f"   Time range: {dt_array[0]} to {dt_array[-1]}")
        
        # Check raw_data
        raw_data = getattr(class_instance, 'raw_data', {})
        print(f"   raw_data keys: {list(raw_data.keys())}")
        for key in ['wavePower_LH', 'wavePower_RH']:
            if key in raw_data:
                val = raw_data[key]
                if val is not None:
                    print(f"   {key}: shape={getattr(val, 'shape', 'N/A')}")
    
    # Check styling persistence after first load
    print("\n🎨 Styling after first load:")
    print(f"   LH: color={psp_waves_test.wavePower_LH.color}, label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: color={psp_waves_test.wavePower_RH.color}, label='{psp_waves_test.wavePower_RH.legend_label}'")
    
except Exception as e:
    print(f"❌ First load failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# STEP 4: Load data from second date (2023-06-22)
# ============================================================================
print("\n" + "=" * 60)
print("📅 STEP 4: Loading data from second date (2023-06-22)")
print("-" * 60)

trange2 = ['2023-06-22/06:00:00', '2023-06-22/12:00:00']
print(f"🕐 Time range: {trange2[0]} to {trange2[1]}")

try:
    # Check styling BEFORE second load (should still be custom)
    print("\n🎨 Styling BEFORE second load:")
    print(f"   LH: color={psp_waves_test.wavePower_LH.color}, label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: color={psp_waves_test.wavePower_RH.color}, label='{psp_waves_test.wavePower_RH.legend_label}'")
    
    # Update legend labels for second load
    print("\n🎨 Updating legend labels for second date...")
    psp_waves_test.wavePower_LH.legend_label = "LH Power (2023) - Custom Blue"
    psp_waves_test.wavePower_RH.legend_label = "RH Power (2023) - Custom Red"
    print(f"   LH: label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: label='{psp_waves_test.wavePower_RH.legend_label}'")
    
    # Plot second date
    print("\n📈 Plotting second date...")
    plotbot(trange2, psp_waves_test.wavePower_LH, 1, psp_waves_test.wavePower_RH, 2)
    print("✅ Second plot completed")
    
    # Check class state after second load
    print("\n📊 Class state after second load:")
    class_instance = data_cubby.grab("psp_waves_test")
    if class_instance:
        dt_array = getattr(class_instance, 'datetime_array', None)
        if dt_array is not None and len(dt_array) > 0:
            print(f"   datetime_array: {len(dt_array)} points")
            print(f"   Time range: {dt_array[0]} to {dt_array[-1]}")
        
        # Check raw_data
        raw_data = getattr(class_instance, 'raw_data', {})
        print(f"   raw_data keys: {list(raw_data.keys())}")
        for key in ['wavePower_LH', 'wavePower_RH']:
            if key in raw_data:
                val = raw_data[key]
                if val is not None:
                    print(f"   {key}: shape={getattr(val, 'shape', 'N/A')}")
    
    # Check styling persistence after second load
    print("\n🎨 Styling after second load (SHOULD PRESERVE BLUE/RED COLORS!):")
    print(f"   LH: color={psp_waves_test.wavePower_LH.color}, label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: color={psp_waves_test.wavePower_RH.color}, label='{psp_waves_test.wavePower_RH.legend_label}'")
    
    # Compare with expected
    if psp_waves_test.wavePower_LH.color == "blue":
        print("   ✅ LH color preserved correctly!")
    else:
        print(f"   ❌ LH color changed to {psp_waves_test.wavePower_LH.color} (expected blue)")
    
    if psp_waves_test.wavePower_RH.color == "red":
        print("   ✅ RH color preserved correctly!")
    else:
        print(f"   ❌ RH color changed to {psp_waves_test.wavePower_RH.color} (expected red)")
        
except Exception as e:
    print(f"❌ Second load failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# STEP 5: Load data from THIRD time range (back to 2021)
# ============================================================================
print("\n" + "=" * 60)
print("📅 STEP 5: Loading data from third time range (back to 2021)")
print("-" * 60)

trange3 = ['2021-04-29/14:00:00', '2021-04-29/18:00:00']
print(f"🕐 Time range: {trange3[0]} to {trange3[1]}")

try:
    # Update legend labels for third load
    print("\n🎨 Updating legend labels for third time range...")
    psp_waves_test.wavePower_LH.legend_label = "LH Power (2021 afternoon) - Custom Blue"
    psp_waves_test.wavePower_RH.legend_label = "RH Power (2021 afternoon) - Custom Red"
    
    # Plot third time range
    print("\n📈 Plotting third time range...")
    plotbot(trange3, psp_waves_test.wavePower_LH, 1, psp_waves_test.wavePower_RH, 2)
    print("✅ Third plot completed")
    
    # Check styling persistence
    print("\n🎨 Styling after third load (SHOULD STILL BE BLUE/RED!):")
    print(f"   LH: color={psp_waves_test.wavePower_LH.color}, label='{psp_waves_test.wavePower_LH.legend_label}'")
    print(f"   RH: color={psp_waves_test.wavePower_RH.color}, label='{psp_waves_test.wavePower_RH.legend_label}'")
    
except Exception as e:
    print(f"❌ Third load failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# STEP 6: Compare with proven working class (mag_rtn_4sa)
# ============================================================================
print("\n" + "=" * 60)
print("📊 STEP 6: Comparison with proven working class (mag_rtn_4sa)")
print("-" * 60)

try:
    print("\n🎨 Setting custom styling for mag_rtn_4sa...")
    mag_rtn_4sa.br.color = "purple"
    mag_rtn_4sa.br.legend_label = "Br Custom Purple"
    print(f"   br: color=purple, label='{mag_rtn_4sa.br.legend_label}'")
    
    print("\n📈 Plotting mag_rtn_4sa - First load (2021)...")
    plotbot(['2021-04-29/06:00:00', '2021-04-29/12:00:00'], mag_rtn_4sa.br, 1)
    print(f"   After first load - br: color={mag_rtn_4sa.br.color}")
    
    print("\n📈 Plotting mag_rtn_4sa - Second load (different date)...")
    mag_rtn_4sa.br.legend_label = "Br Custom Purple (different date)"
    plotbot(['2021-04-30/06:00:00', '2021-04-30/12:00:00'], mag_rtn_4sa.br, 1)
    print(f"   After second load - br: color={mag_rtn_4sa.br.color}")
    
    if mag_rtn_4sa.br.color == "purple":
        print("   ✅ mag_rtn_4sa color preserved correctly!")
    else:
        print(f"   ❌ mag_rtn_4sa color changed to {mag_rtn_4sa.br.color}")
        
except Exception as e:
    print(f"❌ mag_rtn_4sa comparison failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("🏁 FINAL SUMMARY")
print("=" * 60)

print("\n📊 CDF Class (psp_waves_test):")
print(f"   LH color: {psp_waves_test.wavePower_LH.color} (expected: blue)")
print(f"   RH color: {psp_waves_test.wavePower_RH.color} (expected: red)")
print(f"   LH label: '{psp_waves_test.wavePower_LH.legend_label}'")
print(f"   RH label: '{psp_waves_test.wavePower_RH.legend_label}'")

print("\n📊 Proven Class (mag_rtn_4sa):")
print(f"   br color: {mag_rtn_4sa.br.color} (expected: purple)")
print(f"   br label: '{mag_rtn_4sa.br.legend_label}'")

print("\n🔍 Issues to Look For:")
print("   1. Do CDF classes lose custom colors during subsequent loads?")
print("   2. Are datetime_arrays properly synced between file loads?")
print("   3. Do both files' data load correctly?")
print("   4. Does the merge path properly preserve state?")

print("\n✅ Test completed!")
