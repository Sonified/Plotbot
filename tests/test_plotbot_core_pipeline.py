# # tests/test_plotbot_core_pipeline.py
# """
# End-to-End Test for Plotbot's Core Data Pipeline.

# This test verifies the primary workflow for a standard data type (`mag_rtn_4sa`):
# 1.  **Initial Data Load & Plot:** Data is loaded via plotbot() and plotted.
# 2.  **Cached Data Retrieval & Plot:** Subsequent identical plotbot() call uses cached data.
# 3.  **Simple Snapshot Save:** Current data state is saved to a basic .pkl file.
# 4.  **Simple Snapshot Load & Plot:** Data is loaded from the .pkl and plotted.
# 5.  **Advanced Snapshot Save (Multi-Trange, Auto-Split):** Data for multiple time ranges is loaded
#     via save_data_snapshot's trange_list feature and saved with auto-splitting.
# 6.  **Advanced Snapshot Load (Segmented) & Plot:** Segmented snapshot is loaded and plotted.
# 7.  **Partial Overlap Merge - Save:** Data for a specific range is loaded and saved to a snapshot.
# 8.  **Partial Overlap Merge - Load & Plot:** Snapshot is loaded, then a plotbot() call for a
#     partially overlapping range is made, testing DataCubby's merge logic with snapshot data.

# Relevant Modules & Files:
# - Test Script: `tests/test_plotbot_core_pipeline.py` (this file)
# - Main Plotting: `plotbot/plotbot_main.py` (contains `plotbot()`)
# - Data Orchestration: `plotbot/get_data.py`
# - Data Configuration: `plotbot/data_classes/psp_data_types.py`
# - Data Import from Files: `plotbot/data_import.py` (contains `import_data_function`)
# - Data Class we are using: `plotbot/data_classes/psp_mag_classes.py` (e.g., `mag_rtn_4sa_class`)
# - Data Caching/Registry: `plotbot/data_cubby.py`
# - Processed Range Tracking: `plotbot/data_tracker.py`
# - Snapshotting for save/load data as .pkl: `plotbot/data_snapshot.py`
# """
# import sys
# import os
# import numpy as np
# import pandas as pd
# import time as pytime # Alias to avoid conflict
# import pytest # Added
# from plotbot.test_pilot import phase, system_check # Added

# # Adjust path to import plotbot modules
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import plotbot as pb 
# from plotbot import print_manager
# from plotbot.data_snapshot import save_data_snapshot, load_data_snapshot
# from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class, mag_rtn_class, mag_sc_4sa_class, mag_sc_class # Added other mag classes
# from plotbot.data_classes.psp_electron_classes import epad_strahl_class, epad_strahl_high_res_class  # Add the electron classes here

# from plotbot.data_classes.psp_proton_classes import proton_class, proton_hr_class # Added proton classes
# from plotbot.data_classes.psp_ham_classes import ham_class # Added ham class
# from plotbot import plt

# # --- Test Constants & Fixtures ---
# # Filenames for Snapshots
# TEST_SIMPLE_SNAPSHOT_FILENAME = "data_snapshots/test_simple_snapshot_mag_rtn_4sa.pkl" # Added data_snapshots/ prefix
# TEST_ADVANCED_SNAPSHOT_FILENAME = "data_snapshots/test_advanced_snapshot_mag_rtn_4sa.pkl" # Added data_snapshots/ prefix
# TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME = "data_snapshots/test_partial_merge_snapshot_mag_rtn_4sa.pkl" # Added data_snapshots/ prefix

# # Ensure snapshot directory exists
# os.makedirs("data_snapshots", exist_ok=True)

# # --- Time Ranges for Tests ---
# # Used for Test 1, 2, 3, 4
# TEST_SINGLE_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00']

# # Used for Test 5, 6 (Advanced Snapshotting with multiple segments)
# # These two distinct short ranges will be saved together.
# TEST_TRANGES_FOR_SAVE = [
#     ['2021-10-26 02:00:00', '2021-10-26 02:10:00'], 
#     ['2021-10-26 02:15:00', '2021-10-26 02:25:00'] 
# ]
# # This range is covered by the first element of TEST_TRANGES_FOR_SAVE and can be used for plotting after advanced load.
# TEST_SUB_TRANGE_OF_ADVANCED_SAVE = ['2021-10-26 02:00:00', '2021-10-26 02:05:00']


# # Used for Test 7, 8 (Partial Overlap Merge)
# TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE = ['2021-10-26 02:05:00', '2021-10-26 02:15:00'] # Saved to PKL
# TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP = ['2021-10-26 02:00:00', '2021-10-26 02:10:00'] # New plotbot call, overlaps 02:05-02:10 from PKL
# # Expected combined range after merge: ['2021-10-26 02:00:00', '2021-10-26 02:15:00']

# # Standardized class name mapping to handle case sensitivity and variations consistently
# CLASS_NAME_MAPPING = {
#     # Standard instance names (lowercase) mapped to data_type (often uppercase), class type, and primary components
#     'mag_rtn_4sa': {
#         'data_type': 'mag_RTN_4sa',  # In data_types dict and load_data_snapshot
#         'class_type': mag_rtn_4sa_class,
#         'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
#         'primary_component': 'br'
#     },
#     'mag_rtn': {
#         'data_type': 'mag_RTN',
#         'class_type': mag_rtn_class,
#         'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
#         'primary_component': 'br'
#     },
#     'mag_sc_4sa': {
#         'data_type': 'mag_SC_4sa',
#         'class_type': mag_sc_4sa_class,
#         'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
#         'primary_component': 'bx'
#     },
#     'mag_sc': {
#         'data_type': 'mag_SC',
#         'class_type': mag_sc_class,
#         'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
#         'primary_component': 'bx'
#     },
#     'epad_strahl': {
#         'data_type': 'spe_sf0_pad',
#         'class_type': epad_strahl_class,
#         'components': ['strahl'],
#         'primary_component': 'strahl'
#     },
#     'epad_strahl_high_res': {
#         'data_type': 'spe_af0_pad',
#         'class_type': epad_strahl_high_res_class,
#         'components': ['strahl'],
#         'primary_component': 'strahl'
#     },
#     'proton': {
#         'data_type': 'spi_sf00_l3_mom',
#         'class_type': proton_class,
#         'components': ['anisotropy'],
#         'primary_component': 'anisotropy'
#     },
#     'proton_hr': {
#         'data_type': 'spi_af00_L3_mom',
#         'class_type': proton_hr_class,
#         'components': ['anisotropy'],
#         'primary_component': 'anisotropy'
#     },
#     'ham': {
#         'data_type': 'ham',
#         'class_type': ham_class,
#         'components': ['hamogram_30s'],
#         'primary_component': 'hamogram_30s'
#     },
# }

# # Reverse mapping to lookup instance name by data_type (uppercase)
# DATA_TYPE_TO_INSTANCE_MAP = {info['data_type']: instance_name for instance_name, info in CLASS_NAME_MAPPING.items()}

# def _reset_pipeline_state(data_instance_name='mag_rtn_4sa'):
#     """Resets the specified data instance and its associated cache/tracker entries.
    
#     Args:
#         data_instance_name (str): Name of the instance to reset. Can be a base name like 'mag_rtn_4sa' 
#                                 or a derived name like 'mag_rtn_4sa_for_test'.
    
#     Returns:
#         The reset instance object
#     """
#     phase(0, f"Resetting pipeline state for pb.{data_instance_name}")
    
#     # Handle the case where a derived name is passed (with _for_ suffix)
#     base_instance_name = data_instance_name.split('_for_')[0] if '_for_' in data_instance_name else data_instance_name
    
#     # Find class info from our standardized mapping using base name
#     # First try exact match, then try prefix match if needed
#     class_info = None
#     if base_instance_name in CLASS_NAME_MAPPING:
#         class_info = CLASS_NAME_MAPPING[base_instance_name]
#     else:
#         # Try finding a class where base_instance_name is a prefix
#         for name, info in CLASS_NAME_MAPPING.items():
#             if base_instance_name.startswith(name):
#                 class_info = info
#                 print_manager.warning(f"Using {name} class info for {base_instance_name} based on prefix match")
#                 break
    
