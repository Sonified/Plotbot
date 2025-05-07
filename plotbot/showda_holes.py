import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as dateutil_parse
import sys # For __main__ block mocking

# Assuming these can be imported from the plotbot package
from .data_cubby import data_cubby
from .get_data import get_data
from .print_manager import print_manager as global_pm
from .get_encounter import get_encounter_number

# Placeholder for print_manager if it's not readily available as a module import
# This is a common pattern if print_manager is instantiated elsewhere.
# For a self-contained module, you might pass it as an argument or instantiate it.
class FallbackPrintManager:
    def status(self, msg):
        print(f"STATUS: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")
    def warning(self, msg):
        print(f"WARNING: {msg}")
    def debug(self, msg):
        print(f"DEBUG: {msg}")

def _parse_marker_file(filepath: str, pm):
    """
    Parses a magnetic hole marker file to extract hole time intervals.

    Args:
        filepath (str): The path to the marker file.
        pm: An instance of PrintManager (or a compatible logger).

    Returns:
        list: A list of (hole_start_datetime, hole_end_datetime) tuples (UTC).
              Returns None if parsing fails.
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        pm.debug(f"_parse_marker_file: Successfully opened {filepath}")
    except FileNotFoundError:
        pm.error(f"_parse_marker_file: Marker file not found: {filepath}")
        return None

    metadata = {}
    hole_sample_indices = []

    # Regex patterns for parsing
    meta_pattern = re.compile(r"\[Metadata/(?P<key>[^\]]+)\]\s+\d+\s+(?P<value>.+)")
    mh_pattern = re.compile(r"MH\s+(?P<start>\d+)\s+(?P<end>\d+)")

    for line in lines:
        line = line.strip()
        meta_match = meta_pattern.match(line)
        if meta_match:
            key = meta_match.group('key')
            value_str = meta_match.group('value')
            pm.debug(f"_parse_marker_file: Matched metadata line. Key: '{key}', Raw Value: '{value_str}'")
            if key == 'trange':
                try:
                    date_strings = re.findall(r"\'(.*?)\'", value_str)
                    pm.debug(f"_parse_marker_file: Extracted date_strings for trange: {date_strings}")
                    if len(date_strings) == 2:
                         metadata[key] = [dateutil_parse(ds).replace(tzinfo=timezone.utc) for ds in date_strings]
                         pm.debug(f"_parse_marker_file: Parsed trange: {metadata[key]}")
                    else:
                        pm.warning(f"_parse_marker_file: Could not parse trange from metadata value: {value_str} - incorrect number of date strings.")
                        metadata[key] = None
                except Exception as e:
                    pm.warning(f"_parse_marker_file: Error parsing trange value '{value_str}': {e}")
                    metadata[key] = None
            elif key == 'InstrSR':
                try:
                    sr_match = re.search(r"(\d+\.?\d*)", value_str)
                    if sr_match:
                        metadata[key] = float(sr_match.group(1))
                        pm.debug(f"_parse_marker_file: Parsed InstrSR: {metadata[key]}")
                    else:
                        pm.warning(f"_parse_marker_file: Could not parse InstrSR from metadata value: {value_str} - float not found.")
                        metadata[key] = None
                except ValueError as e:
                    pm.warning(f"_parse_marker_file: Error parsing InstrSR value '{value_str}' as float: {e}")
                    metadata[key] = None
            else:
                metadata[key] = value_str.strip()
            continue

        mh_match = mh_pattern.match(line)
        if mh_match:
            start_idx = int(mh_match.group('start'))
            end_idx = int(mh_match.group('end'))
            hole_sample_indices.append((start_idx, end_idx))

    if 'trange' not in metadata or metadata['trange'] is None:
        pm.error("_parse_marker_file: Critical - 'trange' not in metadata or is None after parsing attempts.")
        return None
    if 'InstrSR' not in metadata or metadata['InstrSR'] is None:
        pm.error("_parse_marker_file: Critical - 'InstrSR' not in metadata or is None after parsing attempts.")
        return None

    file_start_time = metadata['trange'][0]
    sampling_rate = metadata['InstrSR']

    if sampling_rate <= 0:
        pm.error(f"_parse_marker_file: Invalid sampling rate in marker file: {sampling_rate}. Cannot be zero or negative.")
        return None

    time_per_sample_seconds = 1.0 / sampling_rate
    hole_datetime_intervals = []

    for start_idx, end_idx in hole_sample_indices:
        start_offset = timedelta(seconds=start_idx * time_per_sample_seconds)
        end_offset = timedelta(seconds=end_idx * time_per_sample_seconds)
        
        hole_start_dt = file_start_time + start_offset
        hole_end_dt = file_start_time + end_offset
        hole_datetime_intervals.append((hole_start_dt, hole_end_dt))
        
    pm.status(f"Parsed {len(hole_datetime_intervals)} hole intervals from {filepath}")
    return hole_datetime_intervals

# -----------------------------------------------------------
# Internal Helper for Plotting ONE Panel
# -----------------------------------------------------------
def _plot_single_hodogram_panel(
    ax,  # The axes object to plot onto
    trange_plot: list,
    x_data_req,
    y_data_req,
    marker_filepath: str,
    pm, # Pass print_manager instance
    # Optional kwargs for customization, get with defaults
    title: str = "Hodogram Panel", # Default title for a panel
    x_label: str = None, 
    y_label: str = None, 
    inside_color: str = 'red', 
    outside_color: str = 'blue',
    inside_size: int = 50,
    outside_size: int = 10,
    alpha: float = 0.7,
    base_fontsize: int = 12
):
    """
    Internal helper to generate the hodogram scatter plot for a single panel.
    Plots onto the provided 'ax'. Returns True on success, False on failure.
    """
    pm.status(f"Panel: Plotting {x_data_req.class_name}.{x_data_req.subclass_name} vs {y_data_req.class_name}.{y_data_req.subclass_name}")
    
    # 1. Parse trange_plot (redundant check, already done in caller, but safe)
    try:
        plot_start_time = dateutil_parse(trange_plot[0]).replace(tzinfo=timezone.utc)
        plot_end_time = dateutil_parse(trange_plot[1]).replace(tzinfo=timezone.utc)
        if plot_start_time >= plot_end_time:
            pm.error("Panel: Plot start time must be before end time.")
            return False
    except Exception as e:
        pm.error(f"Panel: Could not parse trange_plot: {trange_plot}. Error: {e}")
        return False

    # 2. Load Marker Data
    hole_intervals = _parse_marker_file(marker_filepath, pm)
    if not hole_intervals:
        pm.error(f"Panel: Failed for marker file {marker_filepath}")
        return False # Error already printed by _parse_marker_file

    # 3. Load X and Y Data using get_data (or assume pre-loaded)
    required_data_objects = []
    # Basic check if data seems missing, might need refinement based on how objects work
    if not hasattr(x_data_req, 'datetime_array') or x_data_req.datetime_array is None:
         required_data_objects.append(x_data_req)
    if not hasattr(y_data_req, 'datetime_array') or y_data_req.datetime_array is None:
         required_data_objects.append(y_data_req)
    
    if required_data_objects:
        pm.status(f"Panel: Calling get_data for needed variables.")
        # Using the globally imported get_data
        get_data(trange_plot, *required_data_objects)
        
    # Retrieve from data_cubby
    x_class_instance = data_cubby.grab(x_data_req.class_name)
    y_class_instance = data_cubby.grab(y_data_req.class_name)
    
    if not x_class_instance or not y_class_instance:
         pm.error("Panel: Failed to retrieve class instances from data_cubby.")
         return False
        
    x_data_obj = x_class_instance.get_subclass(x_data_req.subclass_name)
    y_data_obj = y_class_instance.get_subclass(y_data_req.subclass_name)
    
    # --- Data Validation (Using .data attribute) --- 
    if x_data_obj is None: pm.error(f"Panel: Failed X subclass {x_data_req.subclass_name}."); return False
    if not hasattr(x_data_obj, 'datetime_array') or x_data_obj.datetime_array is None: pm.error(f"Panel: X {x_data_req.subclass_name} missing dt_array."); return False
    try:
        if len(x_data_obj.datetime_array) == 0: pm.error(f"Panel: X {x_data_req.subclass_name} empty dt_array."); return False
    except TypeError: pm.error(f"Panel: X {x_data_req.subclass_name} dt_array bad type."); return False
    if not hasattr(x_data_obj, 'data') or x_data_obj.data is None: pm.error(f"Panel: X {x_data_req.subclass_name} missing data."); return False
    try:
        if np.asarray(x_data_obj.data).size == 0: pm.error(f"Panel: X {x_data_req.subclass_name} empty data."); return False
    except Exception as e: pm.error(f"Panel: X {x_data_req.subclass_name} data problematic: {e}"); return False

    if y_data_obj is None: pm.error(f"Panel: Failed Y subclass {y_data_req.subclass_name}."); return False
    if not hasattr(y_data_obj, 'datetime_array') or y_data_obj.datetime_array is None: pm.error(f"Panel: Y {y_data_req.subclass_name} missing dt_array."); return False
    try:
        if len(y_data_obj.datetime_array) == 0: pm.error(f"Panel: Y {y_data_req.subclass_name} empty dt_array."); return False
    except TypeError: pm.error(f"Panel: Y {y_data_req.subclass_name} dt_array bad type."); return False
    if not hasattr(y_data_obj, 'data') or y_data_obj.data is None: pm.error(f"Panel: Y {y_data_req.subclass_name} missing data."); return False
    try:
        if np.asarray(y_data_obj.data).size == 0: pm.error(f"Panel: Y {y_data_req.subclass_name} empty data."); return False
    except Exception as e: pm.error(f"Panel: Y {y_data_req.subclass_name} data problematic: {e}"); return False
    # --- End Validation --- 
    
    x_values = np.array(x_data_obj.data)
    y_values = np.array(y_data_obj.data)
    x_dt_index = pd.to_datetime(x_data_obj.datetime_array, utc=True)
    y_dt_index = pd.to_datetime(y_data_obj.datetime_array, utc=True)

    # 4. Prepare Data for Resampling
    try:
        x_series = pd.Series(data=x_values, index=x_dt_index, name='x')
        y_series = pd.Series(data=y_values, index=y_dt_index, name='y')
    except Exception as e:
        pm.error(f"Panel: Error creating pandas Series: {e}")
        return False

    x_series_clipped = x_series[plot_start_time:plot_end_time]
    y_series_clipped = y_series[plot_start_time:plot_end_time]

    if x_series_clipped.empty or y_series_clipped.empty:
        pm.warning(f"Panel: X({len(x_series_clipped)}) or Y({len(y_series_clipped)}) series empty after clipping to {plot_start_time} - {plot_end_time}.")
        # Check original lengths before clipping
        if x_series.empty or y_series.empty:
             pm.warning("Panel: Original X or Y series was empty even before clipping.")
        else:
             pm.warning(f"Panel: Original X range: {x_series.index.min()} - {x_series.index.max()}")
             pm.warning(f"Panel: Original Y range: {y_series.index.min()} - {y_series.index.max()}")
        return False # Cannot proceed if no data in range

    # 5. Resample and Align Data (Simplified error handling)
    try:
        if len(x_series_clipped.index) > 1: x_median_dt_timedelta = pd.Series(x_series_clipped.index).diff().median()
        else: x_median_dt_timedelta = pd.Timedelta(seconds=1)
        if len(y_series_clipped.index) > 1: y_median_dt_timedelta = pd.Series(y_series_clipped.index).diff().median()
        else: y_median_dt_timedelta = pd.Timedelta(seconds=1)
        
        target_dt_timedelta = max(x_median_dt_timedelta, y_median_dt_timedelta)
        # Ensure target frequency is positive
        if target_dt_timedelta <= pd.Timedelta(0):
             pm.warning(f"Panel: Calculated non-positive resampling interval ({target_dt_timedelta}). Defaulting to 1s.")
             target_dt_timedelta = pd.Timedelta(seconds=1)
            
        pm.status(f"Panel: Target resampling interval: {target_dt_timedelta}")

        common_start_time = max(x_series_clipped.index.min(), y_series_clipped.index.min())
        common_end_time = min(x_series_clipped.index.max(), y_series_clipped.index.max())

        if common_start_time >= common_end_time:
            pm.warning(f"Panel: No overlapping time range found after clipping. X: {x_series_clipped.index.min()} - {x_series_clipped.index.max()}, Y: {y_series_clipped.index.min()} - {y_series_clipped.index.max()}")
            return False

        common_datetime_index = pd.date_range(start=common_start_time, end=common_end_time, freq=target_dt_timedelta)
        
        if common_datetime_index.empty:
            pm.warning(f"Panel: Common datetime index empty. Start: {common_start_time}, End: {common_end_time}, Freq: {target_dt_timedelta}")
            return False

        # Ensure tolerance is at least the resampling interval for 'nearest'
        tolerance = target_dt_timedelta 
        pm.debug(f"Panel: Using reindex tolerance: {tolerance}")

        x_series_reindexed = x_series.reindex(common_datetime_index, method='nearest', tolerance=tolerance)
        y_series_reindexed = y_series.reindex(common_datetime_index, method='nearest', tolerance=tolerance)
        
        df_resampled = pd.DataFrame({'x': x_series_reindexed, 'y': y_series_reindexed})
        df_resampled.dropna(inplace=True)

        if df_resampled.empty:
            pm.warning("Panel: DataFrame empty after resampling and dropping NaNs.")
            return False

        x_resampled = df_resampled['x'].values
        y_resampled = df_resampled['y'].values
        common_times_for_coloring = df_resampled.index
        pm.status(f"Panel: Resampled to {len(x_resampled)} common data points.")

    except Exception as e:
        pm.error(f"Panel: Error during resampling: {e}")
        import traceback; pm.error(traceback.format_exc()) # Enable full traceback for resampling errors
        return False

    # 6. Assign Colors & Sizes
    colors_array = [outside_color] * len(common_times_for_coloring)
    sizes_array = [outside_size] * len(common_times_for_coloring)
    for i, current_pd_time in enumerate(common_times_for_coloring):
        # Pandas Timestamps can be timezone-aware or naive.
        # hole_intervals contain timezone-aware (UTC) datetimes.
        # Comparison needs consistent awareness.
        current_dt_time_utc = current_pd_time.tz_convert('UTC') if current_pd_time.tz is not None else current_pd_time.tz_localize('UTC')
        
        for hole_start, hole_end in hole_intervals:
            # Ensure hole_start and hole_end are also UTC (should be from _parse_marker_file)
            if hole_start <= current_dt_time_utc <= hole_end:
                colors_array[i] = inside_color
                sizes_array[i] = inside_size
                break
    num_inside = colors_array.count(inside_color)
    pm.status(f"Panel: {num_inside} points inside holes.")

    # 7. Plot Hodogram onto the provided 'ax'
    try:
        ax.scatter(x_resampled, y_resampled, c=colors_array, s=sizes_array, alpha=alpha, edgecolors='none')

        # Attempt to get labels from data object, fall back to subclass name
        final_x_label = x_label if x_label is not None else getattr(x_data_obj, 'legend_label', x_data_req.subclass_name)
        final_y_label = y_label if y_label is not None else getattr(y_data_obj, 'legend_label', y_data_req.subclass_name)
        
        ax.set_xlabel(final_x_label, fontsize=base_fontsize)
        ax.set_ylabel(final_y_label, fontsize=base_fontsize)
        ax.set_title(title, fontsize=base_fontsize + 2)

        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label=f'In ({num_inside})', markerfacecolor=inside_color, markersize=np.sqrt(inside_size)), # Shorter legend labels
            Line2D([0], [0], marker='o', color='w', label=f'Out ({len(colors_array) - num_inside})', markerfacecolor=outside_color, markersize=np.sqrt(outside_size))
        ]
        ax.legend(handles=legend_elements, loc='best', fontsize=base_fontsize - 1)
        ax.grid(True, linestyle=':', alpha=0.6)
        pm.status(f"Panel: Successfully plotted {x_data_req.class_name}.{x_data_req.subclass_name} vs {y_data_req.class_name}.{y_data_req.subclass_name}")
        return True # Indicate success for this panel
    except Exception as e:
        pm.error(f"Panel: Error during plotting step: {e}")
        import traceback; pm.error(traceback.format_exc())
        return False # Indicate failure for this panel

# -----------------------------------------------------------
# Main User-Facing Function
# -----------------------------------------------------------
def showda_holes(
    trange_plot: list, 
    x_data_req=None,      # Now optional if panel_definitions is used
    y_data_req=None,      # Now optional if panel_definitions is used
    marker_filepath=None, # Now optional if panel_definitions is used
    panel_definitions: list = None, # New argument for multi-panel definitions
    main_title: str = None, # New argument for main figure title
    main_title_fontsize: int = None, # New: Specific fontsize for main title
    main_title_y: float = 0.98, # New: Vertical position for main title
    # Optional kwargs get passed down or used for single plot
    **kwargs 
):
    """
    Generates a hodogram (or a grid of hodograms) where points are colored 
    based on magnetic hole intervals from marker file(s).

    Can be called in two ways:

    1. Single Plot Mode:
       Provide trange_plot, x_data_req, y_data_req, marker_filepath, and optional 
       keyword arguments (title, labels, colors, sizes, alpha, figsize, base_fontsize).
    
    2. Multi-Panel Mode:
       Provide trange_plot and panel_definitions. Ignore x_data_req, y_data_req, 
       marker_filepath. The panel_definitions argument should be a list of 
       dictionaries, where each dictionary defines a panel and must contain:
         - 'x_data': Data request object for the x-axis.
         - 'y_data': Data request object for the y-axis.
         - 'marker_file': Path to the marker file for this panel.
       Each dictionary can optionally contain arguments like 'title', 'x_label', 
       'y_label', 'inside_color', etc., to override defaults for that specific panel.
       General kwargs passed to showda_holes (like figsize, base_fontsize) will 
       apply globally unless overridden in a panel definition.

    Args:
        trange_plot (list): Time range for the plot(s) [start_time_str, end_time_str].
        x_data_req: Data request object for x-axis (Single Plot Mode).
        y_data_req: Data request object for y-axis (Single Plot Mode).
        marker_filepath (str): Path to marker file (Single Plot Mode).
        panel_definitions (list, optional): List of dicts defining panels (Multi-Panel Mode).
        main_title (str, optional): Overrides the default main title (Encounter + Time Range).
        main_title_fontsize (int, optional): Specific font size for the main title. Defaults to base_fontsize + 4.
        main_title_y (float, optional): Vertical position of the main title (0.0-1.0, default 0.98).
        **kwargs: Optional keyword arguments for customization (passed to single plot 
                  or used as defaults for multi-panel). Includes title, x_label, 
                  y_label, inside_color, outside_color, inside_size, outside_size, 
                  alpha, figsize, base_fontsize.

    Returns:
        tuple: (fig, ax) for single plot mode, or (fig, axes) for multi-panel mode 
               if successful. (None, None) on failure.
    """
    pm = global_pm # Use the imported global print_manager
    
    # --- Determine Main Title --- 
    final_main_title = main_title
    if final_main_title is None:
        try:
            # Parse dates first for encounter and formatting
            start_dt_obj = dateutil_parse(trange_plot[0])
            end_dt_obj = dateutil_parse(trange_plot[1])
            encounter_str = get_encounter_number(start_dt_obj) # Pass datetime object
            # Format dates nicely
            start_fmt = start_dt_obj.strftime("%Y-%m-%d %H:%M")
            end_fmt = end_dt_obj.strftime("%H:%M") if start_dt_obj.date() == end_dt_obj.date() else end_dt_obj.strftime("%Y-%m-%d %H:%M")
            final_main_title = f"{encounter_str}: {start_fmt} to {end_fmt}"
        except Exception as e:
            pm.warning(f"Could not auto-generate main title: {e}")
            final_main_title = "Hodogram Plot" # Fallback title
            
    # --- Decide Mode based on panel_definitions --- 
    if panel_definitions is not None:
        # --- Multi-Panel Mode --- 
        pm.status(f"🚀 Initiating multi-panel showda_holes for {len(panel_definitions)} panels.")
        
        if not isinstance(panel_definitions, list) or not panel_definitions:
            pm.error("Multi-panel mode requires 'panel_definitions' to be a non-empty list.")
            return None, None
            
        num_panels = len(panel_definitions)
        if num_panels == 1:
            nrows, ncols = 1, 1
        elif num_panels == 2:
            nrows, ncols = 1, 2
        elif num_panels == 3 or num_panels == 4:
            nrows, ncols = 2, 2
        else:
            pm.error(f"Unsupported number of panels: {num_panels}. Max 4 supported.")
            return None, None
            
        # Global figure settings from kwargs
        figsize = kwargs.get('figsize', (6*ncols, 5*nrows)) # Adjust default figsize
        base_fontsize_global = kwargs.get('base_fontsize', 12)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False) # Ensure axes is always 2D array
        
        # --- Apply Main Title --- 
        if final_main_title:
            title_size = main_title_fontsize if main_title_fontsize is not None else base_fontsize_global + 4
            fig.suptitle(final_main_title, fontsize=title_size, y=main_title_y)
            
        axes_flat = axes.flat # Flatten for easy iteration
        
        all_panels_success = True
        for i, panel_def in enumerate(panel_definitions):
            if i >= len(axes_flat): # Should not happen with nrows/ncols logic, but safety check
                 pm.warning(f"More panel definitions ({num_panels}) than available axes ({len(axes_flat)}). Skipping extra panels.")
                 break
                 
            ax = axes_flat[i]
            pm.status(f"--- Processing Panel {i+1}/{num_panels} ---")
            
            # Check for required keys in panel definition
            required_keys = ['x_data', 'y_data', 'marker_file']
            if not all(key in panel_def for key in required_keys):
                pm.error(f"Panel {i+1} definition is missing required keys: {required_keys}. Found: {list(panel_def.keys())}")
                all_panels_success = False
                ax.text(0.5, 0.5, f'Panel {i+1}\nConfig Error', ha='center', va='center', transform=ax.transAxes, color='red')
                continue # Skip this panel
                
            # Extract data and customizations for this panel
            panel_x_req = panel_def['x_data']
            panel_y_req = panel_def['y_data']
            panel_marker = panel_def['marker_file']
            
            # Combine global kwargs with panel-specific kwargs (panel overrides global)
            panel_kwargs = kwargs.copy()
            panel_kwargs.update(panel_def) # panel_def overrides kwargs
            
            # Remove keys that are not arguments for the helper function
            panel_kwargs.pop('x_data', None)
            panel_kwargs.pop('y_data', None)
            panel_kwargs.pop('marker_file', None)
            
            # Call the helper to plot on this panel's axis
            success = _plot_single_hodogram_panel(
                ax=ax,
                trange_plot=trange_plot,
                x_data_req=panel_x_req,
                y_data_req=panel_y_req,
                marker_filepath=panel_marker,
                pm=pm,
                # Pass remaining relevant kwargs
                title=panel_kwargs.get('title', f'Panel {i+1}'), # Default panel title
                x_label=panel_kwargs.get('x_label', None),
                y_label=panel_kwargs.get('y_label', None),
                inside_color=panel_kwargs.get('inside_color', 'red'),
                outside_color=panel_kwargs.get('outside_color', 'blue'),
                inside_size=panel_kwargs.get('inside_size', 50),
                outside_size=panel_kwargs.get('outside_size', 10),
                alpha=panel_kwargs.get('alpha', 0.7),
                base_fontsize=panel_kwargs.get('base_fontsize', base_fontsize_global)
            )
            if not success:
                all_panels_success = False
                # Optionally add error text to the panel if plotting failed
                ax.text(0.5, 0.5, f'Panel {i+1}\nPlot Failed', ha='center', va='center', transform=ax.transAxes, color='orange')

        # Hide unused axes if num_panels is 3
        if num_panels == 3:
            axes_flat[-1].set_visible(False)
            
        # Use standard tight_layout; explicit y positioning handles title space
        fig.tight_layout() 
        # fig.tight_layout(rect=[0, 0.03, 1, main_title_y - 0.03]) # Alternative if needed
        plt.show()
        pm.status("✅ Multi-panel hodogram displayed.")
        return fig, axes # Return fig and the array of axes
            
    else:
        # --- Single Plot Mode --- 
        pm.status("🚀 Initiating single-panel showda_holes.")
        
        # Check if required arguments for single plot mode are provided
        if x_data_req is None or y_data_req is None or marker_filepath is None:
            pm.error("Single plot mode requires x_data_req, y_data_req, and marker_filepath arguments.")
            return None, None
            
        # Get figure settings from kwargs
        figsize = kwargs.get('figsize', (10, 8)) # Default single plot size
        base_fontsize_global = kwargs.get('base_fontsize', 12) # Get base fontsize for suptitle
        # main_title_fontsize = kwargs.get('main_title_fontsize', None) # Already handled by direct param
        # main_title_y = kwargs.get('main_title_y', 0.98) # Already handled by direct param

        fig, ax = plt.subplots(figsize=figsize)
        
        # --- Apply Main Title --- 
        if final_main_title:
            title_size = main_title_fontsize if main_title_fontsize is not None else base_fontsize_global + 4
            fig.suptitle(final_main_title, fontsize=title_size, y=main_title_y)
            
        # Call the helper function with the provided arguments
        success = _plot_single_hodogram_panel(
            ax=ax,
            trange_plot=trange_plot,
            x_data_req=x_data_req,
            y_data_req=y_data_req,
            marker_filepath=marker_filepath,
            pm=pm,
            # Pass all optional kwargs directly
            **kwargs 
        )

        if success:
            # Adjust layout for suptitle before showing
            # Use standard tight_layout; explicit y positioning handles title space
            fig.tight_layout() 
            # fig.tight_layout(rect=[0, 0.03, 1, main_title_y - 0.03]) # Alternative if needed
            plt.show() # Show the single plot
            pm.status("✅ Single hodogram displayed.")
            return fig, ax # Return fig and the single axis
        else:
            pm.error("Failed to generate single hodogram panel.")
            # Clean up the empty figure if plotting failed
            plt.close(fig)
            return None, None

if __name__ == '__main__':
    # Example Usage (for testing _parse_marker_file directly)
    # ... (previous __main__ content for _parse_marker_file testing) ...
    # Keep the existing __main__ for _parse_marker_file, 
    # then add a new section for showdaholes if direct testing is desired (requires data setup)

    # --- Test section for _parse_marker_file (from previous step) ---
    pm_test = FallbackPrintManager()
    dummy_file_content_main = """
