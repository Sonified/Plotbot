#plotbot_main.py

import time as timer
from functools import wraps

def timer_decorator(timer_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timer.perf_counter()
            result = func(*args, **kwargs)
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"⏱️ [{timer_name}] {func.__name__}: {duration_ms:.2f}ms")
            return result
        return wrapper
    return decorator

print("\nImporting libraries, this may take a moment. Hold tight... \n")

# --- STANDARD LIBRARIES AND UTILITIES ---
import sys
import os
import re
from getpass import getpass
from collections import defaultdict, namedtuple
from typing import Dict, List, Optional
print("✅ Imported standard libraries and utilities.")

# --- SCIENTIFIC COMPUTING LIBRARIES ---
# MOVED TO FUNCTION LEVEL: Heavy imports moved inside plotbot() function for faster startup
# import numpy as np
# import pandas as pd
# import scipy
# from scipy import stats
print("✅ Deferred numpy, pandas, and scipy libraries (loaded when needed).")

# --- PLOTTING LIBRARIES ---
# MOVED TO FUNCTION LEVEL: Heavy imports moved inside plotbot() function for faster startup
# import matplotlib
# Enhanced plt with options is imported from __init__.py
# import matplotlib.colors as colors
# import matplotlib.dates as mdates
# import matplotlib.ticker as mticker
print("✅ Deferred matplotlib libraries (loaded when needed).")

# --- DATA HANDLING AND WEB ---
import cdflib
try:
    from cdflib.epochs_astropy import CDFAstropy as cdfepoch
except ImportError:
    print("Using cdflib.cdfepoch")
    from cdflib import cdfepoch
import bs4  # Import the module for version checking
from bs4 import BeautifulSoup  # Import the class for HTML parsing
import requests
import dateutil
from dateutil.parser import parse as dateutil_parse
from datetime import datetime, timedelta, timezone, time
print("✅ Imported cdflib, BeautifulSoup, requests, dateutil, and datetime libraries.")
# ----------------------------------------


from .print_manager import print_manager
from .server_access import server_access
from .data_tracker import global_tracker
from .data_cubby import data_cubby
from .data_download_berkeley import download_berkeley_data
from .data_import import import_data_function
from .plot_manager import plot_manager
from .multiplot_options import plt, MultiplotOptions
from .get_data import get_data  # Add get_data import

from .data_classes.data_types import data_types
from . import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton import proton
from .data_classes.psp_proton_hr import proton_hr
from .data_classes.psp_qtn_classes import psp_qtn
from .get_encounter import get_encounter_number
from .time_utils import get_needed_6hour_blocks, daterange
from .plotbot_helpers import time_clip, parse_axis_spec, resample, debug_plot_variable

