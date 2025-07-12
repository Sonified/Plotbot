# plotbot/get_data.py

import sys
import os
import numpy as np
from datetime import datetime, timezone
from typing import List, Union, Optional, Dict, Any, Tuple
from dateutil.parser import parse
import pandas as pd
import time as timer
from functools import wraps

def timer_decorator(timer_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timer.perf_counter()
            result = func(*args, **kwargs)
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"⏱️ [{timer_name}] {func.__name__}: {duration_ms:.2f}ms")
            return result
        return wrapper
    return decorator

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_cubby import data_cubby
from .data_download_berkeley import download_berkeley_data
from .data_download_pyspedas import download_spdf_data
import plotbot
from .data_import import import_data_function, DataObject
from .data_classes.data_types import data_types
from .config import config

# Add global step counter for dynamic numbering
_global_step_counter = 0
def next_step(step_name: str, data_type: str = None) -> tuple:
    """Generate next step number and start timing."""
    global _global_step_counter
    _global_step_counter += 1
    step_key = f"Step {_global_step_counter}: {step_name}"
    if data_type:
        step_key += f" ({data_type})"
    step_start = timer.perf_counter()
    print_manager.speed_test(f"🚀 {step_key}")
    return step_key, step_start

def end_step(step_key: str, step_start: float, metadata: dict = None) -> None:
    """End timing for a step."""
    duration_ms = (timer.perf_counter() - step_start) * 1000
    metadata_str = f" - {metadata}" if metadata else ""
    print_manager.speed_test(f"✅ {step_key}: {duration_ms:.2f}ms{metadata_str}")

# Import specific data classes as needed
from . import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton import proton
from .data_classes.psp_proton_hr import proton_hr
from .data_classes.psp_proton_fits_classes import proton_fits_class, proton_fits
from .data_classes.psp_ham_classes import ham_class, ham

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

