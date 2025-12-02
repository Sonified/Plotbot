# Import plotbot components with relative imports
# working title and colorbar positioning and styling, but broken data handling
from .data_cubby import data_cubby
from .data_tracker import global_tracker  
from .data_download_berkeley import download_berkeley_data
from .data_import import import_data_function
from .print_manager import print_manager, format_datetime_for_log
from .get_encounter import get_encounter_number
from .plotbot_helpers import time_clip
# Import specific functions from multiplot_helpers instead of using wildcard import
from .multiplot_helpers import get_plot_colors, apply_panel_color, apply_bottom_axis_color, validate_log_scale_limits
from .multiplot_options import plt, MultiplotOptions
from .ploptions import ploptions
# Import get_data for custom variables
from .get_data import get_data
# Import the XAxisPositionalDataMapper helper
from .x_axis_positional_data_helpers import XAxisPositionalDataMapper
# Import str_to_datetime from time_utils
from .time_utils import str_to_datetime
# Import perihelion helper
from .utils import get_perihelion_time

# Import standard libraries
import matplotlib.colors as colors
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from PIL import Image   
import matplotlib.pyplot as mpl_plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mticker

def debug_variable_time_ranges(var, trange, label=""):
    """Helper function to debug time range issues with variables."""
    if not hasattr(var, 'datetime_array') or var.datetime_array is None:
        print_manager.custom_debug(f"[DEBUG {label}] Variable has no datetime_array!")
        return
    
    var_start = var.datetime_array[0]
    var_end = var.datetime_array[-1]
    
    # Parse the trange into datetime objects
    if isinstance(trange, list) and len(trange) == 2:
        try:
            from dateutil.parser import parse
            req_start = parse(trange[0])
            req_end = parse(trange[1])
            
            # Convert to numpy datetime64 for comparison
            var_start_dt64 = np.datetime64(var_start)
            var_end_dt64 = np.datetime64(var_end)
            req_start_dt64 = np.datetime64(req_start)
            req_end_dt64 = np.datetime64(req_end)
            
            print_manager.custom_debug(f"[DEBUG {label}] Variable datetime range: {var_start} to {var_end}")
            print_manager.custom_debug(f"[DEBUG {label}] Requested time range: {req_start} to {req_end}")
            
            # Check for overlap
            has_overlap = (var_start_dt64 <= req_end_dt64 and var_end_dt64 >= req_start_dt64)
            print_manager.custom_debug(f"[DEBUG {label}] Time ranges overlap: {has_overlap}")
            
            # Get number of points that should be in range
            if has_overlap:
                # Determine overlap bounds
                overlap_start = max(var_start_dt64, req_start_dt64)
                overlap_end = min(var_end_dt64, req_end_dt64)
                
                # Count points in range
                indices = np.where((np.array(var.datetime_array) >= overlap_start) & 
                                  (np.array(var.datetime_array) <= overlap_end))[0]
                
                print_manager.custom_debug(f"[DEBUG {label}] Points in time range: {len(indices)}")
                if len(indices) == 0:
                    # More detailed examination
                    print_manager.custom_debug(f"[DEBUG {label}] First 5 datetime values: {var.datetime_array[:5]}")
                    print_manager.custom_debug(f"[DEBUG {label}] Last 5 datetime values: {var.datetime_array[-5:]}")
            else:
                print_manager.custom_debug(f"[DEBUG {label}] No overlap between time ranges!")
        except Exception as e:
            print_manager.custom_debug(f"[DEBUG {label}] Error during debug: {str(e)}")
    else:
        print_manager.custom_debug(f"[DEBUG {label}] Invalid trange format: {trange}")

