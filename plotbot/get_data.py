# plotbot/get_data.py

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
# Import plotbot with a clear module name to avoid name conflicts
import plotbot as pb
# The import below doesn't work, so we'll use plotbot.config directly
# from . import config  # Add explicit import for config
from .data_import import import_data_function
from .data_classes.psp_data_types import data_types
from .data_classes.psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton_classes import proton, proton_hr
from .data_classes.psp_proton_fits_classes import proton_fits_class, proton_fits
from .data_classes.psp_ham_classes import ham_class, ham

from .zarr_storage import ZarrStorage
# ✨Initialize ZarrStorage for persistent caching✨
zarr_storage = ZarrStorage()

def normalize_case(s):
    """Helper to normalize case for consistent comparisons"""
    return s.lower() if isinstance(s, str) else s

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
    print_manager.zarr_integration("TRACE: get_data function entry point")
    print_manager.zarr_integration(f"INPUT: trange={trange}, variables={variables}")
    # Debug the required_data_types issue
    if variables:
        print(f"Variable type: {type(variables[0])}, name: {getattr(variables[0], '__name__', 'unknown')}")
    
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
    print_manager.zarr_integration(f"[get_data] required_data_types: {required_data_types}")
    
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
        print_manager.zarr_integration(f"\nProcessing Data Type: {data_type}...")
        
        # --- Handle FITS Calculation Type --- 
        if data_type == 'proton_fits':
            fits_calc_key = 'proton_fits'
            fits_calc_trigger = 'fits_calculated'
            
            # Check if calculation needs to run (using tracker AND refresh logic)
            calculation_needed_by_tracker = global_tracker.is_calculation_needed(trange, fits_calc_key)
            proton_fits_needs_refresh = False
            if hasattr(proton_fits, 'datetime_array') and proton_fits.datetime_array is not None and len(proton_fits.datetime_array) > 0:
                try:
                    cached_start = np.datetime64(proton_fits.datetime_array[0])
                    cached_end = np.datetime64(proton_fits.datetime_array[-1])
                    buffer = np.timedelta64(10, 's')
                    # Use pre-converted numpy values for comparison
                    if (cached_start - buffer) > requested_start_np or (cached_end + buffer) < requested_end_np:
                        proton_fits_needs_refresh = True
                except (IndexError, TypeError, ValueError) as e:
                    print_manager.warning(f"Could not compare proton_fits ranges: {e}. Assuming refresh needed.")
                    proton_fits_needs_refresh = True
            else:
                proton_fits_needs_refresh = True # No data means refresh needed

            if calculation_needed_by_tracker or proton_fits_needs_refresh:
                print_manager.debug(f"FITS Calculation required for {trange} (Triggered by {data_type}).")
                data_obj_fits = import_data_function(trange, fits_calc_trigger)
                
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
                print_manager.status(f"📤 Using existing {fits_calc_key} data, calculation not needed.")
                
            # Continue to next data_type - processing for proton_fits is done
            continue 

        # --- Handle HAM CSV Data Type --- 
        if data_type == 'ham':
            ham_key = 'ham'
            
            # Check if update is needed
            ham_needs_refresh = False
            if hasattr(ham, 'datetime_array') and ham.datetime_array is not None and len(ham.datetime_array) > 0:
                try:
                    cached_start = np.datetime64(ham.datetime_array[0])
                    cached_end = np.datetime64(ham.datetime_array[-1])
                    buffer = np.timedelta64(10, 's')
                    # Use pre-converted numpy values for comparison
                    if (cached_start - buffer) > requested_start_np or (cached_end + buffer) < requested_end_np:
                        ham_needs_refresh = True
                except (IndexError, TypeError, ValueError) as e:
                    print_manager.warning(f"Could not compare ham time ranges: {e}. Assuming refresh needed.")
                    ham_needs_refresh = True
            else:
                ham_needs_refresh = True # No data means refresh needed

            if ham_needs_refresh:
                print_manager.debug(f"Ham data update required for {trange}.")
                data_obj_ham = import_data_function(trange, 'ham')
                
                if data_obj_ham:
                    print_manager.status(f"📥 Updating {ham_key} with CSV data...")
                    if hasattr(ham, 'update'):
                        ham.update(data_obj_ham)
                        print_manager.variable_testing(f"Successfully updated {ham_key}.")
                    else:
                        print_manager.error(f"Error: {ham_key} instance has no 'update' method!")
                else:
                    print_manager.warning(f"Ham data import returned no data for {trange}.")
            else:
                print_manager.status(f"📤 Using existing {ham_key} data, update not needed.")
                
            # Continue to next data_type - processing for ham is done
            continue

        # --- Handle Standard CDF Types --- 
        config = data_types.get(data_type)
        if not config:
            # Try case-insensitive lookup
            data_type_lower = normalize_case(data_type)
            for dt in data_types:
                if normalize_case(dt) == data_type_lower:
                    config = data_types[dt]
                    break
        if not config:
            print_manager.warning(f"Config not found for standard type {data_type} during processing loop.")
            continue
        # Ensure this is not a local_csv source being processed here
        if config.get('file_source') == 'local_csv':
            print_manager.warning(f"Skipping standard processing for local_csv type {data_type}. Should be handled by proton_fits.")
            continue
            
        # Get class instance from data_cubby
        class_name = config.get('class_instance_name')
        if class_name is None:
            print_manager.warning(f"No class_instance_name defined for {data_type}")
            continue
            
        class_instance = data_cubby.grab(class_name)
            
        # Check if import/refresh needed
        needs_import = global_tracker.is_import_needed(trange, data_type)
        needs_refresh = False

        # Check refresh based on instance data range
        if class_instance is not None and hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None and len(class_instance.datetime_array) > 0:
            try:
                cached_start = np.datetime64(class_instance.datetime_array[0])
                cached_end = np.datetime64(class_instance.datetime_array[-1])
                buffer = np.timedelta64(10, 's')
                # Use pre-converted numpy values for comparison
                if (cached_start - buffer) > requested_start_np or (cached_end + buffer) < requested_end_np:
                    needs_refresh = True
            except (IndexError, TypeError, ValueError) as e:
                print_manager.warning(f"Could not compare time ranges for {data_type}: {e}. Assuming refresh needed.")
                needs_refresh = True
        else:
            needs_refresh = True # Treat no data as needing refresh

        # Import/update CDF data if needed
        print_manager.zarr_integration(f"[get_data] {data_type}: needs_import={needs_import}, needs_refresh={needs_refresh}")
        if needs_import or needs_refresh:
            print_manager.zarr_integration(f"[get_data] Import/Refresh logic triggered for {data_type}")
            # First try loading from Zarr storage
            zarr_data = zarr_storage.load_data(data_type, trange)
            
            if zarr_data is not None:
                print_manager.status(f"📥 Loading {data_type} from Zarr storage...")
                
                # Make sure we have a class instance
                if class_instance is None:
                    print_manager.zarr_integration(f"Attempting to locate global {class_name} instance...")
                    
                    # Try to find instance in the global namespace via plotbot
                    if hasattr(pb, class_name):
                        class_instance = getattr(pb, class_name)
                        print_manager.status(f"Found {class_name} in global namespace")
                    else:
                        print_manager.warning(f"Could not find {class_name} in global namespace")
                        continue
                
                # Update instance with Zarr data
                if hasattr(class_instance, 'update'):
                    print_manager.zarr_integration(f"[get_data] Calling update on {class_name} with data_obj for {data_type}")
                    class_instance.update(zarr_data)
                    print_manager.zarr_integration(f"[get_data] Update completed for {class_name}")
                    # Store to Zarr for future use
                    print_manager.zarr_integration(f"[get_data] Calling store_data for {data_type}")
                    zarr_result = zarr_storage.store_data(class_instance, data_type, trange)
                    print_manager.zarr_integration(f"[get_data] store_data result for {data_type}: {'Success' if zarr_result else 'Failed'}")
                    if zarr_result:
                        print_manager.status(f"✅ {data_type} data saved to Zarr storage")
                else:
                    print_manager.warning(f"{class_name} instance has no update method")
            else:
                print_manager.zarr_integration(f"Zarr data not available for {data_type}, proceeding with normal download...")
            
            # Conditional data download based on configuration
            server_mode = pb.config.data_server.lower() 
            print_manager.zarr_integration(f"Server mode for {data_type}: {server_mode}")
            
            download_successful = False # Assume files might exist locally

            if server_mode == 'spdf':
                print_manager.zarr_integration(f"Attempting SPDF download for {data_type}...")
                download_successful = download_spdf_data(trange, data_type)
                print_manager.zarr_integration(f"SPDF download result for {data_type}: {'Success' if download_successful else 'Failed'}")
            elif server_mode == 'berkeley':
                print_manager.zarr_integration(f"Attempting Berkeley download for {data_type}...")
                print_manager.zarr_integration(f"Berkeley download parameters - trange: {trange}, data_type: {data_type}")
                download_successful = download_berkeley_data(trange, data_type)
                print_manager.zarr_integration(f"Berkeley download result for {data_type}: {'Success' if download_successful else 'Failed'}")
            elif server_mode == 'dynamic':
                print_manager.zarr_integration(f"Attempting SPDF download (dynamic mode) for {data_type}...")
                download_successful = download_spdf_data(trange, data_type)
                print_manager.zarr_integration(f"SPDF download result (dynamic mode) for {data_type}: {'Success' if download_successful else 'Failed'}")
                if not download_successful:
                    print_manager.zarr_integration(f"SPDF download failed/incomplete for {data_type}, falling back to Berkeley...")
                    download_successful = download_berkeley_data(trange, data_type)
                    print_manager.zarr_integration(f"Berkeley fallback download result for {data_type}: {'Success' if download_successful else 'Failed'}")
            else:
                print_manager.warning(f"Invalid config.data_server mode: '{server_mode}'. Defaulting to Berkeley.")
                download_successful = download_berkeley_data(trange, data_type)
                print_manager.zarr_integration(f"Default Berkeley download result for {data_type}: {'Success' if download_successful else 'Failed'}")
            
            # Import the downloaded data
            print_manager.zarr_integration(f"[get_data] Calling import_data_function for {data_type}")
            data_obj = import_data_function(trange, data_type)
            print_manager.zarr_integration(f"[get_data] import_data_function returned: {'Success' if data_obj is not None else 'None'}")
            
            if data_obj is None: 
                print_manager.warning(f"No data returned from import_data_function for {data_type}")
                continue
                
            if needs_import: 
                print_manager.zarr_integration(f"Updating tracker for {data_type}")
                global_tracker.update_imported_range(trange, data_type)
            
            print_manager.status(f"📥 Updating {data_type}...")
            
            # Retry getting class instance if not found earlier
            if class_instance is None:
                print_manager.zarr_integration(f"Retrying to get class instance for {class_name}")
                if hasattr(pb, class_name):
                    class_instance = getattr(pb, class_name)
                    print_manager.status(f"Found {class_name} in global namespace")
                else:
                    print_manager.warning(f"Could not find {class_name} in global namespace")
                    continue

            # Update the instance with downloaded data
            if hasattr(class_instance, 'update'):
                print_manager.zarr_integration(f"[get_data] Calling update on {class_name} with data_obj for {data_type}")
                class_instance.update(data_obj)
                print_manager.zarr_integration(f"[get_data] Update completed for {class_name}")
                
                # Store to Zarr for future use
                print_manager.zarr_integration(f"[get_data] Calling store_data for {data_type}")
                zarr_result = zarr_storage.store_data(class_instance, data_type, trange)
                print_manager.zarr_integration(f"[get_data] store_data result for {data_type}: {'Success' if zarr_result else 'Failed'}")
                if zarr_result:
                    print_manager.status(f"✅ {data_type} data saved to Zarr storage")
            else:
                print_manager.warning(f"{class_name} instance has no update method")
        else:
            print_manager.status(f"📤 Using existing {data_type} data, update not needed.")
    
    #====================================================================
    # STEP 3: FINALIZATION
    #====================================================================
    print_manager.status("✅ Data acquisition complete\n")
    return None 