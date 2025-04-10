import matplotlib.pyplot as plt
import matplotlib.colors as colors

plt.rcParams['mathtext.fontset'] = 'stix' #resolves a warning for symbol interpretation

#-----Plotpbot Options-----\

plotbot_custom_options = {}

class PlotbotManager:
    def __init__(self):
        self.custom_options = {}

    def set_option(self, variable, option, value):
        if variable not in self.custom_options:
            self.custom_options[variable] = {}
        self.custom_options[variable][option] = value

plotbot_manager = PlotbotManager()

def ploptions(variable, option, value):
    plotbot_manager.set_option(variable, option, value)

#-----Other Functions-----\

def time_clip(tarray, start, stop): #Currently called within Plotbot
    #input time array in date_time format
    #input start and stop times in '%Y-%m-%d/%H:%M:%S.%f format

    # Ensure datetime_spe is a numpy array
    tarray_np = np.array(tarray)
    start_dt = parse(start).replace(tzinfo=timezone.utc)
    stop_dt = parse(stop).replace(tzinfo=timezone.utc)

    return np.where((tarray_np >= start_dt) & (tarray_np <= stop_dt))[0] #outputs the subset of indexes for which that is true

def apply_time_range(trange, datetime_array, *data_arrays): #Applies the time range to the data
    datetime_array = np.array(datetime_array)
    time_indices = time_clip(datetime_array, trange[0], trange[1])
    datetime_clipped = datetime_array[time_indices]
    data_arrays_clipped = [np.array(data_array)[time_indices] for data_array in data_arrays]
    return [datetime_clipped] + data_arrays_clipped

def parse_axis_spec(spec): #Parses the axis specification for the plotbot function
    if isinstance(spec, int):
        return spec, False
    elif isinstance(spec, str) and spec.endswith('r'):
        return int(spec[:-1]), True
    else:
        raise ValueError(f"Invalid axis specification: {spec}")
    
def resample(data, times, new_times): #Currently unused
    ###interpolate data to times from data2
    interpol_f = interpolate.interp1d(times, data,fill_value="extrapolate")
    new_data1 = interpol_f(new_times)    
    return new_times, new_data1


#FITS Code Functions
#Functions:
#define functions
def resample(data, times, new_times):
    ###interpolate data to times from data2
    interpol_f = interpolate.interp1d(times, data,fill_value="extrapolate")
    new_data1 = interpol_f(new_times)    
    return new_times, new_data1

def convert_time(start, stop):
    #input start and stop times as 'yyyy-mm-dd/hh:mm:ss'
    #return dataframe at those indices
    tindex_sf00 = np.where((df_sf00['datetime'] > start) & (df_sf00['datetime'] < stop))
    return df_sf00.iloc[tindex_sf00]

# def time_clip(tarray,start,stop): #NOTE this original funciton was simpler, could cause issues?
#     #input time array in unix time format
#     #input start and stop times as 'yyyy-mm-dd/hh:mm:ss'
#     #return indices
#     ind = np.logical_and(tarray>= time_double(start),tarray <= time_double(stop))
#     return ind

def downsample_time_based(x_time, x_values, target_times):
    """Interpolate x_values to match target_times."""
    # Convert datetime arrays to numeric timestamps
    x_time_numeric = np.array([dt.timestamp() for dt in x_time])
    target_times_numeric = np.array([dt.timestamp() for dt in target_times])

    f = interpolate.interp1d(
        x_time_numeric, x_values,
        kind='linear',
        bounds_error=False,
        fill_value='extrapolate'
    )
    new_values = f(target_times_numeric)
    return new_values



# Function to downsample x_time and x_values to match target_times within a tolerance

# Function to downsample x_time and x_values to match target_times within a tolerance
def downsample_to_match(x_time, x_values, target_times):
    # Convert datetime arrays to numeric timestamps
    x_time_numeric = np.array([dt.timestamp() for dt in x_time])
    target_times_numeric = np.array([dt.timestamp() for dt in target_times])
    tolerance = target_times_numeric[1] - target_times_numeric[0]

    # Sort x_time and keep track of the original indices
    sorted_indices = np.argsort(x_time_numeric)
    x_time_sorted = x_time_numeric[sorted_indices]
    x_values_sorted = x_values[sorted_indices]
    
    #downsampled_x_time = []
    downsampled_x_values = []

    # Function to find the closest match in x_time for a single element in target_times
    def find_closest_within_tolerance(x):
        # Binary search to find the closest index
        pos = np.searchsorted(x_time_sorted, x)
        closest_idx = None
        min_diff = float('inf')
        
        # Check the position and its neighbors
        if pos > 0 and abs(x_time_sorted[pos - 1] - x) < min_diff:
            min_diff = abs(x_time_sorted[pos - 1] - x)
            closest_idx = pos - 1
        if pos < len(x_time_sorted) and abs(x_time_sorted[pos] - x) < min_diff:
            min_diff = abs(x_time_sorted[pos] - x)
            closest_idx = pos
        
        # Return the closest index if within tolerance
        return closest_idx if closest_idx is not None and min_diff < tolerance else None

    # Iterate through target_times and find closest matches in x_time
    for x in target_times_numeric:
        match_idx = find_closest_within_tolerance(x)
        if match_idx is not None:
            #downsampled_x_time.append(x_time_sorted[match_idx])
            downsampled_x_values.append(x_values_sorted[match_idx])
        else:
            # Fill with NaN for no match
            #downsampled_x_time.append(np.nan)        
            downsampled_x_values.append(np.nan)        

    #return np.array(downsampled_x_time), np.array(downsampled_x_values)
    return np.array(downsampled_x_values)

    
# Perform the downsampling
#A tolerance of 1 finds timestamp to nearest second, which works when comparing between sf00, sf0a, spe, waves. 
#may need to adjust to smaller tolerance if comparing electric field and mag for example, since comparison would rely on sub-seconds
#tolerance = 1e0 
#x_time = datetime_spi
#x_values = vmag
#df_sf00['datetime'] = pd.to_datetime(df_sf00['time'], unit='s', utc=True)
# Convert 'datetime' column to NumPy array of datetime.datetime objects
#target_times = df_sf00['datetime'].dt.to_pydatetime()
#downsampled_x_time, downsampled_x_values = downsample_to_match(x_time, x_values, target_times, tolerance=tolerance)

# Output results
#print(f"Downsampled x_time to match x_time: {downsampled_x_time}")
#print(f"Downsampled x_values associated with x_time: {downsampled_x_values}")



# Function to downsample x_time and x_values to match target_times 
def downsample_to_min_ind(x_time, x_values, target_times):
    # Convert datetime arrays to numeric timestamps
    x_time_numeric = np.array([dt.timestamp() for dt in x_time])
    target_times_numeric = np.array([dt.timestamp() for dt in target_times])    
    x_values_ds = []
    for target_times_idx in range(len(target_times_numeric)): 
        i = np.argmin(np.abs(x_time_numeric - target_times_numeric[target_times_idx]))
        x_values_ds.append(x_values[i])
    return np.asarray(x_values_ds)


def upsample_to_match(x_times, x_values, target_times):
    x_times_numeric = np.array([dt.timestamp() for dt in x_times])   
    target_times_numeric = np.array([dt.timestamp() for dt in target_times]) 
    all_values = np.zeros_like(target_times_numeric) + np.nanmin(x_values[np.nonzero(x_values)])*5e-1
    #all_values = np.zeros_like(target_times_numeric) + np.nanmin(x_values[np.nonzero(x_values)])*np.nan

    for x_idx, x_time in enumerate(x_times_numeric):
        target_idx = np.argmin(np.abs(target_times_numeric - x_time))
        all_values[target_idx] = x_values[x_idx]
    return np.asarray(all_values)


