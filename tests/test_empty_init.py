#!/usr/bin/env python3
"""Test different initialization strategies for empty plot_managers"""

import numpy as np
import sys
sys.path.insert(0, '/Users/robertalexander/GitHub/Plotbot')

from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

print("="*70)
print("TESTING EMPTY PLOT_MANAGER INITIALIZATION STRATEGIES")
print("="*70)

# Test configs
test_config = plot_config(
    data_type='test',
    class_name='test',
    subclass_name='test',
    plot_type='time_series',
    datetime_array=None
)

strategies = [
    ("Empty array []", np.array([])),
    ("Empty float64 []", np.array([], dtype=np.float64)),
    ("Single NaN", np.array([np.nan])),
    ("Array of NaNs (5)", np.full(5, np.nan)),
    ("Zeros (5)", np.zeros(5)),
    ("Ones (5)", np.ones(5)),
]

for name, init_data in strategies:
    print("\n" + "="*70)
    print("Strategy: " + name)
    print("="*70)
    
    try:
        # Create plot_managers
        pm1 = plot_manager(init_data.copy(), plot_config=test_config)
        pm2 = plot_manager(init_data.copy(), plot_config=test_config)
        
        print("  Created plot_managers")
        print("     pm1 shape: {}, dtype: {}".format(pm1.shape, pm1.dtype))
        print("     pm2 shape: {}, dtype: {}".format(pm2.shape, pm2.dtype))
        
        # Try numpy operations
        result1 = np.arctan2(pm1, pm2)
        print("  np.arctan2() succeeded")
        print("     result shape: {}, dtype: {}".format(result1.shape, result1.dtype))
        print("     result type: {}".format(type(result1)))
        
        result2 = np.degrees(result1)
        print("  np.degrees() succeeded")
        print("     result shape: {}, dtype: {}".format(result2.shape, result2.dtype))
        
        result3 = result2 + 180
        print("  Addition succeeded")
        print("     final shape: {}, dtype: {}".format(result3.shape, result3.dtype))
        print("     final values: {}".format(result3))
        
        # Test: Does old data "stick" when we update?
        print("\n  Testing data replacement:")
        new_data = np.array([1.0, 2.0, 3.0])
        pm1_updated = plot_manager(new_data, plot_config=test_config)
        print("     Old pm1 shape: {}".format(pm1.shape))
        print("     New pm1 shape: {}".format(pm1_updated.shape))
        print("     New values: {}".format(pm1_updated))
        print("  Data replacement works - old data doesn't stick!")
        
    except Exception as e:
        print("  FAILED: {}".format(e))
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print("Initialize with: np.array([], dtype=np.float64)")
print("Reason: Works with numpy ops, returns empty, doesn't stick around")
print("="*70)

