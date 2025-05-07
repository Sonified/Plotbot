from . import print_manager
from . import data_cubby
import numpy as np
import pandas as pd
import time
import pickle
from datetime import datetime, timezone, timedelta
import os
import copy
from dateutil.parser import parse

# Import our custom managers and classes
from .print_manager import print_manager
from .data_cubby import data_cubby
from .plot_manager import plot_manager
from .data_tracker import global_tracker
from .data_classes.psp_mag_classes import mag_rtn_class, mag_sc_class # Ensure specific classes can be checked if needed
from .data_classes.psp_data_types import data_types as psp_data_types

# Type hint for raw data object
from typing import Any, List, Tuple, Dict, Optional, Union
DataObject = Any 

# NEW IMPORT for the enhanced functionality
from .get_data import get_data as plotbot_get_data

# --- Maintain your cute variable shorthands mapping ---
VARIABLE_SHORTHANDS = {
    'mag_rtn_4sa_class': 'mag4',
    'mag_rtn_class': 'mag',
    'mag_sc_4sa_class': 'magsc4',
    'mag_sc_class': 'magsc',
    'proton_class': 'pro',
    'proton_hr_class': 'proHR',
    'proton_fits_class': 'proF',
    'epad_strahl_class': 'pad',
    'epad_strahl_high_res_class': 'padHR',
    'ham_class': 'ham'
    # Add more mappings as needed
}

def _is_data_object_empty(obj):
    """
    Helper to check if a data object is empty (no data in main fields).
    Returns True if empty, False otherwise.
    """
    # Try to check for a 'raw_data' dict with all None or empty arrays
    if hasattr(obj, 'raw_data'):
        raw = getattr(obj, 'raw_data')
        if isinstance(raw, dict):
            for v in raw.values():
                if v is not None:
                    # If it's an array, check if it has data
                    try:
                        if hasattr(v, 'size') and v.size > 0:
                            return False
                        if hasattr(v, '__len__') and len(v) > 0:
                            return False
                    except Exception:
                        pass
                    # If it's a scalar or something else, just check not None
                    continue
            return True  # All values None or empty
    # Fallback: check for common data fields
    for field in ['data', 'values', 'array', 'datetime_array']:
        if hasattr(obj, field):
            v = getattr(obj, field)
            if v is not None:
                try:
                    if hasattr(v, 'size') and v.size > 0:
                        return False
                    if hasattr(v, '__len__') and len(v) > 0:
                        return False
                except Exception:
                    pass
    return True

def _create_filtered_instance(instance, start_time, end_time):
    """
    Create a time-filtered copy of a data instance.
    
    Parameters
    ----------
    instance : object
        The original data instance to filter
    start_time, end_time : datetime
        Start and end time for filtering
        
    Returns
    -------
    object
        A new instance with filtered data
    """
    # Create a deep copy of the instance
    filtered_instance = copy.deepcopy(instance)
    
    if not hasattr(instance, 'datetime_array') or instance.datetime_array is None:
        print_manager.warning(f"Instance {instance.__class__.__name__} has no datetime_array, cannot filter")
        return filtered_instance
    
    # Create time mask based on datetime type
    if isinstance(instance.datetime_array[0], np.datetime64):
        # For numpy datetime64 arrays
        np_start = np.datetime64(start_time)
        np_end = np.datetime64(end_time)
        time_mask = (instance.datetime_array >= np_start) & (instance.datetime_array <= np_end)
    elif hasattr(instance.datetime_array[0], 'tzinfo'):
        # Handle timezone-aware datetime objects
        start_utc = start_time.astimezone(timezone.utc) if start_time.tzinfo else start_time.replace(tzinfo=timezone.utc)
        end_utc = end_time.astimezone(timezone.utc) if end_time.tzinfo else end_time.replace(tzinfo=timezone.utc)
        # Need to compare each datetime individually
        time_mask = np.array([(t >= start_utc) and (t <= end_utc) for t in instance.datetime_array])
    else:
        # Naive datetime objects
        time_mask = np.array([(t >= start_time) and (t <= end_time) for t in instance.datetime_array])
    
    # Apply the mask to datetime_array
    filtered_instance.datetime_array = instance.datetime_array[time_mask]
    
    # Filter 'time' attribute if present (TT2000 times)
    if hasattr(instance, 'time') and instance.time is not None:
        filtered_instance.time = instance.time[time_mask]
    
    # Filter raw_data based on the same mask
    if hasattr(instance, 'raw_data') and instance.raw_data is not None:
        filtered_raw_data = {}
        for key, value in instance.raw_data.items():
            if value is None:
                filtered_raw_data[key] = None
            elif isinstance(value, list):
                # Handle list of arrays (common for 'all' key)
                if all(hasattr(item, 'shape') for item in value):
                    filtered_raw_data[key] = [item[time_mask] for item in value]
                else:
                    # If not all items are arrays, keep as is
                    filtered_raw_data[key] = value
            elif hasattr(value, 'shape'):
                # Handle numpy arrays
                if len(value.shape) == 1:
                    # 1D array - filter directly
                    filtered_raw_data[key] = value[time_mask]
                elif len(value.shape) > 1:
                    # Multi-dimensional array - filter along first dimension
                    filtered_raw_data[key] = value[time_mask, ...]
                else:
                    # Scalar or empty - keep as is
                    filtered_raw_data[key] = value
            else:
                # Non-array type, keep as is
                filtered_raw_data[key] = value
        
        filtered_instance.raw_data = filtered_raw_data
    
    # Filter 'field' attribute if present
    if hasattr(instance, 'field') and instance.field is not None and hasattr(instance.field, 'shape'):
        if len(instance.field.shape) > 1:
            filtered_instance.field = instance.field[time_mask, ...]
        else:
            filtered_instance.field = instance.field[time_mask]
    
    return filtered_instance

