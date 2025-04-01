import sys
import os
import numpy as np
from datetime import datetime, timezone
from typing import List, Union, Optional, Dict, Any, Tuple
from dateutil.parser import parse

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_cubby import data_cubby
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .psp_data_types import data_types
from .psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .psp_electron_classes import epad, epad_hr
from .psp_proton_classes import proton, proton_hr

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
    
    print_manager.variable_testing(f"Getting data for time range: {trange[0]} to {trange[1]}")
    
    #====================================================================
    # PROCESS VARIABLE ARGUMENTS AND BUILD DATA STRUCTURES
    #====================================================================
    required_data_types = set()     # Tracks unique data types needed across all variables
    subclasses_by_type = {}         # Initialize empty dictionary to store subclass lists
    
    # First, handle the case where the user passed in a data type rather than variables
    for var in variables:
        if type(var).__name__ in ('module', 'type'):
            # This is likely a data type module or class, not a variable
            try:
                data_type = var.__name__
                print_manager.variable_testing(f"Processing data type module: {data_type}")
                required_data_types.add(data_type)
                if data_type not in subclasses_by_type:
                    subclasses_by_type[data_type] = []
                continue
            except (AttributeError, TypeError):
                pass
                
        # Process variables with data_type attribute (plot_manager instances)
        if hasattr(var, 'data_type'):
            data_type = var.data_type
            print_manager.variable_testing(f"Processing variable with data_type: {data_type}")
            required_data_types.add(data_type)
            
            # Add to subclasses if it has subclass_name
            if hasattr(var, 'subclass_name'):
                if data_type not in subclasses_by_type:
                    subclasses_by_type[data_type] = []
                subclasses_by_type[data_type].append(var.subclass_name)
        else:
            print_manager.variable_testing(f"Warning: Could not determine data type for {var}")
    
    print_manager.variable_testing(f"Data types required: {required_data_types}")
    
    # Print data types being requested
    for data_type in required_data_types:
        subclasses = subclasses_by_type.get(data_type, [])
        if subclasses:
            print_manager.status(f"🛰️ {data_type} - acquiring variables: {', '.join(subclasses)}")
        else:
            print_manager.status(f"🛰️ {data_type} - acquiring all variables")
    
    #====================================================================
    # DOWNLOAD AND PROCESS DATA
    #====================================================================
    
    for data_type in required_data_types:
        print_manager.debug(f"\nProcessing {data_type}...")
        print_manager.variable_testing(f"About to process data_type: {data_type}")
        
        # Skip download and import for derived variables
        if data_type == 'derived':
            print_manager.variable_testing(f"DERIVED data type detected - SKIPPING download and import")
            print_manager.status(f"📤 Using derived variable, no download/import needed")
            continue
            
        # Check if data_type is in psp_data_types
        print_manager.variable_testing(f"Checking if {data_type} is in psp_data_types: {data_type in data_types}")
        
        if data_type not in data_types:
            print_manager.variable_testing(f"Data type {data_type} not found in psp_data_types")
            continue
        
        # Download data if needed
        download_new_psp_data(trange, data_type)
        
        # Try to get class instance name
        class_name = data_type  # Most common case is that class_name matches data_type
        
        # Get the class instance from data_cubby
        class_instance = data_cubby.grab(class_name)
        print_manager.variable_testing(f"Retrieved class instance from data_cubby: {getattr(class_instance, '__class__', None) and class_instance.__class__.__name__}")
        
        # Check if we need to import or if cached data is outside our range
        needs_import = global_tracker.is_import_needed(trange, data_type)
        needs_refresh = False
        print_manager.variable_testing(f"Import needed for {data_type}: {needs_import}")
        
        if class_instance is not None and hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
            print_manager.variable_testing(f"Class instance has datetime_array of length: {len(class_instance.datetime_array)}")
            cached_start = np.datetime64(class_instance.datetime_array[0], 's')
            cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
            requested_start = np.datetime64(start_time, 's')
            requested_end = np.datetime64(end_time, 's')
            
            # Add 10s buffer to handle instrument timing differences
            buffered_start = cached_start - np.timedelta64(10, 's')
            buffered_end = cached_end + np.timedelta64(10, 's')
            
            if buffered_start > requested_start or buffered_end < requested_end:
                print_manager.variable_testing(f"{data_type} - Requested time falls outside cached data range, updating...")
                needs_refresh = True
        else:
            print_manager.variable_testing(f"No valid cached data for {data_type}, import required")
            needs_refresh = True
        
        # Import/update data if needed
        if needs_import or needs_refresh:
            # Import new data
            print_manager.debug(f"{data_type} - {'Import required' if needs_import else 'Refresh required'}")
            print_manager.variable_testing(f"About to call import_data_function for {data_type}")
            
            data_obj = import_data_function(trange, data_type)
            if data_obj is None:
                print_manager.variable_testing(f"No data returned from import for {data_type}")
                continue
                
            print_manager.variable_testing(f"Data object returned from import: {type(data_obj)}")
            
            if needs_import:
                global_tracker.update_imported_range(trange, data_type)
            
            # Update with new data
            print_manager.status(f"📥 Updating {data_type}...")
            
            # If we don't have a class instance yet, we need to instantiate it
            if class_instance is None:
                # Try to instantiate the class if it's one of the standard ones
                if data_type.lower() == 'mag_rtn_4sa':
                    class_instance = mag_rtn_4sa
                elif data_type.lower() == 'mag_rtn':
                    class_instance = mag_rtn
                elif data_type.lower() == 'mag_sc_4sa':
                    class_instance = mag_sc_4sa
                elif data_type.lower() == 'mag_sc':
                    class_instance = mag_sc
                elif data_type.lower() == 'spi_sf00_l3_mom':
                    class_instance = proton
                elif data_type.lower() == 'spi_af00_l3_mom':
                    class_instance = proton_hr
                elif data_type.lower() == 'spe_sf0_pad':
                    class_instance = epad
                elif data_type.lower() == 'spe_af0_pad':
                    class_instance = epad_hr
                    
                print_manager.variable_testing(f"Created class instance for {data_type}")
            
            # Update the class instance with the new data
            if hasattr(class_instance, 'update'):
                print_manager.variable_testing(f"Updating {data_type} with new data")
                class_instance.update(data_obj)
            else:
                print_manager.variable_testing(f"Warning: {data_type} class instance doesn't have an update method")
            
        else:
            # Use existing data and calculations
            print_manager.status(f"📤 Using existing variables, data update not needed for this time range")
    
    print_manager.status("✅ Data acquisition complete\n")
    return None 