import numpy as np
import pandas as pd

def upsample_to_match2(data, x_times, target_times, fill_strategy='nan', labels=None, min_value=None):
    """
    Upsample sparse data to a regular time grid.

    Parameters:
    - data: DataFrame, dict of arrays, or array (1D or 2D)
    - x_times: list/array of datetime objects (same length as data rows)
    - target_times: list/array of datetime objects (desired time grid)
    - fill_strategy: 'nan' (default) or 'minscale'
    - labels: optional list of column names if data is a plain array
    - min_value: optional fill value for 'minscale' strategy

    Returns:
    - DataFrame indexed by target_times
    """
    x_times_numeric = np.array([dt.timestamp() for dt in x_times])
    target_times_numeric = np.array([dt.timestamp() for dt in target_times])
    upsampled_data = {}

    # Detect input format
    if isinstance(data, pd.DataFrame):
        data_items = data.items()
    elif isinstance(data, dict):
        data_items = data.items()
    elif isinstance(data, (list, np.ndarray)):
        data = np.asarray(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        if labels is None:
            labels = [f"var_{i}" for i in range(data.shape[1])]
        data_items = zip(labels, data.T)
    else:
        raise TypeError("Unsupported data type for 'data'.")

    for label, x_values in data_items:
        x_values = np.asarray(x_values)

        # Support multi-dimensional variables
        if x_values.ndim == 1:
            x_values = x_values[:, np.newaxis]

        for i in range(x_values.shape[1]):
            col_label = f"{label}_{i}" if x_values.shape[1] > 1 else label
            column_data = x_values[:, i]

            # If it's datetime-like, just use target_times directly
            is_datetime = (
                np.issubdtype(column_data.dtype, np.datetime64)
                or isinstance(column_data[0], (pd.Timestamp, np.datetime64))
            )
            if is_datetime:
                upsampled_data[col_label] = target_times
                continue

            # Choose fill value
            if fill_strategy == 'nan':
                fill_value = np.nan
            elif fill_strategy == 'minscale':
                if min_value is not None:
                    fill_value = min_value
                else:
                    min_nonzero = np.nanmin(column_data[np.nonzero(column_data)])
                    fill_value = min_nonzero * 0.5
            else:
                raise ValueError("fill_strategy must be 'nan' or 'minscale'")

            # Fill array and insert values at correct indices
            filled_array = np.full(target_times_numeric.shape, fill_value, dtype=np.float64)

            for x_idx, x_time in enumerate(x_times_numeric):
                target_idx = np.argmin(np.abs(target_times_numeric - x_time))
                filled_array[target_idx] = column_data[x_idx]

            upsampled_data[col_label] = filled_array

    return pd.DataFrame(upsampled_data, index=target_times)




  

#example use
#upsampled_df = upsample_data(
    #data=df_sf01,
    #x_times=datetime_array_sf01,
    #target_times=datetime_spi_sf0a,
    #fill_strategy='minscale',
    #min_value=1e-3  # optional, can be left out
#)




def apply_nans_phi_fov(var, thresh = 163.125):
    #input variable, 
    #output variable with insufficent fov phi angle coverage indices filled as nans
    
    #Define insufficent phi angle coverage threshold
    #phi_thresh = spi_nrg_vals_phi[0,1] #163.125 degrees, 
    #note this is very conservative, one could also go up to 165 or even 168 (with care)

    #Find the boolean mask where centroids_spi_phi is greater than or equal to phi_thresh
    #Note, could instead use the maximum phi flux value, rather than weighted mean. Unsure which is better.
    mask = centroids_spi_phi >= thresh

    # Replace the corresponding indices in variable with NaNs, so they will not plot
    var = np.array(var) #convert to numpy array
    var[mask] = np.nan
    return var


def apply_nans_phi_fov_pb(var, thresh = 163.125):
    #input plotbot variable, 
    #output plotbot variable named plotbotvariable with insufficent fov phi angle coverage indices filled as nans
    
    #Define insufficent phi angle coverage threshold
    #phi_thresh = spi_nrg_vals_phi[0,1] #163.125 degrees, 
    #note this is very conservative, one could also go up to 165 or even 168 (with care)

    #Find the boolean mask where centroids_spi_phi is greater than or equal to phi_thresh
    #Note, could instead use the maximum phi flux value, rather than weighted mean. Unsure which is better.
    mask = centroids_spi_phi >= thresh

    # Replace the corresponding indices in variable with NaNs, so they will not plot
    var = np.array(var) #convert to numpy array
    var[mask] = np.nan
    return var

#define function to compute correlation coefficient between 2 variables 
#uses masked_invalid to avoid nans
def corr_nan(A,B):
    a=ma.masked_invalid(A)
    b=ma.masked_invalid(B)

    msk = (~a.mask & ~b.mask)
    corr_matrix = ma.corrcoef(a[msk],b[msk])
    corr_matrix.data
    return corr_matrix.data[0,1]
def apply_fov_filter(
    keys,
    centroid_proton=None,
    threshold_proton=None,
    centroid_alpha=None,
    threshold_alpha=None,
    suffix=True
):
    """
    Flexible filtering by centroid threshold(s). Supports proton-only, alpha-only, or both.
    Returns list of new variable keys added to zipped_data.
    """
    import numpy as np

    if isinstance(keys, str):
        keys = [keys]

    new_keys = []

    for key in keys:
        if key not in zipped_data:
            print(f"⚠️ '{key}' not in zipped_data, skipping.")
            continue

        entry = zipped_data[key]
        plot_type = entry[0]
        data_arrays = [np.asarray(arr) for arr in entry[1]]
        var_names = entry[2]
        time_array = np.asarray(entry[3])
        ylabels = entry[4]
        legends = entry[5]
        colors = entry[6]

        # Generate mask based on whichever centroids are provided
        mask = np.full_like(time_array, True, dtype=bool)
        key_suffix_parts = []
        legend_suffix_parts = []

        if centroid_proton is not None and threshold_proton is not None:
            if len(centroid_proton) != len(time_array):
                print(f"⚠️ Proton centroid length mismatch for '{key}', skipping.")
                continue
            mask &= centroid_proton <= threshold_proton
            key_suffix_parts.append(f"p_le{threshold_proton}")
            legend_suffix_parts.append(f"p ≤ {threshold_proton}°")

        if centroid_alpha is not None and threshold_alpha is not None:
            if len(centroid_alpha) != len(time_array):
                print(f"⚠️ Alpha centroid length mismatch for '{key}', skipping.")
                continue
            mask &= centroid_alpha <= threshold_alpha
            key_suffix_parts.append(f"a_le{threshold_alpha}")
            legend_suffix_parts.append(f"α ≤ {threshold_alpha}°")

        if np.all(mask == True):
            print(f"⚠️ No filtering applied to '{key}' (mask is all True).")
        elif not np.any(mask):
            print(f"⚠️ No data left after filtering '{key}', skipping.")
            continue

        filtered_data = [arr[mask] for arr in data_arrays]
        filtered_time = time_array[mask]

        # Build key and updated legends
        key_suffix = "_" + "_".join(key_suffix_parts) if suffix and key_suffix_parts else ""
        new_key = f"{key}{key_suffix}"
        legends = [f"{l} ({', '.join(legend_suffix_parts)})" for l in legends]

        # Rebuild entry based on plot type
        if plot_type == "time_series":
            zipped_data[new_key] = (
                plot_type,
                filtered_data,
                var_names,
                filtered_time,
                ylabels,
                legends,
                colors,
                entry[7], entry[8], entry[9], entry[10],
                entry[11], entry[12], entry[13], entry[14]
            )
        elif plot_type == "scatter":
            zipped_data[new_key] = (
                plot_type,
                filtered_data,
                var_names,
                filtered_time,
                ylabels,
                legends,
                colors,
                entry[7], entry[8], entry[9],
                entry[10], entry[11]
            )
        else:
            print(f"⚠️ Unsupported plot type '{plot_type}' for '{key}', skipping.")
            continue

        print(f"✅ Filtered '{key}' ➜ '{new_key}' with legend updated.")
        new_keys.append(new_key)

    return new_keys

import numpy as np
import hashlib
import json

filter_metadata = {}
_filter_counter = [1]  # Mutable counter to generate unique suffixes
_filter_lookup = {}  # Maps parameter hash to filter index


def filter_variable(
    zipped_data,
    keys,
    centroid_proton=None,
    threshold_proton=None,
    centroid_alpha=None,
    threshold_alpha=None,
    uncertainty_thresholds_proton=None,
    uncertainty_thresholds_alpha=None,
    additional_thresholds=None,  # e.g., {"np2": (">=", "2*'dens_spi'")}
    mode="proton",
    store_metadata=True
):
    if isinstance(keys, str):
        keys = [keys]

    new_keys = []

    # --- Generate a hash of the filtering criteria ---
    def sort_nested(d):
        if not d:
            return None
        return {k: d[k] if not isinstance(d[k], dict) else sort_nested(d[k]) for k in sorted(d)}

    sorted_uncertainty_proton = sort_nested(uncertainty_thresholds_proton)
    sorted_uncertainty_alpha = sort_nested(uncertainty_thresholds_alpha)
    sorted_additional = sort_nested(additional_thresholds)

    filter_params = {
        'centroid_proton': float(threshold_proton) if threshold_proton is not None else None,
        'centroid_alpha': float(threshold_alpha) if threshold_alpha is not None else None,
        'uncertainty_thresholds_proton': sorted_uncertainty_proton,
        'uncertainty_thresholds_alpha': sorted_uncertainty_alpha,
        'additional_thresholds': sorted_additional,
        'mode': mode
    }
    filter_str = json.dumps(filter_params, sort_keys=True)
    filter_hash = hashlib.md5(filter_str.encode()).hexdigest()

    # --- Reuse or assign a filter index ---
    if filter_hash in _filter_lookup:
        filter_index = _filter_lookup[filter_hash]
    else:
        filter_index = _filter_counter[0]
        _filter_counter[0] += 1
        _filter_lookup[filter_hash] = filter_index

    for key in keys:
        if key not in zipped_data:
            print(f"⚠️ '{key}' not in zipped_data, skipping.")
            continue

        entry = zipped_data[key]
        plot_type = entry[0]
        data_arrays = [np.asarray(arr) for arr in entry[1]]
        var_names = entry[2]
        time_array = np.asarray(entry[3])
        ylabels = entry[4]
        legends = entry[5]
        colors = entry[6]

        mask = np.full_like(time_array, True, dtype=bool)
        metadata = {
            'centroid_proton': None,
            'centroid_alpha': None,
            'uncertainty_thresholds_proton': None,
            'uncertainty_thresholds_alpha': None,
            'additional_thresholds': None,
            'mode': mode,
        }

        if mode in ('proton', 'both') and centroid_proton is not None and threshold_proton is not None:
            if len(centroid_proton) != len(time_array):
                print(f"⚠️ Proton centroid length mismatch for '{key}', skipping proton centroid filter.")
            else:
                mask &= centroid_proton <= threshold_proton
                metadata['centroid_proton'] = threshold_proton

        if mode in ('alpha', 'both') and centroid_alpha is not None and threshold_alpha is not None:
            if len(centroid_alpha) != len(time_array):
                print(f"⚠️ Alpha centroid length mismatch for '{key}', skipping alpha centroid filter.")
            else:
                mask &= centroid_alpha <= threshold_alpha
                metadata['centroid_alpha'] = threshold_alpha

        def apply_uncertainty_filter(thresholds_dict, particle_type):
            umask = np.full_like(time_array, True, dtype=bool)
            for param, thresh in thresholds_dict.items():
                val_key = param
                err_key = f"{param}_delta"
                if val_key not in zipped_data or err_key not in zipped_data:
                    print(f"⚠️ Missing value or uncertainty for '{param}', skipping.")
                    continue
                val_arr = np.asarray(zipped_data[val_key][1][0])
                err_arr = np.asarray(zipped_data[err_key][1][0])

                if len(val_arr) != len(time_array) or len(err_arr) != len(time_array):
                    print(f"⚠️ Length mismatch for '{param}', skipping.")
                    continue

                rel_unc = np.abs(err_arr / val_arr)
                umask &= rel_unc <= thresh
            return umask

        if mode in ('proton', 'both') and uncertainty_thresholds_proton:
            pmask = apply_uncertainty_filter(uncertainty_thresholds_proton, 'proton')
            mask &= pmask
            metadata['uncertainty_thresholds_proton'] = uncertainty_thresholds_proton

        if mode in ('alpha', 'both') and uncertainty_thresholds_alpha:
            amask = apply_uncertainty_filter(uncertainty_thresholds_alpha, 'alpha')
            mask &= amask
            metadata['uncertainty_thresholds_alpha'] = uncertainty_thresholds_alpha

        # --- Additional threshold filtering ---
        if metadata['additional_thresholds'] is None:
            metadata['additional_thresholds'] = {}
        if additional_thresholds:
            logic_mask = np.full_like(time_array, True, dtype=bool)
            for param, (op, compare_expr) in additional_thresholds.items():
                if param not in zipped_data:
                    print(f"⚠️ '{param}' not found for additional thresholding, skipping.")
                    continue

                try:
                    eval_context = {"np": np, "zipped_data": zipped_data}
                    expr = compare_expr
                    import re
                    matches = re.findall(r"'([a-zA-Z0-9_]+)'", expr)
                    def var_replacer(match):
                        varname = match.group(1)
                        if varname in zipped_data:
                            eval_context[varname] = np.asarray(zipped_data[varname][1][0])
                            return varname
                        return match.group(0)
                    expr = re.sub(r"'([a-zA-Z0-9_]+)'", var_replacer, expr)
                    result = eval(expr, eval_context)
                    compare_arr = np.asarray(result)
                    if compare_arr.ndim == 0:
                        compare_arr = np.full_like(time_array, compare_arr.item(), dtype=float)
                    param_arr = np.asarray(zipped_data[param][1][0])
                except Exception as e:
                    print(f"⚠️ Error evaluating threshold expression '{compare_expr}' for '{param}': {e}")
                    continue

                if len(compare_arr) != len(time_array) or len(param_arr) != len(time_array):
                    print(f"⚠️ Length mismatch for additional threshold '{param}', skipping.")
                    continue

                current_mask = np.full_like(time_array, True, dtype=bool)
                if op == '>=':
                    current_mask = param_arr >= compare_arr
                elif op == '<=':
                    current_mask = param_arr <= compare_arr
                elif op == '>':
                    current_mask = param_arr > compare_arr
                elif op == '<':
                    current_mask = param_arr < compare_arr
                elif op == '==':
                    current_mask = param_arr == compare_arr
                elif op == '!=': 
                    current_mask = param_arr != compare_arr
                else:
                    print(f"⚠️ Unsupported operator '{op}' for '{param}', skipping.")
                    continue

                logic_mask &= current_mask

                if metadata['additional_thresholds'] is None:
                    metadata['additional_thresholds'] = {}
                metadata['additional_thresholds'][param] = (op, compare_expr)

            mask &= logic_mask

        if not np.any(mask):
            print(f"⚠️ All data filtered out for '{key}', skipping.")
            continue

        filtered_data = [arr[mask] for arr in data_arrays]
        filtered_time = time_array[mask]

        new_key = f"{key}_filt{filter_index}"
        updated_legends = [f"{l} (filt{filter_index})" for l in legends]

        if plot_type == "time_series":
            zipped_data[new_key] = (
                plot_type, filtered_data, var_names, filtered_time, ylabels,
                updated_legends, colors,
                entry[7], entry[8], entry[9], entry[10],
                entry[11], entry[12], entry[13], entry[14]
            )
        elif plot_type == "scatter":
            zipped_data[new_key] = (
                plot_type, filtered_data, var_names, filtered_time, ylabels,
                updated_legends, colors,
                entry[7], entry[8], entry[9],
                entry[10], entry[11]
            )
        else:
            print(f"⚠️ Unsupported plot type '{plot_type}' for '{key}', skipping.")
            continue

        if store_metadata and f"filt{filter_index}" not in filter_metadata:
            filter_metadata[f"filt{filter_index}"] = metadata

        print(f"✅ Filtered '{key}' ➜ '{new_key}'")
        new_keys.append(new_key)

    return new_keys

#Replace the cell that currently holds your plotbot function with this code:

def plot_efficient_spectrogram(ax, time_data, energy_data, intensity_data, fig, 
                             cmap=None, norm=None):
    """
    Plot a spectrogram efficiently by matching data resolution to display resolution.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axis to plot on
    time_data : array-like
        Time values (x-axis)
    energy_data : array-like
        Energy values (y-axis)
    intensity_data : array-like
        2D intensity values (color)
    fig : matplotlib.figure.Figure
        The figure object (needed for resolution calculation)
    cmap : str or matplotlib.colors.Colormap, optional
        The colormap to use
    norm : matplotlib.colors.Normalize, optional
        The normalization to use
    
    Returns:
    --------
    im : matplotlib.collections.QuadMesh
        The plotted pcolormesh object
    """
    # Calculate appropriate downsample factor based on display width
    fig_width_px = fig.get_size_inches()[0] * fig.dpi
    downsample = max(1, len(time_data) // int(fig_width_px))
    
    # Downsample the data
    time_downsampled = time_data[::downsample]
    energy_downsampled = energy_data[::downsample]
    intensity_downsampled = intensity_data[::downsample]
    
    # Create the efficient pcolormesh
    im = ax.pcolormesh(time_downsampled, 
                      energy_downsampled, 
                      intensity_downsampled,
                      cmap=cmap,
                      norm=norm,
                      shading='nearest',
                      rasterized=True,
                      snap=True,
                      antialiased=False)
    
    return im


def plotbot(trange, *args):
    """
    Run "help(plotbot)" for more information!
    
    Plots multiple variables on different axes within a single figure, performing time clipping internally.
    Supports plotting on right axis when 'r' is appended to the axis number.
    Creates a single, combined legend for each subplot, including all variables.
    Positions the legend outside the plot, moving it further right for subplots with a right axis.
    Plot numbering starts at 1.
    """
    # Group variables by axis
    axis_groups = defaultdict(list)
    for i in range(0, len(args), 2):
        variable, axis_spec = args[i], args[i+1]
        axis_num, is_right = parse_axis_spec(axis_spec)
        axis_groups[(axis_num, is_right)].append(variable)

    # Determine the number of subplots needed
    num_subplots = max(axis_num for axis_num, _ in axis_groups.keys())

    # Create the figure and axes
    fig, axs = plt.subplots(num_subplots, 1, sharex=True, figsize=(12, 2*num_subplots))
    if num_subplots == 1:
        axs = [axs]

    # Adjust the subplot parameters
    plt.subplots_adjust(right=0.75)  # Adjust this value to make room for legends

    # Plot each group of variables
    for axis_index in range(1, num_subplots + 1):
        ax = axs[axis_index - 1]
        ax_right = None
        legend_handles = []
        legend_labels = []
        has_right_axis = False

        for (axis_num, is_right), variable_list in axis_groups.items():
            if axis_num != axis_index:
                continue

            if is_right and ax_right is None:
                ax_right = ax.twinx()
                has_right_axis = True

            for variable in variable_list:
                data = zipped_data.get(variable)
                if data is None:
                    print(f"No data found for variable: {variable}")
                    continue

                plot_type = data[0]

                if plot_type == 'time_series':
                    # Unpack data
                    (plot_type, variables_data, var_names, datetime_array,
                     y_axis_labels, var_legend_labels, colors_list, y_axis_scaling,
                     y_axis_limits, line_widths, line_styles, additional_data,
                     colorbar_map, colorbar_scale, colorbar_limits) = data

                    # Apply custom options if they exist
                    if variable in plotbot_manager.custom_options:
                        custom_opts = plotbot_manager.custom_options[variable]
                        plot_type = custom_opts.get('plot_type', plot_type)
                        variables_data = custom_opts.get('variables_data', variables_data)
                        var_names = custom_opts.get('var_names', var_names)
                        datetime_array = custom_opts.get('datetime_array', datetime_array)
                        y_axis_labels = custom_opts.get('y_label', y_axis_labels)
                        var_legend_labels = custom_opts.get('legend_label', var_legend_labels)
                        y_axis_limits = custom_opts.get('y_lim', y_axis_limits)
                        line_widths = custom_opts.get('line_width', line_widths)
                        line_styles = custom_opts.get('line_style', line_styles)
                        additional_data = custom_opts.get('additional_data', additional_data)
                        colorbar_map = custom_opts.get('colorbar_map', colorbar_map)
                        colorbar_scale = custom_opts.get('colorbar_scale', colorbar_scale)
                        colorbar_limits = custom_opts.get('colorbar_limits', colorbar_limits)

                    # Time clipping
                    clipped_results = apply_time_range(trange, datetime_array, *variables_data)
                    time_data_clipped = clipped_results[0]
                    variables_data_clipped = clipped_results[1:]

                    plot_ax = ax_right if is_right else ax
                    for var_data, label, color, lw, ls in zip(variables_data_clipped, var_legend_labels,
                                                              colors_list, line_widths, line_styles):
                        line, = plot_ax.plot(time_data_clipped, var_data, label=label, color=color,
                                             linewidth=lw, linestyle=ls)
                        legend_handles.append(line)
                        legend_labels.append(label)
                    ylabel = y_axis_labels[0].replace('\\n', '\n')
                    plot_ax.set_ylabel(ylabel)
                    plot_ax.set_yscale(y_axis_scaling)

                    # Apply y-axis limits
                    if y_axis_limits is not None:
                        plot_ax.set_ylim(y_axis_limits)

                elif plot_type == 'spectral':
                    # Unpack data
                    (plot_type, variables_data, var_names, datetime_array,
                     y_axis_labels, var_legend_labels, colors_list, y_axis_scaling,
                     y_axis_limits, line_widths, line_styles, additional_data,
                     colorbar_map, colorbar_scale, colorbar_limits) = data

                    # Debug prints for colorbar limits
                    print(f"Variable '{variable}' colorbar_limits before custom options: {colorbar_limits}")
                    if variable in plotbot_manager.custom_options:
                        print(f"Custom options for '{variable}': {plotbot_manager.custom_options[variable]}")

                    # Apply custom options if they exist
                    if variable in plotbot_manager.custom_options:
                        custom_opts = plotbot_manager.custom_options[variable]
                        plot_type = custom_opts.get('plot_type', plot_type)
                        variables_data = custom_opts.get('variables_data', variables_data)
                        var_names = custom_opts.get('var_names', var_names)
                        datetime_array = custom_opts.get('datetime_array', datetime_array)
                        y_axis_labels = custom_opts.get('y_label', y_axis_labels)
                        var_legend_labels = custom_opts.get('legend_label', var_legend_labels)
                        colors_list = custom_opts.get('line_color', colors_list)
                        y_axis_scaling = custom_opts.get('y_scale', y_axis_scaling)
                        y_axis_limits = custom_opts.get('y_lim', y_axis_limits)
                        line_widths = custom_opts.get('line_width', line_widths)
                        line_styles = custom_opts.get('line_style', line_styles)
                        additional_data = custom_opts.get('additional_data', additional_data)
                        colorbar_map = custom_opts.get('colorbar_map', colorbar_map)
                        colorbar_scale = custom_opts.get('colorbar_scale', colorbar_scale)
                        colorbar_limits = custom_opts.get('colorbar_limits', colorbar_limits)

                    # Time clipping
                    clipped_results = apply_time_range(trange, datetime_array, *variables_data)
                    time_data_clipped = clipped_results[0]
                    variables_data_clipped = clipped_results[1:]

                    time_indices = time_clip(datetime_array, trange[0], trange[1])
                    additional_data_clipped = additional_data[time_indices]

                    # Handle colorbar scaling
                    if colorbar_scale == 'log':
                        norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                    elif colorbar_scale == 'linear':
                        norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
                    else:
                        norm = None
                    cmap = colorbar_map if colorbar_map else None

                    
                    # im = ax.pcolormesh(time_data_clipped, additional_data_clipped, variables_data_clipped[0],
                    #                    cmap=cmap, shading='auto', norm=norm)
                    
                    im = plot_efficient_spectrogram(
                        ax=ax,
                        time_data=time_data_clipped,
                        energy_data=additional_data_clipped,
                        intensity_data=variables_data_clipped[0],
                        fig=fig,
                        cmap=cmap,
                        norm=norm
                    )

                    ylabel = y_axis_labels[0].replace('\\n', '\n')
                    ax.set_ylabel(ylabel)
                    pos = ax.get_position()
                    cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                    cbar = plt.colorbar(im, cax=cax)
                    cbar.set_label(r'Intensity')

                    # Apply y-axis limits and scaling
                    if y_axis_limits is not None:
                        ax.set_ylim(y_axis_limits)
                    ax.set_yscale(y_axis_scaling)

                elif plot_type == 'scatter':
                    # Unpack data
                    (plot_type, variables_data, var_names, datetime_array,
                     y_axis_label, var_legend_labels, colors_list, marker_styles,
                     marker_sizes, alphas, y_axis_scaling, y_axis_limits) = data

                    # Apply custom options if they exist
                    if variable in plotbot_manager.custom_options:
                        custom_opts = plotbot_manager.custom_options[variable]
                        plot_type = custom_opts.get('plot_type', plot_type)
                        variables_data = custom_opts.get('variables_data', variables_data)
                        var_names = custom_opts.get('var_names', var_names)
                        datetime_array = custom_opts.get('datetime_array', datetime_array)
                        y_axis_label = custom_opts.get('y_label', y_axis_label)
                        var_legend_labels = custom_opts.get('legend_label', var_legend_labels)
                        colors_list = custom_opts.get('line_color', colors_list)
                        marker_styles = custom_opts.get('marker_style', marker_styles)
                        marker_sizes = custom_opts.get('marker_size', marker_sizes)
                        alphas = custom_opts.get('alpha', alphas)
                        y_axis_scaling = custom_opts.get('y_scale', y_axis_scaling)
                        y_axis_limits = custom_opts.get('y_lim', y_axis_limits)

                    # Time clipping
                    clipped_results = apply_time_range(trange, datetime_array, *variables_data)
                    time_data_clipped = clipped_results[0]
                    variables_data_clipped = clipped_results[1:]

                    plot_ax = ax_right if is_right else ax
                    for var_data, label, color, marker_style, marker_size, alpha in zip(
                            variables_data_clipped, var_legend_labels, colors_list,
                            marker_styles, marker_sizes, alphas):
                        sc = plot_ax.scatter(time_data_clipped, var_data, label=label, color=color,
                                             marker=marker_style, s=marker_size, alpha=alpha)
                        legend_handles.append(sc)
                        legend_labels.append(label)
                    plot_ax.set_ylabel(y_axis_label)
                    plot_ax.set_yscale(y_axis_scaling)
                    if y_axis_limits is not None:
                        plot_ax.set_ylim(y_axis_limits)

                else:
                    print(f"Unknown plot type: {plot_type}")
                    continue

        # Create a single legend for the subplot
        if legend_handles:
            if has_right_axis:
                leg = ax.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1.095, 0.5))
                for lh in legend_handles: 
                    lh.set_alpha(1)
            else:
                leg = ax.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1.02, 0.5))
             #   for lh in leg.legend_handles: 
                for lh in legend_handles: 
                    lh.set_alpha(1)

        # Remove extra space on x-axis
        ax.margins(x=0)
        if ax_right:
            ax_right.margins(x=0)

    # Set common x-label
    axs[-1].set_xlabel('Time')
    plt.show()
