#!/usr/bin/env python
# Test script for debugging degrees from perihelion feature

import sys
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add Plotbot to the path if needed
#sys.path.append(os.path.abspath('..'))

from plotbot.print_manager import print_manager
from plotbot.multiplot_options import plt, MultiplotOptions
from plotbot import mag_rtn_4sa  # Correct import structure
from plotbot.data_classes.psp_ham_classes import ham as ham_instance  # Fixed ham import
from plotbot.multiplot import multiplot
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

# Enable debug output
print_manager.show_debug = True
print_manager.show_status = True
print_manager.status("Starting degrees from perihelion test...")

# Set up options for degrees from perihelion
print_manager.status("Setting use_degrees_from_perihelion = True")
plt.options.use_degrees_from_perihelion = True
print_manager.status(f"Confirmed use_degrees_from_perihelion is now: {plt.options.use_degrees_from_perihelion}")

plt.options.positional_data_path = 'support_data/trajectories/Parker_positional_data.npz'  # Updated path
plt.options.window = '1day'  # Use a 1-day window 
plt.options.position = 'around'  # Center the plot around the specified time

# Load the positional data mapper
print_manager.status("Attempting to initialize positional mapper directly...")
mapper = XAxisPositionalDataMapper(plt.options.positional_data_path)
if mapper.data_loaded:
    print_manager.status(f"✓ Successfully loaded positional data with {len(mapper.times_numeric)} data points")
    print_manager.status(f"Data ranges:")
    print_manager.status(f"  Longitude: {np.min(mapper.longitude_values):.2f}° to {np.max(mapper.longitude_values):.2f}°")
    if mapper.radial_values is not None:
        print_manager.status(f"  Radial: {np.min(mapper.radial_values):.2f} to {np.max(mapper.radial_values):.2f} R_sun")
    if mapper.latitude_values is not None:
        print_manager.status(f"  Latitude: {np.min(mapper.latitude_values):.2f}° to {np.max(mapper.latitude_values):.2f}°")
    
    # Test direct access to perihelion functions
    from plotbot.utils import get_perihelion_time
    center_time = '2023-09-27'  # E17
    perihelion_time_str = get_perihelion_time(center_time)
    print_manager.status(f"Perihelion time for {center_time}: {perihelion_time_str}")
    
    # Test manual calculation of degrees from perihelion using the mapper
    if perihelion_time_str:
        # Convert perihelion time to datetime
        perihelion_dt = pd.to_datetime(perihelion_time_str, format='%Y/%m/%d %H:%M:%S.%f')
        print_manager.status(f"Perihelion datetime: {perihelion_dt}")
        
        # Map perihelion time to carrington longitude
        perihelion_time_array = np.array([np.datetime64(perihelion_dt)])
        perihelion_lon = mapper.map_to_position(perihelion_time_array, 'carrington_lon')
        
        if perihelion_lon is not None and len(perihelion_lon) > 0:
            perihelion_lon_value = perihelion_lon[0]
            print_manager.status(f"Perihelion longitude: {perihelion_lon_value:.2f}°")
            
            # Test with some nearby times
            test_times = [
                pd.Timestamp(center_time),
                pd.Timestamp(center_time) + pd.Timedelta(hours=6),
                pd.Timestamp(center_time) - pd.Timedelta(hours=6)
            ]
            test_times_np = np.array([np.datetime64(t) for t in test_times])
            
            # Map test times to carrington longitudes
            test_lons = mapper.map_to_position(test_times_np, 'carrington_lon')
            
            if test_lons is not None:
                # Calculate relative degrees (simple subtraction with wrap-around handling)
                relative_degrees = []
                for lon in test_lons:
                    rel_deg = lon - perihelion_lon_value
                    # Handle wrap-around (ensure range is -180 to +180)
                    if rel_deg > 180:
                        rel_deg -= 360
                    elif rel_deg <= -180:
                        rel_deg += 360
                    relative_degrees.append(rel_deg)
                
                print_manager.status(f"Test times: {test_times}")
                print_manager.status(f"Test longitudes: {test_lons}")
                print_manager.status(f"Relative degrees from perihelion: {relative_degrees}")
            else:
                print_manager.error(f"Failed to map test times to longitudes")
        else:
            print_manager.error(f"Failed to map perihelion time to longitude")
    else:
        print_manager.error(f"No perihelion time found for {center_time}")
else:
    print_manager.error("❌ Failed to load positional data!")

print_manager.status("Options configured for degrees from perihelion")

# Use a time that corresponds to a known perihelion time
center_time = '2023-09-27'  # E17 perihelion is 2023/09/27 23:28:00.000
print_manager.status(f"Using center time: {center_time}")

# Choose magnetic field variable for the plot
br = mag_rtn_4sa.br
print_manager.status(f"Using variable: {br.class_name}.{br.subclass_name}")

# Set up multiplot kwargs to enable debugging
kwargs = {
    'use_degrees_from_perihelion': True,
    'degrees_from_perihelion_tick_step': 30  # Set a reasonable tick step
}

# Create the plot
print_manager.status("Creating multiplot with degrees from perihelion...")
print_manager.status(f"Final check before multiplot: use_degrees_from_perihelion = {plt.options.use_degrees_from_perihelion}")
fig, axs = multiplot([(center_time, br)], **kwargs)

print_manager.status("Test completed.") 