# plotbot/data_cubby.py

from .print_manager import print_manager, format_datetime_for_log
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import inspect
import copy

# --- Import Data Class Types for Mapping ---
# Assuming these classes are defined elsewhere and accessible
# We need the actual class types, not just the instances
from .data_classes.psp_mag_classes import mag_rtn_4sa_class, mag_rtn_class, mag_sc_4sa_class, mag_sc_class
from .data_classes.psp_electron_classes import epad_strahl_class, epad_strahl_high_res_class
from .data_classes.psp_proton_classes import proton_class, proton_hr_class
# Note: proton_fits and ham are handled differently in get_data, so maybe not needed here?
# from .data_classes.psp_proton_fits_classes import proton_fits_class
# from .data_classes.psp_ham_classes import ham_class

from .data_import import DataObject # Import the type hint for raw data object

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
        # Add other standard CDF types here as needed
    }

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
        if existing_times is None or new_times is None or len(existing_times) == 0 or len(new_times) == 0:
            print_manager.datacubby("MERGE ARRAYS ABORTED - One or both datetime arrays are None or empty")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None
        if existing_raw_data is None or new_raw_data is None:
            print_manager.datacubby("MERGE ARRAYS ABORTED - Raw data dictionaries are None")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None
            
        # Ensure numpy datetime64 for comparison (input should already be this way ideally)
        try:
            existing_start = np.datetime64(existing_times[0])
            existing_end = np.datetime64(existing_times[-1])
            new_start = np.datetime64(new_times[0])
            new_end = np.datetime64(new_times[-1])
        except Exception as e:
            print_manager.datacubby(f"MERGE ARRAYS ERROR - Could not get datetime64 bounds: {e}")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None

        # Format the datetime objects before printing
        existing_start_str = format_datetime_for_log(existing_start)
        existing_end_str = format_datetime_for_log(existing_end)
        new_start_str = format_datetime_for_log(new_start)
        new_end_str = format_datetime_for_log(new_end)

        print_manager.datacubby(f"MERGE ARRAYS RANGES - Existing: {existing_start_str} to {existing_end_str}")
        print_manager.datacubby(f"MERGE ARRAYS RANGES - New:      {new_start_str} to {new_end_str}")

        # --- Time Range Comparison --- (Simplified for clarity)
        is_identical = (new_start == existing_start) and (new_end == existing_end)
        is_new_contained = (new_start >= existing_start) and (new_end <= existing_end)
        is_entirely_before = new_end < existing_start
        is_entirely_after = new_start > existing_end

        # CASE 1: New data is already covered or identical - No merge needed
        if is_identical or is_new_contained:
            print_manager.datacubby("MERGE ARRAYS INFO - New range identical or contained. No merge needed.")
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None # Signal no merge action taken

        # CASE 2: Non-overlapping ranges - Concatenate and sort
        elif is_entirely_before or is_entirely_after:
            print_manager.datacubby("MERGE ARRAYS ACTION - Non-overlapping ranges detected. Merging...")
            try:
                merged_times = np.concatenate((existing_times, new_times))
                # Use stable sort
                sort_indices = np.argsort(merged_times, kind='stable')
                merged_times = merged_times[sort_indices]
                
                merged_raw_data = {}
                # Combine and sort each data component
                all_keys = set(existing_raw_data.keys()) | set(new_raw_data.keys())
                for key in all_keys:
                    # Skip 'all' for now, handle specific components
                    if key == 'all': continue 
                        
                    existing_comp = existing_raw_data.get(key)
                    new_comp = new_raw_data.get(key)
                    
                    if existing_comp is not None and new_comp is not None:
                        if len(existing_comp) == len(existing_times) and len(new_comp) == len(new_times):
                             merged_comp = np.concatenate((existing_comp, new_comp))
                             merged_raw_data[key] = merged_comp[sort_indices]
                        else:
                             print_manager.datacubby(f"MERGE ARRAYS WARNING - Length mismatch for key '{key}'. Skipping merge for this key.")
                    elif existing_comp is not None:
                         print_manager.datacubby(f"MERGE ARRAYS WARNING - Key '{key}' missing in new data. Trying to pad/sort existing.")
                         if len(existing_comp) == len(existing_times):
                             # Need to figure out how to handle sorting just one part - complex
                             pass # For now, skip if one part is missing
                    elif new_comp is not None:
                         print_manager.datacubby(f"MERGE ARRAYS WARNING - Key '{key}' missing in existing data. Trying to pad/sort new.")
                         if len(new_comp) == len(new_times):
                              pass # For now, skip if one part is missing
                
                # Reconstruct 'all' if possible (assuming components exist)
                if 'br' in merged_raw_data and 'bt' in merged_raw_data and 'bn' in merged_raw_data:
                    merged_raw_data['all'] = [merged_raw_data['br'], merged_raw_data['bt'], merged_raw_data['bn']]
                
                print_manager.datacubby("MERGE ARRAYS SUCCESS - Non-overlapping merge complete.")
                print_manager.datacubby("=== End Array Merge Debug ===\n")
                return merged_times, merged_raw_data
            except Exception as e:
                print_manager.datacubby(f"MERGE ARRAYS ERROR - During non-overlapping merge: {e}")
                import traceback
                print_manager.datacubby(traceback.format_exc())
                print_manager.datacubby("=== End Array Merge Debug ===\n")
                return None, None

        # CASE 3: Overlapping ranges - Use union (more complex, placeholder logic)
        else: # Some form of overlap
            print_manager.datacubby("MERGE ARRAYS ACTION - Overlapping ranges detected. Performing union (placeholder)...")
            # --- Placeholder for Union Logic --- 
            # This part is complex: need to find unique times, create new arrays,
            # map data points correctly, handling conflicts (e.g., prefer new data).
            # For now, we'll just return None, indicating merge wasn't performed for overlap.
            print_manager.datacubby("MERGE ARRAYS INFO - Overlap merge logic not fully implemented. No merge action taken.")
            # In a real scenario, you might choose to replace or implement the full union.
            # Returning None signals to the caller that the existing data was NOT modified/merged.
            # --- End Placeholder --- 
            print_manager.datacubby("=== End Array Merge Debug ===\n")
            return None, None # Signal no merge action taken for overlap yet

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
    def update_global_instance(cls, data_type_str, imported_data_obj: DataObject) -> bool:
        """Updates the existing global instance for a data type with new data.
        
        Handles initial population and merging.
        Args:
            data_type_str (str): The string identifier (e.g., 'mag_rtn_4sa', 'spe_sf0_pad').
            imported_data_obj (DataObject): Raw data object from import_data_function.
            
        Returns:
            bool: True if update/merge was processed successfully, False otherwise.
        """
        print_manager.datacubby(f"\n=== Updating Global Instance: {data_type_str} ===")

        # 1. Find the target global instance
        global_instance = None
        target_key = data_type_str.lower() # Key we expect based on data type

        # Try grabbing by the direct key first
        global_instance = cls.grab(target_key)

        # If grab by key failed, try finding instance by expected TYPE
        if global_instance is None:
            print_manager.debug(f"Grab failed for key '{target_key}'. Attempting to find instance by type...")
            TargetClass = cls._get_class_type_from_string(target_key)
            if TargetClass:
                print_manager.debug(f"Expected type: {TargetClass.__name__}")
                found_instance = None
                found_key = None
                # Search class_registry first (most common)
                for key, instance in cls.class_registry.items():
                    if isinstance(instance, TargetClass):
                        found_instance = instance
                        found_key = key
                        print_manager.debug(f"Found matching instance by type in class_registry with key: '{found_key}'")
                        break
                # Potential: Search other registries if needed?

                if found_instance:
                    global_instance = found_instance
                    # It might be useful to know the key it *was* found under, even if we update using target_key?
                    # For now, we just need the instance reference.
                else:
                    print_manager.warning(f"Could not find any instance of type {TargetClass.__name__} in registries.")
            else:
                print_manager.warning(f"Could not determine target class type for '{target_key}'. Cannot find instance by type.")

        # If still no instance found after key and type search, error out
        if global_instance is None:
            print_manager.error(f"UPDATE GLOBAL ERROR - Could not find/resolve global instance for '{data_type_str}'!")
            print_manager.datacubby("=== End Global Instance Update ===\n")
            return False

        print_manager.datacubby(f"Found target global instance: {type(global_instance).__name__} (ID: {id(global_instance)}) to update for data_type '{data_type_str}'")

        # 2. Check if the global instance is currently empty
        has_existing_data = (hasattr(global_instance, 'datetime_array') and 
                             global_instance.datetime_array is not None and 
                             len(global_instance.datetime_array) > 0)
                             
        # 3. Handle Empty Instance Case
        if not has_existing_data:
            print_manager.datacubby("Global instance is empty. Populating with new data...")
            if hasattr(global_instance, 'update'):
                try:
                    global_instance.update(imported_data_obj)
                    print_manager.datacubby("✅ Instance updated successfully.")
                    print_manager.datacubby("=== End Global Instance Update ===\n")
                    return True
                except Exception as e:
                    print_manager.error(f"UPDATE GLOBAL ERROR - Error calling update() on empty instance: {e}")
                    import traceback
                    print_manager.error(traceback.format_exc())
                    print_manager.datacubby("=== End Global Instance Update ===\n")
                    return False
            else:
                print_manager.error(f"UPDATE GLOBAL ERROR - Global instance for '{data_type_str}' has no update method!")
                print_manager.datacubby("=== End Global Instance Update ===\n")
                return False
                
        # 4. Handle Instance with Existing Data (Merge Logic)
        else:
            print_manager.datacubby("Global instance has existing data. Attempting merge...")
            CorrectClass = cls._get_class_type_from_string(data_type_str)
            if not CorrectClass:
                print_manager.error(f"UPDATE GLOBAL ERROR - Cannot determine class type for '{data_type_str}' for merge.")
                print_manager.datacubby("=== End Global Instance Update ===\n")
                return False
                
            # Process the *new* raw data into structured arrays using a temporary instance
            try:
                print_manager.datacubby("Processing new imported data into temporary instance...")
                temp_new_processed = CorrectClass(None) # Create empty instance
                # We need to simulate the update process to get calculated vars
                if hasattr(temp_new_processed, 'calculate_variables'):
                     temp_new_processed.calculate_variables(imported_data_obj)
                else:
                     print_manager.warning(f"Temp instance for {data_type_str} lacks 'calculate_variables'. Merge might be incomplete.")
                     # Attempt basic assignment if possible (might fail)
                     temp_new_processed.datetime_array = np.array(cdflib.cdfepoch.to_datetime(imported_data_obj.times))
                     temp_new_processed.raw_data = imported_data_obj.data # This is risky!
                     
                new_times = temp_new_processed.datetime_array
                new_raw_data = temp_new_processed.raw_data
                print_manager.datacubby("✅ New data processed.")
            except Exception as e:
                print_manager.error(f"UPDATE GLOBAL ERROR - Failed to process new data in temp instance: {e}")
                import traceback
                print_manager.error(traceback.format_exc())
                print_manager.datacubby("=== End Global Instance Update ===\n")
                return False
                
            # Perform the array merge
            print_manager.datacubby("Calling _merge_arrays...")
            merged_times, merged_raw_data = cls._merge_arrays(
                global_instance.datetime_array, global_instance.raw_data,
                new_times, new_raw_data
            )
            
            # Update the global instance ONLY if merge returned new data
            if merged_times is not None and merged_raw_data is not None:
                print_manager.datacubby("Merge successful. Updating global instance attributes...")
                try:
                    global_instance.datetime_array = merged_times
                    global_instance.raw_data = merged_raw_data
                    # Update plot managers with new data references
                    if hasattr(global_instance, 'set_ploptions'):
                        print_manager.datacubby("Calling set_ploptions() on global instance...")
                        global_instance.set_ploptions()
                    else:
                         print_manager.warning(f"Global instance for {data_type_str} has no set_ploptions(). Plot managers might be stale.")
                    print_manager.datacubby("✅ Global instance updated with merged data.")
                    print_manager.datacubby("=== End Global Instance Update ===\n")
                    return True # Return True because data was successfully merged and assigned
                except Exception as e:
                     print_manager.error(f"UPDATE GLOBAL ERROR - Failed to assign merged data to global instance: {e}")
                     import traceback
                     print_manager.error(traceback.format_exc())
                     print_manager.datacubby("=== End Global Instance Update ===\n")
                     return False # Return False on assignment error
            else:
                print_manager.datacubby("Merge not required or failed. Global instance remains unchanged.")
                print_manager.datacubby("=== End Global Instance Update ===\n")
                # Return False because no data was merged/assigned to the global instance
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
print('initialized data_cubby')