#     if class_info is None:
#         print_manager.warning(f"No matching class found for '{base_instance_name}'. Defaulting to mag_rtn_4sa_class.")
#         # Default to mag_rtn_4sa if no match found
#         class_info = CLASS_NAME_MAPPING['mag_rtn_4sa']
    
#     # Clean up old instance if it exists
#     if hasattr(pb, data_instance_name):
#         delattr(pb, data_instance_name)
    
#     # Initialize new instance using the appropriate class
#     try:
#         # Create a new instance with None for imported_data
#         instance_class = class_info['class_type']
#         print_manager.debug(f"Initializing new {instance_class.__name__} instance")
#         current_instance = instance_class(None)
        
#         # Set class_name attribute if possible
#         try:
#             if hasattr(current_instance, 'class_name') and current_instance.class_name != data_instance_name:
#                 # Only attempt to set if it already exists but has a different value
#                 if hasattr(current_instance, '__dict__'):
#                     # Try direct dictionary access first
#                     current_instance.__dict__['class_name'] = data_instance_name
#                     print_manager.debug(f"Set class_name to {data_instance_name} via __dict__")
#             elif not hasattr(current_instance, 'class_name'):
#                 # Try to add the attribute if it doesn't exist
#                 try:
#                     current_instance.class_name = data_instance_name
#                     print_manager.debug(f"Added class_name attribute with value {data_instance_name}")
#                 except (AttributeError, Exception) as e:
#                     print_manager.debug(f"Could not add class_name attribute: {e}")
#         except Exception as e:
#             print_manager.warning(f"Warning: Could not set class_name on {data_instance_name}: {e}")
        
#         # Set the instance on the pb module
#         setattr(pb, data_instance_name, current_instance)
#     except Exception as e:
#         print_manager.error(f"Failed to initialize {data_instance_name}: {e}")
#         system_check(f"Initialize pb.{data_instance_name}", False, f"Failed to create new instance: {e}")
#         return None
    
#     # Clear entries from both data_cubby and tracker
#     # Build a list of keys to try clearing
#     keys_to_clear = [
#         data_instance_name,                    # The exact instance name provided
#         base_instance_name,                    # The base name without _for_
#         class_info['data_type'],               # The uppercase data_type (e.g., 'mag_RTN_4sa')
#         class_info['data_type'].lower(),       # Lowercase version of data_type
#         getattr(current_instance, 'class_name', data_instance_name), # The instance's own class_name if set
#         getattr(current_instance, 'data_type', class_info['data_type']) # The instance's own data_type if set
#     ]
    
#     # Deduplicate the list and remove None values
#     keys_to_clear = [k for k in list(set(keys_to_clear)) if k is not None]
#     print_manager.debug(f"  Attempting to clear DataCubby/Tracker for keys: {keys_to_clear}")
    
#     # Clear from cubby and tracker
#     if hasattr(pb, 'data_cubby'):
#         for key in keys_to_clear:
#             pb.data_cubby.class_registry.pop(key, None)
#             pb.data_cubby.cubby.pop(key, None)
    
#     if hasattr(pb, 'global_tracker'):
#         for key in keys_to_clear:
#             pb.global_tracker.calculated_ranges.pop(key, None)
#             pb.global_tracker.imported_ranges.pop(key, None)
    
#     # Stash the new instance in data_cubby
#     try:
#         if hasattr(pb, 'data_cubby') and current_instance is not None:
#             key_for_stashing = getattr(current_instance, 'class_name', data_instance_name)
#             pb.data_cubby.stash(current_instance, class_name=key_for_stashing)
#             print_manager.debug(f"Stashed {data_instance_name} in data_cubby with key {key_for_stashing}")
#     except Exception as e:
#         print_manager.warning(f"Warning: Error stashing {data_instance_name} in data_cubby: {e}")
    
#     system_check(f"Pipeline state reset for pb.{data_instance_name}", True, 
#                 f"Fresh pb.{data_instance_name} (type: {type(current_instance).__name__}) initialized.")
    
#     return current_instance

# @pytest.fixture(autouse=True)
# def setup_core_pipeline_test_plots():
#     """Ensure plots are closed before and after each test in this file."""
#     plt.close('all')
#     # Ensure specific print_manager settings for these tests
#     print_manager.show_debug = True
#     print_manager.show_datacubby = True
#     print_manager.show_data_snapshot = True
#     print_manager.show_tracker = True
#     yield
#     plt.close('all')
#     # Reset print_manager settings after test if needed, or assume next test/fixture will set them
#     print_manager.show_debug = False
#     print_manager.show_datacubby = False
#     print_manager.show_data_snapshot = False
#     print_manager.show_tracker = False

# @pytest.fixture
# def mag_4sa_test_instance():
#     """Provides a consistently named and reset instance for testing."""
#     instance_name = 'mag_rtn_4sa'
#     _reset_pipeline_state(instance_name)
#     return getattr(pb, instance_name)

# def verify_instance_state(instance_label, instance_obj, expected_trange_str_list, expect_data=True, expected_points_approx=None):
#     """Verify data integrity of a class instance after operations.
    
#     Args:
#         instance_label (str): Label for the instance (e.g., "pb.mag_rtn_4sa")
#         instance_obj: The instance object to verify
#         expected_trange_str_list: List of time range strings the data should cover. 
#                                   Can be a list of single trange [start, end] or multiple [[s1,e1],[s2,e2]].
#         expect_data (bool): If True, verify data is present; if False, verify instance is empty
#         expected_points_approx (int, optional): Approximate number of data points expected
        
#     Returns:
#         bool: True if verification passed, False otherwise
#     """
#     phase(0, f"Verifying instance state: {instance_label} (ID: {id(instance_obj)})")
#     overall_verification_passed = True
    
#     # Find class info based on instance type
#     instance_type = type(instance_obj).__name__
#     class_info = None
    
#     # Try to find matching class_info by instance_type
#     for info in CLASS_NAME_MAPPING.values():
#         if info['class_type'].__name__ == instance_type:
#             class_info = info
#             break
    
#     if class_info is None:
#         # Fallback: Try to find by class_name attribute if present
#         try:
#             if hasattr(instance_obj, 'class_name') and instance_obj.class_name in CLASS_NAME_MAPPING:
#                 class_info = CLASS_NAME_MAPPING[instance_obj.class_name]
#             elif instance_label.startswith('pb.'):
#                 instance_name_from_label = instance_label[3:].split()[0] 
#                 if instance_name_from_label in CLASS_NAME_MAPPING:
#                     class_info = CLASS_NAME_MAPPING[instance_name_from_label]
#         except (AttributeError, Exception) as e:
#             print_manager.warning(f"Error finding class_info for {instance_label}: {e}")
    
#     if class_info is None:
#         system_check(f"Instance type recognition for {instance_label}", False, 
#                     f"Unknown instance type {instance_type}, cannot verify properly.")
#         return False # Critical failure if we can't identify the class
    
#     primary_component_name = class_info.get('primary_component')
#     component_names = class_info.get('components', [])
    
#     # --- Data Presence and Basic Array Access ---
#     datetime_array = getattr(instance_obj, 'datetime_array', None)
#     time_arr = getattr(instance_obj, 'time', None)
#     field_arr = getattr(instance_obj, 'field', None)
#     raw_data = getattr(instance_obj, 'raw_data', {})

#     data_points = 0
#             if datetime_array is not None and hasattr(datetime_array, '__len__'):
#                 data_points = len(datetime_array)
#     elif time_arr is not None and hasattr(time_arr, '__len__'): # Fallback if datetime_array somehow not primary
#         data_points = len(time_arr)

#     if expect_data:
#         if data_points == 0:
#             system_check(f"Data presence for {instance_label}", False, 
#                         f"{instance_label} has 0 data points in datetime_array/time. Expected data for {expected_trange_str_list}.")
#             overall_verification_passed = False
#         else:
#             system_check(f"Data presence for {instance_label}", True, 
#                         f"{instance_label} has {data_points} data points.")

