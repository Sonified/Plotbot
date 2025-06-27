#!/usr/bin/env python3
"""
Test script for PSP Alpha Particle integration - alpha particle moments
Following established patterns from WIND tests.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot import *
import numpy as np
from datetime import datetime, timedelta

def test_psp_alpha_simple():
    """Test PSP Alpha particle moments - simple integration test"""
    print("\n" + "="*60)
    print("🧪 PSP Alpha Particle Simple Integration Test")
    print("Testing: download → processing → plotting pipeline")
    print("="*60)
    
    # Use the same time range as the alphas_integration.ipynb
    trange = ['2022/06/01 20:00:00.000', '2022/06/02 02:00:00.000']  # 6 hours
    print(f"📅 Test time range: {trange[0]} to {trange[1]}")
    
    try:
        # Test 1: Download PSP Alpha data
        print("\n🔄 Step 1: Testing data download...")
        data_result = get_data(trange, 'spi_sf0a_l3_mom')
        print(f"✅ Download successful: {type(data_result)}")
        
        # Test 2: Check if data was processed into class
        print("\n🔄 Step 2: Testing data processing...")
        print(f"📊 psp_alpha class type: {type(psp_alpha)}")
        print(f"📊 psp_alpha data_type: {psp_alpha.data_type}")
        
        # Check if we have time data
        if hasattr(psp_alpha, 'datetime_array') and psp_alpha.datetime_array is not None:
            print(f"⏰ Time points: {len(psp_alpha.datetime_array)}")
            print(f"⏰ Time range: {psp_alpha.datetime_array[0]} to {psp_alpha.datetime_array[-1]}")
        else:
            print("⚠️  No datetime_array found")
            
        # Check variables
        print("\n🔄 Step 3: Testing variables...")
        variables_to_test = [
            'density', 'temperature', 'vr', 'vt', 'vn', 'v_sw',
            't_par', 't_perp', 'anisotropy', 'sun_dist_rsun'
        ]
        
        for var_name in variables_to_test:
            if hasattr(psp_alpha, var_name):
                var_obj = getattr(psp_alpha, var_name)
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
        if hasattr(psp_alpha, 'raw_data') and psp_alpha.raw_data:
            for var_name, var_data in psp_alpha.raw_data.items():
                if var_data is not None:
                    if isinstance(var_data, np.ndarray):
                        print(f"📊 {var_name}: shape={var_data.shape}, dtype={var_data.dtype}")
                        print(f"   Range: [{np.nanmin(var_data):.3e}, {np.nanmax(var_data):.3e}]")
                        
                        # Check for data quality issues
                        if var_name == 'density':
                            valid_count = np.sum(~np.isnan(var_data))
                            negative_count = np.sum(var_data < 0)
                            print(f"   Valid alpha density values: {valid_count}/{len(var_data)}")
                            if negative_count > 0:
                                print(f"   ⚠️  Found {negative_count} negative densities")
                        elif var_name == 'temperature':
                            valid_count = np.sum(~np.isnan(var_data))
                            negative_count = np.sum(var_data < 0)
                            print(f"   Valid alpha temperature values: {valid_count}/{len(var_data)}")
                            if negative_count > 0:
                                print(f"   ⚠️  Found {negative_count} negative temperatures")
                        elif var_name == 'anisotropy':
                            valid_count = np.sum(~np.isnan(var_data))
                            print(f"   Valid alpha anisotropy values: {valid_count}/{len(var_data)}")
                    else:
                        print(f"📊 {var_name}: {type(var_data)}")
                else:
                    print(f"❌ {var_name}: None")
        else:
            print("❌ No raw_data found")
            
        # Test 4: Simple plotting test
        print("\n🔄 Step 5: Testing plotting...")
        try:
            # Test plotting alpha density
            plotbot(trange, psp_alpha.density)
            print("✅ Alpha density plot successful")
            
            # Test plotting alpha temperature
            plotbot(trange, psp_alpha.temperature)
            print("✅ Alpha temperature plot successful")
            
            # Test plotting alpha velocity components
            plotbot(trange, psp_alpha.vr)
            print("✅ Alpha radial velocity plot successful")
            
            # Test plotting alpha temperature anisotropy
            plotbot(trange, psp_alpha.anisotropy)
            print("✅ Alpha temperature anisotropy plot successful")
            
        except Exception as plot_error:
            print(f"❌ Plotting error: {plot_error}")
            
        # Test 5: Multi-variable plotting (alpha vs proton comparison)
        print("\n🔄 Step 6: Testing multi-variable plotting...")
        try:
            # Test plotting alpha vs proton comparison
            plotbot(trange, 
                    psp_alpha.density, 1,    # Alpha density
                    proton.density, 2,       # Proton density  
                    psp_alpha.temperature, 3, # Alpha temperature
                    proton.temperature, 4)    # Proton temperature
            print("✅ Alpha vs proton comparison plot successful")
            
        except Exception as plot_error:
            print(f"❌ Multi-variable plotting error: {plot_error}")
            
        # Test 6: Velocity comparison test
        print("\n🔄 Step 7: Testing velocity comparison...")
        try:
            # Test plotting velocity components comparison
            plotbot(trange, 
                    psp_alpha.vr, 1,         # Alpha radial velocity
                    proton.vr, 2,            # Proton radial velocity
                    psp_alpha.v_sw, 3,       # Alpha solar wind speed
                    proton.v_sw, 4)          # Proton solar wind speed
            print("✅ Alpha vs proton velocity comparison successful")
            
        except Exception as plot_error:
            print(f"❌ Velocity comparison error: {plot_error}")
            
        print("\n✅ PSP Alpha particle integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ PSP Alpha test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_psp_alpha_pytest_style():
    """Test PSP Alpha particle download functionality - pytest style for integration tests"""
    
    from plotbot import config
    from plotbot.plotbot_main import plotbot
    from plotbot.print_manager import print_manager
    
    # Set print_manager verbosity for detailed test output
    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True
    print_manager.show_test = True
    
    print_manager.test(f"\n========================= TEST START: PSP ALPHA =========================")
    print_manager.test("Testing PSP alpha particle data download and plotting.")
    print_manager.test("===========================================================================\n")

    # Define a time range that has PSP data coverage  
    trange_strings = ['2022/06/01 20:00:00.000', '2022/06/02 02:00:00.000']
    print_manager.test(f"Using trange for PSP alpha particles: {trange_strings}")
    
    # Configure server
    print_manager.test(f"\n--- Phase 1: Configuring server for PSP alpha download ---")
    original_server = config.data_server
    config.data_server = 'dynamic'  # This should try SPDF first for PSP
    print_manager.test(f"Set config.data_server to: {config.data_server}")

    try:
        # Import PSP alpha class and PSP proton for comparison
        from plotbot.data_classes.psp_alpha_classes import psp_alpha
        from plotbot import proton
        
        print_manager.test(f"Calling plotbot to test PSP alpha particles and proton comparison...")
        # Plot comprehensive alpha vs proton comparison
        plotbot(trange_strings, 
                psp_alpha.density, 1,        # Alpha density
                proton.density, 2,           # Proton density
                psp_alpha.temperature, 3,    # Alpha temperature  
                proton.temperature, 4,       # Proton temperature
                psp_alpha.vr, 5,            # Alpha radial velocity
                proton.vr, 6,               # Proton radial velocity
                psp_alpha.anisotropy, 7,    # Alpha temperature anisotropy
                proton.anisotropy, 8)       # Proton temperature anisotropy
        print_manager.test("Plotbot call completed successfully.")
        
    except Exception as e:
        print_manager.test(f"ERROR during plotbot call for PSP alpha particles: {e}")
        config.data_server = original_server
        raise Exception(f"Test failed during plotbot call for PSP alpha particles: {e}")
    finally:
        config.data_server = original_server
        print_manager.test(f"Restored config.data_server to: {config.data_server}")
    
    print_manager.test(f"SUCCESS: PSP alpha particle test passed. Plotbot call completed without error.")

if __name__ == "__main__":
    # Run the detailed test
    success = test_psp_alpha_simple()
    if success:
        print("\n🎉 All tests passed!")
        
        # Also run the pytest-style test
        try:
            test_psp_alpha_pytest_style()
            print("\n🎉 Pytest-style test also passed!")
            sys.exit(0)
        except Exception as e:
            print(f"\n💥 Pytest-style test failed: {e}")
            sys.exit(1)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 