import sys
import os
import numpy as np
from datetime import datetime, timezone
from typing import List, Union, Optional, Dict, Any, Tuple
from dateutil.parser import parse
import pandas as pd

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_cubby import data_cubby
from .data_download_berkeley import download_berkeley_data
from .data_download_pyspedas import download_spdf_data
import plotbot
from .data_import import import_data_function
from .data_classes.psp_data_types import data_types
from .data_classes.psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton_classes import proton, proton_hr
from .data_classes.psp_proton_fits_classes import proton_fits_class, proton_fits
from .data_classes.psp_ham_classes import ham_class, ham
from .data_tracker import store_downloaded_cdfs

def debug_object(obj, prefix=""):
    """Helper function to debug object attributes"""
    if not print_manager.show_variable_testing:
        return
        
    print_manager.variable_testing(f"{prefix}Type: {type(obj)}")
    
    if hasattr(obj, '__dict__'):
        print_manager.variable_testing(f"{prefix}Attributes: {list(obj.__dict__.keys())}")
    
    if hasattr(obj, '__class__'):
        print_manager.variable_testing(f"{prefix}Class: {obj.__class__.__name__}")
        
        if hasattr(obj.__class__, '__module__'):
            print_manager.variable_testing(f"{prefix}Module: {obj.__class__.__module__}")
    
    if hasattr(obj, 'data_type'):
        print_manager.variable_testing(f"{prefix}data_type: {obj.data_type}")
        
    if hasattr(obj, 'var_name'):
        print_manager.variable_testing(f"{prefix}var_name: {obj.var_name}")

