# Import plotbot components with relative imports
from .data_cubby import data_cubby
from .data_tracker import global_tracker  
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .print_manager import print_manager
from .get_encounter import get_encounter_number
from .plotbot_helpers import time_clip
# Import specific functions from multiplot_helpers instead of using wildcard import
from .multiplot_helpers import get_plot_colors, apply_panel_color, apply_bottom_axis_color, validate_log_scale_limits
from .multiplot_options import plt, MultiplotOptions
# Import get_data for custom variables
from .get_data import get_data

# Import standard libraries
import matplotlib.colors as colors
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
    
    # Override any options with provided kwargs
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)
    
    print_manager.debug("\n=== Starting Multiplot Function ===")
    print_manager.debug(f"Window: {options.window}, Position: {options.position}")
    
    # Convert window to timedelta
    window_td = pd.Timedelta(options.window)
    
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
            start_time = pd.Timestamp(center_time) - window_td/2
            end_time = pd.Timestamp(center_time) + window_td/2
            print_manager.time_tracking(f"Panel {i+1} 'around' position: center ± {window_td/2}")
        elif options.position == 'before':
            start_time = pd.Timestamp(center_time) - window_td
            end_time = pd.Timestamp(center_time)
            print_manager.time_tracking(f"Panel {i+1} 'before' position: center - {window_td}")
        else:  # after
            start_time = pd.Timestamp(center_time)
            end_time = pd.Timestamp(center_time) + window_td
            print_manager.time_tracking(f"Panel {i+1} 'after' position: center + {window_td}")
            
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
    
    # Create figure with subplots
    print_manager.debug("\nCreating figure...")
    fig, axs = plt.subplots(n_panels, 1, 
                           figsize=(options.width, options.height_per_panel*n_panels), 
                           sharex=False)
    
    if n_panels == 1:
        axs = [axs]
    
    # Adjust subplot spacing
    plt.subplots_adjust(right=0.85, hspace=options.hspace)
    
    # Get color scheme based on color_mode
    color_scheme = get_plot_colors(n_panels, options.color_mode, options.single_color)

    #==========================================================================
    # STEP 4: POPULATE PLOTS WITH DATA
    #==========================================================================
    for i, (center_time, var) in enumerate(plot_list):
        print_manager.custom_debug(f'Adding data to plot panel {i+1}/{n_panels}... \n')
        center_dt = pd.Timestamp(center_time)
        
        # Get encounter number automatically
        enc_num = get_encounter_number(center_time)
    
        # Format time range
        if options.position == 'around':
            start_time = center_dt - window_td/2
            end_time = center_dt + window_td/2
        elif options.position == 'before':
            start_time = center_dt - window_td
            end_time = center_dt
        else:  # after
            start_time = center_dt
            end_time = center_dt + window_td
        
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
    
                        ax2.plot(single_var.datetime_array[indices], 
                                single_var.data[indices],
                                linewidth=single_var.line_width,
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
                        
                        if panel_color:
                            apply_panel_color(ax2, panel_color, options)
                    
                    else:
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(single_var, 'color') and single_var.color is not None:
                            plot_color = single_var.color
                        elif axis_options.color is not None:
                            plot_color = axis_options.color
                        else:
                            plot_color = None
    
                        axs[i].plot(single_var.datetime_array[indices], 
                                   single_var.data[indices],
                                   linewidth=single_var.line_width,
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
                            axs[i].plot(var.datetime_array[indices], 
                                        var.data[indices],
                                        linewidth=var.line_width,
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

                            axs[i].scatter(var.datetime_array[indices],
                                          var.data[indices],
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
                            data_clipped = np.array(var.data)[indices]
                            additional_data_clipped = np.array(var.additional_data)[indices]
                            
                            colorbar_limits = axis_options.colorbar_limits if hasattr(axis_options, 'colorbar_limits') and axis_options.colorbar_limits else var.colorbar_limits
                            if var.colorbar_scale == 'log':
                                norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                            elif var.colorbar_scale == 'linear':
                                norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
        
                            im = axs[i].pcolormesh(datetime_clipped, additional_data_clipped, data_clipped,
                                                   norm=norm, cmap=var.colormap, shading='auto')
                            
                            pos = axs[i].get_position()
                            cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                            cbar = fig.colorbar(im, cax=cax)
        
                            if hasattr(var, 'colorbar_label'):
                                cbar.set_label(var.colorbar_label)
                        else:
                            # Handle empty data case for spectral data
                            print_manager.warning(f"No spectral data to plot for panel {i+1} - skipping plot")
                            axs[i].text(0.5, 0.5, 'No data for this time range', 
                                       ha='center', va='center', transform=axs[i].transAxes,
                                       fontsize=10, color='gray', style='italic')
                else:
                    plot_color = panel_color
                    if not plot_color:
                        plot_color = axis_options.color if axis_options.color else var.color
                    
                    # CRITICAL FIX: Check if indices is empty before trying to plot
                    if len(indices) > 0:
                        axs[i].plot(var.datetime_array[indices], 
                                    var.data[indices],
                                    linewidth=var.line_width,
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
            
            axs[i].set_ylim(validated_y_limit)
        elif isinstance(var, list):
            all_data = []
            for single_var in var:
                if hasattr(single_var, 'y_limit') and single_var.y_limit:
                    all_data.extend(single_var.y_limit)
            if all_data:
                y_min, y_max = min(all_data), max(all_data)
                axs[i].set_ylim(y_min, y_max)
        elif hasattr(var, 'y_limit') and var.y_limit:
            axs[i].set_ylim(var.y_limit)
        else:
            # Auto-scaling happens by default
            current_ylim = axs[i].get_ylim()
    
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
                axs[i].set_ylabel(y_label, fontsize=options.y_label_size, 
                                  labelpad=options.y_label_pad)
            else:
                y_label = f"$\\mathbf{{{enc_num}}}$"
                axs[i].set_ylabel(y_label, fontsize=options.y_label_size,
                                  rotation=0, ha='right', va='center',
                                  labelpad=options.y_label_pad)
        else:
            axs[i].set_ylabel(y_label, fontsize=options.y_label_size,
                              labelpad=options.y_label_pad)
    
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
    
        if options.use_relative_time:
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
                         axs[i].set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Perihelion)", 
                                        fontweight='bold', fontsize=options.x_label_size)
                   
            else:
                axs[i].set_xticklabels(tick_labels)
                if i < n_panels - 1:
                    axs[i].set_xlabel('')
                else:
                    if options.use_custom_x_axis_label:
                        axs[i].set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Perihelion)", 
                                        fontweight='bold', fontsize=options.x_label_size)
    
            # Add these two lines to set tick label sizes when using relative time
            axs[i].tick_params(axis='x', labelsize=options.x_tick_label_size)
            axs[i].tick_params(axis='y', labelsize=options.y_tick_label_size)
    
            # After setting tick sizes in the relative time section
            # Apply border line width to all spines (top, bottom, left, right)
            for spine_name, spine in axs[i].spines.items():
                spine.set_linewidth(plt.options.border_line_width)
    
        if options.draw_vertical_line:
            color_to_use = panel_color if panel_color else options.vertical_line_color
            axs[i].axvline(x=center_dt, 
                           color=color_to_use,
                           linestyle=options.vertical_line_style,
                           linewidth=options.vertical_line_width)
    
        if options.use_single_title:
            if i == 0:
                title = (options.single_title_text if options.single_title_text 
                         else f"{enc_num} - {pos_desc[options.position]} - {pd.Timestamp(center_time).strftime('%Y-%m-%d %H:%M')}")
                if options.color_mode in ['rainbow', 'single'] and panel_color:
                    axs[i].set_title(title, fontsize=options.title_fontsize, fontweight='bold', color=panel_color)
                else:
                    axs[i].set_title(title, fontsize=options.title_fontsize, fontweight='bold')
        else:
            title = f"{enc_num} - {pos_desc[options.position]} - {pd.Timestamp(center_time).strftime('%Y-%m-%d %H:%M')}"
            if options.color_mode in ['rainbow', 'single'] and panel_color:
                axs[i].set_title(title, fontsize=options.title_fontsize, color=panel_color)
            else:
                axs[i].set_title(title, fontsize=options.title_fontsize)
    
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
    
    if not options.use_relative_time:
        for i, ax in enumerate(axs):
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    ax.set_xticklabels([])
                    ax.set_xlabel('')
                else:
                    if options.use_custom_x_axis_label:
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        ax.set_xlabel("Time", fontweight='bold', fontsize=options.x_label_size)
            else:
                if i == len(axs) - 1:
                    if options.use_custom_x_axis_label:
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        ax.set_xlabel("Time", fontweight='bold', fontsize=options.x_label_size)
                else:
                    ax.set_xlabel('')
    
            ax.tick_params(axis='x', labelsize=options.x_tick_label_size)
            ax.tick_params(axis='y', labelsize=options.y_tick_label_size)
    
    # NEW: Apply dynamic x-axis tick coloring for all panels (changed from only bottom panel)
    if color_scheme:
        for i, ax in enumerate(axs):
            apply_bottom_axis_color(ax, color_scheme['panel_colors'][i])
    
    print_manager.status("Generating multiplot...\n")
    plt.show()
    print_manager.debug("=== Multiplot Complete ===\n")
    
    fig.savefig('multiplot_output.png', dpi=300, bbox_inches='tight', pad_inches=0)
    return fig, axs

print('📈📉 Multiplot Initialized')