@timer_decorator("TIMER_GET_DATA_ENTRY")
def get_data(trange: List[str], *variables, skip_refresh_check=False):
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
    skip_refresh_check : bool, optional
        If True, skips the in-memory refresh check for proton_fits (useful after loading from pickle)
    
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
    
    # Skip refresh check after loading from pickle
    get_data(trange, pb.proton_fits.abs_qz_p, skip_refresh_check=True)
    """
    pm = print_manager # Local alias
    
    # Step: Initialize get_data
    step_key, step_start = next_step("Initialize get_data", "get_data")
    
    # Temporary debug for test_proton_trange_updates.py - RE-ADDING BLOCK
    if 'tests.test_proton_trange_updates' in sys.modules:
        test_module = sys.modules['tests.test_proton_trange_updates']
        if getattr(test_module, 'DEBUG_FORCE_STOP_IN_GET_DATA_CALL2', False):
            # Check if any of the requested variables are related to proton/spi_sf00_l3_mom or epad
            is_relevant_call = False
            problematic_vars = []
            for var_item_tuple in variables:
                # variables are now tuples (var_obj, plot_num, subplot_num)
                var_item = var_item_tuple[0] # Get the actual variable object
                if hasattr(var_item, 'data_type') and var_item.data_type in ['spi_sf00_l3_mom', 'epad_omni_diff_flux']:
                    is_relevant_call = True
                    problematic_vars.append(var_item.data_type)
                    break # Found one, no need to check others for this purpose
                if isinstance(var_item, type) and hasattr(var_item, '__name__') and var_item.__name__ in ['proton_class', 'epad_class']:
                     is_relevant_call = True
                     problematic_vars.append(var_item.__name__)
                     break
            
            if is_relevant_call:
                debug_msg = f"[GET_DATA_DEBUG_STOP] TEMP_DEBUG: Controlled stop in get_data during CALL 2 for {problematic_vars} due to DEBUG_FORCE_STOP_IN_GET_DATA_CALL2. TRANGE: {trange}. Returning None."
                print_manager.debug(debug_msg) # Use existing print_manager
                # Ensure this message also goes to capsys if possible, though print_manager should handle it
                print(debug_msg) # Explicit print for safety, might be redundant if print_manager covers console
                return None # Gracefully stop this specific data call

    # Simpler logging for variables to avoid IndexError
    variable_names_for_log = []
    for var_tuple in variables:
        if isinstance(var_tuple, tuple) and len(var_tuple) > 0:
            actual_var = var_tuple[0]
            if hasattr(actual_var, 'name'):
                variable_names_for_log.append(actual_var.name)
            else:
                variable_names_for_log.append(str(actual_var))
        else:
            # Handle cases where var_tuple might not be a tuple or is empty
            variable_names_for_log.append(str(var_tuple)) 

    print_manager.dependency_management(f"[GET_DATA_ENTRY] Original trange: {trange}, variables: {variable_names_for_log}")
    
    end_step(step_key, step_start, {"variables": len(variables), "trange": f"{trange[0]} to {trange[1]}"})

    # STRATEGIC PRINT GET_DATA_ENTRY
    if variables:
        first_var_spec = variables[0]
        # Check if it's one of our data class instances (has class_name and datetime_array)
        if hasattr(first_var_spec, 'class_name') and hasattr(first_var_spec, 'data_type') and hasattr(first_var_spec, 'datetime_array'):
            dt_len_entry = len(first_var_spec.datetime_array) if first_var_spec.datetime_array is not None else "None"
            min_dt_entry = first_var_spec.datetime_array[0] if dt_len_entry not in ["None", 0] else "N/A"
            max_dt_entry = first_var_spec.datetime_array[-1] if dt_len_entry not in ["None", 0] else "N/A"
            pm.dependency_management(f"[GET_DATA_ENTRY] Instance {getattr(first_var_spec, 'data_type', 'N/A')} (ID: {id(first_var_spec)}) passed in. Len: {dt_len_entry}, Min: {min_dt_entry}, Max: {max_dt_entry}")
        elif isinstance(first_var_spec, str): # It's a data_type string
            pm.dependency_management(f"[GET_DATA_ENTRY] Called with data_type string: {first_var_spec}")

    # Step: Validate time range
    step_key, step_start = next_step("Validate time range")
    
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
        requested_start_np = np.datetime64(start_time.replace(tzinfo=None))
        requested_end_np = np.datetime64(end_time.replace(tzinfo=None))
    except Exception as e:
        print_manager.error(f"Error converting parsed time range to numpy datetime64: {e}")
        return

    print_manager.variable_testing(f"Getting data for time range: {trange[0]} to {trange[1]}")
    
    end_step(step_key, step_start, {"start": trange[0], "end": trange[1]})

    #====================================================================
    # STEP 1: IDENTIFY REQUIRED DATA TYPES
    #====================================================================
    
    # Step: Identify required data types
    step_key, step_start = next_step("Identify required data types")
    
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
                if data_type not in data_types or 'local_csv' in data_types[data_type].get('data_sources', []):
                     data_type = None # Ignore sf00/sf01 passed directly, handled by proton_fits
            except (AttributeError, TypeError):
                data_type = None
        elif hasattr(var, 'data_type'):
            dt = var.data_type
            # Ensure it's not proton_fits (handled above) and not a local CSV source
            if dt != 'proton_fits' and 'local_csv' not in data_types.get(dt, {}).get('data_sources', []):
                 data_type = dt
                 subclass_name = getattr(var, 'subclass_name', '?')
        
        if data_type:
             required_data_types.add(data_type) # Use the identified data type directly

             # Use the identified data type for subclass tracking
             if data_type not in subclasses_by_type: subclasses_by_type[data_type] = []
             if subclass_name and subclass_name not in subclasses_by_type[data_type]:
                 subclasses_by_type[data_type].append(subclass_name)
        else:
            print_manager.variable_testing(f"  Warning: Could not determine processable data type for variable: {var}")

    print_manager.dependency_management(f"[GET_DATA PRE-LOOP] required_data_types set: {required_data_types}")
    
    end_step(step_key, step_start, {"data_types": list(required_data_types), "count": len(required_data_types)})
    
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
    
    for data_type in required_data_types:
        print_manager.dependency_management(f"[GET_DATA IN-LOOP] Current data_type from set: '{data_type}' (Type: {type(data_type)})")
        print_manager.dependency_management(f"Processing Data Type: {data_type}...")
        
        # Step: Process data type
        step_key, step_start = next_step("Process data type", data_type)
        
        # --- Handle FITS Calculation Type --- 
        if data_type == 'proton_fits':
            fits_calc_key = 'proton_fits'
            fits_calc_trigger = 'fits_calculated'
            
            calculation_needed_by_tracker = global_tracker.is_calculation_needed(trange, fits_calc_key)

            if calculation_needed_by_tracker:
                # Step: Calculate FITS data
                fits_step_key, fits_step_start = next_step("Calculate FITS data", data_type)
                
                # print_manager.dependency_management(f"FITS Calculation required for {trange} (Triggered by {data_type}).")
                start_time = timer.perf_counter()
                data_obj_fits = import_data_function(trange, fits_calc_trigger)
                end_time = timer.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                print_manager.speed_test(f"⏱️ import_data_function (FITS): {duration_ms:.2f}ms")
                
                end_step(fits_step_key, fits_step_start, {"duration_ms": duration_ms, "success": data_obj_fits is not None})
                
                if data_obj_fits:
                    print_manager.status(f"📥 Updating {fits_calc_key} with calculated data...")
                    if hasattr(proton_fits, 'update'):
                        proton_fits.update(data_obj_fits)
                        global_tracker.update_calculated_range(trange, fits_calc_key)
                        print_manager.variable_testing(f"Successfully updated {fits_calc_key} and tracker.")
                    else:
                        print_manager.error(f"Error: {fits_calc_key} instance has no 'update' method!")
                else:
                    print_manager.warning(f"FITS calculation returned no data for {trange}.")
            else:
                # Tracker says calculation is NOT needed. Trust the tracker.
                # Optionally, check if in-memory object is empty and warn.
                if not (hasattr(proton_fits, 'datetime_array') and proton_fits.datetime_array is not None and len(proton_fits.datetime_array) > 0):
                    print_manager.warning(f"[DEBUG] Tracker says calculation is NOT needed, but in-memory proton_fits object is empty or missing data. This may indicate a problem with the snapshot or tracker.")
                print_manager.status(f"📤 Using existing {fits_calc_key} data, calculation not needed.")

            end_step(step_key, step_start, {"calculation_needed": calculation_needed_by_tracker})
            # Continue to next data_type - processing for proton_fits is done
            continue 

        # --- Handle Standard CDF Types (and now HAM) --- 
        # data_type here will be e.g., 'spe_sf0_pad' or 'ham'
        print_manager.dependency_management(f"[GET_DATA_CONFIG_CHECK] Attempting to get config for data_type FROM LOOP VAR: '{data_type}'")

        # For 'ham', we bypass the data_types config lookup that's mainly for remote data sources.
        # HAM data is always local CSV handled by import_data_function.
        # We still need to set a cubby_key and proceed to DataCubby interaction.
        if data_type == 'ham':
            cubby_key = 'ham'
            # Download is not applicable for HAM, so set relevant flags accordingly
            # This ensures HAM data directly goes to import_data_function and DataCubby
            # without attempting server downloads.
            # The 'calculation_needed' check via global_tracker is still important.
        else:
            # Standard path for other data types (mostly CDFs)
            print_manager.dependency_management(f"[GET_DATA_CONFIG_CHECK] Available keys in psp_data_types: {list(data_types.keys())}")
            config_from_psp_data_types = data_types.get(data_type) # Renamed to avoid conflict with plotbot.config
            if not config_from_psp_data_types:
                print_manager.warning(f"Config not found in psp_data_types for {data_type} during processing loop.")
                end_step(step_key, step_start, {"error": "config not found"})
                continue
            
            # Ensure this is not a local_csv source being processed here (unless it's specifically HAM, which is handled above)
            if 'local_csv' in config_from_psp_data_types.get('data_sources', []):
                print_manager.warning(f"Skipping standard processing for local_csv type {data_type} (not HAM). Should be handled by proton_fits.")
                end_step(step_key, step_start, {"skipped": "local_csv type"})
                continue
                
            # Determine the canonical key for cubby/tracker interactions
            if data_type == 'spe_sf0_pad':
                cubby_key = 'epad'
            elif data_type == 'spe_af0_pad':
                cubby_key = 'epad_hr'
            elif data_type == 'psp_orbit_data':
                cubby_key = 'psp_orbit'
            # Add other mappings if necessary
            else:
                cubby_key = data_type.lower() # Default to lowercase
        
        # Step: Request data from data cubby
        cubby_step_key, cubby_step_start = next_step("Request data from data cubby", cubby_key)
        
        class_instance = data_cubby.grab(cubby_key) # Use canonical key for CDFs, 'ham' for HAM
        
        end_step(cubby_step_key, cubby_step_start, {"cubby_key": cubby_key, "found": class_instance is not None})
        
        # --- Check Calculation Cache (Applies to HAM as well) ---
        # Use canonical key here too for consistency (cubby_key will be 'ham' for HAM)
        
        # Step: Check calculation cache
        cache_step_key, cache_step_start = next_step("Check calculation cache", data_type)
        
        # DEBUGGING: Print tracker state before check
        print_manager.speed_test(f"TRACKER STATE BEFORE CHECK: {global_tracker.calculated_ranges}")
        
        calculation_needed = global_tracker.is_calculation_needed(trange, data_type)
        
        # DEBUGGING: Print actual tracker check result
        print_manager.speed_test(f"TRACKER CHECK: data_type={data_type}, calculation_needed={calculation_needed}")
        
        end_step(cache_step_key, cache_step_start, {"calculation_needed": calculation_needed})

        if calculation_needed:
            # Check if this is local support data (like NPZ files)
            config_from_psp_data_types = data_types.get(data_type)
            if config_from_psp_data_types and 'local_support_data' in config_from_psp_data_types.get('data_sources', []):
                print_manager.dependency_management(f"Tracker indicates calculation needed for {data_type} (local support data). Skipping download, proceeding to import_data_function.")
            # For HAM, download_successful and server_mode are irrelevant as it's local.
            # The import_data_function handles fetching it.
            # Download logic only for non-HAM and non-support-data types
            elif data_type != 'ham': 
                print_manager.dependency_management(f"Tracker indicates calculation needed for {data_type} (using original type {data_type}). Proceeding with download if applicable...")
                
                # Step: Download data
                download_step_key, download_step_start = next_step("Download data", data_type)
                
                server_mode = plotbot.config.data_server.lower()
                print_manager.dependency_management(f"Server mode for {data_type}: {server_mode}")
                # download_successful = False # download_successful flag is not used later, can be removed
                
                if server_mode == 'spdf':
                    print_manager.status(f"Attempting SPDF acquisition path for {data_type}...")
                    download_spdf_data(trange, data_type) # download_successful = download_spdf_data(trange, data_type)
                elif server_mode == 'berkeley' or server_mode == 'berkley':
                    print_manager.status(f"Attempting Berkeley acquisition path for {data_type}...")
                    download_berkeley_data(trange, data_type) # download_successful = download_berkeley_data(trange, data_type)
                elif server_mode == 'dynamic':
                    print_manager.status(f"Attempting SPDF acquisition path (dynamic mode) for {data_type}...")
                    dl_success_spdf = download_spdf_data(trange, data_type)
                    if not dl_success_spdf:
                        print_manager.status(f"SPDF acquisition path failed/incomplete for {data_type}, falling back to Berkeley...")
                        download_berkeley_data(trange, data_type) # download_successful = download_berkeley_data(trange, data_type)
                else:
                    print_manager.warning(f"Invalid config.data_server mode: '{server_mode}'. Defaulting to Berkeley. Handle invalid mode.")
                    download_berkeley_data(trange, data_type) # download_successful = download_berkeley_data(trange, data_type)
                
                end_step(download_step_key, download_step_start, {"server_mode": server_mode})
            else: # This is for data_type == 'ham'
                print_manager.dependency_management(f"Tracker indicates calculation needed for {data_type} (HAM data). Proceeding to import_data_function.")

            # --- Import/Update Data (Applies to HAM as well) --- 
            # Step: Import/refresh data
            import_step_key, import_step_start = next_step("Import/refresh data", data_type)
            
            print_manager.dependency_management(f"{data_type} - Import/Refresh required") # Use data_type
            start_time = timer.perf_counter()
            if data_type == 'mag_RTN_4sa':
                print_manager.speed_test(f'[TIMER_MAG_4] CDF download/import: {(timer.perf_counter())*1000:.2f}ms')
            if data_type == 'psp_orbit_data':
                print_manager.speed_test(f'[TIMER_ORBIT_4] NPZ file load: {(timer.perf_counter())*1000:.2f}ms')
            data_obj = import_data_function(trange, data_type) # data_type will be 'ham' for HAM
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"[TIMER_IMPORT_DATA_FUNCTION] import_data_function ({data_type}): {duration_ms:.2f}ms")
            
            end_step(import_step_key, import_step_start, {"duration_ms": duration_ms, "success": data_obj is not None})

            if data_obj is None: 
                print_manager.warning(f"Import returned no data for {data_type}, skipping update.")
                # Ensure we don't proceed with a None data_obj to DataCubby for this trange
                # If get_data is called for multiple types in *variables, it will proceed to the next
                # If only one type was requested and it failed, get_data effectively does nothing more for it.
                # The overall_success in the test script will depend on save_data_snapshot failing if data isn't loaded.
                end_step(step_key, step_start, {"error": "import returned no data"})
                continue # This skips the DataCubby update for THIS data_type and trange

            # Step: Update data cubby
            cubby_update_step_key, cubby_update_step_start = next_step("Update data cubby", cubby_key)
            
            # Tell DataCubby to handle the update/merge for the global instance
            # Use canonical key for cubby update
            print_manager.status(f"📥 Requesting DataCubby to update/merge global instance for {cubby_key}...")
            print_manager.dependency_management(f"[GET_DATA PRE-CUBBY CALL] Passing to DataCubby: cubby_key='{cubby_key}', original_requested_trange='{trange}', type(original_requested_trange[0])='{type(trange[0]) if trange and len(trange)>0 else 'N/A'}'")
            start_time = timer.perf_counter()
            update_success = data_cubby.update_global_instance(
                data_type_str=cubby_key, # Use canonical cubby_key
                imported_data_obj=data_obj,
                # is_segment_merge can use default False if not explicitly determined earlier
                original_requested_trange=trange # Pass the original trange
            )
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"[TIMER_UPDATE_GLOBAL_INSTANCE] update_global_instance: {duration_ms:.2f}ms")
            
            end_step(cubby_update_step_key, cubby_update_step_start, {"duration_ms": duration_ms, "success": update_success})

            if update_success:
                pm.status(f"✅ DataCubby processed update for {cubby_key}.")
                global_tracker.update_calculated_range(trange, data_type) # Use data_type for tracker consistency
                # DEBUGGING: Verify tracker was updated
                print_manager.speed_test(f"TRACKER UPDATED: {data_type} for {trange}")
                print_manager.speed_test(f"TRACKER STATE AFTER UPDATE: {global_tracker.calculated_ranges}")
            else:
                pm.warning(f"DataCubby failed to process update for {cubby_key}. Tracker not updated.")
            # --- End Import/Update Data --- 

        else: # Calculation NOT needed
             # Use canonical key in status message
            print_manager.status(f"📤 Using existing {data_type} data, calculation/import not needed.")
        
        end_step(step_key, step_start, {"calculation_needed": calculation_needed})
    
    #====================================================================
    # STEP 3: FINALIZATION
    #====================================================================
    
    # Step: Finalize get_data
    final_step_key, final_step_start = next_step("Finalize get_data")
    
    print_manager.status("✅ Complete")
    
    end_step(final_step_key, final_step_start, {"total_data_types": len(required_data_types)})
    
    return None 