# Define the midpoint for the colormap with log normalization
class MidpointLogNormalize(colors.LogNorm):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        super().__init__(vmin, vmax, clip)

    def __call__(self, value, clip=None):
        if self.midpoint is None:
            return super().__call__(value, clip)
        log_vmin = np.log10(self.vmin)
        log_vmax = np.log10(self.vmax)
        log_midpoint = np.log10(self.midpoint)
        x, y = [log_vmin, log_midpoint, log_vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(np.log10(value), x, y))
    
# Define the midpoint for the colormap
class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        super().__init__(vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

# Create a colorbar with the center around 1
#norm = MidpointNormalize(vmin=0, vmax=2, midpoint=1)

# Create a colorbar with the center around 1 using log normalization
#norm = MidpointLogNormalize(vmin=0.1, vmax=100, midpoint=1)

def showdahodo(trange, var1, var2, color_var=None, norm_ = None, xlim_ = None, ylim_ = None, 
               fname = None, s_ = None, alpha_ = None, xlabel_ = None, ylabel_ = None, 
               clabel_ = None, xlog_ = None, ylog_ = None, cmap_ = None, sort = None, 
               invsort = None, lumsort = None, brazil = None, corr = None, wvpow = None, 
               rsun = None, noshow = None, face_c = None, face_a = None, identity_line = None):
    """
    Run "help(showdahodo)" for more information!

    Create a hodogram plot of two variables, optionally colored by a third variable.
    Also calculates and displays the correlation coefficient and plots a trend line.

    """

    def check_lengths(name, original_len, clipped_len, resampled_len=None, resampling_done=False):
        
        # print(f"{name} original length: {original_len}")
        # print(f"{name} length after time clipping: {clipped_len}")
        # if resampled_len is not None:
        #     print(f"{name} length after resampling: {resampled_len}")
        #     if resampling_done:
        #         print(f"{name} resampling successful!")
        #     else:
        #         print(f"{name} resampling not needed.")
        # print()  # For better readability
        
        pass

    # Get data for var1 and var2
    data1 = zipped_data[var1]
    data2 = zipped_data[var2]

    # Extract data and time arrays
    values1_full = np.array(data1[1][0])  # Data array is now at index 1
    time1_full = np.array(data1[3])       # Time array is now at index 3
    values2_full = np.array(data2[1][0])  # Data array is now at index 1
    time2_full = np.array(data2[3])       # Time array is now at index 3

    if wvpow is not None:
        color1_time_full = datetime_wvpow
        color2_time_full = datetime_wvpow
        color1_values_full = wvpow_LH_spi
        color2_values_full = wvpow_RH_spi


    # Save original lengths
    time1_original_len = len(time1_full)
    time2_original_len = len(time2_full)

    # Apply time range using apply_time_range
    time1_clipped, values1_clipped = apply_time_range(trange, time1_full, values1_full)
    time2_clipped, values2_clipped = apply_time_range(trange, time2_full, values2_full)

    time1_clipped_len = len(time1_clipped)
    time2_clipped_len = len(time2_clipped)
    # Prepare color data
    if color_var is not None:
        if color_var == 'wvpow':
            color1_time_full = datetime_wvpow
            color2_time_full = datetime_wvpow
            color1_values_full = wvpow_LH_spi
            color2_values_full = wvpow_RH_spi
            color1_time_original_len = len(color1_time_full)
            color2_time_original_len = len(color2_time_full)
            # Apply time range
            color1_time_clipped, color1_values_clipped = apply_time_range(trange, color1_time_full, color1_values_full)
            color1_time_clipped_len = len(color1_time_clipped)
            # Apply time range
            color2_time_clipped, color2_values_clipped = apply_time_range(trange, color2_time_full, color2_values_full)
            color2_time_clipped_len = len(color2_time_clipped)
        else:
            color_data = zipped_data[color_var]
            color_values_full = np.array(color_data[1][0])  # Data array is now at index 1
            color_time_full = np.array(color_data[3])       # Time array is now at index 3
            color_time_original_len = len(color_time_full)

            # Apply time range
            color_time_clipped, color_values_clipped = apply_time_range(trange, color_time_full, color_values_full)
            color_time_clipped_len = len(color_time_clipped)
    else:
        color_time_clipped = None
        color_values_clipped = None
        color_time_original_len = 0
        color_time_clipped_len = 0

    # Determine which time series has the lowest sampling rate
    # We'll use the one with the fewest data points as target_times
    lengths = {
        'time1': time1_clipped_len,
        'time2': time2_clipped_len,
        'color_time': color_time_clipped_len if color_time_clipped is not None else float('inf')
    }    
    min_length = min(lengths.values())
    if lengths['time1'] == min_length:
        target_times = time1_clipped
    elif lengths['time2'] == min_length:
        target_times = time2_clipped
    else:
        target_times = color_time_clipped

    # Check if time arrays are equal
    time_arrays_equal = np.array_equal(time1_clipped, target_times) and np.array_equal(time2_clipped, target_times)
    if color_var is not None and color_time_clipped is not None:
        time_arrays_equal = time_arrays_equal and np.array_equal(color_time_clipped, target_times)

    # Decide whether resampling is needed
    if time_arrays_equal:
        # No resampling needed
        values1 = values1_clipped
        values2 = values2_clipped
        if color_var is not None:
            color_values = color_values_clipped
        else:
            color_values = None

        # Use clipped lengths as resampled lengths
        resampled_len = len(target_times)
        check_lengths('values1', time1_original_len, time1_clipped_len, resampled_len, resampling_done=False)
        check_lengths('values2', time2_original_len, time2_clipped_len, resampled_len, resampling_done=False)
        if color_var is not None:
            check_lengths('color_values', color_time_original_len, color_time_clipped_len, resampled_len, resampling_done=False)
    else:
        # Resampling is needed
        if not np.array_equal(time1_clipped, target_times):
            #values1 = downsample_time_based(time1_clipped, values1_clipped, target_times) #this is for downsampling via interpolation
            #values1 = downsample_to_match(time1_clipped, values1_clipped, target_times)
            values1 = downsample_to_min_ind(time1_clipped, values1_clipped, target_times)
            resampling_done1 = True
        else:
            values1 = values1_clipped
            resampling_done1 = False

        if not np.array_equal(time2_clipped, target_times):
            #values2 = downsample_time_based(time2_clipped, values2_clipped, target_times)
            #values2 = downsample_to_match(time2_clipped, values2_clipped, target_times)
            values2 = downsample_to_min_ind(time2_clipped, values2_clipped, target_times)

            resampling_done2 = True
        else:
            values2 = values2_clipped
            resampling_done2 = False

        if color_var is not None and color_time_clipped is not None:
            if not np.array_equal(color_time_clipped, target_times):
                #color_values = downsample_time_based(color_time_clipped, color_values_clipped, target_times)
                #color_values = downsample_to_match(color_time_clipped, color_values_clipped, target_times)
                color_values = downsample_to_min_ind(color_time_clipped, color_values_clipped, target_times)                
                resampling_done_color = True
            else:
                color_values = color_values_clipped
                resampling_done_color = False
        else:
            color_values = None
            resampling_done_color = False

        # Use resampled lengths
        resampled_len = len(target_times)
        check_lengths('values1', time1_original_len, time1_clipped_len, resampled_len, resampling_done=resampling_done1)
        check_lengths('values2', time2_original_len, time2_clipped_len, resampled_len, resampling_done=resampling_done2)
        if color_var is not None:
            check_lengths('color_values', color_time_original_len, color_time_clipped_len, resampled_len, resampling_done=resampling_done_color)

    # Prepare colors
    if color_var is None:
        colors = mdates.date2num(target_times) - mdates.date2num(target_times[0])
        color_label = 'Time'
    else:
        colors = color_values
        if clabel_ is not None:
            color_label = clabel_
        else:
            color_label = color_data[5][0] if color_data[0] != 'scatter' else color_data[5]  # legend label for color variable

    # Create the plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    if s_ is not None:
        s_ = s_
    else:
        s_ = 20
        
    if alpha_ is not None:
        alpha_ = alpha_
    else:
        alpha_ = .7
    if norm_ is not None:
        norm_ = norm_
    else:
        norm_ = Normalize()
    if cmap_ is not None:
        cmap_ = cmap_
    else:
        cmap_ = 'plasma'
        
    if sort is not None:
    #sort color by ascending order so highest color value plotted last
        sort_c = np.argsort(colors)
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
        
    if invsort is not None:
    #sort color by descending order so lowest color value plotted last
        sort_c = np.argsort(colors)[::-1]
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
    
    if lumsort is not None:
        #sort color by plotting lightest color last
        # Get the colormap instance
        colormap = get_cmap(cmap_)
        # Calculate RGB values for each data point
        colors_rbg = colormap(norm(colors))
        # Calculate luminance (relative brightness) of each color
        luminance = 0.2126 * colors_rbg[:, 0] + 0.7152 * colors_rbg[:, 1] + 0.0722 * colors_rbg[:, 2]
        # Sort data by luminance
        sort_c = np.argsort(luminance)  # Darker colors first, lighter colors last
        sort_c = np.argsort(colors)[::-1]
        values1 = values1[sort_c]
        values2 = values2[sort_c]
        colors = colors[sort_c]
        colors = np.log10(colors)
    if face_c is not None:
        ax.patch.set_facecolor(face_c)
    if face_a is not None:
        ax.patch.set_alpha(face_a)
    
    scatter = plt.scatter(values1, values2, c=colors, cmap=cmap_, norm=norm_, s=s_, alpha = alpha_)
    cbar = plt.colorbar(scatter, label=color_label)
    cbar.solids.set(alpha=1)
    
    corr_title = ''
    if corr is not None:
        if ((xlog_ is not None) and (ylog_ is not None)) or brazil is not None:
            #Calculate correlation coefficient
           # correlation_coefficient, p_value = stats.pearsonr(np.log10(values1), np.log10(values2))
            # Calculate trend line
           # z = np.polyfit(np.log10(values1), np.log10(values2), 1)
           # p = np.poly1d(z)
           # plt.plot(np.log10(values1), p(np.log10(values1)), ".k", alpha=0.5)  # Add trend line
            coeff = corr_nan(np.log10(values1),np.log10(values2))
            corr_title = f'Corr Coeff: {coeff:.2f}, '
            #plt.title(f'log({var1}) vs log({var2})\nCorrelation Coefficient: {coeff:.2f}')
        else:
            # Calculate correlation coefficient
            correlation_coefficient, p_value = stats.pearsonr(values1, values2)
            # Calculate trend line
            z = np.polyfit(values1, values2, 1)
            p = np.poly1d(z)
            plt.plot(values1, p(values1), ".k", alpha=0.5)  # Add trend line
            corr_title = f'Corr Coef: {correlation_coefficient:.2f}, '
            #plt.title(f'{var1} vs {var2}\nCorrelation Coefficient: {correlation_coefficient:.2f}')

    if color_var is None:
        # Convert colorbar ticks to datetime
        cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(
            lambda x, p: (target_times[0] + timedelta(days=x)).strftime('%Y-%m-%d/%H:%M:%S')
        ))
    
    if xlabel_ is not None:
        xlabel = xlabel_
    else:
         # Set axis labels based on plot type
         # data[4] = yaxis title, data[5] = legend
        xlabel = data1[5][0] if data1[0] != 'scatter' else data1[5]
    if ylabel_ is not None:
        ylabel = ylabel_
    else:
        ylabel = data2[5][0] if data2[0] != 'scatter' else data2[5]

    plt.xlabel(xlabel, fontsize = 16)
    plt.ylabel(ylabel, fontsize = 16)
    
    if xlim_ is not None:
        xlim = xlim_
        plt.xlim(xlim)
    if ylim_ is not None:
        ylim = ylim_
        plt.ylim(ylim)
        
    if brazil is not None:
    #add instability threshold curves and plot on loglog scale
        #step =  np.nanmin(values1_clipped)
        beta_par       = np.arange(0, 1000, 1e-4)
        trat_parfire = 1-(.47/(beta_par - .59)**.53)
        trat_oblfire = 1-(1.4/(beta_par + .11))
        trat_protcyc = 1+(.43/(beta_par + .0004)**.42)
        trat_mirror = 1+(.77/(beta_par + .016)**.76)
        plt.plot(beta_par,trat_parfire,color='black',linestyle='dashed')
        plt.plot(beta_par,trat_oblfire,color='grey',linestyle='dashed')
        plt.plot(beta_par,trat_protcyc,color='black',linestyle='dotted')
        plt.plot(beta_par,trat_mirror,color='grey',linestyle='dotted')
        plt.loglog()
        
    if xlog_ is not None:
        plt.xscale('log')
    if ylog_ is not None:
        plt.yscale('log')
        
    
    if identity_line is not None:
        ax.axline((0, 0), slope=1, c = 'black', linestyle = '--')
    
    tname=f"{trange[0]}" + ' - ' + f"{trange[-1]}"
    
    rsun_title = ''
    if rsun is not None:
        dist_time_clipped, dist_values_clipped = apply_time_range(trange, datetime_spi, sun_dist_rsun)    
        sun_dist_rsun_clipped_avg = np.round(np.average(dist_values_clipped),1)
        rsun_title = f"Rs = {sun_dist_rsun_clipped_avg}, "
       # plt.title(f"Rs = {sun_dist_rsun_clipped_avg},  " +  tname)
    #plt.title(f'Hodogram: {var1} vs {var2}\nCorrelation Coefficient: {correlation_coefficient:.2f}')
    #plt.grid(True)
    
    plt.title(rsun_title + corr_title + tname, fontsize = 12)
    
    if fname is not None:
        plt.savefig(f"{fname}_brazil.png", bbox_inches='tight')
    
    if noshow is None:
        plt.show()
        
    



