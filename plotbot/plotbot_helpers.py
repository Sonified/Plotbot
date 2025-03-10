from .multiplot_options import plt  # Import our enhanced plt with options
import numpy as np
import cdflib
import os
import warnings
from datetime import datetime, timezone, timedelta
import pandas as pd
from dateutil.parser import parse
from scipy import interpolate
from .print_manager import print_manager
#-----Plotbot Helper Functions-----\

def time_clip(tarray, start, stop):
    """Find indices where time array is within the given range."""
    # Return empty array if input is None or empty
    if tarray is None or len(tarray) == 0:
        return np.array([])
        
    # Parse times without timezone info
    start_dt = np.datetime64(parse(start))
    # Add 1 microsecond to stop time to include points right up to the boundary
    stop_dt = np.datetime64(parse(stop)) + np.timedelta64(1, 'us')
    
    # Handle different array shapes - spectral data has 2D time array
    if isinstance(tarray[0], (list, np.ndarray)):
        if isinstance(tarray[0][0], (str, np.datetime64)):
            tarray = tarray[:,0]

    # Find indices where time is within range
    try:
        indices = np.where((tarray >= start_dt) & (tarray < stop_dt))[0]
        print_manager.debug(f"Found {len(indices)} points within range")
        if len(indices) > 0:
            print_manager.debug(f"Time range of selected points: {tarray[indices[0]]} to {tarray[indices[-1]]}")
        return indices
    except TypeError as e:
        print_manager.debug(f"Error comparing time arrays: {e}")
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
