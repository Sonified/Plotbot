# tests/test_plotbot_core_pipeline.py
"""
End-to-End Test for Plotbot's Core Data Pipeline.

This test verifies the primary workflow for a standard data type (`mag_rtn_4sa`):
1.  **Initial Data Load & Plot:** 
    - A `pb.plotbot()` call for a specific time range (`TEST_TRANGE_SHORT`) and variable
      (`pb.mag_rtn_4sa.br`) should trigger the full data loading pipeline:
        - `plotbot.get_data` orchestrates the process.
        - `plotbot.data_tracker` is checked (cache miss expected).
        - `plotbot.data_download` (if needed, via `get_data` -> `import_data_function` path,
          though this test assumes local files or successful prior download for speed).
        - `plotbot.data_import.import_data_function` reads the CDF, extracts raw variables
          (e.g., 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc') based on `plotbot.data_classes.psp_data_types`,
          and returns a `DataObject` (with `.times` as TT2000 and `.data` as a dict).
        - `plotbot.data_cubby.update_global_instance` receives this `DataObject`.
          Since the global `pb.mag_rtn_4sa` instance is initially empty, it calls
          `pb.mag_rtn_4sa.update()`, which calls `pb.mag_rtn_4sa.calculate_variables()`.
        - `mag_rtn_4sa_class.calculate_variables()` processes the `DataObject`: sets `self.time` (TT2000),
          `self.datetime_array` (datetime64), `self.field`, and populates `self.raw_data` with
          calculated components (e.g., 'br', 'bt', 'bn', 'bmag').
        - `mag_rtn_4sa_class.set_ploptions()` creates `plot_manager` attributes (e.g., `self.br`).
        - `plotbot.data_tracker` is updated with the processed time range.
    - Verification: `pb.mag_rtn_4sa` should contain data for `TEST_TRANGE_SHORT` and its internal
      arrays (`.time`, `.datetime_array`, `.field`, `.raw_data` components) should be consistent in length.
      A plot window should appear (or the call should complete without data errors).

2.  **Cached Data Retrieval & Plot:**
    - A second, identical `pb.plotbot(TEST_TRANGE_SHORT, pb.mag_rtn_4sa.br, 1)` call is made.
    - `plotbot.get_data` should now find (via `plotbot.data_tracker`) that the data for this
      `trange` and `data_type` is already processed.
    - It should retrieve the existing `pb.mag_rtn_4sa` instance directly from `plotbot.data_cubby.grab()`
      without re-triggering import or calculations.
    - Verification: `pb.mag_rtn_4sa` should be the same (or equivalent) as at the end of Test 1.
      A plot window should appear.

3.  **Snapshot Save, Reset, Load & Plot:**
    - The current state of `pb.mag_rtn_4sa` (containing data for `TEST_TRANGE_SHORT`) is saved
      to a snapshot using `plotbot.data_snapshot.save_data_snapshot`.
      To test merging within `save_data_snapshot` and subsequent loading of segments, we use
      `TEST_TRANGES_FOR_SAVE` (two distinct short ranges) and `auto_split=True`.
    - The global `pb.mag_rtn_4sa` instance is reset to an empty state, and its corresponding
      entries in `DataCubby` and `DataTracker` are cleared to simulate a new session.
    - `plotbot.data_snapshot.load_data_snapshot` is called to load the saved file.
        - This will load segments if the snapshot was saved with `auto_split=True`.
        - For each segment, it reconstructs a `SimpleDataObject` where the `.data` dictionary
          contains the primary field key (e.g., 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc') by stacking
          components from the segment's `raw_data`.
        - It calls `plotbot.data_cubby.update_global_instance` for each segment, using the
          `is_segment_merge` flag to distinguish the first segment (uses `instance.update()`) 
          from subsequent segments (uses `DataCubby`'s merge logic, which now ensures `.time`
          is a consistent int64 version of `.datetime_array`).
        - After all segments for a base class are merged, `ensure_internal_consistency()` and
          `set_ploptions()` are called on the fully merged global instance.
        - `plotbot.data_tracker` is updated with the full time range covered by the loaded snapshot.
    - Verification: The reloaded `pb.mag_rtn_4sa` should contain the combined data from the snapshot
      and be internally consistent.
    - A final `pb.plotbot()` call using data from the reloaded `pb.mag_rtn_4sa` is made to ensure
      it's usable for plotting.

Relevant Modules & Files:
- Test Script: `tests/test_plotbot_core_pipeline.py` (this file)
- Main Plotting: `plotbot/plotbot_main.py` (contains `plotbot()`)
- Data Orchestration: `plotbot/get_data.py`
- Data Configuration: `plotbot/data_classes/psp_data_types.py`
- Data Import from Files: `plotbot/data_import.py` (contains `import_data_function`)
- Data Classes: `plotbot/data_classes/psp_mag_classes.py` (e.g., `mag_rtn_4sa_class`)
- Data Caching/Registry: `plotbot/data_cubby.py`
- Processed Range Tracking: `plotbot/data_tracker.py`
- Snapshotting: `plotbot/data_snapshot.py`
"""
import sys
import os
import numpy as np
import pandas as pd
import time as pytime # Alias to avoid conflict

