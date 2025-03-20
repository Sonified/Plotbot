# Import plotbot components with relative imports
from .print_manager import print_manager
from .data_cubby import data_cubby
from .data_tracker import global_tracker  
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .plotbot_helpers import time_clip
from .multiplot_options import plt  # Import our enhanced plt with options

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
    start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    
    if start_time >= end_time:
        print(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
        return None
    
    # Identify required data types
    required_data_types = {var1.data_type, var2.data_type}

    if var3 is not None:
        required_data_types.add(var3.data_type)
    if color_var is not None:
        required_data_types.add(color_var.data_type)
    
    # Download and process data for each data type
    for data_type in required_data_types:
        print(f"Processing {data_type}...")
        
        download_new_psp_data(trange, data_type)
        
        # Get class instance
        if data_type == var1.data_type:
            class_name = var1.class_name
        elif data_type == var2.data_type:
            class_name = var2.class_name
        elif color_var is not None and data_type == color_var.data_type:
            class_name = color_var.class_name
        elif var3 is not None and data_type == var3.data_type:
            class_name = var3.class_name
        
        class_instance = data_cubby.grab(class_name)
        
        # Check if we need to update data
        needs_import = global_tracker.is_import_needed(trange, data_type)
        needs_refresh = False
        
        if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
            cached_start = np.datetime64(class_instance.datetime_array[0], 's')
            cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
            requested_start = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'), 's')
            requested_end = np.datetime64(datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f'), 's')
            
            # Add buffer for timing differences
            buffered_start = cached_start - np.timedelta64(10, 's')
            buffered_end = cached_end + np.timedelta64(10, 's')
            
            if buffered_start > requested_start or buffered_end < requested_end:
                print(f"{data_type} - Requested time falls outside cached data range, updating...")
                needs_refresh = True

        if needs_import or needs_refresh:
            data_obj = import_data_function(trange, data_type)
            if needs_import:
                global_tracker.update_imported_range(trange, data_type)
            
            class_instance.update(data_obj)

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
        # Parse time range
        start_dt = parse(trange[0])
        stop_dt = parse(trange[1])
        
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
        # Convert datetime arrays to numeric timestamps for interpolation
        x_time_numeric = mdates.date2num(x_time)
        target_times_numeric = mdates.date2num(target_times)
        
        # Handle NaN values
        valid_mask = ~np.isnan(x_values)
        if not np.any(valid_mask):
            return np.full_like(target_times_numeric, np.nan)
            
        if not np.all(valid_mask):
            x_time_numeric = x_time_numeric[valid_mask]
            x_values = x_values[valid_mask]
        
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
    
    # ====================================================================
    # PART 3: PREPARE DATA FOR PLOTTING
    # ====================================================================
    print("Preparing data for plotting...")
    
    # Extract data from class instances
    values1_full = var1_instance.data
    time1_full = var1_instance.datetime_array
    values2_full = var2_instance.data  
    time2_full = var2_instance.datetime_array

    # Save original lengths
    time1_original_len = len(time1_full)
    time2_original_len = len(time2_full)
    
    # Apply time range 
    time1_clipped, values1_clipped = apply_time_range(trange, time1_full, values1_full)
    time2_clipped, values2_clipped = apply_time_range(trange, time2_full, values2_full)
    
    # Check data availability
    if len(time1_clipped) == 0 or len(time2_clipped) == 0:
        print("No data available in the specified time range")
        return None
    
    time1_clipped_len = len(time1_clipped)
    time2_clipped_len = len(time2_clipped)
    
    # Prepare color data if provided
    if color_var is not None:
        color_values_full = color_var_instance.data
        color_time_full = color_var_instance.datetime_array
        color_time_original_len = len(color_time_full)
        
        # Apply time range to color data
        color_time_clipped, color_values_clipped = apply_time_range(trange, color_time_full, color_values_full)
        color_time_clipped_len = len(color_time_clipped)
        
        if len(color_time_clipped) == 0:
            print("No color data available in the specified time range")
            color_var = None  # Fall back to time-based coloring
            color_time_clipped = None
            color_values_clipped = None

    # Prepare color data if provided
    if var3 is not None:
        var3_values_full = var3_instance.data
        var3_time_full = var3_instance.datetime_array
        var3_time_original_len = len(var3_time_full)
        
        # Apply time range to color data
        var3_time_clipped, var3_values_clipped = apply_time_range(trange, var3_time_full, var3_values_full)
        var3_time_clipped_len = len(var3_time_clipped)
        
        if len(var3_time_clipped) == 0:
            print("No var3 data available in the specified time range")
            var3 = None  # Fall back to time-based coloring
            var3_time_clipped = None
            var3_values_clipped = None
    else:
        color_time_clipped = None
        color_values_clipped = None
        color_time_original_len = 0
        color_time_clipped_len = 0
        var3_time_clipped = None
        var3_values_clipped = None
        var3_time_original_len = 0
        var3_time_clipped_len = 0
    
    # Determine which time series has the lowest sampling rate for target_times
    lengths = {
        'time1': time1_clipped_len,
        'time2': time2_clipped_len
    }
    
    if color_var is not None:
        lengths['color_time'] = color_time_clipped_len

    if var3 is not None:
        lengths['var3_time'] = var3_time_clipped_len
        
    min_length = min(lengths.values())
    
    if lengths['time1'] == min_length:
        target_times = time1_clipped
    elif lengths['time2'] == min_length:
        target_times = time2_clipped
    elif color_var is not None and lengths['color_time'] == min_length:
        target_times = color_time_clipped
    elif var3 is not None and lengths['var3_time'] == min_length:
        target_times = var3_time_clipped
    
    # Check if time arrays are equal or need resampling
    time_arrays_equal = (len(time1_clipped) == len(target_times) and 
                         np.array_equal(mdates.date2num(time1_clipped), mdates.date2num(target_times)))
    time_arrays_equal = time_arrays_equal and (len(time2_clipped) == len(target_times) and 
                        np.array_equal(mdates.date2num(time2_clipped), mdates.date2num(target_times)))
    
    if color_var is not None:
        time_arrays_equal = time_arrays_equal and (len(color_time_clipped) == len(target_times) and 
                            np.array_equal(mdates.date2num(color_time_clipped), mdates.date2num(target_times)))

    if var3 is not None:
        time_arrays_equal = time_arrays_equal and (len(var3_time_clipped) == len(target_times) and 
                            np.array_equal(mdates.date2num(var3_time_clipped), mdates.date2num(target_times)))
    
    # Resample data if needed
    if time_arrays_equal:
        print("No resampling needed - time arrays are aligned")
        values1 = values1_clipped
        values2 = values2_clipped
        if color_var is not None:
            color_values = color_values_clipped
        if var3 is not None:
            var3_values = var3_values_clipped
    else:
        print("Resampling data to align time series")
        if not np.array_equal(mdates.date2num(time1_clipped), mdates.date2num(target_times)):
            values1 = downsample_time_based(time1_clipped, values1_clipped, target_times)
        else:
            values1 = values1_clipped
            
        if not np.array_equal(mdates.date2num(time2_clipped), mdates.date2num(target_times)):
            values2 = downsample_time_based(time2_clipped, values2_clipped, target_times)
        else:
            values2 = values2_clipped
            
        if color_var is not None:
            if not np.array_equal(mdates.date2num(color_time_clipped), mdates.date2num(target_times)):
                color_values = downsample_time_based(color_time_clipped, color_values_clipped, target_times)
            else:
                color_values = color_values_clipped

        if var3 is not None:
            if not np.array_equal(mdates.date2num(var3_time_clipped), mdates.date2num(target_times)):
                var3_values = downsample_time_based(var3_time_clipped, var3_values_clipped, target_times)
            else:
                var3_values = var3_values_clipped
    
    # Prepare colors
    if color_var is None:
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
    print("Creating hodogram plot...")
    
    # Create the plot
    #fig = plt.figure(figsize=(8, 6))
    #ax = fig.add_subplot(111)
    
    # Set default values if not specified
    s_ = 20 if s_ is None else s_
    alpha_ = 0.7 if alpha_ is None else alpha_
    norm_ = Normalize() if norm_ is None else norm_
    cmap_ = 'plasma' if cmap_ is None else cmap_
    
    # Sort data by color if requested
    if sort is not None:
        print("Sorting by ascending color value")
        sort_c = np.argsort(colors)
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
        
    if invsort is not None:
        print("Sorting by descending color value")
        sort_c = np.argsort(colors)[::-1]
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
    
    # Create hodogram scatter plot
    fig = plt.figure()
    
    if var3 is not None:
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
        zlabel = var3_instance.legend_label

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
        print("Adding instability thresholds (Brazil plot)")
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