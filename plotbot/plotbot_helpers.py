"""
Plotbot helper functions for plotting and data processing.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from dateutil.parser import parse
from .print_manager import print_manager
from .data_cubby import data_cubby
import inspect
import textwrap
from .multiplot_options import plt  # Import our enhanced plt with options
import cdflib
import os
import warnings
from scipy import interpolate
#-----Plotbot Helper Functions-----\

def time_clip(datetime_array, start_time, end_time):
    """
    Return indices of points within a specified time range.
    
    Parameters
    ----------
    datetime_array : array-like
        Array of datetime64 values
    start_time : str
        Start time in format YYYY-MM-DD/HH:MM:SS.mmm
    end_time : str
        End time in format YYYY-MM-DD/HH:MM:SS.mmm
        
    Returns
    -------
    numpy.ndarray
        Array of indices for points in the time range.
    """
    # Log input time range
    print_manager.time_input("time_clip", [start_time, end_time])
    
    if datetime_array is None or len(datetime_array) == 0:
        print_manager.warning(f"❌ time_clip received empty datetime_array!")
        # Log empty output
        print_manager.time_output("time_clip", "empty_array")
        return np.array([])
    
    # Log original datetime_array range for comparison
    if len(datetime_array) > 0:
        print_manager.time_tracking(f"Original datetime_array range: {datetime_array[0]} to {datetime_array[-1]}")
    
    # Parse times without timezone info
    try:
        start_dt = np.datetime64(parse(start_time))
        # Add 1 microsecond to end time to include points right up to the boundary
        end_dt = np.datetime64(parse(end_time)) + np.timedelta64(1, 'us')
        
        # Log the parsed datetime objects
        print_manager.time_tracking(f"Parsed start_dt: {start_dt}, end_dt: {end_dt}")
    except Exception as e:
        print_manager.warning(f"❌ Error parsing time range: {e}")
        print_manager.time_output("time_clip", "parse_error")
        return np.array([])
    
    # Handle different array shapes - spectral data has 2D time array
    if isinstance(datetime_array[0], (list, np.ndarray)):
        if isinstance(datetime_array[0][0], (str, np.datetime64)):
            print_manager.time_tracking(f"Detected 2D datetime array, using first column")
            datetime_array = datetime_array[:,0]
    
    print_manager.custom_debug(f"🔍 Time clipping: {start_time} to {end_time}")
    print_manager.custom_debug(f"🔍 Data time range: {datetime_array[0]} to {datetime_array[-1]}")
    
    # CUSTOM DEBUG: Add more debug output for comparison
    print_manager.debug(f"DETAILED TIME CLIP - Start comparison: {start_dt} vs {datetime_array[0]}")
    print_manager.debug(f"DETAILED TIME CLIP - End comparison: {end_dt} vs {datetime_array[-1]}")
    
    # Find indices where time is within range
    try:
        # Get indices within range
        within_start = datetime_array >= start_dt
        within_end = datetime_array < end_dt
        
        # CUSTOM DEBUG: Print first few results of comparison
        print_manager.debug(f"DETAILED TIME CLIP - First 3 within_start results: {within_start[:3]}")
        print_manager.debug(f"DETAILED TIME CLIP - Last 3 within_start results: {within_start[-3:]}")
        print_manager.debug(f"DETAILED TIME CLIP - First 3 within_end results: {within_end[:3]}")
        print_manager.debug(f"DETAILED TIME CLIP - Last 3 within_end results: {within_end[-3:]}")
        
        indices = np.where((within_start) & (within_end))[0]
        
        print_manager.custom_debug(f"🔍 Time clip found {len(indices)} points in range")
        
        # CUSTOM DEBUG: Print summary of results
        print_manager.debug(f"DETAILED TIME CLIP - Total points in datetime_array: {len(datetime_array)}")
        print_manager.debug(f"DETAILED TIME CLIP - Points >= start_dt: {np.sum(within_start)}")
        print_manager.debug(f"DETAILED TIME CLIP - Points < end_dt: {np.sum(within_end)}")
        print_manager.debug(f"DETAILED TIME CLIP - Points in range: {len(indices)}")
        
        # Time tracking for result details
        if len(indices) == 0:
            print_manager.warning(f"⚠️ No data points found in time range {start_time} to {end_time}!")
            print_manager.time_tracking(f"No matching points found between {start_dt} and {end_dt}")
        elif len(indices) > 0:
            first_time = datetime_array[indices[0]]
            last_time = datetime_array[indices[-1]]
            print_manager.custom_debug(f"🔍 First point: {first_time}, Last point: {last_time}")
            print_manager.time_tracking(f"Found {len(indices)} points from {first_time} to {last_time}")
        
        # Log output
        print_manager.time_output("time_clip", [
            str(datetime_array[indices[0]]) if len(indices) > 0 else "empty", 
            str(datetime_array[indices[-1]]) if len(indices) > 0 else "empty"
        ])
        
        return indices
    except TypeError as e:
        print_manager.warning(f"❌ Error comparing time arrays: {e}")
        print_manager.time_output("time_clip", "type_error")
        return np.array([])

# Helper function to parse axis specification
def parse_axis_spec(spec):
    """Convert axis specification to (number, is_right) tuple."""
    spec = str(spec)
    is_right = spec.endswith('r')
    num = int(spec.rstrip('r'))
    return num, is_right
    
def resample(data, times, new_times): #Currently unused
    ###interpolate data to times from data2
    interpol_f = interpolate.interp1d(times, data,fill_value="extrapolate")
    new_data1 = interpol_f(new_times)    
    return new_times, new_data1

def debug_plot_variable(var, request, print_manager):
        """Debug function to print detailed information about a plot variable"""
        print_manager.debug(f"\nDEBUG:")
        print_manager.debug(f"var: {var}")
        print_manager.debug(f"var type: {type(var)}")
        print_manager.debug(f"var.datetime_array type: {type(var.datetime_array)}")
        
        # Protect against None values in debug printing
        if var is not None and var.datetime_array is not None and len(var.datetime_array) > 0:
            print_manager.debug(f"First element type: {type(var.datetime_array[0])}")
            print_manager.debug(f"First element: {var.datetime_array[0]}")
            print_manager.debug(f"Time range: {var.datetime_array[0]} to {var.datetime_array[-1]}")
        else:
            print_manager.debug("No datetime array available")
        
        if hasattr(var, 'data'):
            print_manager.debug(f"var.data type: {type(var.data)}")
            print_manager.debug(f"var.data shape: {np.array(var.data).shape if hasattr(var.data, 'shape') else 'no shape'}")

        # Verify we have good data
        print_manager.debug(f"\nVariable verification for {request['class_name']}.{request['subclass_name']}:")
        print_manager.debug(f"Plot attributes example:")
        if var is not None:
            print_manager.debug(f"- Color: {var.color}")
            print_manager.debug(f"- Y-label: {var.y_label}")
            print_manager.debug(f"- Legend: {var.legend_label}")
        else:
            print_manager.debug("No plot attributes available - data is None")

#FITS Code Functions (currently unused)
def resample(data, times, new_times):
    ###interpolate data to times from data2
    interpol_f = interpolate.interp1d(times, data,fill_value="extrapolate")
    new_data1 = interpol_f(new_times)    
    return new_times, new_data1