# Adjust path to import plotbot modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot as pb 
from plotbot import print_manager
from plotbot.data_snapshot import save_data_snapshot, load_data_snapshot
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class

SNAPSHOT_FILENAME = "test_core_pipeline_mag_rtn_4sa"
# Use 2 distinct short ranges for save_data_snapshot to test merging and segmentation.
TEST_TRANGES_FOR_SAVE = [
    ['2021-10-26 02:00:00', '2021-10-26 02:10:00'], 
    ['2021-10-26 02:15:00', '2021-10-26 02:25:00'] 
]
# Single short trange for initial load tests and final plot after snapshot load.
# This range should be covered by TEST_TRANGES_FOR_SAVE.
TEST_SINGLE_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00'] 

def print_test_result(test_name, success, message=""):
    status_icon = "✅ PASS" if success else "❌ FAIL"
    full_message = f"{status_icon}: {test_name}"
    if not success and message:
        full_message += f" - {message}"
    print(full_message)
    return success

def verify_instance_state(instance_label, instance_obj, expected_trange_str_list, expect_data=True, expected_points_approx=None):
    print(f"--- Verifying instance state: {instance_label} (ID: {id(instance_obj)}) ---")
    if not isinstance(instance_obj, mag_rtn_4sa_class):
        print(f"  FAIL: Instance is not of type mag_rtn_4sa_class (is {type(instance_obj)})" )
        return False

    dt_array = getattr(instance_obj, 'datetime_array', None)
    time_arr = getattr(instance_obj, 'time', None)
    field_arr = getattr(instance_obj, 'field', None)
    raw_data = getattr(instance_obj, 'raw_data', {})
    br_arr = raw_data.get('br')

    dt_len = len(dt_array) if dt_array is not None and hasattr(dt_array, '__len__') else 0
    print(f"    {instance_label} - datetime_array len: {dt_len if dt_array is not None else 'None'}")

    if expect_data:
        if not (dt_len > 0):
            print(f"    ERROR: {instance_label}.datetime_array is empty or None, but data was expected for range(s) like {expected_trange_str_list}.")
            return False
        if expected_points_approx is not None and not (expected_points_approx * 0.8 < dt_len < expected_points_approx * 1.2):
            print(f"    WARNING: {instance_label}.datetime_array length ({dt_len}) is not close to expected ({expected_points_approx}).")
        
        time_len = len(time_arr) if time_arr is not None and hasattr(time_arr, '__len__') else 0
        field_len = field_arr.shape[0] if field_arr is not None and hasattr(field_arr, 'shape') and field_arr.ndim > 0 else 0
        br_len = len(br_arr) if br_arr is not None and hasattr(br_arr, '__len__') else 0

        print(f"    {instance_label} - time len          : {time_len if time_arr is not None else 'None'}")
        print(f"    {instance_label} - field shape       : {field_arr.shape if field_arr is not None else 'None'}")
        print(f"    {instance_label} - raw_data['br'] len: {br_len if br_arr is not None else 'None'}")

        consistent = True
        if not (time_len == dt_len):
            print(f"    ERROR: {instance_label} - time length ({time_len}) != datetime_array length ({dt_len}).")
            consistent = False
        if not (field_len == dt_len):
            print(f"    ERROR: {instance_label} - field length ({field_len}) != datetime_array length ({dt_len}).")
            consistent = False
        if not (br_len == dt_len):
            print(f"    ERROR: {instance_label} - raw_data['br'] length ({br_len}) != datetime_array length ({dt_len}).")
            consistent = False
        
        if consistent:
            print(f"    {instance_label} appears internally consistent with {dt_len} data points.")
        else:
            print(f"    {instance_label} has INCONSISTENCIES.")
        return consistent
    else: 
        if dt_len == 0 and (time_arr is None or len(time_arr)==0) and (field_arr is None or (hasattr(field_arr, 'size') and field_arr.size==0) or (not hasattr(field_arr, 'size')) ) :
             print(f"    {instance_label} is consistently empty, as expected.")
             return True
        else:
            print(f"    ERROR: {instance_label} was expected to be empty but is not. Dt_len: {dt_len}, Time_len: {time_len if time_arr is not None else 'None'}")
            return False

