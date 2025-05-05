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

# Type hint for raw data object
from typing import Any, List, Tuple, Dict, Optional, Union
DataObject = Any 

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
    if not hasattr(instance, 'datetime_array') or instance.datetime_array is None or len(instance.datetime_array) == 0:
        return []
        
    # Apply time filter if provided
    if time_filter:
        filtered_instance = _create_filtered_instance(instance, time_filter[0], time_filter[1])
        
        if _is_data_object_empty(filtered_instance) or len(filtered_instance.datetime_array) == 0:
            return []
            
        times = filtered_instance.datetime_array
    else:
        times = instance.datetime_array
        
    # Sort times and get sorted indices
    sorted_indices = np.argsort(times)
    sorted_times = times[sorted_indices]
    
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
        segment = copy.deepcopy(instance)
        
        # Apply the mask to datetime_array and time
        segment.datetime_array = times[segment_mask]
        if hasattr(instance, 'time') and instance.time is not None:
            segment.time = instance.time[segment_mask]
        
        # Filter raw_data based on the same mask
        if hasattr(instance, 'raw_data') and instance.raw_data is not None:
            filtered_raw_data = {}
            for key, value in instance.raw_data.items():
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
        if hasattr(instance, 'field') and instance.field is not None and hasattr(instance.field, 'shape'):
            if len(instance.field.shape) > 1:
                segment.field = instance.field[segment_mask, ...]
            else:
                segment.field = instance.field[segment_mask]
        
        segments.append(segment)
        start_idx = end_idx
    
    # Don't forget the last segment
    segment_mask = sorted_indices[start_idx:]
    segment = copy.deepcopy(instance)
    segment.datetime_array = times[segment_mask]
    if hasattr(instance, 'time') and instance.time is not None:
        segment.time = instance.time[segment_mask]
    
    # Filter raw_data for last segment
    if hasattr(instance, 'raw_data') and instance.raw_data is not None:
        filtered_raw_data = {}
        for key, value in instance.raw_data.items():
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
    if hasattr(instance, 'field') and instance.field is not None and hasattr(instance.field, 'shape'):
        if len(instance.field.shape) > 1:
            segment.field = instance.field[segment_mask, ...]
        else:
            segment.field = instance.field[segment_mask]
    
    segments.append(segment)
    return segments

class SimpleDataObject:
    """Simple data object for passing segment data."""
    def __init__(self):
        self.times = None
        self.data = {}

