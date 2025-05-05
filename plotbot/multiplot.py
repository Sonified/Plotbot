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
# --- ADDED: Import perihelion functions from utils ---
from .utils import get_perihelion_time, calculate_degrees_from_perihelion
# --- END ADDED ---

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

    # Override any options with provided kwargs - BEFORE initializing mapper
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)
        # Handle new options passed via kwargs
        elif key == 'use_degrees_from_perihelion':
            options.use_degrees_from_perihelion = value
        elif key == 'degrees_from_perihelion_range':
            options.degrees_from_perihelion_range = value
        elif key == 'degrees_from_perihelion_tick_step':
            options.degrees_from_perihelion_tick_step = value
            
    # --- DEBUG PRINT: Show initial option state --- 
    print_manager.debug("--- Multiplot Start --- Options State After Kwargs ---")
    print_manager.debug(f"  use_degrees_from_perihelion: {getattr(options, 'use_degrees_from_perihelion', 'N/A')}")
    print_manager.debug(f"  x_axis_carrington_lon: {getattr(options, 'x_axis_carrington_lon', 'N/A')}")
    print_manager.debug(f"  x_axis_carrington_lat: {getattr(options, 'x_axis_carrington_lat', 'N/A')}")
    print_manager.debug(f"  x_axis_r_sun: {getattr(options, 'x_axis_r_sun', 'N/A')}")
    print_manager.debug(f"  use_relative_time: {getattr(options, 'use_relative_time', 'N/A')}")
    print_manager.debug("-----------------------------------------------------")
    # --- END DEBUG PRINT --- 

    # Initialize positional mapper if needed
    positional_mapper = None
    # --- MODIFIED: Determine if ANY positional feature is active *after* applying kwargs ---
    using_positional_axis = False  # Default to False
    data_type = 'time' # Default
    axis_label = "Time" # Default
    units = "" # Default
    
    positional_feature_requested = (
        options.x_axis_r_sun or 
        options.x_axis_carrington_lon or 
        options.x_axis_carrington_lat or 
        getattr(options, 'use_degrees_from_perihelion', False) 
    )
    print_manager.debug(f"Initial check - positional_feature_requested: {positional_feature_requested}")
    # --- Explicitly set using_positional_axis based on the check --- 
    if positional_feature_requested:
        using_positional_axis = True 
        print_manager.debug(f"--> Setting using_positional_axis = True based on request.")
    # --- END ---
    # --- END MODIFIED ---

    # --- MODIFIED: Initialize mapper only if a positional feature is requested ---
    if positional_feature_requested:
        # Ensure positional_data_path exists
        if not hasattr(options, 'positional_data_path') or not options.positional_data_path:
             print_manager.error("❌ Positional data path (options.positional_data_path) is not set. Cannot use positional x-axis or degrees from perihelion.")
             # Disable positional features if path is missing
             options.use_degrees_from_perihelion = False # Also disable degrees explicitly
             options.x_axis_r_sun = False 
             options.x_axis_carrington_lon = False 
             options.x_axis_carrington_lat = False
             positional_feature_requested = False # Prevent further positional logic
             using_positional_axis = False # Ensure this is false too
             print_manager.debug("--> Resetting positional flags due to missing path.")
        else:
            print_manager.debug(f"--> Initializing XAxisPositionalDataMapper with path: {options.positional_data_path}")
            positional_mapper = XAxisPositionalDataMapper(options.positional_data_path)
            # Check if mapper initialized successfully (data loaded)
            mapper_loaded = hasattr(positional_mapper, 'data_loaded') and positional_mapper.data_loaded
            print_manager.debug(f"--> Mapper data_loaded status: {mapper_loaded}")
            
            # If mapper failed, reset flags
            if not mapper_loaded:
                print_manager.warning("❌ Failed to load positional data. Disabling positional x-axis and degrees from perihelion.")
                options.use_degrees_from_perihelion = False
                options.x_axis_r_sun = False 
                options.x_axis_carrington_lon = False 
                options.x_axis_carrington_lat = False
                positional_feature_requested = False 
                using_positional_axis = False 
            else:
                # Mapper loaded, now determine the *primary* data type for plotting
                if options.use_degrees_from_perihelion:
                    print_manager.debug("--> Mode Determination: use_degrees_from_perihelion is True.")
                    data_type = 'degrees_from_perihelion'
                    axis_label = "Degrees from Perihelion (°)"
                    units = "°"
                    # Ensure conflicting standard positional options are off (should be handled by setter, but double-check)
                    options.x_axis_carrington_lon = False
                    options.x_axis_r_sun = False
                    options.x_axis_carrington_lat = False
                elif options.x_axis_carrington_lon:
                    print_manager.debug("--> Mode Determination: x_axis_carrington_lon is True.")
                    data_type = 'carrington_lon'
                    values_array = positional_mapper.longitude_values
                    axis_label = "Carrington Longitude (°)"
                    units = "°"
                elif options.x_axis_r_sun:
                    print_manager.debug("--> Mode Determination: x_axis_r_sun is True.")
                    data_type = 'r_sun'
                    values_array = positional_mapper.radial_values
                    axis_label = "Radial Distance (R_sun)"
                    units = "R_sun"
                elif options.x_axis_carrington_lat:
                    print_manager.debug("--> Mode Determination: x_axis_carrington_lat is True.")
                    data_type = 'carrington_lat'
                    values_array = positional_mapper.latitude_values
                    axis_label = "Carrington Latitude (°)"
                    units = "°"
                else:
                     # This case means positional_feature_requested was true initially, but no specific mode ended up active.
                     print_manager.debug("--> Mode Determination: Positional feature requested but no specific type active, defaulting to time.")
                     using_positional_axis = False # Fallback
                     axis_label = "Time"
                     units = ""
                     data_type = 'time'

                # Verify relative time conflict only if a positional mode is confirmed active
                if using_positional_axis and options.use_relative_time:
                        print_manager.warning("⚠️ Positional axis/degrees AND relative time are enabled.")
                        print_manager.status("--> Automatically disabling use_relative_time.")
                        options.use_relative_time = False
                        
    # Final check: If positional feature was requested but ultimately failed or wasn't specific, default to time.
    if not using_positional_axis:
        print_manager.debug("--> Final check: using_positional_axis is False. Setting mode to Time.")
        data_type = 'time'
        axis_label = "Time" 
        units = ""
    # --- END MODIFIED ---

    # Store original rcParams to restore later
    original_rcparams = {}
    
    # Override any options with provided kwargs - INCLUDING NEW ONES
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)
        # --- ADDED: Handling for new options if passed via kwargs ---
        # These would ideally be in MultiplotOptions class
        elif key == 'use_degrees_from_perihelion':
            options.use_degrees_from_perihelion = value
        elif key == 'degrees_from_perihelion_range':
            options.degrees_from_perihelion_range = value
        elif key == 'degrees_from_perihelion_tick_step':
            options.degrees_from_perihelion_tick_step = value
        # --- END ADDED ---

    # --- ADDED: Define defaults for new options if not set ---
    # These should live in MultiplotOptions eventually
    if not hasattr(options, 'use_degrees_from_perihelion'):
        options.use_degrees_from_perihelion = False
    if not hasattr(options, 'degrees_from_perihelion_range'):
        options.degrees_from_perihelion_range = None # Auto-range by default
    if not hasattr(options, 'degrees_from_perihelion_tick_step'):
        options.degrees_from_perihelion_tick_step = None # Auto-ticks by default
    # --- END ADDED ---
    
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
        # <<< MODIFIED DEBUG >>>
        print_manager.custom_debug(f'Adding data to plot panel {i+1}/{n_panels}... Var ID from plot_list: {id(var)}\n')
        # <<< END MODIFIED DEBUG >>>
        # Add diagnostic for HAM feature status
        print_manager.debug(f"Panel {i+1} - HAM feature status: hamify={options.hamify}, ham_var={options.ham_var is not None}")
        center_dt = pd.Timestamp(center_time)

        # Get encounter number automatically
        enc_num = get_encounter_number(center_time)

        # --- Initialize flag for successful degree plotting --- 
        panel_actually_uses_degrees = False # Default to False for this panel

        # --- ADDED: Get Perihelion Time if needed ---
        perihelion_time_str = None
        current_panel_use_degrees = False # Reset for this panel
        # Use getattr for safety, check if positional axis is generally usable
        if getattr(options, 'use_degrees_from_perihelion', False) and using_positional_axis:
            print_manager.debug(f"Panel {i+1} [Data Prep]: Trying to get perihelion time for center: {center_time}")
            perihelion_time_str = get_perihelion_time(center_time) # Use center_time of the plot
            if perihelion_time_str is None:
                print_manager.debug(f"Panel {i+1} [Data Prep]: Could not get perihelion time. Setting current_panel_use_degrees = False.")
                current_panel_use_degrees = False # Flag that degrees cannot be used for this panel
            else:
                print_manager.debug(f"Panel {i+1} [Data Prep]: Got perihelion time: {perihelion_time_str}. Setting current_panel_use_degrees = True.")
                current_panel_use_degrees = True # Flag that we intend to use degrees
        else:
            print_manager.debug(f"Panel {i+1} [Data Prep]: Degrees not requested or positional axis not active. current_panel_use_degrees = False.")
            current_panel_use_degrees = False
        # --- END ADDED ---

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
        
        # --- Add a point to store the final x_data before plotting --- 
        final_x_data_for_plot = None
        final_y_data_for_plot = None
        
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
    
                        # --- MODIFIED: X-Data Calculation ---
                        time_slice = single_var.datetime_array[indices]
                        data_slice = single_var.data[indices]
                        x_data = time_slice # Default to time
                        times_for_data = time_slice # Track the time corresponding to data_slice
                        panel_actually_uses_degrees = False # Reset flag

                        if current_panel_use_degrees and perihelion_time_str:
                            print_manager.debug(f"Panel {i+1} (Right Axis): Calculating degrees from perihelion for {len(time_slice)} points")
                            output_times, relative_degrees = calculate_degrees_from_perihelion(
                                time_slice, perihelion_time_str, options.positional_data_path
                            )
                            if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                                original_df = pd.DataFrame({'time': time_slice, 'data': data_slice})
                                output_df = pd.DataFrame({'time': output_times, 'x_data': relative_degrees})
                                original_df['time'] = pd.to_datetime(original_df['time'])
                                output_df['time'] = pd.to_datetime(output_df['time'])
                                merged_df = pd.merge_asof(output_df.sort_values('time'),
                                                          original_df.sort_values('time'),
                                                          on='time', direction='nearest', tolerance=pd.Timedelta('1s'))
                                merged_df.dropna(subset=['data', 'x_data'], inplace=True)

                                if not merged_df.empty:
                                    x_data = merged_df['x_data'].values
                                    data_slice = merged_df['data'].values
                                    times_for_data = merged_df['time'].values
                                    print_manager.debug(f"Panel {i+1} (Right Axis): Using {len(x_data)} points for degrees from perihelion plot.")
                                    panel_actually_uses_degrees = True # Success
                                else:
                                    print_manager.warning(f"Panel {i+1} (Right Axis): Failed to align data with relative degrees after merge. Falling back to time axis.")
                                    x_data = time_slice
                                    data_slice = single_var.data[indices]
                                    times_for_data = time_slice
                            else:
                                print_manager.warning(f"Panel {i+1} (Right Axis): Calculation of relative degrees failed or returned all NaNs. Falling back to time axis.")
                                x_data = time_slice
                                data_slice = single_var.data[indices]
                                times_for_data = time_slice

                        if not panel_actually_uses_degrees:
                            if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                                # --- Existing Standard Positional Logic ---
                                print_manager.debug(f"Panel {i+1} (Right Axis): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals)
                                    num_valid = np.sum(valid_mask)
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        data_slice = data_slice[valid_mask]
                                        times_for_data = time_slice[valid_mask]
                                        print_manager.debug(f"Panel {i+1} (Right Axis): Standard positional mapping successful, using {num_valid} valid points")
                                    else:
                                        print_manager.status(f"Panel {i+1} (Right Axis): Standard positional mapping resulted in no valid points. Using time.")
                                else:
                                    print_manager.status(f"Panel {i+1} (Right Axis): Standard positional mapping failed (returned None). Using time.")
                            # else: x_data remains time_slice (default)
                        # --- END MODIFIED X-Data Calculation ---
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
                            ham_ylabel = getattr(ham_var, 'y_label', 'HAM') 
                            # --- REMOVE set_ylabel for HAM plot --- 
                            # ax2.set_ylabel(ham_ylabel,
                            #               fontsize=options.y_axis_label_font_size,
                            #               labelpad=options.y_label_pad,
                            #               fontweight='bold' if options.bold_y_axis_label else 'normal',
                            #               ha=options.y_label_alignment,
                            #               color=panel_color) # Apply color here too
                            
                            # Set tick color and label size
                            ax2.tick_params(axis='y', colors=panel_color, which='both', labelsize=options.y_tick_label_font_size)
                            # Set all spines to panel color
                            for spine in ax2.spines.values():
                                spine.set_color(panel_color)
                        # --- END Apply rainbow --- 
                        else: # Apply normal label if not rainbow
                             ham_ylabel = getattr(ham_var, 'y_label', 'HAM') 
                             # --- REMOVE set_ylabel for HAM plot --- 
                             # ax2.set_ylabel(ham_ylabel,
                             #               fontsize=options.y_axis_label_font_size,
                             #               labelpad=options.y_label_pad,
                             #               fontweight='bold' if options.bold_y_axis_label else 'normal',
                             #               ha=options.y_label_alignment)

                        # Set the right y-axis label to match the panel color and style
                        ham_ylabel = getattr(ham_var, 'y_label', 'HAM')
                        ax2.set_ylabel(ham_ylabel,
                                      fontsize=options.y_axis_label_font_size,
                                      labelpad=options.y_label_pad,
                                      fontweight='bold' if options.bold_y_axis_label else 'normal',
                                      ha=options.y_label_alignment)
                        # Force all right axis elements to rainbow color
                        # --- REMOVED call to non-existent function --- 
                        # apply_right_axis_color(ax2, panel_color, options) 
                        print(f"DEBUG: Panel {i+1} right axis label is: '{ax2.get_ylabel()}'")
                        # Set right y-axis tick params and spine colors to match panel color
                        # This is handled correctly by the `if panel_color is not None:` block above
                        # ax2.tick_params(axis='y', colors=panel_color, which='both')
                        # for spine in ax2.spines.values():
                        #     spine.set_color(panel_color)
                        # Now apply the panel color to ax2 (for y-label, etc.) # This comment seems out of place
                    
                    else: # Plotting first variable (or only variable) in list on left axis
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

                        # --- MODIFIED: X-Data Calculation ---
                        time_slice = single_var.datetime_array[indices]
                        data_slice = single_var.data[indices]
                        x_data = time_slice  # Default to time
                        times_for_data = time_slice
                        panel_actually_uses_degrees = False  # Reset flag

                        if current_panel_use_degrees and perihelion_time_str:
                            print_manager.debug(f"Panel {i+1} (List Var): Calculating degrees from perihelion for {len(time_slice)} points")
                            output_times, relative_degrees = calculate_degrees_from_perihelion(
                                time_slice, perihelion_time_str, options.positional_data_path
                            )
                            if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                                original_df = pd.DataFrame({'time': time_slice, 'data': data_slice})
                                output_df = pd.DataFrame({'time': output_times, 'x_data': relative_degrees})
                                original_df['time'] = pd.to_datetime(original_df['time'])
                                output_df['time'] = pd.to_datetime(output_df['time'])
                                merged_df = pd.merge_asof(output_df.sort_values('time'),
                                                          original_df.sort_values('time'),
                                                          on='time', direction='nearest', tolerance=pd.Timedelta('1s'))
                                merged_df.dropna(subset=['data', 'x_data'], inplace=True)

                                if not merged_df.empty:
                                    x_data = merged_df['x_data'].values
                                    data_slice = merged_df['data'].values
                                    times_for_data = merged_df['time'].values
                                    print_manager.debug(f"Panel {i+1} (List Var): Using {len(x_data)} points for degrees from perihelion plot.")
                                    panel_actually_uses_degrees = True  # Success
                                    # Store flag on axis for later formatting check
                                    axs[i]._panel_actually_used_degrees = True 
                                else:
                                    print_manager.warning(f"Panel {i+1} (List Var): Failed to align data with relative degrees after merge. Falling back to time axis.")
                                    x_data = time_slice
                                    data_slice = single_var.data[indices]
                                    times_for_data = time_slice
                            else:
                                print_manager.warning(f"Panel {i+1} (List Var): Calculation of relative degrees failed or returned all NaNs. Falling back to time axis.")
                                x_data = time_slice
                                data_slice = single_var.data[indices]
                                times_for_data = time_slice

                        if not panel_actually_uses_degrees:
                            if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                                # --- Existing Standard Positional Logic ---
                                print_manager.debug(f"Panel {i+1} (List Var): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals)
                                    num_valid = np.sum(valid_mask)
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        data_slice = data_slice[valid_mask]
                                        times_for_data = time_slice[valid_mask]
                                        print_manager.debug(f"Panel {i+1} (List Var): Standard positional mapping successful, using {num_valid} valid points")
                                    else:
                                        print_manager.status(f"Panel {i+1} (List Var): Standard positional mapping resulted in no valid points. Using time.")
                                else:
                                    print_manager.status(f"Panel {i+1} (List Var): Standard positional mapping failed (returned None). Using time.")
                            # else: x_data remains time_slice (default)
                        # --- END MODIFIED X-Data Calculation ---

                        # --- Plot using potentially modified x_data and data_slice ---
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
                            # Get x-axis data - use longitude if available
                            # x_data = var.datetime_array[indices] # OLD
                            time_slice = var.datetime_array[indices]
                            data_slice = var.data[indices]
                            x_data = time_slice # Default to time

                            if using_positional_axis and positional_mapper is not None:
                                print_manager.debug(f"Panel {i+1} (Time Series): Attempting positional mapping for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                     # --- NEW: Create mask for successful mapping --- 
                                    valid_mask = ~np.isnan(positional_vals) 
                                    num_valid = np.sum(valid_mask)
                                    
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        data_slice = data_slice[valid_mask] 
                                        print_manager.debug(f"Panel {i+1} (Time Series): Positional mapping successful, using {num_valid} valid points")
                                        panel_actually_uses_degrees = True # Success
                                        # Store flag on axis for later formatting check
                                        axs[i]._panel_actually_used_degrees = True 
                                    else:
                                        print_manager.status(f"Panel {i+1} (Time Series): Positional mapping resulted in no valid points. Using time.")
                                else:
                                    print_manager.status(f"Panel {i+1} (Time Series): Positional mapping failed (returned None). Using time.")

                            # --- Use filtered x_data and data_slice --- 
                            axs[i].plot(x_data, 
                                        data_slice, # Use filtered data_slice
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

                            # --- MODIFIED: X-Data Calculation for Scatter ---
                            time_slice = var.datetime_array[indices]
                            data_slice = var.data[indices]
                            x_data = time_slice # Default to time
                            times_for_data = time_slice
                            panel_actually_uses_degrees = False # Reset flag

                            if current_panel_use_degrees and perihelion_time_str:
                                print_manager.debug(f"Panel {i+1} (Scatter): Calculating degrees from perihelion for {len(time_slice)} points")
                                output_times, relative_degrees = calculate_degrees_from_perihelion(
                                    time_slice, perihelion_time_str, options.positional_data_path
                                )
                                if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                                    original_df = pd.DataFrame({'time': time_slice, 'data': data_slice})
                                    output_df = pd.DataFrame({'time': output_times, 'x_data': relative_degrees})
                                    original_df['time'] = pd.to_datetime(original_df['time'])
                                    output_df['time'] = pd.to_datetime(output_df['time'])
                                    merged_df = pd.merge_asof(output_df.sort_values('time'),
                                                              original_df.sort_values('time'),
                                                              on='time', direction='nearest', tolerance=pd.Timedelta('1s'))
                                    merged_df.dropna(subset=['data', 'x_data'], inplace=True)

                                    if not merged_df.empty:
                                        x_data = merged_df['x_data'].values
                                        data_slice = merged_df['data'].values
                                        times_for_data = merged_df['time'].values
                                        print_manager.debug(f"Panel {i+1} (Scatter): Using {len(x_data)} points for degrees from perihelion plot.")
                                        panel_actually_uses_degrees = True # Success
                                        # Store flag on axis for later formatting check
                                        axs[i]._panel_actually_used_degrees = True 
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Scatter): Failed to align data with relative degrees after merge. Falling back to time axis.")
                                        x_data = time_slice
                                        data_slice = var.data[indices]
                                        times_for_data = time_slice
                                else:
                                    print_manager.warning(f"Panel {i+1} (Scatter): Calculation of relative degrees failed or returned all NaNs. Falling back to time axis.")
                                    x_data = time_slice
                                    data_slice = var.data[indices]
                                    times_for_data = time_slice

                            if not panel_actually_uses_degrees:
                                if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                                    # --- Existing Standard Positional Logic ---
                                    print_manager.debug(f"Panel {i+1} (Scatter): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                    positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                    if positional_vals is not None:
                                        valid_mask = ~np.isnan(positional_vals)
                                        num_valid = np.sum(valid_mask)
                                        if num_valid > 0:
                                            x_data = positional_vals[valid_mask]
                                            data_slice = data_slice[valid_mask]
                                            times_for_data = time_slice[valid_mask]
                                            print_manager.debug(f"Panel {i+1} (Scatter): Standard positional mapping successful, using {num_valid} valid points")
                                        else:
                                            print_manager.status(f"Panel {i+1} (Scatter): Standard positional mapping resulted in no valid points. Using time.")
                                    else:
                                        print_manager.status(f"Panel {i+1} (Scatter): Standard positional mapping failed (returned None). Using time.")
                                # else: x_data remains time_slice (default)
                            # --- END MODIFIED X-Data Calculation ---

                            # --- Use filtered x_data and data_slice --- 
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
                            # data_clipped = np.array(var.data)[indices] # Handled below
                            # additional_data_clipped = np.array(var.additional_data)[indices] # Handled below
                            
                            colorbar_limits = axis_options.colorbar_limits if hasattr(axis_options, 'colorbar_limits') and axis_options.colorbar_limits else var.colorbar_limits
                            if var.colorbar_scale == 'log':
                                norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                            elif var.colorbar_scale == 'linear':
                                norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
                            else: # Default or unknown scale
                                norm = None
        
                            # --- MODIFIED: X-Data Calculation for Spectral ---
                            # Spectral data needs slightly different handling
                            time_slice = datetime_clipped # Use already clipped times
                            # Use UNCLIPPED y-axis bins (additional_data assumed to be energy bins etc.)
                            y_spectral_axis_full = np.array(var.additional_data)
                            # Use time-indexed spectral data (already clipped along time axis)
                            spectral_data_slice = np.array(var.data)[indices]

                            x_data = time_slice # Default to time (as raw datetimes or np.datetime64)
                            times_for_data = time_slice # Keep track
                            panel_actually_uses_degrees = False # Reset flag

                            if current_panel_use_degrees and perihelion_time_str:
                                print_manager.debug(f"Panel {i+1} (Spectral): Calculating degrees from perihelion for {len(time_slice)} time points")
                                output_times, relative_degrees = calculate_degrees_from_perihelion(
                                    time_slice, perihelion_time_str, options.positional_data_path
                                )

                                if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                                    # Align spectral data with the output times/degrees
                                    original_times_pd = pd.Series(time_slice)
                                    output_times_pd = pd.Series(output_times)
                                    original_times_ns = pd.to_datetime(original_times_pd).astype(np.int64)
                                    output_times_ns = pd.to_datetime(output_times_pd).astype(np.int64)
                                    output_time_to_index_map = {t: idx for idx, t in enumerate(output_times_ns)}
                                    original_indices_present_in_output = []
                                    output_indices_to_keep = []
                                    for original_idx, t_ns in enumerate(original_times_ns):
                                        if t_ns in output_time_to_index_map:
                                            original_indices_present_in_output.append(original_idx)
                                            output_indices_to_keep.append(output_time_to_index_map[t_ns])

                                    if original_indices_present_in_output:
                                        filtered_spectral_data = spectral_data_slice[original_indices_present_in_output, :]
                                        filtered_relative_degrees = relative_degrees[output_indices_to_keep]
                                        nan_degree_mask = np.isnan(filtered_relative_degrees)
                                        if np.all(nan_degree_mask):
                                             print_manager.warning(f"Panel {i+1} (Spectral): All aligned degrees are NaN. Falling back to time axis.")
                                             x_data = time_slice
                                             spectral_data_slice = np.array(var.data)[indices]
                                        else:
                                            x_data = filtered_relative_degrees[~nan_degree_mask]
                                            spectral_data_slice = filtered_spectral_data[~nan_degree_mask, :]
                                            print_manager.debug(f"Panel {i+1} (Spectral): Using {len(x_data)} points for degrees from perihelion plot.")
                                            panel_actually_uses_degrees = True # Success
                                            # Store flag on axis for later formatting check
                                            axs[i]._panel_actually_used_degrees = True 
                                    else:
                                        print_manager.warning(f"Panel {i+1} (Spectral): Failed to align spectral data with relative degrees. Falling back to time axis.")
                                        x_data = time_slice
                                        spectral_data_slice = np.array(var.data)[indices]
                                else:
                                    print_manager.warning(f"Panel {i+1} (Spectral): Calculation of relative degrees failed or returned all NaNs. Falling back to time axis.")
                                    x_data = time_slice
                                    spectral_data_slice = np.array(var.data)[indices]

                            if not panel_actually_uses_degrees:
                                if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                                    # --- Existing Standard Positional Logic ---
                                    print_manager.debug(f"Panel {i+1} (Spectral): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                    positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                    if positional_vals is not None:
                                        valid_mask = ~np.isnan(positional_vals)
                                        num_valid = np.sum(valid_mask)
                                        if num_valid > 0:
                                            x_data = positional_vals[valid_mask]
                                            spectral_data_slice = spectral_data_slice[valid_mask, :]
                                            print_manager.debug(f"Panel {i+1} (Spectral): Standard positional mapping successful, using {num_valid} valid points")
                                        else:
                                            print_manager.status(f"Panel {i+1} (Spectral): Standard positional mapping resulted in no valid points. Using time.")
                                            x_data = time_slice
                                    else:
                                        print_manager.status(f"Panel {i+1} (Spectral): Standard positional mapping failed (returned None). Using time.")
                                        x_data = time_slice
                                # else: x_data remains time_slice (default)
                            # --- END MODIFIED X-Data Calculation for Spectral ---

                            # FIXED: Create properly shaped mesh grid for pcolormesh to avoid dimension mismatch
                            try:
                                z_shape = spectral_data_slice.shape
                                y_shape_expected = z_shape[1] if len(z_shape) > 1 else 0
                                x_len = len(x_data) if hasattr(x_data, '__len__') else 0
                                print_manager.debug(f"Spectral data shapes for pcolormesh: X:{x_len}, Y:{len(y_spectral_axis_full)}, Z:{z_shape}")

                                if y_shape_expected != len(y_spectral_axis_full):
                                     print_manager.warning(f"Spectral Y axis length ({len(y_spectral_axis_full)}) does not match filtered data dimension ({y_shape_expected}). Skipping plot.")
                                else:
                                     # --- MODIFIED: Use potentially updated x_data and handle datetimes ---
                                     if x_len > 0:
                                         if isinstance(x_data[0], (datetime, np.datetime64)):
                                             x_plot_data = mdates.date2num(x_data)
                                         else:
                                             x_plot_data = x_data

                                         # Ensure x_plot_data and y_spectral_axis_full have compatible lengths for pcolormesh
                                         # pcolormesh needs X and Y to define the grid corners, so dimensions should be N+1 or handled by shading='auto'
                                         # With shading='auto', X defines the centers (or edges) of N columns, Y defines centers/edges of M rows.
                                         # Data Z should be M x N.
                                         if len(x_plot_data) == z_shape[0] and len(y_spectral_axis_full) == z_shape[1]:
                                             im = axs[i].pcolormesh(x_plot_data, y_spectral_axis_full, spectral_data_slice.T, # Transpose Z data
                                                                   norm=norm, cmap=var.colormap, shading='auto')

                                             pos = axs[i].get_position()
                                             cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                                             cbar = fig.colorbar(im, cax=cax)

                                             if hasattr(var, 'colorbar_label'):
                                                 cbar.set_label(var.colorbar_label)
                                         else:
                                             print_manager.warning(f"Dimension mismatch for pcolormesh: X({len(x_plot_data)}), Y({len(y_spectral_axis_full)}), Z({z_shape}). Skipping plot.")
                                     else: # x_len is 0
                                         print_manager.warning("No X data points for spectral plot after processing. Skipping plot.")

                            except Exception as e:
                                print_manager.warning(f"Error plotting spectral data: {str(e)}")
                                x_len_err = len(x_data) if hasattr(x_data, '__len__') else 'scalar'
                                y_len_err = len(y_spectral_axis_full) if hasattr(y_spectral_axis_full, '__len__') else 'scalar'
                                z_shape_err = spectral_data_slice.shape if hasattr(spectral_data_slice, 'shape') else 'unknown'
                                print_manager.warning(f"Data shapes at error: X:{x_len_err}, Y:{y_len_err}, Z:{z_shape_err}")

                else: # Default plot type (handles if var.plot_type is not set or different)
                    plot_color = panel_color
                    if not plot_color:
                        plot_color = axis_options.color if axis_options.color else var.color
                    
                    # CRITICAL FIX: Check if indices is empty before trying to plot
                    if len(indices) > 0:
                        # --- MODIFIED: X-Data Calculation --- 
                        time_slice = var.datetime_array[indices]
                        data_slice = var.data[indices]
                        x_data = time_slice # Default to time
                        times_for_data = time_slice
                        panel_actually_uses_degrees = False # Reset flag

                        if current_panel_use_degrees and perihelion_time_str:
                            print_manager.debug(f"Panel {i+1} (Default Plot): Calculating degrees from perihelion for {len(time_slice)} points")
                            output_times, relative_degrees = calculate_degrees_from_perihelion(
                                time_slice, perihelion_time_str, options.positional_data_path
                            )
                            if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                                original_df = pd.DataFrame({'time': time_slice, 'data': data_slice})
                                output_df = pd.DataFrame({'time': output_times, 'x_data': relative_degrees})
                                original_df['time'] = pd.to_datetime(original_df['time'])
                                output_df['time'] = pd.to_datetime(output_df['time'])
                                merged_df = pd.merge_asof(output_df.sort_values('time'),
                                                          original_df.sort_values('time'),
                                                          on='time', direction='nearest', tolerance=pd.Timedelta('1s'))
                                merged_df.dropna(subset=['data', 'x_data'], inplace=True)

                                if not merged_df.empty:
                                    x_data = merged_df['x_data'].values
                                    data_slice = merged_df['data'].values
                                    times_for_data = merged_df['time'].values
                                    print_manager.debug(f"Panel {i+1} (Default Plot): Using {len(x_data)} points for degrees from perihelion plot.")
                                    panel_actually_uses_degrees = True # Success
                                    # Store flag on axis for later formatting check
                                    axs[i]._panel_actually_used_degrees = True 
                                else:
                                    print_manager.warning(f"Panel {i+1} (Default Plot): Failed to align data with relative degrees after merge. Falling back to time axis.")
                                    x_data = time_slice
                                    data_slice = var.data[indices]
                                    times_for_data = time_slice
                            else:
                                print_manager.warning(f"Panel {i+1} (Default Plot): Calculation of relative degrees failed or returned all NaNs. Falling back to time axis.")
                                x_data = time_slice
                                data_slice = var.data[indices]
                                times_for_data = time_slice

                        if not panel_actually_uses_degrees:
                            if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                                # --- Existing Standard Positional Logic ---
                                print_manager.debug(f"Panel {i+1} (Default Plot): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                                positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                                if positional_vals is not None:
                                    valid_mask = ~np.isnan(positional_vals)
                                    num_valid = np.sum(valid_mask)
                                    if num_valid > 0:
                                        x_data = positional_vals[valid_mask]
                                        data_slice = data_slice[valid_mask]
                                        times_for_data = time_slice[valid_mask]
                                        print_manager.debug(f"Panel {i+1} (Default Plot): Standard positional mapping successful, using {num_valid} valid points")
                                    else:
                                        print_manager.status(f"Panel {i+1} (Default Plot): Standard positional mapping resulted in no valid points. Using time.")
                                        x_data = time_slice # Ensure fallback
                                else:
                                    print_manager.status(f"Panel {i+1} (Default Plot): Standard positional mapping failed (returned None). Using time.")
                                    x_data = time_slice # Ensure fallback
                            # else: x_data remains time_slice (default)
                        # --- END MODIFIED X-Data Calculation ---
                        
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
                ham_var_subclass_name = getattr(options.ham_var, 'subclass_name', 'hamogram_30s') # Get name before overwriting
                ham_var = ham_class_instance.get_subclass(ham_var_subclass_name) # Use the potentially default name
                # --- MODIFIED: Explicit check for None --- 
                if ham_var is not None:
                # --- END MODIFIED --- 
                    print_manager.debug(f"Panel {i+1}: Refreshed HAM variable '{ham_var_subclass_name}' reference from data_cubby")
                else:
                    print_manager.error(f"Panel {i+1}: Failed to get HAM subclass '{ham_var_subclass_name}' from data_cubby after get_data")
                    ham_var = None # Ensure ham_var is None if lookup failed
            else:
                print_manager.error(f"Panel {i+1}: Failed to get ham class instance from data_cubby")
                ham_var = None # Ensure ham_var is None if lookup failed
            
            # Use ham_var for plotting below
            # Add checks for ham_var existence and necessary attributes
            if ham_var is not None and hasattr(ham_var, 'datetime_array') and ham_var.datetime_array is not None and hasattr(ham_var, 'data') and ham_var.data is not None:
                print_manager.debug(f"Panel {i+1}: HAM feature enabled, plotting {ham_var.subclass_name if hasattr(ham_var, 'subclass_name') else 'HAM variable'} on right axis")
                # Create a twin axis for the HAM data
                ax2 = axs[i].twinx()
                
                # Get color - use panel color if available, otherwise right axis color or ham_var's color
                if panel_color is not None:
                    plot_color = panel_color
                elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
                    plot_color = axis_options.r.color
                else:
                    plot_color = ham_var.color # Fallback to ham_var's defined color
                    
                # Get time-clipped indices for HAM data
                print_manager.debug(f"Panel {i+1}: Attempting to time_clip HAM data with range: {trange[0]} to {trange[1]}")
                # Check if ham_var.datetime_array is empty before accessing elements
                if len(ham_var.datetime_array) > 0:
                    print_manager.debug(f"Panel {i+1}: HAM data range is {ham_var.datetime_array[0]} to {ham_var.datetime_array[-1]}")
                    ham_indices = time_clip(ham_var.datetime_array, trange[0], trange[1])
                else:
                    print_manager.warning(f"Panel {i+1}: HAM variable has empty datetime_array. Skipping HAM plot.")
                    ham_indices = [] # Ensure indices list is empty
                
                print_manager.debug(f"Panel {i+1}: Found {len(ham_indices)} HAM data points in time range")
                
                if len(ham_indices) > 0:
                    # --- MODIFIED: X-Data Calculation for HAM ---
                    time_slice = ham_var.datetime_array[ham_indices]
                    data_slice = ham_var.data[ham_indices]
                    x_data = time_slice # Default to time
                    times_for_data = time_slice
                    # Check if main panel intended to use degrees
                    ham_panel_actually_uses_degrees = False # Reset flag for HAM

                    if current_panel_use_degrees and perihelion_time_str:
                        print_manager.debug(f"Panel {i+1} (HAM Plot): Calculating degrees from perihelion for {len(time_slice)} points")
                        output_times, relative_degrees = calculate_degrees_from_perihelion(
                            time_slice, perihelion_time_str, options.positional_data_path
                        )
                        if relative_degrees is not None and len(relative_degrees) > 0 and not np.all(np.isnan(relative_degrees)):
                            original_df = pd.DataFrame({'time': time_slice, 'data': data_slice})
                            output_df = pd.DataFrame({'time': output_times, 'x_data': relative_degrees})
                            original_df['time'] = pd.to_datetime(original_df['time'])
                            output_df['time'] = pd.to_datetime(output_df['time'])
                            merged_df = pd.merge_asof(output_df.sort_values('time'),
                                                      original_df.sort_values('time'),
                                                      on='time', direction='nearest', tolerance=pd.Timedelta('1s'))
                            merged_df.dropna(subset=['data', 'x_data'], inplace=True)

                            if not merged_df.empty:
                                x_data = merged_df['x_data'].values
                                data_slice = merged_df['data'].values
                                times_for_data = merged_df['time'].values
                                print_manager.debug(f"Panel {i+1} (HAM Plot): Using {len(x_data)} points for degrees from perihelion plot.")
                                ham_panel_actually_uses_degrees = True # HAM uses degrees
                            else:
                                print_manager.warning(f"Panel {i+1} (HAM Plot): Failed to align HAM data with relative degrees after merge. Falling back to time axis.")
                                x_data = time_slice
                                data_slice = ham_var.data[ham_indices]
                                times_for_data = time_slice
                        else:
                            print_manager.warning(f"Panel {i+1} (HAM Plot): Calculation of relative degrees failed or returned all NaNs for HAM data. Falling back to time axis.")
                            x_data = time_slice
                            data_slice = ham_var.data[ham_indices]
                            times_for_data = time_slice

                    if not ham_panel_actually_uses_degrees:
                         if using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                            # --- Existing Standard Positional Logic ---
                            print_manager.debug(f"Panel {i+1} (HAM Plot): Attempting standard positional mapping ({data_type}) for {len(time_slice)} points")
                            positional_vals = positional_mapper.map_to_position(time_slice, data_type)
                            if positional_vals is not None:
                                valid_mask = ~np.isnan(positional_vals)
                                num_valid = np.sum(valid_mask)
                                if num_valid > 0:
                                    x_data = positional_vals[valid_mask]
                                    data_slice = data_slice[valid_mask]
                                    times_for_data = time_slice[valid_mask]
                                    print_manager.debug(f"Panel {i+1} (HAM Plot): Standard positional mapping successful, using {num_valid} valid points")
                                else:
                                    print_manager.status(f"Panel {i+1} (HAM Plot): Standard positional mapping resulted in no valid points. Using time.")
                                    x_data = time_slice # Ensure fallback
                            else:
                                 print_manager.status(f"Panel {i+1} (HAM Plot): Standard positional mapping failed (returned None). Using time.")
                                 x_data = time_slice # Ensure fallback
                         # else: x_data remains time_slice (default)
                    # --- END MODIFIED X-Data Calculation ---
                    
                    # Plot the HAM data using potentially filtered x_data and data_slice
                    print_manager.debug(f"Panel {i+1}: Plotting HAM data on right axis")
                    ax2.plot(x_data, 
                            data_slice, # Use potentially filtered data_slice
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
                    
                    # --- Apply rainbow color to all right axis elements ---
                    if panel_color is not None:
                        # Set y-axis label color and font weight
                        ham_ylabel = getattr(ham_var, 'y_label', 'HAM') 
                        # --- REMOVE set_ylabel for HAM plot --- 
                        # ax2.set_ylabel(ham_ylabel,
                        #               fontsize=options.y_axis_label_font_size,
                        #               labelpad=options.y_label_pad,
                        #               fontweight='bold' if options.bold_y_axis_label else 'normal',
                        #               ha=options.y_label_alignment,
                        #               color=panel_color) # Apply color here too
                        
                        # Set tick color and label size
                        ax2.tick_params(axis='y', colors=panel_color, which='both', labelsize=options.y_tick_label_font_size)
                        # Set all spines to panel color
                        for spine in ax2.spines.values():
                            spine.set_color(panel_color)
                    # --- END Apply rainbow --- 
                    else: # Apply normal label if not rainbow
                         ham_ylabel = getattr(ham_var, 'y_label', 'HAM') 
                         # --- REMOVE set_ylabel for HAM plot --- 
                         # ax2.set_ylabel(ham_ylabel,
                         #               fontsize=options.y_axis_label_font_size,
                         #               labelpad=options.y_label_pad,
                         #               fontweight='bold' if options.bold_y_axis_label else 'normal',
                         #               ha=options.y_label_alignment)

                    
                    # Include HAM in legend
                    lines_left, labels_left = axs[i].get_legend_handles_labels()
                    lines_right, labels_right = ax2.get_legend_handles_labels()
                    # Combine legends
                    all_lines = lines_left + lines_right
                    all_labels = labels_left + labels_right
                    # Create legend only if there are labels to show
                    if all_labels:
                        leg = axs[i].legend(all_lines, all_labels,
                                            bbox_to_anchor=(1.025, 1),
                                            loc='upper left')
                        # Set legend label color to rainbow if in rainbow mode
                        if options.color_mode == 'rainbow' and panel_color is not None and leg:
                            for text in leg.get_texts():
                                text.set_color(panel_color)
                            # Set the legend border (frame) color to match the panel color
                            leg.get_frame().set_edgecolor(panel_color)
                else:
                    print_manager.status(f"Panel {i+1}: No HAM data points found in time range {trange[0]} to {trange[1]}")
            else:
                # Print more specific reason why HAM wasn't plotted
                if ham_var is None:
                    print_manager.status(f"Panel {i+1}: Not plotting HAM - ham_var is None (check data cubby/get_data)")
                elif not hasattr(ham_var, 'datetime_array') or ham_var.datetime_array is None:
                    print_manager.status(f"Panel {i+1}: Not plotting HAM - ham_var is missing or has None datetime_array")
                elif not hasattr(ham_var, 'data') or ham_var.data is None:
                     print_manager.status(f"Panel {i+1}: Not plotting HAM - ham_var is missing or has None data array")
        
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
            current_ylim = axs[i].get_ylim()

        # --- MODIFIED: Defer Set X Limits until final formatting stage ---
        pass # Limit setting moved to final formatting loop
        # --- END MODIFIED ---

        # --- Y Label and Scale Setting --- 
        # ... [Existing Y Label and Scale Logic - should be here]
        if isinstance(var, list):
            if all(hasattr(v, 'y_label') for v in var):
                y_label = var[0].y_label
            else:
                y_label = ''
        else:
            y_label = getattr(var, 'y_label', '') # Use getattr for safety
    
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
    
        # --- Y Scale Setting --- 
        current_y_scale = 'linear' # Default
        can_set_log = False
        if isinstance(var, list):
            if hasattr(var[0], 'y_scale') and var[0].y_scale == 'log':
                 current_y_scale = 'log'
                 # Check if data exists for log scale
                 if hasattr(var[0], 'data') and len(indices) > 0:
                      data_subset = var[0].data[indices]
                      if np.any(data_subset > 0):
                          can_set_log = True 
        elif hasattr(var, 'y_scale') and var.y_scale == 'log':
            current_y_scale = 'log'
            if hasattr(var, 'data') and len(indices) > 0:
                data_subset = var.data[indices]
                if np.any(data_subset > 0):
                    can_set_log = True
        elif hasattr(var, 'y_scale'): # Handle non-log scales directly
             current_y_scale = var.y_scale
             can_set_log = False # Ensure log isn't set

        if current_y_scale == 'log' and not can_set_log:
            print_manager.warning(f"Panel {i+1}: Cannot set log scale - no positive data in range. Using linear scale.")
            axs[i].set_yscale('linear')
        elif current_y_scale:
             axs[i].set_yscale(current_y_scale)
             
        # --- Handle Relative Time Ticks inside loop if active --- 
        if options.use_relative_time and not using_positional_axis: # Only use relative time if NOT using longitude/degrees
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
                    return # Abort plot if units invalid
    
                if abs(value_from_center) < 1e-9: # Check for near-zero float
                    label = "0"
                else:
                    label = f"{value_from_center:.1f}".rstrip('0').rstrip('.')
                tick_labels.append(label)
                current += step_td
    
            axs[i].set_xticks(ticks)
            axs[i].set_xticklabels(tick_labels)
             # Add tick label sizes when using relative time
            axs[i].tick_params(axis='x', labelsize=options.x_tick_label_font_size)
            axs[i].tick_params(axis='y', labelsize=options.y_tick_label_font_size)
             # Set relative time label only on bottom plot if using single axis
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    axs[i].set_xticklabels([]) # Hide labels for non-bottom
                    axs[i].set_xlabel('')
                else: 
                    axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Center)", 
                                        fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                        labelpad=options.x_label_pad)
            else: # Not single axis - apply label to all
                 axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Center)", 
                                     fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                                     labelpad=options.x_label_pad)

        # --- Draw Vertical Line --- 
        if options.draw_vertical_line:
            # Determine value for vertical line based on axis type
            vline_value = center_dt # Default for time/relative time
            # Now this check is safe because the variable is guaranteed to exist
            if panel_actually_uses_degrees: 
                 vline_value = 0 # Center is 0 degrees
            elif using_positional_axis and positional_mapper is not None and not options.use_degrees_from_perihelion:
                 # Map center time to positional value
                 center_pos_val = positional_mapper.map_to_position([center_dt], data_type)
                 if center_pos_val is not None and len(center_pos_val) > 0 and not np.isnan(center_pos_val[0]):
                     vline_value = center_pos_val[0]
                 else:
                     print_manager.warning(f"Panel {i+1}: Could not map center time {center_dt} to {data_type} for vertical line.")
                     vline_value = None # Prevent drawing line if mapping fails
            
            if vline_value is not None:
                color_to_use = panel_color if panel_color else options.vertical_line_color
                axs[i].axvline(x=vline_value, 
                               color=color_to_use,
                               linestyle=options.vertical_line_style,
                               linewidth=options.vertical_line_width)
    
        # --- Individual Title Setting --- 
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
    
        # --- Horizontal Lines --- 
        # Check for global horizontal line
        if plt.options.draw_horizontal_line:
            axs[i].axhline(
                y=plt.options.horizontal_line_value,
                linewidth=plt.options.horizontal_line_width,
                color=plt.options.horizontal_line_color,
                linestyle=plt.options.horizontal_line_style
            )
        # Check for axis-specific horizontal line
        axis_options = getattr(options, f'ax{i+1}') # Get axis options again
        if axis_options and axis_options.draw_horizontal_line:
            axs[i].axhline(
                y=axis_options.horizontal_line_value,
                linewidth=axis_options.horizontal_line_width,
                color=axis_options.horizontal_line_color,
                linestyle=axis_options.horizontal_line_style
            )
    
        # --- Apply Border Width --- 
        for spine_name, spine in axs[i].spines.items():
            spine.set_linewidth(plt.options.border_line_width)

    # --- End of Main Plotting Loop --- 

    # --- MODIFIED: Final X-Axis Formatting Logic --- 
    # Iterate through axes to set final x-axis properties (label, ticks, limits)
    for i, ax in enumerate(axs):
        print_manager.debug(f"--- Final Formatting Axis {i} ---") # DEBUG
        is_bottom_panel = (i == n_panels - 1)
        apply_label_and_ticks = not options.use_single_x_axis or is_bottom_panel

        # Determine the active axis type for this plot configuration
        # --- MODIFIED: More robust mode detection --- 
        current_axis_mode = 'time' # Default
        # Get the panel-specific flag indicating successful degree plotting
        panel_used_degrees_flag = getattr(ax, '_panel_actually_used_degrees', False)
        print_manager.debug(f"Axis {i}: Retrieved _panel_actually_used_degrees flag: {panel_used_degrees_flag}") # DEBUG

        if panel_used_degrees_flag:
            current_axis_mode = 'degrees_from_perihelion'
        elif using_positional_axis and options.using_positional_x_axis and options.active_positional_data_type:
            # Check if standard positional axis was used (e.g., carrington_lon, r_sun)
            current_axis_mode = options.active_positional_data_type
        elif options.use_relative_time:
             current_axis_mode = 'relative_time'
        # else: current_axis_mode remains 'time' (default)
        # --- END MODIFIED MODE DETECTION --- 

        print_manager.debug(f"Axis {i}: Determined final formatting mode: {current_axis_mode}") # DEBUG

        # Set X Label based on mode
        if apply_label_and_ticks:
            final_axis_label = "" # Initialize
            if current_axis_mode == 'degrees_from_perihelion':
                final_axis_label = "Degrees from Perihelion (°)"
            elif current_axis_mode == 'carrington_lon':
                final_axis_label = "Carrington Longitude (°)"
            elif current_axis_mode == 'r_sun':
                final_axis_label = "Radial Distance (R_sun)"
            elif current_axis_mode == 'carrington_lat':
                 final_axis_label = "Carrington Latitude (°)"
            elif current_axis_mode == 'relative_time':
                 final_axis_label = f"Relative Time ({options.relative_time_step_units} from Center)"
            elif options.use_custom_x_axis_label:
                 # Apply custom label only if not using a specific positional/degree/relative mode
                 if current_axis_mode == 'time':
                     final_axis_label = options.custom_x_axis_label
                 else:
                     # Keep the specific mode label if custom label is set but mode isn't time
                     # Get the label determined during initialization phase
                     # REVISIT: data_type might not be correct here if fallback occurred
                     if current_axis_mode == 'degrees_from_perihelion': final_axis_label = "Degrees from Perihelion (°)"
                     elif current_axis_mode == 'carrington_lon': final_axis_label = "Carrington Longitude (°)"
                     elif current_axis_mode == 'r_sun': final_axis_label = "Radial Distance (R_sun)"
                     elif current_axis_mode == 'carrington_lat': final_axis_label = "Carrington Latitude (°)"
                     else: final_axis_label = "Time" # Fallback 
            else: # Default time label
                final_axis_label = "Time"

            print_manager.debug(f"Axis {i}: Setting final_axis_label to: '{final_axis_label}'") # DEBUG
            ax.set_xlabel(final_axis_label, fontweight='bold' if options.bold_x_axis_label else 'normal', fontsize=options.x_axis_label_font_size,
                          labelpad=options.x_label_pad)
        else:
            print_manager.debug(f"Axis {i}: Not applying label/ticks (not bottom or not single axis).") # DEBUG
            ax.set_xlabel('')
            # Ensure tick labels are hidden for non-bottom plots in single-axis mode
            if options.use_single_x_axis:
                ax.set_xticklabels([]) # Explicitly hide labels

        # Set Ticks and Limits based on mode
        if current_axis_mode == 'time':
            print_manager.debug(f"Axis {i}: Entering TIME formatting block.") # DEBUG
            if apply_label_and_ticks:
                # Check if formatter is already set (e.g., by relative time)
                # Ensure we don't overwrite a potentially numeric formatter if time fallback occurred
                if not isinstance(ax.xaxis.get_major_formatter(), (mdates.ConciseDateFormatter, FuncFormatter)):
                    try:
                         # Attempt to set date formatter, might fail if axis holds non-date data
                         locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                         formatter = mdates.ConciseDateFormatter(locator)
                         ax.xaxis.set_major_locator(locator)
                         ax.xaxis.set_major_formatter(formatter)
                    except Exception as e:
                        print_manager.warning(f"Axis {i}: Failed to set date formatter for 'time' mode ({e}). Axis might contain non-time data.")
                        # Consider setting a default numeric formatter here if needed
            
            # Set time limits if not already set (e.g., if plot failed or axis defaulted to time)
            xlim = ax.get_xlim()
            needs_time_limits = False
            try: # Check if limits are convertible to datetime
                 dt_min = pd.to_datetime(xlim[0], unit='d') # date2num uses days since epoch
                 dt_max = pd.to_datetime(xlim[1], unit='d')
                 # If limits are default (0,1) or look like large numbers (posix), reset
                 if xlim == (0.0, 1.0) or (xlim[0] > 1e9 and xlim[1] > 1e9):
                      needs_time_limits = True
            except (ValueError, TypeError, OverflowError):
                 needs_time_limits = True # Assume they need setting if not datetime-like
            
            if needs_time_limits:
                 center_time_panel, _ = plot_list[i]
                 start_dt_panel = pd.Timestamp(center_time_panel) - pd.Timedelta(options.window)/2 if options.position == 'around' else (pd.Timestamp(center_time_panel) - pd.Timedelta(options.window) if options.position == 'before' else pd.Timestamp(center_time_panel))
                 end_dt_panel = pd.Timestamp(center_time_panel) + pd.Timedelta(options.window)/2 if options.position == 'around' else (pd.Timestamp(center_time_panel) if options.position == 'before' else pd.Timestamp(center_time_panel) + pd.Timedelta(options.window))
                 ax.set_xlim(start_dt_panel, end_dt_panel)
                 print_manager.debug(f"Axis {i}: Set final time limits: {start_dt_panel} to {end_dt_panel}")

        elif current_axis_mode == 'relative_time':
            print_manager.debug(f"Axis {i}: Entering RELATIVE_TIME formatting block.") # DEBUG
            # This mode handles its own ticks and labels inside the main loop
            # However, ensure limits are set correctly if not done already
            # Ensure this block has correct indentation relative to the elif above
            if ax.get_xlim() == (0.0, 1.0): # Check for default limits
                 center_time_panel, _ = plot_list[i]
                 center_dt_panel = pd.Timestamp(center_time_panel)
                 start_dt_panel = center_dt_panel - pd.Timedelta(options.window)/2 if options.position == 'around' else (center_dt_panel - pd.Timedelta(options.window) if options.position == 'before' else center_dt_panel)
                 end_dt_panel = center_dt_panel + pd.Timedelta(options.window)/2 if options.position == 'around' else (center_dt_panel if options.position == 'before' else center_dt_panel + pd.Timedelta(options.window))
                 ax.set_xlim(start_dt_panel, end_dt_panel) # Set underlying limits as datetime
                 print_manager.debug(f"Axis {i}: Set underlying limits for relative time axis.")

        # --- MODIFIED: Combine degrees and longitude formatting --- 
        elif current_axis_mode == 'degrees_from_perihelion' or current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat':
            print_manager.debug(f"Axis {i}: Entering DEGREE formatting block ({current_axis_mode}).") # DEBUG
            print_manager.debug(f"Setting up axis {i} for Degree-based display: {current_axis_mode}")
            current_units = "°"
             # Set Ticks
            if apply_label_and_ticks:
                # Determine tick step based on mode
                tick_step = None
                if current_axis_mode == 'degrees_from_perihelion' and options.degrees_from_perihelion_tick_step:
                    tick_step = options.degrees_from_perihelion_tick_step
                    step_source = "degrees_from_perihelion_tick_step"
                # Add similar check if there was a specific tick step for carrington_lon/lat
                # elif current_axis_mode == 'carrington_lon' and options.carrington_lon_tick_step:
                #     tick_step = options.carrington_lon_tick_step 
                #     step_source = "carrington_lon_tick_step"
                
                if tick_step is not None:
                    step = abs(tick_step) if isinstance(tick_step, (int, float)) and tick_step != 0 else 10 # Default step 10
                    locator = mticker.MultipleLocator(base=step)
                    print_manager.debug(f"-> Using tick step: {step}° (from {step_source})")
                else:
                    # Default MaxNLocator if no specific step is set
                    num_ticks = 5 * options.positional_tick_density
                    locator = mpl_plt.MaxNLocator(int(max(2, num_ticks)), prune='both')
                    print_manager.debug(f"-> Using MaxNLocator with ~{int(max(2, num_ticks))} ticks (density={options.positional_tick_density}x)")
                ax.xaxis.set_major_locator(locator)

                # Set Formatter (Same for all degree types)
                def degree_formatter(x, pos):
                    if abs(x - round(x)) < 1e-6: return f"{int(round(x))}°"
                    else: return f"{x:.1f}°"
                ax.xaxis.set_major_formatter(FuncFormatter(degree_formatter))
                print_manager.debug(f"Axis {i}: Applying Formatter: degree_formatter") # DEBUG
            else:
                 ax.set_xticklabels([]) # Hide labels if not bottom

            # Set Limits (logic combines degrees and standard positional range options)
            user_range = None
            if current_axis_mode == 'degrees_from_perihelion' and options.degrees_from_perihelion_range:
                user_range = options.degrees_from_perihelion_range
                range_source = "degrees_from_perihelion_range"
            elif current_axis_mode != 'degrees_from_perihelion' and options.x_axis_positional_range:
                 # Use standard positional range for carrington_lon/lat if set
                 user_range = options.x_axis_positional_range
                 range_source = "x_axis_positional_range"
                 
            if user_range:
                min_val, max_val = user_range
                if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)) and min_val < max_val:
                     ax.set_xlim(min_val, max_val)
                     print_manager.debug(f"-> Using user-specified range: {min_val} to {max_val} {current_units} (from {range_source})")
                else:
                    print_manager.warning(f"Invalid user-specified range: {user_range} from {range_source}. Auto-scaling.")
                    # Fall through to auto-scaling if user range is invalid
                    user_range = None # Ensure auto-scaling happens
                    
            if not user_range: # Auto-scale if no valid user range provided
                 if not options.use_single_x_axis:
                     # Auto-scale individual panel
                     ax.relim()
                     ax.autoscale(enable=True, axis='x', tight=False)
                     xlim = ax.get_xlim()
                     data_range = xlim[1] - xlim[0]
                     padding = data_range * 0.05 if data_range > 0 else 1 # Default padding 1 degree
                     ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
                     xlim = ax.get_xlim()
                     print_manager.debug(f"-> Auto-scaled individual axis {i} range: {xlim[0]:.1f}° to {xlim[1]:.1f}°")
                 # Else: Common range calculation will handle limits if use_single_x_axis is True
                 
            # Apply tight margin if requested
            if getattr(options, 'tight_x_axis', False):
                 ax.margins(x=0)
                 print_manager.debug(f"-> Applied tight x-axis margin to axis {i}")
 
        elif current_axis_mode == 'r_sun':
            print_manager.debug(f"Axis {i}: Entering R_SUN formatting block.") # DEBUG
            # Keep R_sun formatting separate as it uses different units/formatter
            print_manager.debug(f"Setting up axis {i} for standard positional display: {current_axis_mode}")
            current_units = "R_sun"
             # Set Ticks
            if apply_label_and_ticks:
                num_ticks = 5 * options.positional_tick_density
                locator = mpl_plt.MaxNLocator(int(max(2, num_ticks)), prune='both')
                ax.xaxis.set_major_locator(locator)
                print_manager.debug(f"-> Using MaxNLocator with ~{int(max(2, num_ticks))} ticks")

                # Set Formatter for R_sun
                def radial_formatter(x, pos):
                    if abs(x - round(x)) < 1e-6: return f"{int(round(x))}"
                    elif abs(x*10 - round(x*10)) < 1e-6: return f"{x:.1f}"
                    else: return f"{x:.2f}"
                ax.xaxis.set_major_formatter(FuncFormatter(radial_formatter))
                print_manager.debug(f"Axis {i}: Applying Formatter: radial_formatter") # DEBUG
            else:
                 ax.set_xticklabels([]) # Hide labels if not bottom

            # Set Limits for R_sun
            if options.x_axis_positional_range:
                min_val, max_val = options.x_axis_positional_range
                if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)) and min_val < max_val:
                     ax.set_xlim(min_val, max_val)
                     print_manager.debug(f"-> Using user-specified positional range: {min_val} to {max_val} {current_units}")
                else:
                    print_manager.warning(f"Invalid x_axis_positional_range: {options.x_axis_positional_range}. Auto-scaling.")
                    if not options.use_single_x_axis:
                         ax.relim()
                         ax.autoscale(enable=True, axis='x', tight=False)
                         xlim = ax.get_xlim()
                         data_range = xlim[1] - xlim[0]
                         padding = data_range * 0.05 if data_range > 0 else 0.1 # Default padding for R_sun
                         ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
                         xlim = ax.get_xlim()
                         print_manager.debug(f"-> Auto-scaled individual axis {i} range: {xlim[0]:.2f} to {xlim[1]:.2f} {current_units}")
            elif not options.use_single_x_axis:
                 ax.relim()
                 ax.autoscale(enable=True, axis='x', tight=False)
                 xlim = ax.get_xlim()
                 data_range = xlim[1] - xlim[0]
                 padding = data_range * 0.05 if data_range > 0 else 0.1 # Default padding for R_sun
                 ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
                 xlim = ax.get_xlim()
                 print_manager.debug(f"-> Auto-scaled individual axis {i} range: {xlim[0]:.2f} to {xlim[1]:.2f} {current_units}")
            # Else: Common range calculation handles limits if use_single_x_axis is True
            # Apply tight margin if requested
            if getattr(options, 'tight_x_axis', False):
                 ax.margins(x=0)
                 print_manager.debug(f"-> Applied tight x-axis margin to axis {i}")
        # --- END MODIFIED --- 
 
        # Apply tick label font size universally
        ax.tick_params(axis='x', labelsize=options.x_tick_label_font_size)
        ax.tick_params(axis='y', labelsize=options.y_tick_label_font_size)
        print_manager.debug(f"--- End Final Formatting Axis {i} ---") # DEBUG
    # --- END Final X-Axis Formatting Loop ---

    # Apply common x-axis range if needed for POSITIONAL or DEGREE axes
    # --- MODIFIED: Check for positional or degree mode and ensure axis mode matches ---
    common_axis_mode = None
    if options.use_single_x_axis:
        # Determine the intended common mode based on options
        # Degrees mode takes precedence if enabled and functional
        if getattr(options, 'use_degrees_from_perihelion', False) and using_positional_axis:
            common_axis_mode = 'degrees_from_perihelion'
        elif options.using_positional_x_axis and options.active_positional_data_type:
            common_axis_mode = options.active_positional_data_type
        # else: no common positional/degree axis needed (likely time or relative time)

    if common_axis_mode:
        print_manager.debug(f"Attempting common x-axis range calculation for mode: {common_axis_mode}")
        # Only apply common range if a specific range wasn't provided by the user
        user_range_set = (common_axis_mode == 'degrees_from_perihelion' and options.degrees_from_perihelion_range is not None) or \
                         (common_axis_mode != 'degrees_from_perihelion' and options.x_axis_positional_range is not None)

        if not user_range_set:
            all_mins = []
            all_maxs = []
            found_data_for_common_range = False
            for i, ax in enumerate(axs):
                # Check if this axis actually plotted data in the target common mode
                # Re-check the heuristic used in the formatting loop more carefully
                x_sample = []
                is_numeric = False
                plotted_in_mode = False
                x_data_plotted = None # Store the actual x data used for limits

                if ax.lines:
                    if len(ax.lines) > 0 and hasattr(ax.lines[0], 'get_xdata') and len(ax.lines[0].get_xdata()) > 0:
                        x_data_plotted = ax.lines[0].get_xdata()
                        is_numeric = not isinstance(x_data_plotted[0], (datetime, np.datetime64))
                elif ax.collections:
                     if len(ax.collections) > 0 and isinstance(ax.collections[0], mpl_plt.collections.PathCollection): # Scatter
                         x_data_plotted = ax.collections[0].get_offsets()[:, 0]
                         if len(x_data_plotted) > 0: is_numeric = True
                     elif len(ax.collections) > 0 and isinstance(ax.collections[0], mpl_plt.collections.QuadMesh): # pcolormesh
                          # For pcolormesh, x data might be edges or centers. Get limits as proxy.
                          # We already determined it's likely numeric in the previous loop if mode is positional/degrees.
                           x_data_plotted = ax.get_xlim()
                           is_numeric = True # Assume numeric for range check

                if is_numeric and x_data_plotted is not None and len(x_data_plotted) > 0:
                    # Check range based on common_axis_mode
                    min_x, max_x = np.nanmin(x_data_plotted), np.nanmax(x_data_plotted)
                    if common_axis_mode == 'degrees_from_perihelion' or common_axis_mode == 'carrington_lon' or common_axis_mode == 'carrington_lat':
                        if min_x >= -361 and max_x <= 361: plotted_in_mode = True
                    elif common_axis_mode == 'r_sun':
                        if min_x > 0: plotted_in_mode = True # Simple check for R_sun

                if plotted_in_mode:
                    min_val, max_val = np.nanmin(x_data_plotted), np.nanmax(x_data_plotted)
                    # Ensure values are finite numbers before adding
                    if np.isfinite(min_val) and np.isfinite(max_val):
                         all_mins.append(min_val)
                         all_maxs.append(max_val)
                         found_data_for_common_range = True
                         print_manager.debug(f"Axis {i}: Included in common range calc (Min: {min_val:.2f}, Max: {max_val:.2f})")
                    else:
                         print_manager.debug(f"Axis {i}: Found non-finite data ({min_val}, {max_val}). Excluding from common range.")
                else:
                    print_manager.debug(f"Axis {i}: Data not plotted in common mode '{common_axis_mode}' or non-numeric/empty. Excluding from common range calculation.")

            if found_data_for_common_range and all_mins and all_maxs:
                global_min = min(all_mins)
                global_max = max(all_maxs)
                data_range = global_max - global_min
                
                # Determine padding based on units, considering tight_x_axis
                if getattr(options, 'tight_x_axis', False):
                    padding = 0
                    print_manager.debug("Common range: tight_x_axis enabled, setting padding=0")
                elif data_range > 1e-9: # Check if range is effectively non-zero
                    padding = data_range * 0.05
                else: # Handle single point or flat line case across all panels
                    padding = 0 if getattr(options, 'tight_x_axis', False) else (1 if common_axis_mode != 'r_sun' else 0.1)

                final_min = global_min - padding
                final_max = global_max + padding

                # Apply the global range to all axes
                for k, ax_k in enumerate(axs):
                     # Re-check if this specific axis actually plotted in the common mode before applying limits
                     # (Prevents applying degree limits to a panel that fell back to time)
                    x_sample_k = []
                    is_numeric_k = False
                    plotted_in_mode_k = False
                    x_data_plotted_k = None

                    if ax_k.lines:
                        if len(ax_k.lines) > 0 and hasattr(ax_k.lines[0], 'get_xdata') and len(ax_k.lines[0].get_xdata()) > 0:
                             x_data_plotted_k = ax_k.lines[0].get_xdata()
                             is_numeric_k = not isinstance(x_data_plotted_k[0], (datetime, np.datetime64))
                    elif ax_k.collections:
                         if len(ax_k.collections) > 0 and isinstance(ax_k.collections[0], mpl_plt.collections.PathCollection):
                              x_data_plotted_k = ax_k.collections[0].get_offsets()[:, 0]
                              if len(x_data_plotted_k) > 0: is_numeric_k = True
                         elif len(ax_k.collections) > 0 and isinstance(ax_k.collections[0], mpl_plt.collections.QuadMesh):
                              x_data_plotted_k = ax_k.get_xlim() # Use limits proxy
                              is_numeric_k = True
                    
                    if is_numeric_k and x_data_plotted_k is not None and len(x_data_plotted_k) > 0:
                        min_xk, max_xk = np.nanmin(x_data_plotted_k), np.nanmax(x_data_plotted_k)
                        if common_axis_mode == 'degrees_from_perihelion' or common_axis_mode == 'carrington_lon' or common_axis_mode == 'carrington_lat':
                            if min_xk >= -361 and max_xk <= 361: plotted_in_mode_k = True
                        elif common_axis_mode == 'r_sun':
                            if min_xk > 0: plotted_in_mode_k = True
                    
                    if plotted_in_mode_k:
                         ax_k.set_xlim(final_min, final_max)
                         print_manager.debug(f" -> Applied common range to Axis {k}")
                    else:
                         print_manager.debug(f" -> Skipped applying common range to Axis {k} (not in common mode '{common_axis_mode}')")

                print_manager.status(f"Applied common auto-scaled x-axis range ({common_axis_mode}): {final_min:.2f} to {final_max:.2f}")
            elif found_data_for_common_range: # Data found, but min/max lists ended up empty (e.g., all NaNs)
                print_manager.warning(f"Could not determine numeric min/max for common range mode '{common_axis_mode}'. Check plotted data.")
            else: # No data found across any panel for the specified common mode
                 print_manager.warning(f"Could not determine common range for mode '{common_axis_mode}' - no data found in this mode across panels.")
        else:
            print_manager.debug("Using user-specified range for common x-axis. No auto-scaling needed.")
    # --- END MODIFIED Common Axis Range Logic ---

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