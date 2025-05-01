"""
Plotbot helper functions for plotting and data processing.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, timezone
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
    
    # Parse times into aware Python datetime objects
    try:
        start_dt_aware = parse(start_time).replace(tzinfo=timezone.utc)
        # Use aware datetime for end comparison, maybe add timedelta directly if compatible
        # end_dt_aware = parse(end_time).replace(tzinfo=timezone.utc) + timedelta(microseconds=1) 
        # Let's try comparing up to *including* the end time first, without adding microseconds
        end_dt_aware = parse(end_time).replace(tzinfo=timezone.utc)
        
        # Log the parsed datetime objects
        print_manager.time_tracking(f"Parsed aware start_dt: {start_dt_aware}, end_dt: {end_dt_aware}")
    except Exception as e:
        print_manager.warning(f"❌ Error parsing time range: {e}")
        print_manager.time_output("time_clip", "parse_error")
        return np.array([])
    
    # Convert start/end times to timezone-aware numpy datetime64 for robust comparison
    try:
        # Fix: Use pandas to properly handle timezone conversion
        # Convert timezone-aware datetime to datetime64 through pandas
        start_dt_np = pd.Timestamp(start_dt_aware).to_datetime64()
        end_dt_np = pd.Timestamp(end_dt_aware).to_datetime64()
    except Exception as e:
        print_manager.error(f"❌ Failed to convert start/end times to np.datetime64: {e}")
        print_manager.time_output("time_clip", "error: time conversion failed")
        return np.array([]) # Return empty array if conversion fails
    
    # Ensure datetime_array is a numpy array for comparison
    datetime_array_np = np.asarray(datetime_array)
    if datetime_array_np.size == 0:
        print_manager.warning("Input datetime_array is empty. Cannot clip.")
        print_manager.time_output("time_clip", "empty input array")
        return np.array([])

    # Handle different array shapes - spectral data has 2D time array
    if datetime_array_np.ndim == 2 and isinstance(datetime_array_np[0,0], (datetime, np.datetime64)):
            print_manager.time_tracking(f"Detected 2D datetime array, using first column")
            datetime_array_np = datetime_array_np[:,0]
    
    print_manager.custom_debug(f"🔍 Time clipping: {start_time} to {end_time}")
    print_manager.custom_debug(f"🔍 Data time range: {datetime_array_np[0]} to {datetime_array_np[-1]}")
    
    # <<< ADDED DEBUG: Check dtypes and values before comparison >>>
    print_manager.debug(f"  [time_clip DEBUG] datetime_array_np dtype: {datetime_array_np.dtype}")
    print_manager.debug(f"  [time_clip DEBUG] start_dt_np dtype: {start_dt_np.dtype}, value: {start_dt_np}")
    print_manager.debug(f"  [time_clip DEBUG] end_dt_np dtype: {end_dt_np.dtype}, value: {end_dt_np}")
    if datetime_array_np.size > 0:
        print_manager.debug(f"  [time_clip DEBUG] datetime_array_np first: {datetime_array_np[0]}")
        print_manager.debug(f"  [time_clip DEBUG] datetime_array_np last: {datetime_array_np[-1]}")
    # <<< END ADDED DEBUG >>>
    
    # Perform comparison using numpy datetime64
    try:
        # <<< FIX: Ensure consistent dtype (e.g., nanoseconds) before comparison >>>
        datetime_array_ns = datetime_array_np.astype('datetime64[ns]')
        start_dt_ns = start_dt_np.astype('datetime64[ns]')
        end_dt_ns = end_dt_np.astype('datetime64[ns]')
        print_manager.debug(f"  [time_clip DEBUG] Comparing arrays cast to datetime64[ns]")
        
        indices = np.where((datetime_array_ns >= start_dt_ns) & 
                           (datetime_array_ns <= end_dt_ns))[0]
        print_manager.custom_debug(f"Successfully compared numpy datetime64 times, found {len(indices)} indices.")
    except TypeError as e:
        # This might happen if datetime_array_np contains incompatible types despite best efforts
        print_manager.warning(f"❌ TypeError during numpy time comparison: {e}. Returning empty.")
        print_manager.debug(f"  datetime_array_np dtype: {datetime_array_np.dtype}, first element: {datetime_array_np[0] if datetime_array_np.size > 0 else 'N/A'}")
        print_manager.debug(f"  start_dt_np: {start_dt_np}, end_dt_np: {end_dt_np}")
        indices = np.array([])
    except Exception as e_inner:
        print_manager.warning(f"❌ Unexpected error during numpy time comparison: {e_inner}. Returning empty.")
        indices = np.array([])

    # Log clipped indices
    if len(indices) > 0:
        print_manager.time_tracking(f"Clipped indices range from {indices[0]} to {indices[-1]}")

    # Time tracking for result details
    if len(indices) == 0:
        print_manager.warning(f"⚠️ No data points found in time range {start_time} to {end_time}!")
        print_manager.time_tracking(f"No matching points found between {start_dt_aware} and {end_dt_aware}")
    elif len(indices) > 0:
        first_time = datetime_array_np[indices[0]]
        last_time = datetime_array_np[indices[-1]]
        print_manager.custom_debug(f"🔍 First point: {first_time}, Last point: {last_time}")
        print_manager.time_tracking(f"Found {len(indices)} points from {first_time} to {last_time}")
    
    # Log output
    print_manager.time_output("time_clip", [
        str(datetime_array_np[indices[0]]) if len(indices) > 0 else "empty", 
        str(datetime_array_np[indices[-1]]) if len(indices) > 0 else "empty"
    ])
    
    return indices

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