def _identify_data_segments(instance, time_filter=None):
    """
    Identify distinct data segments with significant time gaps.
    
    Parameters
    ----------
    instance : object
        The data instance to analyze
    time_filter : tuple, optional
        Optional (start_time, end_time) filter to apply first
        
    Returns
    -------
    list
        List of segment instances, or empty list if no significant gaps found
    """
    pm = print_manager

    if not hasattr(instance, 'datetime_array') or instance.datetime_array is None or len(instance.datetime_array) == 0:
        return []
        
    source_for_segment_data = instance # Default to original instance
    if time_filter:
        # If time_filter is applied, source_for_segment_data becomes the filtered_instance
        source_for_segment_data = _create_filtered_instance(instance, time_filter[0], time_filter[1])
        
        # Check if filtering resulted in an empty or invalid object
        if _is_data_object_empty(source_for_segment_data) or \
           not hasattr(source_for_segment_data, 'datetime_array') or \
           source_for_segment_data.datetime_array is None or \
           len(source_for_segment_data.datetime_array) == 0:
            return []
            
    times_to_sort = source_for_segment_data.datetime_array
    # Additional check if, after all, times_to_sort is still problematic (e.g. if datetime_array was None after filtering)
    if times_to_sort is None or len(times_to_sort) == 0:
        pm.warning("[SNAPSHOT DEBUG] _identify_data_segments: times_to_sort is None or empty after source determination.")
        return []

    # --- Add Enhanced Sanity Check for component data structures --- 
    if hasattr(source_for_segment_data, 'raw_data') and source_for_segment_data.raw_data is not None and 'all' in source_for_segment_data.raw_data:
        all_data = source_for_segment_data.raw_data['all']
        # Handle case where 'all' is a list of components (like in mag_rtn_4sa)
        if isinstance(all_data, list) and len(all_data) > 0:
            # Check if each component has the expected length
            for i, comp in enumerate(all_data):
                if len(comp) != len(source_for_segment_data.datetime_array):
                    pm.error(f"[SNAPSHOT CRITICAL] _identify_data_segments: COMPONENT LENGTH MISMATCH! "
                            f"Component {i} length: {len(comp)}, "
                            f"datetime_array length: {len(source_for_segment_data.datetime_array)} "
                            f"for instance type {type(source_for_segment_data).__name__}.")
                    # We'll continue but log the discrepancy
            
            # Only check the first component for the sanity check message
            pm.debug(f"[SNAPSHOT DEBUG] _identify_data_segments: Component data structure detected. "
                    f"First component length: {len(all_data[0])}, "
                    f"datetime_array length: {len(source_for_segment_data.datetime_array)}")
        # Handle case where 'all' is a single array
        elif hasattr(all_data, '__len__') and not isinstance(all_data, list):
            if len(all_data) != len(source_for_segment_data.datetime_array):
                pm.error(f"[SNAPSHOT CRITICAL] _identify_data_segments: LEN MISMATCH! "
                        f"raw_data['all'] len: {len(all_data)}, "
                        f"datetime_array len: {len(source_for_segment_data.datetime_array)} "
                        f"for instance type {type(source_for_segment_data).__name__}.")
    
    # --- Standard time/datetime_array length check ---
    if hasattr(source_for_segment_data, 'time') and source_for_segment_data.time is not None and \
       hasattr(source_for_segment_data, 'datetime_array') and source_for_segment_data.datetime_array is not None:
        # This check is crucial: are the time array (often TT2000) and datetime_array (Python/Numpy datetime) of the same length?
        if len(source_for_segment_data.time) != len(source_for_segment_data.datetime_array):
            pm.error(f"[SNAPSHOT CRITICAL] _identify_data_segments: LEN MISMATCH! "
                     f".time len: {len(source_for_segment_data.time)}, "
                     f".datetime_array len: {len(source_for_segment_data.datetime_array)} "
                     f"for instance type {type(source_for_segment_data).__name__}. This will likely cause indexing errors.")
            # Depending on desired robustness, one might return [] here or try to reconcile.
            # For now, logging the error is the primary goal of this check.
        else:
            pm.status(f"[SNAPSHOT DEBUG] _identify_data_segments: Lengths match for .time and .datetime_array: {len(source_for_segment_data.datetime_array)} for {type(source_for_segment_data).__name__}")
    elif hasattr(source_for_segment_data, 'datetime_array') and source_for_segment_data.datetime_array is not None and \
         (not hasattr(source_for_segment_data, 'time') or source_for_segment_data.time is None):
        pm.warning(f"[SNAPSHOT DEBUG] _identify_data_segments: Instance {type(source_for_segment_data).__name__} has datetime_array but no .time attribute or .time is None.")
    # --- End Enhanced Sanity Check ---
        
    sorted_indices = np.argsort(times_to_sort)
    sorted_times = times_to_sort[sorted_indices]
    
    # Calculate time differences between consecutive points
    if isinstance(sorted_times[0], np.datetime64):
        # For numpy datetime64 arrays
        time_diffs = np.diff(sorted_times).astype('timedelta64[s]').astype(float)
    else:
        # For regular datetime objects
        time_diffs = np.array([(sorted_times[i+1] - sorted_times[i]).total_seconds() 
                              for i in range(len(sorted_times)-1)])
    
    # Find the median time difference as a reference
    median_diff = np.median(time_diffs)
    
    # Set threshold for significant gaps (10x median or 1 hour, whichever is smaller)
    threshold_seconds = min(median_diff * 10, 3600)  # 3600 seconds = 1 hour
    
    # Find indices where gaps exceed the threshold
    gap_indices = []
    for i, diff in enumerate(time_diffs):
        if diff > threshold_seconds:
            gap_indices.append(i + 1)  # +1 because diff[i] is between times[i] and times[i+1]
            
    # If no significant gaps, return empty list
    if not gap_indices:
        return []
        
    # Create segments based on gaps
    segments = []
    
    # Process each segment
    start_idx = 0
    
    for end_idx in gap_indices:
        # Create segment by filtering the instance
        segment_mask = sorted_indices[start_idx:end_idx]
        segment = copy.deepcopy(source_for_segment_data)
        
        # Apply the mask to datetime_array and time
        segment.datetime_array = times_to_sort[segment_mask]
        if hasattr(source_for_segment_data, 'time') and source_for_segment_data.time is not None:
            segment.time = source_for_segment_data.time[segment_mask]
        
        # Filter raw_data based on the same mask
        if hasattr(source_for_segment_data, 'raw_data') and source_for_segment_data.raw_data is not None:
            filtered_raw_data = {}
            for key, value in source_for_segment_data.raw_data.items():
                if value is None:
                    filtered_raw_data[key] = None
                elif isinstance(value, list) and all(hasattr(item, 'shape') for item in value):
                    # Enhanced handling for component-based data (like in mag_rtn_4sa)
                        filtered_raw_data[key] = [item[segment_mask] for item in value]
                elif hasattr(value, 'shape'):
                    if len(value.shape) == 1:
                        filtered_raw_data[key] = value[segment_mask]
                    elif len(value.shape) > 1:
                        filtered_raw_data[key] = value[segment_mask, ...]
                    else:
                        filtered_raw_data[key] = value
                else:
                    filtered_raw_data[key] = value
            
            segment.raw_data = filtered_raw_data
        
        # Filter 'field' attribute if present
        if hasattr(source_for_segment_data, 'field') and source_for_segment_data.field is not None and hasattr(source_for_segment_data.field, 'shape'):
            if len(source_for_segment_data.field.shape) > 1:
                segment.field = source_for_segment_data.field[segment_mask, ...]
            else:
                segment.field = source_for_segment_data.field[segment_mask]
        
        segments.append(segment)
        start_idx = end_idx
    
    # Don't forget the last segment
    segment_mask = sorted_indices[start_idx:]
    segment = copy.deepcopy(source_for_segment_data)
    segment.datetime_array = times_to_sort[segment_mask]
    if hasattr(source_for_segment_data, 'time') and source_for_segment_data.time is not None:
        segment.time = source_for_segment_data.time[segment_mask]
    
    # Filter raw_data for last segment
    if hasattr(source_for_segment_data, 'raw_data') and source_for_segment_data.raw_data is not None:
        filtered_raw_data = {}
        for key, value in source_for_segment_data.raw_data.items():
            if value is None:
                filtered_raw_data[key] = None
            elif isinstance(value, list) and all(hasattr(item, 'shape') for item in value):
                # Enhanced handling for component-based data (like in mag_rtn_4sa)
                    filtered_raw_data[key] = [item[segment_mask] for item in value]
            elif hasattr(value, 'shape'):
                if len(value.shape) == 1:
                    filtered_raw_data[key] = value[segment_mask]
                elif len(value.shape) > 1:
                    filtered_raw_data[key] = value[segment_mask, ...]
                else:
                    filtered_raw_data[key] = value
            else:
                filtered_raw_data[key] = value
        
        segment.raw_data = filtered_raw_data
    
    # Filter 'field' attribute for last segment
    if hasattr(source_for_segment_data, 'field') and source_for_segment_data.field is not None and hasattr(source_for_segment_data.field, 'shape'):
        if len(source_for_segment_data.field.shape) > 1:
            segment.field = source_for_segment_data.field[segment_mask, ...]
        else:
            segment.field = source_for_segment_data.field[segment_mask]
    
    segments.append(segment)
    return segments

class SimpleDataObject:
    """Simple data object for passing segment data."""
    def __init__(self):
        self.times = None
        self.data = {}
        # Could add a flag: self.is_reconstituted_segment = False

def _ensure_component_consistency(instance):
    """
    Ensures that all components in instance.raw_data['all'] have the same length
    as instance.datetime_array. If not, truncates the longer ones to match.
    
    Parameters
    ----------
    instance : object
        The data instance to check/fix
        
    Returns
    -------
    bool
        True if modifications were made, False if already consistent or not applicable
    """
    pm = print_manager
    
    if not hasattr(instance, 'datetime_array') or instance.datetime_array is None:
        return False
        
    if not hasattr(instance, 'raw_data') or instance.raw_data is None or 'all' not in instance.raw_data:
        return False
        
    all_data = instance.raw_data['all']
    
    # Handle component-based structures (list of arrays)
    if isinstance(all_data, list) and len(all_data) > 0:
        dt_len = len(instance.datetime_array)
        modifications_made = False
        
        for i, comp in enumerate(all_data):
            if len(comp) != dt_len:
                pm.warning(f"[SNAPSHOT] Fixing component length mismatch: Component {i} length ({len(comp)}) != datetime_array length ({dt_len})")
                # Truncate the longer one to match
                if len(comp) > dt_len:
                    instance.raw_data['all'][i] = comp[:dt_len]
                    modifications_made = True
                else:
                    # This case is trickier - datetime_array is longer than component
                    # Safest option is to truncate datetime_array to match the shortest component
                    pm.warning(f"[SNAPSHOT] Component {i} is shorter than datetime_array. Will truncate datetime_array.")
                    instance.datetime_array = instance.datetime_array[:len(comp)]
                    if hasattr(instance, 'time') and instance.time is not None:
                        instance.time = instance.time[:len(comp)]
                    
                    # Now truncate any other components that might be longer than this one
                    for j in range(len(all_data)):
                        if j != i and len(all_data[j]) > len(comp):
                            instance.raw_data['all'][j] = all_data[j][:len(comp)]
                    
                    # Fix any individual named components too
                    for key in instance.raw_data:
                        if key != 'all' and hasattr(instance.raw_data[key], '__len__') and len(instance.raw_data[key]) > len(comp):
                            instance.raw_data[key] = instance.raw_data[key][:len(comp)]
                    
                    # Also fix field attribute if present
                    if hasattr(instance, 'field') and instance.field is not None and hasattr(instance.field, 'shape'):
                        if len(instance.field.shape) > 1 and instance.field.shape[0] > len(comp):
                            instance.field = instance.field[:len(comp), ...]
                    
                    modifications_made = True
                    break  # We've already fixed everything based on this component
        
        # After fixing individual components, check if named components need fixing
        component_names = ['br', 'bt', 'bn']  # Common names for mag data
        dt_len = len(instance.datetime_array)  # Get possibly updated length
        
        for name in component_names:
            if name in instance.raw_data and hasattr(instance.raw_data[name], '__len__'):
                if len(instance.raw_data[name]) != dt_len:
                    pm.warning(f"[SNAPSHOT] Fixing named component '{name}' length mismatch: {len(instance.raw_data[name])} != {dt_len}")
                    if len(instance.raw_data[name]) > dt_len:
                        instance.raw_data[name] = instance.raw_data[name][:dt_len]
                        modifications_made = True
        
        # Rebuild field array if components were modified
        if modifications_made and all(name in instance.raw_data for name in component_names):
            try:
                instance.field = np.column_stack([
                    instance.raw_data['br'],
                    instance.raw_data['bt'],
                    instance.raw_data['bn']
                ])
                pm.debug(f"[SNAPSHOT] Rebuilt field array with shape {instance.field.shape}")
            except Exception as e:
                pm.error(f"[SNAPSHOT] Failed to rebuild field array: {e}")
        
        return modifications_made
    
    # Standard case (direct array in 'all')
    elif hasattr(all_data, '__len__'):
        dt_len = len(instance.datetime_array)
        if len(all_data) != dt_len:
            pm.warning(f"[SNAPSHOT] Fixing raw_data['all'] length mismatch: {len(all_data)} != {dt_len}")
            # Choose which one to truncate
            if len(all_data) > dt_len:
                instance.raw_data['all'] = all_data[:dt_len]
            else:
                instance.datetime_array = instance.datetime_array[:len(all_data)]
                if hasattr(instance, 'time') and instance.time is not None:
                    instance.time = instance.time[:len(all_data)]
            return True
    
    return False

