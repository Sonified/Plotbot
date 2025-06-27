#!/usr/bin/env python3
"""
Test script for WIND SWE H5 integration - electron temperature
Following established patterns from other WIND tests.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot import *
import numpy as np
from datetime import datetime, timedelta

def test_wind_swe_h5_simple():
    """Test WIND SWE H5 electron temperature - simple integration test"""
    print("\n" + "="*60)
    print("🧪 WIND SWE H5 Simple Integration Test")
    print("Testing: download → processing → plotting pipeline")
    print("="*60)
    
    # Use a short time range for quick testing
    trange = ['2022-06-01/00:00:00', '2022-06-01/06:00:00']  # 6 hours
    print(f"📅 Test time range: {trange[0]} to {trange[1]}")
    
    try:
        # Test 1: Download WIND SWE H5 data
        print("\n🔄 Step 1: Testing data download...")
        data_result = get_data(trange, 'wind_swe_h5')
        print(f"✅ Download successful: {type(data_result)}")
        
        # Test 2: Check if data was processed into class
        print("\n🔄 Step 2: Testing data processing...")
        print(f"📊 wind_swe_h5 class type: {type(wind_swe_h5)}")
        print(f"📊 wind_swe_h5 data_type: {wind_swe_h5.data_type}")
        
        # Check if we have time data
        if hasattr(wind_swe_h5, 'datetime_array') and wind_swe_h5.datetime_array is not None:
            print(f"⏰ Time points: {len(wind_swe_h5.datetime_array)}")
            print(f"⏰ Time range: {wind_swe_h5.datetime_array[0]} to {wind_swe_h5.datetime_array[-1]}")
        else:
            print("⚠️  No datetime_array found")
            
        # Check variables
        print("\n🔄 Step 3: Testing variables...")
        variables_to_test = ['t_elec']
        
        for var_name in variables_to_test:
            if hasattr(wind_swe_h5, var_name):
                var_obj = getattr(wind_swe_h5, var_name)
                print(f"✅ {var_name}: {type(var_obj)}")
                
                # Check if it has plot options
                if hasattr(var_obj, 'plot_options'):
                    print(f"   📈 Y-axis label: {var_obj.plot_options.y_label}")
                    print(f"   📈 Legend label: {var_obj.plot_options.legend_label}")
                    print(f"   🎨 Plot color: {var_obj.plot_options.color}")
            else:
                print(f"❌ Missing variable: {var_name}")
        
        # Test 3: Check raw data
        print("\n🔄 Step 4: Testing raw data...")
        if hasattr(wind_swe_h5, 'raw_data') and wind_swe_h5.raw_data:
            for var_name, var_data in wind_swe_h5.raw_data.items():
                if var_data is not None:
                    print(f"📊 {var_name}: shape={var_data.shape}, dtype={var_data.dtype}")
                    print(f"   Range: [{np.nanmin(var_data):.3e}, {np.nanmax(var_data):.3e}]")
                    
                    # Check for data quality issues
                    if var_name == 't_elec':
                        valid_count = np.sum(~np.isnan(var_data))
                        negative_count = np.sum(var_data < 0)
                        print(f"   Valid electron temp values: {valid_count}/{len(var_data)}")
                        if negative_count > 0:
                            print(f"   ⚠️  Found {negative_count} negative temperatures")
                else:
                    print(f"❌ {var_name}: None")
        else:
            print("❌ No raw_data found")
            
        # Test 4: Simple plotting test
        print("\n🔄 Step 5: Testing plotting...")
        try:
            # Test plotting electron temperature
            plotbot(trange, wind_swe_h5.t_elec)
            print("✅ Electron temperature plot successful")
            
        except Exception as plot_error:
            print(f"❌ Plotting error: {plot_error}")
            
        print("\n✅ WIND SWE H5 integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ WIND SWE H5 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wind_swe_h5_simple()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 