def showdahodo_brazil_wvpow(trange, xlim_ = None, ylim_ = None, fname = None, s_ = None, alpha_ = None, 
                            vmin_ = None, vmax_ = None, rsun = None, sort = None, invsort = None, norm_ = None):

    time1_full = datetime_spi
    values1_full = beta_ppar_spi
    time2_full = datetime_spi
    values2_full = Anisotropy
    color1_time_full = datetime_spi
    color2_time_full = datetime_spi
    color1_values_full = wvpow_LH_spi
    color2_values_full = wvpow_RH_spi

    # Apply time range using apply_time_range
    time1_clipped, values1_clipped = apply_time_range(trange, time1_full, values1_full)
    time2_clipped, values2_clipped = apply_time_range(trange, time2_full, values2_full)
    color1_time_clipped, color1_values_clipped = apply_time_range(trange, color1_time_full, color1_values_full)
    color2_time_clipped, color2_values_clipped = apply_time_range(trange, color2_time_full, color2_values_full)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ytitle = r'Proton $T_\perp/T_\parallel$'
    xtitle = r'Proton $\beta_\parallel$'
    ctitle1 = 'Log(LH Wave Pow)'
    ctitle2 = 'Log(RH Wave Pow)'
    
    if s_ is not None:
        s_ = s_
    else:
        s_ = 20
        
    if alpha_ is not None:
        alpha_ = alpha_
    else:
        alpha_ = .7
        
    if sort is not None:
    #sort color by ascending order so highest color value plotted last
        sort_c1 = np.argsort(color1_values_clipped)
        values1_clipped_c1 = values1_clipped[sort_c1]
        values2_clipped_c1 = values2_clipped[sort_c1]
        color1_values_clipped = color1_values_clipped[sort_c1]
        sort_c2 = np.argsort(color2_values_clipped)
        values1_clipped_c2 = values1_clipped[sort_c2]
        values2_clipped_c2 = values2_clipped[sort_c2]
        color2_values_clipped = color2_values_clipped[sort_c2]
    else:
        values1_clipped_c1 = values1_clipped
        values2_clipped_c1 = values2_clipped
        values1_clipped_c2 = values1_clipped
        values2_clipped_c2 = values2_clipped


    if invsort is not None:
    #sort color by descending order so lowest color value plotted last
        sort_c1 = np.argsort(color1_values_clipped)[::-1]
        values1_clipped_c1 = values1_clipped[sort_c1]
        values2_clipped_c1 = values2_clipped[sort_c1]
        color1_values_clipped = color1_values_clipped[sort_c1]
        sort_c2 = np.argsort(color2_values_clipped)[::-1]
        values1_clipped_c2 = values1_clipped[sort_c2]
        values2_clipped_c2 = values2_clipped[sort_c2]
        color2_values_clipped = color2_values_clipped[sort_c2]
    else:
        values1_clipped_c1 = values1_clipped
        values2_clipped_c1 = values2_clipped
        values1_clipped_c2 = values1_clipped
        values2_clipped_c2 = values2_clipped
    if norm_ is not None:
        norm_ = norm_
    else:
        norm_ = colors.LogNorm()

    if vmin_ is not None:
        s1=plt.scatter(values1_clipped_c1, values2_clipped_c1, c = color1_values_clipped, cmap='Blues_r', s=s_, alpha=alpha_, vmin = vmin_, vmax = vmax_, norm = norm_)
        s2=plt.scatter(values1_clipped_c2, values2_clipped_c2, c = color2_values_clipped, cmap='Reds_r', s=s_, alpha=alpha_, vmin = vmin_, vmax = vmax_, norm = norm_)
    else:
        s1=plt.scatter(values1_clipped_c1, values2_clipped_c1, c = color1_values_clipped, cmap='Blues', s=s_, alpha=alpha_, norm = norm_)
        s2=plt.scatter(values1_clipped_c2, values2_clipped_c2, c = color2_values_clipped, cmap='Reds', s=s_, alpha=alpha_, norm = norm_)
        
    if xlim_ is not None:
        plt.xlim(xlim_)
    if ylim_ is not None:
        plt.ylim(ylim_)
        
        
    plt.ylabel(ytitle, fontsize = 16)
    plt.xlabel(xtitle, fontsize = 16)
    plt.loglog()

    ax.patch.set_facecolor('mediumspringgreen')
    ax.patch.set_alpha(0.3)

    cbar1 = plt.colorbar(s1)
    cbar1.set_label(ctitle1)
    cbar2 = plt.colorbar(s2)
    cbar2.set_label(ctitle2)
    cbar1.solids.set(alpha=1)
    cbar2.solids.set(alpha=1)

    fig.set_size_inches(15, 10)
    
    tname=f"{trange[0]}" + ' - ' + f"{trange[-1]}"
    rsun_title = ''
    if rsun is not None:
        dist_time_clipped, dist_values_clipped = apply_time_range(trange, datetime_spi, sun_dist_rsun)    
        sun_dist_rsun_clipped_avg = np.round(np.average(dist_values_clipped),1)
        rsun_title = f"Rs = {sun_dist_rsun_clipped_avg}, "
    

    plt.title(rsun_title + tname, fontsize = 12)
    
    #step =  min(values1_clipped)    
    beta_par       = np.arange(0, 1000, 1e-4)
    trat_parfire = 1-(.47/(beta_par - .59)**.53)
    trat_oblfire = 1-(1.4/(beta_par + .11))
    trat_protcyc = 1+(.43/(beta_par + .0004)**.42)
    trat_mirror = 1+(.77/(beta_par + .016)**.76)
    plt.rcParams.update({'font.size': 16})
    plt.plot(beta_par,trat_parfire,color='black',linestyle='dashed')
    plt.plot(beta_par,trat_oblfire,color='grey',linestyle='dashed')
    plt.plot(beta_par,trat_protcyc,color='black',linestyle='dotted')
    plt.plot(beta_par,trat_mirror,color='grey',linestyle='dotted')
    
    if fname is not None:
        plt.savefig(f"{fname}_brazil_wvpow.png", bbox_inches='tight')

    plt.show()
