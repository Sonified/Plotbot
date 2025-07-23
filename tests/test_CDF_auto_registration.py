#!/usr/bin/env python3
"""
Test script to verify CDF auto-registration fix works.
This test checks if auto-registered CDF variables can now be plotted properly.
"""

import sys
import os

# Add project root to path (from tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot
from plotbot.data_cubby import data_cubby

def test_cdf_auto_registration_fix():
    """Test that auto-registered CDF variables can now be plotted (not empty)."""
    print("🔧 TESTING CDF AUTO-REGISTRATION FIX")
    print("=" * 60)
    
    # Check if CDF classes were auto-registered
    print("\n📋 Checking auto-registered CDF classes...")
    cdf_classes = []
    for class_name in data_cubby.class_registry.keys():
        if any(keyword in class_name for keyword in ['waves', 'spectral', 'cdf']):
            cdf_classes.append(class_name)
            print(f"  ✅ Found: {class_name}")
    
    if not cdf_classes:
        print("❌ No CDF classes found in registry")
        return False
    
    # Check if CDF data types were added to data_types
    print("\n📋 Checking CDF data types in configuration...")
    from plotbot.data_classes.data_types import data_types
    
    cdf_data_types = []
    for data_type, config in data_types.items():
        if config.get('data_sources', [None])[0] == 'local_cdf':
            cdf_data_types.append(data_type)
            print(f"  ✅ Found: {data_type} -> {config.get('cdf_class_name', 'Unknown')}")
    
    if not cdf_data_types:
        print("❌ No CDF data types found in configuration")
        return False
    
    # Test get_data with a CDF variable
    print("\n🔄 Testing get_data with CDF variable...")
    
    # Get a CDF class instance
    if 'psp_waves_auto' in data_cubby.class_registry:
        test_class = data_cubby.class_registry['psp_waves_auto']
        print(f"  📊 Using test class: {test_class.__class__.__name__}")
        
        # Check if the class has variables
        if hasattr(test_class, 'wavePower_LH'):
            test_var = test_class.wavePower_LH
            print(f"  📈 Testing variable: {test_var.class_name}.{test_var.subclass_name}")
            
            # Check initial state (should be empty)
            initial_has_data = hasattr(test_var, 'datetime_array') and test_var.datetime_array is not None and len(test_var.datetime_array) > 0
            print(f"  📊 Initial data state: {'Has data' if initial_has_data else 'Empty (expected)'}")
            
            # Test get_data call
            try:
                print("  🔄 Calling get_data for CDF variable...")
                trange = ['2021-04-29/06:00:00', '2021-04-29/07:00:00']
                
                # Enable debug output
                from plotbot.print_manager import print_manager
                original_debug = print_manager.dependency_management_enabled
                print_manager.dependency_management_enabled = True
                print_manager.variable_testing_enabled = True
                
                print(f"  🔍 DEBUG: Variable data_type = {test_var.data_type}")
                print(f"  🔍 DEBUG: Variable class_name = {test_var.class_name}")
                print(f"  🔍 DEBUG: Variable subclass_name = {test_var.subclass_name}")
                
                # Check if the data type is in data_types
                from plotbot.data_classes.data_types import data_types
                if test_var.data_type in data_types:
                    config = data_types[test_var.data_type]
                    print(f"  🔍 DEBUG: Found config for {test_var.data_type}")
                    print(f"  🔍 DEBUG: Data sources: {config.get('data_sources', [])}")
                    print(f"  🔍 DEBUG: Local path: {config.get('local_path', 'None')}")
                else:
                    print(f"  🔍 DEBUG: {test_var.data_type} NOT found in data_types!")
                
                plotbot.get_data(trange, test_var)
                
                # Restore debug settings
                print_manager.dependency_management_enabled = original_debug
                print_manager.variable_testing_enabled = False
                
                # CRITICAL FIX: Re-grab the variable from data_cubby after get_data
                # get_data updates the class instance in data_cubby, not the original variable reference
                updated_class = data_cubby.grab('psp_waves_auto')
                updated_var = updated_class.get_subclass('wavePower_LH')
                
                print(f"  🔄 DEBUG: Original test_var datetime_array: {hasattr(test_var, 'datetime_array') and test_var.datetime_array is not None}")
                print(f"  🔄 DEBUG: Updated var datetime_array: {hasattr(updated_var, 'datetime_array') and updated_var.datetime_array is not None}")
                
                # Check if data was loaded (using the updated variable)
                after_has_data = hasattr(updated_var, 'datetime_array') and updated_var.datetime_array is not None and len(updated_var.datetime_array) > 0
                print(f"  📊 After get_data: {'Has data' if after_has_data else 'Still empty'}")
                
                if after_has_data:
                    print(f"  ✅ SUCCESS: get_data loaded {len(updated_var.datetime_array)} data points")
                    
                    # Test plotting with the updated variable
                    print("  🎨 Testing plotbot call...")
                    try:
                        plotbot.plotbot(trange, updated_var, 1)
                        print("  ✅ SUCCESS: plotbot call completed without empty plot")
                        return True
                    except Exception as e:
                        print(f"  ❌ FAILED: plotbot call failed: {e}")
                        return False
                else:
                    print("  ❌ FAILED: get_data did not load data")
                    return False
                    
            except Exception as e:
                print(f"  ❌ FAILED: get_data call failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("  ❌ Test class has no wavePower_LH variable")
            return False
    else:
        print("  ❌ psp_waves_auto class not found")
        return False

if __name__ == "__main__":
    success = test_cdf_auto_registration_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CDF AUTO-REGISTRATION FIX: SUCCESS!")
        print("✅ Auto-registered CDF variables can now be plotted properly")
    else:
        print("❌ CDF AUTO-REGISTRATION FIX: FAILED!")
        print("🔧 The empty plot issue persists - check implementation") 