def run_pipeline_test():
    print_manager.show_debug = True
    print_manager.show_datacubby = True
    print_manager.show_data_snapshot = True
    print_manager.show_tracker = True

    overall_success = True
    snapshot_filepath_actual = None 
    mag_4sa_instance_name = 'mag_rtn_4sa'

    # --- Test Initialization: Clean Slate for pb.mag_rtn_4sa --- 
    print_manager.status(f"--- Test Script Setup: Ensuring clean state for pb.{mag_4sa_instance_name} ---")
    if hasattr(pb, mag_4sa_instance_name):
        delattr(pb, mag_4sa_instance_name)
    current_instance_for_test = mag_rtn_4sa_class(None) 
    setattr(pb, mag_4sa_instance_name, current_instance_for_test)
    
    cubby_key_to_clear = getattr(current_instance_for_test, 'data_type', 'mag_RTN_4sa').lower()
    config_key_to_clear = getattr(current_instance_for_test, 'data_type', 'mag_RTN_4sa')
    if hasattr(pb, 'data_cubby'):
        pb.data_cubby.class_registry.pop(cubby_key_to_clear, None)
        pb.data_cubby.cubby.pop(cubby_key_to_clear, None)
        pb.data_cubby.class_registry.pop(config_key_to_clear, None) 
        pb.data_cubby.cubby.pop(config_key_to_clear, None)
    if hasattr(pb, 'global_tracker'):
        pb.global_tracker.calculated_ranges.pop(cubby_key_to_clear, None)
        pb.global_tracker.imported_ranges.pop(cubby_key_to_clear, None)
        pb.global_tracker.calculated_ranges.pop(config_key_to_clear, None) 
        pb.global_tracker.imported_ranges.pop(config_key_to_clear, None)
    
    if hasattr(pb, 'data_cubby') and hasattr(pb, mag_4sa_instance_name):
        instance_to_stash = getattr(pb, mag_4sa_instance_name)
        key_for_stashing = getattr(instance_to_stash, 'class_name', mag_4sa_instance_name) 
        pb.data_cubby.stash(instance_to_stash, class_name=key_for_stashing)
        print(f"  Explicitly stashed new pb.{mag_4sa_instance_name} (ID: {id(instance_to_stash)}) in DataCubby.")
    
    print_manager.status(f"  Initialized test with fresh pb.{mag_4sa_instance_name} (ID: {id(getattr(pb, mag_4sa_instance_name))}). Its .data_type = '{getattr(pb.mag_rtn_4sa, 'data_type', 'ERROR')}'")

    # === Test 1: Initial data load and plotbot() call ===
    print("\n--- Test 1: Initial Load & plotbot() call ---")
    test1_passed = pb.plotbot(TEST_SINGLE_TRANGE[0], pb.mag_rtn_4sa.br)
    overall_success &= print_test_result("Test 1: Initial Load & plotbot() call", test1_passed)
    
    # === Test 2: Second plotbot() call (should use cached data from DataCubby/Tracker) ===
    print("\n--- Test 2: Second plotbot() call (Cache Check) ---")
    test2_passed = pb.plotbot(TEST_SINGLE_TRANGE[0], pb.mag_rtn_4sa.br, 1)
    overall_success &= print_test_result("Test 2: Second plotbot() call (Cache Check)", test2_passed)

    # === Test 3: Snapshot Save, Reset, Load & Plot ===
    print("\n--- Test 3: Snapshot Save, Reset, Load & Plot ---")
    test3_passed = save_data_snapshot(SNAPSHOT_FILENAME, TEST_TRANGES_FOR_SAVE, auto_split=True)
    overall_success &= print_test_result("Test 3: Snapshot Save, Reset, Load & Plot", test3_passed)

    if not overall_success:
        print("\n--- Test Results Summary ---")
        print(f"Overall Test Result: {'❌ FAIL' if not overall_success else '✅ PASS'}")
    else:
        print("\n--- Test Results Summary ---")
        print(f"All tests passed successfully!")

    return overall_success 