def unix2datetime(ut_arr) : 
    """Convert 1D array of unix timestamps (float) to `datetime.datetime`"""
    return np.array([datetime.utcfromtimestamp(ut) for ut in ut_arr])

def lista_hista(times, tau, plot = None):
    #input array of datetimes for histagram and 
    #temporal bin size tau in s
    
    times_numeric = np.array([dt.timestamp() for dt in times])
    tlen = times_numeric[-1] - times_numeric[0] #total length of time in s
    nbins = round(tlen/tau) 
    c, b, f = plt.hist(times, bins=nbins, histtype='step')

    # Calculate bin centers
    bin_centers = b[:-1] + np.diff(b) / 2

    # Convert bin centers to datetime objects using num2date
    bin_centers_datetime = [num2date(center) for center in bin_centers]
    bin_centers_datetime = np.asarray(bin_centers_datetime)
    if plot is not None:
        # Plot the histogram using plt.plot
        plt.plot(bin_centers_datetime, c)
        plt.xlabel('Time')
        plt.ylabel('Counts')
        plt.title('Histogram of Datetimes')
        plt.show()
    
    return c, bin_centers_datetime


# Assuming `hardham_datetime` is an array of datetime objects
# First, use plt.hist to get counts and bins
def lista_hista2d(times, vals, tau, density = None, cmax = None, range = None, cmap = None):
    #input array of datetimes for histagram and 
    #temporal bin size tau in s
    #h_RH,bx,by, f = ax.hist2d(wvpow_times, np.log10(wvpow_RH),density=True, cmax=1e-3,bins=300, range = [[wvpow_times[0],wvpow_times[-1]],[-3,2]],cmap='Reds')
    if density is not None:
        density = density
    if cmax is not None:
        cmax = cmax
    if range is not None:
        range = range
    if cmap is not None:
        cmap = cmap
    
    times_numeric = np.array([dt.timestamp() for dt in times])
    tlen = times_numeric[-1] - times_numeric[0] #total length of time in s
    nbins = round(tlen/tau) 
    h, bx , by, f = plt.hist2d(times_numeric, vals, bins = nbins,
                              density = density, cmax = cmax, range = range, cmap = cmap)

    # Calculate bin centers
    bin_centers_times = bx[:-1] + np.diff(bx) / 2

    # Convert bin centers to datetime objects using num2date
    bin_centers_datetime = unix2datetime(bin_centers_times)
    bin_centers_datetime = np.asarray(bin_centers_datetime)
    bin_centers_datetime_utc = np.array([dt.replace(tzinfo=timezone.utc) for dt in bin_centers_datetime])

    bin_centers_vals = by[:-1] + np.diff(by) / 2

    #if plot is not None:
     #   plt.pcolormesh(bin_centers_datetime_utc, bin_centers_vals , h.T, cmap = cmap)
    
    return h.T, bin_centers_datetime_utc, bin_centers_vals 