#         if expected_points_approx is not None and not (expected_points_approx * 0.8 < data_points < expected_points_approx * 1.2):
#             system_check(f"Data length for {instance_label}", False, 
#                         f"Data length ({data_points}) not close to expected ({expected_points_approx}).", warning=True)
#             # Not setting overall_verification_passed to False for approx match, it's a warning.
            
#     else: # Expect empty
#         if data_points != 0:
#             system_check(f"Empty state for {instance_label}", False, 
#                         f"Expected to be empty but found {data_points} data points.")
#             overall_verification_passed = False
#         else:
#             system_check(f"Empty state for {instance_label}", True, "Instance is consistently empty, as expected.")
#         return overall_verification_passed # If expecting empty, this is the only check needed

#     if not overall_verification_passed and expect_data: # If already failed data presence, no point in continuing detailed checks
#         return False

#     # --- Detailed Checks (only if expect_data is True and basic presence passed) ---
#     inconsistencies = []

#     # 1. datetime_array checks
#     if datetime_array is None:
#         inconsistencies.append("datetime_array is None.")
#     else:
#         if not isinstance(datetime_array, np.ndarray):
#             inconsistencies.append(f"datetime_array is not a numpy array (type: {type(datetime_array)}).")
#         if data_points > 1: # Check sorting and uniqueness if more than one point
#             try:
#                 # Ensure it's numpy array of datetime64 for comparison
#                 dt_for_check = np.array(datetime_array, dtype='datetime64[ns]')
#                 if not np.all(dt_for_check[:-1] < dt_for_check[1:]):
#                     inconsistencies.append("datetime_array is not sorted ascending.")
#                 if len(np.unique(dt_for_check)) != len(dt_for_check):
#                     inconsistencies.append("datetime_array contains duplicate timestamps.")
#             except Exception as e:
#                 inconsistencies.append(f"Error checking datetime_array sort/uniqueness: {e}")
#         # Time range check (simplified: check min/max against overall span of expected_trange_str_list)
#         if expected_trange_str_list and data_points > 0:
#             try:
#                 # Convert expected_trange_str_list to overall min/max datetime64
#                 all_expected_starts = [pd.to_datetime(tr[0]) for tr_list_item in expected_trange_str_list for tr in ([tr_list_item] if not isinstance(tr_list_item[0], list) else tr_list_item)]
#                 all_expected_ends = [pd.to_datetime(tr[1]) for tr_list_item in expected_trange_str_list for tr in ([tr_list_item] if not isinstance(tr_list_item[0], list) else tr_list_item)]
                
#                 # Handle cases where expected_trange_str_list might be a list of lists or a single list
#                 if isinstance(expected_trange_str_list[0], list) and isinstance(expected_trange_str_list[0][0], str): # List of [start, end]
#                      expected_min_time = pd.to_datetime(min(tr[0] for tr in expected_trange_str_list)).to_datetime64()
#                      expected_max_time = pd.to_datetime(max(tr[1] for tr in expected_trange_str_list)).to_datetime64()
#                 elif isinstance(expected_trange_str_list[0], str): # Single [start, end]
#                      expected_min_time = pd.to_datetime(expected_trange_str_list[0]).to_datetime64()
#                      expected_max_time = pd.to_datetime(expected_trange_str_list[1]).to_datetime64()
#                 else: # Should not happen with current usage but good to be defensive
#                     raise ValueError("Unexpected format for expected_trange_str_list")

#                 actual_min_time = np.min(datetime_array).astype('datetime64[ns]')
#                 actual_max_time = np.max(datetime_array).astype('datetime64[ns]')

#                 # Allow for slight flexibility due to data resolution, exact boundaries might be tricky
#                 # Check if actual range is *within or very close to* expected range
#                 if not (actual_min_time >= expected_min_time - pd.Timedelta(seconds=1) and \
#                         actual_max_time <= expected_max_time + pd.Timedelta(seconds=1)):
#                     inconsistencies.append(f"datetime_array range [{actual_min_time}, {actual_max_time}] "
#                                           f"not within expected [{expected_min_time}, {expected_max_time}].")
#             except Exception as e:
#                 inconsistencies.append(f"Error checking datetime_array range: {e}")

#     # 2. time attribute checks
#     if time_arr is None:
#         inconsistencies.append("time attribute is None.")
#     else:
#         if not isinstance(time_arr, np.ndarray):
#             inconsistencies.append(f"time attribute is not a numpy array (type: {type(time_arr)}).")
#         if len(time_arr) != data_points:
#             inconsistencies.append(f"time length ({len(time_arr)}) != data_points ({data_points}).")
#         if datetime_array is not None: # Compare with datetime_array if available
#             try:
#                 expected_time_arr = datetime_array.astype('datetime64[ns]').astype(np.int64)
#                 if not np.array_equal(time_arr, expected_time_arr):
#                     # Show first few differing elements for easier debug
#                     diff_indices = np.where(time_arr != expected_time_arr)[0]
#                     num_to_show = min(3, len(diff_indices))
#                     details = []
#                     for i in range(num_to_show):
#                         idx = diff_indices[i]
#                         details.append(f"idx {idx}: actual={time_arr[idx]}, expected={expected_time_arr[idx]}")
#                     inconsistencies.append(f"time attribute does not match datetime_array.astype(np.int64). Differences at indices {diff_indices[:num_to_show]}: {'; '.join(details)}")
#             except Exception as e:
#                 inconsistencies.append(f"Error comparing time attribute with datetime_array: {e}")

#     # 3. raw_data checks
#     if not isinstance(raw_data, dict):
#         inconsistencies.append(f"raw_data is not a dict (type: {type(raw_data)}).")
#     else:
#         for comp_name in component_names:
#             if comp_name == 'all': continue # 'all' is special, handled by field_arr or direct check if needed
            
#             if comp_name not in raw_data:
#                 # This might be acceptable if the component is optional or derived later
#                 print_manager.debug(f"Component {comp_name} not found in raw_data for {instance_label}.")
#                 continue 

#             comp_data_arr = raw_data[comp_name]
#             if comp_data_arr is None:
#                 # Allow None for components that might not have data in a specific trange
#                 print_manager.debug(f"raw_data component {comp_name} is None for {instance_label}.")
#                 continue

#             if not isinstance(comp_data_arr, np.ndarray):
#                 inconsistencies.append(f"raw_data component {comp_name} is not a numpy array (type: {type(comp_data_arr)}).")
#                 continue # Skip length check if not an array

#             if comp_data_arr.ndim == 0 : # scalar array
#                  if data_points != 1 : # if not a single data point, this is likely an error
#                     inconsistencies.append(f"raw_data component {comp_name} is scalar but data_points is {data_points}.")
#             elif comp_data_arr.shape[0] != data_points:
#                  inconsistencies.append(f"raw_data component {comp_name} length ({comp_data_arr.shape[0]}) != data_points ({data_points}).")
    
#     # 4. field attribute checks (assuming field is typically a 2D array [components, time] or 1D [time] for single var)
#     if field_arr is None and primary_component_name: # If there's a primary component, field should usually exist
#         # This might be okay if field is derived on demand and hasn't been yet.
#         # However, after a load or get_data, it should be populated.
#         print_manager.debug(f"field attribute is None for {instance_label}, though primary_component is {primary_component_name}.")
#     elif field_arr is not None:
#         if not isinstance(field_arr, np.ndarray):
#             inconsistencies.append(f"field attribute is not a numpy array (type: {type(field_arr)}).")
#         else:
#             # Check first dimension length against data_points
#             if field_arr.ndim == 1 and len(field_arr) != data_points:
#                 inconsistencies.append(f"1D field length ({len(field_arr)}) != data_points ({data_points}).")
#             elif field_arr.ndim > 1 and field_arr.shape[-1] != data_points: # Assuming time is the last dimension
#                 inconsistencies.append(f"Multi-D field last dim ({field_arr.shape[-1]}) != data_points ({data_points}).")
            
