# plotbot/data_cubby.py

from .print_manager import print_manager, format_datetime_for_log
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import inspect
import copy
import cdflib
from typing import Optional, List

# --- Import Data Class Types for Mapping ---
# Assuming these classes are defined elsewhere and accessible
# We need the actual class types, not just the instances
from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa_class
from .data_classes.psp_mag_rtn import mag_rtn_class
from .data_classes.psp_mag_sc_4sa import mag_sc_4sa_class
from .data_classes.psp_mag_sc import mag_sc_class
from .data_classes.psp_electron_classes import epad_strahl_class, epad_strahl_high_res_class
from .data_classes.psp_proton import proton_class
from .data_classes.psp_proton_hr import proton_hr_class
# Note: proton_fits and ham are handled differently in get_data, so maybe not needed here?
# from .data_classes.psp_proton_fits_classes import proton_fits_class
from .data_classes.psp_ham_classes import ham_class, ham
# WIND satellite data classes
from .data_classes.wind_mfi_classes import wind_mfi_h2_class
from .data_classes.wind_3dp_classes import wind_3dp_elpd_class
from .data_classes.wind_3dp_pm_classes import wind_3dp_pm_class
from .data_classes.psp_alpha_classes import psp_alpha_class
from .data_classes.psp_qtn_classes import psp_qtn_class
from .data_classes.psp_dfb_classes import psp_dfb_class
from .data_classes.wind_swe_h5_classes import wind_swe_h5_class
from .data_classes.wind_swe_h1_classes import wind_swe_h1_class

from .data_import import DataObject # Import the type hint for raw data object

