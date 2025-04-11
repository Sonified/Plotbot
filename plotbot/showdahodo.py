# Import plotbot components with relative imports
from .print_manager import print_manager
from .data_cubby import data_cubby
from .data_tracker import global_tracker  
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .plotbot_helpers import time_clip
from .multiplot_options import plt  # Import our enhanced plt with options
from .get_data import get_data  # Import get_data function

from matplotlib.colors import Normalize
from scipy import stats
import matplotlib.dates as mdates
import numpy as np
from dateutil.parser import parse
import pandas as pd
import scipy.signal as signal
import matplotlib.colors as colors
from datetime import datetime, timezone, timedelta
#%matplotlib notebook
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import logging

def showdahodo(trange, var1, var2, var3 = None, color_var = None, norm_ = None, 
               xlim_ = None, ylim_ = None, zlim_ = None, s_ = None, alpha_ = None, 
               xlabel_ = None, ylabel_ = None, zlabel_ = None, clabel_ = None, 
               xlog_ = None, ylog_ = None, zlog_ = None, cmap_ = None, 
               elev = None, azi = None, roll = None, sort = None, invsort = None, lumsort = None, 
               brazil = None, corr = None, wvpow = None, rsun = None, noshow = None, 
               face_c = None, face_a = None, fname = None):
    """
    Create a hodogram plot of two variables, optionally colored by a third variable.
    Also calculates and displays the correlation coefficient and plots a trend line.
    """
    
    # print("Starting showdahodo with plotbot class integration...")
    
    # ====================================================================
    # PART 1: DOWNLOAD AND PROCESS DATA (adapted from plotbot)
    # ====================================================================
    
    # Validate time range
    try:
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        
        if start_time >= end_time:
            print_manager.error(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
            return None
    except (ValueError, TypeError) as e:  # Catch TypeError for non-string inputs
        logging.error(f"showdahodo: Invalid time format or type in trange: {e}")
        print_manager.error(f"showdahodo: Invalid time format or type provided: {trange}. Please use 'YYYY-MM-DD HH:MM:SS' or similar.")
        return None
    
    # Identify required data types
    required_data_types = {var1.data_type, var2.data_type}

    if var3 is not None:
        required_data_types.add(var3.data_type)
    if color_var is not None:
        required_data_types.add(color_var.data_type)
    
    # Special handling for custom variables
    custom_vars = []
    if 'custom_data_type' in required_data_types:
        print_manager.processing("Processing custom variables...")
        # Collect all custom variables
        if var1.data_type == 'custom_data_type':
            custom_vars.append(var1)
        if var2.data_type == 'custom_data_type':
            custom_vars.append(var2)
        if var3 is not None and var3.data_type == 'custom_data_type':
            custom_vars.append(var3)
        if color_var is not None and color_var.data_type == 'custom_data_type':
            custom_vars.append(color_var)
        
        # Process each custom variable
        for var in custom_vars:
            if hasattr(var, 'source_var') and var.source_var is not None:
                # Get base variables (non-custom) that need to be downloaded
                base_vars = []
                for src_var in var.source_var:
                    if hasattr(src_var, 'class_name') and src_var.class_name != 'custom_class' and src_var.data_type != 'custom_data_type':
                        base_vars.append(src_var)
                
                # Download fresh data for base variables if needed
                if base_vars:
                    print_manager.processing(f"Downloading fresh data for {len(base_vars)} source variables...")
                    get_data(trange, *base_vars)
            
            # Update the variable with new time range
            if hasattr(var, 'update'):
                print_manager.processing(f"Updating custom variable: {var.subclass_name}...")
                updated_var = var.update(trange)
                if updated_var is not None:
                    print_manager.processing(f"Successfully updated custom variable: {var.subclass_name}")
                else:
                    print_manager.warning(f"Warning: update method for {var.subclass_name} returned None")
    
    # Collect regular variables for data loading
    regular_vars = []
    if var1.data_type != 'custom_data_type':
        regular_vars.append(var1)
    if var2.data_type != 'custom_data_type':
        regular_vars.append(var2)
    if var3 is not None and var3.data_type != 'custom_data_type':
        regular_vars.append(var3)
    if color_var is not None and color_var.data_type != 'custom_data_type':
        regular_vars.append(color_var)
    
    # Use get_data for all regular variables (same as plotbot_main.py)
    if regular_vars:
        print_manager.processing(f"Loading data for {len(regular_vars)} regular variables...")
        get_data(trange, *regular_vars)

    # Get processed variable instances
    var1_instance = data_cubby.grab(var1.class_name).get_subclass(var1.subclass_name)
    var2_instance = data_cubby.grab(var2.class_name).get_subclass(var2.subclass_name)
    color_var_instance = None
    var3_instance = None
    if color_var is not None:
        color_var_instance = data_cubby.grab(color_var.class_name).get_subclass(color_var.subclass_name)
    if var3 is not None:
        var3_instance = data_cubby.grab(var3.class_name).get_subclass(var3.subclass_name)
    # ====================================================================
    # PART 2: HELPER FUNCTIONS (from original showdahodo)
    # ====================================================================
    
    def apply_time_range(trange, time_array, values_array):
        """Extract data within specified time range."""
        # Parse time range using dateutil.parser.parse
        try:
            start_dt = parse(trange[0]).replace(tzinfo=timezone.utc)
            stop_dt = parse(trange[1]).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError) as e:
             logging.error(f"apply_time_range: Invalid time format or type in trange: {e}")
             print_manager.error(f"apply_time_range: Invalid time format or type provided: {trange}. Please use 'YYYY-MM-DD HH:MM:SS' or similar.")
             # Return empty arrays or raise an error, depending on desired behavior
             return np.array([]), np.array([])

        # Convert to numeric timestamps for comparison
        start_ts = mdates.date2num(start_dt)
        stop_ts = mdates.date2num(stop_dt)
        time_ts = mdates.date2num(time_array)
        
        # Find indices within time range
        indices = np.where((time_ts >= start_ts) & (time_ts <= stop_ts))[0]
        
        if len(indices) == 0:
            return np.array([]), np.array([])
            
        return time_array[indices], values_array[indices]
    
    def downsample_time_based(x_time, x_values, target_times):
        """Interpolate x_values to match target_times using simple linear interpolation."""
        try:
            # Convert datetime arrays to numeric timestamps for interpolation
            x_time_numeric = mdates.date2num(x_time)
            target_times_numeric = mdates.date2num(target_times)
            
            # Check for sufficient data points for interpolation
            if len(x_time) < 2:
                if len(x_time) == 1 and len(target_times) > 0:
                    # If we only have one point, replicate it for all target times
                    return np.full(len(target_times), x_values[0])
                return None
            
            # Handle NaN values
            valid_mask = ~np.isnan(x_values)
            valid_count = np.sum(valid_mask)
            
            if not np.any(valid_mask):
                return np.full(len(target_times), np.nan)
                
            if not np.all(valid_mask):
                x_time_numeric = x_time_numeric[valid_mask]
                x_values = x_values[valid_mask]
                
                # Re-check if we have enough points after removing NaNs
                if len(x_time_numeric) < 2:
                    if len(x_time_numeric) == 1:
                        # If we only have one point, replicate it for all target times
                        return np.full(len(target_times), x_values[0])
                    return None
            
            # Simple linear interpolation
            from scipy import interpolate
            f = interpolate.interp1d(
                x_time_numeric, x_values,
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
            
            new_values = f(target_times_numeric)
            return new_values
            
        except Exception as e:
            print_manager.debug(f"Error in interpolation: {str(e)}")
            return None
    
    # ====================================================================
    # PART 3: PREPARE DATA FOR PLOTTING
    # ====================================================================
    print_manager.processing("Preparing data for plotting...")
    
    # Extract data from class instances
    values1_full = var1_instance.data
    time1_full = var1_instance.datetime_array
    values2_full = var2_instance.data  
    time2_full = var2_instance.datetime_array
    # Save original lengths
    time1_original_len = len(time1_full)
    time2_original_len = len(time2_full)
    color_var_original_len = 0
    var3_original_len = 0
    if color_var_instance is not None:
        color_var_full = color_var_instance.data
        color_time_full = color_var_instance.datetime_array
        color_var_original_len = len(color_time_full) if color_time_full is not None else 0
    else:
        color_var_full = None
        color_time_full = None

    if var3_instance is not None:
        values3_full = var3_instance.data
        time3_full = var3_instance.datetime_array
        var3_original_len = len(time3_full) if time3_full is not None else 0
    else:
        values3_full = None
        time3_full = None

    print_manager.debug(f"DEBUG: Original lengths - time1: {time1_original_len}, time2: {time2_original_len}, color: {color_var_original_len}, var3: {var3_original_len}")
    
    # Apply time range 
    time1_clipped, values1_clipped = apply_time_range(trange, time1_full, values1_full)
    time2_clipped, values2_clipped = apply_time_range(trange, time2_full, values2_full)
    
    # Check data availability
    if len(time1_clipped) == 0 or len(time2_clipped) == 0:
        print_manager.warning("No data available in the specified time range")
        return None
    
    time1_clipped_len = len(time1_clipped)
    time2_clipped_len = len(time2_clipped)
    
    # Prepare color data if provided
    if color_var is not None:
        color_values_full = color_var_instance.data
        color_time_full = color_var_instance.datetime_array
        
        if color_values_full is not None and color_time_full is not None:
            color_time_original_len = len(color_time_full)
            
            # Apply time range to color data
            color_time_clipped, color_values_clipped = apply_time_range(trange, color_time_full, color_values_full)
            
            if color_time_clipped is not None and color_values_clipped is not None:
                color_time_clipped_len = len(color_time_clipped)
                
                if len(color_time_clipped) == 0:
                    print_manager.warning("No color data available in the specified time range")
                    color_var = None  # Fall back to time-based coloring
                    color_time_clipped = None
                    color_values_clipped = None
            else:
                color_time_clipped = None
                color_values_clipped = None
                color_time_clipped_len = 0
        else:
            color_time_clipped = None
            color_values_clipped = None
            color_time_original_len = 0
            color_time_clipped_len = 0

    # Prepare var3 data if provided
    if var3 is not None:
        var3_values_full = var3_instance.data
        var3_time_full = var3_instance.datetime_array
        var3_time_original_len = len(var3_time_full)
        
        # Apply time range to var3 data
        var3_time_clipped, var3_values_clipped = apply_time_range(trange, var3_time_full, var3_values_full)
        var3_time_clipped_len = len(var3_time_clipped)
        
        if len(var3_time_clipped) == 0:
            print_manager.warning("No var3 data available in the specified time range")
            var3 = None  # Fall back to time-based coloring
            var3_time_clipped = None
            var3_values_clipped = None
        var3_values = None  # Explicitly initialize var3_values to None
    else:
        # Initialize var3-related variables only, don't reset color variables!
        var3_time_clipped = None
        var3_values_clipped = None
        var3_time_original_len = 0
        var3_time_clipped_len = 0
        var3_values = None  # Explicitly initialize var3_values to None
    
    # Determine which time series has the lowest sampling rate for target_times
    lengths = {
        'time1': time1_clipped_len,
        'time2': time2_clipped_len
    }
    
    if color_var is not None and color_time_clipped is not None and len(color_time_clipped) > 0:
        lengths['color_time'] = color_time_clipped_len

    if var3 is not None and var3_time_clipped is not None and len(var3_time_clipped) > 0:
        lengths['var3_time'] = var3_time_clipped_len
        
    min_length = min(lengths.values())
    
    if lengths['time1'] == min_length:
        target_times = time1_clipped
    elif lengths['time2'] == min_length:
        target_times = time2_clipped
    elif color_var is not None and 'color_time' in lengths and lengths['color_time'] == min_length:
        target_times = color_time_clipped
    elif var3 is not None and 'var3_time' in lengths and lengths['var3_time'] == min_length:
        target_times = var3_time_clipped
    
    # Check if time arrays are equal or need resampling
    print_manager.debug(f"Data lengths - time1: {time1_clipped_len}, time2: {time2_clipped_len}, " +
                        f"color: {color_time_clipped_len if color_var is not None and color_time_clipped is not None else 'N/A'}, " +
                        f"var3: {var3_time_clipped_len if var3 is not None and var3_time_clipped is not None else 'N/A'}")
    
    if target_times is None:
        print_manager.warning("Target times is None, falling back to time1_clipped")
        # Fall back to using time1_clipped if target_times is None
        target_times = time1_clipped
    
    # Determine which variables need resampling by comparing with target_times
    time1_needs_resampling = not (len(time1_clipped) == len(target_times) and 
                              np.array_equal(mdates.date2num(time1_clipped), mdates.date2num(target_times)))
    
    time2_needs_resampling = not (len(time2_clipped) == len(target_times) and 
                              np.array_equal(mdates.date2num(time2_clipped), mdates.date2num(target_times)))
    
    color_needs_resampling = False
    if color_var is not None and color_time_clipped is not None and len(color_time_clipped) > 0:
        # Always resample if the arrays have different lengths
        if len(color_time_clipped) != len(target_times):
            color_needs_resampling = True
        else:
            # Only compare arrays if they are the same length
            color_needs_resampling = not np.array_equal(mdates.date2num(color_time_clipped), mdates.date2num(target_times))
    
    var3_needs_resampling = False
    if var3 is not None and var3_time_clipped is not None and len(var3_time_clipped) > 0:
        var3_needs_resampling = not (len(var3_time_clipped) == len(target_times) and 
                                 np.array_equal(mdates.date2num(var3_time_clipped), mdates.date2num(target_times)))
    
    # Resample variables as needed
    print_manager.processing(f"Resampling status - time1: {time1_needs_resampling}, time2: {time2_needs_resampling}, color: {color_needs_resampling}, var3: {var3_needs_resampling}")
    
    # Always resample variables that need it
    if time1_needs_resampling:
        print_manager.processing("Resampling time1")
        values1 = downsample_time_based(time1_clipped, values1_clipped, target_times)
    else:
        values1 = values1_clipped
        
    if time2_needs_resampling:
        print_manager.processing("Resampling time2")
        values2 = downsample_time_based(time2_clipped, values2_clipped, target_times)
    else:
        values2 = values2_clipped
        
    if color_var is not None and color_time_clipped is not None and len(color_time_clipped) > 0:
        if color_needs_resampling:
            print_manager.processing("Resampling color values")
            color_values = downsample_time_based(color_time_clipped, color_values_clipped, target_times)
            if color_values is None:
                # In case interpolation fails, create a default color array
                print_manager.debug("Interpolation failed for color values, creating default gradient")
                # Use a simple gradient based on the original values
                min_val = np.nanmin(color_values_clipped)
                max_val = np.nanmax(color_values_clipped)
                color_values = np.linspace(min_val, max_val, len(target_times))
        else:
            color_values = color_values_clipped
    else:
        color_values = None
        
    if var3 is not None and var3_time_clipped is not None and len(var3_time_clipped) > 0:
        if var3_needs_resampling:
            var3_values = downsample_time_based(var3_time_clipped, var3_values_clipped, target_times)
        else:
            var3_values = var3_values_clipped
    else:
        var3_values = None
    
    # Prepare colors
    if color_var is None or color_values is None:
        # Convert to days from first time point, which is what colorbar expects
        times_num = mdates.date2num(target_times)
        colors = times_num - times_num[0]
        color_label = 'Time'
    else:
        colors = color_values
        color_label = color_var_instance.legend_label if clabel_ is None else clabel_
    
    # ====================================================================
    # PART 4: CREATE THE HODOGRAM PLOT
    # ====================================================================
    print_manager.processing("Creating hodogram plot...")
    
    # Create the plot
    #fig = plt.figure(figsize=(8, 6))
    #ax = fig.add_subplot(111)
    
    # Set default values if not specified
    s_ = 20 if s_ is None else s_
    alpha_ = 0.7 if alpha_ is None else alpha_
    norm_ = Normalize() if norm_ is None else norm_
    cmap_ = 'plasma' if cmap_ is None else cmap_
    
    # ===================================================================
    # HANDLE SORT OPERATIONS FOR 3D AND COLOR VALUES
    # ===================================================================
    # Sort data by color if requested
    if sort is not None:
        print_manager.processing("Sorting by ascending color value")
        sort_c = np.argsort(colors)
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
        if var3 is not None and 'var3_values' in locals():
            var3_values = var3_values[sort_c]
        
    if invsort is not None:
        print_manager.processing("Sorting by descending color value")
        sort_c = np.argsort(colors)[::-1]
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
        if var3 is not None and 'var3_values' in locals():
            var3_values = var3_values[sort_c]
    
    # Create hodogram scatter plot
    fig = plt.figure()
    
    if var3 is not None and 'var3_values' in locals() and var3_values is not None:
        ax = fig.add_subplot(projection='3d')
        s = ax.scatter(values1, values2, var3_values, c=colors, cmap=cmap_, norm=norm_, s=s_, alpha=alpha_)
        cbar = plt.colorbar(s, label=color_label, pad = .1)
    else:
        ax = fig.add_subplot()
        s = ax.scatter(values1, values2, c=colors, cmap=cmap_, norm=norm_, s=s_, alpha=alpha_)
        cbar = plt.colorbar(s, label=color_label)
    
    #set colorbar to no transparency
    cbar.solids.set(alpha=1)

    # Set background color if specified
    if face_c is not None:
        ax.patch.set_facecolor(face_c)
    if face_a is not None:
        ax.patch.set_alpha(face_a)
    
    # Calculate correlation coefficient and add trend line
    corr_title = ''
    if corr is not None:
        # Get valid data points
        valid_mask = ~np.isnan(values1) & ~np.isnan(values2)
        
        if ((xlog_ is not None) and (ylog_ is not None)) or brazil is not None:
            # Log-scale correlation requires positive values
            log_mask = valid_mask & (values1 > 0) & (values2 > 0)
            if np.sum(log_mask) > 1:
                log_values1 = np.log10(values1[log_mask])
                log_values2 = np.log10(values2[log_mask])
                correlation = np.corrcoef(log_values1, log_values2)[0, 1]
                corr_title = f'Corr Coeff: {correlation:.2f}, '
        else:
            # Linear correlation
            if np.sum(valid_mask) > 1:
                correlation, p_value = stats.pearsonr(values1[valid_mask], values2[valid_mask])
                # Calculate trend line
                z = np.polyfit(values1[valid_mask], values2[valid_mask], 1)
                p = np.poly1d(z)
                plt.plot(values1, p(values1), ".k", alpha=0.5)  # Add trend line
                corr_title = f'Corr Coef: {correlation:.2f}, '
    
    # Format colorbar for time data
    if color_var is None:
        # Use a simple formatter for time on colorbar
        def time_formatter(x, pos):
            # x is days from first time point
            days_fraction = x
            if days_fraction >= 0 and days_fraction <= colors[-1]:
                base_date = mdates.num2date(mdates.date2num(target_times[0]))
                delta = timedelta(days=days_fraction)
                date = base_date + delta
                return date.strftime('%Y-%m-%d/%H:%M:%S')
            return ''
            
        cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(time_formatter))
    
    # Set axis labels
    if xlabel_ is not None:
        xlabel = xlabel_
    else:
        xlabel = var1_instance.legend_label
        
    if ylabel_ is not None:
        ylabel = ylabel_
    else:
        ylabel = var2_instance.legend_label

    if zlabel_ is not None:
        zlabel = zlabel_
    else:
        if var3_instance is not None:
            zlabel = var3_instance.legend_label
        else:
            zlabel = ""

    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    if var3 is not None:
        ax.set_zlabel(zlabel, fontsize=16)
    
    # Set axis limits if specified
    if xlim_ is not None:
        ax.set_xlim(xlim_)
    if ylim_ is not None:
        ax.set_ylim(ylim_)
    if zlim_ is not None:
        ax.set_zlim(zlim_)
        
    # Handle brazil plot mode (instability thresholds)
    if brazil is not None:
        print_manager.processing("Adding instability thresholds (Brazil plot)")
        beta_par = np.arange(0, 1000, 1e-4)
        trat_parfire = 1-(.47/(beta_par - .59)**.53)
        trat_oblfire = 1-(1.4/(beta_par + .11))
        trat_protcyc = 1+(.43/(beta_par + .0004)**.42)
        trat_mirror = 1+(.77/(beta_par + .016)**.76)
        plt.plot(beta_par, trat_parfire, color='black', linestyle='dashed')
        plt.plot(beta_par, trat_oblfire, color='grey', linestyle='dashed')
        plt.plot(beta_par, trat_protcyc, color='black', linestyle='dotted')
        plt.plot(beta_par, trat_mirror, color='grey', linestyle='dotted')
        plt.loglog()
        
    # Set axis scales
    if xlog_ is not None:
        ax.set_xscale('log')
    if ylog_ is not None:
        ax.set_yscale('log')
    if zlog_ is not None:
        ax.set_zscale('log')
    
    # Build title
    tname = f"{trange[0]}" + ' - ' + f"{trange[1]}"
    
    # Add radial sun distance to title if requested
    rsun_title = ''
    if rsun is not None:
        try:
            # Try to get actual distance data if available
            dist_time_clipped, dist_values_clipped = apply_time_range(trange, datetime_spi, sun_dist_rsun)    
            sun_dist_rsun_clipped_avg = np.round(np.average(dist_values_clipped), 1)
            rsun_title = f"Rs = {sun_dist_rsun_clipped_avg}, "
        except NameError:
            # Fallback if distance data not available
            rsun_title = f"Rs requested, "
    
    # Set plot title
    plt.title(rsun_title + corr_title + tname, fontsize=12)

    if elev and azi and roll is not None:
        ax.view_init(elev, azi, roll)
    
    # Save figure if filename provided
    if fname is not None:
        plt.savefig(f"{fname}_brazil.png", bbox_inches='tight')
    
    # Show plot unless noshow specified
    if noshow is None:
        plt.show();
    
    return fig, ax

print("✨ Showdahodo initialized")