def save_data_snapshot(filename: Optional[str] = None, 
                       classes: Optional[List[Any]] = None, 
                       trange_list: Optional[List[List[str]]] = None, 
                       compression: str = "none", 
                       time_range: Optional[List[str]] = None, 
                       auto_split: bool = True) -> Optional[str]:
    """
    Save data class instances to a pickle file with optional time filtering and data population.
    Places file in 'data_snapshots/' directory.
    Generates intelligent filename if filename='auto'.

    Parameters
    ----------
    filename : str or 'auto', optional
        Desired filename (CAN include .pkl or compression extension, these will be handled).
        If 'auto' or None, a timestamped filename is generated.
        Path component: if filename includes 'data_snapshots/', it's used as is (minus extension for re-adding).
        Otherwise, it's treated as a base name to be placed in 'data_snapshots/'.
    classes : list of Plotbot data class instances, optional
        Specific global Plotbot class instances (e.g., [plotbot.mag_rtn, plotbot.proton]) to save.
        If None or empty, attempts to save all from data_cubby (behavior might need refinement for this case).
    trange_list : list of trange lists, optional
        If provided, the function will first call plotbot_get_data for each class in `classes`
        across each trange in `trange_list` to ensure data is loaded/updated before saving.
        Example: [[trange1_start, trange1_stop], [trange2_start, trange2_stop]]
    compression : str, optional
        Compression level: "none", "low", "medium", "high", or format ("gzip", "bz2", "lzma").
    time_range : list, optional
        Time range [start, end] to filter data by before saving. This filter applies *after* any
        data population from `trange_list`.
    auto_split : bool, optional
        Whether to automatically detect and split data segments at significant time gaps.
        Default is True.

    Returns
    -------
    Optional[str]
        The full path to the saved snapshot file if successful, otherwise None.
    """
    pm = print_manager

    # --- Informative Print about what will be processed ---
    if classes and trange_list:
        pm.status(f"[SNAPSHOT SAVE] Attempting to populate and save data for {len(classes)} class type(s) across {len(trange_list)} time range(s).")
        pm.status(f"[SNAPSHOT SAVE] Target classes: {[getattr(inst, 'data_type', type(inst).__name__) for inst in classes]}")
    elif classes:
        pm.status(f"[SNAPSHOT SAVE] Attempting to save pre-populated data for {len(classes)} class type(s): {[getattr(inst, 'data_type', type(inst).__name__) for inst in classes]}")
    # If only trange_list is given, the first validation handles it.
    # If neither is given, other warnings will apply.

    # --- INPUT VALIDATION --- 
    if trange_list and not classes:
        pm.error("[SNAPSHOT SAVE] 'trange_list' was provided, but no 'classes' were specified to populate. Cannot proceed.")
        return False
    # If classes is None or empty, and no trange_list to imply specific classes that will be populated.
    if not classes and not trange_list: # If no classes AND no trange_list to populate them, then nothing to do.
        pm.warning("[SNAPSHOT SAVE] No 'classes' specified and no 'trange_list' to populate. Nothing to save.")
        return False 
    if classes and not all(isinstance(c, object) for c in classes): # Basic check that classes are objects
        pm.error("[SNAPSHOT SAVE] 'classes' must be a list of Plotbot class instances. Cannot proceed.")
        return False
    if trange_list and not all(isinstance(tr, list) and len(tr) == 2 and all(isinstance(s, str) for s in tr) for tr in trange_list):
        pm.error("[SNAPSHOT SAVE] 'trange_list' must be a list of tranges (each trange being a list of two strings). Cannot proceed.")
        return False

    # --- Optional: Populate data --- 
    if trange_list and classes: # This outer check ensures both are provided and non-empty
        if not trange_list: 
             pm.warning("⚠️ [SNAPSHOT SAVE] 'trange_list' parameter is an empty list. Skipping data population.")
        elif not classes: 
             pm.warning("⚠️ [SNAPSHOT SAVE] 'classes' parameter is an empty list. Skipping data population.")
        else:
            pm.status(f"[SNAPSHOT SAVE] Initiating data population for {len(classes)} class type(s) across {len(trange_list)} time range(s)...")
            for data_class_instance in classes: 
                instance_name = type(data_class_instance).__name__
                descriptive_name = getattr(data_class_instance, 'data_type', instance_name)
                if not descriptive_name: descriptive_name = instance_name
                
                # STRATEGIC PRINT A
                dt_len_before_loop = len(data_class_instance.datetime_array) if hasattr(data_class_instance, 'datetime_array') and data_class_instance.datetime_array is not None else "None_or_NoAttr"
                pm.debug(f"[SAVE_SNAPSHOT_DEBUG A] Instance {descriptive_name} (ID: {id(data_class_instance)}) BEFORE trange loop. datetime_array len: {dt_len_before_loop}")

                # Create a fresh temporary instance to accumulate data from all tranges
                temp_instance = None
                try:
                    # Create an instance of the same class
                    temp_instance = type(data_class_instance)(None)  # Initialize with None (empty)
                    
                    # Initialize as empty if not already
                    if not hasattr(temp_instance, 'datetime_array') or temp_instance.datetime_array is None:
                        pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Temp instance initialized empty for accumulating all tranges.")
                except Exception as e_inst:
                    pm.error(f"[SAVE_SNAPSHOT_DEBUG] Could not create temporary instance for {descriptive_name}: {e_inst}. Falling back to in-place updates.")
                    temp_instance = None

                pm.status(f"  Populating/updating data for: {descriptive_name}")
                
                # Store data for each trange separately, then merge at the end
                trange_instances = []
                
                # Track overall min and max time across all tranges to ensure we preserve the full time span
                overall_min_time = None
                overall_max_time = None
                
                # Process data for each trange
                for t_range_idx, t_range in enumerate(trange_list): 
                    pm.status(f"    Processing trange: {t_range} for {descriptive_name}")
                    try:
                        # Create new instance for this trange
                        trange_instance = type(data_class_instance)(None)
                        plotbot_get_data(t_range, trange_instance)
                        
                        # If we got data, add this instance to our collection
                        if hasattr(trange_instance, 'datetime_array') and trange_instance.datetime_array is not None and len(trange_instance.datetime_array) > 0:
                            pm.debug(f"[SAVE_SNAPSHOT_DEBUG] trange {t_range_idx} ({t_range}) produced {len(trange_instance.datetime_array)} data points from {trange_instance.datetime_array[0]} to {trange_instance.datetime_array[-1]}")
                            # IMPORTANT: Make a deep copy to avoid shared references
                            trange_instances.append(copy.deepcopy(trange_instance))
                            
                            # Track overall time range
                            min_time = np.min(trange_instance.datetime_array)
                            max_time = np.max(trange_instance.datetime_array)
                            if overall_min_time is None or min_time < overall_min_time:
                                overall_min_time = min_time
                            if overall_max_time is None or max_time > overall_max_time:
                                overall_max_time = max_time
                        else:
                            pm.warning(f"[SAVE_SNAPSHOT_DEBUG] trange {t_range_idx} ({t_range}) produced no data points")
                    except Exception as e:
                        pm.error(f"    ⚠️ Error during plotbot_get_data for {descriptive_name} with trange {t_range}: {e}")
                
                # Now merge all the trange instances into one
                if len(trange_instances) > 0:
                    # CRITICAL FIX: We need to merge ALL tranges, not just use the last one
                    # First, ensure we have a place to merge into
                    if temp_instance is None:
                        temp_instance = copy.deepcopy(trange_instances[0])
                        pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Using first trange as base for merging. dt_len: {len(temp_instance.datetime_array)}")
                        
                        # If we only have one trange, we're already done
                        if len(trange_instances) == 1:
                            pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Only one trange, no merging needed.")
                        else:
                            # Merge any additional tranges
                            for i, trange_inst in enumerate(trange_instances[1:], 1):
                                pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Merging trange {i} with {len(trange_inst.datetime_array)} points into temp instance.")
                                
                                # Use data_cubby's merge logic which handles both time arrays and components
                                merged_data = data_cubby._merge_arrays(
                                    temp_instance.datetime_array, 
                                    trange_inst.datetime_array,
                                    temp_instance.raw_data, 
                                    trange_inst.raw_data
                                )
                                
                                if merged_data:
                                    merged_times, merged_raw_data = merged_data
                                    
                                    # Update the temp instance with merged data
                                    temp_instance.datetime_array = merged_times
                                    temp_instance.raw_data = merged_raw_data
                                    
                                    # Rebuild the time attribute (convert from datetime64 to int64)
                                    temp_instance.time = temp_instance.datetime_array.astype(np.int64)
                                    
                                    # Rebuild the field array if needed
                                    if hasattr(temp_instance, 'field') and 'all' in temp_instance.raw_data and isinstance(temp_instance.raw_data['all'], list) and len(temp_instance.raw_data['all']) > 0:
                                        components = temp_instance.raw_data['all']
                                        temp_instance.field = np.column_stack(components)
                                    
                                    pm.debug(f"[SAVE_SNAPSHOT_DEBUG] After merging trange {i}, temp instance has {len(temp_instance.datetime_array)} points.")
                                else:
                                    pm.error(f"[SAVE_SNAPSHOT_DEBUG] Failed to merge trange {i}.")
                    
                    # Ensure the temp instance is internally consistent
                    if hasattr(temp_instance, 'ensure_internal_consistency'):
                        temp_instance.ensure_internal_consistency()
                    
                    # Set any plot options that may be needed
                    if hasattr(temp_instance, 'set_ploptions'):
                        temp_instance.set_ploptions()
                    
                    # Stash the merged instance back to data_cubby
                    pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Stashing merged instance back to data_cubby with key {data_type_str}")
                    data_cubby.stash(temp_instance, class_name=descriptive_name)
                    
                    # Refresh the reference to match the one in the cubby
                    data_class_instance = data_cubby.grab(data_type_str)
                    pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Refreshing data_class_instance for {data_type_str} (Old ID: {id(mag_4sa_test_instance)}) with cubby instance (New ID: {id(data_class_instance)}) for key {data_type_str}.")
                
                # Update data_class_instance with the merged result
                if hasattr(temp_instance, 'datetime_array') and temp_instance.datetime_array is not None:
                    pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Final merged instance has {len(temp_instance.datetime_array)} points covering all tranges. Min: {temp_instance.datetime_array[0]}, Max: {temp_instance.datetime_array[-1]}")
                    
                    # Copy the merged instance to the original class instance
                    if hasattr(data_class_instance, 'restore_from_snapshot'):
                        data_class_instance.restore_from_snapshot(temp_instance)
                    else:
                        # Manual copy of critical attributes
                        for attr in ['datetime_array', 'time', 'raw_data', 'field']:
                            if hasattr(temp_instance, attr):
                                setattr(data_class_instance, attr, copy.deepcopy(getattr(temp_instance, attr)))
                    
                    # Log the final state we achieved
                    if hasattr(data_class_instance, 'datetime_array') and data_class_instance.datetime_array is not None:
                        pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Successfully updated data_class_instance with {len(data_class_instance.datetime_array)} points")
                else:
                    pm.warning(f"[SAVE_SNAPSHOT_DEBUG] Merged instance has no datetime_array. Nothing to update.")

                dt_len_after_loop = len(data_class_instance.datetime_array) if hasattr(data_class_instance, 'datetime_array') and data_class_instance.datetime_array is not None else "None_or_NoAttr"
                pm.debug(f"[SAVE_SNAPSHOT_DEBUG C] Instance {descriptive_name} (ID: {id(data_class_instance)}) AFTER trange loop (and potential refresh). datetime_array len: {dt_len_after_loop}")

            pm.status("[SNAPSHOT SAVE] Data population phase complete.")
    elif trange_list and not classes: 
        pm.warning("[SNAPSHOT SAVE] 'trange_list' was provided, but no 'classes' were specified to populate. Skipping population (this should have been caught by validation).")

    effective_classes_to_save = classes if classes else []

    if not effective_classes_to_save:
        # This case should ideally be caught by earlier validation if classes was None and trange_list was also None.
        pm.warning("[SNAPSHOT SAVE] No effective classes to process for snapshot after population/initial checks. Nothing to save.")
        return False

    # --- Build the initial data_snapshot from effective_classes_to_save ---
    data_snapshot = {} 
    for original_instance_ref in effective_classes_to_save: # Iterate over original references
        # Determine a name/key for the instance in the snapshot dictionary
        # Grab the potentially updated instance from the cubby using its data_type or class_name
        instance_key_attr = getattr(original_instance_ref, 'data_type', None)
        if not instance_key_attr:
            instance_key_attr = getattr(original_instance_ref, 'class_name', type(original_instance_ref).__name__.lower())
        
        instance = data_cubby.grab(instance_key_attr) # Fetch the latest from cubby
        
        if instance is None: # If grab failed, fall back to the original reference (though it might be stale)
            pm.warning(f"[SAVE_SNAPSHOT_DEBUG] Could not grab instance for key '{instance_key_attr}' from cubby. Using original reference for snapshot.")
            instance = original_instance_ref 
            instance_key_final = instance_key_attr # Use the key we tried to grab with
        else:
            # Use the data_type of the grabbed instance as the primary key, fallback to class_name
            instance_key_final = getattr(instance, 'data_type', None)
            if not instance_key_final: instance_key_final = getattr(instance, 'class_name', type(instance).__name__.lower())

        dt_len_for_snapshot = len(instance.datetime_array) if hasattr(instance, 'datetime_array') and instance.datetime_array is not None else "None_or_NoAttr"
        pm.debug(f"[SAVE_SNAPSHOT_DEBUG] Preparing to add instance for key '{instance_key_final}' (ID: {id(instance)}) to data_snapshot. datetime_array len: {dt_len_for_snapshot}")

        if instance is None or _is_data_object_empty(instance):
            pm.status(f"[SNAPSHOT SAVE] Instance for key '{instance_key_final}' is empty or None. Skipping from initial snapshot build.")
            continue
            
        data_snapshot[instance_key_final] = instance 

    # --- Now, the filtering/segmentation logic using the populated `data_snapshot` --- 
    processed_snapshot = {} 
    final_loaded_classes_details = [] 

    time_filter_for_snapshot = None
    if time_range is not None:
        try:
            filter_start = dateutil_parse(time_range[0]) 
            filter_end = dateutil_parse(time_range[1])
            time_filter_for_snapshot = (filter_start, filter_end)
            pm.status(f"[SNAPSHOT SAVE] Applying final filter to time range: {filter_start} to {filter_end}")
        except Exception as e:
            pm.warning(f"[SNAPSHOT SAVE] Could not parse time_range {time_range} for filtering: {e}. No final filtering.")

    if not data_snapshot: # Check if data_snapshot is empty AFTER trying to build it
        pm.warning("[SNAPSHOT SAVE] Initial data_snapshot is empty (no valid classes/instances found or all were empty). Nothing to process.")
    else:
        for key, instance_to_process in data_snapshot.items():
            # STRATEGIC PRINT D
            dt_len_instance_to_process = len(instance_to_process.datetime_array) if hasattr(instance_to_process, 'datetime_array') and instance_to_process.datetime_array is not None else "None_or_NoAttr"
            pm.debug(f"[SAVE_SNAPSHOT_DEBUG D] Instance for key '{key}' (ID: {id(instance_to_process)}) BEFORE segmentation/filtering. datetime_array len: {dt_len_instance_to_process}")

            if _is_data_object_empty(instance_to_process):
                pm.status(f"[SNAPSHOT SAVE] Instance for {key} is empty before final processing. Skipping.")
                continue

            # === Call ensure_internal_consistency before further processing ===
            if hasattr(instance_to_process, 'ensure_internal_consistency'):
                pm.status(f"[SNAPSHOT SAVE] Ensuring internal consistency for {key}...")
                try:
                    instance_to_process.ensure_internal_consistency()
                    pm.status(f"[SNAPSHOT SAVE] Consistency check complete for {key}.")
                except Exception as e_consistency:
                    pm.error(f"[SNAPSHOT SAVE] Error during ensure_internal_consistency for {key}: {e_consistency}. Proceeding with potentially inconsistent data.")
            # === End call ===
            
            # === Additional component consistency checking ===
            try:
                if _ensure_component_consistency(instance_to_process):
                    pm.status(f"[SNAPSHOT SAVE] Fixed component length inconsistencies for {key}.")
            except Exception as e_comp_fix:
                pm.error(f"[SNAPSHOT SAVE] Error during component consistency fixing for {key}: {e_comp_fix}. Proceeding with potentially inconsistent data.")
            # === End additional check ===
            
            current_instance_for_saving = instance_to_process

            # === GOLD PRINTS for save_data_snapshot ===
            print_manager.debug(f"[GOLD_SNAPSHOT_PRE_SEGMENT ID:{id(current_instance_for_saving)}] About to process instance for key '{key}' (Type: {type(current_instance_for_saving).__name__})")
            dt_array_len_snap = len(current_instance_for_saving.datetime_array) if hasattr(current_instance_for_saving, 'datetime_array') and current_instance_for_saving.datetime_array is not None else 'NoneType_or_NoAttr'
            time_len_snap = len(current_instance_for_saving.time) if hasattr(current_instance_for_saving, 'time') and current_instance_for_saving.time is not None else 'NoneType_or_NoAttr'
            field_shape_snap = current_instance_for_saving.field.shape if hasattr(current_instance_for_saving, 'field') and current_instance_for_saving.field is not None else 'NoneType_or_NoAttr'
            print_manager.debug(f"    datetime_array len: {dt_array_len_snap}")
            print_manager.debug(f"    time len: {time_len_snap}")
            print_manager.debug(f"    field shape: {field_shape_snap}")
            # === END GOLD PRINTS ===

            original_len = len(getattr(current_instance_for_saving, 'datetime_array', []))

            segments = []
            if time_filter_for_snapshot:
                if auto_split:
                    segments = _identify_data_segments(current_instance_for_saving, time_filter_for_snapshot)
                
                if not segments: 
                    current_instance_for_saving = _create_filtered_instance(current_instance_for_saving, time_filter_for_snapshot[0], time_filter_for_snapshot[1])
                    if _is_data_object_empty(current_instance_for_saving):
                        pm.warning(f"[SNAPSHOT SAVE] Filtered instance for {key} is empty. Skipping.")
                        continue
                    processed_snapshot[key] = current_instance_for_saving
                    final_loaded_classes_details.append((key, current_instance_for_saving))
                    # ... (status print for filtered len) ...
                else: 
                    # ... (handle segments as in your original function, populating processed_snapshot and final_loaded_classes_details) ...
                    pm.status(f"[SNAPSHOT SAVE] Found {len(segments)} distinct time segments for {key} after filtering.")
                    # (This loop needs to correctly add to processed_snapshot and final_loaded_classes_details)
                    segment_metadata = {"original_class": key, "segments": len(segments), "segment_ranges": []}
                    for i, segment in enumerate(segments):
                        segment_name = f"{key}_segment_{i+1}"
                        processed_snapshot[segment_name] = segment
                        final_loaded_classes_details.append((segment_name, segment))
                        # ... collect segment metadata ...
                    processed_snapshot[f"{key}_segments_meta"] = segment_metadata

            else: # No time_range filter, process original (or populated) instance
                if auto_split:
                    segments = _identify_data_segments(current_instance_for_saving)
                if not segments:
                    processed_snapshot[key] = current_instance_for_saving
                    final_loaded_classes_details.append((key, current_instance_for_saving))
                else:
                    # ... (handle segmentation without prior time_range filter, similar to above) ...
                    pm.status(f"[SNAPSHOT SAVE] Found {len(segments)} distinct time segments for {key} (no time_range filter).")
                    segment_metadata = {"original_class": key, "segments": len(segments), "segment_ranges": []} # Example
                    for i, segment in enumerate(segments):
                        segment_name = f"{key}_segment_{i+1}"
                        processed_snapshot[segment_name] = segment
                        final_loaded_classes_details.append((segment_name, segment))
                        # ... collect segment metadata ...
                    processed_snapshot[f"{key}_segments_meta"] = segment_metadata

    # This is where your actual saving logic (auto-filename, compression, pickling of processed_snapshot) exists.
    final_filepath = None
    # Check if there is anything in processed_snapshot to save
    if not processed_snapshot:
         pm.warning("[SNAPSHOT SAVE] No data was processed to be included in the snapshot after filtering/segmentation. File not saved.")
         final_filepath = None # Ensure final_filepath is None if nothing to save
    else:
        output_dir = "data_snapshots"
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine the base name (without extension) and the directory to save in.
        _name_to_use_for_file = ""
        _dir_to_save_in = output_dir

        if filename == 'auto' or filename is None:
            _timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            _vars_str = 'data'
            if final_loaded_classes_details: # Preferred source for naming
                 _vars_str = '+'.join(sorted(list(set(type(inst).__name__ for name, inst in final_loaded_classes_details))))
            elif classes: # Fallback
                 _vars_str = '+'.join(sorted(list(set(type(inst).__name__ for inst in classes))))
            _name_to_use_for_file = f"snapshot_{_timestamp}_{_vars_str}"
            # _dir_to_save_in is already output_dir
        elif filename.startswith(output_dir + os.sep):
            # Filename already contains "data_snapshots/" prefix.
            _dir_to_save_in = os.path.dirname(filename) # This should effectively be output_dir or a subdir within it
            _name_to_use_for_file = os.path.basename(filename)
        else:
            # Filename is just a base name, or a name with extension.
            _name_to_use_for_file = filename
            # _dir_to_save_in is already output_dir

        # Strip known extensions from _name_to_use_for_file to get a clean base.
        # Handles .pkl, .pkl.gz, .pkl.bz2, .pkl.xz
        for ext_to_strip in [".pkl.gz", ".pkl.bz2", ".pkl.xz", ".pkl"]:
            if _name_to_use_for_file.lower().endswith(ext_to_strip):
                _name_to_use_for_file = _name_to_use_for_file[:-len(ext_to_strip)]
                break
        
        # _name_to_use_for_file is now the clean base name.
        # _dir_to_save_in is the directory (e.g., "data_snapshots")

        # Add compression extension (this part of logic was mostly fine)
        compression_ext_map = {"gzip": ".pkl.gz", "bz2": ".pkl.bz2", "lzma": ".pkl.xz", "none": ".pkl"}
        selected_compression_format = compression.lower()
        if selected_compression_format not in ["low", "medium", "high"] and selected_compression_format not in compression_ext_map:
            pm.warning(f"[SNAPSHOT SAVE] Unknown compression format '{compression}'. Using no compression.")
            selected_compression_format = "none"

        actual_compression_format = selected_compression_format
        compress_level = None 
        lzma_preset = None    

        if selected_compression_format == "low": actual_compression_format = "gzip"; compress_level = 1
        elif selected_compression_format == "medium": actual_compression_format = "gzip"; compress_level = 5
        elif selected_compression_format == "high": actual_compression_format = "lzma"; lzma_preset = 9
        
        _final_filename_ext_to_add = compression_ext_map.get(actual_compression_format, ".pkl")
        
        final_filepath = os.path.join(_dir_to_save_in, _name_to_use_for_file + _final_filename_ext_to_add)
        # Example: path = "data_snapshots", name = "my_snap", ext = ".pkl.gz" -> "data_snapshots/my_snap.pkl.gz"
        # Example: path = "data_snapshots", name from input "data_snapshots/test_advanced_snapshot_mag_rtn_4sa" (after stripping), ext = ".pkl"
        #          _dir_to_save_in becomes "data_snapshots"
        #          _name_to_use_for_file becomes "test_advanced_snapshot_mag_rtn_4sa"
        #          final_filepath = "data_snapshots/test_advanced_snapshot_mag_rtn_4sa.pkl" - CORRECT!

        try:
            if actual_compression_format == "gzip":
                import gzip
                with gzip.open(final_filepath, 'wb', compresslevel=compress_level if compress_level else 5) as f:
                    pickle.dump(processed_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            elif actual_compression_format == "bz2":
                import bz2
                with bz2.open(final_filepath, 'wb', compresslevel=compress_level if compress_level else 9) as f:
                    pickle.dump(processed_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            elif actual_compression_format == "lzma":
                import lzma
                with lzma.open(final_filepath, 'wb', preset=lzma_preset) as f:
                    pickle.dump(processed_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            else: # "none"
                with open(final_filepath, 'wb') as f:
                    pickle.dump(processed_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            pm.status(f"[SNAPSHOT SAVE] Successfully pickled data to {final_filepath}")
        except Exception as e_pickle:
            pm.error(f"[SNAPSHOT SAVE] Error during pickling process: {e_pickle}")
            final_filepath = None 
            return False
    
    # --- Explicit check if file exists after trying to save ---
    if final_filepath and not os.path.exists(final_filepath):
        pm.error(f"[SNAPSHOT SAVE CRITICAL] File was supposed to be saved to {final_filepath} but it does NOT exist on disk immediately after saving!")
        # Even if we thought it was a success, if the file isn't there, it's a failure.
        return False 

    # --- Final Status Print --- 
    if final_filepath:
        # STRATEGIC PRINT: Check cubby state right before returning from save_data_snapshot
        pm.debug("\n[SAVE_SNAPSHOT_DEBUG FINAL_CUBBY_CHECK]")
        if classes:
            for inst_class_ref in classes: # Iterate over the original class instances passed in
                key_to_check = getattr(inst_class_ref, 'data_type', None)
                if not key_to_check: key_to_check = getattr(inst_class_ref, 'class_name', type(inst_class_ref).__name__.lower())
                
                cubby_instance = data_cubby.grab(key_to_check)
                if cubby_instance:
                    dt_len_final_cubby = len(cubby_instance.datetime_array) if hasattr(cubby_instance, 'datetime_array') and cubby_instance.datetime_array is not None else "None_or_NoAttr"
                    min_dt_final_cubby = cubby_instance.datetime_array[0] if dt_len_final_cubby not in ["None_or_NoAttr", 0] else "N/A"
                    max_dt_final_cubby = cubby_instance.datetime_array[-1] if dt_len_final_cubby not in ["None_or_NoAttr", 0] else "N/A"
                    pm.debug(f"  Cubby Key: '{key_to_check}', Instance ID: {id(cubby_instance)}, dt_len: {dt_len_final_cubby}, min: {min_dt_final_cubby}, max: {max_dt_final_cubby}")
                    if inst_class_ref is not cubby_instance:
                        pm.warning(f"    Original instance (ID: {id(inst_class_ref)}) is different from cubby instance (ID: {id(cubby_instance)}) at save_data_snapshot exit.")
                else:
                    pm.debug(f"  Cubby Key: '{key_to_check}' not found in cubby at save_data_snapshot exit.")
        # --- END STRATEGIC PRINT ---

        pm.status(f"✅ SNAPSHOT CREATED: {final_filepath}") # Unified success message
        # Add more details from your original summary if desired, e.g., number of classes/tranges
        if classes: pm.status(f"   Included data for types: {[type(inst).__name__ for inst in classes]}")
        if trange_list: pm.status(f"   Processed {len(trange_list)} time range(s).")
        return True # Return True if final_filepath is not None
    else:
        pm.error("⚠️ SNAPSHOT CREATION FAILED or nothing to save (check logs above for specific errors).") # Unified failure message
        return False # Return False if final_filepath is None

def load_data_snapshot(filename, classes=None, merge_segments=True):
    print("DEBUG_LOAD_SNAPSHOT: Entered function load_data_snapshot") # DBG
    pm = print_manager
    # --- Adjust filename to check data_snapshots/ directory ---
    if not os.path.isabs(filename) and not filename.startswith('data_snapshots/'):
        filepath = os.path.join('data_snapshots', filename)
        if not os.path.exists(filepath) and os.path.exists(filename):
             filepath = filename
             print_manager.warning(f"Snapshot found in root ({filename}), not in data_snapshots/. Using root path.")
        elif not os.path.exists(filepath):
             print_manager.error(f"Snapshot file not found in data_snapshots/ or root: {filename}")
             print("DEBUG_LOAD_SNAPSHOT: Returning False - file not found in data_snapshots/ or root") # DBG
             return False
    else:
        filepath = filename
        if not os.path.exists(filepath):
             print_manager.error(f"Snapshot file not found: {filepath}")
             print("DEBUG_LOAD_SNAPSHOT: Returning False - file not found (abs path check)") # DBG
             return False
    # --- End path adjustment ---

    print_manager.data_snapshot(f"Starting load from {filepath}")
    try:
        # Auto-detect compression format based on file extension
        base, ext = os.path.splitext(filepath)
        compression_ext = ext.lower()
        # Handle double extensions like .pkl.gz
        if compression_ext in ['.gz', '.bz2', '.xz']:
             base, ext = os.path.splitext(base) # Get the .pkl part
        # Now ext should be .pkl or similar

        print_manager.data_snapshot(f"Detected compression extension: {compression_ext}")
        if compression_ext == ".gz":
            import gzip
            print_manager.data_snapshot("Using gzip compression")
            with gzip.open(filepath, 'rb') as f:
                data_snapshot = pickle.load(f)
            compression_used = "gzip"
        elif compression_ext == ".bz2":
            import bz2
            print_manager.data_snapshot("Using bz2 compression")
            with bz2.open(filepath, 'rb') as f:
                data_snapshot = pickle.load(f)
            compression_used = "bz2"
        elif compression_ext == ".xz":
            import lzma
            print_manager.data_snapshot("Using lzma compression")
            with lzma.open(filepath, 'rb') as f:
                data_snapshot = pickle.load(f)
            compression_used = "lzma"
        else: # Assume no compression or just .pkl
            print_manager.data_snapshot("Using no compression")
            with open(filepath, 'rb') as f:
                data_snapshot = pickle.load(f)
            compression_used = "none"
        print_manager.data_snapshot(f"Data snapshot loaded from file. Keys: {list(data_snapshot.keys())}")
        
        if classes is not None:
            pm.data_snapshot(f"Filtering snapshot based on requested classes: {classes}")
            if not isinstance(classes, list):
                classes = [classes]
            
            target_data_type_strings = []
            for cls_item in classes:
                if isinstance(cls_item, str):
                    # Assume it's already a data_type string like 'mag_RTN_4sa'
                    target_data_type_strings.append(cls_item)
                elif hasattr(cls_item, 'data_type') and isinstance(getattr(cls_item, 'data_type'), str):
                    # It's an instance, get its .data_type attribute
                    target_data_type_strings.append(cls_item.data_type)
                elif isinstance(cls_item, type):
                    # It's a class type. Try to instantiate it to get its default data_type.
                    # This assumes __init__(None) is safe and sets up .data_type.
                    try:
                        temp_instance = cls_item(None)
                        if hasattr(temp_instance, 'data_type') and isinstance(getattr(temp_instance, 'data_type'), str):
                            target_data_type_strings.append(temp_instance.data_type)
                        else:
                            pm.warning(f"Could not determine data_type from class type {cls_item.__name__}, falling back to class name.")
                            target_data_type_strings.append(cls_item.__name__)
                    except Exception as e_inst:
                        pm.warning(f"Error instantiating {cls_item.__name__} to get data_type: {e_inst}. Falling back to class name.")
                        target_data_type_strings.append(cls_item.__name__)
                else:
                    pm.warning(f"Unrecognized item in classes list: {cls_item}. Attempting to use its string representation or class name.")
                    try:
                        target_data_type_strings.append(str(cls_item) if not hasattr(cls_item, '__name__') else cls_item.__name__)
                    except:
                        pass # Skip if cannot convert
            
            # Remove duplicates and ensure all are strings
            target_data_type_strings = sorted(list(set(filter(None, target_data_type_strings))))
            pm.data_snapshot(f"Processed target data_type strings for filtering: {target_data_type_strings}")
            
            filtered_snapshot = {}
            if not target_data_type_strings: # If no valid target types determined, maybe load all or none?
                pm.warning("No valid target data_type strings derived from 'classes' argument. Will attempt to load all keys from snapshot or matching segment base names.")
                # To be safe, if classes was specified but resulted in no targets, perhaps load nothing from segments?
                # For now, if target_data_type_strings is empty due to bad input, this loop won't add anything.

            for key_in_snapshot, value_in_snapshot in data_snapshot.items():
                load_this_key = False
                if not target_data_type_strings: # If classes arg was None or yielded no targets, consider all keys
                    load_this_key = True 
                elif key_in_snapshot in target_data_type_strings:
                    load_this_key = True
                elif '_segment_' in key_in_snapshot and key_in_snapshot.split('_segment_')[0] in target_data_type_strings:
                    load_this_key = True
                elif key_in_snapshot.endswith('_segments_meta') and key_in_snapshot.split('_segments_meta')[0] in target_data_type_strings:
                    load_this_key = True
                
                if load_this_key:
                    filtered_snapshot[key_in_snapshot] = value_in_snapshot
            
            data_snapshot = filtered_snapshot # Replace with the filtered version
            pm.data_snapshot(f"Filtered snapshot keys based on 'classes' argument: {list(data_snapshot.keys())}")
        else:
            pm.data_snapshot("No 'classes' filter provided. Loading all data from snapshot.")

        # --- Process and load segments ---
        segment_groups = {}
        regular_classes_keys = [] 
        if not data_snapshot: # If filtering resulted in an empty snapshot
            pm.warning("Snapshot is empty after filtering by 'classes'. Nothing to load.")
        else:
            for key_in_snapshot in data_snapshot.keys():
                if '_segment_' in key_in_snapshot and not key_in_snapshot.endswith('_segments_meta'):
                    base_class_name = key_in_snapshot.split('_segment_')[0]
                    try:
                        segment_id = int(key_in_snapshot.split('_segment_')[1])
                        if base_class_name not in segment_groups:
                            segment_groups[base_class_name] = []
                        segment_groups[base_class_name].append((segment_id, key_in_snapshot))
                    except ValueError:
                        pm.warning(f"Could not parse segment ID from key: {key_in_snapshot}. Skipping.")
                elif not key_in_snapshot.endswith('_segments_meta'):
                    regular_classes_keys.append(key_in_snapshot)
            
            restored_ranges = {}

            # Process regular (non-segmented) classes first
            for class_key in regular_classes_keys:
                instance_from_snapshot = data_snapshot[class_key]
                if _is_data_object_empty(instance_from_snapshot):
                    pm.data_snapshot(f"Skipping {class_key} (empty in snapshot)")
                    continue
            # Convert class objects to class names
            class_names = []
            for cls in classes:
                if isinstance(cls, str):
                    class_names.append(cls)
                elif hasattr(cls, '__name__'):
                    class_names.append(cls.__name__)
                else:
                    class_names.append(cls.__class__.__name__)
            print_manager.data_snapshot(f"Class names after conversion: {class_names}")
            
            # Build filtered snapshot - include requested classes plus their segments if any
            filtered_snapshot = {}
            for key, value in data_snapshot.items():
                # Check if this is a regular class that was requested
                if key in class_names:
                    filtered_snapshot[key] = value
                # Check if this is a segment of a requested class
                elif '_segment_' in key and key.split('_segment_')[0] in class_names:
                    if merge_segments:
                        # When merging, we'll handle these separately
                        filtered_snapshot[key] = value
                # Check if this is segment metadata for a requested class
                elif key.endswith('_segments_meta') and key.split('_segments_meta')[0] in class_names:
                    filtered_snapshot[key] = value
                
            data_snapshot = filtered_snapshot
            print_manager.data_snapshot(f"Filtered keys: {list(data_snapshot.keys())}")
        
        # --- Process and load segments ---
        segment_groups = {}
        regular_classes_keys = [] # keys for non-segmented items in snapshot
        for key_in_snapshot in data_snapshot.keys():
            if '_segment_' in key_in_snapshot and not key_in_snapshot.endswith('_segments_meta'):
                base_class_name = key_in_snapshot.split('_segment_')[0]
                try:
                    segment_id = int(key_in_snapshot.split('_segment_')[1])
                    if base_class_name not in segment_groups:
                        segment_groups[base_class_name] = []
                    segment_groups[base_class_name].append((segment_id, key_in_snapshot))
                except ValueError:
                    pm.warning(f"Could not parse segment ID from key: {key_in_snapshot}. Skipping.")
            elif not key_in_snapshot.endswith('_segments_meta'):
                regular_classes_keys.append(key_in_snapshot)
        
        restored_ranges = {}

        # Process regular (non-segmented) classes first
        for class_key in regular_classes_keys:
            instance_from_snapshot = data_snapshot[class_key]
            if _is_data_object_empty(instance_from_snapshot):
                pm.data_snapshot(f"Skipping {class_key} (empty in snapshot)")
                continue
            pm.data_snapshot(f"Processing regular class: {class_key} from snapshot (type: {type(instance_from_snapshot)})")
            global_instance = data_cubby.grab(class_key) # Check if global instance exists
            if global_instance is None: # If not, create and stash
                TargetClass = data_cubby._get_class_type_from_string(class_key)
                if TargetClass:
                    global_instance = TargetClass(None)
                    data_cubby.stash(global_instance, class_name=class_key)
                    global_instance = data_cubby.grab(class_key) # Re-grab
                else:
                    pm.warning(f"Could not determine class type for {class_key}. Skipping restore.")
                    continue
            
            if hasattr(global_instance, 'restore_from_snapshot'):
                try:
                    global_instance.restore_from_snapshot(instance_from_snapshot)
                    pm.data_snapshot(f"  Restored {class_key} using restore_from_snapshot.")
                    if hasattr(global_instance, 'ensure_internal_consistency'): global_instance.ensure_internal_consistency()
                    if hasattr(global_instance, 'set_ploptions'): global_instance.set_ploptions()
                except Exception as e_restore:
                    pm.error(f"  Error during restore_from_snapshot for {class_key}: {e_restore}. Stashing directly.")
                    data_cubby.stash(instance_from_snapshot, class_name=class_key) # Stash the loaded one directly
            else:
                pm.data_snapshot(f"  {class_key} has no restore_from_snapshot. Stashing directly.")
                data_cubby.stash(instance_from_snapshot, class_name=class_key) # Stash the loaded one directly
            # ... (logic to update restored_ranges for regular_classes - simplified here) ...

        # Now process segment groups if merge_segments is True
        if merge_segments and segment_groups:
            pm.data_snapshot(f"Processing {len(segment_groups)} segment groups for merging...")
            for base_class_name, segments_info in segment_groups.items():
                pm.data_snapshot(f"  Merging segments for {base_class_name} ({len(segments_info)} segments)")
                # Critical fix: Sort segments by ID to ensure segments are processed in order
                sorted_segments_info = sorted(segments_info, key=lambda x: x[0])
                
                # Track the overall time range for the reconstructed instance
                overall_min_time = None
                overall_max_time = None
                
                global_instance = data_cubby.grab(base_class_name)
                if global_instance is None: # Create if doesn't exist
                    TargetClass = data_cubby._get_class_type_from_string(base_class_name)
                    if TargetClass:
                        global_instance = TargetClass(None) 
                        data_cubby.stash(global_instance, class_name=base_class_name)
                        # global_instance = data_cubby.grab(base_class_name) # Not needed, stash returns the stashed obj or use directly
                    else:
                        pm.warning(f"    Could not determine class type for {base_class_name}. Skipping segments.")
                        continue
                
                # Collect all segments first - important to process them all together
                segments_to_merge = []
                for segment_id, segment_key_in_snapshot in sorted_segments_info:
                    instance_from_segment_snapshot = data_snapshot[segment_key_in_snapshot]
                    if _is_data_object_empty(instance_from_segment_snapshot):
                        pm.data_snapshot(f"    Skipping {segment_key_in_snapshot} (empty in snapshot)")
                        continue
                    
                    # Update time range tracking
                    if hasattr(instance_from_segment_snapshot, 'datetime_array') and \
                       instance_from_segment_snapshot.datetime_array is not None and \
                       len(instance_from_segment_snapshot.datetime_array) > 0:
                        segment_min_dt = np.min(instance_from_segment_snapshot.datetime_array)
                        segment_max_dt = np.max(instance_from_segment_snapshot.datetime_array)
                        
                        # Update overall range
                        if overall_min_time is None or segment_min_dt < overall_min_time:
                            overall_min_time = segment_min_dt
                        if overall_max_time is None or segment_max_dt > overall_max_time:
                            overall_max_time = segment_max_dt
                        
                        # Log segment range
                        pm.debug(f"    Segment {segment_id} time range: {segment_min_dt} to {segment_max_dt}")
                    
                    segments_to_merge.append(instance_from_segment_snapshot)
                    pm.data_snapshot(f"    Queued segment {segment_id} ({segment_key_in_snapshot}) for merging")
                
                if not segments_to_merge:
                    pm.warning(f"    No valid segments found for {base_class_name}. Skipping merge.")
                    continue
                
                # Now merge all segments at once to preserve the complete time range
                merged_instance = segments_to_merge[0]
                if len(segments_to_merge) > 1:
                    try:
                        pm.data_snapshot(f"    Performing full merge of {len(segments_to_merge)} segments for {base_class_name}")
                        
                        # Collect all datetime arrays, time arrays, and component data
                        all_datetime_arrays = []
                        all_time_arrays = []
                        component_data = {}
                        
                        for segment in segments_to_merge:
                            if hasattr(segment, 'datetime_array') and segment.datetime_array is not None:
                                all_datetime_arrays.append(segment.datetime_array)
                            
                            if hasattr(segment, 'time') and segment.time is not None:
                                all_time_arrays.append(segment.time)
                            
                            if hasattr(segment, 'raw_data') and segment.raw_data is not None:
                                for key, value in segment.raw_data.items():
                                    if key not in component_data:
                                        component_data[key] = []
                                    
                                    if key == 'all' and isinstance(value, list):
                                        # Handle 'all' specially since it's a list of component arrays
                                        if len(component_data[key]) == 0:
                                            component_data[key] = [[] for _ in range(len(value))]
                                        
                                        for i, comp in enumerate(value):
                                            component_data[key][i].append(comp)
                                    else:
                                        component_data[key].append(value)
                        
                        # Create a new merged instance
                        merged_instance = type(segments_to_merge[0])(None)
                        
                        # Merge datetime arrays
                        if all_datetime_arrays:
                            combined_dt = np.concatenate(all_datetime_arrays)
                            sort_indices = np.argsort(combined_dt)
                            sorted_dt = combined_dt[sort_indices]
                            # Remove duplicates but maintain order
                            _, unique_indices = np.unique(sorted_dt, return_index=True)
                            unique_indices = np.sort(unique_indices)
                            merged_instance.datetime_array = sorted_dt[unique_indices]
                            
                            pm.data_snapshot(f"    Merged datetime_array has {len(merged_instance.datetime_array)} points from {merged_instance.datetime_array[0]} to {merged_instance.datetime_array[-1]}")
                        
                        # Merge time arrays
                        if all_time_arrays:
                            combined_time = np.concatenate(all_time_arrays)
                            # Use same sort indices and unique indices from datetime array
                            merged_instance.time = combined_time[sort_indices][unique_indices]
                        
                        # Merge component data
                        merged_instance.raw_data = {}
                        for key, arrays in component_data.items():
                            if key == 'all':
                                # Handle 'all' specially
                                merged_instance.raw_data[key] = []
                                for comp_arrays in arrays:
                                    if comp_arrays:
                                        combined_comp = np.concatenate(comp_arrays)
                                        merged_instance.raw_data[key].append(combined_comp[sort_indices][unique_indices])
                            elif arrays:
                                # Standard array merge
                                try:
                                    combined_array = np.concatenate(arrays)
                                    merged_instance.raw_data[key] = combined_array[sort_indices][unique_indices]
                                except Exception as e_arr:
                                    pm.warning(f"      Error merging arrays for key {key}: {e_arr}")
                        
                        # Reconstruct field array if needed
                        if 'all' in merged_instance.raw_data and merged_instance.raw_data['all']:
                            try:
                                merged_instance.field = np.column_stack(merged_instance.raw_data['all'])
                                pm.data_snapshot(f"    Reconstructed field array with shape {merged_instance.field.shape}")
                            except Exception as e_field:
                                pm.warning(f"      Error reconstructing field array: {e_field}")
                        
                        # Call ensure_internal_consistency if available
                        if hasattr(merged_instance, 'ensure_internal_consistency'):
                            merged_instance.ensure_internal_consistency()
                        
                        # Set plot options if available
                        if hasattr(merged_instance, 'set_ploptions'):
                            merged_instance.set_ploptions()
                            
                    except Exception as e_merge:
                        pm.error(f"    Failed to merge segments for {base_class_name}: {e_merge}")
                
                # Restore the merged data to the global instance
                if hasattr(global_instance, 'restore_from_snapshot'):
                    global_instance.restore_from_snapshot(merged_instance)
                else:
                    # Manual copy of critical attributes
                    for attr in ['datetime_array', 'time', 'raw_data', 'field']:
                        if hasattr(merged_instance, attr):
                            setattr(global_instance, attr, copy.deepcopy(getattr(merged_instance, attr)))
                
                # Final consistency check
                if hasattr(global_instance, 'ensure_internal_consistency'):
                    global_instance.ensure_internal_consistency()
                
                # Set plot options
                if hasattr(global_instance, 'set_ploptions'):
                    global_instance.set_ploptions()
                
                # Special handling for tracker consistency 
                tracker_range = _ensure_tracker_consistency(base_class_name, global_instance)
                if tracker_range:
                    restored_ranges[base_class_name.lower()] = tracker_range
                    pm.debug(f"    LOAD_SNAPSHOT_DEBUG: Using unified tracker range for '{base_class_name.lower()}'")
                
                # After processing all segments for this base_class, check time range consistency with the tracker
                _ensure_tracker_time_ranges_during_load(base_class_name, global_instance, restored_ranges)
                
                # Verify time range
                if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None:
                    actual_min = np.min(global_instance.datetime_array)
                    actual_max = np.max(global_instance.datetime_array)
                    
                    pm.data_snapshot(f"    Time range check for {base_class_name}:")
                    pm.data_snapshot(f"      Expected: {overall_min_time} to {overall_max_time}")
                    pm.data_snapshot(f"      Actual: {actual_min} to {actual_max}")
                    
                    # Check if there's a mismatch and log warning
                    if actual_min != overall_min_time or actual_max != overall_max_time:
                        pm.warning(f"    Time range mismatch after segment merge! Expected {overall_min_time} to {overall_max_time}, got {actual_min} to {actual_max}")
                
                # Update the restored_ranges dictionary with the overall merged range
                if overall_min_time is not None and overall_max_time is not None:
                    # Convert to timezone-aware datetime for tracker
                    min_dt = pd.Timestamp(overall_min_time).to_pydatetime()
                    max_dt = pd.Timestamp(overall_max_time).to_pydatetime()
                    
                    if min_dt.tzinfo is None:
                        min_dt = min_dt.replace(tzinfo=timezone.utc)
                    else:
                        min_dt = min_dt.astimezone(timezone.utc)
                        
                    if max_dt.tzinfo is None:
                        max_dt = max_dt.replace(tzinfo=timezone.utc)
                    else:
                        max_dt = max_dt.astimezone(timezone.utc)
                    
                    restored_ranges[base_class_name.lower()] = (min_dt, max_dt)
                    print(f"    LOAD_SNAPSHOT_DEBUG: Updated restored_ranges for '{base_class_name.lower()}' with overall merged range: {min_dt} to {max_dt}")

        # ===== UPDATE THE DATA TRACKER WITH TIME RANGES =====
        pm.data_snapshot("Updating DataTracker with loaded time ranges...")
        if not restored_ranges:
            pm.data_snapshot("   LOAD_SNAPSHOT_DEBUG: restored_ranges is EMPTY before updating tracker.")
        else:
            pm.data_snapshot(f"   LOAD_SNAPSHOT_DEBUG: restored_ranges has keys: {list(restored_ranges.keys())} before updating tracker.")
            for class_key, (start_time, end_time) in restored_ranges.items():
                # Update tracker using the determined start/end times
                global_tracker._update_range((start_time, end_time), class_key, global_tracker.calculated_ranges)
                
                # Print confirmation
                trange_str_dbg = [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],
                                  end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
                pm.data_snapshot(f"   - Updated tracker for '{class_key}' with range: {trange_str_dbg[0]} to {trange_str_dbg[1]}")
        
        # --- Replace the old final message with a new status update ---
        # Old message:
        # print_manager.data_snapshot(f"Snapshot load finished from {filepath} (Compression: {compression_used})")

        # New message:
        processed_keys = list(restored_ranges.keys()) # Get keys updated in the tracker
        if processed_keys:
            keys_str = ', '.join(processed_keys)
            # Use os.path.basename to get just the filename from the potentially long path
            print_manager.status(f"🚀 Snapshot '{os.path.basename(filepath)}' loaded. Processed data for: {keys_str}. (Compression: {compression_used})\n")
        else:
            # Fallback if restored_ranges was empty for some reason (e.g., loading an empty snapshot)
            print_manager.status(f"🚀 Snapshot '{os.path.basename(filepath)}' loaded. (Compression: {compression_used}) - Note: No specific data ranges were processed/updated.\n")
        # --- End replacement ---

    except FileNotFoundError:
        print_manager.error(f"Snapshot file not found: {filepath}")
        print("DEBUG_LOAD_SNAPSHOT: Returning False - FileNotFoundError exception") # DBG
        return False
    except Exception as e:
        print_manager.error(f"Error loading snapshot: {e}")
        import traceback
        print_manager.error(traceback.format_exc())
        print("DEBUG_LOAD_SNAPSHOT: Returning False - Generic Exception") # DBG
        return False

    print("DEBUG_LOAD_SNAPSHOT: Returning True - Successful completion") # DBG
    return True

def _ensure_tracker_time_ranges_during_load(base_class_name, instance, restored_ranges):
    """
    Ensure instance time range matches what's in the global tracker.
    Used during snapshot loading to maintain time range consistency.
    
    Parameters
    ----------
    base_class_name : str
        The class name to check in the tracker
    instance : object
        The data instance to verify
    restored_ranges : dict
        Dictionary to update with expected time ranges
        
    Returns
    -------
    bool
        True if time range is consistent, False if issues were detected
    """
    pm = print_manager
    
    # Get the expected range from the tracker
    expected_range = global_tracker.get_calculated_range(base_class_name.lower())
    
    if not expected_range:
        # If no range in tracker, add current instance range to tracker
        if hasattr(instance, 'datetime_array') and instance.datetime_array is not None and len(instance.datetime_array) > 0:
            min_time = np.min(instance.datetime_array)
            max_time = np.max(instance.datetime_array)
            min_time_dt = pd.Timestamp(min_time).to_pydatetime().replace(tzinfo=timezone.utc)
            max_time_dt = pd.Timestamp(max_time).to_pydatetime().replace(tzinfo=timezone.utc)
            
            # Record the time range in the tracker
            global_tracker.update_calculated_range([min_time_dt, max_time_dt], base_class_name.lower())
            pm.data_snapshot(f"Added instance range to tracker for {base_class_name}: {min_time} to {max_time}")
            
            # Make sure restored_ranges has this info too
            restored_ranges[base_class_name.lower()] = (min_time_dt, max_time_dt)
            return True
            
    # At this point, we have an expected range from the tracker
    expected_min, expected_max = expected_range
    
    if hasattr(instance, 'datetime_array') and instance.datetime_array is not None and len(instance.datetime_array) > 0:
        actual_min = np.min(instance.datetime_array)
        actual_max = np.max(instance.datetime_array)
        
        pm.data_snapshot(f"Time Range Check for {base_class_name}:")
        pm.data_snapshot(f"  Expected from tracker: {expected_min} to {expected_max}")
        pm.data_snapshot(f"  Actual in instance: {actual_min} to {actual_max}")
        
        # Define a 5-second tolerance, matching what's in the tracker code
        tolerance = pd.Timedelta(seconds=5)
        
        # Check if the actual range is outside the expected range (beyond tolerance)
        min_too_late = pd.Timestamp(actual_min) > (pd.Timestamp(expected_min) + tolerance)
        max_too_early = pd.Timestamp(actual_max) < (pd.Timestamp(expected_max) - tolerance)
        
        if min_too_late or max_too_early:
            pm.warning(f"Time range mismatch for {base_class_name}!")
            if min_too_late:
                pm.warning(f"  Min time issue: actual {actual_min} > expected {expected_min}")
            if max_too_early:
                pm.warning(f"  Max time issue: actual {actual_max} < expected {expected_max}")
            
            # Update the tracker with the expected range to ensure consistency
            expected_min_dt = pd.Timestamp(expected_min).to_pydatetime().replace(tzinfo=timezone.utc)
            expected_max_dt = pd.Timestamp(expected_max).to_pydatetime().replace(tzinfo=timezone.utc)
            restored_ranges[base_class_name.lower()] = (expected_min_dt, expected_max_dt)
            
            # Let the test know about the issue
            pm.warning(f"Fixed time range in tracker for {base_class_name}")
            
            return False
        else:
            pm.data_snapshot(f"Time range verified for {base_class_name} (within tolerance)")
            
    return True

def _ensure_tracker_consistency(base_class_name, merged_instance):
    """
    Ensure consistency between instance data and tracker ranges for arbitrary time regions.
    
    Parameters
    ----------
    base_class_name : str
        The class name to check
    merged_instance : object
        The merged data instance
        
    Returns
    -------
    tuple or None
        (expected_start, expected_end) if special handling is needed, None otherwise
    """
    pm = print_manager
    
    # Get all known ranges from tracker for this class
    all_tracker_ranges = global_tracker.calculated_ranges.get(base_class_name.lower(), [])
    
    if not all_tracker_ranges:
        pm.debug(f"No tracker ranges found for {base_class_name}, nothing to reconcile")
        return None
        
    # Determine the full expected range from tracker
    earliest_start = min(r[0] for r in all_tracker_ranges)
    latest_end = max(r[1] for r in all_tracker_ranges)
    
    # Get actual range from loaded instance
    if hasattr(merged_instance, 'datetime_array') and merged_instance.datetime_array is not None and len(merged_instance.datetime_array) > 0:
        actual_min = np.min(merged_instance.datetime_array)
        actual_max = np.max(merged_instance.datetime_array)
        
        pm.data_snapshot(f"Time range check for {base_class_name}:")
        pm.data_snapshot(f"  Expected from tracker: {earliest_start} to {latest_end}")
        pm.data_snapshot(f"  Actual in instance: {actual_min} to {actual_max}")
        
        # Check if we need to reconcile
        tolerance = timedelta(seconds=5)
        min_too_late = pd.Timestamp(actual_min) > (pd.Timestamp(earliest_start) + tolerance)
        max_too_early = pd.Timestamp(actual_max) < (pd.Timestamp(latest_end) - tolerance)
        
        if min_too_late or max_too_early:
            pm.warning(f"Time range mismatch for {base_class_name}")
            
            # Update tracker to ensure it knows about the full range
            # (This is the key part - we're ensuring the tracker has the full expected range)
            unified_range = [earliest_start, latest_end]
            global_tracker.update_calculated_range(unified_range, base_class_name.lower())
            pm.status(f"Updated tracker with unified range: {earliest_start} to {latest_end}")
            
            # Return the expected range for restored_ranges
            return (earliest_start, latest_end)
    
    return None