def save_data_snapshot(filename=None, classes=None, compression="none", time_range=None, auto_split=True):
    """
    Save data class instances to a pickle file with optional time filtering.
    Places file in 'data_snapshots/' directory.
    Generates intelligent filename if filename='auto'.

    Parameters
    ----------
    filename : str or 'auto', optional
        Desired filename (without extension or path), or 'auto' to generate.
        Defaults to timestamped filename if None.
    classes : list, class object, or None
        Specific class object(s) to save. If None, saves all available classes.
    compression : str, optional
        Compression level: "none", "low", "medium", "high", or format ("gzip", "bz2", "lzma").
    time_range : list, optional
        Time range [start, end] to filter data by before saving.
    auto_split : bool, optional
        Whether to automatically detect and split data segments at significant time gaps.
        Default is True.
    """
    # Parse time range if provided
    time_filter = None
    if time_range is not None:
        try:
            filter_start = parse(time_range[0])
            filter_end = parse(time_range[1])
            time_filter = (filter_start, filter_end)
            print_manager.status(f"Filtering data to time range: {filter_start} to {filter_end}")
        except Exception as e:
            print_manager.warning(f"Could not parse time range {time_range}: {e}. No filtering will be applied.")
    
    # Handle class object vs class name conversion
    if classes is not None:
        # Convert to list if a single class was passed
        if not isinstance(classes, list):
            classes = [classes]
            
        # Convert class objects to class names
        class_names = []
        for cls in classes:
            if isinstance(cls, str):
                class_names.append(cls)
            elif hasattr(cls, '__name__'):
                class_names.append(cls.__name__)
            else:
                # Try to get class name from the object
                class_names.append(cls.__class__.__name__)
    else:
        # Use all registered classes if none specified
        if hasattr(data_cubby, 'class_registry'):
            class_names = list(data_cubby.class_registry.keys())
        else:
            # Default list if registry not available
            class_names = [
                'mag_rtn_4sa', 'mag_rtn', 'mag_sc_4sa', 'mag_sc',
                'proton', 'proton_hr', 'proton_fits',
                'epad', 'epad_hr', 'ham'
            ]
    
    # Gather data from the cubby
    data_snapshot = {}
    loaded_classes_details = [] # Store tuples (name, instance)
    
    for class_name in class_names:
        instance = data_cubby.grab(class_name)
        if instance is None or _is_data_object_empty(instance):
            print_manager.status(f"[SNAPSHOT SAVE] Skipping {class_name} (empty or not initialized)")
            continue
            
        # If time filtering is requested
        if time_filter is not None and hasattr(instance, 'datetime_array') and instance.datetime_array is not None:
            try:
                # Get the original time range for reference
                orig_len = len(instance.datetime_array)
                
                # Identify data segments if auto_split is enabled
                segments = []
                
                if auto_split:
                    # Find segments with significant time gaps
                    segments = _identify_data_segments(instance, time_filter)
                
                if not segments:
                    # Just create a single filtered instance
                    filtered_instance = _create_filtered_instance(instance, time_filter[0], time_filter[1])
                    
                    if _is_data_object_empty(filtered_instance):
                        print_manager.warning(f"[SNAPSHOT SAVE] Filtered instance for {class_name} is empty (no data in time range). Skipping.")
                        continue
                        
                    filtered_len = len(filtered_instance.datetime_array)
                    print_manager.status(f"[SNAPSHOT SAVE] Filtered {class_name} from {orig_len} to {filtered_len} points")
                    data_snapshot[class_name] = filtered_instance
                    loaded_classes_details.append((class_name, filtered_instance))
                else:
                    # We have multiple segments - save them with segment identifiers
                    print_manager.status(f"[SNAPSHOT SAVE] Found {len(segments)} distinct time segments for {class_name}")
                    
                    # Record segment metadata
                    segment_metadata = {
                        "original_class": class_name,
                        "segments": len(segments),
                        "segment_ranges": []
                    }
                    
                    total_points = 0
                    for i, segment in enumerate(segments):
                        segment_name = f"{class_name}_segment_{i+1}"
                        segment_start = min(segment.datetime_array)
                        segment_end = max(segment.datetime_array)
                        segment_len = len(segment.datetime_array)
                        total_points += segment_len
                        
                        # Add segment range to metadata
                        segment_metadata["segment_ranges"].append({
                            "segment_id": i+1,
                            "start": segment_start,
                            "end": segment_end,
                            "points": segment_len
                        })
                        
                        print_manager.status(f"[SNAPSHOT SAVE] Segment {i+1}: {segment_len} points from {segment_start} to {segment_end}")
                        data_snapshot[segment_name] = segment
                        loaded_classes_details.append((segment_name, segment))
                    
                    # Add the metadata to the snapshot
                    data_snapshot[f"{class_name}_segments_meta"] = segment_metadata
                    print_manager.status(f"[SNAPSHOT SAVE] Total: filtered {class_name} from {orig_len} to {total_points} points across {len(segments)} segments")
            except Exception as e:
                print_manager.warning(f"[SNAPSHOT SAVE] Error filtering {class_name}: {e}. Saving original instance.")
                data_snapshot[class_name] = instance
                loaded_classes_details.append((class_name, instance))
        else:
            # No time filtering - save the original instance
            data_snapshot[class_name] = instance
            loaded_classes_details.append((class_name, instance))
    
    if not loaded_classes_details:
        print_manager.warning("No data classes found to save!")
        return None
    
    # --- Determine Base Filename ---
    output_dir = "data_snapshots"
    os.makedirs(output_dir, exist_ok=True) # Ensure directory exists

    # Add time filter info to filename if provided
    time_filter_str = ""
    if time_filter is not None:
        try:
            time_format = "%Y%m%d-%H%M%S"
            filter_start_str = time_filter[0].strftime(time_format)
            filter_end_str = time_filter[1].strftime(time_format)
            time_filter_str = f"_filtered_{filter_start_str}_to_{filter_end_str}"
        except Exception:
            time_filter_str = "_filtered"

    if filename == 'auto':
        # --- Auto-generate filename ---
        shorthands = set()
        all_times = []
        
        for name, inst in loaded_classes_details:
            if '_segment_' in name:  # Handle segmented class names
                orig_class = name.split('_segment_')[0]
                class_type_name = inst.__class__.__name__
                shorthands.add(VARIABLE_SHORTHANDS.get(class_type_name, 'unk'))
            else:
                class_type_name = inst.__class__.__name__
                shorthands.add(VARIABLE_SHORTHANDS.get(class_type_name, 'unk'))
                
            if hasattr(inst, 'datetime_array') and inst.datetime_array is not None and len(inst.datetime_array) > 0:
                all_times.append(inst.datetime_array)

        # Generate time range string for filename
        if not all_times:
            min_time_str = "no_time"
            max_time_str = "no_time"
        else:
            try:
                # Find min/max across all arrays
                min_times = [np.min(times) for times in all_times if len(times) > 0]
                max_times = [np.max(times) for times in all_times if len(times) > 0]
                
                if min_times and max_times:
                    min_time = pd.Timestamp(min(min_times))
                    max_time = pd.Timestamp(max(max_times))
                    time_format = "%Y%m%d-%H%M%S"
                    min_time_str = min_time.strftime(time_format)
                    max_time_str = max_time.strftime(time_format)
                else:
                    min_time_str = "no_time"
                    max_time_str = "no_time"
            except Exception as e:
                print_manager.warning(f"Could not determine time range for auto filename: {e}")
                min_time_str = "time_error"
                max_time_str = "time_error"

        sorted_shorthands = sorted(list(shorthands))
        vars_str = '+'.join(sorted_shorthands)
        segments_str = "_segmented" if auto_split and any('_segment_' in name for name, _ in loaded_classes_details) else ""
        base_filename = f"{vars_str}_from_{min_time_str}_to_{max_time_str}{time_filter_str}{segments_str}"
        print_manager.status(f"[SNAPSHOT SAVE] Auto-generated base filename: {base_filename}")
        # --- End Auto-generate ---

    elif filename is None:
        # Default timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        segments_str = "_segmented" if auto_split and any('_segment_' in name for name, _ in loaded_classes_details) else ""
        base_filename = f"data_snapshot_{timestamp}{time_filter_str}{segments_str}"
    else:
        # Use user-provided filename (remove extension)
        base_filename = os.path.splitext(filename)[0]
        if time_filter is not None and "_filtered" not in base_filename:
            base_filename += time_filter_str
        if auto_split and any('_segment_' in name for name, _ in loaded_classes_details) and "_segmented" not in base_filename:
            base_filename += "_segmented"
    
    # --- Handle Compression and Save ---
    compression_used_str = "None"
    final_filepath = None

    if compression.lower() == "none":
        final_filename_ext = f"{base_filename}.pkl"
        final_filepath = os.path.join(output_dir, final_filename_ext)
        with open(final_filepath, 'wb') as f:
            pickle.dump(data_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        # Map compression levels to specific settings
        if compression.lower() == "low":
            compression = "gzip"
            level = 1
        elif compression.lower() == "medium":
            compression = "gzip"
            level = 5
        elif compression.lower() == "high":
            compression = "lzma"
            level = 9
        else:
            # Assume a specific compression format was specified
            level = 5  # Default level
        
        # Apply the selected compression
        if compression.lower() == "gzip":
            import gzip
            final_filename_ext = f"{base_filename}.pkl.gz"
            final_filepath = os.path.join(output_dir, final_filename_ext)
            with gzip.open(final_filepath, 'wb', compresslevel=level) as f:
                pickle.dump(data_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            compression_used_str = f"gzip (level {level})"
        elif compression.lower() == "bz2":
            import bz2
            final_filename_ext = f"{base_filename}.pkl.bz2"
            final_filepath = os.path.join(output_dir, final_filename_ext)
            with bz2.open(final_filepath, 'wb', compresslevel=level) as f:
                pickle.dump(data_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            compression_used_str = f"bz2 (level {level})"
        elif compression.lower() == "lzma":
            import lzma
            final_filename_ext = f"{base_filename}.pkl.xz"
            final_filepath = os.path.join(output_dir, final_filename_ext)
            with lzma.open(final_filepath, 'wb', preset=level) as f:
                pickle.dump(data_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            compression_used_str = f"lzma (preset {level})"
        else:
            print_manager.warning(f"Unknown compression format '{compression}', using no compression")
            final_filename_ext = f"{base_filename}.pkl"
            final_filepath = os.path.join(output_dir, final_filename_ext)
            with open(final_filepath, 'wb') as f:
                pickle.dump(data_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    if final_filepath:
        filter_notice = " (time-filtered)" if time_filter is not None else ""
        segment_notice = " with segmentation" if auto_split and any('_segment_' in name for name, _ in loaded_classes_details) else ""
        print_manager.status(f"✅ Data snapshot{filter_notice}{segment_notice} saved to {final_filepath}")
        
        # Count data classes vs segment classes
        data_classes = [name for name, _ in loaded_classes_details if '_segment_' not in name and '_segments_meta' not in name]
        segment_classes = set(name.split('_segment_')[0] for name, _ in loaded_classes_details if '_segment_' in name)
        
        # Create a nice summary message
        if segment_classes:
            print_manager.status(f"   Saved {len(data_classes)} regular classes and {len(segment_classes)} segmented classes")
            print_manager.status(f"   Regular classes: {', '.join(data_classes) if data_classes else 'None'}")
            print_manager.status(f"   Segmented classes: {', '.join(segment_classes)}")
        else:
            print_manager.status(f"   Saved classes: {', '.join(data_classes)}")
            
        print_manager.status(f"   Compression: {compression_used_str}")
    else:
        print_manager.error("[SNAPSHOT SAVE] Failed to determine final save path.")

    return final_filepath # Return the full path

def load_data_snapshot(filename, classes=None, merge_segments=True):
    """
    Load data from a previously saved snapshot file.
    Assumes file is in 'data_snapshots/' unless an absolute path is given.

    Parameters
    ----------
    filename : str
        Filename (potentially without path) or full path to the pickle file.
    classes : list, class object, or None
        Specific class object(s) to load. If None, loads all classes in the file.
    merge_segments : bool, optional
        Whether to automatically merge segments of the same class. Default is True.
    """
    # --- Adjust filename to check data_snapshots/ directory ---
    if not os.path.isabs(filename) and not filename.startswith('data_snapshots/'):
        filepath = os.path.join('data_snapshots', filename)
        if not os.path.exists(filepath) and os.path.exists(filename):
             filepath = filename # Use original if found in root and not in data_snapshots
             print_manager.warning(f"Snapshot found in root ({filename}), not in data_snapshots/. Using root path.")
        elif not os.path.exists(filepath):
             print_manager.error(f"Snapshot file not found in data_snapshots/ or root: {filename}")
             return None
    else:
        filepath = filename # Use provided path (absolute or already includes dir)
        if not os.path.exists(filepath):
             print_manager.error(f"Snapshot file not found: {filepath}")
             return None
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
        
        # Filter classes if needed
        if classes is not None:
            print_manager.data_snapshot(f"Filtering for classes: {classes}")
            # Convert to list if a single class was passed
            if not isinstance(classes, list):
                classes = [classes]
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
        # Identify segment groups in the snapshot
        segment_groups = {}
        regular_classes = []
        
        for key in data_snapshot.keys():
            if '_segment_' in key:
                # This is a segment class (e.g., 'mag_rtn_4sa_segment_1')
                base_class = key.split('_segment_')[0]
                segment_id = int(key.split('_segment_')[1])
                
                if base_class not in segment_groups:
                    segment_groups[base_class] = []
                    
                segment_groups[base_class].append((segment_id, key))
            elif key.endswith('_segments_meta'):
                # Skip metadata entries - we'll use them during processing
                continue
            else:
                # This is a regular class
                regular_classes.append(key)
        
        # Process regular classes first
        restored_ranges = {}
        for class_name in regular_classes:
            instance_from_snapshot = data_snapshot[class_name]
            if _is_data_object_empty(instance_from_snapshot):
                print_manager.data_snapshot(f"Skipping {class_name} (empty in snapshot)")
                continue
                
            print_manager.data_snapshot(f"Processing {class_name} from snapshot (type: {type(instance_from_snapshot)})")
            
            # Get the existing global instance
            global_instance = data_cubby.grab(class_name)
            restored_instance = None
            
            # Process this regular class using standard methods
            if global_instance is not None and hasattr(global_instance, 'restore_from_snapshot'):
                try:
                    print_manager.data_snapshot(f"    Attempting restore_from_snapshot for {class_name} into existing global instance (ID: {id(global_instance)})...")
                    # Call the instance's own method to restore state
                    global_instance.restore_from_snapshot(instance_from_snapshot)
                    print_manager.data_snapshot(f"    - restore_from_snapshot successful for {class_name}.")
                    
                    # Call set_ploptions on the updated global instance
                    if hasattr(global_instance, 'set_ploptions'):
                        try:
                            global_instance.set_ploptions()
                            print_manager.data_snapshot(f"    - Called set_ploptions on updated global instance for {class_name}.")
                        except Exception as plopt_err:
                             print_manager.warning(f"    - Error calling set_ploptions for {class_name} after restore: {plopt_err}")
                    
                    restored_instance = global_instance
                    
                except Exception as restore_err:
                     print_manager.warning(f"    - Error calling restore_from_snapshot for {class_name}: {restore_err}. Stashing pickled instance as fallback.")
                     # Fallback: stash the loaded instance
                     data_cubby.stash(instance_from_snapshot, class_name=class_name)
                     # Grab the newly stashed instance
                     restored_instance = data_cubby.grab(class_name) 
                     if restored_instance:
                         # Call set_ploptions if available
                         if hasattr(restored_instance, 'set_ploptions'):
                             try:
                                 restored_instance.set_ploptions()
                                 print_manager.data_snapshot(f"    - Called set_ploptions on newly stashed instance for {class_name}.")
                             except Exception as plopt_err:
                                  print_manager.warning(f"    - Error calling set_ploptions for {class_name} after stashing: {plopt_err}")
                     else:
                         print_manager.error(f"    - Failed to grab instance {class_name} after stashing fallback!")
            else:
                # If no global instance or no restore method, stash the loaded instance
                if global_instance is None:
                     print_manager.data_snapshot(f"    No existing global instance found for {class_name}. Stashing pickled instance.")
                else: # Global instance exists but no restore method
                     print_manager.data_snapshot(f"    Global instance for {class_name} lacks restore_from_snapshot. Stashing pickled instance.")
                
                data_cubby.stash(instance_from_snapshot, class_name=class_name)
                # Grab the newly stashed instance
                restored_instance = data_cubby.grab(class_name) 
                if restored_instance:
                    # Call set_ploptions if available
                    if hasattr(restored_instance, 'set_ploptions'):
                        try:
                            restored_instance.set_ploptions()
                            print_manager.data_snapshot(f"    - Called set_ploptions on newly stashed instance for {class_name}.")
                        except Exception as plopt_err:
                                print_manager.warning(f"    - Error calling set_ploptions for {class_name} after stashing: {plopt_err}")
                else:
                     print_manager.error(f"    - Failed to grab instance {class_name} after stashing fallback!")
            
            # Extract time range info
            if restored_instance and hasattr(restored_instance, 'datetime_array') and restored_instance.datetime_array is not None and len(restored_instance.datetime_array) > 0:
                try:
                    min_dt64 = np.min(restored_instance.datetime_array)
                    max_dt64 = np.max(restored_instance.datetime_array)
                    min_time_pd = pd.Timestamp(min_dt64)
                    max_time_pd = pd.Timestamp(max_dt64)
                    if min_time_pd.tz is None: min_time_pd = min_time_pd.tz_localize('UTC')
                    else: min_time_pd = min_time_pd.tz_convert('UTC')
                    if max_time_pd.tz is None: max_time_pd = max_time_pd.tz_localize('UTC')
                    else: max_time_pd = max_time_pd.tz_convert('UTC')
                    
                    # Store time range
                    restored_ranges[class_name.lower()] = (min_time_pd, max_time_pd)
                    
                    # Format for debug message
                    trange_str_dbg = [min_time_pd.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],
                                    max_time_pd.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
                    print_manager.data_snapshot(f"    - Determined time range for {class_name}: {trange_str_dbg[0]} to {trange_str_dbg[1]}")
                except Exception as calc_err:
                    print_manager.warning(f"    - Could not determine time range for {class_name} from restored instance data: {calc_err}")
            else:
                print_manager.data_snapshot(f"    - No time range data found or determined for {class_name}.")
            
            # Repair plot_manager attributes
            try:
                if restored_instance:
                    for attr_name in dir(restored_instance):
                        if attr_name.startswith('__'):
                            continue
                        try:
                            attr = getattr(restored_instance, attr_name)
                            # Check if it's a plot_manager
                            if isinstance(attr, plot_manager): 
                                needs_fix = False
                                # Ensure plot_options has correct class/subclass
                                if not hasattr(attr, 'plot_options') or attr.plot_options is None:
                                    from .ploptions import ploptions
                                    attr.plot_options = ploptions()
                                    needs_fix = True
                                
                                if getattr(attr.plot_options, 'class_name', None) != class_name:
                                    setattr(attr.plot_options, 'class_name', class_name)
                                    needs_fix = True
                                if getattr(attr.plot_options, 'subclass_name', None) != attr_name:
                                    setattr(attr.plot_options, 'subclass_name', attr_name)
                                    needs_fix = True
                                
                                # Ensure _plot_state exists and has correct class/subclass
                                if not hasattr(attr, '_plot_state') or attr._plot_state is None:
                                    object.__setattr__(attr, '_plot_state', {})
                                    needs_fix = True 
                                if attr._plot_state.get('class_name') != class_name:
                                    attr._plot_state['class_name'] = class_name
                                    needs_fix = True
                                if attr._plot_state.get('subclass_name') != attr_name:
                                    attr._plot_state['subclass_name'] = attr_name
                                    needs_fix = True
                                
                                if needs_fix:
                                    print_manager.data_snapshot(f"    - Repaired plot_manager state/options for {class_name}.{attr_name}")
                        except Exception as e:
                            print_manager.data_snapshot(f"    - Skipping repair check for attribute {attr_name} in {class_name} due to error: {e}")
                            continue
            except Exception as e:
                print_manager.warning(f"    - Error during plot_manager repair loop for {class_name}: {e}")
        
        # Now process segment groups if merge_segments is True
        if merge_segments and segment_groups:
            print_manager.data_snapshot(f"Processing {len(segment_groups)} segment groups")
            
            for base_class, segments in segment_groups.items():
                print_manager.data_snapshot(f"Processing segment group for {base_class} with {len(segments)} segments")
                
                # Sort segments by ID
                sorted_segments = sorted(segments, key=lambda x: x[0])
                
                # Get metadata if available
                metadata = data_snapshot.get(f"{base_class}_segments_meta", None)
                if metadata:
                    print_manager.data_snapshot(f"Found metadata for {base_class} segments: {len(metadata['segment_ranges'])} segments described")
                
                # Get the global instance for this base class
                global_instance = data_cubby.grab(base_class)
                
                if global_instance is None:
                    print_manager.data_snapshot(f"No global instance for {base_class}. Creating new instance.")
                    # Try to determine the correct class type
                    CorrectClass = data_cubby._get_class_type_from_string(base_class)
                    if CorrectClass:
                        global_instance = CorrectClass(None)  # Create empty instance
                        data_cubby.stash(global_instance, class_name=base_class)
                        global_instance = data_cubby.grab(base_class)  # Re-grab to ensure we have the stashed instance
                    else:
                        print_manager.warning(f"Could not determine class type for {base_class}. Skipping segments.")
                        continue
                
                # Process each segment
                for segment_id, segment_key in sorted_segments:
                    instance_from_snapshot = data_snapshot[segment_key]
                    
                    if _is_data_object_empty(instance_from_snapshot):
                        print_manager.data_snapshot(f"Skipping {segment_key} (empty in snapshot)")
                        continue
                    
                    print_manager.data_snapshot(f"Processing segment {segment_id} for {base_class} (key: {segment_key})")
                    
                    # Here's the key part: we use the data_cubby's update_global_instance method to merge segments
                    if hasattr(data_cubby, 'update_global_instance'):
                        # Prepare a data object with the segment's data
                        segment_data = SimpleDataObject()
                        segment_data.times = instance_from_snapshot.time if hasattr(instance_from_snapshot, 'time') else None
                        segment_data.data = instance_from_snapshot.raw_data if hasattr(instance_from_snapshot, 'raw_data') else {}
                        
                        # Update the global instance with this segment's data
                        print_manager.data_snapshot(f"Calling update_global_instance for {base_class} with segment {segment_id} data")
                        success = data_cubby.update_global_instance(base_class, segment_data)
                        
                        if success:
                            print_manager.data_snapshot(f"Successfully merged segment {segment_id} into {base_class}")
                            
                            # Record the time range of this segment
                            if hasattr(instance_from_snapshot, 'datetime_array') and instance_from_snapshot.datetime_array is not None:
                                try:
                                    min_dt64 = np.min(instance_from_snapshot.datetime_array)
                                    max_dt64 = np.max(instance_from_snapshot.datetime_array)
                                    min_time_pd = pd.Timestamp(min_dt64)
                                    max_time_pd = pd.Timestamp(max_dt64)
                                    
                                    # Add this segment's range to the restoration tracking
                                    if base_class.lower() not in restored_ranges:
                                        restored_ranges[base_class.lower()] = (min_time_pd, max_time_pd)
                                    else:
                                        # Update with wider range
                                        current_min, current_max = restored_ranges[base_class.lower()]
                                        restored_ranges[base_class.lower()] = (
                                            min(current_min, min_time_pd),
                                            max(current_max, max_time_pd)
                                        )
                                        
                                    print_manager.data_snapshot(f"Updated time range for {base_class.lower()}: {min_time_pd} to {max_time_pd}")
                                except Exception as e:
                                    print_manager.warning(f"Error calculating time range for {segment_key}: {e}")
                        else:
                            print_manager.warning(f"Failed to merge segment {segment_id} into {base_class}")
                    else:
                        print_manager.warning(f"data_cubby lacks update_global_instance method. Cannot merge segments for {base_class}")
            
            # After all segments are processed, ensure plot managers are set up
            for base_class in segment_groups.keys():
                global_instance = data_cubby.grab(base_class)
                if global_instance and hasattr(global_instance, 'set_ploptions'):
                    try:
                        global_instance.set_ploptions()
                        print_manager.data_snapshot(f"Reset plot options for merged segments in {base_class}")
                    except Exception as e:
                        print_manager.warning(f"Error resetting plot options for {base_class}: {e}")
        
        # ===== UPDATE THE DATA TRACKER WITH TIME RANGES =====
        print_manager.data_snapshot("Updating DataTracker with loaded time ranges...")
        if not restored_ranges:
            print_manager.data_snapshot("   No time ranges were determined from the loaded snapshot.")
        else:
            for class_key, (start_time, end_time) in restored_ranges.items():
                # Update tracker using the determined start/end times
                global_tracker._update_range((start_time, end_time), class_key, global_tracker.calculated_ranges)
                
                # Print confirmation
                trange_str_dbg = [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],
                                  end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
                print_manager.data_snapshot(f"   - Updated tracker for '{class_key}' with range: {trange_str_dbg[0]} to {trange_str_dbg[1]}")
        
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
        return False # Explicitly return False on FileNotFoundError
    except Exception as e:
        print_manager.error(f"Error loading snapshot: {e}")
        import traceback
        print_manager.error(traceback.format_exc())
        return False # Explicitly return False on other exceptions

    return True # Return True on successful completion