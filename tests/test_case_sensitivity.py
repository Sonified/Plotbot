# Quick test of get_data_type_config

import sys
sys.path.insert(0, '/Users/robertalexander/GitHub/Plotbot')

from plotbot.data_classes.data_types import data_types, get_data_type_config

print("Testing get_data_type_config()...")
available_keys = list(data_types.keys())[:5]
print("\nAvailable keys (first 5):", available_keys)

# Test the function
test_keys = ['mag_rtn_4sa', 'mag_RTN_4sa', 'MAG_RTN_4SA']

for test_key in test_keys:
    result = get_data_type_config(test_key)
    print(f"\nget_data_type_config('{test_key}'):")
    print(f"  Result: {result is not None}")
    if result:
        print(f"  Mission: {result.get('mission')}")
        print(f"  Data sources: {result.get('data_sources')}")
    else:
        print(f"  ERROR: Returned None!")
        
        # Debug: check what's in data_types
        print(f"\n  Debugging:")
        print(f"    Exact match '{test_key}' in data_types: {test_key in data_types}")
        print(f"    test_key.lower(): '{test_key.lower()}'")
        
        # Check each key
        for key in data_types.keys():
            if 'mag' in key.lower() and 'rtn' in key.lower() and '4' in key:
                print(f"    Found MAG key: '{key}' -> key.lower() = '{key.lower()}'")
                print(f"      Match? {key.lower() == test_key.lower()}")

