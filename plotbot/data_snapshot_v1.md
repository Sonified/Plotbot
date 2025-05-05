from . import print_manager
from . import data_cubby
import numpy as np
import pandas as pd
import time
import pickle
from datetime import datetime, timezone
import os

# Import our custom managers and classes
from .print_manager import print_manager
from .data_cubby import data_cubby # Import data_cubby class
# from .config import VARIABLE_SHORTHANDS
from .plot_manager import plot_manager # ADD THIS IMPORT

# Type hint for raw data object (replace with actual DataObject if defined)
from typing import Any
DataObject = Any 

# --- Add helper mapping for variable shorthands ---
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
# --- End helper mapping ---

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

def save_data_snapshot(filename=None, classes=None, compression="none"):
    """
    Save data class instances to a pickle file with optional compression.
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
    """
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
        if instance is not None and not _is_data_object_empty(instance):
            data_snapshot[class_name] = instance
            loaded_classes_details.append((class_name, instance)) # Store tuple
        else:
            print_manager.status(f"[SNAPSHOT SAVE] Skipping {class_name} (empty or not initialized)")
    
    if not loaded_classes_details:
        print_manager.warning("No data classes found to save!")
        return None
    
    # --- Determine Base Filename ---
    output_dir = "data_snapshots"
    os.makedirs(output_dir, exist_ok=True) # Ensure directory exists

    if filename == 'auto':
        # --- Auto-generate filename ---
        shorthands = set()
        all_times = []
        for name, inst in loaded_classes_details:
            class_type_name = inst.__class__.__name__
            shorthands.add(VARIABLE_SHORTHANDS.get(class_type_name, 'unk')) # Use shorthand map
            if hasattr(inst, 'datetime_array') and inst.datetime_array is not None:
                all_times.append(inst.datetime_array)

        if not all_times:
            min_time_str = "no_time"
            max_time_str = "no_time"
        else:
            try:
                full_time_array = np.concatenate(all_times)
                min_time = pd.Timestamp(np.min(full_time_array))
                max_time = pd.Timestamp(np.max(full_time_array))
                # Format time: YYYYMMDD-HHMMSS
                time_format = "%Y%m%d-%H%M%S"
                min_time_str = min_time.strftime(time_format)
                max_time_str = max_time.strftime(time_format)
            except Exception as e:
                print_manager.warning(f"Could not determine time range for auto filename: {e}")
                min_time_str = "time_error"
                max_time_str = "time_error"

        sorted_shorthands = sorted(list(shorthands))
        vars_str = '+'.join(sorted_shorthands)
        base_filename = f"{vars_str}_from_{min_time_str}_to_{max_time_str}"
        print_manager.status(f"[SNAPSHOT SAVE] Auto-generated base filename: {base_filename}")
        # --- End Auto-generate ---

    elif filename is None:
        # Default timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"data_snapshot_{timestamp}"
    else:
        # Use user-provided filename (remove extension)
        base_filename = os.path.splitext(filename)[0]

    # --- Handle Compression and Save ---
    # (Compression logic remains largely the same, but uses os.path.join)
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
        print_manager.status(f"✅ Data snapshot saved to {final_filepath}")
        saved_class_names = [name for name, inst in loaded_classes_details]
        print_manager.status(f"   Saved classes: {', '.join(saved_class_names)}")
        print_manager.status(f"   Compression: {compression_used_str}")
    else:
        print_manager.error("[SNAPSHOT SAVE] Failed to determine final save path.")

    return final_filepath # Return the full path

