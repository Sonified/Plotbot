#!/usr/bin/env python3
"""
VDF GET_DATA PIPELINE DEBUG TEST

This test rebuilds the entire get_data() pipeline with massive debug prints
to find exactly where the VDF processing breaks between import_data_function()
success and calculate_variables() never being called.

CONFIRMED WORKING:
✅ Berkeley download (484MB file)
✅ CDF import (perfect DataObject with 25M+ data points)
✅ DataObject creation (all VDF variables present)

BROKEN PIPELINE:
❌ VDF calculate_variables() never called
❌ VDF raw_data remains empty (all None)
❌ DataCubby.update_global_instance() likely failing

TARGET: Find the exact failure point in the pipeline
"""

import sys
import os
sys.path.append('.')

import numpy as np
from datetime import datetime, timezone
from dateutil.parser import parse

def debug_get_data_pipeline():
    """
    Manually rebuild get_data() pipeline with debug prints at every step
    to find where the VDF processing breaks.
    """
    print("🚨 VDF GET_DATA PIPELINE DEBUG")
    print("="*70)
    
    # Import all required modules with debug
    print("\n🔧 STEP 1: Import modules...")
    from plotbot.print_manager import print_manager
    from plotbot.data_tracker import global_tracker
    from plotbot.data_cubby import data_cubby
    from plotbot.data_import import import_data_function
    from plotbot.data_classes.data_types import data_types
    
    # Enable debug prints
    print_manager.show_debug = True
    
    print("✅ All modules imported successfully")
    
    # Setup test parameters
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    data_type = 'psp_span_vdf'
    
    print(f"\n🔧 STEP 2: Validate inputs...")
    print(f"   trange: {trange}")
    print(f"   data_type: {data_type}")
    
    # Check data type configuration
    print(f"\n🔧 STEP 3: Check data_type configuration...")
    config = data_types.get(data_type)
    if not config:
        print(f"❌ FATAL: data_type '{data_type}' not found in data_types!")
        return False
    
    print(f"✅ Config found for '{data_type}':")
    print(f"   class_file: {config.get('class_file')}")
    print(f"   class_name: {config.get('class_name')}")
    print(f"   data_vars: {config.get('data_vars')}")
    
    # Get VDF instance BEFORE processing
    print(f"\n🔧 STEP 4: Get VDF instance from DataCubby BEFORE processing...")
    vdf_before = data_cubby.grab('psp_span_vdf')
    if not vdf_before:
        print(f"❌ FATAL: VDF instance not found in DataCubby!")
        return False
    
    print(f"✅ VDF instance found:")
    print(f"   Instance ID: {id(vdf_before)}")
    print(f"   Instance type: {type(vdf_before)}")
    print(f"   Has raw_data: {hasattr(vdf_before, 'raw_data')}")
    print(f"   Has datetime_array: {hasattr(vdf_before, 'datetime_array')}")
    print(f"   datetime_array value: {vdf_before.datetime_array}")
    
    if hasattr(vdf_before, 'raw_data'):
        print(f"   raw_data keys: {list(vdf_before.raw_data.keys())}")
        print(f"   raw_data['epoch']: {vdf_before.raw_data.get('epoch')}")
    
    # Check if calculation is needed
    print(f"\n🔧 STEP 5: Check if calculation is needed...")
    calculation_needed = global_tracker.is_calculation_needed(trange, data_type)
    print(f"   Calculation needed: {calculation_needed}")
    print(f"   Tracker state: {global_tracker.calculated_ranges}")
    
    if not calculation_needed:
        print("⚠️  Tracker says no calculation needed - forcing fresh calculation")
        # Clear tracker to force calculation
        if data_type in global_tracker.calculated_ranges:
            del global_tracker.calculated_ranges[data_type]
        print(f"   Cleared tracker for {data_type}")
    
    # Call import_data_function directly
    print(f"\n🔧 STEP 6: Call import_data_function()...")
    print(f"   Calling: import_data_function({trange}, '{data_type}')")
    
    data_obj = import_data_function(trange, data_type)
    
    print(f"\n📊 IMPORT_DATA_FUNCTION RESULT:")
    print(f"   Result: {data_obj}")
    print(f"   Result type: {type(data_obj)}")
    
    if data_obj is None:
        print("❌ FATAL: import_data_function returned None!")
        return False
    
    # Validate DataObject
    print(f"\n🔧 STEP 7: Validate DataObject...")
    print(f"   Has .data: {hasattr(data_obj, 'data')}")
    print(f"   Has .times: {hasattr(data_obj, 'times')}")
    
    if hasattr(data_obj, 'data') and data_obj.data:
        print(f"   Data keys: {list(data_obj.data.keys())}")
        for key in ['THETA', 'PHI', 'ENERGY', 'EFLUX']:
            if key in data_obj.data:
                value = data_obj.data[key]
                print(f"     {key}: shape={getattr(value, 'shape', 'no shape')}, type={type(value)}")
    
    if hasattr(data_obj, 'times') and data_obj.times is not None:
        print(f"   Times: length={len(data_obj.times)}, type={type(data_obj.times)}")
        print(f"   First 3 times: {data_obj.times[:3]}")
    
    print("✅ DataObject validation complete - ALL DATA PRESENT!")
    
    # Now test DataCubby.update_global_instance
    print(f"\n🔧 STEP 8: Call DataCubby.update_global_instance()...")
    print(f"   Instance ID before: {id(vdf_before)}")
    print(f"   Calling: data_cubby.update_global_instance('{data_type}', data_obj, trange)")
    
    # Add extra debug to DataCubby call
    try:
        update_success = data_cubby.update_global_instance(
            data_type_str=data_type,
            imported_data_obj=data_obj,
            original_requested_trange=trange
        )
        print(f"   update_global_instance returned: {update_success}")
    except Exception as e:
        print(f"❌ EXCEPTION in update_global_instance: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Get VDF instance AFTER processing
    print(f"\n🔧 STEP 9: Get VDF instance AFTER processing...")
    vdf_after = data_cubby.grab('psp_span_vdf')
    
    print(f"   Instance ID after: {id(vdf_after)}")
    print(f"   Same instance: {id(vdf_before) == id(vdf_after)}")
    print(f"   Has datetime_array: {hasattr(vdf_after, 'datetime_array')}")
    print(f"   datetime_array value: {vdf_after.datetime_array}")
    
    if hasattr(vdf_after, 'raw_data'):
        print(f"   raw_data keys: {list(vdf_after.raw_data.keys())}")
        
        # Check if any data was actually populated
        populated_keys = []
        for key, value in vdf_after.raw_data.items():
            if value is not None:
                populated_keys.append(key)
        
        print(f"   Populated keys: {populated_keys}")
        print(f"   Empty keys: {[k for k in vdf_after.raw_data.keys() if k not in populated_keys]}")
        
        # Check specific critical data
        epoch_data = vdf_after.raw_data.get('epoch')
        theta_data = vdf_after.raw_data.get('theta')
        vdf_data = vdf_after.raw_data.get('vdf')
        
        print(f"   epoch data: {epoch_data}")
        print(f"   theta data: {theta_data}")
        print(f"   vdf data: {vdf_data}")
    
    # Final analysis
    print(f"\n📊 PIPELINE ANALYSIS:")
    if hasattr(vdf_after, 'raw_data') and any(v is not None for v in vdf_after.raw_data.values()):
        print("✅ SUCCESS: VDF raw_data was populated!")
        print("✅ calculate_variables() was called successfully!")
        return True
    else:
        print("❌ FAILURE: VDF raw_data is still empty!")
        print("❌ calculate_variables() was NOT called!")
        print("\n🔍 POSSIBLE FAILURE POINTS:")
        print("   1. DataCubby.update_global_instance() not calling VDF.update()")
        print("   2. VDF.update() method missing or broken")
        print("   3. VDF.update() not calling calculate_variables()")
        print("   4. calculate_variables() failing silently")
        return False

def test_vdf_update_method():
    """
    Test if VDF instance has an update() method and if it works.
    """
    print("\n🔧 TESTING VDF UPDATE METHOD DIRECTLY")
    print("="*50)
    
    from plotbot.data_cubby import data_cubby
    from plotbot.data_import import import_data_function
    
    # Get VDF instance
    vdf_instance = data_cubby.grab('psp_span_vdf')
    print(f"VDF instance: {vdf_instance}")
    print(f"Has update method: {hasattr(vdf_instance, 'update')}")
    
    if hasattr(vdf_instance, 'update'):
        print("✅ VDF has update() method")
        
        # Get fresh DataObject
        trange = ['2020-01-29/00:00', '2020-01-30/00:00']
        data_obj = import_data_function(trange, 'psp_span_vdf')
        
        if data_obj:
            print("✅ Got fresh DataObject")
            print("   Calling vdf_instance.update(data_obj) directly...")
            
            try:
                result = vdf_instance.update(data_obj)
                print(f"   update() returned: {result}")
                
                # Check if data was populated
                if hasattr(vdf_instance, 'raw_data'):
                    populated = [k for k, v in vdf_instance.raw_data.items() if v is not None]
                    print(f"   Populated after update: {populated}")
                
            except Exception as e:
                print(f"❌ EXCEPTION in update(): {e}")
                import traceback
                traceback.print_exc()
    else:
        print("❌ VDF has NO update() method!")
        
        # Check what methods it does have
        methods = [attr for attr in dir(vdf_instance) if callable(getattr(vdf_instance, attr)) and not attr.startswith('_')]
        print(f"Available methods: {methods}")

if __name__ == '__main__':
    print("Starting VDF get_data() pipeline debug...")
    
    # Test the full pipeline
    success = debug_get_data_pipeline()
    
    # If pipeline failed, test VDF update method directly
    if not success:
        test_vdf_update_method()
    
    print("\n" + "="*70)
    if success:
        print("🎉 VDF PIPELINE DEBUG: SUCCESS!")
    else:
        print("💥 VDF PIPELINE DEBUG: FAILED - Check output above for failure point")