[Metadata/trange]	0		trange = ['2023-09-28 05:32:00', '2023-09-28 07:45:00']
[Metadata/Encountr]	0		E17
[Metadata/Holes]	0		Holes Found: 2
[Metadata/AvgWidth]	0		Avg Hole Width: 127.74
[Metadata/AvgDepth]	0		Avg Hole Depth: 26.27%
[Metadata/Duration]	0		Total Duration: 2:13:00
[Metadata/Samples]	0		Total Samples: 2337879
[Metadata/InstrSR]	0		Instr Sampling Rate: 292.97 s/s

MH	1000	2000
MH_MIN	1500
MH	3000	4000
MH_MIN	3500
    """
    dummy_filepath_main = "dummy_marker_file_for_main_test.txt"
    with open(dummy_filepath_main, "w") as f:
        f.write(dummy_file_content_main)

    intervals_main = _parse_marker_file(dummy_filepath_main, pm_test)
    if intervals_main:
        pm_test.status(f"(Main Test) Successfully parsed {len(intervals_main)} intervals:")
        # for start, end in intervals_main:
        #     pm_test.status(f"  Start: {start}, End: {end}")
    else:
        pm_test.error("(Main Test) Failed to parse dummy marker file.")
    
    # --- Test section for showdaholes (conceptual) ---
    # To truly test showdaholes here, we'd need to:
    # 1. Mock data_cubby, get_data, and actual data classes (e.g., mag_rtn_4sa).
    # 2. Create dummy data that get_data would load.
    # This is complex for a simple __main__. Usually, such tests are done with a testing framework (pytest).
    
    pm_test.status("\n--- Conceptual showdaholes test (plotting will not appear without real data/mocks) ---")

    # Dummy data request objects (mimicking what your actual data classes might look like)
    class DummyDataReq:
        def __init__(self, class_name, subclass_name, legend_label="Dummy Data"):
            self.class_name = class_name
            self.subclass_name = subclass_name
            self.legend_label = legend_label
            self.datetime_array = None # Must be populated by get_data or a mock
            self.values = None         # Must be populated by get_data or a mock

    # Mocking get_data and data_cubby for a self-contained example is non-trivial.
    # For now, we assume these would be available in the broader application context.
    # If you run this file directly, the showdaholes call below would likely fail
    # unless you mock data_cubby.grab, get_data, and the data objects.

    # Example call structure (would need mocks to run fully):
    trange_example = ['2023-09-28 05:33:00', '2023-09-28 05:40:00']
    x_req = DummyDataReq("mag_rtn_4sa_data", "Br")
    y_req = DummyDataReq("proton_data_psp", "Vr")
    
    # Mock data_cubby and get_data for a direct run if needed for a basic check:
    class MockDataCubby:
        def __init__(self):
            self.store = {}
        def grab(self, class_name):
            return self.store.get(class_name)
        def store_data(self, data_object_instance):
            self.store[data_object_instance.class_name] = data_object_instance
            
    # These globals will be rebound for the test
    _original_data_cubby = data_cubby
    _original_get_data = get_data
    
    # It's important to use the actual names that showdaholes imports and uses.
    # If showdaholes does `from .data_cubby import data_cubby`, we need to ensure
    # this __main__ block can effectively change what `data_cubby` refers to when showdaholes is called.
    # For a script run directly, assignments here in __main__ change globals in the __main__ module.
    # If showdaholes is in the same file, it will see these changed globals.
    
    current_module = sys.modules[__name__] # Get a reference to the current module
    current_module.data_cubby = MockDataCubby() # Override with mock

    def mock_get_data(trange, *data_reqs):
        pm_test.status(f"Mock get_data called for {len(data_reqs)} items in trange {trange}")
        base_time = dateutil_parse(trange[0]).replace(tzinfo=timezone.utc)
        n_points = 100
        time_deltas = np.array([timedelta(seconds=i) for i in range(n_points)]) # Correct timedelta generation
        mock_datetimes = np.array([base_time + td for td in time_deltas])
        
        for req in data_reqs:
            req.datetime_array = mock_datetimes
            # Simulate some data pattern
            if req.subclass_name == "Br":
                req.values = np.sin(np.linspace(0, 4 * np.pi, n_points)) * 10 
            else:
                req.values = np.cos(np.linspace(0, 4 * np.pi, n_points)) * 400 + 450
            
            class MockClassInstance:
                def __init__(self, data_obj):
                    self.data_obj = data_obj
                    self.class_name = data_obj.class_name # So data_cubby.grab finds it by original name
                def get_subclass(self, subclass_name):
                    if subclass_name == self.data_obj.subclass_name:
                        return self.data_obj
                    return None
            
            # Use the module-level (mocked) data_cubby
            current_module.data_cubby.store_data(MockClassInstance(req))
        return True

    current_module.get_data = mock_get_data # Override with mock

    # Replace global_pm methods with our test pm for the duration of this direct test.
    old_pm_status, old_pm_error, old_pm_warning, old_pm_debug = None, None, None, None
    # Check if global_pm exists and is an object with methods (not None)
    if hasattr(current_module, 'global_pm') and current_module.global_pm is not None:
        actual_pm_instance = current_module.global_pm
        old_pm_status = getattr(actual_pm_instance, 'status', None)
        old_pm_error = getattr(actual_pm_instance, 'error', None)
        old_pm_warning = getattr(actual_pm_instance, 'warning', None)
        old_pm_debug = getattr(actual_pm_instance, 'debug', None)

        actual_pm_instance.status = pm_test.status
        actual_pm_instance.error = pm_test.error
        actual_pm_instance.warning = pm_test.warning
        actual_pm_instance.debug = pm_test.debug
    else:
        pm_test.warning("global_pm not found or not initialized in the module, cannot redirect for test.")

    pm_test.status("Attempting to run showdaholes with mocked data (plot may show)...")
    # The showdaholes function is defined in this file, so it will use the mocked versions if called from here.
    fig, ax = showda_holes(
        trange_plot=trange_example,
        x_data_req=x_req,
        y_data_req=y_req,
        marker_filepath=dummy_filepath_main
    )
    pm_test.status(f"showdaholes call completed with fig, ax: {fig is not None and ax is not None}")

    # Restore original print_manager functions and other mocks
    if hasattr(current_module, 'global_pm') and current_module.global_pm is not None and old_pm_status:
        actual_pm_instance = current_module.global_pm
        actual_pm_instance.status = old_pm_status
        actual_pm_instance.error = old_pm_error
        actual_pm_instance.warning = old_pm_warning
        actual_pm_instance.debug = old_pm_debug
        
    current_module.data_cubby = _original_data_cubby
    current_module.get_data = _original_get_data

    import os
    os.remove(dummy_filepath_main)
    pm_test.status(f"(Main Test) Cleaned up {dummy_filepath_main}") 