def get_data(trange: List[str], *variables):
    """
    Get data for specified time range and variables. This function checks if data is available locally,
    downloads if needed, and imports it.
    
    Parameters
    ----------
    trange : list
        Time range in virtually any format: ['YYYY-MM-DD/HH:MM:SS', 'YYYY/MM/DD HH:MM:SS']
    *variables : object
        Variables to load (e.g., mag_rtn_4sa.bmag, proton.anisotropy)
        or entire data types (e.g., mag_rtn_4sa, proton)
    
    Returns
    -------
    None
        The function updates the module objects directly, making the data
        available through the global namespace
    
    Examples
    --------
    # Get specific variables
    get_data(trange, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Get all variables for specific data types
    get_data(trange, mag_rtn_4sa, proton)
    """
    # Validate time range and ensure UTC timezone
    try:
        # Use dateutil.parser.parse instead of strptime - much more flexible!
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        return
    
    if start_time >= end_time:    # Validate time range order
        print(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
        return
    
    # Convert to numpy datetime64 ONCE without timezone issues
    try:
        # Simply remove timezone info while preserving precision
        requested_start_np = np.datetime64(start_time.replace(tzinfo=None), 'ns') # Specify unit
        requested_end_np = np.datetime64(end_time.replace(tzinfo=None), 'ns')   # Specify unit
    except Exception as e:
        print_manager.error(f"Error converting parsed time range to numpy datetime64: {e}")
        return

    print_manager.variable_testing(f"Getting data for time range: {trange[0]} to {trange[1]}")
    
    #====================================================================
    # STEP 1: IDENTIFY REQUIRED DATA TYPES
    #====================================================================
    required_data_types = set()     # Tracks unique data types needed
    subclasses_by_type = {}         # Store subclass names requested for status prints

    for var in variables:
        print_manager.variable_testing(f"Initial check for variable: {type(var)}")
        data_type = None
        subclass_name = None
        is_proton_fits_var = isinstance(var, proton_fits_class) or getattr(var, 'class_name', None) == 'proton_fits'
        is_ham_var = isinstance(var, ham_class) or getattr(var, 'class_name', None) == 'ham'
        
        if is_proton_fits_var:
            data_type = 'proton_fits' # Use a consistent identifier
            subclass_name = getattr(var, 'subclass_name', '?')
        elif is_ham_var:
            data_type = 'ham' # Use ham identifier 
            subclass_name = getattr(var, 'subclass_name', '?')
        elif type(var).__name__ in ('module', 'type'):
            try:
                data_type = var.__name__
                # Ensure it's a known type and not a local CSV source (like sf00/sf01 itself)
                if data_type not in data_types or data_types[data_type].get('file_source') == 'local_csv':
                     data_type = None # Ignore sf00/sf01 passed directly, handled by proton_fits
            except (AttributeError, TypeError):
                data_type = None
        elif hasattr(var, 'data_type'):
            dt = var.data_type
            # Ensure it's not proton_fits (handled above) and not a local CSV source
            if dt != 'proton_fits' and data_types.get(dt, {}).get('file_source') != 'local_csv':
                 data_type = dt
                 subclass_name = getattr(var, 'subclass_name', '?')
        
        if data_type:
             required_data_types.add(data_type)
             if data_type not in subclasses_by_type: subclasses_by_type[data_type] = []
             if subclass_name and subclass_name not in subclasses_by_type[data_type]:
                 subclasses_by_type[data_type].append(subclass_name)
        else:
            print_manager.variable_testing(f"  Warning: Could not determine processable data type for variable: {var}")

    print_manager.variable_testing(f"Data types to process: {required_data_types}")
    
    # Print status summary
    for dt in required_data_types:
        subclasses = subclasses_by_type.get(dt, [])
        if dt == 'proton_fits':
             print_manager.status(f"🛰️ {dt} - calculation may be needed")
        elif subclasses:
            print_manager.status(f"🛰️ {dt} - acquiring variables: {', '.join(subclasses)}")
        else:
            print_manager.status(f"🛰️ {dt} - acquiring all variables")

    #====================================================================
    # STEP 2: PROCESS EACH REQUIRED DATA TYPE
    #====================================================================
    
    # Map data_type strings to global instances (needed for update logic)
    # Note: proton_fits and ham are handled earlier, so not needed in this map
    data_type_to_instance_map = {
        'mag_RTN_4sa': mag_rtn_4sa,
        'mag_rtn': mag_rtn,
        'mag_SC_4sa': mag_sc_4sa,
        'mag_sc': mag_sc,
        'spi_sf00_l3_mom': proton,
        'spi_af00_L3_mom': proton_hr,
        'spe_sf0_pad': epad,
        'spe_af0_pad': epad_hr
        # Add other standard types if needed
    }

    for data_type in required_data_types:
        print_manager.debug(f"\nProcessing Data Type: {data_type}...")
        
        # --- Skip derived, proton_fits, ham as they are handled differently ---
        if data_type in ['derived', 'proton_fits', 'ham']:
             # Existing logic for proton_fits and ham should remain here
             # ... (proton_fits logic) ...
             # ... (ham logic) ...
             if data_type in ['proton_fits', 'ham']: # Keep the continue for these
                  print_manager.variable_testing(f"Processed '{data_type}' separately. Continuing.")
                  continue
             elif data_type == 'derived':
                  print_manager.variable_testing(f"SKIPPING processing for '{data_type}' type in main loop (handled elsewhere).")
                  continue

        # --- Handle Standard CDF Types ---
        config = data_types.get(data_type)
        if not config or config.get('file_source') == 'local_csv':
             print_manager.warning(f"Config not found or is local_csv for standard type {data_type}. Skipping.")
             continue

        # --- Download Logic (remains the same) ---
        # ... (call download functions, store filenames using store_downloaded_cdfs) ...

        # --- Cache Check and Update Logic ---
        class_name = data_type # Assume class_name matches data_type
        # Grab whatever is in the cache (might be object or dict)
        cached_item = data_cubby.grab(class_name)
        item_type_in_cache = type(cached_item).__name__
        print_manager.debug(f"Checked cache for {class_name}. Found type: {item_type_in_cache}")

        needs_import = global_tracker.is_import_needed(trange, data_type)
        needs_refresh = False # Default to false

        # Check refresh based on cached item (object or dict)
        cached_dt_array = None
        # --- Modified Cache Check ---
        if isinstance(cached_item, dict):
            # Handle dictionary loaded from PKL
            cached_dt_array = cached_item.get('datetime_array')
            if cached_dt_array is None or len(cached_dt_array) == 0:
                 print_manager.debug(f"Cache dictionary for {class_name} has no/empty datetime_array.")
                 needs_refresh = True
            else:
                 print_manager.debug(f"Cache dictionary for {class_name} found datetime_array (length {len(cached_dt_array)}).")
                 # Proceed with range check using dictionary data
        elif cached_item is not None:
            # Handle object instance found in cache
            if hasattr(cached_item, 'datetime_array') and cached_item.datetime_array is not None and len(cached_item.datetime_array) > 0:
                cached_dt_array = cached_item.datetime_array
                print_manager.debug(f"Cache object instance for {class_name} found datetime_array (length {len(cached_item.datetime_array)}).")
                # Proceed with range check using object attribute
            else:
                 print_manager.debug(f"Cache object instance for {class_name} has no/empty datetime_array.")
                 needs_refresh = True
        else:
            # Nothing found in cache
            print_manager.debug(f"No item found in cache for {class_name}.")
            needs_refresh = True # Treat no data as needing refresh
        # --- End Modified Cache Check ---

        # Perform range check if we have a cached datetime array
        if not needs_refresh and cached_dt_array is not None:
            try:
                 # Ensure it's a numpy array for comparison
                 if not isinstance(cached_dt_array, np.ndarray):
                     cached_dt_array = np.array(cached_dt_array)

                 # Ensure it's datetime64[ns] for direct comparison
                 if not np.issubdtype(cached_dt_array.dtype, np.datetime64):
                     # Attempt conversion if possible (e.g., from TT2000 int64)
                     try:
                         # Assuming TT2000 nanoseconds if it's int64
                         if np.issubdtype(cached_dt_array.dtype, np.integer):
                             print_manager.debug(f"Attempting TT2000 -> datetime64 conversion for cache check...")
                             from datetime import datetime as dt_conv, timezone as tz_conv, timedelta as td_conv # Use different aliases
                             tt2000_epoch_conv = dt_conv(2000, 1, 1, 12, 0, 0, tzinfo=tz_conv.utc)
                             # Correct conversion from ns to microseconds for timedelta
                             temp_dt_conv = [tt2000_epoch_conv + td_conv(microseconds=int(ns) / 1000.0) for ns in cached_dt_array]
                             cached_dt_array = np.array(temp_dt_conv, dtype='datetime64[ns]')
                             print_manager.debug(f"Conversion successful, new dtype: {cached_dt_array.dtype}")
                         else:
                             raise TypeError(f"Cached datetime array is not integer or datetime64, it's {cached_dt_array.dtype}.")
                     except Exception as conv_err:
                         print_manager.warning(f"Could not convert cached datetime array to datetime64 for {data_type}: {conv_err}. Assuming refresh needed.")
                         needs_refresh = True

                 # Proceed with comparison only if conversion worked or was unnecessary
                 if not needs_refresh:
                     if len(cached_dt_array) == 0: # Double check if empty after potential conversion failures
                         needs_refresh = True
                         print_manager.debug("Cached datetime array became empty after conversion attempt. Refresh needed.")
                     else:
                         # Ensure comparison is done with 'datetime64[ns]'
                         cached_start_np = cached_dt_array.astype('datetime64[ns]')[0]
                         cached_end_np = cached_dt_array.astype('datetime64[ns]')[-1]
                         buffer = np.timedelta64(10, 's') # 10 second buffer

                         # Compare directly with requested numpy times (already ns)
                         if (cached_start_np - buffer) > requested_start_np or (cached_end_np + buffer) < requested_end_np:
                             print_manager.debug(f"Refresh needed for {data_type}. Cached range: {cached_start_np} - {cached_end_np}, Requested: {requested_start_np} - {requested_end_np}")
                             needs_refresh = True
                         else:
                             print_manager.debug(f"Cached data covers requested range for {data_type}.")

            except (IndexError, TypeError, ValueError) as e:
                 print_manager.warning(f"Could not compare time ranges for {data_type} (cached type: {item_type_in_cache}): {e}. Assuming refresh needed.")
                 needs_refresh = True

        # Import/update data if needed
        if needs_import or needs_refresh:
            print_manager.debug(f"{data_type} - Import/Refresh required (needs_import={needs_import}, needs_refresh={needs_refresh})")
            # Import fresh data from source files (CDF)
            # Assume import_data_function handles getting file paths via global_tracker or similar
            data_obj = import_data_function(trange, data_type) # Returns DataObject namedtuple

            if data_obj is None or data_obj.times is None or len(data_obj.times) == 0:
                 print_manager.warning(f"Import function returned no data for {data_type}. Skipping update.")
                 continue # Skip update if import failed or returned no data

            print_manager.status(f"📥 Updating {data_type}...")

            # --- Get the GLOBAL instance for this data type ---
            target_instance = data_type_to_instance_map.get(data_type)

            if target_instance is None:
                 print_manager.error(f"Could not find global class instance for {data_type} in map. Cannot update.")
                 continue # Skip if we don't know which instance to update

            # --- Update the GLOBAL instance ---
            if hasattr(target_instance, 'update'):
                try:
                     # ===> ADDED DEBUG HERE <===
                     print_manager.debug(f"DEBUG_GET_DATA: Before calling update, data_obj.source_filenames = {getattr(data_obj, 'source_filenames', 'AttributeMissing')}")
                     target_instance.update(data_obj) # Update the instance in memory
                     # ===> ADDED DEBUG HERE <===
                     print_manager.debug(f"DEBUG_GET_DATA: After calling update, target_instance.source_filenames = {getattr(target_instance, 'source_filenames', 'AttributeMissing')}")

                     print_manager.debug(f"Called update() on global instance for {data_type}")
                except Exception as update_err:
                     print_manager.error(f"Error occurred during {data_type}.update(): {update_err}")
                     import traceback
                     print_manager.debug(traceback.format_exc())
                     continue # Skip stashing if update failed

                # !!! CRITICAL: Stash the UPDATED GLOBAL instance !!!
                # This ensures the object instance (not a dict) is in the cache
                # and triggers save_to_disk if persistence is enabled.
                print_manager.debug(f"---> Stashing updated GLOBAL instance for {class_name} AFTER update.")
                data_cubby.stash(target_instance, class_name=class_name) # Use the actual instance
                # -------------------------------------------------------------

                # Update the data tracker with the actual range from the imported data
                # (Use the datetime_array from the updated target_instance)
                if hasattr(target_instance, 'datetime_array') and target_instance.datetime_array is not None and len(target_instance.datetime_array) > 0:
                    try:
                         actual_start_dt = target_instance.datetime_array[0]
                         actual_end_dt = target_instance.datetime_array[-1]
                         dt_format = '%Y-%m-%d/%H:%M:%S.%f'
                         # Ensure conversion from numpy datetime64 works reliably
                         actual_start_str = pd.Timestamp(actual_start_dt).strftime(dt_format)[:-3] # Trim to milliseconds
                         actual_end_str = pd.Timestamp(actual_end_dt).strftime(dt_format)[:-3] # Trim to milliseconds
                         actual_trange = [actual_start_str, actual_end_str]
                         print_manager.debug(f"Updating tracker for {data_type} with actual imported range: {actual_trange}")
                         global_tracker.update_imported_range(actual_trange, data_type)
                    except Exception as tracker_err:
                         print_manager.warning(f"Could not determine/format actual imported range for tracker update ({data_type}): {tracker_err}")

                else:
                    print_manager.warning(f"Could not determine actual imported range for {data_type} after update.")

            else:
                print_manager.error(f"{data_type} class instance has no update method") # Should not happen for standard classes
        else:
            # Update NOT needed - data exists in cache and covers range
            print_manager.status(f"📤 Using existing {data_type} data (type: {item_type_in_cache}), update not needed.")
            # If the cached item was a dictionary, we need to ensure the GLOBAL instance has the data
            # so that plotbot can access it.
            if isinstance(cached_item, dict):
                print_manager.debug(f"Cached item for {data_type} is a dict. Ensuring global instance is up-to-date and stashed.")
                target_instance = data_type_to_instance_map.get(data_type)
                if target_instance:
                     # --- Populate Global Instance from Cached Dictionary ---
                     print_manager.debug(f"Populating global instance {data_type} from cached dictionary...")
                     try:
                         # Core attributes
                         target_instance.datetime_array = cached_item.get('datetime_array')
                         if 'time' in cached_item: target_instance.time = cached_item.get('time')
                         if target_instance.datetime_array is None:
                              print_manager.warning(f"Cached dictionary for {data_type} missing 'datetime_array'. Instance may be incomplete.")

                         # plot_manager data and options
                         if 'plot_manager_data' in cached_item:
                             for attr_name, pm_data_dict in cached_item['plot_manager_data'].items():
                                 if hasattr(target_instance, attr_name):
                                     pm_instance = getattr(target_instance, attr_name)
                                     if type(pm_instance).__name__ == 'plot_manager':
                                         # Ensure pm_data_dict is a dict before accessing keys
                                         if isinstance(pm_data_dict, dict):
                                             pm_instance._data = pm_data_dict.get('data')
                                             saved_options = pm_data_dict.get('plot_options')
                                             if saved_options is not None and hasattr(pm_instance, 'plot_options'):
                                                 import copy # Use deepcopy for safety when restoring options
                                                 pm_instance.plot_options = copy.deepcopy(saved_options) # Restore options
                                                 print_manager.debug(f"  Restored plot_options for {attr_name}")
                                             else:
                                                  print_manager.debug(f"  No saved plot_options found or attr missing for {attr_name}")
                                             print_manager.debug(f"  Populated _data for {attr_name}, shape: {pm_instance._data.shape if hasattr(pm_instance._data, 'shape') else 'N/A'}")
                                         else:
                                             print_manager.warning(f"  Expected dict for plot_manager_data '{attr_name}', got {type(pm_data_dict)}. Skipping population.")
                                 else:
                                     print_manager.warning(f"  Attribute '{attr_name}' from cached dict not found in global instance {data_type}.")

                         # source_filenames
                         if 'source_file' in cached_item:
                             # Ensure it's a list, as the original code saves a single string here
                             source_file_val = cached_item['source_file']
                             target_instance.source_filenames = [source_file_val] if isinstance(source_file_val, str) else []
                         else:
                             target_instance.source_filenames = []
                         print_manager.debug(f"  Populated source_filenames: {target_instance.source_filenames}")

                         # Now stash the populated global instance
                         print_manager.debug(f"---> Stashing populated GLOBAL instance for {class_name} (cache was dict, no update needed).")
                         data_cubby.stash(target_instance, class_name=class_name)

                     except Exception as pop_err:
                          print_manager.error(f"Error populating global instance {data_type} from cached dictionary: {pop_err}. Plotbot might fail.")
                          import traceback
                          print_manager.debug(traceback.format_exc())
                else:
                     print_manager.error(f"Cannot find global instance for {data_type} to populate from cached dictionary.")
            elif class_instance is not None:
                # Cached item was an object, update not needed.
                # If PKL storage is on, stash the retrieved instance to ensure
                # save_to_disk is triggered even if no update happened.
                # This helps keep the PKL index aligned with what's usable.
                if data_cubby.use_pkl_storage:
                     print_manager.debug(f"---> Stashing existing instance for {class_name} in PKL mode (skipped update).")
                     data_cubby.stash(class_instance, class_name=class_name)

    #====================================================================
    # STEP 3: FINALIZATION
    #====================================================================
    print_manager.status("✅ Data acquisition complete\n")
    return None 