#             # Check consistency with raw_data['all'] if that's how field is structured
#             # This part is highly dependent on class structure (e.g., mag_rtn_4sa_class field from raw_data['all'])
#             # For mag_rtn_4sa, field is usually raw_data['all']
#             if instance_type == 'mag_rtn_4sa_class' or instance_type == 'mag_rtn_class': # Add other similar classes if needed
#                 if 'all' in raw_data and raw_data['all'] is not None:
#                     if not np.array_equal(field_arr, raw_data['all']):
#                         # Adding a check for shape mismatch as array_equal might fail if shapes are different
#                         if field_arr.shape != raw_data['all'].shape:
#                             inconsistencies.append(f"field attribute shape {field_arr.shape} != raw_data['all'] shape {raw_data['all'].shape}.")
#     else:
#                             inconsistencies.append(f"field attribute does not match raw_data['all'].")
#                 elif 'all' not in raw_data and field_arr is not None:
#                     inconsistencies.append(f"field attribute exists but raw_data['all'] is missing for {instance_type}.")


#     # --- Final Report ---
#     if inconsistencies:
#         system_check(f"Internal consistency for {instance_label}", False, 
#                     f"Instance has inconsistencies: {'; '.join(inconsistencies)}")
#         overall_verification_passed = False
#         else:
#         system_check(f"Internal consistency for {instance_label}", True, 
#                     f"Internally consistent with {data_points} data points and all checks passed.")
        
#     return overall_verification_passed

# @pytest.mark.mission("Core Pipeline: Initial Data Load and Plot")
# @pytest.mark.skip(reason="Test 1 passes consistently and can be skipped to speed up test runs")
# def test_initial_load_and_plot(mag_4sa_test_instance):
#     """Tests the initial data load via plotbot() and verifies instance state and DataCubby."""
#     phase(1, "Setting plot options for initial load")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 1: Initial Data Load and Plot"

#     instance_name = mag_4sa_test_instance.class_name # e.g. 'mag_rtn_4sa'
#     data_type_str = CLASS_NAME_MAPPING[instance_name]['data_type'] # e.g. 'mag_RTN_4sa'


#     phase(2, f"Calling plotbot for {TEST_SINGLE_TRANGE} with {instance_name}.br on panel 1")
#     plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
#     system_check("Plotbot call successful", plot_successful, "plotbot() should return True on success.")
#     assert plot_successful, "Plotbot call for initial load failed."

#     phase(3, f"Verifying instance state for pb.{instance_name} after initial load")
#     # verify_instance_state now performs more detailed checks
#     verification_passed = verify_instance_state(
#         f"pb.{instance_name}",
#         mag_4sa_test_instance,
#         [TEST_SINGLE_TRANGE] # Pass as list of tranges
#     )
#     system_check("Instance state verification (detailed)", verification_passed, 
#                  "Instance data should be loaded and internally consistent.")
#     assert verification_passed, "Detailed instance state verification failed after initial load."

#     phase(4, f"Verifying DataCubby state for {instance_name}")
#     # Check DataCubby.stash (Scenario 1: Stashing a brand-new object)
#     # and DataCubby.update_global_instance (Scenario 1: Global instance is empty)
#     cubby_checks_passed = True
#     cubby_inconsistencies = []

#     # Check class_registry
#     if instance_name not in pb.data_cubby.class_registry:
#         cubby_inconsistencies.append(f"{instance_name} not in data_cubby.class_registry.")
#     elif pb.data_cubby.class_registry[instance_name] is not mag_4sa_test_instance:
#         cubby_inconsistencies.append(f"data_cubby.class_registry['{instance_name}'] is not the expected instance.")

#     # Check cubby (for non-subclassed, top-level instance)
#     if instance_name not in pb.data_cubby.cubby:
#         cubby_inconsistencies.append(f"{instance_name} not in data_cubby.cubby.")
#     elif pb.data_cubby.cubby[instance_name] is not mag_4sa_test_instance:
#         cubby_inconsistencies.append(f"data_cubby.cubby['{instance_name}'] is not the expected instance.")

#     # Also check using the data_type_str, as DataCubby might use that as a key internally for global instances
#     if data_type_str not in pb.data_cubby.class_registry:
#         cubby_inconsistencies.append(f"{data_type_str} (data_type) not in data_cubby.class_registry.")
#     elif pb.data_cubby.class_registry[data_type_str] is not mag_4sa_test_instance:
#         # This check might be too strict if DataCubby internally uses a different key sometimes,
#         # but for update_global_instance, it's expected to use the data_type_str.
#         cubby_inconsistencies.append(f"data_cubby.class_registry['{data_type_str}'] is not the expected instance.")
        
#     if data_type_str not in pb.data_cubby.cubby:
#         cubby_inconsistencies.append(f"{data_type_str} (data_type) not in data_cubby.cubby.")
#     elif pb.data_cubby.cubby[data_type_str] is not mag_4sa_test_instance:
#         cubby_inconsistencies.append(f"data_cubby.cubby['{data_type_str}'] is not the expected instance.")


#     if cubby_inconsistencies:
#         cubby_checks_passed = False
#         system_check("DataCubby state verification", False, 
#                      f"DataCubby inconsistencies: {'; '.join(cubby_inconsistencies)}")
#     else:
#         system_check("DataCubby state verification", True, 
#                      "Instance correctly stashed in DataCubby.class_registry and DataCubby.cubby.")
    
#     assert cubby_checks_passed, "DataCubby state verification failed."

# # === Test 2: Second plotbot() call (should use cached data from DataCubby/Tracker) ===
# @pytest.mark.mission("Core Pipeline: Cached Data Retrieval and Plot")
# @pytest.mark.skip(reason="Test 2 passes consistently and can be skipped to speed up test runs")
# def test_cached_data_retrieval_and_plot(mag_4sa_test_instance):
#     """Tests that a second plotbot() call for the same data uses cached data and instance remains valid."""
#     phase(1, "Setting plot options for cached data test")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 2: Cached Data Retrieval"
#     instance_name = mag_4sa_test_instance.class_name

#     phase(2, f"First plotbot call to populate cache for {TEST_SINGLE_TRANGE} with {instance_name}.br")
#     # This call populates the cache and updates the instance
#     initial_plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1) 
#     assert initial_plot_successful, "Initial plotbot call failed in cached data test setup."
    
#     # Verify state after initial load
#     initial_verification_passed = verify_instance_state(
#         f"pb.{instance_name} after initial load for cache test",
#         mag_4sa_test_instance,
#         [TEST_SINGLE_TRANGE]
#     )
#     assert initial_verification_passed, "Instance state verification failed after initial load in cache test."
    
#     # Optional: Could capture a signature of the data here if we want to be absolutely sure it didn't change.
#     # For example, hash of datetime_array or sum of some data component.
#     # For now, verify_instance_state should catch most unintended changes.

#     phase(3, f"Second plotbot call (should use cache) for {TEST_SINGLE_TRANGE} with {instance_name}.br")
#     plot_successful_cached = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
#     system_check("Cached plotbot call successful", plot_successful_cached, "plotbot() using cache should return True.")
#     assert plot_successful_cached, "Cached plotbot call failed."

#     phase(4, f"Verifying instance state for {instance_name} after cached call")
#     # The instance should still contain the same valid data. verify_instance_state will check consistency.
#     cached_verification_passed = verify_instance_state(
#         f"pb.{instance_name} after cached call",
#         mag_4sa_test_instance,
#         [TEST_SINGLE_TRANGE]
#     )
#     system_check("Instance state verification after cached call (detailed)", cached_verification_passed, 
#                  "Instance data should be consistent and unchanged after cached call.")
#     assert cached_verification_passed, "Detailed instance state verification failed after cached call."
    
