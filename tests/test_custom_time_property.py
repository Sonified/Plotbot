#!/usr/bin/env python3
"""
Test if .time property works for mag_rtn_4sa and custom variables
"""

import plotbot as pb_module
from plotbot import *
from plotbot.data_classes.custom_variables import custom_variable

print_manager.show_status = True
print_manager.show_custom_debug = True

trange = ['2023-09-28/06:00:00', '2023-09-28/06:30:00']

# Load data
plotbot(trange, mag_rtn_4sa.bmag, 1)

print("=" * 70)
print("Checking .time property:")
print("=" * 70)

# Check mag_rtn_4sa.bmag
print(f"\nmag_rtn_4sa.bmag.time:")
print(f"  Type: {type(mag_rtn_4sa.bmag.time)}")
print(f"  Is None: {mag_rtn_4sa.bmag.time is None}")
if mag_rtn_4sa.bmag.time is not None:
    print(f"  Shape: {mag_rtn_4sa.bmag.time.shape}")
    print(f"  First value: {mag_rtn_4sa.bmag.time[0]}")

# Create custom variable
b_mag_sq = custom_variable('b_mag_sq', mag_rtn_4sa.bmag ** 2)
plotbot(trange, b_mag_sq, 1)

print(f"\nb_mag_sq.time (custom variable via LOCAL variable):")
print(f"  Type: {type(b_mag_sq.time)}")
print(f"  Is None: {b_mag_sq.time is None}")
if b_mag_sq.time is not None:
    print(f"  Shape: {b_mag_sq.time.shape}")
    print(f"  First value: {b_mag_sq.time[0]}")

# Now check via GLOBAL namespace
print(f"\npb_module.b_mag_sq.time (custom variable via GLOBAL namespace):")
print(f"  Type: {type(pb_module.b_mag_sq.time)}")
print(f"  Is None: {pb_module.b_mag_sq.time is None}")
if pb_module.b_mag_sq.time is not None:
    print(f"  Shape: {pb_module.b_mag_sq.time.shape}")
    print(f"  First value: {pb_module.b_mag_sq.time[0]}")
    print("\n✅ .time property WORKS when accessed via global namespace!")
else:
    print("\n❌ .time is still None even via global namespace")

# Check plot_config
print(f"\nb_mag_sq.plot_config.time:")
print(f"  Type: {type(b_mag_sq.plot_config.time)}")
print(f"  Is None: {b_mag_sq.plot_config.time is None}")
if b_mag_sq.plot_config.time is not None:
    print(f"  Shape: {b_mag_sq.plot_config.time.shape}")

