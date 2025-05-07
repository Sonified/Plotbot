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

    # --- Add Sanity Check for lengths --- 
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
    # --- End Sanity Check ---
        
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
                elif isinstance(value, list):
                    if all(hasattr(item, 'shape') for item in value):
                        filtered_raw_data[key] = [item[segment_mask] for item in value]
                    else:
                        filtered_raw_data[key] = value
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
            elif isinstance(value, list):
                if all(hasattr(item, 'shape') for item in value):
                    filtered_raw_data[key] = [item[segment_mask] for item in value]
                else:
                    filtered_raw_data[key] = value
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
        if not trange_list: # Explicitly check if the trange_list is empty
             pm.warning("⚠️ [SNAPSHOT SAVE] 'trange_list' parameter is an empty list. Skipping data population.")
        elif not classes: # Explicitly check if the classes list is empty
             pm.warning("⚠️ [SNAPSHOT SAVE] 'classes' parameter is an empty list. Skipping data population.")
        else:
            # This status message was already correct from the previous diff.
            pm.status(f"[SNAPSHOT SAVE] Initiating data population for {len(classes)} class type(s) across {len(trange_list)} time range(s)...")
            for data_class_instance in classes: 
                instance_name = type(data_class_instance).__name__
                descriptive_name = getattr(data_class_instance, 'data_type', instance_name)
                if not descriptive_name: descriptive_name = instance_name
                
                pm.status(f"  Populating/updating data for: {descriptive_name}")
                for t_range in trange_list: 
                    pm.status(f"    Processing trange: {t_range} for {descriptive_name}")
                    try:
                        plotbot_get_data(t_range, data_class_instance)
                    except Exception as e:
                        pm.error(f"    ⚠️ Error during plotbot_get_data for {descriptive_name} with trange {t_range}: {e}")
            pm.status("[SNAPSHOT SAVE] Data population phase complete.")
    elif trange_list and not classes: # This case is handled by the input validation now
        # This pm.warning is technically redundant due to earlier validation but kept for belt-and-suspenders
        pm.warning("[SNAPSHOT SAVE] 'trange_list' was provided, but no 'classes' were specified to populate. Skipping population (this should have been caught by validation).")

    # --- Gather data to be saved ---
    # `classes` should now be the list of (potentially) populated global instances.
    effective_classes_to_save = classes if classes else []

    if not effective_classes_to_save:
        # This case should ideally be caught by earlier validation if classes was None and trange_list was also None.
        pm.warning("[SNAPSHOT SAVE] No effective classes to process for snapshot after population/initial checks. Nothing to save.")
        return False

    # --- Build the initial data_snapshot from effective_classes_to_save ---
    data_snapshot = {} 
    # loaded_classes_details = [] # Not strictly needed if we iterate over data_snapshot later

    for instance in effective_classes_to_save:
        # Determine a name/key for the instance in the snapshot dictionary
        instance_key = getattr(instance, 'data_type', None) 
        if not instance_key: # Fallback to class_name
            instance_key = getattr(instance, 'class_name', None)
        if not instance_key: # Fallback to actual type name if others are missing
            instance_key = type(instance).__name__
        # Ensure unique key if multiple instances of same unnamed type (should be rare with global instances)
        # temp_key = instance_key
        # count = 0
        # while temp_key in data_snapshot:
        #     count += 1
        #     temp_key = f"{instance_key}_{count}"
        # instance_key = temp_key

        if instance is None or _is_data_object_empty(instance):
            pm.status(f"[SNAPSHOT SAVE] Instance for key '{instance_key}' is empty or None. Skipping from initial snapshot build.")
            continue
            
        data_snapshot[instance_key] = instance 
        # loaded_classes_details.append((instance_key, instance))

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
                sorted_segments_info = sorted(segments_info, key=lambda x: x[0])
                
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
                # else: # If it exists, potentially reset it if we want a clean merge from segments
                    # pm.data_snapshot(f"    Global instance for {base_class_name} exists. Consider if it needs reset for segment merge.")
                    # For now, we assume update_global_instance with is_segment_merge=True handles first segment correctly.

                is_first_segment_for_this_base_class = True
                # Variables to track overall range of merged segments for this base_class
                current_merged_min_time = None
                current_merged_max_time = None

                for segment_id, segment_key_in_snapshot in sorted_segments_info:
                    instance_from_segment_snapshot = data_snapshot[segment_key_in_snapshot]
                    if _is_data_object_empty(instance_from_segment_snapshot):
                        pm.data_snapshot(f"    Skipping {segment_key_in_snapshot} (empty in snapshot)")
                        continue
                    
                    pm.data_snapshot(f"    Processing segment {segment_id} ({segment_key_in_snapshot}) for {base_class_name}")
                    
                    segment_data_for_cubby = SimpleDataObject()
                    segment_data_for_cubby.times = instance_from_segment_snapshot.time if hasattr(instance_from_segment_snapshot, 'time') else None
                    
                    raw_data_from_loaded_segment = instance_from_segment_snapshot.raw_data if hasattr(instance_from_segment_snapshot, 'raw_data') else {}
                    final_data_dict_for_cubby = {} 

                    expected_field_var_name = None
                    data_type_config = psp_data_types.get(base_class_name) 
                    if data_type_config and data_type_config.get('data_vars'):
                        if base_class_name == 'mag_RTN': expected_field_var_name = 'psp_fld_l2_mag_RTN'
                        elif base_class_name == 'mag_SC': expected_field_var_name = 'psp_fld_l2_mag_SC'
                        elif base_class_name == 'mag_RTN_4sa': expected_field_var_name = 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc'
                        elif base_class_name == 'mag_SC_4sa': expected_field_var_name = 'psp_fld_l2_mag_SC_4_Sa_per_Cyc'
                        # Add more explicit mappings if needed

                    if expected_field_var_name:
                        components = []
                        component_names = []
                        if base_class_name in ['mag_RTN', 'mag_RTN_4sa']:
                            component_names = ['br', 'bt', 'bn']
                        elif base_class_name in ['mag_SC', 'mag_SC_4sa']:
                            component_names = ['bx', 'by', 'bz']
                        
                        if component_names:
                            components = [raw_data_from_loaded_segment.get(c_name) for c_name in component_names]

                        if all(c is not None for c in components) and all(hasattr(c, '__len__') and len(c) == (len(components[0]) if components[0] is not None else 0) for c in components):
                            # Check against segment times if available
                            if segment_data_for_cubby.times is not None and len(segment_data_for_cubby.times) != (len(components[0]) if components[0] is not None else 0):
                                pm.warning(f"      Segment {segment_key_in_snapshot}: Component lengths ({len(components[0]) if components[0] is not None else 'N/A'}) mismatch with times length ({len(segment_data_for_cubby.times)}). Passing raw_data as is for field.")
                                final_data_dict_for_cubby.update(raw_data_from_loaded_segment) # Pass all raw data as fallback
                            else:
                                final_data_dict_for_cubby[expected_field_var_name] = np.column_stack(components)
                                pm.data_snapshot(f"      Reconstructed '{expected_field_var_name}' (shape {final_data_dict_for_cubby[expected_field_var_name].shape}) for segment {segment_id}.")
                        else:
                            pm.warning(f"      Segment {segment_key_in_snapshot}: Missing or inconsistent components for {base_class_name}. Not reconstructing field vector. Passing raw data keys: {list(raw_data_from_loaded_segment.keys())}")
                            final_data_dict_for_cubby.update(raw_data_from_loaded_segment) # Pass all raw data if reconstruction fails
                    else:
                        pm.warning(f"      Segment {segment_key_in_snapshot}: Could not determine expected field var for {base_class_name}. Passing raw_data as is.")
                        final_data_dict_for_cubby.update(raw_data_from_loaded_segment)
                    
                    # Ensure other non-component raw_data items from the segment are passed through if not already handled
                    for r_key, r_val in raw_data_from_loaded_segment.items():
                        if r_key not in final_data_dict_for_cubby: # Avoid overwriting reconstructed field
                            final_data_dict_for_cubby[r_key] = r_val

                    segment_data_for_cubby.data = final_data_dict_for_cubby
                    
                    # Diagnostic before calling update_global_instance
                    print(f"    LOAD_SNAPSHOT_DEBUG: About to call update_global_instance for segment {segment_id} of {base_class_name}.")
                    print(f"        segment_data_for_cubby.times is None: {segment_data_for_cubby.times is None}")
                    if segment_data_for_cubby.times is not None:
                        print(f"        segment_data_for_cubby.times len: {len(segment_data_for_cubby.times)}")
                    print(f"        segment_data_for_cubby.data keys: {list(segment_data_for_cubby.data.keys())}")

                    success = data_cubby.update_global_instance(base_class_name, segment_data_for_cubby, is_segment_merge=is_first_segment_for_this_base_class)
                    is_first_segment_for_this_base_class = False 

                    if success:
                        pm.data_snapshot(f"    Successfully processed/merged segment {segment_id} into {base_class_name}")
                        # Update overall time range for this base_class from the segment data
                        if hasattr(instance_from_segment_snapshot, 'datetime_array') and instance_from_segment_snapshot.datetime_array is not None and len(instance_from_segment_snapshot.datetime_array) > 0:
                            segment_min_dt = pd.Timestamp(np.min(instance_from_segment_snapshot.datetime_array))
                            segment_max_dt = pd.Timestamp(np.max(instance_from_segment_snapshot.datetime_array))
                            print(f"        Segment {segment_id} original datetime_array range: {segment_min_dt} to {segment_max_dt}")
                            if current_merged_min_time is None or segment_min_dt < current_merged_min_time:
                                current_merged_min_time = segment_min_dt
                            if current_merged_max_time is None or segment_max_dt > current_merged_max_time:
                                current_merged_max_time = segment_max_dt
                    else:
                        pm.warning(f"    Failed to process/merge segment {segment_id} into {base_class_name}")
                
                # After all segments for a base_class are processed:
                if current_merged_min_time is not None and current_merged_max_time is not None:
                    # Ensure UTC for tracker
                    if current_merged_min_time.tzinfo is None: current_merged_min_time = current_merged_min_time.tz_localize('UTC')
                    else: current_merged_min_time = current_merged_min_time.tz_convert('UTC')
                    if current_merged_max_time.tzinfo is None: current_merged_max_time = current_merged_max_time.tz_localize('UTC')
                    else: current_merged_max_time = current_merged_max_time.tz_convert('UTC')
                    
                    restored_ranges[base_class_name.lower()] = (current_merged_min_time, current_merged_max_time)
                    print(f"    LOAD_SNAPSHOT_DEBUG: Updated restored_ranges for '{base_class_name.lower()}' with overall merged range: {current_merged_min_time} to {current_merged_max_time}")
                else:
                    print(f"    LOAD_SNAPSHOT_DEBUG: No valid segment time ranges found to update restored_ranges for {base_class_name.lower()}")

                current_global_instance = data_cubby.grab(base_class_name)
                if current_global_instance:
                    if hasattr(current_global_instance, 'ensure_internal_consistency'):
                        pm.data_snapshot(f"  Ensuring final internal consistency for merged {base_class_name}...")
                        try: current_global_instance.ensure_internal_consistency()
                        except Exception as e_final_consistency: pm.error(f"  Error during final ensure_internal_consistency for {base_class_name}: {e_final_consistency}")
                    if hasattr(current_global_instance, 'set_ploptions'):
                        try: 
                            current_global_instance.set_ploptions()
                            pm.data_snapshot(f"  Final set_ploptions call for merged {base_class_name}")
                        except Exception as e_final_ploptions: pm.warning(f"  Error during final set_ploptions for {base_class_name}: {e_final_ploptions}")

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