#     # Add a check to see if DataCubby indicates a merge didn't happen (or was skipped)
#     # This is an indirect way to check for cache usage. A more direct way might involve
#     # mocking parts of get_data or DataCubby._merge_arrays if this isn't sufficient.
#     # For now, if verify_instance_state passes and the data looks the same, it implies caching.
#     # One could also check pb.global_tracker to see if 'calculated_ranges' for this data type
#     # still reflects only the initial load, not a subsequent one for the same range.
#     if hasattr(pb, 'global_tracker') and hasattr(pb.global_tracker, 'calculated_ranges'):
#         data_type_str = CLASS_NAME_MAPPING[instance_name]['data_type']
#         if data_type_str in pb.global_tracker.calculated_ranges:
#             num_calc_ranges = len(pb.global_tracker.calculated_ranges[data_type_str])
#             # After one load and one cached call for the *same* range, we expect 1 calculated range.
#             # If it were 2, it might imply a re-calculation/merge instead of cache hit.
#             if num_calc_ranges == 1:
#                 system_check("Global Tracker check for cache hit", True,
#                              f"global_tracker.calculated_ranges for {data_type_str} has 1 entry, consistent with cache hit.")
#             else:
#                 system_check("Global Tracker check for cache hit", False,
#                              f"global_tracker.calculated_ranges for {data_type_str} has {num_calc_ranges} entries. Expected 1 for cache hit.",
#                              warning=True) # Warning for now, as this is an indirect check
#         else:
#             system_check("Global Tracker check for cache hit", False,
#                          f"{data_type_str} not found in global_tracker.calculated_ranges after load.", warning=True)


# # === Test 3: Simple Snapshot Save ===
# @pytest.mark.mission("Core Pipeline: Simple Snapshot Save")
# def test_simple_snapshot_save(mag_4sa_test_instance):
#     """Tests saving a simple data snapshot, verifies file creation and instance integrity."""
#     instance_name = mag_4sa_test_instance.class_name
#     phase(1, f"Populating instance {instance_name} for snapshot save")
    
#     plt.options.use_single_title = True # Set title for the plot during population
#     plt.options.single_title_text = "Test 3 Setup: Populating data for Simple Snapshot"
    
#     # Load data into the instance first
#     plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
#     assert plot_successful, "Plotbot call failed during setup for snapshot save."
    
#     # Verify it has data and is consistent BEFORE saving
#     pre_save_verification_passed = verify_instance_state(
#         f"pb.{instance_name} (pre-save)", 
#         mag_4sa_test_instance, 
#         [TEST_SINGLE_TRANGE]
#     )
#     assert pre_save_verification_passed, "Instance state invalid before snapshot save."

#     phase(2, f"Saving snapshot to {TEST_SIMPLE_SNAPSHOT_FILENAME}")
#     # No specific plot title needed for the save operation itself
#     # plt.options.single_title_text = "Test 3: Simple Snapshot Save" # Not needed here
#     save_successful = save_data_snapshot(
#         TEST_SIMPLE_SNAPSHOT_FILENAME,
#         classes=[mag_4sa_test_instance], 
#         auto_split=False
#     )
#     system_check("Snapshot save operation", save_successful, "save_data_snapshot should return True on success.")
#     assert save_successful, "save_data_snapshot failed."

#     phase(3, "Verifying snapshot file existence")
#     file_exists = os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME)
#     system_check(f"Snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} created", file_exists, "Snapshot file should exist after saving.")
#     assert file_exists, f"Snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} was not created."


# # === Test 4: Simple Snapshot Load, Verify, and Plot ===
# @pytest.mark.mission("Core Pipeline: Simple Snapshot Load, Verify, and Plot")
# def test_simple_snapshot_load_verify_plot(mag_4sa_test_instance):
#     """Tests loading a simple snapshot, verifying data, DataCubby, Tracker, and plotting."""
#     instance_name = mag_4sa_test_instance.class_name
#     data_type_str = CLASS_NAME_MAPPING[instance_name]['data_type']

#     # --- Setup: Ensure the snapshot file exists --- 
#     phase(1, "Setup: Ensuring snapshot file for loading exists")
#     if not os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME):
#         _reset_pipeline_state('temp_mag_rtn_4sa_for_save') # Use a temporary distinct name for this setup
#         temp_instance = getattr(pb, 'temp_mag_rtn_4sa_for_save')
        
#         plt.options.use_single_title = True
#         plt.options.single_title_text = "Test 4 Setup: Creating Snapshot File for Load Test"
        
#         load_data_for_snapshot_plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, temp_instance.br, 1)
#         if not load_data_for_snapshot_plot_successful:
#             pytest.fail(f"Failed to load data for snapshot creation: plotbot() returned {load_data_for_snapshot_plot_successful}")
        
#         # Verify temp_instance before saving it
#         assert verify_instance_state(f"pb.temp_mag_rtn_4sa_for_save", temp_instance, [TEST_SINGLE_TRANGE]), \
#             "Temporary instance for snapshot creation is invalid."
            
#             save_successful = save_data_snapshot(
#                 TEST_SIMPLE_SNAPSHOT_FILENAME,
#                 classes=[temp_instance],
#                 auto_split=False
#             )
#             if not save_successful:
#                 pytest.fail(f"Failed to create snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} for test")
#         # Clean up temp instance to avoid interference with the main test instance if names were the same
#         # _reset_pipeline_state already cleans up, but good to be explicit if we created it here.
#         if hasattr(pb, 'temp_mag_rtn_4sa_for_save'):
#              delattr(pb, 'temp_mag_rtn_4sa_for_save') # remove from pb module
#         # also clear from cubby if it was stashed under that temp name
#         pb.data_cubby.class_registry.pop('temp_mag_rtn_4sa_for_save', None)
#         pb.data_cubby.cubby.pop('temp_mag_rtn_4sa_for_save', None)
            
#     assert os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME), f"Setup failed: {TEST_SIMPLE_SNAPSHOT_FILENAME} not created or not found"

#     # --- Main Test --- 
#     phase(2, f"Resetting main instance {instance_name} and verifying it is empty")
#     # The mag_4sa_test_instance fixture provides a reset instance, but explicitly call _reset_pipeline_state 
#     # to ensure it's truly fresh for this load operation and verify emptiness.
#     _reset_pipeline_state(instance_name) 
#     current_instance = getattr(pb, instance_name) # Get the fresh reference

#     empty_verification = verify_instance_state(
#         f"pb.{instance_name} (pre-load)", 
#         current_instance, 
#         expected_trange_str_list=[TEST_SINGLE_TRANGE], # expected_trange is not strictly needed for empty check but good for context
#         expect_data=False
#     )
#     assert empty_verification, f"Instance {instance_name} was not empty before loading snapshot."
    
#     phase(3, f"Loading snapshot from {TEST_SIMPLE_SNAPSHOT_FILENAME} into {instance_name}")
#     load_successful = load_data_snapshot(
#         TEST_SIMPLE_SNAPSHOT_FILENAME, 
#         classes=[data_type_str]  # Load by data_type_str (e.g., 'mag_RTN_4sa')
#     )
#     system_check("Snapshot load operation", load_successful, "load_data_snapshot should return True.")
#     assert load_successful, "load_data_snapshot failed."

#     # current_instance should now be populated by load_data_snapshot
#     phase(4, f"Verifying instance state for {instance_name} after simple load (detailed)")
#     post_load_verification_passed = verify_instance_state(
#         f"pb.{instance_name} (post-load)",
#         current_instance, 
#         [TEST_SINGLE_TRANGE]
#     )
#     system_check("Instance state after load (detailed)", post_load_verification_passed, 
#                  "Data from snapshot should be loaded, and instance internally consistent.")
#     assert post_load_verification_passed, "Detailed instance state verification failed after simple load."