def read_pickle(fname):
    with open(f'{fname}.pkl', 'rb') as handle:
        x = pickle.load(handle)
    return x

#Proton temperature anisotropy from Temperature Tensor
def find_Tanisotropy(T_XX,T_YY,T_ZZ,T_XY,T_XZ,T_YZ):
    #Access tensor elements -- The temperature is an array of 9 elements. We want to find out how much temp is aligned parallel or perp to the mag field.
    T_YX = T_XY
    T_ZX = T_XZ
    T_ZY = T_YZ

    #Access magnetic field in span-I coordinates
    B_spi = get_data('psp_spi_sf00_MAGF_INST')
    B_X = B_spi.y[:,0]
    B_Y = B_spi.y[:,1]
    B_Z = B_spi.y[:,2]
    B_mag_XYZ = np.sqrt(B_X**2 + B_Y**2 + B_Z**2)

    #Project Tensor onto B field, find perpendicular and parallel components
    T_parallel=[]
    T_perpendicular=[]
    Anisotropy=[]
    for hamepoch_idx in range(len(T_XX)):  #Calculates Tperp and Tpar from the projection of the magnetic field vector
        i = np.argmin(np.abs(spi_epoch - hardham_list[hamepoch_idx]))
        Sum_1=B_X[i]*B_X[i]*T_XX[hamepoch_idx]
        Sum_2=B_X[i]*B_Y[i]*T_XY[hamepoch_idx]
        Sum_3=B_X[i]*B_Z[i]*T_XZ[hamepoch_idx]
        Sum_4=B_Y[i]*B_X[i]*T_YX[hamepoch_idx]
        Sum_5=B_Y[i]*B_Y[i]*T_YY[hamepoch_idx]
        Sum_6=B_Y[i]*B_Z[i]*T_YZ[hamepoch_idx]
        Sum_7=B_Z[i]*B_X[i]*T_ZX[hamepoch_idx]
        Sum_8=B_Z[i]*B_Y[i]*T_ZY[hamepoch_idx]
        Sum_9=B_Z[i]*B_Z[i]*T_ZZ[hamepoch_idx]    
        T_para=((Sum_1+Sum_2+Sum_3+Sum_4+Sum_5+Sum_6+Sum_7+Sum_8+Sum_9)/(B_mag_XYZ[i])**2)
        Trace_Temp=(T_XX[hamepoch_idx]+T_YY[hamepoch_idx]+T_ZZ[hamepoch_idx])
        T_perp=(Trace_Temp-T_para)/2.0
        T_parallel.append((Sum_1+Sum_2+Sum_3+Sum_4+Sum_5+Sum_6+Sum_7+Sum_8+Sum_9)/(B_mag_XYZ[i])**2)
        T_perpendicular.append(T_perp)
        Anisotropy.append(T_perp/T_para)

    return np.array(T_perpendicular), np.array(T_parallel), np.array(Anisotropy)