# print_manager.show_processing = True # SETTING THIS EARLY
class data_cubby:
    """
    Enhanced data storage system that intelligently manages time series data
    with rigorous type checking and data integrity validation.
    """
    cubby = {}
    class_registry = {}
    subclass_registry = {}

    # --- Map data_type strings to their corresponding class types ---
    _CLASS_TYPE_MAP = {
        'mag_rtn_4sa': mag_rtn_4sa_class,
        'mag_rtn': mag_rtn_class,
        'mag_sc_4sa': mag_sc_4sa_class,
        'mag_sc': mag_sc_class,
        'spi_sf00_l3_mom': proton_class,
        'spi_af00_l3_mom': proton_hr_class,
        'spe_sf0_pad': epad_strahl_class,
        'spe_af0_pad': epad_strahl_high_res_class,
        'proton_hr': proton_hr_class,
        'epad': epad_strahl_class,
        'epad_hr': epad_strahl_high_res_class,
        'ham': ham_class,
        'sqtn_rfs_v1v2': psp_qtn_class,  # QTN (Quasi-Thermal Noise) electron density and temperature
        # PSP FIELDS DFB electric field spectra data types
        'dfb_ac_spec_dv12hg': psp_dfb_class,  # AC spectrum dv12 
        'dfb_ac_spec_dv34hg': psp_dfb_class,  # AC spectrum dv34
        'dfb_dc_spec_dv12hg': psp_dfb_class,  # DC spectrum dv12
        # WIND satellite data types
        'wind_mfi_h2': wind_mfi_h2_class,
        'wind_3dp_elpd': wind_3dp_elpd_class,
        'wind_3dp_pm': wind_3dp_pm_class,
    'spi_sf0a_l3_mom': psp_alpha_class,
        'wind_swe_h5': wind_swe_h5_class,
        'wind_swe_h1': wind_swe_h1_class,
        # Add other standard CDF types here as needed
    }

    def __init__(self):
        """
        Initialize the DataCubby instance.
        This is where we can register pre-existing global data instances
        that DataCubby needs to manage from the start.
        """
        print_manager.datacubby("DataCubby instance initializing...")
        
        # Stash the globally defined `ham` instance.
        # `ham` should be imported at the module level from .data_classes.psp_ham_classes
        # `self.stash` correctly calls the classmethod `stash`.
        try:
            global_ham_instance = globals().get('ham')
            if global_ham_instance is not None and isinstance(global_ham_instance, ham_class):
                self.stash(global_ham_instance, class_name='ham')
                print_manager.datacubby("Successfully stashed global 'ham' instance during DataCubby initialization.")
            else:
                # This warning helps diagnose if `ham` wasn't imported as expected before DataCubby instantiation.
                print_manager.warning("Global 'ham' instance for stashing not found or of incorrect type during DataCubby __init__. Expected 'ham' to be an instance of 'ham_class'.")
        except Exception as e:
            print_manager.error(f"CRITICAL STARTUP ERROR: Failed to stash global 'ham' instance during DataCubby __init__: {e}")
            # Depending on application design, one might want to re-raise e or handle it more severely.

    @classmethod
    def _get_class_type_from_string(cls, data_type_str):
        """Helper to get class type from string using the map."""
        return cls._CLASS_TYPE_MAP.get(data_type_str.lower())

    @classmethod
    def stash(cls, obj, class_name=None, subclass_name=None):
        """Store object with class and subclass tracking, intelligently merging time series data."""
        print_manager.datacubby("\n=== Stashing Debug (INSIDE DATA CUBBY)===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"STASH CALLER: {caller_info}")
        
        # Normalize case of class_name if provided
        if class_name:
            class_name = class_name.lower()
            
        identifier = f"{class_name}.{subclass_name}" if class_name and subclass_name else class_name
        print_manager.datacubby(f"Stashing with identifier: {identifier}")
        
        # Type check for incoming object
        print_manager.datacubby(f"STASH TYPE CHECK - Object type: {type(obj)}")
        
        # Debug datetime_array if present
        if hasattr(obj, 'datetime_array') and obj.datetime_array is not None:
            print_manager.datacubby(f"STASH INPUT - datetime_array type: {type(obj.datetime_array)}")
            if len(obj.datetime_array) > 0:
                print_manager.datacubby(f"STASH INPUT - datetime_array element type: {type(obj.datetime_array[0])}")
                print_manager.datacubby(f"STASH INPUT - datetime_array shape: {obj.datetime_array.shape}")
                print_manager.datacubby(f"STASH INPUT - datetime_array first few elements: {obj.datetime_array[:5]}")
                print_manager.datacubby(f"STASH INPUT - datetime_array range: {obj.datetime_array[0]} to {obj.datetime_array[-1]}")
            else:
                print_manager.datacubby(f"STASH INPUT - datetime_array is empty")
        else:
            print_manager.datacubby(f"STASH INPUT - No datetime_array attribute found")
            
        # Debug raw_data if present
        if hasattr(obj, 'raw_data') and obj.raw_data is not None:
            print_manager.datacubby(f"STASH INPUT - raw_data keys: {obj.raw_data.keys()}")
            for key, value in obj.raw_data.items():
                if isinstance(value, list):
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] is a list of length {len(value)}")
                    if value and len(value) > 0:
                        for i, item in enumerate(value):
                            if hasattr(item, 'shape'):
                                print_manager.datacubby(f"STASH INPUT - raw_data[{key}][{i}] type: {type(item)}, shape: {item.shape}")
                            else:
                                print_manager.datacubby(f"STASH INPUT - raw_data[{key}][{i}] type: {type(item)}")
                elif hasattr(value, 'shape'):
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] type: {type(value)}, shape: {value.shape}")
                else:
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] type: {type(value)}")
        else:
            print_manager.datacubby(f"STASH INPUT - No raw_data attribute found")
        
        # Check if we already have this object and if it has time series data
        print_manager.datacubby(f"STASH MERGE CHECK - Looking for existing object with class_name: {class_name}")
        existing_obj = cls.class_registry.get(class_name)
        
        if existing_obj:
            print_manager.datacubby(f"STASH MERGE CHECK - Found existing object of type: {type(existing_obj)}")
            # Debug existing object datetime_array
            if hasattr(existing_obj, 'datetime_array') and existing_obj.datetime_array is not None:
                if len(existing_obj.datetime_array) > 0:
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array type: {type(existing_obj.datetime_array)}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array element type: {type(existing_obj.datetime_array[0])}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array shape: {existing_obj.datetime_array.shape}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array range: {existing_obj.datetime_array[0]} to {existing_obj.datetime_array[-1]}")
                else:
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array is empty")
            else:
                print_manager.datacubby(f"STASH MERGE CHECK - No existing datetime_array found")
        else:
            print_manager.datacubby(f"STASH MERGE CHECK - No existing object found")
            
        # Perform merge if both objects have datetime_array
        # Get a copy of the existing object for comparison
        existing_obj_copy = copy.deepcopy(existing_obj) if existing_obj else None

        # Perform merge with the copy
        if existing_obj_copy and hasattr(existing_obj_copy, 'datetime_array') and hasattr(obj, 'datetime_array'):
            if existing_obj_copy.datetime_array is not None and obj.datetime_array is not None:
                if len(existing_obj_copy.datetime_array) > 0 and len(obj.datetime_array) > 0:
                    print_manager.datacubby(f"STASH MERGE - Both objects have datetime_array, attempting to merge time series data for {class_name}")
                    
                    # Both existing and new object have time data - attempt to merge them using the copy
                    if cls._merge_arrays(existing_obj_copy.datetime_array, existing_obj_copy.raw_data, obj.datetime_array, obj.raw_data):
                        print_manager.datacubby(f"STASH MERGE - Successfully merged time series data for {class_name}")
                        
                        # Update class registry with the merged result
                        cls.cubby[identifier] = existing_obj_copy
                        if class_name:
                            cls.class_registry[class_name] = existing_obj_copy
                        if subclass_name:
                            cls.subclass_registry[subclass_name] = existing_obj_copy
                        
                        # Final type check for returned object (the merged copy)
                        print_manager.datacubby(f"STASH OUTPUT - Returned object type after merge: {type(existing_obj_copy)}")
                        if hasattr(existing_obj_copy, 'datetime_array') and existing_obj_copy.datetime_array is not None:
                            print_manager.datacubby(f"STASH OUTPUT - Final datetime_array type: {type(existing_obj_copy.datetime_array)}")
                            if len(existing_obj_copy.datetime_array) > 0:
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array element type: {type(existing_obj_copy.datetime_array[0])}")
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array shape: {existing_obj_copy.datetime_array.shape}")
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array range: {existing_obj_copy.datetime_array[0]} to {existing_obj_copy.datetime_array[-1]}")
                        
                        # Return the existing object (the merged copy) since it now contains the merged data
                        print_manager.datacubby("=== End Stashing Debug (LEAVING DATA CUBBY)===\n")
                        return existing_obj_copy # Return the merged copy
                    else:
                        print_manager.datacubby(f"STASH MERGE - Merge attempt failed, proceeding with normal stashing of the new object")
                else:
                    print_manager.datacubby(f"STASH MERGE - One or both datetime_arrays are empty, skipping merge")
            else:
                print_manager.datacubby(f"STASH MERGE - One or both datetime_arrays are None, skipping merge")
        else:
            print_manager.datacubby(f"STASH MERGE - One or both objects missing datetime_array or no existing object, skipping merge")
        
        # If merge didn't happen or failed, proceed with normal stashing of the *new* object
        cls.cubby[identifier] = obj
        if class_name:
            cls.class_registry[class_name] = obj
            print_manager.datacubby(f"STASH STORE - Stored in class_registry: {class_name}")
            
        if subclass_name:
            cls.subclass_registry[subclass_name] = obj
            print_manager.datacubby(f"STASH STORE - Stored in subclass_registry: {subclass_name}")
        
        # Final type check for stored object
        print_manager.datacubby(f"STASH OUTPUT - Stored object type: {type(obj)}")
        if hasattr(obj, 'datetime_array') and obj.datetime_array is not None:
            print_manager.datacubby(f"STASH OUTPUT - Final datetime_array type: {type(obj.datetime_array)}")
            if len(obj.datetime_array) > 0:
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array element type: {type(obj.datetime_array[0])}")
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array shape: {obj.datetime_array.shape}")
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array range: {obj.datetime_array[0]} to {obj.datetime_array[-1]}")
            
        print_manager.datacubby("=== End Stashing Debug (LEAVING DATA CUBBY)===\n")
        return obj
    
    @classmethod
    def _merge_arrays(cls, existing_times, existing_raw_data, new_times, new_raw_data):
        """Merges new time/data arrays into existing ones.
        
        Args:
            existing_times (np.ndarray): Current datetime array.
            existing_raw_data (dict): Dictionary of current data arrays.
            new_times (np.ndarray): New datetime array to merge.
            new_raw_data (dict): Dictionary of new data arrays to merge.
            
        Returns:
            tuple: (merged_times, merged_raw_data) if merge successful, 
                   (None, None) if no merge needed or error occurred.
        """
        print_manager.datacubby("\n=== Array Merge Debug ===")
        # Basic validation
        if new_times is None or len(new_times) == 0 or new_raw_data is None:
            print_manager.datacubby("MERGE ARRAYS ABORTED - New time array or data is None or empty")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None # Cannot merge nothing

        # Handle case where existing data is empty/None
        if existing_times is None or len(existing_times) == 0 or existing_raw_data is None:
            print_manager.datacubby("MERGE ARRAYS INFO - Existing data is empty. Using new data directly.")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            # Return the new data as the "merged" data
            return new_times, new_raw_data

        # Ensure numpy datetime64 for comparison (input should already be this way ideally)
        try:
            # Get overall bounds for logging/simple checks
            existing_start_bound = np.datetime64(existing_times[0])
            existing_end_bound = np.datetime64(existing_times[-1])
            new_start = np.datetime64(new_times[0])
            new_end = np.datetime64(new_times[-1])
        except Exception as e:
            print_manager.datacubby(f"MERGE ARRAYS ERROR - Could not get datetime64 bounds: {e}")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None

        # Format the datetime objects before printing
        existing_start_str = format_datetime_for_log(existing_start_bound)
        existing_end_str = format_datetime_for_log(existing_end_bound)
        new_start_str = format_datetime_for_log(new_start)
        new_end_str = format_datetime_for_log(new_end)

        print_manager.datacubby(f"MERGE ARRAYS RANGES - Existing Bounds: {existing_start_str} to {existing_end_str}")
        print_manager.datacubby(f"MERGE ARRAYS RANGES - New:           {new_start_str} to {new_end_str}")

        # --- Robust Check for Need to Merge ---
        # Combine times and find unique ones. A merge is needed if the unique set
        # is larger than the original existing set. This handles gaps correctly.
        combined_times = np.concatenate((existing_times, new_times))
        unique_times = np.unique(combined_times)

        if len(unique_times) == len(existing_times):
            # This implies all new times were already present in existing_times
            print_manager.datacubby("MERGE ARRAYS INFO - All new timestamps are already present. No merge needed.")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None # Signal no merge action taken

        # --- Perform the Merge ---
        # Since we determined a merge is needed (new unique times exist)
        print_manager.datacubby("MERGE ARRAYS ACTION - New unique timestamps found. Performing merge...")
        try:
            final_merged_times = unique_times

            merged_raw_data = {}
            all_keys = set(existing_raw_data.keys()) | set(new_raw_data.keys())
            
            # Create mapping from timestamps to indices for efficiency
            merged_time_to_idx = {time: i for i, time in enumerate(final_merged_times)}

            for key in all_keys:
                if key == 'all': continue

                existing_comp = existing_raw_data.get(key)
                new_comp = new_raw_data.get(key)

                # Determine the correct dtype and shape for the final merged array
                if existing_comp is not None:
                    final_dtype = existing_comp.dtype
                    y_shape = existing_comp.shape[1:] if existing_comp.ndim > 1 else ()
                elif new_comp is not None:
                    final_dtype = new_comp.dtype
                    y_shape = new_comp.shape[1:] if new_comp.ndim > 1 else ()
                else:
                    continue # Should not happen

                # Create an empty (NaN-filled) container for the final merged data
                final_shape = (len(final_merged_times),) + y_shape
                fill_value = np.nan if np.issubdtype(final_dtype, np.number) else None
                final_array = np.full(final_shape, fill_value, dtype=final_dtype)

                # --- Place existing data into the final array ---
                if existing_comp is not None and len(existing_comp) == len(existing_times):
                    try:
                        existing_indices_in_final = [merged_time_to_idx[t] for t in existing_times]
                        final_array[existing_indices_in_final] = existing_comp
                    except KeyError:
                        print_manager.warning(f"MERGE ARRAYS WARNING: A timestamp from existing_times was not found in merged_time_to_idx for key '{key}'.")

                # --- Place new data into the final array (overwriting if necessary) ---
                if new_comp is not None and len(new_comp) == len(new_times):
                    try:
                        new_indices_in_final = [merged_time_to_idx[t] for t in new_times]
                        final_array[new_indices_in_final] = new_comp
                    except KeyError:
                        print_manager.warning(f"MERGE ARRAYS WARNING: A timestamp from new_times was not found in merged_time_to_idx for key '{key}'.")
                
                merged_raw_data[key] = final_array

            # Reconstruct 'all' if possible
            if 'br' in merged_raw_data and 'bt' in merged_raw_data and 'bn' in merged_raw_data:
                merged_raw_data['all'] = [merged_raw_data['br'], merged_raw_data['bt'], merged_raw_data['bn']]

            print_manager.datacubby("MERGE ARRAYS SUCCESS - Merge complete.")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return final_merged_times, merged_raw_data

        except Exception as e:
            print_manager.datacubby(f"MERGE ARRAYS ERROR - During merge: {e}")
            import traceback
            print_manager.datacubby(traceback.format_exc())
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None

    @classmethod
    def grab(cls, identifier):
        """Retrieve object by its identifier with enhanced type tracking."""
        print_manager.datacubby(f"\n=== Retrieving {identifier} from data_cubby ===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"GRAB CALLER: {caller_info}")
        
        # Normalize case of identifier if it's a string
        if isinstance(identifier, str):
            identifier = identifier.lower()
        # Convert the input identifier to lowercase
        identifier_lower = identifier.lower() if isinstance(identifier, str) else identifier

        # Check all dictionaries with both original and lowercase versions
        result = (cls.cubby.get(identifier) or 
                  cls.cubby.get(identifier_lower) or
                  cls.class_registry.get(identifier) or 
                  cls.class_registry.get(identifier_lower) or
                  cls.subclass_registry.get(identifier) or
                  cls.subclass_registry.get(identifier_lower))
        
        if result is not None:
            print_manager.datacubby(f"GRAB SUCCESS - Retrieved {identifier} with type {type(result)}")

            # STRATEGIC PRINT: Log state of object just before returning from GRAB
            dt_len_grab_return = len(result.datetime_array) if hasattr(result, 'datetime_array') and result.datetime_array is not None else "None_or_NoAttr"
            min_dt_grab_return = result.datetime_array[0] if dt_len_grab_return not in ["None_or_NoAttr", 0] else "N/A"
            max_dt_grab_return = result.datetime_array[-1] if dt_len_grab_return not in ["None_or_NoAttr", 0] else "N/A"
            print_manager.datacubby(f"[CUBBY_GRAB_RETURN_STATE] Object ID {id(result)} for key '{identifier}'. dt_len: {dt_len_grab_return}, min: {min_dt_grab_return}, max: {max_dt_grab_return}")

            # Debug datetime_array (Condensed & Formatted)
            if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                if len(result.datetime_array) > 0:
                    start_dt = result.datetime_array[0]
                    end_dt = result.datetime_array[-1]

                    # Format datetimes using the imported helper
                    start_str = format_datetime_for_log(start_dt)
                    end_str = format_datetime_for_log(end_dt)

                    dt_summary = (
                        f"datetime_array type={type(result.datetime_array).__name__}, "
                        f"elem_type={type(start_dt).__name__}, "
                        f"shape={result.datetime_array.shape}, "
                        f"range={start_str} to {end_str}"
                    )
                    print_manager.datacubby(f"GRAB OUTPUT - {dt_summary}")
                else:
                    print_manager.datacubby(f"GRAB OUTPUT - datetime_array is empty")
            else:
                print_manager.datacubby(f"GRAB OUTPUT - No datetime_array attribute found")

            # Debug raw_data (Condensed)
            if hasattr(result, 'raw_data') and result.raw_data is not None:
                keys = list(result.raw_data.keys())
                summary_parts = [f"raw_data keys={keys}"]
                for key, value in result.raw_data.items():
                    shape_str = f"shape={getattr(value, 'shape', 'N/A')}"
                    if isinstance(value, list):
                        len_str = f"len={len(value)}"
                        if value and len(value) > 0 and hasattr(value[0], 'shape'):
                            elem_shape_str = f"elem_shape={getattr(value[0], 'shape', 'N/A')}"
                            summary_parts.append(f"{key}(list): {len_str}, {elem_shape_str}")
                        else:
                             summary_parts.append(f"{key}(list): {len_str}")
                    else:
                        summary_parts.append(f"{key}: type={type(value).__name__}, {shape_str}")
                print_manager.datacubby(f"GRAB OUTPUT - {' | '.join(summary_parts)}")
            else:
                print_manager.datacubby(f"GRAB OUTPUT - No raw_data attribute found")
        else:
            print_manager.datacubby(f"GRAB FAIL - Failed to retrieve {identifier}")
        
        print_manager.datacubby("=== End Retrieval Debug (LEAVING DATA CUBBY)===\n")
        return result

    @classmethod
    def get_all_keys(cls):
        """Get all keys from all registries for debugging."""
        result = {
            "cubby": list(cls.cubby.keys()),
            "class_registry": list(cls.class_registry.keys()),
            "subclass_registry": list(cls.subclass_registry.keys())
        }
        return result

    @classmethod
    def grab_component(cls, class_name, subclass_name):
        """
        Retrieve a component (subclass) from a class instance.
        
        Parameters
        ----------
        class_name : str
            Name of the class to retrieve from data_cubby
        subclass_name : str
            Name of the subclass/component to retrieve from the class
            
        Returns
        -------
        object or None
            The subclass object if found, otherwise None
        """
        print_manager.datacubby(f"\n=== Grabbing component {class_name}.{subclass_name} ===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"GRAB_COMPONENT CALLER: {caller_info}")
        
        # First get the class instance
        class_instance = cls.grab(class_name)
        if class_instance is None:
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Could not find class: {class_name}")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
            
        # Check if the class has a get_subclass method
        if not hasattr(class_instance, 'get_subclass'):
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Class {class_name} has no get_subclass method")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
            
        # Get the subclass from the class instance
        subclass = class_instance.get_subclass(subclass_name)
        if subclass is None:
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Could not find subclass: {subclass_name} in class {class_name}")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
        
        print_manager.datacubby(f"GRAB_COMPONENT SUCCESS - Found component: {class_name}.{subclass_name} with type {type(subclass)}")
        
        # Debug subclass attributes
        if hasattr(subclass, 'datetime_array') and subclass.datetime_array is not None:
            print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array type: {type(subclass.datetime_array)}")
            if len(subclass.datetime_array) > 0:
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array element type: {type(subclass.datetime_array[0])}")
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array shape: {subclass.datetime_array.shape}")
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array range: {subclass.datetime_array[0]} to {subclass.datetime_array[-1]}")
            else:
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array is empty")
        else:
            print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - No datetime_array attribute found")
        
        print_manager.datacubby("=== End Component Grab Debug ===\n")
        return subclass

    @classmethod
    def make_globally_accessible(cls, name, variable):
        """
        Make a variable accessible globally with the given name.
        
        Parameters
        ----------
        name : str
            The name to use for the variable in the global scope
        variable : object
            The variable to make globally accessible
        """
        try:
            import builtins
            from .print_manager import print_manager
            print_manager.datacubby(f"GLOBAL ACCESS - Making variable '{name}' globally accessible with ID {id(variable)}")
            
            # Debug variable type
            print_manager.datacubby(f"GLOBAL ACCESS - Variable type: {type(variable)}")
            if hasattr(variable, 'datetime_array') and variable.datetime_array is not None:
                print_manager.datacubby(f"GLOBAL ACCESS - datetime_array type: {type(variable.datetime_array)}")
                if len(variable.datetime_array) > 0:
                    print_manager.datacubby(f"GLOBAL ACCESS - datetime_array element type: {type(variable.datetime_array[0])}")
            
            setattr(builtins, name, variable)
            
            # Verify it was set correctly
            if hasattr(builtins, name):
                print_manager.datacubby(f"GLOBAL ACCESS SUCCESS - '{name}' globally accessible")
                return variable
            else:
                print_manager.datacubby(f"GLOBAL ACCESS FAIL - Failed to make '{name}' globally accessible")
                return variable
        except Exception as e:
            print_manager.datacubby(f"GLOBAL ACCESS ERROR - {str(e)}")
            return variable

    @classmethod
    def update_global_instance(cls, 
                               data_type_str: str, 
                               imported_data_obj: DataObject, 
                               is_segment_merge: bool = False, 
                               original_requested_trange: Optional[List[str]] = None
                              ) -> bool:
        """
        Updates the global instance of a data type with new data.
        Handles merging if data already exists or populating if it's empty.

        Args:
            data_type_str (str): The string identifier for the data type (e.g., 'mag_rtn_4sa', 'spi_sf00_l3_mom').
            imported_data_obj (DataObject): The new data object (typically from import_data_function).
            is_segment_merge (bool): Flag indicating if this is a segment merge (not fully implemented yet).
            original_requested_trange (Optional[List[str]]): The original time range requested by the user/higher-level function.

        Returns:
            bool: True if the update was successful or deemed unnecessary, False otherwise.
        """
        pm = print_manager # Local alias
        pm.dependency_management(f"[CUBBY_UPDATE_ENTRY] Received call for '{data_type_str}'. Original trange: '{original_requested_trange}', type(original_requested_trange[0])='{type(original_requested_trange[0]) if original_requested_trange and len(original_requested_trange)>0 else 'N/A'}'")

        # --- Helper for time range validation (NEW) ---
        def _validate_trange_elements(trange_to_validate, context_msg=""):
            # Changed pm.error to pm.processing for this initial check
            if not isinstance(trange_to_validate, list) or len(trange_to_validate) != 2:
                pm.processing(f"VALIDATION_STRUCT_FAIL: Input trange for {context_msg} must be a list/tuple of two elements. Received: {trange_to_validate}")
                return False
            
            # Existing processing prints - will remain as is
            pm.processing(f"[VALIDATE_DEBUG_ENTRY] _validate_trange_elements received: {trange_to_validate} with types {[type(x) for x in trange_to_validate]}. Context: {context_msg}")

            # New diagnostic prints OUTSIDE the critical if block, using pm.processing as per new strict rule
            pm.processing(f"SCOPE_PROC_DEBUG: id(str) is {id(str)}, str is {str}")
            pm.processing(f"SCOPE_PROC_DEBUG: id(datetime) is {id(datetime)}, datetime is {datetime}")
            pm.processing(f"SCOPE_PROC_DEBUG: id(pd.Timestamp) is {id(pd.Timestamp)}, pd.Timestamp is {pd.Timestamp}")

            for i, item in enumerate(trange_to_validate):
                # Existing processing print - will remain as is
                pm.processing(f"[VALIDATE_DEBUG] Validating item '{item}' of type {type(item)}. Context: {context_msg}")
                # New diagnostic print OUTSIDE the critical if block, using pm.processing as per new strict rule
                pm.processing(f"ITEM_PROC_DEBUG: id(item) is {id(item)}, item is '{item}', type(item) is {type(item)}")

                if not isinstance(item, (str, datetime, pd.Timestamp)):
                    print("RAW PRINT AT START OF IF BLOCK") # Keep raw print
                    # ALL DIAGNOSTIC PRINTS *INSIDE THIS IF BLOCK* WILL BE PM.PROCESSING
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: item is '{item}', type(item) is {type(item)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, str) is {isinstance(item, str)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, datetime) is {isinstance(item, datetime)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, pd.Timestamp) is {isinstance(item, pd.Timestamp)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: id(str) is {id(str)}, id(datetime) is {id(datetime)}, id(pd.Timestamp) is {id(pd.Timestamp)}")

                    # Original error-causing lines, ensuring they are pm.processing
                    pm.processing("ERROR_TEST_AT_FAIL_POINT_PROCESSING") 
                    print('just saying hi! 🥰🥰🥰')
                    pm.processing(f"Error parsing/validating input time range for {context_msg}: Input trange elements must be strings or datetime/timestamp objects. Element {i} is {type(item)}.")
                    return False
            return True
        # --- End Helper ---

        if imported_data_obj is None and not is_segment_merge:
            pm.warning(f"[CUBBY_UPDATE_WARNING] imported_data_obj is None and not a segment merge for {data_type_str}. Update aborted.")
            return False

        # --- STEP 1: Get the target global instance --- 
        global_instance = None
        target_class_type = cls._get_class_type_from_string(data_type_str)
        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG A] data_type_str: '{data_type_str}', target_class_type: '{target_class_type}'")

        if target_class_type:
            # Try to find an existing instance by its actual class type in the class_registry
            for key, inst in cls.class_registry.items():
                if isinstance(inst, target_class_type):
                    global_instance = inst
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG B] Found matching instance by type in class_registry with key: '{key}', instance ID: {id(global_instance)}")
                    break
        
        if global_instance is None:
            # Fallback: try direct key lookup in class_registry (old way, less robust for type matching)
            global_instance = cls.class_registry.get(data_type_str.lower()) # Ensure lowercase for lookup
            if global_instance:
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG C] Found instance by direct key '{data_type_str.lower()}' in class_registry, instance ID: {id(global_instance)}")
            else:
                # If still not found, it might be an issue with registration or a new data type
                pm.error(f"[CUBBY_UPDATE_ERROR] No global instance found or registered for data_type '{data_type_str}'. Cannot update.")
                # Optionally, create a new instance if that's the desired behavior for unknown types
                # if target_class_type:
                #     pm.status(f"No instance found for {data_type_str}, creating a new one of type {target_class_type}")
                #     global_instance = target_class_type(None) # Initialize with no data
                #     cls.class_registry[data_type_str.lower()] = global_instance
                # else:
                return False

        pm.dependency_management(f"[CUBBY] Found target global instance: {type(global_instance).__name__} (ID: {id(global_instance)}) to update for data_type '{data_type_str}'")
        
        # --- STEP 2: Validate the original_requested_trange if provided (especially for proton) --- 
        # This is the "Cranky Timekeeper" point for proton data
        # Using data_type_str.lower() for reliable matching against common keys
        # Explicitly check for proton related keys: 'spi_sf00_l3_mom' (official CDF name) and 'proton' (common alias)
        if data_type_str.lower() == 'spi_sf00_l3_mom' or data_type_str.lower() == 'proton':
            if original_requested_trange:
                pm.dependency_management(f"[CUBBY_UPDATE_TRANGE_VALIDATION] Validating original_requested_trange for '{data_type_str}': {original_requested_trange}, Types: [{type(original_requested_trange[0]) if len(original_requested_trange)>0 else 'N/A'}, {type(original_requested_trange[1]) if len(original_requested_trange)>1 else 'N/A'}]")
                if not _validate_trange_elements(original_requested_trange, context_msg=data_type_str):
                    # Error already printed by _validate_trange_elements
                    return False # Stop update if validation fails
            else:
                pm.dependency_management(f"[CUBBY_UPDATE_TRANGE_VALIDATION] No original_requested_trange provided for '{data_type_str}', skipping explicit validation here.")

        # --- STEP 3: Determine if the global instance has existing data ---
        has_existing_data = False
        if global_instance and hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None and len(global_instance.datetime_array) > 0:
            has_existing_data = True

        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG D] has_existing_data: {has_existing_data}")

        # --- STEP 4: Handle the update logic based on existing data ---
        if not has_existing_data or is_segment_merge:
            if is_segment_merge and has_existing_data:
                pm.datacubby(f"[CUBBY DEBUG] is_segment_merge is True, but instance for {data_type_str} already has data. Will overwrite with first segment via update().")
            elif not has_existing_data:
                pm.datacubby(f"Global instance for {data_type_str} is empty. Populating with new data via update()...")
            else: # is_segment_merge is True and no existing data
                pm.datacubby(f"Global instance for {data_type_str} is being initialized with the first segment via update()...")
            
            if hasattr(global_instance, 'update'):
                try:
                    # STRATEGIC PRINT H1
                    dt_len_before_instance_update = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG H1] Instance (ID: {id(global_instance)}) BEFORE global_instance.update(). datetime_array len: {dt_len_before_instance_update}")
                    
                    print_manager.datacubby(f"Calling update() on global instance of {data_type_str} (ID: {id(global_instance)}). is_segment_merge={is_segment_merge}")
                    
                    try:
                        # Try the new signature first (with original_requested_trange)
                        global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
                        print_manager.datacubby(f"Successfully called update() with original_requested_trange on global instance of {data_type_str}")
                    except TypeError as te:
                        # If that fails, fall back to the old signature (without original_requested_trange)
                        if "unexpected keyword argument" in str(te) or "takes" in str(te):
                            print_manager.datacubby(f"Falling back to simple update() signature for {data_type_str}")
                            global_instance.update(imported_data_obj)
                            print_manager.datacubby(f"Successfully called update() with simple signature on global instance of {data_type_str}")
                        else:
                            # Re-raise if it's a different TypeError
                            raise te
                    
                    # STRATEGIC PRINT H2
                    dt_len_after_instance_update = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG H2] Instance (ID: {id(global_instance)}) AFTER global_instance.update(). datetime_array len: {dt_len_after_instance_update}")
                    
                    pm.datacubby("✅ Instance updated successfully via .update() method.")
                    pm.datacubby("=== End Global Instance Update ===\n")
                    return True
                    
                except Exception as e:
                    pm.error(f"UPDATE GLOBAL ERROR - Error calling update() on instance: {e}")
                    import traceback
                    pm.error(traceback.format_exc())
                    pm.datacubby("=== End Global Instance Update ===\n")
                    return False
            else:
                pm.error(f"UPDATE GLOBAL ERROR - Global instance for '{data_type_str}' has no update method!")
                pm.datacubby("=== End Global Instance Update ===\n")
                return False
                
        # 4. Handle Instance with Existing Data (Merge Logic)
        else:
            pm.datacubby("Global instance has existing data. Attempting merge...")
            CorrectClass = cls._get_class_type_from_string(data_type_str)
            if not CorrectClass:
                pm.error(f"UPDATE GLOBAL ERROR - Cannot determine class type for '{data_type_str}' for merge.")
                pm.datacubby("=== End Global Instance Update ===\n")
                return False
                
            # Process the *new* raw data into structured arrays using a temporary instance
            try:
                pm.datacubby("Processing new imported data into temporary instance...")
                temp_new_processed = CorrectClass(None) # Create empty instance
                # We need to simulate the update process to get calculated vars
                if hasattr(temp_new_processed, 'calculate_variables'):
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG Merge Path - Pre-calc]: imported_data_obj ID: {id(imported_data_obj)}, .data ID: {id(imported_data_obj.data) if hasattr(imported_data_obj, 'data') else 'N/A'}, .data keys: {list(imported_data_obj.data.keys()) if hasattr(imported_data_obj, 'data') else 'N/A'} ***")
                    temp_new_processed.calculate_variables(imported_data_obj)
                else:
                     pm.warning(f"Temp instance for {data_type_str} lacks 'calculate_variables'. Merge might be incomplete.")
                     # Attempt basic assignment if possible (might fail)
                     temp_new_processed.datetime_array = np.array(cdflib.cdfepoch.to_datetime(imported_data_obj.times))
                     temp_new_processed.raw_data = imported_data_obj.data # This is risky!
                     
                new_times = temp_new_processed.datetime_array
                new_raw_data = temp_new_processed.raw_data
                pm.datacubby("✅ New data processed.")
                
                # STRATEGIC PRINT M
                existing_dt_len_for_M = len(global_instance.datetime_array) if global_instance.datetime_array is not None else "None"
                existing_dt_range_for_M = (global_instance.datetime_array[0], global_instance.datetime_array[-1]) if existing_dt_len_for_M not in ["None", 0] else "N/A"
                new_dt_len_for_M = len(new_times) if new_times is not None else "None"
                new_dt_range_for_M = (new_times[0], new_times[-1]) if new_dt_len_for_M not in ["None", 0] else "N/A"
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG M] Before _merge_arrays. Existing (ID: {id(global_instance)}) dt_len: {existing_dt_len_for_M}, range: {existing_dt_range_for_M}. New (temp) dt_len: {new_dt_len_for_M}, range: {new_dt_range_for_M}")

            except Exception as e:
                pm.error(f"UPDATE GLOBAL ERROR - Failed to process new data in temp instance: {e}")
                import traceback
                pm.error(traceback.format_exc())
                pm.datacubby("=== End Global Instance Update ===\n")
                return False
                
            # Perform the array merge
            pm.datacubby("Calling _merge_arrays...")
            merged_times, merged_raw_data = cls._merge_arrays(
                global_instance.datetime_array, global_instance.raw_data,
                new_times, new_raw_data
            )
            
            # Update the global instance ONLY if merge returned new data
            if merged_times is not None and merged_raw_data is not None:
                pm.dependency_management("[CUBBY DEBUG] Merge successful. Attempting to update global instance attributes...")
                try:
                    global_instance.datetime_array = merged_times
                    global_instance.raw_data = merged_raw_data
                    # STRATEGIC PRINT F
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG F] Instance (ID: {id(global_instance)}) AFTER assigning merged_times/raw_data. merged_times len: {len(merged_times)}, global_instance.datetime_array len: {len(global_instance.datetime_array) if global_instance.datetime_array is not None else 'None'}")

                    # STEP 2: Reconstruct .time from .datetime_array (CRITICAL)
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] PRE-TIME-RECONSTRUCTION:")
                    pm.dependency_management(f"    datetime_array len: {len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else 'None'}")
                    pm.dependency_management(f"    current time len: {len(global_instance.time) if hasattr(global_instance, 'time') and global_instance.time is not None else 'None'}")
                    if global_instance.datetime_array is not None and len(global_instance.datetime_array) > 0:
                        # OPTION: Convert to int64 directly from datetime64[ns] for self.time
                        # This is NOT TT2000 after the first load, but ensures length consistency and is fast.
                        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Converting merged datetime_array (len {len(global_instance.datetime_array)}) directly to int64 for .time attribute.")
                        global_instance.time = global_instance.datetime_array.astype('datetime64[ns]').astype(np.int64)
                        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] POST-TIME-ASSIGNMENT (direct int64 cast):")
                        pm.dependency_management(f"    NEW time len: {len(global_instance.time) if global_instance.time is not None else 'None'}, shape: {global_instance.time.shape if hasattr(global_instance.time, 'shape') else 'N/A'}, dtype: {global_instance.time.dtype}")
                    else:
                        global_instance.time = np.array([], dtype=np.int64) # Ensure correct dtype for empty
                        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] datetime_array was empty or None, set time to empty int64 array.")

                    # Call set_ploptions on the global_instance AFTER all raw data arrays are set
                    # This is crucial because set_ploptions uses these arrays to initialize PlotManagers
                    if hasattr(global_instance, 'set_ploptions'):
                        global_instance.set_ploptions()
                        dt_len_after_setploptions = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                        min_dt_G = global_instance.datetime_array[0] if dt_len_after_setploptions not in ["None_or_NoAttr", 0] else "N/A"
                        max_dt_G = global_instance.datetime_array[-1] if dt_len_after_setploptions not in ["None_or_NoAttr", 0] else "N/A"
                        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG G_POST_FINAL] Instance (ID: {id(global_instance)}) AFTER ALL MERGE LOGIC (before return True). datetime_array len: {dt_len_after_setploptions}, min: {min_dt_G}, max: {max_dt_G}")
                        
                        # STRATEGIC PRINT CHECK_REGISTRY
                        instance_in_registry_check = cls.class_registry.get(data_type_str.lower()) # target_key is data_type_str.lower()
                        if instance_in_registry_check is not None:
                            reg_len = len(instance_in_registry_check.datetime_array) if hasattr(instance_in_registry_check, 'datetime_array') and instance_in_registry_check.datetime_array is not None else "None_or_NoAttr"
                            reg_min_dt = instance_in_registry_check.datetime_array[0] if reg_len not in ["None_or_NoAttr", 0] else "N/A"
                            reg_max_dt = instance_in_registry_check.datetime_array[-1] if reg_len not in ["None_or_NoAttr", 0] else "N/A"
                            pm.dependency_management(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance in class_registry['{data_type_str.lower()}'] (ID: {id(instance_in_registry_check)}) state. dt_len: {reg_len}, min: {reg_min_dt}, max: {reg_max_dt}")
                            if instance_in_registry_check is not global_instance:
                                pm.warning(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance in registry (ID: {id(instance_in_registry_check)}) is NOT THE SAME OBJECT as global_instance (ID: {id(global_instance)}) just updated!")
                        else:
                            pm.dependency_management(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance for key '{data_type_str.lower()}' NOT FOUND in class_registry after merge ops.")
                        return True
                    else:
                         pm.warning(f"Global instance for {data_type_str} has no set_ploptions(). Plot managers might be stale.")
                    
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Global instance fully updated and ploptions set.")
                    return True
                except Exception as e:
                     # Using f-string for direct print of error
                     pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] UPDATE GLOBAL ERROR - Failed during critical update steps for {data_type_str} global instance: {e}")
                     import traceback
                     # Using f-string for direct print of traceback
                     pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] GOLD CUBBY TRACEBACK ***\n{traceback.format_exc()}")
                     return False
            else:
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Merge not required or _merge_arrays returned None. Global instance remains unchanged from this merge op.")
                return False

class Variable:
    """
    A variable class that can hold data and metadata, 
    while also behaving like a numpy array.
    """
    def __init__(self, class_name, subclass_name):
        self.class_name = class_name
        self.subclass_name = subclass_name
        self.datetime_array = None
        self.time_values = None
        self.values = None
        self.data_type = None
        self.internal_id = id(self)  # Add an internal ID for unique identification
        
        print_manager.datacubby(f"VARIABLE INIT - Created Variable {class_name}.{subclass_name} with id {self.internal_id}")
    
    def __array__(self):
        """Return the values array when used in numpy operations."""
        print_manager.datacubby(f"VARIABLE __array__ - Converting Variable {self.class_name}.{self.subclass_name} to array")
        if self.values is None:
            import numpy as np
            return np.array([])  # Return empty array if values is None
        return self.values
    
    def __len__(self):
        """Return length of the values array."""
        if self.values is None:
            return 0
        try:
            return len(self.values)
        except TypeError:
            return 0  # Handle case where values doesn't support len()
    
    def __getitem__(self, key):
        """Support for indexing operations."""
        if self.values is None:
            raise ValueError("No values available in this variable.")
        return self.values[key]
    
    def __repr__(self):
        """String representation of the variable."""
        return f"<Variable {self.class_name}.{self.subclass_name}, type={self.data_type}, id={self.internal_id}>"

# Create global instance
data_cubby = data_cubby()
print('initialized data_cubby.')