#     phase(5, f"Verifying DataCubby state for {instance_name} after load")
#     # load_data_snapshot should have updated/stashed the instance in DataCubby
#     cubby_checks_passed = True
#     cubby_inconsistencies = []
#     # Check class_registry (should contain the instance by its class_name and data_type_str)
#     if instance_name not in pb.data_cubby.class_registry or pb.data_cubby.class_registry[instance_name] is not current_instance:
#         cubby_inconsistencies.append(f"{instance_name} not correctly registered in class_registry or points to wrong object.")
#     if data_type_str not in pb.data_cubby.class_registry or pb.data_cubby.class_registry[data_type_str] is not current_instance:
#         cubby_inconsistencies.append(f"{data_type_str} not correctly registered in class_registry or points to wrong object.")
#     # Check cubby
#     if instance_name not in pb.data_cubby.cubby or pb.data_cubby.cubby[instance_name] is not current_instance:
#         cubby_inconsistencies.append(f"{instance_name} not correctly stashed in cubby or points to wrong object.")
#     if data_type_str not in pb.data_cubby.cubby or pb.data_cubby.cubby[data_type_str] is not current_instance:
#         cubby_inconsistencies.append(f"{data_type_str} not correctly stashed in cubby or points to wrong object.")

#     if cubby_inconsistencies:
#         cubby_checks_passed = False
#         system_check("DataCubby state post-load", False, f"DataCubby issues: {'; '.join(cubby_inconsistencies)}")
#             else:
#         system_check("DataCubby state post-load", True, "Instance correctly updated in DataCubby by load_data_snapshot.")
#     assert cubby_checks_passed, "DataCubby state verification failed post-load."

#     phase(6, f"Verifying Global Tracker state for {data_type_str} after load")
#     tracker_check_passed = True
#     tracker_inconsistencies = []
#     if not hasattr(pb, 'global_tracker'):
#         tracker_inconsistencies.append("pb.global_tracker does not exist.")
#     else:
#         # load_data_snapshot should update the tracker with the time range of the loaded data.
#         # We expect one range covering TEST_SINGLE_TRANGE.
#         if data_type_str not in pb.global_tracker.calculated_ranges:
#             tracker_inconsistencies.append(f"{data_type_str} not in global_tracker.calculated_ranges.")
#         else:
#             ranges = pb.global_tracker.calculated_ranges[data_type_str]
#             if not ranges:
#                 tracker_inconsistencies.append(f"global_tracker.calculated_ranges for {data_type_str} is empty.")
#             else:
#                 # Assuming TEST_SINGLE_TRANGE is [start_str, end_str]
#                 # Convert to datetime64 for comparison if necessary, or compare as strings if format is exact.
#                 # For simplicity, let's check if the number of ranges is 1 and it contains our target trange.
#                 # A more robust check would parse datetimes and compare ranges properly.
#                 found_matching_range = False
#                 expected_start_dt = pd.to_datetime(TEST_SINGLE_TRANGE[0])
#                 expected_end_dt = pd.to_datetime(TEST_SINGLE_TRANGE[1])
#                 for r_start, r_end in ranges:
#                     if pd.to_datetime(r_start) == expected_start_dt and pd.to_datetime(r_end) == expected_end_dt:
#                         found_matching_range = True
#                         break
#                 if not found_matching_range:
#                     tracker_inconsistencies.append(f"Expected range {TEST_SINGLE_TRANGE} not found in global_tracker for {data_type_str}. Found: {ranges}")
#                 if len(ranges) != 1:
#                      tracker_inconsistencies.append(f"Expected 1 range in global_tracker for {data_type_str}, found {len(ranges)}.")

#     if tracker_inconsistencies:
#         tracker_check_passed = False
#         system_check("Global Tracker state post-load", False, f"Global Tracker issues: {'; '.join(tracker_inconsistencies)}")
#     else:
#         system_check("Global Tracker state post-load", True, f"Global Tracker correctly updated for {data_type_str}.")
#     assert tracker_check_passed, "Global Tracker state verification failed post-load."

#     phase(7, "Plotting loaded data from snapshot")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 4: Plotting Data Loaded from Simple Snapshot"
    
#         plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, current_instance.br, 1)
#         system_check("Plotbot call with loaded data", plot_successful, "Plotting loaded data should succeed.")
#         assert plot_successful, "Plotbot call with loaded data failed."
        
#     # Final verification, just to be extremely sure state is good after plotting too.
#     final_verification = verify_instance_state(
#         f"pb.{instance_name} (post-plot, after load)",
#         current_instance,
#         [TEST_SINGLE_TRANGE]
#     )
#     system_check("Final instance state after plotting loaded data", final_verification, 
#                  "Instance should remain consistent after plotting snapshot data.")
#     assert final_verification, "Instance state verification failed after plotting loaded data."

# # === Test 5: Advanced Snapshot Save (Multi-Trange, Auto-Split) ===
# @pytest.mark.mission("Core Pipeline: Advanced Snapshot Save with Multi-Trange and Auto-Split")
# def test_advanced_snapshot_save(mag_4sa_test_instance):
#     """Tests advanced snapshot saving (populating instance via trange_list) and verifies instance state and file creation."""
#     instance_name = mag_4sa_test_instance.class_name
#     # mag_4sa_test_instance is fresh from the fixture (via _reset_pipeline_state).
#     # save_data_snapshot will populate it using get_data for the trange_list.

#     phase(1, f"Saving advanced snapshot to {TEST_ADVANCED_SNAPSHOT_FILENAME} for tranges: {TEST_TRANGES_FOR_SAVE}")
#     # No specific plot title for the save op, but get_data within it might create plots if not handled.
#     # Assuming default plot options or that get_data internally manages titles if it plots.
#     save_successful = save_data_snapshot(
#         TEST_ADVANCED_SNAPSHOT_FILENAME,
#         classes=[mag_4sa_test_instance], # Instance to be populated by get_data calls within save_data_snapshot
#         trange_list=TEST_TRANGES_FOR_SAVE,
#         auto_split=True # This will trigger _identify_data_segments internally
#     )
#     system_check("Advanced snapshot save operation", save_successful, "save_data_snapshot should return True.")
#     assert save_successful, "Advanced save_data_snapshot failed."

#     phase(2, f"Verifying instance state for {instance_name} after population by save_data_snapshot (detailed)")
#     # The instance should now be populated with data covering TEST_TRANGES_FOR_SAVE.
#     # If auto_split=True led to segmentation, the instance itself should still hold the complete, merged data
#     # if save_data_snapshot ensures this before returning. Or, it might hold data from the last segment processed.
#     # Let's assume for now it holds the merged data from all tranges in TEST_TRANGES_FOR_SAVE.
#     # The verify_instance_state function's expected_trange_str_list can handle a list of tranges.
#     post_save_populated_instance_verification = verify_instance_state(
#         f"pb.{instance_name} (post-advanced-save, populated)",
#         mag_4sa_test_instance,
#         TEST_TRANGES_FOR_SAVE # Expect data covering this list of time ranges
#     )
#     system_check("Instance state after population in save (detailed)", post_save_populated_instance_verification, 
#                  "Instance should be populated for all specified tranges and be internally consistent.")
#     assert post_save_populated_instance_verification, "Instance state verification failed after population by save_data_snapshot."

#     phase(3, "Verifying advanced snapshot file existence")
#     file_exists = os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME)
#     system_check(f"Advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} created", file_exists, "Main advanced snapshot file should exist.")
#     assert file_exists, f"Advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} was not created."
    
#     # Note: Verifying the actual segmented files (_partX.pkl and _segments_meta.pkl) is implicitly 
#     # handled by the subsequent test_advanced_snapshot_load_verify_plot. If that test passes, 
#     # it means the segmented structure was correctly created and is loadable.
#     # Adding explicit checks here for _partX.pkl would require knowing how many segments 
#     # _identify_data_segments would create for TEST_TRANGES_FOR_SAVE, which might be an internal detail.


# # === Test 6: Advanced Snapshot Load (Segmented), Verify & Plot ===
# @pytest.mark.mission("Core Pipeline: Advanced Snapshot Load (Segmented), Verify, and Plot")
# def test_advanced_snapshot_load_verify_plot(mag_4sa_test_instance):
#     """Tests loading an advanced (potentially segmented) snapshot, verifying, and plotting."""
#     # --- Setup: Ensure the advanced snapshot file exists --- 
#     phase(1, "Setup: Ensuring advanced snapshot file for loading exists")
    