def multiplot(plot_list, **kwargs):
    """
    Create multiple time-series plots centered around specific times.
    Uses global plt.options for defaults, with kwargs allowing parameter override.
    
    Args:
        plot_list: List of tuples (time, variable)
        **kwargs: Optional overrides for any MultiplotOptions attributes
    """

    print_manager.debug("\n=== Starting Multiplot Function ===")
    # Set global font size for tiny date and other default text
    mpl_plt.rcParams['font.size'] = plt.options.size_of_tiny_date_in_the_corner
    
    # Position descriptions for titles
    pos_desc = {
        'around': 'Around',
        'before': 'Before',
        'after': 'After'
    }
    
    #==========================================================================
    # STEP 1: INITIALIZE OPTIONS AND SETTINGS
    #==========================================================================
    # Get options instance
    options = plt.options

   # ---  DEBUG: Print initial relevant options --- 
    print_manager.debug("[Multiplot Start] Initial Options State:")
    print_manager.debug(f"  x_axis_r_sun: {getattr(options, 'x_axis_r_sun', 'N/A')}")
    print_manager.debug(f"  x_axis_carrington_lon: {getattr(options, 'x_axis_carrington_lon', 'N/A')}")
    print_manager.debug(f"  x_axis_carrington_lat: {getattr(options, 'x_axis_carrington_lat', 'N/A')}")
    print_manager.debug(f"  use_degrees_from_perihelion: {getattr(options, 'use_degrees_from_perihelion', 'N/A')}")
    print_manager.debug(f"  use_relative_time: {getattr(options, 'use_relative_time', 'N/A')}")
    # --- END DEBUG --- 

    # Override any options with provided kwargs - BEFORE initializing mapper
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)
        # Handle new options passed via kwargs
        # Check for existence before setting to avoid creating if not passed
        if key == 'use_degrees_from_perihelion' and value is not None:
            options.use_degrees_from_perihelion = value
        elif key == 'degrees_from_perihelion_range' and value is not None:
            options.degrees_from_perihelion_range = value
        elif key == 'degrees_from_perihelion_tick_step' and value is not None:
            options.degrees_from_perihelion_tick_step = value
            
    # --- DEBUG PRINT: Show initial option state --- 
    # (Keep existing debug prints)
    # ... 

    # Initialize positional mapper if needed
    positional_mapper = None
    using_positional_axis = False  # Default to False
    data_type = 'time' # Default
    axis_label = "Time" # Default
    units = "" # Default
    
    # --- Check if *any* positional feature is enabled --- 
    positional_feature_requested = (
        options.x_axis_r_sun or 
        options.x_axis_carrington_lon or 
        options.x_axis_carrington_lat or 
        getattr(options, 'use_degrees_from_perihelion', False) or # Added perihelion option
        getattr(options, 'use_degrees_from_center_times', False) # Added center_times option
    )
    print_manager.debug(f"Initial check - positional_feature_requested: {positional_feature_requested}")
    
    # --- Explicitly set using_positional_axis based on the check --- 
    if positional_feature_requested:
        using_positional_axis = True 
        print_manager.debug(f"--> Setting using_positional_axis = True based on request.")
    # --- END ---

    # --- Initialize mapper only if a positional feature is requested --- 
    if positional_feature_requested:
        # Ensure positional_data_path exists
        if not hasattr(options, 'positional_data_path') or not options.positional_data_path:
            print_manager.error("❌ Positional data path (options.positional_data_path) is not set. Cannot use positional x-axis or degrees from perihelion/center_times.")
            # Disable positional features if path is missing
            if hasattr(options, 'use_degrees_from_perihelion'): options.use_degrees_from_perihelion = False
            if hasattr(options, 'use_degrees_from_center_times'): options.use_degrees_from_center_times = False
            options.x_axis_r_sun = False 
            options.x_axis_carrington_lon = False 
            options.x_axis_carrington_lat = False
            positional_feature_requested = False # Prevent further positional logic
            using_positional_axis = False # Ensure this is false too
            print_manager.debug("--> Resetting positional flags due to missing path.")
        else:
            print_manager.debug(f"--> Initializing XAxisPositionalDataMapper with path: {options.positional_data_path}")
            positional_mapper = XAxisPositionalDataMapper(options.positional_data_path)
            mapper_loaded = hasattr(positional_mapper, 'data_loaded') and positional_mapper.data_loaded
            print_manager.debug(f"--> Mapper data_loaded status: {mapper_loaded}")
            # --- <CURSOR_INSERT> ---
            # <<< DEBUG: Confirm mapper loaded status >>>
            # print_manager.debug(f"DEBUG_TRACE: Positional Mapper Loaded: {mapper_loaded}")
            # <<< END DEBUG >>>
            # --- </CURSOR_INSERT> ---
            
            if not mapper_loaded:
                print_manager.warning("❌ Failed to load positional data. Disabling positional x-axis and degrees from perihelion/center_times.")
                if hasattr(options, 'use_degrees_from_perihelion'): options.use_degrees_from_perihelion = False
                if hasattr(options, 'use_degrees_from_center_times'): options.use_degrees_from_center_times = False
                options.x_axis_r_sun = False 
                options.x_axis_carrington_lon = False 
                options.x_axis_carrington_lat = False
                positional_feature_requested = False 
                using_positional_axis = False 
            else:
                # --- Determine the *primary* data type for plotting --- 
                if getattr(options, 'use_degrees_from_perihelion', False):
                    print_manager.debug("--> Mode Determination: use_degrees_from_perihelion is True.")
                    data_type = 'degrees_from_perihelion' # Use a distinct type identifier
                    axis_label = "Degrees from Perihelion (°)"
                    units = "°"
                    # Ensure conflicting modes are off (setters should handle this, but verify)
                    options.x_axis_carrington_lon = False
                    options.x_axis_r_sun = False
                    options.x_axis_carrington_lat = False
                    # options.use_relative_time = False # Explicitly disable relative time - REMOVED TO ALLOW USER CONTROL
                elif getattr(options, 'use_degrees_from_center_times', False):
                    print_manager.debug("--> Mode Determination: use_degrees_from_center_times is True.")
                    data_type = 'degrees_from_center_times' # Use a distinct type identifier
                    axis_label = "Degrees from Center Times (°)"
                    units = "°"
                    # Ensure conflicting modes are off (setters should handle this, but verify)
                    options.x_axis_carrington_lon = False
                    options.x_axis_r_sun = False
                    options.x_axis_carrington_lat = False
                elif options.x_axis_carrington_lon:
                    print_manager.debug("--> Mode Determination: x_axis_carrington_lon is True.")
                    data_type = 'carrington_lon'
                    # values_array = positional_mapper.longitude_values # Not needed here
                    axis_label = "Carrington Longitude (°)"
                    units = "°"
                    options.use_relative_time = False # Explicitly disable relative time
                elif options.x_axis_r_sun:
                    print_manager.debug("--> Mode Determination: x_axis_r_sun is True.")
                    data_type = 'r_sun'
                    # values_array = positional_mapper.radial_values # Not needed here
                    axis_label = "Radial Distance (R_sun)"
                    units = "R_sun"
                    options.use_relative_time = False # Explicitly disable relative time
                elif options.x_axis_carrington_lat:
                    print_manager.debug("--> Mode Determination: x_axis_carrington_lat is True.")
                    data_type = 'carrington_lat'
                    # values_array = positional_mapper.latitude_values # Not needed here
                    axis_label = "Carrington Latitude (°)"
                    units = "°"
                    options.use_relative_time = False # Explicitly disable relative time
                else:
                    # This case means positional_feature_requested was true initially, but no specific mode ended up active.
                    print_manager.warning("--> Mode Determination: Positional feature requested but no specific type active, defaulting to time.")
                    using_positional_axis = False # Fallback
                    axis_label = "Time"
                    units = ""
                    data_type = 'time'

                # Verify relative time conflict only if a positional mode is confirmed active
                # (This check is now redundant as positional setters disable relative time)
                # if using_positional_axis and options.use_relative_time:
                #         print_manager.warning("⚠️ Positional axis/degrees AND relative time are enabled.")
                #         print_manager.status("--> Automatically disabling use_relative_time.")
                #         options.use_relative_time = False
                        
    # Final check: If positional feature was requested but ultimately failed or wasn't specific, default to time.
    if not using_positional_axis:
        print_manager.debug("--> Final check: using_positional_axis is False. Setting mode to Time.")
        data_type = 'time'
        axis_label = "Time" 
        units = ""
    # --- END Initialization Section Modifications ---

    # --- DEBUG: Print determined mode --- 
    print_manager.debug("[Multiplot Mode Determined] State:")
    print_manager.debug(f"  data_type: {data_type}")
    print_manager.debug(f"  axis_label: {axis_label}")
    print_manager.debug(f"  using_positional_axis: {using_positional_axis}")
    # --- END DEBUG --- 

    # Store original rcParams to restore later
    original_rcparams = {}
    
    print_manager.debug("\n=== Starting Multiplot Function ===")
    
    # Apply preset configuration if specified
    if options.save_preset:
        options._apply_preset_config()
        # --- TEMPORARILY SET RCPARAMS FOR PRESET --- 
        preset_config = options.PRESET_CONFIGS.get(options.save_preset, {})
        params_to_set = {
            'xtick.major.width': options.tick_width, # Use the option we just added
            'ytick.major.width': options.tick_width, # Use the option we just added
            'xtick.major.size': options.tick_length, # Corresponds to tick_length 
            'ytick.major.size': options.tick_length, # Corresponds to tick_length
            'axes.linewidth': options.border_line_width # Corresponds to spine width
        }
        for key, value in params_to_set.items():
            if key in mpl_plt.rcParams:
                original_rcparams[key] = mpl_plt.rcParams[key]
                mpl_plt.rcParams[key] = value
                print_manager.debug(f"Preset applying rcParam: {key} = {value}")
        # --- END TEMPORARILY SET RCPARAMS --- 
    
    #==========================================================================
    # STEP 2: PROCESS VARIABLES AND ENSURE DATA AVAILABILITY
    #==========================================================================
    for i, (center_time, var) in enumerate(plot_list):
        # DEBUG - Consolidate variable inspection into a single line
        var_info = f"Variable {i}: type={type(var).__name__}"
        if hasattr(var, 'shape'):
            var_info += f", shape={var.shape}"
        print_manager.custom_debug(var_info)
        
        # ENHANCED DEBUG: Track encounter processing
        enc_num = get_encounter_number(center_time)
        print_manager.status(f"🚀 PROCESSING ENCOUNTER {enc_num} (Panel {i+1}) - Center time: {center_time}")
        
        # Add time tracking for center time
        print_manager.time_tracking(f"Panel {i+1} center time: {center_time}")
        
        # Calculate time range for this panel
        if options.position == 'around':
            start_time = pd.Timestamp(center_time) - pd.Timedelta(options.window)/2
            end_time = pd.Timestamp(center_time) + pd.Timedelta(options.window)/2
            print_manager.time_tracking(f"Panel {i+1} 'around' position: center ± {pd.Timedelta(options.window)/2}")
        elif options.position == 'before':
            start_time = pd.Timestamp(center_time) - pd.Timedelta(options.window)
            end_time = pd.Timestamp(center_time)
            print_manager.time_tracking(f"Panel {i+1} 'before' position: center - {pd.Timedelta(options.window)}")
        else:  # after
            start_time = pd.Timestamp(center_time)
            end_time = pd.Timestamp(center_time) + pd.Timedelta(options.window)
            print_manager.time_tracking(f"Panel {i+1} 'after' position: center + {pd.Timedelta(options.window)}")
            
        # Track calculated time range
        print_manager.time_tracking(f"Panel {i+1} calculated time range: {start_time} to {end_time}")
            
        trange = [
            start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'),
            end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
        ]
        
        # Track formatted time range 
        print_manager.time_tracking(f"Panel {i+1} formatted trange: {trange[0]} to {trange[1]}")

        #----------------------------------------------------------------------
        # STEP 2.1: HANDLE CUSTOM VARIABLES - CRITICAL DATA PREPARATION
        #----------------------------------------------------------------------
        if hasattr(var, 'data_type') and var.data_type == 'custom_data_type':
            print_manager.status(f"Panel {i+1}: Custom variable detected: {getattr(var, 'subclass_name', 'unknown')}")
            
            # CRITICAL CHECK: Does the variable have ANY data at all?
            has_initial_data = hasattr(var, 'datetime_array') and var.datetime_array is not None and len(var.datetime_array) > 0
            
            if not has_initial_data:
                print_manager.status(f"⚠️ Custom variable has NO initial data - ensuring source variables have data")
                
                # CRITICAL FIX: Always ensure source variables have data for empty custom variables
                if hasattr(var, 'source_var') and var.source_var is not None:
                    base_vars = []
                    for src_var in var.source_var:
                        if hasattr(src_var, 'class_name') and src_var.class_name != 'custom_class' and src_var.data_type != 'custom_data_type':
                            base_vars.append(src_var)
                            print_manager.test(f"Adding source variable for data download: {src_var.class_name}.{src_var.subclass_name}")
                    
                    # Download fresh data for base variables
                    if base_vars:
                        print_manager.status(f"Downloading initial data for {len(base_vars)} source variables...")
                        # Set TimeRangeTracker for this panel's time range
                        TimeRangeTracker.set_current_trange(trange)
                        get_data(trange, *base_vars)
                
                # Check if time range update is needed (or in this case, initial data)
                needs_refresh = True
            else:
                # Normal refresh check for variables with existing data
                needs_refresh = False
                # Only do time range check if we have data
                cached_start = np.datetime64(var.datetime_array[0], 's')
                cached_end = np.datetime64(var.datetime_array[-1], 's')
                requested_start = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'), 's')
                requested_end = np.datetime64(datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f'), 's')
                
                # Add 10s buffer to handle instrument timing differences
                buffered_start = cached_start - np.timedelta64(10, 's')
                buffered_end = cached_end + np.timedelta64(10, 's')
                
                if buffered_start > requested_start or buffered_end < requested_end:
                    print_manager.custom_debug(f"Custom variable - Requested time falls outside cached data range, updating...")
                    needs_refresh = True
            
            # If we need to refresh (or get initial data), handle the source variables
            if needs_refresh:
                # IMPORTANT: Get the source variables and ensure they have fresh data
                if hasattr(var, 'source_var') and var.source_var is not None:
                    # Get base variables (non-custom) that need to be downloaded
                    base_vars = []
                    for src_var in var.source_var:
                        if hasattr(src_var, 'class_name') and src_var.class_name != 'custom_class' and src_var.data_type != 'custom_data_type':
                            base_vars.append(src_var)
                    
                    # Download fresh data for base variables if needed
                    if base_vars:
                        print_manager.custom_debug(f"Downloading fresh data for {len(base_vars)} source variables...")
                        # Set TimeRangeTracker for this panel's time range
                        TimeRangeTracker.set_current_trange(trange)
                        get_data(trange, *base_vars)
                
                # Update the variable for the new time range using its update method
                if hasattr(var, 'update'):
                    print_manager.status(f"Updating custom variable for new time range...")
                    # Key diagnostic print before update
                    print_manager.test(f"Custom variable before update: has_data={has_initial_data}, name={getattr(var, 'subclass_name', 'unknown')}")
                    
                    # Important! Capture the returned variable which contains the updated data
                    updated_var = var.update(trange)
                    if updated_var is not None:
                        # Update the plot list with the returned updated variable
                        plot_list[i] = (center_time, updated_var)
                        print_manager.status(f"✅ Updated plot list with refreshed custom variable")
                        
                        # Key diagnostic print after update
                        has_data_after = hasattr(updated_var, 'datetime_array') and updated_var.datetime_array is not None and len(updated_var.datetime_array) > 0
                        print_manager.test(f"Custom variable after update: has_data={has_data_after}, data_points={len(updated_var.datetime_array) if has_data_after else 0}")
                    else:
                        print_manager.warning(f"Cannot update custom variable - update method returned None")
                else:
                    print_manager.warning(f"Cannot update custom variable - no update method available")
                
        # NEW: Handle REGULAR variables (non-custom) by fetching fresh data for each time range
        elif hasattr(var, 'data_type') and hasattr(var, 'class_name') and hasattr(var, 'subclass_name'):
            print_manager.custom_debug(f"Regular variable detected: {var.class_name}.{var.subclass_name} - fetching data for time range: {trange}")
            print_manager.time_tracking(f"Panel {i+1} regular variable {var.class_name}.{var.subclass_name} processing with trange: {trange[0]} to {trange[1]}")
            
            try:
                # Use get_data to handle loading for all regular types (including FITS)
                # <<< NEW DEBUG >>>
                print_manager.debug(f"Loop 1, Panel {i+1} Pre-Grab: Checking var with class='{getattr(var, 'class_name', 'N/A')}', subclass='{getattr(var, 'subclass_name', 'N/A')}', ID={id(var)}")
                # <<< END NEW DEBUG >>>
                print_manager.custom_debug(f"Calling get_data for {var.class_name}.{var.subclass_name} for time range: {trange}")
                print_manager.time_tracking(f"Panel {i+1} calling get_data for {var.class_name}.{var.subclass_name} with trange: {trange[0]} to {trange[1]}")
                
                # 🚀 CRITICAL FIX: Set TimeRangeTracker for this specific panel's time range
                # This ensures data classes get the correct time range for this panel
                from .time_utils import TimeRangeTracker
                TimeRangeTracker.set_current_trange(trange)
                
                get_data(trange, var) # <<< USE CENTRAL get_data function >>>

                # After get_data, the variable instance in data_cubby should be updated.
                # We need to retrieve the potentially updated variable to use for plotting.
                class_instance = data_cubby.grab(var.class_name)
                if class_instance:
                    updated_var = class_instance.get_subclass(var.subclass_name)
                    if updated_var is not None:
                        # Update the plot_list with the potentially updated variable instance
                        plot_list[i] = (center_time, updated_var)
                        enc_num = get_encounter_number(center_time)  # Get encounter number for context
                        print_manager.status(f"✅ ENCOUNTER {enc_num} (Panel {i+1}) DATA SUCCESSFULLY LOADED!")
                        print_manager.custom_debug(f"✅ Refreshed variable reference in plot_list for {var.class_name}.{var.subclass_name}")
                        # <<< NEW DEBUG >>>
                        print_manager.debug(f"Loop 1, Panel {i+1}: Stored var ID in plot_list: {id(plot_list[i][1])}")
                        # <<< END NEW DEBUG >>>
                        # Check if the updated variable has data
                        if hasattr(updated_var, 'datetime_array') and updated_var.datetime_array is not None:
                            data_points = len(updated_var.datetime_array)
                            print_manager.status(f"✅ ENCOUNTER {enc_num}: Variable contains {data_points} data points")
                        else:
                            print_manager.warning(f"⚠️ ENCOUNTER {enc_num}: Variable updated but has no datetime_array!")
                    else:
                        enc_num = get_encounter_number(center_time)
                        print_manager.error(f"🚨 ENCOUNTER {enc_num} (Panel {i+1}): Failed to get updated subclass {var.subclass_name} after get_data")
                else:
                    enc_num = get_encounter_number(center_time)
                    print_manager.error(f"🚨 ENCOUNTER {enc_num} (Panel {i+1}): Failed to get class instance {var.class_name} from data_cubby after get_data")
            except Exception as e:
                enc_num = get_encounter_number(center_time)  # Get encounter number for context
                print_manager.error(f"🚨 CRITICAL: ENCOUNTER {enc_num} (Panel {i+1}) DATA FETCH FAILED!")
                print_manager.error(f"❌ Error during get_data or variable update for {var.class_name}.{var.subclass_name}: {str(e)}")
                print_manager.error(f"❌ This encounter will show as BLACK/MISSING in the plot!")
                print_manager.time_tracking(f"Panel {i+1} error during get_data for {var.class_name}.{var.subclass_name}: {str(e)}")
                # Continue to the next variable in the plot_list
                continue 
    
    #==========================================================================
    # STEP 3: CREATE FIGURE AND CONFIGURE SUBPLOTS
    #==========================================================================
    # Calculate number of panels needed
    n_panels = len(plot_list)
    
    # Get color scheme BEFORE creating figure (needed for title color)
    color_scheme = get_plot_colors(n_panels, options.color_mode, options.single_color)
    
    # NEW: Always use constrained_layout=True and do not set manual margins
    if getattr(options, 'use_default_plot_settings', False) or options.save_preset or options.output_dimensions:
        # Determine figure size and dpi from preset or options
        if options.save_preset:
            config = options.PRESET_CONFIGS[options.save_preset]
            figsize = config['figsize']
            dpi = config.get('dpi', 300)
        elif options.output_dimensions:
            target_width_px, target_height_px = options.output_dimensions
            # Convert pixels to inches for figsize
            dpi = 300
            figsize = (target_width_px / dpi, target_height_px / dpi)
        else:
            figsize = (options.width, options.height_per_panel * n_panels)
            dpi = 300
        # CRITICAL FIX: Check for spectral plots and force constrained_layout=False if found
        # This prevents constrained_layout from interfering with manual colorbar positioning
        has_spectral_plots = any(
            hasattr(var, 'plot_type') and var.plot_type == 'spectral' 
            for time, var in plot_list
        )
        
        if has_spectral_plots and options.constrained_layout:
            print_manager.status(f"🔧 SPECTRAL PLOTS DETECTED: Forcing constrained_layout=False to prevent colorbar positioning issues")
            use_constrained_layout = False
        else:
            use_constrained_layout = options.constrained_layout
            
        print_manager.test(f"[LAYOUT] Final constrained_layout setting: {use_constrained_layout} (user setting: {options.constrained_layout}, has spectral: {has_spectral_plots})")
        fig, axs = plt.subplots(n_panels, 1, figsize=figsize, dpi=dpi, constrained_layout=use_constrained_layout)
        
        if use_constrained_layout:
            print_manager.status(f"Using constrained_layout=True - letting matplotlib handle all spacing automatically.")
        else:
            print_manager.status(f"Using constrained_layout=False - applying manual margins.")
            fig.subplots_adjust(
                top=options.margin_top,
                bottom=options.margin_bottom,
                left=options.margin_left,
                right=options.margin_right,
                hspace=options.hspace_vertical_space_between_plots
            )
            print_manager.status(f"Set margins (top={options.margin_top}, bottom={options.margin_bottom}, left={options.margin_left}, right={options.margin_right}) and hspace={options.hspace_vertical_space_between_plots}")
    else:
        # CRITICAL FIX: Check for spectral plots and force constrained_layout=False if found
        # This prevents constrained_layout from interfering with manual colorbar positioning
        has_spectral_plots = any(
            hasattr(var, 'plot_type') and var.plot_type == 'spectral' 
            for time, var in plot_list
        )
        
        if has_spectral_plots and options.constrained_layout:
            print_manager.status(f"🔧 SPECTRAL PLOTS DETECTED: Forcing constrained_layout=False to prevent colorbar positioning issues")
            use_constrained_layout = False
        else:
            use_constrained_layout = options.constrained_layout
            
        print_manager.test(f"[LAYOUT] Final constrained_layout setting: {use_constrained_layout} (user setting: {options.constrained_layout}, has spectral: {has_spectral_plots})")
        fig, axs = plt.subplots(n_panels, 1, figsize=(options.width, options.height_per_panel * n_panels), constrained_layout=use_constrained_layout)
        
        if use_constrained_layout:
            print_manager.status(f"Using constrained_layout=True - letting matplotlib handle all spacing automatically.")
        else:
            print_manager.status(f"Using constrained_layout=False - applying manual margins.")
            fig.subplots_adjust(
                top=options.margin_top,
                bottom=options.margin_bottom,
                left=options.margin_left,
                right=options.margin_right,
                hspace=options.hspace_vertical_space_between_plots
            )
            print_manager.status(f"Set margins (top={options.margin_top}, bottom={options.margin_bottom}, left={options.margin_left}, right={options.margin_right}) and hspace={options.hspace_vertical_space_between_plots}")
    # Ensure axs is always a flat list of Axes
    import numpy as _np
    if not isinstance(axs, (list, _np.ndarray)):
        axs = [axs]
    elif isinstance(axs, _np.ndarray):
        axs = axs.flatten().tolist()
    
    #==========================================================================
    # STEP 4: POPULATE PLOTS WITH DATA
    #==========================================================================
    for i, (center_time, var) in enumerate(plot_list): # <--- Loop 2 (Plotting)
        # <<< NEW: Initialize panel-specific flag for perihelion degrees >>>
        panel_actually_uses_degrees = False
        perihelion_time_str = None # Initialize
        current_panel_use_degrees = False # Initialize
        center_dt = pd.Timestamp(center_time)
        # <<< END NEW >>>

        # <<< NEW: Initialize separate variables for center_times degrees >>>
        panel_uses_center_times_degrees = False
        center_time_reference_str = None
        # <<< END NEW >>>

        # ENHANCED DEBUG: Track encounter in plotting loop
        enc_num = get_encounter_number(center_time)
        print_manager.status(f"🎨 PLOTTING ENCOUNTER {enc_num} (Panel {i+1}) - Center time: {center_time}")
        
        # <<< MODIFIED DEBUG >>>
        print_manager.custom_debug(f'Adding data to plot panel {i+1}/{n_panels}... Var ID from plot_list: {id(var)}\n')
        # <<< END MODIFIED DEBUG >>>
        
        # CRITICAL DEBUG: Check if variable has data before plotting
        if hasattr(var, 'datetime_array') and var.datetime_array is not None:
            data_points = len(var.datetime_array)
            print_manager.status(f"✅ ENCOUNTER {enc_num}: Ready to plot with {data_points} data points")
        else:
            print_manager.error(f"🚨 ENCOUNTER {enc_num}: NO DATA AVAILABLE FOR PLOTTING! This will show as BLACK/MISSING!")
        # Add diagnostic for HAM feature status
        print_manager.debug(f"Panel {i+1} - HAM feature status: hamify={options.hamify}, ham_var={options.ham_var is not None}")
        # center_dt = pd.Timestamp(center_time) # Moved up

        # <<< NEW: Get perihelion time and determine if this panel should use degrees >>>
        if using_positional_axis and getattr(options, 'use_degrees_from_perihelion', False):
            try:
                # <<< ADD DEBUG PRINT: Show center_dt BEFORE lookup >>>
                print_manager.debug(f"[DEBUG Perihelion Lookup - Panel {i+1}] Center Datetime for Lookup: {center_dt}")
                
                perihelion_time_str = get_perihelion_time(center_dt)

                # <<< ADD DEBUG PRINT: Show result AFTER lookup >>>
                print_manager.debug(f"[DEBUG Perihelion Lookup - Panel {i+1}] Returned Perihelion Time Str: {perihelion_time_str}")

                if perihelion_time_str:
                    print_manager.debug(f"Panel {i+1}: Found perihelion time: {perihelion_time_str}")
                    current_panel_use_degrees = True
                    # --- <CURSOR_INSERT> ---
                    # <<< DEBUG: Confirm perihelion time found >>>
                    # print_manager.debug(f"DEBUG_TRACE: Panel {i+1} FOUND perihelion: {perihelion_time_str}, setting current_panel_use_degrees=True")
                    # <<< END DEBUG >>>
                    # --- </CURSOR_INSERT> ---
                else:
                    print_manager.status(f"Panel {i+1}: Perihelion time not found for {center_dt}. Cannot use degrees from perihelion for this panel.")
                    current_panel_use_degrees = False
                    # --- <CURSOR_INSERT> ---
                    # <<< DEBUG: Confirm perihelion time NOT found >>>
                    # print_manager.debug(f"DEBUG_TRACE: Panel {i+1} DID NOT FIND perihelion for {center_dt}, setting current_panel_use_degrees=False")
                    # <<< END DEBUG >>>
                    # --- </CURSOR_INSERT> ---
            except Exception as e:
                print_manager.error(f"Panel {i+1}: Error getting perihelion time: {e}")
                current_panel_use_degrees = False
                # --- <CURSOR_INSERT> ---
                # <<< DEBUG: Confirm EXCEPTION during perihelion lookup >>>
                # print_manager.debug(f"DEBUG_TRACE: Panel {i+1} EXCEPTION getting perihelion: {e}, setting current_panel_use_degrees=False")
                # <<< END DEBUG >>>
                # --- </CURSOR_INSERT> ---
        # <<< END NEW >>>

        # <<< NEW: Simple center_times degrees (completely separate from perihelion) >>>
        elif using_positional_axis and getattr(options, 'use_degrees_from_center_times', False):
            print_manager.debug(f"Panel {i+1}: Using degrees from center_times mode - simple reference to center_time")
            # For center_times mode, we always use the center_time as reference - no lookup needed!
            panel_uses_center_times_degrees = True
            center_time_reference_str = center_dt.strftime('%Y/%m/%d %H:%M:%S.%f')
            print_manager.debug(f"Panel {i+1}: Center time reference: {center_time_reference_str}")
        # <<< END NEW >>>

        # Get encounter number automatically
        enc_num = get_encounter_number(center_time)
    
        # Format time range
        if options.position == 'around':
            start_time = center_dt - pd.Timedelta(options.window)/2
            end_time = center_dt + pd.Timedelta(options.window)/2
        elif options.position == 'before':
            start_time = center_dt - pd.Timedelta(options.window)
            end_time = center_dt
        else:  # after
            start_time = center_dt
            end_time = center_dt + pd.Timedelta(options.window)
        
        trange = [
            start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'),
            end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
        ]
        
        # ====================================================================
        # Plot Variables (Multi-Variable) with Plot Type Handling
        # ====================================================================
        panel_color = color_scheme['panel_colors'][i] if color_scheme else None
        axis_options = getattr(options, f'ax{i+1}')
        
        if isinstance(var, list):
            for idx, single_var in enumerate(var):
                indices = []
                # Add a check for None datetime_array
                if single_var is None:
                    print_manager.error(f"❌ ERROR: Variable is None, cannot plot")
                    continue
                
                if not hasattr(single_var, 'datetime_array') or single_var.datetime_array is None:
                    print_manager.error(f"❌ ERROR: Variable has no datetime_array, cannot plot")
                    print_manager.error(f"This might be caused by a problem with custom variable lookup.")
                    print_manager.error(f"Check that you're using the registered name of the variable (e.g., 'Hello') and not the operation string (e.g., 'anisotropy + bmag')")
                    continue
                    
                # Debug the time range
                debug_variable_time_ranges(single_var, trange, f"Panel {i+1}")
                
                # Debug the time range issue
                print_manager.custom_debug(f"🕐 Panel {i+1}: Checking time range of '{single_var.subclass_name}'")
                print_manager.custom_debug(f"🕐 Variable datetime_array: {len(single_var.datetime_array)} points from {single_var.datetime_array[0]} to {single_var.datetime_array[-1]}")
                print_manager.custom_debug(f"🕐 Requested time range: {trange[0]} to {trange[1]}")
                
                # Track time range before time_clip
                print_manager.time_tracking(f"Panel {i+1} plot var time range: {single_var.datetime_array[0]} to {single_var.datetime_array[-1]}")
                print_manager.time_tracking(f"Panel {i+1} plot requested trange: {trange[0]} to {trange[1]}")
                
                # Only get time clip indices if the datetime_array exists
                print_manager.time_tracking(f"Panel {i+1} calling time_clip with trange: {trange[0]} to {trange[1]}")
                indices = []
                # CRITICAL FIX: More robust handling of empty datetime_array
                if single_var.datetime_array is not None and len(single_var.datetime_array) > 0:
                    # <<< ADDED DEBUG PRINTS >>>
                    # print_manager.debug(f"Panel {i+1} pre-clip: var ID={id(single_var)}, Array len={len(single_var.datetime_array)}") # COMMENTED OUT
                    try:
                        # --- MODIFIED LINES START ---
                        start_str = format_datetime_for_log(single_var.datetime_array[0])
                        end_str = format_datetime_for_log(single_var.datetime_array[-1])
                        # print_manager.debug(f"Panel {i+1} pre-clip: Var data range: {start_str} to {end_str}") # COMMENTED OUT
                        formatted_trange_list = [format_datetime_for_log(t) for t in trange]
                        # print_manager.debug(f"Panel {i+1} pre-clip: Requested trange: {formatted_trange_list[0]} to {formatted_trange_list[1]}") # COMMENTED OUT
                        # --- MODIFIED LINES END ---
                    except IndexError:
                        # print_manager.debug(f"Panel {i+1} pre-clip: Var data range: INDEX ERROR (array likely empty despite len check?)") # COMMENTED OUT
                        pass # Keep pass to avoid syntax error
                    # print_manager.debug(f"Panel {i+1} pre-clip: Requested trange: {trange[0]} to {trange[1]}") # COMMENTED OUT
                    # <<< END ADDED DEBUG PRINTS >>>
                    raw_datetime_array = single_var.plot_config.datetime_array if hasattr(single_var, 'plot_options') else single_var.datetime_array
                    indices = time_clip(raw_datetime_array, trange[0], trange[1])
                else:
                    print_manager.warning(f"Empty datetime_array for panel {i+1} - cannot clip times")

                if len(indices) > 0:
                    print_manager.time_tracking(f"Panel {i+1} time_clip returned {len(indices)} points: first={raw_datetime_array[indices[0]]}, last={raw_datetime_array[indices[-1]]}")
                    
                    if idx == 1 and options.second_variable_on_right_axis:
                        ax2 = axs[i].twinx()
                        
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
                            plot_color = axis_options.r.color
                        else:
                            plot_color = single_var.color
    
                        # Get x-axis data - use longitude if available
                        # x_data = raw_datetime_array[indices] # OLD: Start with time
                        time_slice = raw_datetime_array[indices]
                        data_slice = single_var.all_data[indices]
                        x_data = time_slice # Default to time

                        if using_positional_axis and positional_mapper is not None:
                            print_manager.debug(f"Panel {i+1} (Right Axis): Attempting positional mapping for {len(time_slice)} points")
                            positional_vals = positional_mapper.map_to_position(time_slice, data_type)

                            if positional_vals is not None:
                                # --- NEW: Create mask for successful mapping --- 
                                # Assuming None or np.nan indicates a mapping failure
                                valid_mask = ~np.isnan(positional_vals) 
                                num_valid = np.sum(valid_mask)
                                
                                if num_valid > 0:
                                    x_data = positional_vals[valid_mask] # Use only valid positions
                                    data_slice = data_slice[valid_mask]   # Filter data slice accordingly
                                    print_manager.debug(f"Panel {i+1} (Right Axis): Positional mapping successful, using {num_valid} valid points")
                                else:
                                    print_manager.status(f"Panel {i+1} (Right Axis): Positional mapping resulted in no valid points. Using time.")
                                    # x_data remains time_slice, data_slice remains original data_slice
                            else:
                                print_manager.status(f"Panel {i+1} (Right Axis): Positional mapping failed (returned None). Using time.")
                                # x_data remains time_slice, data_slice remains original data_slice
                            
                            # --- Transform to relative time if use_relative_time is True (Right Axis) ---
                            if options.use_relative_time and not using_positional_axis:
                                # Convert datetime x_data to relative time (hours/days from center_time)
                                if hasattr(x_data, '__iter__') and len(x_data) > 0:
                                    # Convert to pandas Timestamp if needed, then calculate relative time
                                    time_deltas = pd.to_datetime(x_data) - center_dt
                                    if options.relative_time_step_units == 'days':
                                        x_data = time_deltas.total_seconds() / (3600 * 24)
                                    elif options.relative_time_step_units == 'hours':
                                        x_data = time_deltas.total_seconds() / 3600
                                    elif options.relative_time_step_units == 'minutes':
                                        x_data = time_deltas.total_seconds() / 60
                                    elif options.relative_time_step_units == 'seconds':
                                        x_data = time_deltas.total_seconds()
                                    else:
                                        # Default to hours if unit not recognized
                                        x_data = time_deltas.total_seconds() / 3600
                                    print_manager.debug(f"Panel {i+1} (Right Axis): Transformed x_data to relative time ({options.relative_time_step_units}). Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")

                        # --- Use filtered x_data and data_slice --- 
                        print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                        ax2.plot(x_data, 
                                data_slice, # Use filtered data_slice
                                linewidth=options.magnetic_field_line_width if options.save_preset else single_var.line_width,
                                linestyle=single_var.line_style,
                                label=single_var.legend_label,
                                color=plot_color)
                        
                        if hasattr(single_var, 'y_limit') and single_var.y_limit:
                            # Keep this functionality but remove the debug print
                            pass
                        
                        if hasattr(axis_options, 'r') and axis_options.r.y_limit is not None:
                            # Determine the y_scale for the right axis
                            # This is tricky as right axis doesn't always have its own scale setting
                            # We'll use the same scale as the main variable or a default
                            right_y_scale = getattr(single_var, 'y_scale', 'linear')
                            
                            # Validate the y_limit if we're using a log scale
                            validated_r_y_limit = validate_log_scale_limits(
                                axis_options.r.y_limit, 
                                right_y_scale, 
                                f"right axis of panel {i+1}"
                            )
                            
                            ax2.set_ylim(validated_r_y_limit)
                        elif hasattr(single_var, 'y_limit') and single_var.y_limit:
                            # Validate the y_limit if we're using a log scale
                            right_y_scale = getattr(single_var, 'y_scale', 'linear')
                            validated_r_y_limit = validate_log_scale_limits(
                                single_var.y_limit, 
                                right_y_scale, 
                                f"right axis of panel {i+1}"
                            )
                            ax2.set_ylim(single_var.y_limit)
                        
                        # --- NEW: Apply rainbow color to all right axis elements ---
                        if panel_color is not None:
                            # Set y-axis label color and font weight
                            ax2.yaxis.label.set_color(panel_color)
                            if hasattr(options, 'bold_y_axis_label') and options.bold_y_axis_label:
                                ax2.yaxis.label.set_weight('bold')
                            else:
                                ax2.yaxis.label.set_weight('normal')
                            # Set tick color and label size
                            ax2.tick_params(axis='y', colors=panel_color, which='both', labelsize=options.y_tick_label_font_size)
                            # Set all spines to panel color
                            for spine in ax2.spines.values():
                                spine.set_color(panel_color)
                        # --- END NEW ---
                        
                        # Set the right y-axis label to match the panel color and style
                        ham_ylabel = getattr(ham_var, 'y_label', 'HAM')
                        ax2.set_ylabel(ham_ylabel,
                                    fontsize=options.y_axis_label_font_size,
                                    labelpad=options.y_label_pad,
                                    fontweight='bold' if options.bold_y_axis_label else 'normal',
                                    ha=options.y_label_alignment)
                        # Force all right axis elements to rainbow color
                        apply_right_axis_color(ax2, panel_color, options)
                        print(f"DEBUG: Panel {i+1} right axis label is: '{ax2.get_ylabel()}'")
                        # Set right y-axis tick params and spine colors to match panel color
                        ax2.tick_params(axis='y', colors=panel_color, which='both')
                        for spine in ax2.spines.values():
                            spine.set_color(panel_color)
                        # Now apply the panel color to ax2 (for y-label, etc.)
                    
                    else:
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(single_var, 'color') and single_var.color is not None:
                            plot_color = single_var.color
                        elif axis_options.color is not None:
                            plot_color = axis_options.color
                        else:
                            plot_color = None
    
                        # Get x-axis data - use longitude if available
                        # x_data = raw_datetime_array[indices] # OLD
                        time_slice = raw_datetime_array[indices]
                        data_slice = single_var.all_data[indices]
                        x_data = time_slice # Default to time

                        if using_positional_axis and positional_mapper is not None:
                            print_manager.debug(f"Panel {i+1} (List Var): Attempting positional mapping for {len(time_slice)} points")
                            positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                            if positional_vals is not None:
                                # --- NEW: Create mask for successful mapping --- 
                                valid_mask = ~np.isnan(positional_vals) 
                                num_valid = np.sum(valid_mask)
                                
                                if num_valid > 0:
                                    x_data = positional_vals[valid_mask]
                                    data_slice = data_slice[valid_mask] 
                                    print_manager.debug(f"Panel {i+1} (List Var): Positional mapping successful, using {num_valid} valid points")
                                else:
                                    print_manager.status(f"Panel {i+1} (List Var): Positional mapping resulted in no valid points. Using time.")
                            else:
                                print_manager.status(f"Panel {i+1} (List Var): Positional mapping failed (returned None). Using time.")
                            
                            # --- Transform to relative time if use_relative_time is True (List Var) ---
                            if options.use_relative_time and not using_positional_axis:
                                # Convert datetime x_data to relative time (hours/days from center_time)
                                if hasattr(x_data, '__iter__') and len(x_data) > 0:
                                    # Convert to pandas Timestamp if needed, then calculate relative time
                                    time_deltas = pd.to_datetime(x_data) - center_dt
                                    if options.relative_time_step_units == 'days':
                                        x_data = time_deltas.total_seconds() / (3600 * 24)
                                    elif options.relative_time_step_units == 'hours':
                                        x_data = time_deltas.total_seconds() / 3600
                                    elif options.relative_time_step_units == 'minutes':
                                        x_data = time_deltas.total_seconds() / 60
                                    elif options.relative_time_step_units == 'seconds':
                                        x_data = time_deltas.total_seconds()
                                    else:
                                        # Default to hours if unit not recognized
                                        x_data = time_deltas.total_seconds() / 3600
                                    print_manager.debug(f"Panel {i+1} (List Var): Transformed x_data to relative time ({options.relative_time_step_units}). Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                        
                        # --- Use filtered x_data and data_slice --- 
                        print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                        axs[i].plot(x_data, 
                                data_slice, # Use filtered data_slice
                                linewidth=options.magnetic_field_line_width if options.save_preset else single_var.line_width,
                                linestyle=single_var.line_style,
                                label=single_var.legend_label,
                                color=plot_color)
                        
                        if panel_color:
                            apply_panel_color(axs[i], panel_color, options)
            
            if len(var) > 1:
                lines_left, labels_left = axs[i].get_legend_handles_labels()
                if options.second_variable_on_right_axis:
                    lines_right, labels_right = ax2.get_legend_handles_labels()
                    axs[i].legend(lines_left + lines_right, 
                                labels_left + labels_right,
                                bbox_to_anchor=(1.025, 1),
                                loc='upper left')
                    # Set legend label color to rainbow if in rainbow mode
                    if options.color_mode == 'rainbow' and panel_color is not None:
                        leg = axs[i].get_legend()
                        for text in leg.get_texts():
                            text.set_color(panel_color)
                        # Set the legend border (frame) color to match the panel color
                        leg.get_frame().set_edgecolor(panel_color)
                else:
                    axs[i].legend(bbox_to_anchor=(1.025, 1),
                                loc='upper left')
        else:
            indices = []
            # Add a check for None datetime_array
            if var is None:
                print_manager.error(f"❌ ERROR: Variable is None, cannot plot")
                continue
            
            if not hasattr(var, 'datetime_array') or var.datetime_array is None:
                print_manager.error(f"❌ ERROR: Variable has no datetime_array, cannot plot")
                print_manager.error(f"This might be caused by a problem with custom variable lookup.")
                print_manager.error(f"Check that you're using the registered name of the variable (e.g., 'Hello') and not the operation string (e.g., 'anisotropy + bmag')")
                continue
            
            # Debug the time range
            debug_variable_time_ranges(var, trange, f"Panel {i+1}")
            
            # Debug the time range issue
            print_manager.custom_debug(f"🕐 Panel {i+1}: Checking time range of '{var.subclass_name}'")
            print_manager.custom_debug(f"🕐 Variable datetime_array: {len(var.datetime_array)} points from {var.datetime_array[0]} to {var.datetime_array[-1]}")
            print_manager.custom_debug(f"🕐 Requested time range: {trange[0]} to {trange[1]}")
            
            # Track time range before time_clip
            print_manager.time_tracking(f"Panel {i+1} plot var time range: {var.datetime_array[0]} to {var.datetime_array[-1]}")
            print_manager.time_tracking(f"Panel {i+1} plot requested trange: {trange[0]} to {trange[1]}")
                
            # Only get time clip indices if the datetime_array exists
            print_manager.time_tracking(f"Panel {i+1} calling time_clip with trange: {trange[0]} to {trange[1]}")
            indices = []
            # CRITICAL FIX: More robust handling of empty datetime_array
            if var.datetime_array is not None and len(var.datetime_array) > 0:
                # <<< ADDED DEBUG PRINTS >>>
                # print_manager.debug(f"Panel {i+1} pre-clip: var ID={id(var)}, Array len={len(var.datetime_array)}") # COMMENTED OUT
                try:
                    # --- MODIFIED LINES START ---
                    start_str = format_datetime_for_log(var.datetime_array[0])
                    end_str = format_datetime_for_log(var.datetime_array[-1])
                    # print_manager.debug(f"Panel {i+1} pre-clip: Var data range: {start_str} to {end_str}") # COMMENTED OUT
                    formatted_trange_list = [format_datetime_for_log(t) for t in trange]
                    # print_manager.debug(f"Panel {i+1} pre-clip: Requested trange: {formatted_trange_list[0]} to {formatted_trange_list[1]}") # COMMENTED OUT
                    # --- MODIFIED LINES END ---
                except IndexError:
                    # print_manager.debug(f"Panel {i+1} pre-clip: Var data range: INDEX ERROR (array likely empty despite len check?)") # COMMENTED OUT
                    pass # Keep pass to avoid syntax error
                # print_manager.debug(f"Panel {i+1} pre-clip: Requested trange: {trange[0]} to {trange[1]}") # COMMENTED OUT
                # <<< END ADDED DEBUG PRINTS >>>
                raw_datetime_array = var.plot_config.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                indices = time_clip(raw_datetime_array, trange[0], trange[1])
            else:
                print_manager.warning(f"Empty datetime_array for panel {i+1} - cannot clip times")

            if len(indices) > 0:
                print_manager.time_tracking(f"Panel {i+1} time_clip returned {len(indices)} points: first={raw_datetime_array[indices[0]]}, last={raw_datetime_array[indices[-1]]}")
                
                # DEBUG: Track E14 and E15 specifically
                if i+1 in [14, 15]:
                    print(f"🔍 DEBUG E{i+1}: Found {len(indices)} time indices")
                    print(f"🔍 DEBUG E{i+1}: Data shape: {np.array(var.all_data).shape}")
                    print(f"🔍 DEBUG E{i+1}: Time range: {raw_datetime_array[indices[0]]} to {raw_datetime_array[indices[-1]]}")
                
                if hasattr(var, 'y_limit') and var.y_limit:
                    # Keep functionality but remove debug print
                    pass
                
                if hasattr(var, 'plot_type'):
                    if var.plot_type == 'time_series':
                        plot_color = panel_color
                        if not plot_color:
                            plot_color = axis_options.color if axis_options.color else var.color
                        
                        # CRITICAL FIX: Check if indices is empty before trying to plot
                        if len(indices) > 0:
                            # Get initial time and data slices
                            time_slice = raw_datetime_array[indices]
                            data_slice = var.all_data[indices]
                            x_data = time_slice # Default to time
                            valid_lon_mask = None # Initialize mask

                            # --- Perihelion Degree Calculation ---
                            if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Time Series): Calculating Degrees from Perihelion.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    # <<< MOVE PERIHELION LON CALCULATION *INSIDE* THIS BLOCK >>>
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon', unwrap_angles=True)
                                    
                                    # 2. Map *panel-specific* perihelion time to its longitude
                                    perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                    perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)
                                    
                                    if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                        perihelion_lon_val = perihelion_lon_arr[0]
                                        
                                        # <<< Existing Debug Prints Here >>>
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Plot Type: Time Series")
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Time Str: {perihelion_time_str}")
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Lon Value Used: {perihelion_lon_val:.4f}")

                                        # Create mask for valid longitude values in the slice
                                        valid_lon_mask = ~np.isnan(carrington_lons_slice) # Assign mask here
                                        num_valid_lons = np.sum(valid_lon_mask)

                                        if num_valid_lons > 0:
                                            # Filter slice data based on valid longitudes
                                            carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                            data_slice_filtered_lon = data_slice[valid_lon_mask]

                                            # 3. Calculate relative degrees (raw difference of unwrapped)
                                            relative_degrees = carrington_lons_slice_valid - perihelion_lon_val

                                            # 4. CRITICAL FIX: Wrap the difference to the [-180, 180] range
                                            relative_degrees_wrapped = (relative_degrees + 180) % 360 - 180

                                            # 5. Set x_data & filtered data_slice
                                            x_data = relative_degrees_wrapped # Use the WRAPPED version
                                            data_slice = data_slice_filtered_lon

                                            # 6. Set flags
                                            panel_actually_uses_degrees = True
                                            print_manager.debug(f"  Successfully calculated relative degrees. Wrapped Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                                            # 7. Store flag on axis
                                            axs[i]._panel_actually_used_degrees = True
                                            print_manager.debug(f"--> Stored _panel_actually_used_degrees=True on axis {i} (Time Series)")
                                        else:
                                            print_manager.warning(f"Panel {i+1} (Time Series): No valid longitudes found in time slice after mapping. Falling back to time axis.")
                                            panel_actually_uses_degrees = False
                                            x_data = time_slice # Ensure fallback
                                            # data_slice remains the original full slice matching time_slice
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Time Series): Failed to map time slice or perihelion time to longitude. Falling back to time axis.")
                                        panel_actually_uses_degrees = False
                                        x_data = time_slice # Ensure fallback
                                        # data_slice remains the original full slice matching time_slice
                                except Exception as e:
                                    print_manager.error(f"Panel {i+1} (Time Series): Error during degrees from perihelion calculation: {e}")
                                    panel_actually_uses_degrees = False
                                    x_data = time_slice # Ensure fallback
                                    # data_slice remains the original full slice matching time_slice

                            # --- Center Times Degree Calculation (simpler - no lookup needed) ---
                            elif panel_uses_center_times_degrees and center_time_reference_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Time Series): Calculating Degrees from Center Time.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon', unwrap_angles=True)
                                    
                                    # 2. Use center_time directly (no lookup needed!)
                                    center_time_dt = datetime.strptime(center_time_reference_str, '%Y/%m/%d %H:%M:%S.%f')
                                    center_time_np = np.array([np.datetime64(center_time_dt)])
                                    center_time_lon_arr = positional_mapper.map_to_position(center_time_np, 'carrington_lon', unwrap_angles=True)
                                    
                                    if carrington_lons_slice is not None and center_time_lon_arr is not None and len(center_time_lon_arr) > 0:
                                        center_time_lon_val = center_time_lon_arr[0]
                                        
                                        print_manager.debug(f"[DEBUG Center Time Offset Calc - Panel {i+1}] Plot Type: Time Series")
                                        print_manager.debug(f"[DEBUG Center Time Offset Calc - Panel {i+1}] Center Time: {center_time_reference_str}")
                                        print_manager.debug(f"[DEBUG Center Time Offset Calc - Panel {i+1}] Center Time Lon Value: {center_time_lon_val:.4f}")

                                        # Create mask for valid longitude values in the slice
                                        valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                        num_valid_lons = np.sum(valid_lon_mask)

                                        if num_valid_lons > 0:
                                            # Filter slice data based on valid longitudes
                                            carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                            data_slice_filtered_lon = data_slice[valid_lon_mask]

                                            # 3. Calculate relative degrees (raw difference of unwrapped)
                                            relative_degrees = carrington_lons_slice_valid - center_time_lon_val

                                            # 4. Wrap the difference to the [-180, 180] range
                                            relative_degrees_wrapped = (relative_degrees + 180) % 360 - 180

                                            # 5. Set x_data & filtered data_slice
                                            x_data = relative_degrees_wrapped
                                            data_slice = data_slice_filtered_lon

                                            # 6. Set flags
                                            panel_actually_uses_degrees = True
                                            print_manager.debug(f"Panel {i+1}: Successfully calculated degrees from center time. Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                                            # 7. Store flag on axis
                                            axs[i]._panel_actually_used_degrees = True
                                            print_manager.debug(f"--> Stored _panel_actually_used_degrees=True on axis {i} (Time Series - Center Times)")
                                        else:
                                            print_manager.warning(f"Panel {i+1} (Time Series): No valid longitudes found for center times. Falling back to time axis.")
                                            panel_actually_uses_degrees = False
                                            x_data = time_slice # Ensure fallback
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Time Series): Failed to map center time to longitude. Falling back to time axis.")
                                        panel_actually_uses_degrees = False
                                        x_data = time_slice # Ensure fallback
                                except Exception as e:
                                    print_manager.error(f"Panel {i+1} (Time Series): Error during degrees from center time calculation: {e}")
                                    panel_actually_uses_degrees = False
                                    x_data = time_slice # Ensure fallback

                            # --- Standard Positional Mapping (if degrees not used/failed) ---
                            elif using_positional_axis and positional_mapper is not None:
                                print_manager.debug(f"Panel {i+1} (Time Series): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals) # Assign mask here too
                                    num_valid = np.sum(valid_mask)
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        # Filter data_slice *inside* this block
                                        data_slice = data_slice[valid_mask]
                                        print_manager.debug(f"Panel {i+1} (Time Series): Standard positional mapping successful, using {num_valid} valid points")
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Time Series): Standard positional mapping resulted in no valid points. Using time axis.")
                                        x_data = time_slice # Fallback to time, data_slice remains original
                                        panel_actually_uses_degrees = False # Ensure flag is False
                                else:
                                    print_manager.warning(f"Panel {i+1} (Time Series): Standard positional mapping failed (returned None). Using time axis.")
                                    x_data = time_slice # Fallback to time, data_slice remains original
                                    panel_actually_uses_degrees = False # Ensure flag is False
                            # If not using positional axis at all, x_data and data_slice remain the initial time-based slices
                            
                            # --- Transform to relative time if use_relative_time is True ---
                            if options.use_relative_time and not using_positional_axis and not panel_actually_uses_degrees:
                                # Convert datetime x_data to relative time (hours/days from center_time)
                                if hasattr(x_data, '__iter__') and len(x_data) > 0:
                                    # Convert to pandas Timestamp if needed, then calculate relative time
                                    time_deltas = pd.to_datetime(x_data) - center_dt
                                    if options.relative_time_step_units == 'days':
                                        x_data = time_deltas.total_seconds() / (3600 * 24)
                                    elif options.relative_time_step_units == 'hours':
                                        x_data = time_deltas.total_seconds() / 3600
                                    elif options.relative_time_step_units == 'minutes':
                                        x_data = time_deltas.total_seconds() / 60
                                    elif options.relative_time_step_units == 'seconds':
                                        x_data = time_deltas.total_seconds()
                                    else:
                                        # Default to hours if unit not recognized
                                        x_data = time_deltas.total_seconds() / 3600
                                    print_manager.debug(f"Panel {i+1}: Transformed x_data to relative time ({options.relative_time_step_units}). Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")

                            # --- Plot using the determined x_data and potentially filtered data_slice ---
                            # <<< DEBUG PRINT: Verify x_data just before plotting >>>
                            # print_manager.debug(f"[DEBUG] Plotting Axis {i} (Time Series)")
                            # print_manager.debug(f"  x_data (first 5): {x_data[:5]}")
                            # print_manager.debug(f"  x_data (last 5): {x_data[-5:]}")
                            # if np.issubdtype(np.array(x_data).dtype, np.number):
                            #     print_manager.debug(f"  x_data range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                            # else:
                            #     print_manager.debug(f"  x_data range: {np.min(x_data)} to {np.max(x_data)}")
                            # <<< END DEBUG >>>

                            # --- << INSERTED BLOCK >> ---
                            # --- DEBUG: Verify value at Perihelion ---
                            if panel_actually_uses_degrees and 'perihelion_dt' in locals(): # Ensure perihelion_dt was defined
                                try:
                                    perihelion_dt_np = np.datetime64(perihelion_dt)
                                    # Find index in ORIGINAL time_slice closest to the perihelion time
                                    # Ensure time_slice exists and is not empty
                                    if 'time_slice' in locals() and len(time_slice) > 0:
                                        idx_closest = np.argmin(np.abs(time_slice - perihelion_dt_np))
                                        original_time = time_slice[idx_closest]

                                        # Check if this closest point survived the valid_lon_mask filtering
                                        # Ensure valid_lon_mask was created during degree calculation
                                        if valid_lon_mask is not None and idx_closest < len(valid_lon_mask) and valid_lon_mask[idx_closest]:
                                            # Find its index in the FINAL x_data array
                                            idx_in_x_data = np.sum(valid_lon_mask[:idx_closest])
                                            # Ensure idx_in_x_data is within bounds of x_data
                                            if idx_in_x_data < len(x_data):
                                                final_x_value = x_data[idx_in_x_data]
                                                print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Perihelion: {perihelion_dt}, Closest Original Time: {original_time}, Final X-Value: {final_x_value:.5f}\u00b0")
                                            else:
                                                print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Calculated index {idx_in_x_data} out of bounds for x_data (len {len(x_data)}). Point likely at the very end and filtered.")
                                        else:
                                            # The point closest to the actual perihelion time was removed during filtering or mask unavailable
                                            print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Point closest to Perihelion ({perihelion_dt}) was filtered out by valid_lon_mask or mask not available.")
                                    else:
                                         print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Original time_slice is empty or not available.")
                                except Exception as dbg_e:
                                    print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Error during value check: {dbg_e}")

                            print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                            axs[i].plot(x_data,
                                        data_slice, # Use potentially filtered data_slice
                                        linewidth=options.magnetic_field_line_width if options.save_preset else var.line_width,
                                        linestyle=var.line_style,
                                        color=plot_color)
                        else:
                            # Handle empty data case - add a message on the plot
                            print_manager.warning(f"No data to plot for panel {i+1} - skipping plot")
                            axs[i].text(0.5, 0.5, 'No data for this time range',
                                       ha='center', va='center', transform=axs[i].transAxes,
                                       fontsize=10, color='gray', style='italic')
                        if panel_color:
                            apply_panel_color(axs[i], panel_color, options)
    
                    elif var.plot_type == 'scatter':
                        # Handle scatter plots
                        if len(indices) > 0:
                            # Determine plot color (priority: panel_color > axis_options > var.color)
                            plot_color = panel_color
                            if not plot_color:
                                plot_color = axis_options.color if axis_options.color else getattr(var, 'color', None)

                            # Get scatter-specific attributes safely
                            marker_style = getattr(var, 'marker_style', '.') # Default to small dot
                            marker_size = getattr(var, 'marker_size', 5)     # Default size
                            alpha = getattr(var, 'alpha', 1.0)               # Default alpha
                            legend_label = getattr(var, 'legend_label', None) # Get legend label if it exists

                            # Get x-axis data
                            time_slice = raw_datetime_array[indices]
                            data_slice = var.all_data[indices]
                            x_data = time_slice # Default to time

                            # --- Perihelion Degree Calculation (Scatter) --- 
                            if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Scatter): Calculating Degrees from Perihelion.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    # <<< MOVE PERIHELION LON CALCULATION *INSIDE* THIS BLOCK >>>
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon', unwrap_angles=True)
                                    
                                    # 2. Map *panel-specific* perihelion time to its longitude
                                    perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                    perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)
                                    
                                    if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                        perihelion_lon_val = perihelion_lon_arr[0]

                                        # <<< Existing Debug Prints Here >>>
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Plot Type: Scatter")
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Time Str: {perihelion_time_str}")
                                        print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Lon Value Used: {perihelion_lon_val:.4f}")

                                        # Create mask for valid longitude values in the slice
                                        valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                        num_valid_lons = np.sum(valid_lon_mask)
                                        
                                        if num_valid_lons > 0:
                                            # Filter slice data based on valid longitudes
                                            carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                            data_slice_filtered_lon = data_slice[valid_lon_mask]
                                            
                                            # 3. Calculate relative degrees (raw difference of unwrapped)
                                            relative_degrees = carrington_lons_slice_valid - perihelion_lon_val

                                            # 4. CRITICAL FIX: Wrap the difference to the [-180, 180] range
                                            relative_degrees_wrapped = (relative_degrees + 180) % 360 - 180

                                            # 5. Set x_data & filtered data_slice
                                            x_data = relative_degrees_wrapped # Use the WRAPPED version
                                            data_slice = data_slice_filtered_lon
                                            # 6. Set flags
                                            panel_actually_uses_degrees = True
                                            axs[i]._panel_actually_used_degrees = True
                                            print_manager.debug(f"--> Stored _panel_actually_used_degrees=True on axis {i} (Scatter)")
                                        else:
                                            print_manager.warning(f"Panel {i+1} (Scatter): No valid longitudes. Fallback time.")
                                            x_data = time_slice # Fallback
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Scatter): Failed map. Fallback time.")
                                        x_data = time_slice # Fallback
                                except Exception as e:
                                    print_manager.error(f"Panel {i+1} (Scatter): Error during degrees calc: {e}")
                                    x_data = time_slice # Fallback
                                    
                            # --- Standard Positional Mapping (if degrees not used/failed - Scatter) --- 
                            elif using_positional_axis and positional_mapper is not None:
                                print_manager.debug(f"Panel {i+1} (Scatter): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals)
                                    num_valid = np.sum(valid_mask)
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        data_slice = data_slice[valid_mask]
                                        print_manager.debug(f"Panel {i+1} (Scatter): Standard positional mapping successful, using {num_valid} valid points")
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Scatter): Standard positional mapping resulted in no valid points. Using time axis.")
                                        x_data = time_slice
                                else:
                                    print_manager.warning(f"Panel {i+1} (Scatter): Standard positional mapping failed (returned None). Using time axis.")
                                    x_data = time_slice
                            
                            # --- Transform to relative time if use_relative_time is True (Scatter) ---
                            if options.use_relative_time and not using_positional_axis and not panel_actually_uses_degrees:
                                # Convert datetime x_data to relative time (hours/days from center_time)
                                if hasattr(x_data, '__iter__') and len(x_data) > 0:
                                    # Convert to pandas Timestamp if needed, then calculate relative time
                                    time_deltas = pd.to_datetime(x_data) - center_dt
                                    if options.relative_time_step_units == 'days':
                                        x_data = time_deltas.total_seconds() / (3600 * 24)
                                    elif options.relative_time_step_units == 'hours':
                                        x_data = time_deltas.total_seconds() / 3600
                                    elif options.relative_time_step_units == 'minutes':
                                        x_data = time_deltas.total_seconds() / 60
                                    elif options.relative_time_step_units == 'seconds':
                                        x_data = time_deltas.total_seconds()
                                    else:
                                        # Default to hours if unit not recognized
                                        x_data = time_deltas.total_seconds() / 3600
                                    print_manager.debug(f"Panel {i+1} (Scatter): Transformed x_data to relative time ({options.relative_time_step_units}). Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")

                            # --- Plot using the determined x_data and potentially filtered data_slice --- 
                            # <<< DEBUG PRINT: Verify x_data just before plotting >>>
                            print_manager.debug(f"[DEBUG] Plotting Axis {i} (Scatter - Degrees Mode)")
                            print_manager.debug(f"  x_data (first 5): {x_data[:5]}")
                            print_manager.debug(f"  x_data (last 5): {x_data[-5:]}")
                            if np.issubdtype(np.array(x_data).dtype, np.number):
                                print_manager.debug(f"  x_data range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                            else:
                                print_manager.debug(f"  x_data range: {np.min(x_data)} to {np.max(x_data)}")
                            # <<< END DEBUG >>>
                            print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                            axs[i].scatter(x_data,
                                          data_slice, # Use filtered data_slice
                                          color=plot_color,
                                          marker=marker_style,
                                          s=marker_size,  # Note: Matplotlib uses 's' for size
                                          alpha=alpha,
                                          label=legend_label) # Add label for potential legend use

                            # Apply panel color formatting if needed
                            if panel_color:
                                apply_panel_color(axs[i], panel_color, options)
                        else:
                            # Handle empty data case for scatter plots
                            print_manager.warning(f"No scatter data to plot for panel {i+1} - skipping plot")
                            axs[i].text(0.5, 0.5, 'No data for this time range',
                                       ha='center', va='center', transform=axs[i].transAxes,
                                       fontsize=10, color='gray', style='italic')

                            # Apply panel color formatting if needed (even for empty plots)
                            if panel_color:
                                apply_panel_color(axs[i], panel_color, options)
                    
                    elif var.plot_type == 'spectral':
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: SPECTRAL PLOT TYPE DETECTED")
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Variable: {var.class_name}.{var.subclass_name}")
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Indices available: {len(indices)}")
                        raw_datetime_array = var.plot_config.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                        datetime_clipped = raw_datetime_array[indices]
                        data_clipped = np.array(var.all_data)[indices] # Use improved data handling
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: data_clipped shape: {data_clipped.shape}")
                        # Handle additional_data for spectral plots (energy/frequency channels)
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Checking additional_data...")
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: hasattr(var, 'additional_data'): {hasattr(var, 'additional_data')}")
                        if hasattr(var, 'additional_data'):
                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: var.additional_data is not None: {var.additional_data is not None}")
                            if var.additional_data is not None:
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: additional_data shape: {var.additional_data.shape}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: additional_data ndim: {var.additional_data.ndim}")
                        
                        if hasattr(var, 'additional_data') and var.additional_data is not None:
                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ✅ additional_data exists, processing...")
                            # For spectral data, additional_data represents energy channels, not time-varying data
                            # So we should NOT apply time indices to it
                            if var.additional_data.ndim == 1:
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: 📍 Taking 1D path - using additional_data directly")
                                # 1D array - use directly as energy channels
                                y_spectral_axis = var.additional_data
                            elif var.additional_data.ndim == 2:
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: 📍 Taking 2D path - using first row of additional_data")
                                # 2D array - take first row as energy channels (assuming constant across time)
                                y_spectral_axis = var.additional_data[0, :]
                            else:
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: 📍 Taking fallback path - unexpected dimensions ({var.additional_data.ndim}D)")
                                # Fallback for unexpected dimensions
                                y_spectral_axis = np.arange(data_clipped.shape[1]) if data_clipped.ndim > 1 else np.arange(len(data_clipped))
                        else:
                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: 📍 Taking no-additional_data path - generating array")
                            y_spectral_axis = np.arange(data_clipped.shape[1]) if data_clipped.ndim > 1 else np.arange(len(data_clipped))
                        
                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Final y_spectral_axis shape: {y_spectral_axis.shape}")
                        
                        colorbar_limits = axis_options.colorbar_limits if hasattr(axis_options, 'colorbar_limits') and axis_options.colorbar_limits else var.colorbar_limits
                        if var.colorbar_scale == 'log':
                            norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                        elif var.colorbar_scale == 'linear':
                            norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
    
                        # Get x-axis data
                        time_slice = datetime_clipped
                        data_slice = data_clipped # This is the 2D spectral data
                        # y_spectral_axis remains the full energy/frequency axis
                        
                        # CRITICAL FIX: Extract 1D time array for pcolormesh
                        if time_slice.ndim == 2:
                            # 2D time array - extract first column to get 1D time values
                            x_data = time_slice[:, 0]  
                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Extracted 1D time from 2D array, shape: {x_data.shape}")
                        else:
                            # Already 1D
                            x_data = time_slice
                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Using 1D time array directly, shape: {x_data.shape}")

                        # --- Perihelion Degree Calculation (Spectral) --- 
                        if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                            print_manager.debug(f"Panel {i+1} (Spectral): Calculating Degrees from Perihelion.")
                            try:
                                # 1. Map time slice to Carrington longitude
                                # <<< MOVE PERIHELION LON CALCULATION *INSIDE* THIS BLOCK >>>
                                carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon', unwrap_angles=True)
                                
                                # 2. Map *panel-specific* perihelion time to its longitude
                                perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)
                                
                                if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                    perihelion_lon_val = perihelion_lon_arr[0]

                                    # <<< Existing Debug Prints Here >>>
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Plot Type: Spectral")
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Time Str: {perihelion_time_str}")
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Lon Value Used: {perihelion_lon_val:.4f}")

                                    # Create mask for valid longitude values in the slice
                                    valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                    num_valid_lons = np.sum(valid_lon_mask)
                                    
                                    if num_valid_lons > 0:
                                        # Filter slice data based on valid longitudes
                                        carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                        # Filter the 2D spectral data along the time dimension (axis 0)
                                        data_slice_filtered_lon = data_slice[valid_lon_mask, :]
                                        
                                        # 3. Calculate relative degrees
                                        relative_degrees = carrington_lons_slice_valid - perihelion_lon_val

                                        # 5. Set x_data & filtered data_slice
                                        x_data = relative_degrees
                                        data_slice = data_slice_filtered_lon # Use filtered spectral data
                                        # 6. Set flags
                                        panel_actually_uses_degrees = True
                                        axs[i]._panel_actually_used_degrees = True
                                        print_manager.debug(f"--> Stored _panel_actually_used_degrees=True on axis {i} (Spectral)")
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Spectral): No valid longitudes. Fallback time.")
                                        x_data = time_slice # Fallback
                                        # data_slice remains original full spectral data
                                else:
                                    print_manager.warning(f"Panel {i+1} (Spectral): Failed map. Fallback time.")
                                    x_data = time_slice # Fallback
                                    # data_slice remains original full spectral data
                            except Exception as e:
                                print_manager.error(f"Panel {i+1} (Spectral): Error during degrees calc: {e}")
                                x_data = time_slice # Fallback
                                # data_slice remains original full spectral data

                        # --- Standard Positional Mapping (if degrees not used/failed - Spectral) --- 
                        elif using_positional_axis and positional_mapper is not None:
                            print_manager.debug(f"Panel {i+1} (Spectral): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                            positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                            if positional_vals is not None:
                                valid_mask = ~np.isnan(positional_vals)
                                num_valid = np.sum(valid_mask)
                                if num_valid > 0:
                                    x_data = positional_vals[valid_mask]
                                    # Filter the 2D spectral data along the time dimension
                                    data_slice = data_slice[valid_mask, :]
                                    print_manager.debug(f"Panel {i+1} (Spectral): Standard positional mapping successful, using {num_valid} valid points")
                                else:
                                    print_manager.warning(f"Panel {i+1} (Spectral): Standard positional mapping resulted in no valid points. Using time axis.")
                                    x_data = time_slice
                                    # data_slice remains original full spectral data
                            else:
                                print_manager.warning(f"Panel {i+1} (Spectral): Standard positional mapping failed (returned None). Using time axis.")
                                x_data = time_slice
                                # data_slice remains original full spectral data

                        # FIXED: Create properly shaped mesh grid for pcolormesh to avoid dimension mismatch
                        try:
                            # Remove the transpose - data should not be transposed
                            # Debug the shapes for troubleshooting
                            x_shape = len(x_data)
                            # y_shape = len(additional_data_clipped) # y_spectral_axis might change
                            z_shape = data_slice.shape # Use filtered data_slice shape
                            y_shape = z_shape[1] if len(z_shape) > 1 else 0 # Infer Y shape from Z
                            print_manager.debug(f"Spectral data shapes after filtering: X:{x_shape}, Y:{y_shape}, Z:{z_shape}")

                            print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: y_shape={y_shape}, y_spectral_axis length={len(y_spectral_axis)}")
                            # Ensure y_spectral_axis matches the Z dimension
                            if y_shape != len(y_spectral_axis):
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ❌ Y axis mismatch - y_shape={y_shape}, y_spectral_axis={len(y_spectral_axis)}")
                                print_manager.warning(f"Spectral Y axis length ({len(y_spectral_axis)}) does not match filtered data dimension ({y_shape}). Skipping plot.")
                                # Handle error: plot text or skip?
                            else:
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ✅ Y axis dimensions match, proceeding with plot")
                                # Always use 'auto' shading which handles the dimension requirements correctly
                                # and don't transpose the data
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Creating pcolormesh...")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Shapes for pcolormesh - X: {len(x_data)}, Y: {len(y_spectral_axis)}, Z: {data_slice.shape}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: x_data type: {type(x_data)}, sample values: {x_data[:3] if len(x_data) > 3 else x_data}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: y_spectral_axis type: {type(y_spectral_axis)}, sample values: {y_spectral_axis[:3] if len(y_spectral_axis) > 3 else y_spectral_axis}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: data_slice.T shape: {data_slice.T.shape}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: norm: {norm}")
                                print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: colormap: {getattr(var, 'colormap', 'None')}")
                                try:
                                    im = axs[i].pcolormesh(x_data, y_spectral_axis, data_slice.T, # Transpose needed for pcolormesh
                                                                norm=norm, cmap=var.colormap, shading='auto')
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ✅ pcolormesh created successfully!")
                                except Exception as pcolor_e:
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ❌ pcolormesh failed: {str(pcolor_e)}")
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ❌ Exception type: {type(pcolor_e)}")
                                    # Skip pcolormesh creation but continue with the panel
                                    im = None

                                if im is not None:
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Adding colorbar...")
                                    pos = axs[i].get_position()
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: Axis position - x0={pos.x0:.3f}, y0={pos.y0:.3f}, x1={pos.x1:.3f}, y1={pos.y1:.3f}, width={pos.width:.3f}, height={pos.height:.3f}")
                                    
                                    # RESTORED: Use the original working manual positioning from v2.99
                                    # This was the approach that worked perfectly before!
                                    try:
                                        # Original working positioning: width=0.02, full panel height
                                        cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                                        cbar = fig.colorbar(im, cax=cax)
                                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ✅ Colorbar added with ORIGINAL working manual positioning!")
                                    except Exception as cbar_e:
                                        print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ❌ Manual colorbar failed: {str(cbar_e)}")
                                        cbar = None

                                    if hasattr(var, 'colorbar_label') and cbar is not None:
                                        cbar.set_label(var.colorbar_label)
                                else:
                                    print_manager.test(f"[TEST SPECTRAL] Panel {i+1}: ❌ Skipping colorbar - pcolormesh failed")
                        except Exception as e:
                            print_manager.warning(f"Error plotting spectral data: {str(e)}")
                            print_manager.warning(f"Data shapes: X:{len(x_data)}, Y:{len(y_spectral_axis)}, Z:{data_slice.shape}")
                        
                        # Apply panel color formatting if needed
                        if panel_color:
                            apply_panel_color(axs[i], panel_color, options)
                else: # Default plot type (treat as time_series)
                    print('THIS IS A DEFAULT PLOT🍀🍀🍀🍀🍀🍀')
                    plot_color = panel_color
                    if not plot_color:
                        plot_color = axis_options.color if axis_options.color else var.color
                    
                    # CRITICAL FIX: Check if indices is empty before trying to plot
                    if len(indices) > 0:
                        # --- MODIFIED: X-Data Calculation --- 
                        time_slice = raw_datetime_array[indices]
                        data_slice = var.all_data[indices]
                        x_data = time_slice # Default to time
                        
                        
                                                # --- DEBUG: Verify value at Perihelion ---
                        if panel_actually_uses_degrees: # Only check if degrees were actually calculated
                            try:
                                perihelion_dt_np = np.datetime64(perihelion_dt)
                                # Find index in ORIGINAL time_slice closest to the perihelion time
                                idx_closest = np.argmin(np.abs(time_slice - perihelion_dt_np))
                                original_time = time_slice[idx_closest]

                                # Check if this closest point survived the valid_lon_mask filtering
                                if valid_lon_mask[idx_closest]:
                                    # Find its index in the FINAL x_data array
                                    idx_in_x_data = np.sum(valid_lon_mask[:idx_closest])
                                    final_x_value = x_data[idx_in_x_data]
                                    print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} Default] Perihelion: {perihelion_dt}, Closest Original Time: {original_time}, Final X-Value: {final_x_value:.5f}°") # Changed label to Default
                                else:
                                    # The point closest to the actual perihelion time was removed during filtering
                                    print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} Default] Point closest to Perihelion ({perihelion_dt}) was filtered out by valid_lon_mask.") # Changed label to Default
                            except Exception as dbg_e:
                                print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} Default] Error during value check: {dbg_e}") # Changed label to Default
                        # --- END DEBUG ---
                        
                        
                        
                        
                        print_manager.debug(f"⭐️⭐️⭐️⭐️⭐️current_panel_use_degrees: {current_panel_use_degrees}, perihelion_time_str: {perihelion_time_str}, positional_mapper: {positional_mapper} *")
                        # --- Perihelion Degree Calculation (Default) --- 
                        if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                            print_manager.debug(f"Panel {i+1} (Default): Calculating Degrees from Perihelion.")
                            try:
                                # 1. Map time slice to Carrington longitude
                                # <<< MOVE PERIHELION LON CALCULATION *INSIDE* THIS BLOCK >>>
                                carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon', unwrap_angles=True)
                                
                                # 2. Map *panel-specific* perihelion time to its longitude
                                perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)
                                
                                if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                    perihelion_lon_val = perihelion_lon_arr[0]

                                    # <<< Existing Debug Prints Here >>>
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Plot Type: Default")
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Time Str: {perihelion_time_str}")
                                    print_manager.debug(f"[DEBUG Perihelion Offset Calc - Panel {i+1}] Perihelion Lon Value Used: {perihelion_lon_val:.4f}")

                                    # Create mask for valid longitude values in the slice
                                    valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                    num_valid_lons = np.sum(valid_lon_mask)

                                    if num_valid_lons > 0:
                                        # Filter slice data based on valid longitudes
                                        carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                        data_slice_filtered_lon = data_slice[valid_lon_mask]

                                        # 3. Calculate relative degrees (raw difference of unwrapped)
                                        relative_degrees = carrington_lons_slice_valid - perihelion_lon_val

                                        # 4. CRITICAL FIX: Wrap the difference to the [-180, 180] range
                                        relative_degrees_wrapped = (relative_degrees + 180) % 360 - 180

                                        # 5. Set x_data & filtered data_slice
                                        x_data = relative_degrees_wrapped # Use the WRAPPED version
                                        data_slice = data_slice_filtered_lon
                                        x_data = relative_degrees
                                        data_slice = data_slice_filtered_lon
                                        
                                        # 6. Set flags
                                        panel_actually_uses_degrees = True
                                        axs[i]._panel_actually_used_degrees = True
                                        print_manager.debug(f"--> Stored _panel_actually_used_degrees=True on axis {i} (Default)")
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Default): No valid longitudes. Fallback time.")
                                        x_data = time_slice # Fallback
                                else:
                                    print_manager.warning(f"Panel {i+1} (Default): Failed map. Fallback time.")
                                    x_data = time_slice # Fallback
                            except Exception as e:
                                print_manager.error(f"Panel {i+1} (Default): Error during degrees calc: {e}")
                                x_data = time_slice # Fallback
                                
                        # --- Standard Positional Mapping (if degrees not used/failed - Default) --- 
                        elif using_positional_axis and positional_mapper is not None:
                            print_manager.debug(f"Panel {i+1} (Default): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                            positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                            if positional_vals is not None:
                                valid_mask = ~np.isnan(positional_vals)
                                num_valid = np.sum(valid_mask)
                                if num_valid > 0:
                                    x_data = positional_vals[valid_mask]
                                    data_slice = data_slice[valid_mask] # Filter data too
                                    print_manager.debug(f"Panel {i+1} (Default): Standard positional mapping successful, using {num_valid} valid points")
                                else:
                                    print_manager.warning(f"Panel {i+1} (Default): Standard positional mapping resulted in no valid points. Using time axis.")
                                    x_data = time_slice
                            else:
                                print_manager.warning(f"Panel {i+1} (Default): Standard positional mapping failed (returned None). Using time axis.")
                                x_data = time_slice
                        # --- END X-Data Calc --- 
                        
                        # --- Plot using potentially modified x_data and data_slice --- 
                        # <<< DEBUG PRINT: Verify x_data just before plotting >>>
                        print_manager.debug(f"[DEBUG] Plotting Axis {i} (Default - Degrees Mode)")
                        print_manager.debug(f"  x_data (first 5): {x_data[:5]}")
                        print_manager.debug(f"  x_data (last 5): {x_data[-5:]}")
                        print_manager.debug(f"  x_data range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                        # <<< END DEBUG >>>
                        
                        # print(f'panel_actually_uses_degrees: {panel_actually_uses_degrees}') #⭐️I ADDED THIS
                        # panel_actually_uses_degrees = True
                        
                         # --- DEBUG: Verify value at Perihelion --- 
                        if panel_actually_uses_degrees:
                            try:
                                perihelion_dt_np = np.datetime64(perihelion_dt) 
                                idx_closest = np.argmin(np.abs(time_slice - perihelion_dt_np))
                                original_time = time_slice[idx_closest]
                                if valid_lon_mask[idx_closest]:
                                    idx_in_x_data = np.sum(valid_lon_mask[:idx_closest])
                                    final_x_value = x_data[idx_in_x_data]
                                    print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Perihelion: {perihelion_dt}, Closest Original Time: {original_time}, Final X-Value: {final_x_value:.5f}\u00b0")
                                else:
                                    print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Point closest to Perihelion ({perihelion_dt}) was filtered out by valid_lon_mask.")
                            except Exception as dbg_e:
                                print_manager.debug(f"[DEBUG Perihelion Value Check - Panel {i+1} TimeSeries] Error during value check: {dbg_e}")
                        
                        print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                        axs[i].plot(x_data, 
                                    data_slice, # Use potentially filtered data_slice
                                    linewidth=options.magnetic_field_line_width if options.save_preset else var.line_width,
                                    linestyle=var.line_style,
                                    color=plot_color)
                    else:
                        # Handle empty data case
                        print_manager.warning(f"No data to plot for panel {i+1} - skipping plot")
                        axs[i].text(0.5, 0.5, 'No data for this time range', 
                                ha='center', va='center', transform=axs[i].transAxes,
                                fontsize=10, color='gray', style='italic')
                    
                    if panel_color:
                        apply_panel_color(axs[i], panel_color, options)
        
        # Add HAM data plotting on right axis (if enabled)
        # print_manager.debug(f"Panel {i+1}: Checking HAM plotting conditions: hamify={options.hamify}, ham_var={options.ham_var is not None}, second_variable_on_right_axis={options.second_variable_on_right_axis}") # COMMENTED OUT
        if options.hamify and options.ham_var is not None and not options.second_variable_on_right_axis:
            # For each panel, load the correct HAM data for the time range
            ham_var = options.ham_var
            # Call get_data for this panel's time range
            print_manager.debug(f"Panel {i+1}: Calling get_data for HAM variable for trange {trange}")
            # Set TimeRangeTracker for this panel's time range
            TimeRangeTracker.set_current_trange(trange)
            get_data(trange, ham_var)
            # Refresh the reference from data_cubby
            ham_class_instance = data_cubby.grab('ham')
            if ham_class_instance:
                ham_var = ham_class_instance.get_subclass(getattr(options.ham_var, 'subclass_name', 'hamogram_30s'))
                # CRITICAL FIX: Update the original options.ham_var reference to point to the refreshed instance
                options.ham_var = ham_var
                print_manager.debug(f"Panel {i+1}: Refreshed HAM variable reference from data_cubby and updated options.ham_var")
            else:
                print_manager.error(f"Panel {i+1}: Failed to get ham class from data_cubby")
            # Use ham_var for plotting below
            print_manager.debug(f"Panel {i+1}: HAM feature enabled, plotting {ham_var.subclass_name if hasattr(ham_var, 'subclass_name') else 'HAM variable'} on right axis")
            if ham_var is not None and hasattr(ham_var, 'datetime_array') and ham_var.datetime_array is not None:
                # Create a twin axis for the HAM data
                ax2 = axs[i].twinx()
                
                # Get color - use panel color if available, otherwise right axis color or ham_var's color
                if panel_color is not None:
                    plot_color = panel_color
                elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
                    plot_color = axis_options.r.color
                else:
                    plot_color = ham_var.color
                    
                # Get time-clipped indices
                print_manager.debug(f"Panel {i+1}: Attempting to time_clip HAM data with range: {trange[0]} to {trange[1]}")
                print_manager.debug(f"Panel {i+1}: HAM data range is {ham_var.datetime_array[0]} to {ham_var.datetime_array[-1]}")
                
                ham_indices = time_clip(ham_var.datetime_array, trange[0], trange[1])
                print_manager.debug(f"Panel {i+1}: Found {len(ham_indices)} HAM data points in time range")
                
                if len(ham_indices) > 0:
                    # Get x-axis data and handle positional mapping
                    # x_data = ham_var.datetime_array[ham_indices] # OLD
                    time_slice = ham_var.datetime_array[ham_indices]  # HAM uses its own datetime_array 
                    data_slice = ham_var.all_data[ham_indices]
                    x_data = time_slice # Default to time

                    if using_positional_axis and positional_mapper is not None:
                        positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                        if positional_vals is not None:
                            # --- NEW: Create mask for successful mapping --- 
                            valid_mask = ~np.isnan(positional_vals) 
                            num_valid = np.sum(valid_mask)
                            
                            if num_valid > 0:
                                x_data = positional_vals[valid_mask]
                                data_slice = data_slice[valid_mask] 
                                print_manager.debug(f"Panel {i+1}: Successfully mapped HAM data to {data_type} coordinates ({num_valid} points)")
                            else:
                                print_manager.debug(f"Panel {i+1}: HAM positional mapping resulted in no valid points. Using time.")
                        else:
                            print_manager.debug(f"Panel {i+1}: HAM positional mapping failed (returned None). Using time.")
                    
                    # --- Transform to relative time if use_relative_time is True (HAM) ---
                    if options.use_relative_time and not using_positional_axis:
                        # Convert datetime x_data to relative time (hours/days from center_time)
                        if hasattr(x_data, '__iter__') and len(x_data) > 0:
                            # Convert to pandas Timestamp if needed, then calculate relative time
                            time_deltas = pd.to_datetime(x_data) - center_dt
                            if options.relative_time_step_units == 'days':
                                x_data = time_deltas.total_seconds() / (3600 * 24)
                            elif options.relative_time_step_units == 'hours':
                                x_data = time_deltas.total_seconds() / 3600
                            elif options.relative_time_step_units == 'minutes':
                                x_data = time_deltas.total_seconds() / 60
                            elif options.relative_time_step_units == 'seconds':
                                x_data = time_deltas.total_seconds()
                            else:
                                # Default to hours if unit not recognized
                                x_data = time_deltas.total_seconds() / 3600
                            print_manager.debug(f"Panel {i+1} (HAM): Transformed x_data to relative time ({options.relative_time_step_units}). Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                    
                    # Plot the HAM data using filtered x_data and data_slice
                    print_manager.debug(f"Panel {i+1}: Plotting HAM data on right axis")
                    print_manager.processing(f"[PLOT_DEBUG Panel {i}] x_data type: {type(x_data).__name__}, first 5: {x_data[:5] if hasattr(x_data, '__getitem__') else x_data}")
                    ax2.plot(x_data, 
                            data_slice, # Use filtered data_slice
                            linewidth=ham_var.line_width,
                            linestyle=ham_var.line_style,
                            label=ham_var.legend_label,
                            color=plot_color,
                            alpha=options.ham_opacity)
                    print_manager.debug(f"Panel {i+1}: Successfully plotted HAM data on right axis")
                    
                    # Apply y-limits if specified
                    if hasattr(axis_options, 'r') and axis_options.r.y_limit is not None:
                        ax2.set_ylim(axis_options.r.y_limit)
                        print_manager.debug(f"Panel {i+1}: Applied right axis y-limits from axis_options: {axis_options.r.y_limit}")
                    elif hasattr(ham_var, 'y_limit') and ham_var.y_limit:
                        ax2.set_ylim(ham_var.y_limit)
                        print_manager.debug(f"Panel {i+1}: Applied right axis y-limits from ham_var: {ham_var.y_limit}")
                    
                    # --- NEW: Apply rainbow color to all right axis elements ---
                    if panel_color is not None:
                        # Set y-axis label color and font weight
                        ax2.yaxis.label.set_color(panel_color)
                        if hasattr(options, 'bold_y_axis_label') and options.bold_y_axis_label:
                            ax2.yaxis.label.set_weight('bold')
                        else:
                            ax2.yaxis.label.set_weight('normal')
                        # Set tick color and label size
                        ax2.tick_params(axis='y', colors=panel_color, which='both', labelsize=options.y_tick_label_font_size)
                        # Set all spines to panel color
                        for spine in ax2.spines.values():
                            spine.set_color(panel_color)
                    # --- END NEW ---
                    
                    # Include HAM in legend
                    lines_left, labels_left = axs[i].get_legend_handles_labels()
                    lines_right, labels_right = ax2.get_legend_handles_labels()
                    axs[i].legend(lines_left + lines_right, 
                                labels_left + labels_right,
                                bbox_to_anchor=(1.025, 1),
                                loc='upper left')
                    # Set legend label color to rainbow if in rainbow mode
                    if options.color_mode == 'rainbow' and panel_color is not None:
                        leg = axs[i].get_legend()
                        for text in leg.get_texts():
                            text.set_color(panel_color)
                        # Set the legend border (frame) color to match the panel color
                        leg.get_frame().set_edgecolor(panel_color)
                else:
                    print_manager.debug(f"Panel {i+1}: No HAM data points found in time range {trange[0]} to {trange[1]}")
            else:
                print_manager.debug(f"Panel {i+1}: HAM variable {getattr(ham_var, 'subclass_name', 'unknown')} has no datetime_array or is None")
                if ham_var is None:
                    print_manager.debug(f"Panel {i+1}: ham_var is None")
                elif not hasattr(ham_var, 'datetime_array'):
                    print_manager.debug(f"Panel {i+1}: ham_var has no datetime_array attribute")
                elif ham_var.datetime_array is None:
                    print_manager.status(f"Panel {i+1}: ham_var.datetime_array is None")
        else:
            # print_manager.status(f"Panel {i+1}: Not plotting HAM data - conditions not met: hamify={options.hamify}, ham_var={options.ham_var is not None}, second_variable_on_right_axis={options.second_variable_on_right_axis}") # COMMENTED OUT
            pass # Keep pass to avoid syntax error
        
        if axis_options.y_limit:
            # Determine the y_scale
            current_y_scale = None
            if isinstance(var, list):
                if hasattr(var[0], 'y_scale') and var[0].y_scale:
                    current_y_scale = var[0].y_scale
            elif hasattr(var, 'y_scale') and var.y_scale:
                # CRITICAL FIX: Check if we have data points before setting log scale
                # This fixes the "Data has no positive values, and therefore cannot be log-scaled" error
                if var.y_scale == 'log':
                    # Check if we have any data points in the current time range
                    has_data_points = False
                    if hasattr(var, 'datetime_array') and hasattr(var, 'data'):
                        indices = []
                        if len(var.datetime_array) > 0:
                            # Get indices of points within the time range
                            start_dt64 = np.datetime64(start_time)
                            end_dt64 = np.datetime64(end_time)
                            indices = np.where((np.array(var.datetime_array) >= start_dt64) & 
                                            (np.array(var.datetime_array) <= end_dt64))[0]
                            has_data_points = len(indices) > 0
                    
                    if has_data_points:
                        # Safe to set log scale since we have data points
                        current_y_scale = var.y_scale
                    else:
                        # Skip setting log scale for empty datasets
                        print_manager.warning(f"Cannot set log scale for panel {i+1} - no data points in time range")
                        # Set to linear scale instead to avoid errors
                        current_y_scale = 'linear'
                else:
                    # For non-log scales, just set directly
                    current_y_scale = var.y_scale
            
            # Validate the y_limit if we're using a log scale
            validated_y_limit = validate_log_scale_limits(
                axis_options.y_limit, 
                current_y_scale, 
                f"axis {i+1}"
            )
            print_manager.debug(f"Panel {i+1}: Validated limit: {validated_y_limit}")
            axs[i].set_ylim(validated_y_limit)
            print_manager.debug(f"Panel {i+1}: ylim after setting via axis_options: {axs[i].get_ylim()}")
        elif isinstance(var, list):
            all_data = []
            for single_var in var:
                if hasattr(single_var, 'y_limit') and single_var.y_limit:
                    all_data.extend(single_var.y_limit)
            if all_data:
                y_min, y_max = min(all_data), max(all_data)
                axs[i].set_ylim(y_min, y_max)
        elif hasattr(var, 'y_limit') and var.y_limit:
            print_manager.debug(f"Panel {i+1}: Applying var.y_limit: {var.y_limit}")
            axs[i].set_ylim(var.y_limit)
            print_manager.debug(f"Panel {i+1}: ylim after setting via var.y_limit: {axs[i].get_ylim()}")
        else:
            # Auto-scaling happens by default
            # print_manager.debug(f"Panel {i+1}: Using auto-scaling.") # COMMENTED OUT
            current_ylim = axs[i].get_ylim()
            # print_manager.debug(f"Panel {i+1}: ylim after auto-scaling: {current_ylim}") # COMMENTED OUT
    
        # Set x-axis limits - transform to relative time if use_relative_time is True
        if options.use_relative_time and not using_positional_axis:
            # Convert start_time and end_time to relative time values
            start_rel = (start_time - center_dt).total_seconds()
            end_rel = (end_time - center_dt).total_seconds()
            
            if options.relative_time_step_units == 'days':
                start_rel = start_rel / (3600 * 24)
                end_rel = end_rel / (3600 * 24)
            elif options.relative_time_step_units == 'hours':
                start_rel = start_rel / 3600
                end_rel = end_rel / 3600
            elif options.relative_time_step_units == 'minutes':
                start_rel = start_rel / 60
                end_rel = end_rel / 60
            # else: seconds - no conversion needed
            
            axs[i].set_xlim(start_rel, end_rel)
        else:
            axs[i].set_xlim(start_time, end_time)
    
        if isinstance(var, list):
            if all(hasattr(v, 'y_label') for v in var):
                y_label = var[0].y_label
            else:
                y_label = ''
        else:
            y_label = var.y_label
    
        if options.y_label_uses_encounter:
            if options.y_label_includes_time:
                y_label = f"{enc_num} Around\n{pd.Timestamp(center_time).strftime('%Y-%m-%d')}\n{pd.Timestamp(center_time).strftime('%H:%M')}"
                axs[i].set_ylabel(y_label, fontsize=options.y_axis_label_font_size, 
                                labelpad=options.y_label_pad, fontweight='bold' if options.bold_y_axis_label else 'normal',
                                ha=options.y_label_alignment)
            else:
                if options.bold_y_axis_label:
                    y_label = f"$\\mathbf{{{enc_num}}}$"
                else:
                    y_label = f"$\\mathrm{{{enc_num}}}$"
                axs[i].set_ylabel(y_label, fontsize=options.y_axis_label_font_size,
                                rotation=0, ha=options.y_label_alignment, va='center',
                                labelpad=options.y_label_pad)
        else:
            axs[i].set_ylabel(y_label, fontsize=options.y_axis_label_font_size,
                            labelpad=options.y_label_pad, fontweight='bold' if options.bold_y_axis_label else 'normal',
                            ha=options.y_label_alignment)
    
        if isinstance(var, list):
            if hasattr(var[0], 'y_scale') and var[0].y_scale:
                axs[i].set_yscale(var[0].y_scale)
        elif hasattr(var, 'y_scale') and var.y_scale:
            # CRITICAL FIX: Check if we have data points before setting log scale
            # This fixes the "Data has no positive values, and therefore cannot be log-scaled" error
            if var.y_scale == 'log':
                # Check if we have any data points in the current time range
                has_data_points = False
                if hasattr(var, 'datetime_array') and hasattr(var, 'data'):
                    indices = []
                    if len(var.datetime_array) > 0:
                        # Get indices of points within the time range
                        start_dt64 = np.datetime64(start_time)
                        end_dt64 = np.datetime64(end_time)
                        indices = np.where((np.array(var.datetime_array) >= start_dt64) & 
                                        (np.array(var.datetime_array) <= end_dt64))[0]
                        has_data_points = len(indices) > 0
                
                if has_data_points:
                    # Safe to set log scale since we have data points
                    axs[i].set_yscale(var.y_scale)
                else:
                    # Skip setting log scale for empty datasets
                    print_manager.warning(f"Cannot set log scale for panel {i+1} - no data points in time range")
                    # Set to linear scale instead to avoid errors
                    axs[i].set_yscale('linear')
            else:
                # For non-log scales, just set directly
                axs[i].set_yscale(var.y_scale)
    
        if options.use_relative_time and not using_positional_axis: # Only use relative time if NOT using longitude
            step_td = pd.Timedelta(value=options.relative_time_step, unit=options.relative_time_step_units)
            current = start_time
            ticks = []
            tick_labels = []
            while current <= end_time:
                time_from_center = (current - center_dt)
                if options.relative_time_step_units == 'days':
                    value_from_center = time_from_center.total_seconds() / (3600 * 24)
                elif options.relative_time_step_units == 'hours':
                    value_from_center = time_from_center.total_seconds() / 3600
                elif options.relative_time_step_units == 'minutes':
                    value_from_center = time_from_center.total_seconds() / 60
                elif options.relative_time_step_units == 'seconds':
                    value_from_center = time_from_center.total_seconds()
                else:
                    print(f"Unrecognized time step unit: {options.relative_time_step_units}. Please use 'days', 'hours', 'minutes', or 'seconds'.")
                    return
                
                # Append relative time value (not absolute datetime) to ticks
                ticks.append(value_from_center)
    
                if value_from_center == 0:
                    label = "0"
                else:
                    label = f"{value_from_center:.1f}".rstrip('0').rstrip('.')
                tick_labels.append(label)
                current += step_td
    
            axs[i].set_xticks(ticks)
            
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    axs[i].set_xticklabels([])
                    axs[i].set_xlabel('')
                else:
                    axs[i].set_xticklabels(tick_labels)
                    if options.use_custom_x_axis_label:
                        axs[i].set_xlabel(options.custom_x_axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                        labelpad=options.x_label_pad)
                    else:
                        relative_label = f"Relative Time ({options.relative_time_step_units} from Perihelion)"
                        axs[i].set_xlabel(relative_label, 
                                        fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                        labelpad=options.x_label_pad)
            else:
                axs[i].set_xticklabels(tick_labels)
                if i < n_panels - 1:
                    axs[i].set_xlabel('')
                else:
                    relative_label = f"Relative Time ({options.relative_time_step_units} from Perihelion)"
                    axs[i].set_xlabel(relative_label, 
                                    fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                    labelpad=options.x_label_pad)
    
            # Add these two lines to set tick label sizes when using relative time
            axs[i].tick_params(axis='x', labelsize=options.x_tick_label_font_size)
            axs[i].tick_params(axis='y', labelsize=options.y_tick_label_font_size)
    
            # After setting tick sizes 
            # Apply border line width to all spines (top, bottom, left, right)
            for spine_name, spine in axs[i].spines.items():
                spine.set_linewidth(plt.options.border_line_width)
    
        if options.draw_vertical_line:
            color_to_use = panel_color if panel_color else options.vertical_line_color

            # Default x-coordinate for the vertical line
            x_coord_for_line = center_dt

            # Check if this specific panel actually plotted data in degrees mode
            panel_is_degrees_mode = hasattr(axs[i], '_panel_actually_used_degrees') and axs[i]._panel_actually_used_degrees

            if panel_is_degrees_mode:
                # If the panel is plotted with degrees from perihelion, the vertical line (if drawn) should be at 0.
                x_coord_for_line = 0.0
                print_manager.debug(f"Panel {i}: Vertical line at x=0 (degrees_from_perihelion mode detected for panel).")
            else:
                # This debug message helps confirm non-degrees mode for the line.
                print_manager.debug(f"Panel {i}: Vertical line at x={x_coord_for_line} (standard time or non-degrees mode for panel).")

            axs[i].axvline(x=x_coord_for_line,
                           color=color_to_use,
                           linestyle=options.vertical_line_style,
                           linewidth=options.vertical_line_width)
        # --- Individual Title Setting (only if not using single title) ---
        if not options.use_single_title:
            title = f"{enc_num} - {pos_desc[options.position]} - {pd.Timestamp(center_time).strftime('%Y-%m-%d %H:%M')}"
            if options.color_mode in ['rainbow', 'single'] and panel_color:
                axs[i].set_title(title, fontsize=options.title_font_size, color=panel_color,
                               pad=options.title_pad, fontweight='bold' if options.bold_title else 'normal',
                               y=options.title_y_position)
            else:
                axs[i].set_title(title, fontsize=options.title_font_size,
                               pad=options.title_pad, fontweight='bold' if options.bold_title else 'normal',
                               y=options.title_y_position)
    
        # Check for global horizontal line
        if plt.options.draw_horizontal_line:
            axs[i].axhline(
                y=plt.options.horizontal_line_value,
                linewidth=plt.options.horizontal_line_width,
                color=plt.options.horizontal_line_color,
                linestyle=plt.options.horizontal_line_style
            )
    
        # Check for axis-specific horizontal line
        axis_options = getattr(options, f'ax{i+1}')
        if axis_options and axis_options.draw_horizontal_line:
            axs[i].axhline(
                y=axis_options.horizontal_line_value,
                linewidth=axis_options.horizontal_line_width,
                color=axis_options.horizontal_line_color,
                linestyle=axis_options.horizontal_line_style
            )
    
        # Apply border line width to all spines (top, bottom, left, right)
        for spine_name, spine in axs[i].spines.items():
            spine.set_linewidth(plt.options.border_line_width)
    
    if not options.use_relative_time or using_positional_axis: # If NOT relative time, OR if using longitude (which disables relative)
        for i, ax in enumerate(axs):
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    ax.set_xticklabels([])
                    ax.set_xlabel('')
                else:
                    # --- APPLY X LABEL LOGIC HERE ---
                    if using_positional_axis:
                        # When positional mapping is enabled, use the appropriate axis label
                        ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
                    elif options.use_custom_x_axis_label:
                        # Only use custom label if not using positional mapping
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
                    else:
                        # Default time label
                        ax.set_xlabel("Time", fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
            else: # Not using single x axis
                # --- APPLY X LABEL LOGIC HERE TOO ---
                if i == len(axs) - 1: # Apply label only to bottom-most axis if not single
                    if using_positional_axis:
                        # When positional mapping is enabled, use the appropriate axis label
                        ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
                    elif options.use_custom_x_axis_label:
                        # Only use custom label if not using positional mapping
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
                    else:
                        # Default time label
                        ax.set_xlabel("Time", fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                      labelpad=options.x_label_pad)
                else: # Hide labels for upper panels if not single axis mode
                    ax.set_xlabel('')
    
            # Apply tick size formatting for Time or Longitude axis
            if not using_positional_axis and not options.use_relative_time: # Standard Time Formatting (but not if using relative time)
                locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                formatter = mdates.ConciseDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
            else: # Configure axis for positional data display with appropriate limits
                # This is critical - set up proper formatting for positional axis
                print_manager.debug(f"Setting up axis {i} for {data_type} display")
                
                # Calculate number of ticks based on density multiplier
                # Base number of ticks is 5, multiplied by the density factor
                num_ticks = 5 * options.positional_tick_density
                print_manager.debug(f"Using {num_ticks} ticks for {data_type} axis (density={options.positional_tick_density}x)")
                
                # Set ticks for positional data
                ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
                
                # Use a simple numeric formatter with appropriate units
                if data_type == 'carrington_lon' or data_type == 'carrington_lat':
                    def angle_formatter(x, pos):
                        if x == int(x):
                            return f"{int(x)}°"
                        else:
                            return f"{x:.1f}°"
                        ax.xaxis.set_major_formatter(FuncFormatter(angle_formatter))
                else:  # radial
                    def radial_formatter(x, pos):
                        if x == int(x):
                            return f"{int(x)}"
                        else:
                            return f"{x:.1f}"
                    ax.xaxis.set_major_formatter(FuncFormatter(radial_formatter))
                
                # IMPORTANT FIX: Hide tick labels for all but bottom plot when using single x-axis
                if options.use_single_x_axis and i < len(axs) - 1:
                    ax.set_xticklabels([])
                    print_manager.debug(f"Hiding x tick labels for panel {i} (not bottom panel)")
                
                # Set axis limits based on user preference or data
                if options.x_axis_positional_range is not None:
                    # User specified a fixed range for positional axis
                    min_val, max_val = options.x_axis_positional_range
                    ax.set_xlim(min_val, max_val)
                    print_manager.debug(f"Using user-specified positional range for axis {i}: {min_val} to {max_val}")
                else:
                    # Calculate range from data
                    lines = ax.get_lines()
                    if lines and len(lines) > 0 and len(lines[0].get_xdata()) > 0:
                        x_data = lines[0].get_xdata()
                        min_val = np.min(x_data)
                        max_val = np.max(x_data)
                        
                        # Store the data ranges for each panel (needed for common x-axis logic)
                        if not hasattr(ax, '_positional_data_range'):
                            ax._positional_data_range = (min_val, max_val)
                            
                        # Apply panel-specific range immediately if not using common x-axis
                        if not options.use_single_x_axis:
                            # Add reasonable padding
                            data_range = max_val - min_val
                            padding = data_range * 0.05  # 5% padding
                            ax.set_xlim(min_val - padding, max_val + padding)
                            print_manager.debug(f"Set individual range for axis {i}: {min_val-padding:.2f} to {max_val+padding:.2f}")
                    else:
                        print_manager.warning(f"No {data_type} data found for axis {i}, using default limits")
                        # Default range depends on data type
                        if data_type == 'carrington_lon':
                            ax.set_xlim(0, 90)  # Default longitude range
                        elif data_type == 'carrington_lat':
                            ax.set_xlim(-10, 10)  # Default latitude range
                        else:  # radial
                            ax.set_xlim(0, 50)  # Default radial range

            ax.tick_params(axis='x', labelsize=options.x_tick_label_font_size)
            ax.tick_params(axis='y', labelsize=options.y_tick_label_font_size)
    
    # Apply common x-axis range if needed
    if using_positional_axis and options.use_single_x_axis and options.x_axis_positional_range is None:
        # Find the global min and max across all axes
        all_mins = []
        all_maxs = []
        for ax in axs:
            if hasattr(ax, '_positional_data_range'):
                min_val, max_val = ax._positional_data_range
                # Only include numeric values for positional axis scaling
                if isinstance(min_val, (int, float, np.number)) and isinstance(max_val, (int, float, np.number)):
                    all_mins.append(min_val)
                    all_maxs.append(max_val)
                else:
                    print_manager.warning(f"Non-numeric values found in positional data range: {type(min_val)}, {type(max_val)}")
        
        # --- Explicitly filter lists again to ensure only numerics remain ---
        initial_min_count = len(all_mins)
        numeric_mins = [m for m in all_mins if isinstance(m, (int, float, np.number))]
        numeric_maxs = [m for m in all_maxs if isinstance(m, (int, float, np.number))]
        
        if len(numeric_mins) != initial_min_count:
             print_manager.warning(f"Filtered out {initial_min_count - len(numeric_mins)} non-numeric values from positional range calculation. Check axis types.")

        # Now use the filtered lists
        if numeric_mins and numeric_maxs:
            global_min = min(numeric_mins)
            global_max = max(numeric_maxs)
            data_range = global_max - global_min
            padding = data_range * 0.05  # 5% padding
            global_min -= padding
            global_max += padding
            
            # Apply the global range to all axes
            for ax in axs:
                ax.set_xlim(global_min, global_max)
            
            print_manager.debug(f"Applied common x-axis range to all panels: {global_min:.2f} to {global_max:.2f}")
            
    # --- Final plot adjustments (Labels, titles, legends, grid) ---
    
    # NEW: Apply dynamic x-axis tick coloring for all panels (changed from only bottom panel)
    if color_scheme:
        for i, ax in enumerate(axs):
            apply_bottom_axis_color(ax, color_scheme['panel_colors'][i])
    
    # --- Figure-Level Title Setting (when using single title) --- 
    if options.use_single_title:
        if options.single_title_text:
            title_text = options.single_title_text
        else:
            # Construct default title
            enc_nums = []
            for center_time, _ in plot_list:
                time_dt = str_to_datetime(center_time) if isinstance(center_time, str) else center_time
                enc_num = get_encounter_number(time_dt)
                if enc_num not in enc_nums:
                    enc_nums.append(enc_num)
                    
            enc_nums_str = ", ".join(enc_nums)
            title_text = f"{enc_nums_str} - {pos_desc[options.position]}"

        # Add title color if using rainbow color mode
        title_kwargs = {
            'fontsize': options.title_font_size,
            'pad': options.title_pad,
            'fontweight': 'bold' if options.bold_title else 'normal'
        }
        
        if options.color_mode == 'rainbow' and color_scheme and color_scheme['panel_colors']:
            title_kwargs['color'] = color_scheme['panel_colors'][0]  # Use color of first panel
            
        # Place title on the top axis instead of using suptitle
        # This keeps it properly aligned with the plots regardless of panel count
        axs[0].set_title(title_text, y=options.title_y_position, **title_kwargs)
        print_manager.debug(f"Added title to top axis with pad={options.title_pad}")
    
    print_manager.status("Generating multiplot...\n")
    
    #==========================================================================
    # STEP 5: FINAL AXIS FORMATTING (Ticks, Labels, Limits)
    #==========================================================================
    print_manager.processing("[XAXIS_FORMATTING] Entering consolidated x-axis formatting block.")
    for i, ax in enumerate(axs):
        # Determine the mode for the current axis for formatting
        current_axis_mode = data_type
        if data_type == 'degrees_from_perihelion':
            if not (hasattr(ax, '_panel_actually_used_degrees') and ax._panel_actually_used_degrees):
                current_axis_mode = 'time'
                print_manager.debug(f"Panel {i}: Global mode is 'degrees_from_perihelion', but panel fell back. Formatting as 'time'.")
        print_manager.debug(f"Panel {i}: Final formatting using current_axis_mode = '{current_axis_mode}', global_data_type_for_x-axis = '{data_type}'")

        # X-Axis Label AND Tick Label Visibility
        if options.use_single_x_axis:
            if i == len(axs) - 1: # If it's the bottom panel
                if not options.use_relative_time:
                    # Only set label if not using relative time (which already set its own label)
                    ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                ax.tick_params(axis='x', labelbottom=True) # Ensure tick labels are on for bottom
            else: # If it's not the bottom panel
                ax.set_xlabel('')
                ax.set_xticklabels([]) # Hide tick labels
                ax.tick_params(axis='x', labelbottom=False) # Explicitly turn off tick labels
        else: # If not using single_x_axis (each panel gets its own)
            if not options.use_relative_time:
                # Only set label if not using relative time (which already set its own label)
                ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
            ax.tick_params(axis='x', labelbottom=True) # Ensure tick labels are on for all panels

        # X-Axis Tick Formatter and Locator (consolidated)
        if current_axis_mode == 'time' and not options.use_relative_time:
            locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
            formatter = mdates.ConciseDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
        elif current_axis_mode == 'relative_time':
            # (Assume relative time logic is handled elsewhere, or add here if needed)
            pass
        elif current_axis_mode in ['degrees_from_perihelion', 'degrees_from_center_times', 'carrington_lon', 'carrington_lat']:
            num_ticks = 5 * options.positional_tick_density
            ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
            def angle_formatter(x, pos):
                if x == int(x):
                    return f"{int(x)}°"
                else:
                    return f"{x:.1f}°"
            ax.xaxis.set_major_formatter(FuncFormatter(angle_formatter))
        elif current_axis_mode == 'r_sun':
            num_ticks = 5 * options.positional_tick_density
            ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
            def radial_formatter(x, pos):
                if x == int(x):
                    return f"{int(x)}"
                else:
                    return f"{x:.1f}"
            ax.xaxis.set_major_formatter(FuncFormatter(radial_formatter))
        else:
            print_manager.debug(f"Panel {i}: Unknown axis mode '{current_axis_mode}', letting Matplotlib handle defaults.")

        # X-Axis Limits (consolidated)
        fixed_range = None
        if current_axis_mode == 'degrees_from_perihelion' and hasattr(options, 'degrees_from_perihelion_range') and options.degrees_from_perihelion_range:
            fixed_range = options.degrees_from_perihelion_range
            ax.set_xlim(fixed_range)
        elif current_axis_mode == 'degrees_from_center_times' and hasattr(options, 'degrees_from_center_times_range') and options.degrees_from_center_times_range:
            fixed_range = options.degrees_from_center_times_range
            ax.set_xlim(fixed_range)
        elif current_axis_mode in ['carrington_lon', 'carrington_lat'] and options.x_axis_positional_range:
            fixed_range = options.x_axis_positional_range
            ax.set_xlim(fixed_range)
        # (Add more limit logic as needed for other axis types)

        # Tick label size
        ax.tick_params(axis='x', labelsize=options.x_tick_label_font_size)
        ax.tick_params(axis='y', labelsize=options.y_tick_label_font_size)

    print_manager.processing("[XAXIS_FORMATTING] Exiting consolidated x-axis formatting block.")
    
    print_manager.debug("=== Multiplot Complete ===\n")
    
    # Handle figure display and return based on ploptions
    if ploptions.display_figure:
        plt.show()
    
    if ploptions.return_figure:
        return fig
    else:
        return fig, axs  # Backward compatibility when not returning figure

print('📈📉 Multiplot Initialized')