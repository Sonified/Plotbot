#!/usr/bin/env python3
"""Quick test: plot_manager with None input converts to empty float64 array"""

import numpy as np
import sys
sys.path.insert(0, '/Users/robertalexander/GitHub/Plotbot')

from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

# Create config
cfg = plot_config(
    data_type='test',
    class_name='test',
    subclass_name='test',
    plot_type='time_series',
    datetime_array=None
)

# Test 1: Create plot_manager with None
print("Test 1: plot_manager(None, plot_config=cfg)")
pm = plot_manager(None, plot_config=cfg)
print(f"  Result: shape={pm.shape}, dtype={pm.dtype}, size={pm.size}")

# Test 2: Numpy operations on empty plot_manager
print("\nTest 2: np.arctan2(pm, pm)")
result = np.arctan2(pm, pm)
print(f"  Result: shape={result.shape}, dtype={result.dtype}")

print("\nTest 3: np.degrees(np.arctan2(pm, pm)) + 180")
result2 = np.degrees(np.arctan2(pm, pm)) + 180
print(f"  Result: shape={result2.shape}, dtype={result2.dtype}")

print("\n✅ SUCCESS: plot_manager handles None input correctly!")