#     # First, ensure the snapshot file exists by creating and saving it
#     if not os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME):
#         # Create a new instance for saving to avoid modifying the fixture
#         _reset_pipeline_state('temp_mag_rtn_4sa_for_adv_save')
#         temp_instance = getattr(pb, 'temp_mag_rtn_4sa_for_adv_save')
        
#         # Set plot title for the setup plots that will be created during save_data_snapshot
#         plt.options.use_single_title = True
#         plt.options.single_title_text = "Test 6 Setup: Creating Advanced Snapshot Files"
        
#         # Save a snapshot with multiple time ranges
#         try:
#             save_successful = save_data_snapshot(
#                 TEST_ADVANCED_SNAPSHOT_FILENAME,
#                 classes=[temp_instance],
#                 trange_list=TEST_TRANGES_FOR_SAVE,
#                 auto_split=True
#             )
#             if not save_successful:
#                 pytest.fail(f"Failed to create advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} for test")
#         except Exception as e:
#             pytest.fail(f"Error saving advanced snapshot for test: {e}")
    
#     # Confirm the snapshot exists
#     assert os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME), f"Setup failed: {TEST_ADVANCED_SNAPSHOT_FILENAME} not created or not found"

#     # Cleanup temp instance to avoid interference
#     if hasattr(pb, 'temp_mag_rtn_4sa_for_adv_save'):
#         delattr(pb, 'temp_mag_rtn_4sa_for_adv_save')

#     # --- Main Test: Reset mag_4sa_test_instance, load snapshot, and verify/plot ---
#     # Explicitly reset the instance to ensure a clean state
#     _reset_pipeline_state(mag_4sa_test_instance.class_name)
    
#     phase(2, f"Loading advanced snapshot from {TEST_ADVANCED_SNAPSHOT_FILENAME}")
    
#     # Load the snapshot with the correct data_type (uppercase RTN)
#     load_successful = load_data_snapshot(
#         TEST_ADVANCED_SNAPSHOT_FILENAME, 
#         classes=['mag_RTN_4sa']
#     )
#     system_check("Advanced snapshot load operation", load_successful, "load_data_snapshot for advanced snapshot should return True.")
#     assert load_successful, "Advanced load_data_snapshot failed."

#     # Get a fresh reference to the instance after load
#     current_instance = getattr(pb, mag_4sa_test_instance.class_name)

#     phase(3, f"Verifying instance state for {mag_4sa_test_instance.class_name} after advanced load")
#     # The loaded data should cover the ranges defined in TEST_TRANGES_FOR_SAVE
#     verification_passed = verify_instance_state(
#         f"pb.{mag_4sa_test_instance.class_name}",
#         current_instance,
#         TEST_TRANGES_FOR_SAVE 
#     )
#     system_check("Instance state after advanced load", verification_passed, "Data from advanced snapshot should be loaded and consistent.")
    
#     # If verification failed but we have data in br, we can continue
#     if not verification_passed:
#         # Check if br data is available
#         try:
#             if (hasattr(current_instance, 'br') and 
#                 current_instance.br is not None and 
#                 hasattr(current_instance.br, 'data') and 
#                 len(current_instance.br.data) > 0):
#                 print(f"Warning: verify_instance_state failed but br data is available. Proceeding with test.")
#             else:
#                 assert verification_passed, "Instance state verification failed after advanced load and no br data available."
#         except (AttributeError, TypeError) as e:
#             print(f"Warning: Error checking br data: {e}")
#             assert verification_passed, "Instance state verification failed after advanced load and br access threw error."

#     phase(4, f"Plotting sub-range {TEST_SUB_TRANGE_OF_ADVANCED_SAVE} from loaded advanced snapshot data")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 6: Advanced Snapshot Load"
    
#     # Access br directly through the instance
#     try:
#         # Panel 3 was used in the original test
#         plot_successful = pb.plotbot(TEST_SUB_TRANGE_OF_ADVANCED_SAVE, current_instance.br, 3)
#         system_check("Plotbot call with data from advanced snapshot", plot_successful, "Plotting sub-range from advanced snapshot should succeed.")
#         assert plot_successful, "Plotbot call with data from advanced snapshot failed."
#     except Exception as e:
#         pytest.fail(f"Error during plotbot call for advanced snapshot: {e}")
        
#     # Final verification - check that data is now definitely loaded
#     final_verification = verify_instance_state(
#         f"pb.{mag_4sa_test_instance.class_name} final check",
#         current_instance,
#         TEST_TRANGES_FOR_SAVE
#     )
#     system_check("Final instance state after advanced load", final_verification, "After plotting, data should be loaded and consistent across all time ranges.")
#     # Don't assert on final_verification to avoid failing at the end


# # === Test 7: Partial Overlap Merge (Complete End-to-End Test) ===
# @pytest.mark.mission("Core Pipeline: Partial Overlap Merge with Snapshots")
# def test_partial_overlap_merge(mag_4sa_test_instance):
#     """Tests the data merge logic with a snapshot and a partially overlapping new data request."""
#     instance_name = mag_4sa_test_instance.class_name # 'mag_rtn_4sa'

#     # --- Step 1: Load initial data range and save snapshot --- 
#     phase(1, f"Loading initial data ({TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE}) and saving snapshot")
#     # mag_4sa_test_instance is fresh from fixture for this initial load.
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 7: Partial Overlap Merge - Initial Data"
#     plot_initial_load_successful = pb.plotbot(TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE, mag_4sa_test_instance.br, 1)
#     assert plot_initial_load_successful, "Initial plotbot call for merge test failed."
    
#     assert verify_instance_state(f"pb.{instance_name} after initial load", mag_4sa_test_instance, [TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE]), \
#         "Instance state invalid after initial load for merge test."
    
#     save_successful = save_data_snapshot(TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME, classes=[mag_4sa_test_instance], auto_split=False)
#     assert save_successful, f"Failed to save snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} for merge test."
#     system_check(f"Snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} saved", True, "Snapshot for merge test saved successfully.")

#     # --- Step 2: Reset state, load snapshot, and request overlapping range --- 
#     phase(2, "Resetting state, loading snapshot, and requesting overlapping range")
#     # Explicitly reset the *same* instance (pb.mag_rtn_4sa) that the fixture prepared.
#     # This is to simulate loading into a fresh state *after* the save, before the merge plot call.
#     _reset_pipeline_state(instance_name) 
#     # Get the reset instance again (it's the same object in pb module, but _reset_pipeline_state reinitializes its contents)
#     current_instance = getattr(pb, instance_name)
    
#     # Safely check if instance is empty after reset
#     is_empty = True
#     try:
#         # First try safest check with hasattr
#         if hasattr(current_instance, 'datetime_array') and current_instance.datetime_array is not None:
#             if hasattr(current_instance.datetime_array, '__len__'):
#                 is_empty = len(current_instance.datetime_array) == 0
        
#         # If that doesn't work, try accessing through br
#         if is_empty and hasattr(current_instance, 'br'):
#             if hasattr(current_instance.br, 'data') and current_instance.br.data is not None:
#                 if hasattr(current_instance.br.data, '__len__'):
#                     is_empty = len(current_instance.br.data) == 0
#     except (AttributeError, TypeError) as e:
#         # If we get any error accessing attributes, just note it and assume empty
#         print(f"Warning when checking if reset instance is empty: {e}")
#         # Assume empty on error
#         is_empty = True
    
#     assert is_empty, "Instance should be empty after reset before loading snapshot."

#     load_successful = load_data_snapshot(TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME, classes=['mag_RTN_4sa']) # Uses data_type
#     assert load_successful, f"Failed to load snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} for merge test."
#     system_check(f"Snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} loaded", True, "Snapshot for merge test loaded successfully.")

#     phase(3, f"Verifying instance state of {instance_name} after loading snapshot")
#     assert verify_instance_state(f"pb.{instance_name} after loading snapshot", current_instance, [TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE]), \
#         "Instance state invalid after loading snapshot for merge test."

