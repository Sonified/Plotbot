#!/usr/bin/env python3
"""
Basic test of WIND 3DP electron classes
Tests import and basic instantiation
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test imports
try:
    from plotbot.data_classes.wind_3dp_classes import wind_3dp_elpd_class, wind_3dp_elpd
    print("✅ Successfully imported wind_3dp_elpd_class and wind_3dp_elpd")
except ImportError as e:
    print(f"❌ Failed to import WIND 3DP classes: {e}")
    sys.exit(1)

# Test class instantiation
try:
    test_instance = wind_3dp_elpd_class(None)
    print("✅ Successfully created wind_3dp_elpd_class instance")
    
    # Check basic attributes
    print(f"Class name: {test_instance.class_name}")
    print(f"Data type: {test_instance.data_type}")
    print(f"Raw data keys: {list(test_instance.raw_data.keys())}")
    print(f"Energy index: {test_instance.energy_index}")
    
except Exception as e:
    print(f"❌ Failed to create wind_3dp_elpd_class instance: {e}")
    sys.exit(1)

# Test global instance
try:
    print(f"Global instance class name: {wind_3dp_elpd.class_name}")
    print(f"Global instance data type: {wind_3dp_elpd.data_type}")
    print("✅ Global wind_3dp_elpd instance working")
except Exception as e:
    print(f"❌ Global wind_3dp_elpd instance failed: {e}")
    sys.exit(1)

# Test data_cubby integration
try:
    from plotbot.data_cubby import data_cubby
    
    # Check if class mapping exists
    class_type = data_cubby._get_class_type_from_string('wind_3dp_elpd')
    if class_type == wind_3dp_elpd_class:
        print("✅ data_cubby class mapping working")
    else:
        print(f"❌ data_cubby class mapping failed: {class_type}")
        
except Exception as e:
    print(f"❌ data_cubby integration failed: {e}")
    sys.exit(1)

print("\n🎉 All basic WIND 3DP electron class tests passed!") 