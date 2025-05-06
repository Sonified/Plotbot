# Import plotbot components with relative imports
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

    # --- DEBUG: Print initial relevant options --- 
    print("[Multiplot Start] Initial Options State:")
    print(f"  x_axis_r_sun: {getattr(options, 'x_axis_r_sun', 'N/A')}")
    print(f"  x_axis_carrington_lon: {getattr(options, 'x_axis_carrington_lon', 'N/A')}")
    print(f"  x_axis_carrington_lat: {getattr(options, 'x_axis_carrington_lat', 'N/A')}")
    print(f"  use_degrees_from_perihelion: {getattr(options, 'use_degrees_from_perihelion', 'N/A')}")
    print(f"  use_relative_time: {getattr(options, 'use_relative_time', 'N/A')}")
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
        getattr(options, 'use_degrees_from_perihelion', False) # Added perihelion option
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
            print_manager.error("❌ Positional data path (options.positional_data_path) is not set. Cannot use positional x-axis or degrees from perihelion.")
            # Disable positional features if path is missing
            if hasattr(options, 'use_degrees_from_perihelion'): options.use_degrees_from_perihelion = False
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
            
            if not mapper_loaded:
                print_manager.warning("❌ Failed to load positional data. Disabling positional x-axis and degrees from perihelion.")
                if hasattr(options, 'use_degrees_from_perihelion'): options.use_degrees_from_perihelion = False
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
                    options.use_relative_time = False # Explicitly disable relative time
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
    print("[Multiplot Mode Determined] State:")
    print(f"  data_type: {data_type}")
    print(f"  axis_label: {axis_label}")
    print(f"  using_positional_axis: {using_positional_axis}")
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
                get_data(trange, var) # <<< USE CENTRAL get_data function >>>

                # After get_data, the variable instance in data_cubby should be updated.
                # We need to retrieve the potentially updated variable to use for plotting.
                class_instance = data_cubby.grab(var.class_name)
                if class_instance:
                    updated_var = class_instance.get_subclass(var.subclass_name)
                    if updated_var is not None:
                        # Update the plot_list with the potentially updated variable instance
                        plot_list[i] = (center_time, updated_var)
                        print_manager.custom_debug(f"✅ Refreshed variable reference in plot_list for {var.class_name}.{var.subclass_name}")
                        # <<< NEW DEBUG >>>
                        print_manager.debug(f"Loop 1, Panel {i+1}: Stored var ID in plot_list: {id(plot_list[i][1])}")
                        # <<< END NEW DEBUG >>>
                        # Optional: Add check if data is now present
                        # has_data_after_get = hasattr(updated_var, 'datetime_array') and updated_var.datetime_array is not None and len(updated_var.datetime_array) > 0
                        # print_manager.custom_debug(f"  Variable has data after get_data: {has_data_after_get}")
                    else:
                        print_manager.warning(f"❌ Failed to get updated subclass {var.subclass_name} after get_data")
                else:
                    print_manager.warning(f"❌ Failed to get class instance {var.class_name} from data_cubby after get_data")
            except Exception as e:
                print_manager.warning(f"❌ Error during get_data or variable update for {var.class_name}.{var.subclass_name}: {str(e)}")
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
        fig, axs = plt.subplots(n_panels, 1, figsize=figsize, dpi=dpi, constrained_layout=options.constrained_layout)
        print_manager.status(f"Using constrained_layout={options.constrained_layout} and letting matplotlib handle all margins and spacing.")
        # If constrained_layout is False, set all margins and hspace using the options
        if not options.constrained_layout:
            fig.subplots_adjust(
                top=options.margin_top,
                bottom=options.margin_bottom,
                left=options.margin_left,
                right=options.margin_right,
                hspace=options.hspace_vertical_space_between_plots
            )
            print_manager.status(f"Set margins (top={options.margin_top}, bottom={options.margin_bottom}, left={options.margin_left}, right={options.margin_right}) and hspace={options.hspace_vertical_space_between_plots}")
        else:
            if hasattr(options, 'hspace_vertical_space_between_plots') and options.hspace_vertical_space_between_plots != 0.2:
                print_manager.warning("hspace_vertical_space_between_plots is set but constrained_layout=True, so it will be ignored.")
    else:
        fig, axs = plt.subplots(n_panels, 1, figsize=(options.width, options.height_per_panel * n_panels), constrained_layout=options.constrained_layout)
        print_manager.status(f"Using constrained_layout={options.constrained_layout} and letting matplotlib handle all margins and spacing.")
        if not options.constrained_layout:
            fig.subplots_adjust(
                top=options.margin_top,
                bottom=options.margin_bottom,
                left=options.margin_left,
                right=options.margin_right,
                hspace=options.hspace_vertical_space_between_plots
            )
            print_manager.status(f"Set margins (top={options.margin_top}, bottom={options.margin_bottom}, left={options.margin_left}, right={options.margin_right}) and hspace={options.hspace_vertical_space_between_plots}")
        else:
            if hasattr(options, 'hspace_vertical_space_between_plots') and options.hspace_vertical_space_between_plots != 0.2:
                print_manager.warning("hspace_vertical_space_between_plots is set but constrained_layout=True, so it will be ignored.")
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

        # <<< MODIFIED DEBUG >>>
        print_manager.custom_debug(f'Adding data to plot panel {i+1}/{n_panels}... Var ID from plot_list: {id(var)}\n')
        # <<< END MODIFIED DEBUG >>>
        # Add diagnostic for HAM feature status
        print_manager.debug(f"Panel {i+1} - HAM feature status: hamify={options.hamify}, ham_var={options.ham_var is not None}")
        # center_dt = pd.Timestamp(center_time) # Moved up

        # <<< NEW: Get perihelion time and determine if this panel should use degrees >>>
        if using_positional_axis and getattr(options, 'use_degrees_from_perihelion', False):
            try:
                perihelion_time_str = get_perihelion_time(center_dt)
                if perihelion_time_str:
                    print_manager.debug(f"Panel {i+1}: Found perihelion time: {perihelion_time_str}")
                    current_panel_use_degrees = True
                else:
                    print_manager.status(f"Panel {i+1}: Perihelion time not found for {center_dt}. Cannot use degrees from perihelion for this panel.")
                    current_panel_use_degrees = False
            except Exception as e:
                print_manager.error(f"Panel {i+1}: Error getting perihelion time: {e}")
                current_panel_use_degrees = False
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
                    indices = time_clip(single_var.datetime_array, trange[0], trange[1])
                else:
                    print_manager.warning(f"Empty datetime_array for panel {i+1} - cannot clip times")

                if len(indices) > 0:
                    print_manager.time_tracking(f"Panel {i+1} time_clip returned {len(indices)} points: first={single_var.datetime_array[indices[0]]}, last={single_var.datetime_array[indices[-1]]}")
                    
                    if idx == 1 and options.second_variable_on_right_axis:
                        ax2 = axs[i].twinx()
                        
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
                            plot_color = axis_options.r.color
                        else:
                            plot_color = single_var.color
    
                        # Get x-axis data - use longitude if available
                        # x_data = single_var.datetime_array[indices] # OLD: Start with time
                        time_slice = single_var.datetime_array[indices]
                        data_slice = single_var.data[indices]
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

                        # --- Use filtered x_data and data_slice --- 
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
                        # x_data = single_var.datetime_array[indices] # OLD
                        time_slice = single_var.datetime_array[indices]
                        data_slice = single_var.data[indices]
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
                        
                        # --- Use filtered x_data and data_slice --- 
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
                indices = time_clip(var.datetime_array, trange[0], trange[1])
            else:
                print_manager.warning(f"Empty datetime_array for panel {i+1} - cannot clip times")

            if len(indices) > 0:
                print_manager.time_tracking(f"Panel {i+1} time_clip returned {len(indices)} points: first={var.datetime_array[indices[0]]}, last={var.datetime_array[indices[-1]]}")
                
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
                            time_slice = var.datetime_array[indices]
                            data_slice = var.data[indices]
                            x_data = time_slice # Default to time

                            # --- Perihelion Degree Calculation --- 
                            if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Time Series): Calculating Degrees from Perihelion.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon')
                                    
                                    # 2. Map perihelion time to its longitude
                                    # Convert string to datetime object first
                                    perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                    perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon')
                                    
                                    # Check if mapping was successful
                                    if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                        perihelion_lon_val = perihelion_lon_arr[0]
                                        print_manager.debug(f"  Perihelion Lon: {perihelion_lon_val:.2f}")
                                        
                                        # Create mask for valid longitude values in the slice
                                        valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                        num_valid_lons = np.sum(valid_lon_mask)
                                        print_manager.debug(f"  Found {num_valid_lons} valid longitudes in the time slice.")
                                        
                                        if num_valid_lons > 0:
                                            # Filter slice data based on valid longitudes
                                            carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                            data_slice_filtered_lon = data_slice[valid_lon_mask]
                                            print_manager.debug(f"  Peri Lon Value: {perihelion_lon_val:.2f}") # DEBUG
                                            print_manager.debug(f"  Carrington Lons Slice (Valid): Range {np.nanmin(carrington_lons_slice_valid):.2f} to {np.nanmax(carrington_lons_slice_valid):.2f}") # DEBUG
                                            
                                            # 3. Calculate relative degrees using only valid longitudes
                                            relative_degrees = carrington_lons_slice_valid - perihelion_lon_val
                                            
                                            # 4. Apply wrap-around
                                            relative_degrees[relative_degrees > 180] -= 360
                                            relative_degrees[relative_degrees <= -180] += 360
                                            
                                            # 5. Set x_data for plotting
                                            x_data = relative_degrees
                                            # 5b. Update data_slice to match the filtered x_data
                                            data_slice = data_slice_filtered_lon
                                            
                                            # 6. Set panel flag
                                            panel_actually_uses_degrees = True
                                            print_manager.debug(f"  Successfully calculated relative degrees. Range: {np.nanmin(x_data):.2f} to {np.nanmax(x_data):.2f}")
                                            
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
                                    
                            # --- Standard Positional Mapping (if degrees not used/failed) --- 
                            elif using_positional_axis and positional_mapper is not None:
                                print_manager.debug(f"Panel {i+1} (Time Series): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals)
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

                            # --- Plot using the determined x_data and potentially filtered data_slice --- 
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
                            time_slice = var.datetime_array[indices]
                            data_slice = var.data[indices]
                            x_data = time_slice # Default to time

                            # --- Perihelion Degree Calculation (Scatter) --- 
                            if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Scatter): Calculating Degrees from Perihelion.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon')
                                    
                                    # 2. Map perihelion time to its longitude
                                    perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                    perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon')
                                    
                                    if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                        perihelion_lon_val = perihelion_lon_arr[0]
                                        
                                        # Create mask for valid longitude values in the slice
                                        valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                        num_valid_lons = np.sum(valid_lon_mask)
                                        
                                        if num_valid_lons > 0:
                                            # Filter slice data based on valid longitudes
                                            carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                            data_slice_filtered_lon = data_slice[valid_lon_mask]
                                            
                                            # 3. Calculate relative degrees
                                            relative_degrees = carrington_lons_slice_valid - perihelion_lon_val
                                            
                                            # 4. Apply wrap-around
                                            relative_degrees[relative_degrees > 180] -= 360
                                            relative_degrees[relative_degrees <= -180] += 360
                                            
                                            # 5. Set x_data & filtered data_slice
                                            x_data = relative_degrees
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

                            # --- Plot using the determined x_data and potentially filtered data_slice --- 
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
                        # CRITICAL FIX: Check if indices is empty before trying to plot spectral data
                        if len(indices) > 0:
                            datetime_clipped = var.datetime_array[indices]
                            data_clipped = np.array(var.data)[indices] # This is the 2D spectral data (Z)
                            y_spectral_axis = np.array(var.additional_data) # This is the y-axis (e.g., energy bins)
                            
                            colorbar_limits = axis_options.colorbar_limits if hasattr(axis_options, 'colorbar_limits') and axis_options.colorbar_limits else var.colorbar_limits
                            if var.colorbar_scale == 'log':
                                norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                            elif var.colorbar_scale == 'linear':
                                norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
        
                            # Get x-axis data
                            time_slice = datetime_clipped
                            data_slice = data_clipped # This is the 2D spectral data
                            # y_spectral_axis remains the full energy/frequency axis
                            x_data = time_slice # Default to time

                            # --- Perihelion Degree Calculation (Spectral) --- 
                            if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                                print_manager.debug(f"Panel {i+1} (Spectral): Calculating Degrees from Perihelion.")
                                try:
                                    # 1. Map time slice to Carrington longitude
                                    carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon')
                                    
                                    # 2. Map perihelion time to its longitude
                                    perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                    perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon')
                                    
                                    if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                        perihelion_lon_val = perihelion_lon_arr[0]
                                        
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
                                            
                                            # 4. Apply wrap-around
                                            relative_degrees[relative_degrees > 180] -= 360
                                            relative_degrees[relative_degrees <= -180] += 360
                                            
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

                                # Ensure y_spectral_axis matches the Z dimension
                                if y_shape != len(y_spectral_axis):
                                    print_manager.warning(f"Spectral Y axis length ({len(y_spectral_axis)}) does not match filtered data dimension ({y_shape}). Skipping plot.")
                                    # Handle error: plot text or skip?
                                else:
                                    # Always use 'auto' shading which handles the dimension requirements correctly
                                    # and don't transpose the data
                                    im = axs[i].pcolormesh(x_data, y_spectral_axis, data_slice.T, # Transpose needed for pcolormesh
                                                                norm=norm, cmap=var.colormap, shading='auto')

                                    pos = axs[i].get_position()
                                    cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                                    cbar = fig.colorbar(im, cax=cax)

                                    if hasattr(var, 'colorbar_label'):
                                        cbar.set_label(var.colorbar_label)
                            except Exception as e:
                                print_manager.warning(f"Error plotting spectral data: {str(e)}")
                                print_manager.warning(f"Data shapes: X:{len(x_data)}, Y:{len(y_spectral_axis)}, Z:{data_slice.shape}")

                else: # Default plot type (treat as time_series)
                    plot_color = panel_color
                    if not plot_color:
                        plot_color = axis_options.color if axis_options.color else var.color
                    
                    # CRITICAL FIX: Check if indices is empty before trying to plot
                    if len(indices) > 0:
                        # --- MODIFIED: X-Data Calculation --- 
                        time_slice = var.datetime_array[indices]
                        data_slice = var.data[indices]
                        x_data = time_slice # Default to time
                        
                        # --- Perihelion Degree Calculation (Default) --- 
                        if current_panel_use_degrees and perihelion_time_str and positional_mapper:
                            print_manager.debug(f"Panel {i+1} (Default): Calculating Degrees from Perihelion.")
                            try:
                                # 1. Map time slice to Carrington longitude
                                carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon')
                                
                                # 2. Map perihelion time to its longitude
                                perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
                                perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
                                perihelion_lon_arr = positional_mapper.map_to_position(perihelion_time_np, 'carrington_lon')
                                
                                if carrington_lons_slice is not None and perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0:
                                    perihelion_lon_val = perihelion_lon_arr[0]
                                    
                                    # Create mask for valid longitude values in the slice
                                    valid_lon_mask = ~np.isnan(carrington_lons_slice)
                                    num_valid_lons = np.sum(valid_lon_mask)
                                    
                                    if num_valid_lons > 0:
                                        # Filter slice data based on valid longitudes
                                        carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
                                        data_slice_filtered_lon = data_slice[valid_lon_mask]
                                        
                                        # 3. Calculate relative degrees
                                        relative_degrees = carrington_lons_slice_valid - perihelion_lon_val
                                        
                                        # 4. Apply wrap-around
                                        relative_degrees[relative_degrees > 180] -= 360
                                        relative_degrees[relative_degrees <= -180] += 360
                                        
                                        # 5. Set x_data & filtered data_slice
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
            get_data(trange, ham_var)
            # Refresh the reference from data_cubby
            ham_class_instance = data_cubby.grab('ham')
            if ham_class_instance:
                ham_var = ham_class_instance.get_subclass(getattr(options.ham_var, 'subclass_name', 'hamogram_30s'))
                print_manager.debug(f"Panel {i+1}: Refreshed HAM variable reference from data_cubby")
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
                    time_slice = ham_var.datetime_array[ham_indices]
                    data_slice = ham_var.data[ham_indices]
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
                                print_manager.status(f"Panel {i+1}: HAM positional mapping resulted in no valid points. Using time.")
                        else:
                            print_manager.status(f"Panel {i+1}: HAM positional mapping failed (returned None). Using time.")
                    
                    # Plot the HAM data using filtered x_data and data_slice
                    print_manager.debug(f"Panel {i+1}: Plotting HAM data on right axis")
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
                    print_manager.status(f"Panel {i+1}: No HAM data points found in time range {trange[0]} to {trange[1]}")
            else:
                print_manager.status(f"Panel {i+1}: HAM variable {getattr(ham_var, 'subclass_name', 'unknown')} has no datetime_array or is None")
                if ham_var is None:
                    print_manager.status(f"Panel {i+1}: ham_var is None")
                elif not hasattr(ham_var, 'datetime_array'):
                    print_manager.status(f"Panel {i+1}: ham_var has no datetime_array attribute")
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
                ticks.append(current)
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
                        axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Perihelion)", 
                                        fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                        labelpad=options.x_label_pad)
            else:
                axs[i].set_xticklabels(tick_labels)
                if i < n_panels - 1:
                    axs[i].set_xlabel('')
    
            # Add these two lines to set tick label sizes when using relative time
            axs[i].tick_params(axis='x', labelsize=options.x_tick_label_font_size)
            axs[i].tick_params(axis='y', labelsize=options.y_tick_label_font_size)
    
            # After setting tick sizes 
            # Apply border line width to all spines (top, bottom, left, right)
            for spine_name, spine in axs[i].spines.items():
                spine.set_linewidth(plt.options.border_line_width)
    
        if options.draw_vertical_line:
            color_to_use = panel_color if panel_color else options.vertical_line_color
            axs[i].axvline(x=center_dt, 
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
            if not using_positional_axis: # Standard Time Formatting
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
    print_manager.debug("Starting final axis formatting loop...")
    for i, ax in enumerate(axs):
        # --- Determine Current Axis Mode --- 
        # Trust the data_type determined during initialization, 
        # but double-check with the flag for perihelion degrees specifically.
        panel_used_degrees = getattr(ax, '_panel_actually_used_degrees', False)
        current_axis_mode = 'time' # Default

        if using_positional_axis:
            # If the flag indicates degrees were used, trust it absolutely.
            if panel_used_degrees and data_type == 'degrees_from_perihelion':
                 current_axis_mode = 'degrees_from_perihelion'
            # Otherwise, use the initially determined data_type if it's positional.
            elif data_type in ['degrees_from_perihelion', 'carrington_lon', 'r_sun', 'carrington_lat']:
                # If the flag is False but data_type is perihelion, warn about inconsistency
                if not panel_used_degrees and data_type == 'degrees_from_perihelion':
                     print_manager.warning(f"Axis {i}: Inconsistency - data_type is 'degrees_from_perihelion' but panel flag is False. Proceeding with degree formatting.")
                current_axis_mode = data_type 
            # else: remains 'time' (shouldn't happen if using_positional_axis is True and data_type was set)
        elif options.use_relative_time:
             current_axis_mode = 'relative_time' # Need a distinct mode for relative time
        # else: remains 'time'
        
        # --- DEBUG: Print determined axis mode for this panel --- 
        print(f"[Final Format Loop - Axis {i}] Determined current_axis_mode: '{current_axis_mode}'")
        # --- END DEBUG --- 

        # --- Apply Formatting Based on Mode --- 
        # Note: Added distinct 'relative_time' mode check
        if current_axis_mode == 'time':
            print_manager.debug(f"Axis {i}: Applying standard Time formatting.")
            locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
            formatter = mdates.ConciseDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            # Set x-label using the globally determined axis_label
            if options.use_single_x_axis:
                if i == len(axs) - 1:
                    ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                    # print_manager.debug(f"  Set bottom x-label: '{axis_label}'") # Use axis_label - Reduced verbosity
                else:
                    ax.set_xlabel('')
            else:
                ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                # print_manager.debug(f"  Set individual x-label: '{axis_label}'") # Use axis_label - Reduced verbosity

        elif current_axis_mode == 'degrees_from_perihelion' or current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat':
            print_manager.debug(f"Axis {i}: Entering DEGREE formatting block ({current_axis_mode}).")
            
            # --- TICK LOCATOR --- 
            tick_step = None
            if current_axis_mode == 'degrees_from_perihelion' and hasattr(options, 'degrees_from_perihelion_tick_step') and options.degrees_from_perihelion_tick_step:
                tick_step = options.degrees_from_perihelion_tick_step
                print_manager.debug(f"  Using fixed tick step for degrees_from_perihelion: {tick_step}")
            # Add elif for potential future fixed steps for lon/lat if needed
            
            if tick_step:
                # Use FixedLocator if a specific step is provided
                start_tick = np.ceil(ax.get_xlim()[0] / tick_step) * tick_step
                end_tick = np.floor(ax.get_xlim()[1] / tick_step) * tick_step
                ticks = np.arange(start_tick, end_tick + tick_step, tick_step)
                ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
                print_manager.debug(f"  Applied FixedLocator with step {tick_step}")
            else:
                # Default: Use MaxNLocator based on density
                num_ticks = 5 * options.positional_tick_density
                ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
                print_manager.debug(f"  Applied MaxNLocator with ~{num_ticks} ticks (density={options.positional_tick_density}x)")

            # --- TICK FORMATTER (Same for all degree types) --- 
            def angle_formatter(x, pos):
                # Ensure clean formatting, avoid unnecessary decimals like .0
                if x == int(x):
                    return f"{int(x)}°"
                else:
                    # Round to avoid excessive precision, e.g., 123.4567°
                    return f"{x:.1f}°"
            ax.xaxis.set_major_formatter(FuncFormatter(angle_formatter))
            print_manager.debug(f"  Applied angle_formatter.")
            
            # --- X-AXIS LIMITS --- 
            fixed_range = None
            if current_axis_mode == 'degrees_from_perihelion' and hasattr(options, 'degrees_from_perihelion_range') and options.degrees_from_perihelion_range:
                fixed_range = options.degrees_from_perihelion_range
                print_manager.debug(f"  Using fixed range for degrees_from_perihelion: {fixed_range}")
            elif (current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat') and options.x_axis_positional_range:
                 fixed_range = options.x_axis_positional_range
                 print_manager.debug(f"  Using fixed range for {current_axis_mode}: {fixed_range}")
            
            if fixed_range:
                ax.set_xlim(fixed_range)
                print_manager.debug(f"  Applied fixed xlim: {ax.get_xlim()}")
            elif not options.use_single_x_axis: # Auto-scale if no fixed range AND not using single x-axis
                # Calculate range from data if not using single x axis (handled later for single axis)
                lines = ax.get_lines()
                if lines and len(lines) > 0 and len(lines[0].get_xdata()) > 0:
                    x_data = lines[0].get_xdata()
                    min_val, max_val = np.nanmin(x_data), np.nanmax(x_data)
                    if np.isfinite(min_val) and np.isfinite(max_val):
                        data_range = max_val - min_val
                        padding = data_range * 0.05 if data_range > 0 else 1 # Add padding, handle zero range
                        ax.set_xlim(min_val - padding, max_val + padding)
                        print_manager.debug(f"  Auto-scaled individual xlim: {ax.get_xlim()}")
                    else:
                         print_manager.warning(f"Axis {i}: Cannot auto-scale limits, data contains NaNs or Infs.")
                else:
                    print_manager.warning(f"Axis {i}: Cannot auto-scale limits, no plottable data found.")
            # Else: If using single x-axis and no fixed range, scaling is handled globally later

            # --- X-AXIS LABEL --- 
            # Use the axis_label determined during initialization
            if options.use_single_x_axis:
                if i == len(axs) - 1:
                    # --- DEBUG: Print label being set --- 
                    print(f"[Final Format Loop - Axis {i}] Setting bottom label to: '{axis_label}'")
                    # --- END DEBUG --- 
                    ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                    # print_manager.debug(f"  Set bottom x-label: '{axis_label}'") # Use axis_label - Reduced verbosity
                else:
                    ax.set_xlabel('')
            else:
                # --- DEBUG: Print label being set --- 
                print(f"[Final Format Loop - Axis {i}] Setting individual label to: '{axis_label}'")
                # --- END DEBUG --- 
                ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                # print_manager.debug(f"  Set individual x-label: '{axis_label}'") # Use axis_label - Reduced verbosity

        elif current_axis_mode == 'r_sun':
            print_manager.debug(f"Axis {i}: Entering R_SUN formatting block.")
            # --- TICK LOCATOR --- 
            num_ticks = 5 * options.positional_tick_density
            ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
            print_manager.debug(f"  Applied MaxNLocator with ~{num_ticks} ticks (density={options.positional_tick_density}x)")

            # --- TICK FORMATTER --- 
            def radial_formatter(x, pos):
                if x == int(x):
                    return f"{int(x)}"
                else:
                    # Show more precision for radial distance
                    return f"{x:.2f}" 
            ax.xaxis.set_major_formatter(FuncFormatter(radial_formatter))
            print_manager.debug(f"  Applied radial_formatter.")

            # --- X-AXIS LIMITS --- 
            if options.x_axis_positional_range:
                ax.set_xlim(options.x_axis_positional_range)
                print_manager.debug(f"  Applied fixed xlim: {ax.get_xlim()}")
            elif not options.use_single_x_axis:
                # Auto-scale if no fixed range AND not using single x-axis
                lines = ax.get_lines()
                if lines and len(lines) > 0 and len(lines[0].get_xdata()) > 0:
                    x_data = lines[0].get_xdata()
                    min_val, max_val = np.nanmin(x_data), np.nanmax(x_data)
                    if np.isfinite(min_val) and np.isfinite(max_val):
                        data_range = max_val - min_val
                        padding = data_range * 0.05 if data_range > 0 else 0.1 # Add padding
                        ax.set_xlim(min_val - padding, max_val + padding)
                        print_manager.debug(f"  Auto-scaled individual xlim: {ax.get_xlim()}")
                    else:
                        print_manager.warning(f"Axis {i}: Cannot auto-scale R_sun limits, data contains NaNs or Infs.")
                else:
                    print_manager.warning(f"Axis {i}: Cannot auto-scale R_sun limits, no plottable data found.")
            # Else: Single x-axis auto-scaling handled later

            # --- X-AXIS LABEL --- 
            # Use the axis_label determined during initialization
            if options.use_single_x_axis:
                if i == len(axs) - 1:
                    ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                    # print_manager.debug(f"  Set bottom x-label: '{axis_label}'") # Use axis_label - Reduced verbosity
                else:
                    ax.set_xlabel('')
            else:
                 ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                 # print_manager.debug(f"  Set individual x-label: '{axis_label}'") # Use axis_label - Reduced verbosity
                 
        elif current_axis_mode == 'relative_time': # Check for the new mode name
             print_manager.debug(f"Axis {i}: Applying Relative Time formatting.")
             step_td = pd.Timedelta(value=options.relative_time_step, unit=options.relative_time_step_units)
             # Need center_dt for this panel - recalculate or pass from loop?
             # Recalculate: center_dt = pd.Timestamp(plot_list[i][0]) 
             center_dt_panel = pd.Timestamp(plot_list[i][0]) # Get center time for this specific panel
             
             # Need start/end time for this panel to calculate ticks
             panel_start_time, panel_end_time = ax.get_xlim() # Get current time limits
             # Convert numerical limits back to datetime if necessary (matplotlib might store them as numbers)
             try:
                 panel_start_dt = mdates.num2date(panel_start_time)
                 panel_end_dt = mdates.num2date(panel_end_time)
             except: # Handle cases where limits might already be datetime-like
                 panel_start_dt = pd.Timestamp(panel_start_time)
                 panel_end_dt = pd.Timestamp(panel_end_time)
                 
             # --- NEW: Enforce Naive Python Datetime Early ---
             def to_naive_py_datetime(dt):
                 # Converts pandas Timestamp or existing datetime to naive Python datetime
                 if hasattr(dt, 'to_pydatetime'):
                     dt = dt.to_pydatetime()
                 return dt.replace(tzinfo=None) if hasattr(dt, 'tzinfo') and dt.tzinfo is not None else dt
             panel_start_dt = to_naive_py_datetime(panel_start_dt)
             panel_end_dt = to_naive_py_datetime(panel_end_dt)
             center_dt_panel = to_naive_py_datetime(center_dt_panel)
             print(f"[DEBUG] (Early Convert) panel_start_dt: {repr(panel_start_dt)} (type: {type(panel_start_dt)})")
             print(f"[DEBUG] (Early Convert) panel_end_dt: {repr(panel_end_dt)} (type: {type(panel_end_dt)})")
             print(f"[DEBUG] (Early Convert) center_dt_panel: {repr(center_dt_panel)} (type: {type(center_dt_panel)})")
             # --- END NEW ---

             # <<< REMOVED: Previous scattered timezone patches >>>

             current = panel_start_dt
             # Align ticks to the step interval relative to the center time
             # Find the first tick >= start_time that is on a step interval from center_time
             time_diff_start = panel_start_dt - center_dt_panel # Subtraction should now work
             steps_from_center = np.floor(time_diff_start / step_td)
             first_tick_dt = center_dt_panel + (steps_from_center * step_td)
             if first_tick_dt < panel_start_dt: # Ensure first tick is within bounds
                  first_tick_dt += step_td
             current = first_tick_dt

             ticks = []
             tick_labels = []
             while current <= panel_end_dt:
                 # <<< REMOVED: Previous patch inside loop >>>
                 ticks.append(current)
                 time_from_center = (current - center_dt_panel)
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

                 if abs(value_from_center) < 1e-9: # Check for near zero
                     label = "0"
                 else:
                     # Format to remove trailing .0 if it's an integer
                     label = f"{value_from_center:.1f}".rstrip('0').rstrip('.') if '.' in f"{value_from_center:.1f}" else str(int(value_from_center))
                 tick_labels.append(label)
                 current += step_td
     
             ax.set_xticks(ticks)
             
             # --- X-AXIS LABEL (Relative Time) --- 
             # Use the axis_label determined during initialization (should be relative time label)
             # current_axis_label = f"Relative Time ({options.relative_time_step_units} from Perihelion)" # Default
             # if options.use_custom_x_axis_label:
             #      current_axis_label = options.custom_x_axis_label
                  
             if options.use_single_x_axis:
                 if i == len(axs) - 1:
                      ax.set_xticklabels(tick_labels)
                      ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                      # print_manager.debug(f"  Set bottom x-label: '{axis_label}'") # Use axis_label - Reduced verbosity
                 else: 
                      ax.set_xticklabels([])
                      ax.set_xlabel('')
             else:
                 ax.set_xticklabels(tick_labels)
                 ax.set_xlabel(axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size, labelpad=options.x_label_pad)
                 # print_manager.debug(f"  Set individual x-label: '{axis_label}'") # Use axis_label - Reduced verbosity

        # Apply tick font sizes regardless of mode
        ax.tick_params(axis='x', labelsize=options.x_tick_label_font_size)
        ax.tick_params(axis='y', labelsize=options.y_tick_label_font_size)

    # Apply common x-axis range if needed (handles all positional types)
    common_range_applied = False # Flag to track if common range was set
    if options.use_single_x_axis and (current_axis_mode != 'time' or options.use_relative_time):
        # Check if a fixed range was provided for the active positional mode
        fixed_range_global = None
        if current_axis_mode == 'degrees_from_perihelion' and hasattr(options, 'degrees_from_perihelion_range') and options.degrees_from_perihelion_range:
             fixed_range_global = options.degrees_from_perihelion_range
        elif (current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat' or current_axis_mode == 'r_sun') and options.x_axis_positional_range:
            fixed_range_global = options.x_axis_positional_range
            
        if fixed_range_global:
            # Apply the fixed range to all axes
            global_min, global_max = fixed_range_global
            for ax in axs:
                ax.set_xlim(global_min, global_max)
            print_manager.debug(f"Applied common FIXED x-axis range to all panels ({current_axis_mode}): {global_min:.2f} to {global_max:.2f}")
            common_range_applied = True
        elif current_axis_mode != 'time': # Auto-scale only if no fixed range and it's a positional/relative axis
            # Find the global min and max across all axes based on plotted data
            all_mins = []
            all_maxs = []
            for ax in axs:
                lines = ax.get_lines()
                if lines and len(lines) > 0:
                    x_data = lines[0].get_xdata()
                    if len(x_data) > 0:
                        # Ensure data is numeric before finding min/max
                        if np.issubdtype(x_data.dtype, np.number):
                            min_val, max_val = np.nanmin(x_data), np.nanmax(x_data)
                            if np.isfinite(min_val) and np.isfinite(max_val):
                                all_mins.append(min_val)
                                all_maxs.append(max_val)
                        else:
                            print_manager.warning(f"Axis data type is not numeric ({x_data.dtype}), cannot use for common range.")

            if all_mins and all_maxs:
                global_min = min(all_mins)
                global_max = max(all_maxs)
                data_range = global_max - global_min
                padding = data_range * 0.05 if data_range > 0 else 0.1 # Add padding
                global_min -= padding
                global_max += padding

                # Apply the global auto-scaled range to all axes
                for ax in axs:
                    ax.set_xlim(global_min, global_max)
                
                print_manager.debug(f"Applied common AUTO-SCALED x-axis range to all panels ({current_axis_mode}): {global_min:.2f} to {global_max:.2f}")
                common_range_applied = True
            else:
                 print_manager.warning("Could not determine common auto-scaled range - no valid numeric data found.")
                 
    # If common range was applied, ensure ticks match the final range
    if common_range_applied:
        print_manager.debug("Re-applying tick locators after setting common range.")
        for i, ax in enumerate(axs):
            # Re-apply the locator logic based on the final determined mode and range
             if current_axis_mode == 'degrees_from_perihelion' or current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat':
                 tick_step = None
                 if current_axis_mode == 'degrees_from_perihelion' and hasattr(options, 'degrees_from_perihelion_tick_step') and options.degrees_from_perihelion_tick_step:
                     tick_step = options.degrees_from_perihelion_tick_step
                 # Add future elifs for lon/lat fixed steps if needed
                 
                 if tick_step:
                     start_tick = np.ceil(ax.get_xlim()[0] / tick_step) * tick_step
                     end_tick = np.floor(ax.get_xlim()[1] / tick_step) * tick_step
                     ticks = np.arange(start_tick, end_tick + tick_step, tick_step)
                     ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
                 else:
                     num_ticks = 5 * options.positional_tick_density
                     ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
                     
             elif current_axis_mode == 'r_sun':
                  num_ticks = 5 * options.positional_tick_density
                  ax.xaxis.set_major_locator(mpl_plt.MaxNLocator(num_ticks))
                  
             elif options.use_relative_time:
                  # Re-calculate relative time ticks based on final common range
                  step_td = pd.Timedelta(value=options.relative_time_step, unit=options.relative_time_step_units)
                  center_dt_panel = pd.Timestamp(plot_list[i][0]) # Need panel center time
                  panel_start_num, panel_end_num = ax.get_xlim() # Get final numeric limits
                  panel_start_dt = mdates.num2date(panel_start_num)
                  panel_end_dt = mdates.num2date(panel_end_num)
                  
                  # Align ticks
                  time_diff_start = panel_start_dt - center_dt_panel
                  steps_from_center = np.floor(time_diff_start / step_td)
                  first_tick_dt = center_dt_panel + (steps_from_center * step_td)
                  if first_tick_dt < panel_start_dt: first_tick_dt += step_td
                  current = first_tick_dt
                  
                  ticks = []
                  while current <= panel_end_dt:
                      # --- PATCH: Ensure current is a Python datetime.datetime ---
                      print(f"[DEBUG] current tick type: {type(current)}")
                      if isinstance(current, pd.Timestamp):
                          current = current.to_pydatetime()
                      # --- END PATCH ---
                      ticks.append(current)
                      time_from_center = (current - center_dt_panel)
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

                      if abs(value_from_center) < 1e-9: # Check for near zero
                          label = "0"
                      else:
                          # Format to remove trailing .0 if it's an integer
                          label = f"{value_from_center:.1f}".rstrip('0').rstrip('.') if '.' in f"{value_from_center:.1f}" else str(int(value_from_center))
                      tick_labels.append(label)
                      current += step_td
                  ax.set_xticks(ticks)
                  print_manager.warning(f"Could not set relative tick labels for axis {i} due to limit conversion error.") 
                  # ax.set_xlabel(...) # Already handled in mode-specific blocks
             # ax.set_xlabel(...) # Already handled in mode-specific blocks
    
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
    # STEP 3: SAVE OUTPUT IF REQUESTED
    #==========================================================================
    if options.save_output:
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
        filename = f'PSP_MULTIPLOT_{timestamp}.png'
        
        if options.save_preset:
            # --- Preset Saving Logic --- 
            config = options.PRESET_CONFIGS[options.save_preset]
            # Save with preset configuration - REMOVE bbox_inches='tight'
            fig.savefig(
                filename,
                dpi=config['dpi'],
                facecolor='white'
            )
            
            # Verify and resize if necessary
            try:
                with Image.open(filename) as img:
                    target_size = (config['width_pixels'], config['height_pixels'])
                    if img.size != target_size:
                        print_manager.status(f"Resizing saved image from {img.size} to {target_size}...")
                        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                        resized_img.save(filename)
                    final_size = target_size
            except Exception as e:
                print_manager.warning(f"Error resizing image using preset: {e}")
                final_size = "Unknown"

            print_manager.status(f'Plot saved to: {os.path.abspath(filename)}')
            print_manager.status(f'Final dimensions: {final_size[0]}x{final_size[1]} pixels' if final_size != "Unknown" else "Final dimensions: Unknown")
        
        elif options.output_dimensions:
            # --- Custom Dimensions Saving Logic --- 
            target_width_px, target_height_px = options.output_dimensions
            # Save the figure as it is currently rendered (respecting user settings)
            # Use a reasonable default DPI for initial save, as resizing handles final pixel dimensions
            initial_dpi = 300 
            fig.savefig(
                filename,
                dpi=initial_dpi,
                bbox_inches=options.bbox_inches_save_crop_mode,
                pad_inches=0.1,
                facecolor='white'
            )
            
            # Resize the saved image to the exact requested dimensions
            try:
                with Image.open(filename) as img:
                    target_size = (target_width_px, target_height_px)
                    if img.size != target_size:
                        print_manager.status(f"Resizing saved image from {img.size} to {target_size}...")
                        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                        resized_img.save(filename)
                    final_size = target_size
            except Exception as e:
                print_manager.warning(f"Error resizing image to custom dimensions: {e}")
                final_size = "Unknown"
                
            print_manager.status(f'Plot saved to: {os.path.abspath(filename)}')
            print_manager.status(f'Final dimensions: {final_size[0]}x{final_size[1]} pixels' if final_size != "Unknown" else "Final dimensions: Unknown")
            
        else:
            # --- Standard Save (no preset, no specific dimensions) --- 
            fig.savefig(
                filename,
                dpi=options.save_dpi if options.save_dpi else 300, # Use save_dpi if set, else default
                bbox_inches=options.bbox_inches_save_crop_mode,
                pad_inches=0.1
            )
            print_manager.status(f'Plot saved to: {os.path.abspath(filename)}')
    
    # Show the plot
    plt.show()
    # Reset font size to matplotlib default after plotting
    mpl_plt.rcParams['font.size'] = 10
    
    # Restore original values if using preset
    if options.save_preset:
        options._restore_original_values()
        # --- RESTORE ORIGINAL RCPARAMS --- 
        if original_rcparams:
            for key, value in original_rcparams.items():
                mpl_plt.rcParams[key] = value
                print_manager.debug(f"Restored rcParam: {key} = {value}")
        # --- END RESTORE ORIGINAL RCPARAMS --- 
            
    # FINAL FIX: Ensure tick labels are hidden for non-bottom plots when using positional data and single x-axis
    if options.use_single_x_axis and using_positional_axis:
        print_manager.debug("Performing final check to ensure tick labels are hidden on non-bottom panels")
        for i, ax in enumerate(axs):
            if i < len(axs) - 1:  # All but the last (bottom) plot
                ax.set_xticklabels([])  # Force hide tick labels
                # print_manager.debug(f"Final fix: Hiding tick labels for panel {i}")
    
    # NEW: Apply x_label_pad directly using matplotlib's labelpad parameter
    for i, ax in enumerate(axs):
        # Only modify the bottom plot or plots with visible x-labels
        if (options.use_single_x_axis and i == len(axs) - 1) or not options.use_single_x_axis:
            # Update the x-label pad directly - this controls spacing better than position
            ax.xaxis.labelpad = options.x_label_pad
            # print_manager.debug(f"Applied x_label_pad={options.x_label_pad} to axis {i}")
    
    # ALWAYS enforce hiding tick labels for single-x-axis mode, regardless of axis type
    if options.use_single_x_axis:
        print_manager.debug("Performing final enforced check to hide tick labels on non-bottom panels for single-x-axis mode")
        for i, ax in enumerate(axs):
            if i < len(axs) - 1:  # All but the last (bottom) plot
                ax.set_xticklabels([])  # Force hide tick labels
                # Also set tick visibility to False for extra assurance
                for tick in ax.get_xticklabels():
                    tick.set_visible(False)
                # print_manager.debug(f"Forcibly hid all tick labels for panel {i}")
    
    print_manager.debug("=== Multiplot Complete ===\n")
    
    return fig, axs

print('📈📉 Multiplot Initialized')