#====================================================================
# FUNCTION: plotbot - Core plotting function for time series data
#====================================================================
@timer_decorator("TIMER_PLOTBOT_ENTRY")
def plotbot(trange, *args):
    """Plot multiple time series with shared x-axis and optional right y-axes."""
    
    # LAZY IMPORTS: Load heavy scientific libraries only when plotting
    print_manager.status("🤖 Plotbot starting (loading scientific libraries)...")
    
    import numpy as np
    import pandas as pd
    import scipy
    from scipy import stats
    import matplotlib
    import matplotlib.colors as colors
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker
    
    from collections import defaultdict
    import matplotlib.pyplot as mpl_plt
    # mpl_plt.rcParams['font.size'] = 8
    
    print_manager.status("🤖 Plotbot libraries loaded, proceeding...")
    
    # 🚀 CRITICAL FIX: Clear TimeRangeTracker to prevent stale data from interfering with CLIP ONCE optimization
    from .time_utils import TimeRangeTracker
    TimeRangeTracker.clear_trange()
    
    # Validate time range using dateutil.parser for flexibility
    try:
        plot_start_time = dateutil_parse(trange[0]).replace(tzinfo=timezone.utc)
        plot_end_time = dateutil_parse(trange[1]).replace(tzinfo=timezone.utc)
    except Exception as e:
        print(f"Oops! 🤗 Could not parse time range strings: {trange}. Error: {e}")
        return False

    if plot_start_time >= plot_end_time:    # Validate time range order
        print(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
        return False

    # Validate argument pairs
    if len(args) % 2 != 0:
        print("\nOops! 🤗 Arguments must be in pairs of (data, axis_number).")
        print("\nFor example:")
        print("plotbot(trange,")
        print("        data1, 1,")
        print("        data2, 2,")
        print("        data3, '2r')")  # Show that right axis is possible
        print("\nCheck your arguments and try again!")
        return False
        
    # Additional validation for data types
    for i in range(0, len(args), 2):
        if not hasattr(args[i], 'data_type'):
            print(f"\nOops! 🤗 Argument {i+1} doesn't look like a plottable data object.")
            print("Start with trange, then each odd-numbered argument must be a data class e.g. mag_rtn_4sa.br")
            print("Each even-numbered argument must be an axis specification (number or string).")
            print("Note: 1 for left axis, '1r' for right axis")
            print("A well-structured example: plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 2, mag_rtn_4sa.bn, '2r')")
            return False
            
        if not (isinstance(args[i+1], (int, str))):
            print(f"\nOops! 🤗 Axis specification at position {i+2} must be a number or string.")
            print("Note: 1 for left axis, '1r' for right axis")
            print("A well-structured example: plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 2, mag_rtn_4sa.bn, '2r')")
            return False

    #====================================================================
    # INITIALIZE DATA STRUCTURES
    #====================================================================
    plot_requests = []              # Stores metadata for each variable to be plotted (data type, class info, axis)
    required_data_types = set()     # Tracks unique data types needed across all variables
    subclasses_by_type = dict()     # Initialize empty dictionary to store subclass lists
    subclasses_by_type = defaultdict(list, subclasses_by_type)  # Auto-creates empty lists for new data types
    
    #====================================================================
    # PROCESS VARIABLE ARGUMENTS AND BUILD DATA STRUCTURES
    #====================================================================
    for i in range(0, len(args), 2):
        var = args[i]
        axis_spec = args[i+1]
        
        # Debug information about the variable being processed
        print_manager.variable_testing(f"DEBUG - Processing variable {i//2 + 1}:")
        print_manager.variable_testing(f"  Type: {type(var)}")
        print_manager.variable_testing(f"  Class name: {var.class_name}")
        print_manager.variable_testing(f"  Subclass name: {var.subclass_name}")
        print_manager.variable_testing(f"  Data type: {var.data_type}")
        print_manager.variable_testing(f"  Variable ID: {id(var)}")
        print_manager.variable_testing(f"  Has datetime_array: {hasattr(var, 'datetime_array')}")
        
        if hasattr(var, 'datetime_array') and var.datetime_array is not None:
            try:
                print_manager.variable_testing(f"  datetime_array length: {len(var.datetime_array)}")
            except:
                print_manager.variable_testing("  Could not get datetime_array length")
        
        # Try to display some data values directly without checking for a values attribute
        try:
            if len(var) > 0:
                print_manager.variable_testing(f"  First few elements: {var[:3]}")
        except Exception as e:
            pass  # Silently ignore any errors when trying to show elements
        
        # Create a unique identifier that includes object identity
        var_id = f"{var.class_name}.{var.subclass_name}_{id(var)}"
        print_manager.variable_testing(f"  Unique identifier: {var_id}")
        
        # Add variable testing print to see data types being processed
        print_manager.variable_testing(f"Processing variable: {var.class_name}.{var.subclass_name}, data_type: {var.data_type}")
        
        # Store the request
        plot_requests.append({
            'data_type requested for plotbot': var.data_type,
            'class_name': var.class_name,
            'subclass_name': var.subclass_name,
            'axis_spec': axis_spec
        })
        
        # Also capture unique identity for later use
        var_id = f"{var.class_name}.{var.subclass_name}_{id(var)}"
        print_manager.variable_testing(f"  Variable unique ID: {var_id}")
        
        required_data_types.add(var.data_type)
        subclasses_by_type[var.data_type].append(var.subclass_name)
        
    # Print the data types being requested
    print_manager.variable_testing(f"Data types requested: {required_data_types}")
    
    #------------------ Print Data Summary -------------------------#
    for data_type in required_data_types:    # Summarize variables by type
        subclasses = subclasses_by_type[data_type]
        print_manager.status(f"🛰️ {data_type} - acquiring variables: {', '.join(subclasses)}")

    # print_manager.status(" ")    # Add spacing between sections

    #====================================================================
    # PHASE 1: HANDLE CUSTOM VARIABLES AND THEIR SOURCE DATA
    #====================================================================
    custom_vars = []
    for request in plot_requests:
        if request['data_type requested for plotbot'] == 'custom_data_type':
            print_manager.variable_testing(f"Found custom variable request: {request['class_name']}.{request['subclass_name']}")
            class_instance = data_cubby.grab(request['class_name'])
            if class_instance:
                var = class_instance.get_subclass(request['subclass_name'])
                if var is not None:
                    custom_vars.append((var, request['subclass_name']))
                    print_manager.custom_debug(f"Added custom variable: {request['subclass_name']}\n")

    # Process custom variables and their source data
    for var, name in custom_vars:
        if hasattr(var, 'source_var') and var.source_var is not None:
            base_vars = []
            for src_var in var.source_var:
                if hasattr(src_var, 'class_name') and src_var.class_name != 'custom_class' and src_var.data_type != 'custom_data_type':
                    base_vars.append(src_var)
                    print_manager.test(f"Adding source variable for data download: {src_var.class_name}.{src_var.subclass_name}")
            
            # Download fresh data for base variables
            if base_vars:
                print_manager.status(f"📤 Custom variable '{name}' requires data for calculation")
                get_data(trange, *base_vars)
                
                # Update the custom variable
                if hasattr(var, 'update'):
                    updated_var = var.update(trange)
                    if updated_var is not None:
                        print_manager.custom_debug(f"✅ Successfully updated variable '{name}'")
                    else:
                        print_manager.warning(f"Warning: Failed to update '{name}'")

    print_manager.status(" ")    # Add spacing between sections

    #====================================================================
    # PHASE 2: LOAD STANDARD (NON-CUSTOM) DATA USING get_data
    #====================================================================
    # loaded_data_objects = {}
    # print_manager.debug("--- [plotbot] STARTING PHASE 2: Load Standard Data ---")
    # for data_type in required_data_types:
    #     # Skip if it's a custom type already handled
    #     if data_type == 'custom_data_type':
    #         continue
        
    #     print_manager.debug(f"--- [plotbot] Calling get_data for data_type: '{data_type}' ---")
    #     loaded_data = get_data(trange, data_type)  # Call get_data for each required type
    #     print_manager.debug(f"--- [plotbot] Returned from get_data for data_type: '{data_type}'. Result type: {type(loaded_data)} ---")
    #     loaded_data_objects[data_type] = loaded_data
    #     # Debug: Print if data was loaded successfully or not
    #     if loaded_data is not None and hasattr(loaded_data, 'data') and loaded_data.data:
    #         print_manager.variable_testing(f"✅ Successfully loaded data for {data_type}")
    #     else:
    #         print_manager.warning(f"⚠️ Failed to load data for {data_type}")
            
    # print_manager.debug("--- [plotbot] FINISHED PHASE 2: Load Standard Data ---")

    # print_manager.status(" ")    # Add spacing between sections

    #====================================================================
    # PHASE 3: HANDLE REGULAR VARIABLES
    #====================================================================
    regular_vars = []
    for request in plot_requests:
        if request['data_type requested for plotbot'] != 'custom_data_type':
            # print_manager.variable_testing(f"Found regular variable request: {request['class_name']}.{request['subclass_name']}") # User requested this to be less verbose
            class_instance = data_cubby.grab(request['class_name'])
            if class_instance:
                var = class_instance.get_subclass(request['subclass_name'])
                if var is not None:
                    regular_vars.append(var)
                    # print_manager.custom_debug(f"Added regular variable: {request['class_name']}.{request['subclass_name']}\n") # User requested this to be less verbose

    # NEW: Smart caching check
    if regular_vars:
        # Data Cache Check - see if we already have data for this time range
        timer_entry = timer.perf_counter()
        timer_start = timer.perf_counter()  # <-- Ensure timer_start is always initialized
        if regular_vars and hasattr(regular_vars[0], 'data_type'):
            if regular_vars[0].data_type == 'mag_RTN_4sa':
                print_manager.speed_test(f'[TIMER_MAG_2] Data Cache Check: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
            elif regular_vars[0].data_type == 'psp_orbit_data':
                print_manager.speed_test(f'[TIMER_ORBIT_2] Data Cache Check: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
        need_data_loading = False
        
        for var in regular_vars:
            data_type = var.data_type
            # DEBUGGING: Check tracker state for each variable
            print_manager.speed_test(f"DATA CACHE CHECK: var={var.class_name}.{var.subclass_name}, data_type={data_type}")
            print_manager.speed_test(f"TRACKER STATE: {global_tracker.calculated_ranges}")
            
            # Construct a unique identifier for the variable instance for tracker
            # This should align with how it's stored/checked elsewhere if instance-specific tracking is used
            # For now, assuming data_type and trange is enough for global_tracker.is_calculation_needed
            calculation_needed = global_tracker.is_calculation_needed(trange, data_type)
            print_manager.speed_test(f"DATA CACHE CHECK RESULT: data_type={data_type}, calculation_needed={calculation_needed}")
            
            if not calculation_needed:
                print_manager.variable_testing(f"Data for {data_type} in trange {trange} already exists according to global_tracker.")
                continue  # Data exists, skip this variable
            else:
                print_manager.variable_testing(f"Data for {data_type} in trange {trange} needs loading according to global_tracker.")
                need_data_loading = True
                break
        
        timer_end = timer.perf_counter()
        duration_ms = (timer_end - timer_start) * 1000
        print_manager.speed_test(f"[TIMER_EARLY_OPTIMIZATION] Data Cache Check: {duration_ms:.2f}ms")
        
        if need_data_loading:
            if regular_vars and hasattr(regular_vars[0], 'data_type'):
                if regular_vars[0].data_type == 'mag_RTN_4sa':
                    print_manager.speed_test(f'[TIMER_MAG_3] get_data() call: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
                elif regular_vars[0].data_type == 'psp_orbit_data':
                    print_manager.speed_test(f'[TIMER_ORBIT_3] get_data() call: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
            print_manager.status(f"📥 Acquiring data for {len(regular_vars)} regular variables...")
            # Set TimeRangeTracker for user's original request before get_data call
            from .time_utils import TimeRangeTracker
            TimeRangeTracker.set_current_trange(trange)
            timer_start = timer.perf_counter()
            get_data(trange, *regular_vars)
            timer_end = timer.perf_counter()
            duration_ms = (timer_end - timer_start) * 1000
            print_manager.speed_test(f"[TIMER_GET_DATA_CALL] get_data() call: {duration_ms:.2f}ms")
        else:
            print_manager.status(f"✅ All data already cached for {len(regular_vars)} regular variables in the specified trange.")
            # Even for cached data, update TimeRangeTracker so requested_trange gets set correctly
            from .time_utils import TimeRangeTracker
            TimeRangeTracker.set_current_trange(trange)

    #------------------ Prepare Plot Variables ------------------#
    plot_vars = []
    
    # Process plot requests and collect variables
    print_manager.dependency_management("\n=== Preparing variables for plotting ===")
    for request in plot_requests:
        print_manager.dependency_management(f"Processing request: {request['class_name']}.{request['subclass_name']}")
        class_instance = data_cubby.grab(request['class_name'])     # Retrieve class instance for this plot request
        print_manager.dependency_management(f"Retrieved class instance: {class_instance.__class__.__name__}")
        
        var = class_instance.get_subclass(request['subclass_name']) # Get specific component to plot
        print_manager.dependency_management(f"Retrieved variable: {request['class_name']}.{request['subclass_name']}, data_type: {getattr(var, 'data_type', 'unknown')}")
        
        # This is where we'd need to handle custom variables (ensure they have the right attributes)
        if hasattr(var, 'data_type'):
            print_manager.dependency_management(f"Variable data_type: {var.data_type}")
        
        plot_vars.append((var, request['axis_spec']))               # Store variable and its axis specification
        
        debug_plot_variable(var, request, print_manager)

    # Group variables by axis
    axis_groups = defaultdict(list)
    for var, axis_spec in plot_vars:
        axis_num, is_right = parse_axis_spec(axis_spec)
        axis_groups[(axis_num, is_right)].append(var)

    # Create figure and axes
    num_subplots = max(axis_num for axis_num, _ in axis_groups.keys())
    fig, axs = plt.subplots(num_subplots, 1, sharex=True, figsize=(12, 2 * num_subplots))
    if num_subplots == 1:
        axs = [axs]  # Keep this line
    plt.subplots_adjust(right=0.75)

    # Apply title if set in options
    if hasattr(plt.options, 'use_single_title') and plt.options.use_single_title:
        if hasattr(plt.options, 'single_title_text') and plt.options.single_title_text:
            fig.suptitle(plt.options.single_title_text) 
            print_manager.debug(f"Setting title from plt.options: {plt.options.single_title_text}")
    
    # After parsing trange:
    # plot_start_time = dateutil_parse(trange[0]).replace(tzinfo=timezone.utc)
    # plot_end_time = dateutil_parse(trange[1]).replace(tzinfo=timezone.utc)
    # Use plot_start_time/plot_end_time everywhere for datetime logic
    # In ax.set_xlim and date_format, use plot_start_time/plot_end_time
    # Remove any use of start_time/end_time for datetime logic in the plotting section

    #====================================================================
    # PLOT VARIABLES ON APPROPRIATE AXES
    #====================================================================
    timer_start = timer.perf_counter()
    if args and hasattr(args[0], 'data_type'):
        if args[0].data_type == 'mag_RTN_4sa':
            print_manager.speed_test(f'[TIMER_MAG_6] Plotting section: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
        elif args[0].data_type == 'psp_orbit_data':
            print_manager.speed_test(f'[TIMER_ORBIT_6] Plotting section: {(timer.perf_counter() - timer_entry)*1000:.2f}ms')
    for axis_index in range(1, num_subplots + 1):  # Iterate through each subplot (1-based indexing)
        ax = axs[axis_index - 1]                   # Get current subplot axis (0-based array indexing)
        ax_right = None                            # Secondary y-axis for dual-scale plots
        legend_handles = []                        # Store plot lines for legend creation
        legend_labels = []                         # Store corresponding legend text
        has_right_axis = False                     # Track if we need a secondary y-axis
        empty_plot = True                          # Assume empty until we successfully plot data

        #====================================================================
        # PROCESS EACH AXIS GROUP (PRIMARY/SECONDARY Y-AXIS)
        #====================================================================
        for (axis_num, is_right), variables in axis_groups.items():  # Process each group of variables for this axis
            if axis_num != axis_index:  # Skip groups meant for other subplots
                continue

            if is_right and ax_right is None:  # Create secondary y-axis if needed
                ax_right = ax.twinx()          # twinx() creates shared x-axis
                has_right_axis = True
            
            #====================================================================
            # PLOT INDIVIDUAL VARIABLES WITHIN AXIS GROUP
            #====================================================================
            for var in variables:              # Plot each variable in the group
                plot_ax = ax_right if is_right else ax  # Choose primary or secondary y-axis
                print_manager.status(f"📈 Plotting {var.class_name}.{var.subclass_name}")

                # Validate data exists and has content
                try:
                    # print_manager.debug(f"[PLOT DEBUG] id(var)={id(var)}, type(var)={type(var)}") # Commented out
                    # if hasattr(var, '__len__'): # Commented out
                    #     print_manager.debug(f"[PLOT DEBUG] len(var)={len(var)}") # Commented out
                    # if hasattr(var, 'datetime_array') and var.datetime_array is not None and len(var.datetime_array) > 0: # Commented out
                    #     arr = var.datetime_array # Commented out
                    #     print_manager.debug(f"[PLOT DEBUG] datetime_array: min={arr[0]}, max={arr[-1]}, len={len(arr)}") # Commented out
                    # print_manager.debug(f"[PLOT DEBUG] requested trange: {trange}") # Commented out
                    pass # Added pass for empty try block
                except Exception as e:
                    # print_manager.debug(f"[PLOT DEBUG] Error printing debug info: {e}") # Commented out
                    pass # Added pass for empty except block
                if var is None or (hasattr(var, 'all_data') and np.array(var.all_data).size == 0) or var.datetime_array is None:
                    # print_manager.debug(f"No data available for {var.class_name}.{var.subclass_name} in time range")
                    continue

                empty_plot = False                # We have valid data to plot

                #====================================================================
                # PLOT TIME SERIES DATA (e.g. MAG, PROTON MOMENTS)
                #====================================================================
                if var.plot_type == 'time_series':  # Handle standard time series data
                    
                    #====================================================================
                    # DATA VERIFICATION
                    #====================================================================
                    # Check if datetime array exists and has data
                    if var.datetime_array is None or len(var.datetime_array) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No datetime array available")
                        continue

                    # Check if any data points fall within the specified time range
                    # Use raw datetime array for time clipping, not the property (which is now clipped)
                    raw_datetime_array = var.plot_options.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                    time_indices = time_clip(raw_datetime_array, trange[0], trange[1])
                    if len(time_indices) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No valid time indices found")
                        continue

                    # Convert variable data to numpy array for processing
                    data = var.all_data

                    #====================================================================
                    # PROCEED WITH PLOTTING
                    #====================================================================
                    # Only continue if all verification checks passed
                    if not empty_plot:
                        # Use raw datetime array for clipping to match time_indices calculation
                        datetime_clipped = raw_datetime_array[time_indices]  # Get timestamps within range
                        
                        # Handle scalar quantities (single line)
                        if data.ndim == 1:
                            data_clipped = data[time_indices]  # Slice data for time range
                            if np.all(np.isnan(data_clipped)):  # Skip if all data points are NaN
                                empty_plot = True
                                print_manager.debug("empty_plot = True - All data points are NaN")
                                continue
                                
                            line, = plot_ax.plot(  # Create single line plot
                                datetime_clipped,
                                data_clipped,
                                label=var.legend_label,
                                color=var.color,
                                linewidth=var.line_width,
                                linestyle=var.line_style
                            )
                            legend_handles.append(line)  # Store line for legend
                            legend_labels.append(var.legend_label)  # Store label for legend
                            
                        else:  # Handle vector quantities (e.g., 3D magnetic field)
                            data_clipped = data[:,time_indices]  # Slice data for time range
                            
                            for i in range(data_clipped.shape[0]):  # Plot each vector component
                                if np.all(np.isnan(data_clipped[i])):  # Skip components that are all NaN
                                    print_manager.debug(f"Component {i} is all NaNs - skipping")
                                    continue
                                    
                                line, = plot_ax.plot(  # Create line plot with component-specific styling
                                    datetime_clipped,
                                    data_clipped[i],
                                    label=var.legend_label[i] if isinstance(var.legend_label, list) else var.legend_label,
                                    color=var.color[i] if isinstance(var.color, list) else var.color,
                                    linewidth=var.line_width[i] if isinstance(var.line_width, list) else var.line_width,
                                    linestyle=var.line_style[i] if isinstance(var.line_style, list) else var.line_style
                                )
                                legend_handles.append(line)  # Store line for legend creation
                                legend_labels.append(var.legend_label[i] if isinstance(var.legend_label, list) else var.legend_label)
                        plot_ax.set_ylabel(var.y_label)  # Set y-axis label
                        plot_ax.set_yscale(var.y_scale)  # Set linear/log scale
                        if var.y_limit:  # Set y-axis limits if specified
                            plot_ax.set_ylim(var.y_limit)

                #====================================================================
                # PLOT SCATTER DATA (e.g. FITS parameters) #Eventually this can be refactored and many functions from all types can be combined
                #====================================================================
                elif var.plot_type == 'scatter': # Added block for scatter plots
                    # DATA VERIFICATION (similar to time_series)
                    if var.datetime_array is None or len(var.datetime_array) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No datetime array available (scatter)")
                        continue

                    # Use raw datetime array for time clipping, not the property (which is now clipped)
                    raw_datetime_array = var.plot_options.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                    time_indices = time_clip(raw_datetime_array, trange[0], trange[1])
                    if len(time_indices) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No valid time indices found (scatter)")
                        continue

                    data = var.all_data # Ensure data is numpy array

                    # PROCEED WITH PLOTTING
                    if not empty_plot:
                        # Use raw datetime array for clipping to match time_indices calculation
                        datetime_clipped = raw_datetime_array[time_indices]

                        # Handle scalar quantities
                        if data.ndim == 1:
                            data_clipped = data[time_indices]
                            if np.all(np.isnan(data_clipped)):
                                empty_plot = True
                                print_manager.debug("empty_plot = True - All data points are NaN (scatter)")
                                continue

                            # Use scatter plot specific attributes
                            scatter_plot = plot_ax.scatter(
                                datetime_clipped,
                                data_clipped,
                                label=getattr(var, 'legend_label', None),
                                color=getattr(var, 'color', 'black'), # Default to black if not set
                                marker=getattr(var, 'marker_style', 'o'), # Default to circle
                                s=getattr(var, 'marker_size', 20), # Default size 20
                                alpha=getattr(var, 'alpha', 0.7) # Default alpha 0.7
                            )
                            # Note: Appending scatter_plot (PathCollection) to legend_handles might not work perfectly for standard legends.
                            # May need proxy artists later if legend appearance is incorrect.
                            legend_handles.append(scatter_plot)
                            if hasattr(var, 'legend_label'):
                                legend_labels.append(var.legend_label)

                        # Common y-axis settings for scatter plots
                        plot_ax.set_ylabel(getattr(var, 'y_label', ''))
                        plot_ax.set_yscale(getattr(var, 'y_scale', 'linear'))
                        if hasattr(var, 'y_limit') and var.y_limit:  # ✨ y-limit scatter plot handling
                            plot_ax.set_ylim(var.y_limit)

                #====================================================================
                # PLOT SPECTRAL DATA (e.g. ELECTRON PAD SPECTROGRAMS)
                #====================================================================
                elif var.plot_type == 'spectral':  # Handle spectral/colormap data
                    #====================================================================
                    # Verify data availability and validity
                    #====================================================================
                    if var.datetime_array is None or len(var.datetime_array) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No datetime array available (spectral)")
                        continue

                    # Use raw datetime array for time clipping, not the property (which is now clipped)
                    raw_datetime_array = var.plot_options.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                    time_indices = time_clip(raw_datetime_array, trange[0], trange[1])  # Get time range indices
                    if len(time_indices) == 0:
                        empty_plot = True
                        print_manager.debug("empty_plot = True - No valid time indices found (spectral)")
                        continue
                    
                    # Use all_data property for internal plotting (performance optimization)
                    data = var.all_data  # Get full unclipped data for internal processing
                    
                    # For spectral data, ensure indices are valid for the data array
                    max_valid_index = data.shape[0] - 1
                    if len(time_indices) > 0 and time_indices[-1] > max_valid_index:
                        print_manager.debug(f"Adjusting time indices for spectral data: max index {time_indices[-1]} > data length {data.shape[0]}")
                        time_indices = time_indices[time_indices <= max_valid_index]
                        if len(time_indices) == 0:
                            empty_plot = True
                            print_manager.debug("empty_plot = True - No valid time indices after adjustment (spectral)")
                            continue
                    
                    data_clipped = data[time_indices]  # Slice data for time range
                    if np.all(np.isnan(data_clipped)):  # Check for all NaN values
                        empty_plot = True
                        print_manager.debug("empty_plot = True - All data points in time window are NaN (spectral)")
                        continue
                        
                    #====================================================================
                    # Proceed with spectral plotting
                    #====================================================================
                    if not empty_plot:  # Create spectral plot only if we have valid data
                        # For datetime_clipped, also handle potential mismatched dimensions
                        # Use raw datetime array for clipping to match time_indices calculation
                        if raw_datetime_array.ndim == 2:
                            # Keep 2D for pcolormesh compatibility with additional_data
                            datetime_clipped = raw_datetime_array[time_indices, :]
                        else:
                            datetime_clipped = raw_datetime_array[time_indices]
                        
                        # Handle additional_data similarly
                        if hasattr(var, 'additional_data') and var.additional_data is not None:
                            additional_data_clipped = var.additional_data[time_indices] if len(var.additional_data) > max(time_indices) else var.additional_data
                        else:
                            additional_data_clipped = None

                        ax.set_ylabel(var.y_label)  # Set y-axis properties
                        ax.set_yscale(var.y_scale)
                        if var.y_limit:
                            ax.set_ylim(var.y_limit)

                        # Configure color scaling
                        if var.colorbar_scale == 'log':  # Set up logarithmic color scaling
                            norm = colors.LogNorm(vmin=var.colorbar_limits[0], vmax=var.colorbar_limits[1]) if var.colorbar_limits else colors.LogNorm()
                        elif var.colorbar_scale == 'linear':  # Set up linear color scaling
                            norm = colors.Normalize(vmin=var.colorbar_limits[0], vmax=var.colorbar_limits[1]) if var.colorbar_limits else None
                        else:
                            norm = None

                        # Create spectral plot
                        if additional_data_clipped is not None:
                            im = ax.pcolormesh(  # Create 2D color plot
                                datetime_clipped,
                                additional_data_clipped,
                                data_clipped,
                                norm=norm,
                                cmap=var.colormap if hasattr(var, 'colormap') else None,
                                shading='auto'
                            )
                        else:
                            # If no additional_data, create a simple y-axis based on data shape
                            y_values = np.arange(data_clipped.shape[1]) if data_clipped.ndim > 1 else np.arange(len(data_clipped))
                            im = ax.pcolormesh(  # Create 2D color plot
                                datetime_clipped,
                                y_values,
                                data_clipped,
                                norm=norm,
                                cmap=var.colormap if hasattr(var, 'colormap') else None,
                                shading='auto'
                            )
                        
                        # Add and configure colorbar
                        pos = ax.get_position()  # Get plot position
                        cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])  # Create colorbar axes
                        cbar = plt.colorbar(im, cax=cax)  # Add colorbar
                        if hasattr(var, 'colorbar_label'):
                            cbar.set_label(var.colorbar_label)  # Set colorbar label if specified

            # ============================================================================
            # Handle empty plots
            # ============================================================================
            if empty_plot:
                print_manager.debug("Creating empty plot...")
                for (axis_num, is_right), variables in axis_groups.items():
                    if axis_num != axis_index:
                        continue
                    for i, var in enumerate(variables):
                        try:
                            # Single-line debug info with all critical information
                            debug_info = f"Var {i}: {var.class_name}.{var.subclass_name} | type={var.data_type}, plot={var.plot_type}, scale={var.y_scale}"
                            debug_info += f"{', y_limit=' + str(var.y_limit) if hasattr(var, 'y_limit') else ''}"
                            debug_info += f" | sources=[{', '.join(src_var.class_name + '(has_data=' + str(hasattr(src_var, 'datetime_array') and len(src_var.datetime_array) > 0) + ')' for src_var in var.source_var) if hasattr(var, 'source_var') and var.source_var is not None else 'none'}]" if var.data_type == 'custom_data_type' else ''
                            # Use raw datetime array for time clipping, not the property (which is now clipped)
                            raw_datetime_array = var.plot_options.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                            time_indices = time_clip(raw_datetime_array, trange[0], trange[1]) if hasattr(var, 'datetime_array') and var.datetime_array is not None else []
                            debug_info += f" | data: points={len(time_indices)}" + (f", shape={np.array(var)[time_indices].shape}, has_nans={np.isnan(np.array(var)[time_indices]).any()}" if len(time_indices) > 0 else " (no data in range)")
                            print_manager.debug(debug_info)
                        except Exception as e:
                            print_manager.debug(f"Error inspecting variable {i}: {str(e)}")
                
                ax.set_xlim(plot_start_time, plot_end_time)  # Set time range even if empty
                ax.text(0.5, 0.5, 'No Data Available',  # Add centered "No Data" message
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=12,
                    color='gray',
                    style='italic')
                
                # Try to set y-label even for empty plots
                print_manager.debug("Checking for y-label in variables...")
                label_set = False
                for (axis_num, is_right), variables in axis_groups.items():
                    if axis_num != axis_index:
                        continue
                    print_manager.debug(f"Checking axis group {axis_num}, {is_right}")
                    for var in variables:
                        print_manager.debug(f"Checking var: {var}")
                        print_manager.debug(f"Has y_label: {hasattr(var, 'y_label')}")
                        if var is not None and hasattr(var, 'y_label'):
                            print_manager.debug(f"Setting y-label to: {var.y_label}")
                            ax.set_ylabel(var.y_label)             # Set y-label if available
                            label_set = True
                            break
                    if label_set:
                        break

        # ============================================================================
        # Add Legend
        # ============================================================================
        if legend_handles:                                         # Add legend if we have plot handles
            if has_right_axis:                                     # Position legend based on axes layout
                ax.legend(legend_handles, legend_labels,
                          loc='center left', bbox_to_anchor=(1.095, 0.5))
            else:
                ax.legend(legend_handles, legend_labels,
                          loc='center left', bbox_to_anchor=(1.02, 0.5))

        # ============================================================================
        # Final Axis Adjustments
        # ============================================================================
        ax.margins(x=0)                                           # Remove padding on x-axis
        if ax_right:
            ax_right.margins(x=0)                                 # Remove padding on secondary y-axis
    
        # ============================================================================
        # Configure X-Axis
        # ============================================================================
        axs[-1].set_xlabel('Time')                                    # Add time label to bottom subplot
    
        def date_format(x, p):
            dt = mdates.num2date(x)
            
            # Calculate the total time range in minutes
            time_range_minutes = (plot_end_time - plot_start_time).total_seconds() / 60
            
            if dt.hour == 0 and dt.minute == 0:
                return dt.strftime('%b-%d').upper()                   # Format: MMM-DD
            elif time_range_minutes <= 5:  # For ranges <= 5 minutes
                return dt.strftime('%H:%M:%S')                        # Format: HH:MM:SS
            else:
                return dt.strftime('%H:%M')                           # Format: HH:MM
    
        axs[-1].xaxis.set_major_formatter(mticker.FuncFormatter(date_format))

        # ============================================================================
        # Add Date Label to lower right corner of plot
        # ============================================================================
        # Use dateutil_parse to handle different formats robustly, then format just the date part
        try:
            parsed_date = dateutil_parse(trange[0])
            plot_date = parsed_date.strftime('%Y-%m-%d')
            axs[-1].annotate(plot_date, xy=(1, -0.21), xycoords='axes fraction',  # Add date in lower right
                             ha='right', va='top', fontsize=12)
        except Exception as e:
            print_manager.warning(f"Could not parse date from trange[0] ('{trange[0]}') for annotation: {e}")

    timer_end = timer.perf_counter()
    duration_ms = (timer_end - timer_start) * 1000
    print_manager.speed_test(f"[TIMER_PLOTTING] Plotting section: {duration_ms:.2f}ms")
    
    plt.show()                                                    # Display the complete figure
    # return True

print('\n🤖 Plotbot Initialized')