def load_data_snapshot(filename, classes=None):
    """
    Load data from a previously saved snapshot file (auto-detects compression).
    Assumes file is in 'data_snapshots/' unless an absolute path is given.

    Parameters
    ----------
    filename : str
        Filename (potentially without path) or full path to the pickle file.
    classes : list, class object, or None
        Specific class object(s) to load. If None, loads all classes in the file.
    """
    # Import the tracker directly
    from plotbot.data_tracker import global_tracker
    
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

    print_manager.data_snapshot(f"Starting load from {filepath}") # Use adjusted filepath
    try:
        # Auto-detect compression format based on file extension
        # (This logic needs the final filepath)
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
            # Filter the snapshot
            filtered_snapshot = {k: v for k, v in data_snapshot.items() if k in class_names}
            data_snapshot = filtered_snapshot
            print_manager.data_snapshot(f"Filtered keys: {list(data_snapshot.keys())}")
        
        restored_ranges = {}
        
        # Restore data to cubby
        for class_name, instance_from_snapshot in data_snapshot.items():
            if _is_data_object_empty(instance_from_snapshot):
                print_manager.data_snapshot(f"Skipping {class_name} (empty in snapshot)")
                continue
            print_manager.data_snapshot(f"Processing {class_name} from snapshot (type: {type(instance_from_snapshot)})")

            # --- Get the existing global instance --- 
            global_instance = data_cubby.grab(class_name)
            restored_instance = None # Variable to hold the instance whose time range we'll check
            
            # --- Attempt to restore into global instance using its own method --- 
            if global_instance is not None and hasattr(global_instance, 'restore_from_snapshot'):
                try:
                    print_manager.data_snapshot(f"    Attempting restore_from_snapshot for {class_name} into existing global instance (ID: {id(global_instance)})...")
                    # Call the instance's own method to restore state
                    global_instance.restore_from_snapshot(instance_from_snapshot)
                    print_manager.data_snapshot(f"    - restore_from_snapshot successful for {class_name}.")
                    
                    # Call set_ploptions on the updated global instance AFTER restoring
                    if hasattr(global_instance, 'set_ploptions'):
                        try:
                            global_instance.set_ploptions()
                            print_manager.data_snapshot(f"    - Called set_ploptions on updated global instance for {class_name}.")
                        except Exception as plopt_err:
                             print_manager.warning(f"    - Error calling set_ploptions for {class_name} after restore: {plopt_err}")
                    
                    restored_instance = global_instance # Use the updated global instance for time range
                    
                except Exception as restore_err:
                     print_manager.warning(f"    - Error calling restore_from_snapshot for {class_name}: {restore_err}. Stashing pickled instance as fallback.")
                     # Fallback: stash the loaded instance (replaces global instance)
                     data_cubby.stash(instance_from_snapshot, class_name=class_name)
                     # Grab the newly stashed instance
                     restored_instance = data_cubby.grab(class_name) 
                     if restored_instance:
                         # Attempt set_ploptions on the newly stashed instance
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
                    # Attempt set_ploptions on the newly stashed instance
                    if hasattr(restored_instance, 'set_ploptions'):
                        try:
                            restored_instance.set_ploptions()
                            print_manager.data_snapshot(f"    - Called set_ploptions on newly stashed instance for {class_name}.")
                        except Exception as plopt_err:
                                print_manager.warning(f"    - Error calling set_ploptions for {class_name} after stashing: {plopt_err}")
                else:
                     print_manager.error(f"    - Failed to grab instance {class_name} after stashing fallback!")
            
            # --- Time Range Extraction and Tracker Update (using restored_instance) --- 
            if restored_instance and hasattr(restored_instance, 'datetime_array') and restored_instance.datetime_array is not None and len(restored_instance.datetime_array) > 0:
                try:
                    min_dt64 = np.min(restored_instance.datetime_array)
                    max_dt64 = np.max(restored_instance.datetime_array)
                    # Convert numpy datetime64 to pandas Timestamp, ensuring UTC
                    min_time_pd = pd.Timestamp(min_dt64)
                    max_time_pd = pd.Timestamp(max_dt64)
                    if min_time_pd.tz is None: min_time_pd = min_time_pd.tz_localize('UTC')
                    else: min_time_pd = min_time_pd.tz_convert('UTC')
                    if max_time_pd.tz is None: max_time_pd = max_time_pd.tz_localize('UTC')
                    else: max_time_pd = max_time_pd.tz_convert('UTC')
                    
                    # Store pandas Timestamps in restored_ranges dict
                    restored_ranges[class_name.lower()] = (min_time_pd, max_time_pd) 
                    
                    # Format for debug message only
                    trange_str_dbg = [min_time_pd.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],
                                      max_time_pd.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
                    print_manager.data_snapshot(f"    - Determined time range for {class_name}: {trange_str_dbg[0]} to {trange_str_dbg[1]}")
                except Exception as calc_err:
                    print_manager.warning(f"    - Could not determine time range for {class_name} from restored instance data: {calc_err}")
            else:
                print_manager.data_snapshot(f"    - No time range data found or determined for {class_name} (datetime_array missing, empty, or instance invalid).")

            # --- REPAIR STEP: Fix plot_manager attributes (applied to 'restored_instance') ---
            # Note: This step is crucial after restoring/stashing
            try:
                if restored_instance:
                    # Find and repair plot_manager instances within the 'restored_instance'
                    for attr_name in dir(restored_instance):
                        if attr_name.startswith('__'):
                            continue
                        try:
                            attr = getattr(restored_instance, attr_name)
                            # Check if it's a plot_manager using isinstance
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
                            # Skip attributes causing errors during getattr or checks
                            print_manager.data_snapshot(f"    - Skipping repair check for attribute {attr_name} in {class_name} due to error: {e}")
                            continue
            except Exception as e:
                print_manager.warning(f"    - Error during plot_manager repair loop for {class_name}: {e}")
            # --- END REPAIR STEP ---

        # ===== UPDATE THE DATA TRACKER WITH TIME RANGES =====
        print_manager.data_snapshot("Updating DataTracker with loaded time ranges...")
        if not restored_ranges:
            print_manager.data_snapshot("   No time ranges were determined from the loaded snapshot.")
        else:
            for class_key, (start_time, end_time) in restored_ranges.items():
                # Update tracker using the determined start/end times (which are pd.Timestamps)
                # The tracker's _update_range handles conversion if needed, but passing Timestamps is cleaner
                global_tracker._update_range((start_time, end_time), class_key, global_tracker.calculated_ranges)
                # Optionally print confirmation
                trange_str_dbg = [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],
                                  end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
                print_manager.data_snapshot(f"   - Updated tracker for '{class_key}' with range: {trange_str_dbg[0]} to {trange_str_dbg[1]}")
        print_manager.data_snapshot(f"Snapshot load finished from {filepath} (Compression: {compression_used})") # Use adjusted filepath

    except FileNotFoundError:
        print_manager.error(f"Snapshot file not found: {filepath}")
        return False

    return True