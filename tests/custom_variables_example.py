#!/usr/bin/env python3
"""
Custom Variables System Demo

This script demonstrates the custom variables system for Plotbot,
which allows creating derived quantities that update automatically.

To run this example:
cd ~/GitHub/Plotbot && PYTHONPATH=~/GitHub/Plotbot conda run -n plotbot_env python tests/custom_variables_example.py
"""

from plotbot import *
import numpy as np

print("============== Custom Variables System Demo ==============")

# Define a time range
trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
print(f"Using time range: {trange}")

# Create a custom variable that represents the ratio of proton temperature anisotropy to magnetic field magnitude
print("\n1. Creating custom variable 'TAoverB'...")
custom_var = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)

# Access variable properties
print(f"Variable type: {type(custom_var)}")
print(f"Is custom variable: {hasattr(custom_var, 'data_type') and custom_var.data_type == 'custom_data_type'}")
print(f"Class name: {getattr(custom_var, 'class_name', 'unknown')}")
print(f"Subclass name: {getattr(custom_var, 'subclass_name', 'unknown')}")

# Customize the appearance of the custom variable for plotting
print("\n2. Customizing appearance and plotting...")
custom_var.color = 'red'
custom_var.line_style = '-'
custom_var.line_width = 2

# Plot the magnetic field magnitude and the custom variable
print("Generating plot with mag_rtn_4sa.bmag and custom variable...")
# Note: showdahodo or multiplot will handle data loading automatically
showdahodo(trange, mag_rtn_4sa.bmag, custom_var)

# Create more complex custom variables
print("\n3. Creating more complex custom variables...")

# Create a custom variable for the field vector magnitude
print("Creating 'BVecMag' from vector components...")
vec_mag_var = custom_variable('BVecMag', np.sqrt(mag_rtn_4sa.br**2 + mag_rtn_4sa.bt**2 + mag_rtn_4sa.bn**2))

# Create a custom variable for the ratio of radial to transverse field components
print("Creating 'BrOverBt' ratio variable...")
ratio_var = custom_variable('BrOverBt', mag_rtn_4sa.br / mag_rtn_4sa.bt)

# Set colors for plotting
vec_mag_var.color = 'blue'
ratio_var.color = 'green'

# Plot magnetic field magnitude and the vector magnitude for comparison
print("Plotting comparison of field measurements...")
# Note: showdahodo will handle data loading automatically
showdahodo(trange, mag_rtn_4sa.bmag, vec_mag_var, var3=ratio_var)

# Define a new time range to demonstrate time range updates
print("\n4. Demonstrating time range updates...")
new_trange = ['2023-09-28/07:00:00.000', '2023-09-28/08:30:00.000']
print(f"New time range: {new_trange}")

# Plot with the new time range - data and custom variables will update automatically
print("Plotting with new time range...")
showdahodo(new_trange, mag_rtn_4sa.bmag, custom_var)

print("\n============== End of Demo ==============")

# To run tests using the space-themed test runner:
# from plotbot.test_pilot import run_missions
# run_missions("tests.test_custom_variables")

# Alternatively, you can point directly to the test file:
# import pytest
# pytest.main(["-v", "tests/test_custom_variables.py"]) 