#!/usr/bin/env python3

# Debug test to check array shapes in epad plotting
print("Debugging epad plotting array shapes...")

import sys
import os

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plotbot import *
import numpy as np

# Set up the exact same test case as user reported
trange = ['2018-10-22 12:00:00', '2018-10-27 13:00:00']

print(f"Testing plotbot call with trange: {trange}")

# First let's try to load the data and check the shapes manually
print("\n=== Manual data inspection ===")
try:
    # Load some data first
    get_data(trange, epad.strahl)
    
    print(f"epad.strahl data shape: {np.array(epad.strahl).shape}")
    print(f"epad.strahl datetime_array shape: {epad.strahl.datetime_array.shape}")
    if hasattr(epad.strahl, 'additional_data') and epad.strahl.additional_data is not None:
        print(f"epad.strahl additional_data shape: {epad.strahl.additional_data.shape}")
    else:
        print("epad.strahl has no additional_data")
        
    print(f"epad.strahl.plot_config.datetime_array shape: {epad.strahl.plot_config.datetime_array.shape}")
    
    # Now try the plot
    print("\n=== Attempting plotbot call ===")
    plotbot(trange, mag_rtn_4sa.br, 1, epad.strahl, 2)
    print("✅ SUCCESS: epad plotting worked!")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc() 