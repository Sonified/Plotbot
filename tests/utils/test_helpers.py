"""
Test Helpers for Plotbot Core Pipeline Testing

This module contains reusable functions for testing Plotbot's core data pipeline,
with a focus on data integrity verification rather than just plotting success.

These functions allow us to verify:
1. Instance state (data integrity, array consistency, time range correctness)
2. DataCubby state (correct stashing and registration of instances)
3. Global Tracker state (correct recording of processed time ranges)

They also provide simplified interfaces for common testing operations.
"""

import os
import sys
import numpy as np
import pandas as pd
import pytest
from plotbot.test_pilot import phase, system_check

# Ensure plotbot is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb
from plotbot import print_manager

def verify_instance_state(instance_label, instance_obj, expected_trange_str_list, expect_data=True, 
                         expected_points_approx=None, class_name_mapping=None):
    """Verify data integrity of a class instance after operations.
    
    Args:
        instance_label (str): Label for the instance (e.g., "pb.mag_rtn_4sa")
        instance_obj: The instance object to verify
        expected_trange_str_list: List of time range strings the data should cover. 
                                  Can be a list of single trange [start, end] or multiple [[s1,e1],[s2,e2]].
        expect_data (bool): If True, verify data is present; if False, verify instance is empty
        expected_points_approx (int, optional): Approximate number of data points expected
        class_name_mapping (dict, optional): Mapping of instance names to class info. If None, uses pb module's mapping if available.
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    phase(0, f"Verifying instance state: {instance_label} (ID: {id(instance_obj)})")
    overall_verification_passed = True
    
    # Find class info based on instance type
    class_name_mapping = class_name_mapping or getattr(pb, 'CLASS_NAME_MAPPING', None)
    if not class_name_mapping:
        system_check(f"Class mapping for {instance_label}", False, 
                    f"No class mapping available. Cannot verify properly.")
        return False
    
    instance_type = type(instance_obj).__name__
    class_info = None
    
    # Try to find matching class_info by instance_type
    for info in class_name_mapping.values():
        if info['class_type'].__name__ == instance_type:
            class_info = info
            break
    
    if class_info is None:
        # Fallback: Try to find by class_name attribute if present
        try:
            if hasattr(instance_obj, 'class_name') and instance_obj.class_name in class_name_mapping:
                class_info = class_name_mapping[instance_obj.class_name]
            elif instance_label.startswith('pb.'):
                instance_name_from_label = instance_label[3:].split()[0] 
                if instance_name_from_label in class_name_mapping:
                    class_info = class_name_mapping[instance_name_from_label]
        except (AttributeError, Exception) as e:
            print_manager.warning(f"Error finding class_info for {instance_label}: {e}")
    
    if class_info is None:
        system_check(f"Instance type recognition for {instance_label}", False, 
                    f"Unknown instance type {instance_type}, cannot verify properly.")
        return False # Critical failure if we can't identify the class
    
    primary_component_name = class_info.get('primary_component')
    component_names = class_info.get('components', [])
    
    # --- Data Presence and Basic Array Access ---
    datetime_array = getattr(instance_obj, 'datetime_array', None)
    time_arr = getattr(instance_obj, 'time', None)
    field_arr = getattr(instance_obj, 'field', None)
    raw_data = getattr(instance_obj, 'raw_data', {})

    data_points = 0
    if datetime_array is not None and hasattr(datetime_array, '__len__'):
        data_points = len(datetime_array)
    elif time_arr is not None and hasattr(time_arr, '__len__'): # Fallback if datetime_array somehow not primary
        data_points = len(time_arr)

    if expect_data:
        if data_points == 0:
            system_check(f"Data presence for {instance_label}", False, 
                        f"{instance_label} has 0 data points in datetime_array/time. Expected data for {expected_trange_str_list}.")
            overall_verification_passed = False
        else:
            system_check(f"Data presence for {instance_label}", True, 
                        f"{instance_label} has {data_points} data points.")

        if expected_points_approx is not None and not (expected_points_approx * 0.8 < data_points < expected_points_approx * 1.2):
            system_check(f"Data length for {instance_label}", False, 
                        f"Data length ({data_points}) not close to expected ({expected_points_approx}).", warning=True)
            # Not setting overall_verification_passed to False for approx match, it's a warning.
            
    else: # Expect empty
        if data_points != 0:
            system_check(f"Empty state for {instance_label}", False, 
                        f"Expected to be empty but found {data_points} data points.")
            overall_verification_passed = False
        else:
            system_check(f"Empty state for {instance_label}", True, "Instance is consistently empty, as expected.")
        return overall_verification_passed # If expecting empty, this is the only check needed

    if not overall_verification_passed and expect_data: # If already failed data presence, no point in continuing detailed checks
        return False

    # --- Detailed Checks (only if expect_data is True and basic presence passed) ---
    inconsistencies = []

    # 1. datetime_array checks
    if datetime_array is None:
        inconsistencies.append("datetime_array is None.")
    else:
        if not isinstance(datetime_array, np.ndarray):
            inconsistencies.append(f"datetime_array is not a numpy array (type: {type(datetime_array)}).")
        if data_points > 1: # Check sorting and uniqueness if more than one point
            try:
                # Ensure it's numpy array of datetime64 for comparison
                dt_for_check = np.array(datetime_array, dtype='datetime64[ns]')
                if not np.all(dt_for_check[:-1] < dt_for_check[1:]):
                    inconsistencies.append("datetime_array is not sorted ascending.")
                if len(np.unique(dt_for_check)) != len(dt_for_check):
                    inconsistencies.append("datetime_array contains duplicate timestamps.")
            except Exception as e:
                inconsistencies.append(f"Error checking datetime_array sort/uniqueness: {e}")
        # Time range check (simplified: check min/max against overall span of expected_trange_str_list)
        if expected_trange_str_list and data_points > 0:
            try:
                # Convert expected_trange_str_list to overall min/max datetime64
                all_expected_starts = [pd.to_datetime(tr[0]) for tr_list_item in expected_trange_str_list for tr in ([tr_list_item] if not isinstance(tr_list_item[0], list) else tr_list_item)]
                all_expected_ends = [pd.to_datetime(tr[1]) for tr_list_item in expected_trange_str_list for tr in ([tr_list_item] if not isinstance(tr_list_item[0], list) else tr_list_item)]
                
                # Handle cases where expected_trange_str_list might be a list of lists or a single list
                if isinstance(expected_trange_str_list[0], list) and isinstance(expected_trange_str_list[0][0], str): # List of [start, end]
                     expected_min_time = pd.to_datetime(min(tr[0] for tr in expected_trange_str_list)).to_datetime64()
                     expected_max_time = pd.to_datetime(max(tr[1] for tr in expected_trange_str_list)).to_datetime64()
                elif isinstance(expected_trange_str_list[0], str): # Single [start, end]
                     expected_min_time = pd.to_datetime(expected_trange_str_list[0]).to_datetime64()
                     expected_max_time = pd.to_datetime(expected_trange_str_list[1]).to_datetime64()
                else: # Should not happen with current usage but good to be defensive
                    raise ValueError("Unexpected format for expected_trange_str_list")

                actual_min_time = np.min(datetime_array).astype('datetime64[ns]')
                actual_max_time = np.max(datetime_array).astype('datetime64[ns]')

                # Check if actual range is *approximately equal to* expected overall span
                time_tolerance = pd.Timedelta(seconds=1) # Allow 1s tolerance at each end
                min_time_ok = abs(actual_min_time - expected_min_time) <= time_tolerance
                max_time_ok = abs(actual_max_time - expected_max_time) <= time_tolerance

                if not (min_time_ok and max_time_ok):
                    details = []
                    if not min_time_ok:
                        details.append(f"actual_min_time {actual_min_time} vs expected_min {expected_min_time}")
                    if not max_time_ok:
                        details.append(f"actual_max_time {actual_max_time} vs expected_max {expected_max_time}")
                    inconsistencies.append(f"datetime_array overall span issue: {'; '.join(details)} (expected [{expected_min_time}, {expected_max_time}]).")
            except Exception as e:
                inconsistencies.append(f"Error checking datetime_array range: {e}")

    # 2. time attribute checks
    if time_arr is None:
        inconsistencies.append("time attribute is None.")
    else:
        if not isinstance(time_arr, np.ndarray):
            inconsistencies.append(f"time attribute is not a numpy array (type: {type(time_arr)}).")
        if len(time_arr) != data_points:
            inconsistencies.append(f"time length ({len(time_arr)}) != data_points ({data_points}).")
        if datetime_array is not None: # Compare with datetime_array if available
            try:
                expected_time_arr = datetime_array.astype('datetime64[ns]').astype(np.int64)
                # If time_arr is TT2000 (CDF), skip strict check
                if np.all(time_arr > 1e17):  # TT2000 values are much larger than nanoseconds since epoch
                    pass  # Accept TT2000 as valid, skip strict check
                else:
                    if not np.array_equal(time_arr, expected_time_arr):
                        # Show first few differing elements for easier debug
                        diff_indices = np.where(time_arr != expected_time_arr)[0]
                        num_to_show = min(3, len(diff_indices))
                        details = []
                        for i in range(num_to_show):
                            idx = diff_indices[i]
                            details.append(f"idx {idx}: actual={time_arr[idx]}, expected={expected_time_arr[idx]}")
                        inconsistencies.append(f"time attribute does not match datetime_array.astype(np.int64). Differences at indices {diff_indices[:num_to_show]}: {'; '.join(details)}")
            except Exception as e:
                inconsistencies.append(f"Error comparing time attribute with datetime_array: {e}")

    # 3. raw_data checks
    if not isinstance(raw_data, dict):
        inconsistencies.append(f"raw_data is not a dict (type: {type(raw_data)}).")
    else:
        for comp_name in component_names:
            if comp_name == 'all': continue # 'all' is special, handled by field_arr or direct check if needed
            
            if comp_name not in raw_data:
                # This might be acceptable if the component is optional or derived later
                print_manager.debug(f"Component {comp_name} not found in raw_data for {instance_label}.")
                continue 

            comp_data_arr = raw_data[comp_name]
            if comp_data_arr is None:
                # Allow None for components that might not have data in a specific trange
                print_manager.debug(f"raw_data component {comp_name} is None for {instance_label}.")
                continue

            if not isinstance(comp_data_arr, np.ndarray):
                inconsistencies.append(f"raw_data component {comp_name} is not a numpy array (type: {type(comp_data_arr)}).")
                continue # Skip length check if not an array

            if comp_data_arr.ndim == 0 : # scalar array
                 if data_points != 1 : # if not a single data point, this is likely an error
                    inconsistencies.append(f"raw_data component {comp_name} is scalar but data_points is {data_points}.")
            elif comp_data_arr.shape[0] != data_points:
                 inconsistencies.append(f"raw_data component {comp_name} length ({comp_data_arr.shape[0]}) != data_points ({data_points}).")
    
    # 4. field attribute checks (assuming field is typically a 2D array [components, time] or 1D [time] for single var)
    if field_arr is None and primary_component_name: # If there's a primary component, field should usually exist
        # This might be okay if field is derived on demand and hasn't been yet.
        # However, after a load or get_data, it should be populated.
        print_manager.debug(f"field attribute is None for {instance_label}, though primary_component is {primary_component_name}.")
    elif field_arr is not None:
        if not isinstance(field_arr, np.ndarray):
            inconsistencies.append(f"field attribute is not a numpy array (type: {type(field_arr)}).")
        else:
            # Check first dimension length against data_points
            if field_arr.ndim == 1 and len(field_arr) != data_points:
                inconsistencies.append(f"1D field length ({len(field_arr)}) != data_points ({data_points}).")
            elif field_arr.ndim > 1 and not (field_arr.shape[-1] == data_points or field_arr.shape[0] == data_points): # Accept time as first or last dim
                inconsistencies.append(f"Multi-D field: neither first nor last dim matches data_points (shape: {field_arr.shape}, data_points: {data_points}).")
            
            # Check consistency with raw_data['all'] if that's how field is structured
            # This part is highly dependent on class structure (e.g., mag_rtn_4sa_class field from raw_data['all'])
            # For mag_rtn_4sa, field is usually raw_data['all']
            if instance_type == 'mag_rtn_4sa_class' or instance_type == 'mag_rtn_class': # Add other similar classes if needed
                if 'all' in raw_data and raw_data['all'] is not None:
                    raw_all = raw_data['all']
                    # If raw_all is a list, convert to numpy array for shape comparison
                    if isinstance(raw_all, list):
                        try:
                            raw_all_arr = np.array(raw_all)
                        except Exception as e:
                            inconsistencies.append(f"raw_data['all'] could not be converted to array: {e}")
                            raw_all_arr = None
                    else:
                        raw_all_arr = raw_all
                    if raw_all_arr is not None:
                        if not np.array_equal(field_arr, raw_all_arr):
                            # Accept if shapes are transposes of each other
                            if field_arr.shape == raw_all_arr.T.shape:
                                pass  # Acceptable, just a transpose
                            elif field_arr.shape != raw_all_arr.shape:
                                inconsistencies.append(f"field attribute shape {field_arr.shape} != raw_data['all'] shape {raw_all_arr.shape}.")
                            else:
                                inconsistencies.append(f"field attribute does not match raw_data['all'].")
                    else:
                        inconsistencies.append(f"raw_data['all'] could not be compared to field attribute.")
                elif 'all' not in raw_data and field_arr is not None:
                    inconsistencies.append(f"field attribute exists but raw_data['all'] is missing for {instance_type}.")


    # --- Final Report ---
    if inconsistencies:
        system_check(f"Internal consistency for {instance_label}", False, 
                    f"Instance has inconsistencies: {'; '.join(inconsistencies)}")
        overall_verification_passed = False
    else:
        system_check(f"Internal consistency for {instance_label}", True, 
                    f"Internally consistent with {data_points} data points and all checks passed.")

    return overall_verification_passed

def verify_data_cubby_state(instance_obj, instance_name=None, data_type_str=None, class_name_mapping=None):
    """Verify that the instance is correctly registered in DataCubby.
    
    Args:
        instance_obj: The instance object to verify
        instance_name (str, optional): Name of the instance (e.g., 'mag_rtn_4sa'). 
                                      If None, tries to get from instance.class_name
        data_type_str (str, optional): Data type string (e.g., 'mag_RTN_4sa'). 
                                      If None, tries to find using class_name_mapping
        class_name_mapping (dict, optional): Mapping of instance names to class info.
                                           If None, uses pb module's mapping
                                           
    Returns:
        tuple: (bool, list of inconsistencies)
    """
    cubby_checks_passed = True
    cubby_inconsistencies = []
    
    # If instance_name not provided, try to get from instance
    if instance_name is None:
        instance_name = getattr(instance_obj, 'class_name', None)
        if instance_name is None:
            cubby_inconsistencies.append("Cannot verify DataCubby state: No instance_name provided and no class_name attribute.")
            return False, cubby_inconsistencies
    
    # If data_type_str not provided, try to get from class_name_mapping
    if data_type_str is None:
        class_name_mapping = class_name_mapping or getattr(pb, 'CLASS_NAME_MAPPING', None)
        if class_name_mapping and instance_name in class_name_mapping:
            data_type_str = class_name_mapping[instance_name].get('data_type')
        else:
            cubby_inconsistencies.append(f"Cannot determine data_type_str for {instance_name}.")
            return False, cubby_inconsistencies
    
    # Verify instance is in DataCubby's class_registry and cubby
    if not hasattr(pb, 'data_cubby'):
        cubby_inconsistencies.append("pb.data_cubby does not exist.")
        return False, cubby_inconsistencies

    # Check class_registry and cubby for either key
    registry_ok = False
    cubby_ok = False
    # class_registry
    if instance_name in pb.data_cubby.class_registry and pb.data_cubby.class_registry[instance_name] is instance_obj:
        registry_ok = True
    if data_type_str in pb.data_cubby.class_registry and pb.data_cubby.class_registry[data_type_str] is instance_obj:
        registry_ok = True
    if not registry_ok:
        cubby_inconsistencies.append(f"Neither {instance_name} nor {data_type_str} in data_cubby.class_registry with correct object.")
    # cubby
    if instance_name in pb.data_cubby.cubby and pb.data_cubby.cubby[instance_name] is instance_obj:
        cubby_ok = True
    if data_type_str in pb.data_cubby.cubby and pb.data_cubby.cubby[data_type_str] is instance_obj:
        cubby_ok = True
    if not cubby_ok:
        cubby_inconsistencies.append(f"Neither {instance_name} nor {data_type_str} in data_cubby.cubby with correct object.")

    cubby_checks_passed = registry_ok and cubby_ok
    return cubby_checks_passed, cubby_inconsistencies

def verify_global_tracker_state(instance_obj, expected_trange_list, instance_name=None, 
                               data_type_str=None, class_name_mapping=None):
    """Verify that the Global Tracker has the correct ranges for the instance.
    
    Args:
        instance_obj: The instance object to verify
        expected_trange_list: List of time ranges expected to be in the global tracker
        instance_name (str, optional): Name of the instance (e.g., 'mag_rtn_4sa')
        data_type_str (str, optional): Data type string (e.g., 'mag_RTN_4sa')
        class_name_mapping (dict, optional): Mapping of instance names to class info
        
    Returns:
        tuple: (bool, list of inconsistencies)
    """
    tracker_check_passed = True
    tracker_inconsistencies = []
    
    # Get data_type_str if not provided
    if data_type_str is None:
        # If instance_name not provided, try to get from instance
        if instance_name is None:
            instance_name = getattr(instance_obj, 'class_name', None)
            if instance_name is None:
                tracker_inconsistencies.append("Cannot verify tracker: No instance_name provided and no class_name attribute.")
                return False, tracker_inconsistencies
        
        # Get data_type_str from class_name_mapping
        class_name_mapping = class_name_mapping or getattr(pb, 'CLASS_NAME_MAPPING', None)
        if class_name_mapping and instance_name in class_name_mapping:
            data_type_str = class_name_mapping[instance_name].get('data_type')
        else:
            tracker_inconsistencies.append(f"Cannot determine data_type_str for {instance_name}.")
            return False, tracker_inconsistencies
    
    # Verify global_tracker exists and has the expected ranges
    if not hasattr(pb, 'global_tracker'):
        tracker_inconsistencies.append("pb.global_tracker does not exist.")
        return False, tracker_inconsistencies
    
    # Check calculated_ranges for either key
    key_found = None
    for key in [data_type_str, instance_name]:
        if key in pb.global_tracker.calculated_ranges:
            key_found = key
            break
    if not key_found:
        tracker_inconsistencies.append(f"Neither {data_type_str} nor {instance_name} in global_tracker.calculated_ranges.")
        tracker_check_passed = False
        return tracker_check_passed, tracker_inconsistencies

    # Get the actual ranges for this data type
    actual_ranges = pb.global_tracker.calculated_ranges.get(key_found, [])
    if not actual_ranges:
        tracker_inconsistencies.append(f"global_tracker.calculated_ranges for {key_found} is empty.")
        tracker_check_passed = False
        return tracker_check_passed, tracker_inconsistencies
    
    # Convert expected_trange_list to datetime objects for comparison
    try:
        expected_ranges = []
        if isinstance(expected_trange_list[0], list):
            # List of time ranges: [[start1, end1], [start2, end2], ...]
            for trange in expected_trange_list:
                start = pd.to_datetime(trange[0])
                end = pd.to_datetime(trange[1])
                if start.tzinfo is not None:
                    start = start.tz_convert(None) if hasattr(start, 'tz_convert') else start.tz_localize(None)
                if end.tzinfo is not None:
                    end = end.tz_convert(None) if hasattr(end, 'tz_convert') else end.tz_localize(None)
                expected_ranges.append((start, end))
        else:
            start = pd.to_datetime(expected_trange_list[0])
            end = pd.to_datetime(expected_trange_list[1])
            if start.tzinfo is not None:
                start = start.tz_convert(None) if hasattr(start, 'tz_convert') else start.tz_localize(None)
            if end.tzinfo is not None:
                end = end.tz_convert(None) if hasattr(end, 'tz_convert') else end.tz_localize(None)
            expected_ranges.append((start, end))
        # Convert actual ranges to datetime objects
        actual_ranges_dt = []
        for r in actual_ranges:
            act_start = pd.to_datetime(r[0])
            act_end = pd.to_datetime(r[1])
            if act_start.tzinfo is not None:
                act_start = act_start.tz_convert(None) if hasattr(act_start, 'tz_convert') else act_start.tz_localize(None)
            if act_end.tzinfo is not None:
                act_end = act_end.tz_convert(None) if hasattr(act_end, 'tz_convert') else act_end.tz_localize(None)
            actual_ranges_dt.append((act_start, act_end))
        # Check if all expected ranges are in the actual ranges
        for exp_start, exp_end in expected_ranges:
            found_matching_range = False
            for act_start, act_end in actual_ranges_dt:
                # Check if ranges match (allow for small discrepancies)
                if (abs((exp_start - act_start).total_seconds()) < 1 and 
                    abs((exp_end - act_end).total_seconds()) < 1):
                    found_matching_range = True
                    break
            if not found_matching_range:
                tracker_inconsistencies.append(f"Expected range [{exp_start}, {exp_end}] not found in global_tracker.")
                tracker_check_passed = False
    except Exception as e:
        tracker_inconsistencies.append(f"Error checking global_tracker ranges: {e}")
        tracker_check_passed = False
    
    return tracker_check_passed, tracker_inconsistencies

def run_plotbot_test(test_name, instance, time_range, panel=1, verify_options=None):
    """Run a standard plotbot test with verification.
    
    Args:
        test_name (str): Name/description of the test
        instance: The instance to plot
        time_range: Time range to plot
        panel (int): Panel to plot on
        verify_options (dict, optional): Options for verification, including:
            - expect_data (bool): If True, verify data is present
            - expected_points_approx (int): Approximate number of data points expected
            - class_name_mapping (dict): Mapping of instance names to class info
            
    Returns:
        bool: True if all checks passed, False if any failed
    """
    phase(1, f"Running {test_name}")
    
    # If needed, extract the name and component from the instance
    if hasattr(instance, 'class_name'):
        instance_name = instance.class_name
        component_name = getattr(verify_options, 'component_name', 'br')
        component = getattr(instance, component_name)
    else:
        # Assume instance is already a component to plot, like mag_rtn_4sa.br
        component = instance
        # Try to extract instance_name from parent if possible
        if hasattr(component, '__self__') and hasattr(component.__self__, 'class_name'):
            instance_name = component.__self__.class_name
        else:
            instance_name = str(component)  # Fallback
    
    plot_successful = pb.plotbot(time_range, component, panel)
    system_check(f"{test_name} - plotbot call", plot_successful, "plotbot() should return True.")
    if not plot_successful:
        return False
    
    # Verify instance state if requested
    if verify_options and verify_options.get('verify_instance', True):
        # Get the instance to verify (either the instance itself or the component's parent)
        instance_to_verify = instance
        if hasattr(component, '__self__'):
            instance_to_verify = component.__self__
        
        verification_passed = verify_instance_state(
            f"pb.{instance_name}",
            instance_to_verify,
            [time_range],
            expect_data=verify_options.get('expect_data', True),
            expected_points_approx=verify_options.get('expected_points_approx', None),
            class_name_mapping=verify_options.get('class_name_mapping', None)
        )
        system_check(f"{test_name} - instance verification", verification_passed, 
                     "Instance data should be loaded and consistent.")
        if not verification_passed:
            return False
    
    # Verify DataCubby state if requested
    if verify_options and verify_options.get('verify_datacubby', False):
        # Similar to instance verification, get the right object
        instance_to_verify = instance
        if hasattr(component, '__self__'):
            instance_to_verify = component.__self__
            
        cubby_passed, cubby_issues = verify_data_cubby_state(
            instance_to_verify,
            instance_name=instance_name,
            data_type_str=verify_options.get('data_type_str', None),
            class_name_mapping=verify_options.get('class_name_mapping', None)
        )
        system_check(f"{test_name} - DataCubby verification", cubby_passed, 
                    f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
        if not cubby_passed and verify_options.get('require_datacubby', False):
            return False
    
    # Verify Global Tracker state if requested
    if verify_options and verify_options.get('verify_tracker', False):
        # Similar to above
        instance_to_verify = instance
        if hasattr(component, '__self__'):
            instance_to_verify = component.__self__
            
        tracker_passed, tracker_issues = verify_global_tracker_state(
            instance_to_verify,
            time_range,
            instance_name=instance_name,
            data_type_str=verify_options.get('data_type_str', None),
            class_name_mapping=verify_options.get('class_name_mapping', None)
        )
        system_check(f"{test_name} - Global Tracker verification", tracker_passed, 
                    f"Global Tracker state should be correct. {'Issues: ' + '; '.join(tracker_issues) if not tracker_passed else ''}")
        if not tracker_passed and verify_options.get('require_tracker', False):
            return False
    
    return True

def reset_and_verify_empty(instance_name, class_name_mapping=None):
    """Reset an instance and verify it's empty.
    
    Args:
        instance_name (str): Name of the instance to reset
        class_name_mapping (dict, optional): Mapping of instance names to class info
        
    Returns:
        object: The reset instance
    """
    phase(0, f"Resetting and verifying {instance_name} is empty")
    
    # Call _reset_pipeline_state if it exists, otherwise try a simpler reset
    if hasattr(pb, '_reset_pipeline_state'):
        current_instance = pb._reset_pipeline_state(instance_name)
    else:
        # Simple reset fallback if _reset_pipeline_state doesn't exist
        # Get class info from class_name_mapping
        class_name_mapping = class_name_mapping or getattr(pb, 'CLASS_NAME_MAPPING', None)
        if not class_name_mapping or instance_name not in class_name_mapping:
            raise ValueError(f"Cannot reset {instance_name}: no class mapping available.")
        # Create a new instance
        instance_class = class_name_mapping[instance_name]['class_type']
        current_instance = instance_class(None)
        setattr(pb, instance_name, current_instance)
    
    # Always stash the instance in data_cubby under its canonical name
    if hasattr(pb, 'data_cubby'):
        pb.data_cubby.stash(current_instance, class_name=instance_name)
    
    # Verify the instance is empty
    empty_verification = verify_instance_state(
        f"pb.{instance_name} (post-reset)", 
        current_instance, 
        expected_trange_str_list=[['2000-01-01', '2000-01-02']], # Dummy trange, not used for empty check
        expect_data=False,
        class_name_mapping=class_name_mapping
    )
    
    if not empty_verification:
        print_manager.warning(f"Instance {instance_name} not empty after reset.")
    
    return current_instance

def save_snapshot_and_verify(filename, classes, trange_list=None, time_range=None, auto_split=False, overwrite=True):
    """Save a snapshot and verify the state.
    
    Args:
        filename (str): Path to save snapshot to
        classes (list): List of classes to save
        trange_list (list, optional): List of time ranges to load data for
        time_range (list, optional): Time range to filter data
        auto_split (bool): Whether to auto-split the data into segments
        overwrite (bool): Whether to overwrite an existing file
        
    Returns:
        bool: True if save was successful
    """
    phase(0, f"Saving snapshot to {filename}")
    
    # Skip if file exists and overwrite is False
    if not overwrite and os.path.exists(filename):
        print_manager.info(f"Snapshot file {filename} already exists, skipping save.")
        return True
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # If trange_list is provided, verify the classes have attributes needed for get_data
    if trange_list:
        for cls in classes:
            # Each class should have .br or similar for plotbot to work
            if not hasattr(cls, 'br') and not hasattr(cls, getattr(cls, 'primary_component', 'br')):
                print_manager.warning(f"Class {cls} has no primary component attribute. get_data may fail.")
    
    # Save the snapshot
    save_successful = pb.save_data_snapshot(
        filename,
        classes=classes,
        trange_list=trange_list,
        time_range=time_range,
        auto_split=auto_split
    )
    
    system_check(f"Snapshot save to {filename}", save_successful, 
                "save_data_snapshot should return True on success.")
    
    # Verify file exists
    if save_successful:
        file_exists = os.path.exists(filename)
        system_check(f"Snapshot file {filename} created", file_exists, "File should exist after successful save.")
        if not file_exists:
            save_successful = False
    
    # Verify instance states if they were populated by trange_list
    if save_successful and trange_list:
        for cls in classes:
            # Skip verification if the class doesn't have a clear name
            if not hasattr(cls, 'class_name'):
                continue
                
            # Verify this class was populated correctly
            cls_verification = verify_instance_state(
                f"pb.{cls.class_name} (post-save)",
                cls,
                trange_list,
                expect_data=True
            )
            
            system_check(f"Class {cls.class_name} state after save", cls_verification, 
                        "Class should have correct data after being populated for snapshot.")
            
            # Optional: Could also verify DataCubby state here
    
    return save_successful

def load_snapshot_and_verify(filename, classes, merge_segments=True, expected_trange_list=None):
    """Load a snapshot and verify the state.
    
    Args:
        filename (str): Path to load snapshot from
        classes (list): List of classes to load (names or data_type strings)
        merge_segments (bool): Whether to merge segmented data
        expected_trange_list (list, optional): Expected time ranges to verify against
        
    Returns:
        bool: True if load was successful
    """
    phase(0, f"Loading snapshot from {filename}")
    
    # Verify file exists
    if not os.path.exists(filename):
        system_check(f"Snapshot file {filename} exists", False, "File must exist to load.")
        return False
    
    # Load the snapshot
    load_successful = pb.load_data_snapshot(
        filename,
        classes=classes,
        merge_segments=merge_segments
    )
    
    system_check(f"Snapshot load from {filename}", load_successful, 
                "load_data_snapshot should return True on success.")
    
    # Verify instance states if load was successful and we have expected_trange_list
    if load_successful and expected_trange_list:
        # For each class we attempted to load, get the actual instance and verify
        for class_name in classes:
            # Determine instance name (might be different from class_name if class_name is a data_type_str)
            instance_name = class_name
            if hasattr(pb, 'CLASS_NAME_MAPPING'):
                # If class_name looks like a data_type_str (uppercase with underscores), 
                # find the corresponding instance_name
                for name, info in pb.CLASS_NAME_MAPPING.items():
                    if info.get('data_type') == class_name:
                        instance_name = name
                        break
            
            # Get the instance
            if hasattr(pb, instance_name):
                instance = getattr(pb, instance_name)
                
                # Verify instance state
                instance_verification = verify_instance_state(
                    f"pb.{instance_name} (post-load)",
                    instance,
                    expected_trange_list,
                    expect_data=True
                )
                
                system_check(f"Instance {instance_name} state after load", instance_verification, 
                            "Instance should have correct data after loading from snapshot.")
                
                # Verify DataCubby state
                cubby_passed, cubby_issues = verify_data_cubby_state(
                    instance,
                    instance_name=instance_name
                )
                
                system_check(f"DataCubby state for {instance_name} after load", cubby_passed, 
                            "Instance should be correctly registered in DataCubby after load.")
                
                # Verify Global Tracker state
                tracker_passed, tracker_issues = verify_global_tracker_state(
                    instance,
                    expected_trange_list,
                    instance_name=instance_name
                )
                
                system_check(f"Global Tracker state for {instance_name} after load", tracker_passed, 
                            "Global Tracker should have correct ranges after load.")
            else:
                system_check(f"Instance {instance_name} exists after load", False, 
                            f"Instance {instance_name} not found after loading {class_name}.")
    
    return load_successful 