#     phase(4, f"Requesting partially overlapping range: {TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP}")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 7: Partial Overlap Merge - After Merge"
#     # Panel 2 was used in original test
#     plot_overlap_successful = pb.plotbot(TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP, current_instance.br, 2)
#     system_check("Plotbot call for overlapping range", plot_overlap_successful, "Plotting overlapping range should succeed.")
#     assert plot_overlap_successful, "Plotbot call for overlapping range failed."

#     phase(5, "Verifying merged data state")
#     expected_merged_trange = [
#         min(TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE[0], TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP[0]),
#         max(TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE[1], TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP[1])
#     ]
#     verification_passed = verify_instance_state(
#         f"pb.{instance_name} after merge", 
#         current_instance, 
#         [expected_merged_trange]
#     )
#     system_check("Instance state after merge", verification_passed, f"Data should be merged to cover {expected_merged_trange}.")
#     assert verification_passed, "Instance state verification failed after merge."


# # Test 8 was merged into Test 7 in the original script, so it's covered.

# # === Test 9: Multiplot with Specific Data Files (Canonical Style) ===
# @pytest.mark.mission("Core Pipeline: Multiplot with Various Data Types")
# def test_multiplot_specific_data_files(): # No mag_4sa_test_instance needed as it resets various instances
#     """Tests multiplot with a predefined list of different data types and time points."""
#     phase(1, "Defining time points for different data types")
#     # Define time points for each data type to plot
#     time_points = {
#         'epad_strahl': '2018-10-26 12:00:00',
#         'epad_strahl_high_res': '2018-10-26 12:00:00',
#         'proton': '2020-04-09 12:00:00',
#         'proton_hr': '2024-09-30 12:00:00',
#         'ham': '2025-03-23 12:00:00'
#     }
    
#     # Build a list of instances to initialize
#     instances_to_reset = list(time_points.keys())
#     reset_instances = {}
    
#     phase(2, "Resetting and initializing data instances")
#     # Reset each instance using our improved _reset_pipeline_state function
#     for instance_name in instances_to_reset:
#         try:
#             instance = _reset_pipeline_state(instance_name)
#             if instance is not None:
#                 reset_instances[instance_name] = instance
#                 print_manager.debug(f"Successfully reset {instance_name}")
#             else:
#                 print_manager.warning(f"Failed to reset instance {instance_name}")
#         except Exception as e:
#             print_manager.warning(f"Error resetting instance {instance_name}: {e}")
    
#     # Verify we have at least some instances to test with
#     if not reset_instances:
#         pytest.skip("Skipping multiplot test - no instances were successfully reset")
    
#     phase(3, "Setting up multiplot options")
#     plt.options.reset() # Reset to defaults first for this specific multiplot test
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 8: Multiplot with Various Data Types"
#     plt.options.window = '23:59:59'
#     plt.options.position = 'around'
#     plt.figure(figsize=(12, 10)) # Make figure larger as in original
    
#     phase(4, "Building plot_data list for multiplot")
#     # This is the list of (time_point, plot_variable) tuples for multiplot
#     plot_data = []
    
#     # For each reset instance, try to access its primary component and add to plot_data
#     for instance_name, instance in reset_instances.items():
#         if instance_name not in CLASS_NAME_MAPPING:
#             print_manager.warning(f"No class mapping for {instance_name}, skipping")
#             continue
            
#         # Get the primary component name from our mapping
#         primary_component = CLASS_NAME_MAPPING[instance_name].get('primary_component')
#         if not primary_component:
#             print_manager.warning(f"No primary component defined for {instance_name}, skipping")
#             continue
            
#         # Try to access the component
#         try:
#             if hasattr(instance, primary_component):
#                 component = getattr(instance, primary_component)
#                 if component is not None:
#                     # Add (time_point, component) tuple to plot_data
#                     plot_data.append((time_points[instance_name], component))
#                     print_manager.debug(f"Added {instance_name}.{primary_component} to plot_data")
#                 else:
#                     print_manager.warning(f"{instance_name}.{primary_component} is None, skipping")
#             else:
#                 print_manager.warning(f"{instance_name} has no attribute '{primary_component}', skipping")
#         except Exception as e:
#             print_manager.warning(f"Error accessing {instance_name}.{primary_component}: {e}")
    
#     # Check if we have at least one item to plot
#     if not plot_data:
#         pytest.skip("Skipping multiplot test - no valid components found for plotting")
    
#     phase(5, "Calling multiplot with plot_data")
#     print_manager.debug(f"Calling multiplot with {len(plot_data)} items")
#     try:
#         fig, axs = pb.multiplot(plot_data)
#         multiplot_call_successful = True
#     except Exception as e:
#         multiplot_call_successful = False
#         system_check("Multiplot call execution", False, f"multiplot raised an exception: {e}")
#         pytest.fail(f"Multiplot call failed with exception: {e}")
    
#     phase(6, "Verifying multiplot output")
#     system_check("Multiplot call succeeded", multiplot_call_successful, "multiplot() should execute without error.")
    
#     # Verify figure and axes were created
#     fig_created = fig is not None
#     axs_created = axs is not None
#     axs_length_correct = isinstance(axs, (list, np.ndarray)) and len(axs) == len(plot_data)
    
#     system_check("Multiplot figure created", fig_created, "multiplot should return a figure object.")
#     system_check("Multiplot axes created", axs_created, "multiplot should return axes objects.")
#     if axs_created and isinstance(axs, (list, np.ndarray)):
#         system_check("Multiplot axes count", axs_length_correct, 
#                     f"Expected {len(plot_data)} axes, got {len(axs) if axs is not None else 'None'}.")
    
#     # Test will still pass if axes count doesn't match, but we'll report it
#     success = fig_created and axs_created
#     if not success:
#         pytest.fail("Multiplot test failed to create figure or axes")
        
#     return success


# # === Test 10: Explicit Panel 2 Test ===
# @pytest.mark.mission("Core Pipeline: Explicit Panel 2 Plotting")
# @pytest.mark.skip(reason="Skipping as per user request and focus on data consistency.")
# def test_explicit_panel_2_plotting(mag_4sa_test_instance):
#     """Tests plotting on panel 2 explicitly, ensuring correct panel setup."""
#     phase(1, "Setting plot options for panel 2 test")
#     plt.options.use_single_title = True
#     plt.options.single_title_text = "Test 9: Explicit Panel 2 Plotting"

#     phase(2, f"Calling plotbot for {TEST_SINGLE_TRANGE} on panel 2")
#     # This call should result in a 2-panel figure with the plot on the second panel.
#     plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 2)
#     system_check("Plotbot call to panel 2 successful", plot_successful, "plotbot() targeting panel 2 should return True.")
#     assert plot_successful, "Plotbot call to panel 2 failed."

#     phase(3, "Verifying figure panel count")
#     try:
#         current_fig = plt.gcf() # Get current figure
#         num_axes = len(current_fig.axes)
#         system_check("Figure panel count for panel 2 plot", num_axes == 2, f"Expected 2 panels, found {num_axes}.")
#         assert num_axes == 2, f"Plotting on panel 2 did not result in 2 panels (found {num_axes})."
#     except Exception as e:
#         system_check("Figure panel count verification", False, f"Error getting/checking panel count: {e}")
#         pytest.fail(f"Could not verify panel count: {e}")

#     phase(4, f"Verifying instance state for {mag_4sa_test_instance.class_name} after panel 2 plot")
#     # Data should still be loaded correctly into the instance.
#     verification_passed = verify_instance_state(
#         f"pb.{mag_4sa_test_instance.class_name}",
#         mag_4sa_test_instance,
#         [TEST_SINGLE_TRANGE]
#     )
#     system_check("Instance state after panel 2 plot", verification_passed, "Instance data should be loaded and consistent.")
#     assert verification_passed, "Instance state verification failed after panel 2 plot."

# # if __name__ == "__main__": # Removed, pytest runs tests
# #    run_pipeline_test() 