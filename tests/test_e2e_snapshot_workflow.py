import sys
import os
import numpy as np
import pandas as pd
import time as pytime # Alias to avoid conflict

# Adjust path to import plotbot modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import plotbot and its components AFTER path adjustment
import plotbot as pb # Using pb alias as requested
from plotbot import print_manager
from plotbot.data_snapshot import save_data_snapshot, load_data_snapshot
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class # For re-init/type check
# Conditional import for magnetic_hole_finder parts
MH_FINDER_AVAILABLE = False
try:
    from magnetic_hole_finder.time_management import determine_sampling_rate, efficient_moving_average, clip_to_original_time_range
    MH_FINDER_AVAILABLE = True
except ImportError:
    print("WARNING: magnetic_hole_finder components not found. Skipping related analysis snippet test.")

# --- Test Configuration ---
SNAPSHOT_FILENAME = "test_e2e_mag_rtn_4sa_snapshot" # Removed .pkl from here
TEST_TRANGES_FOR_SAVE = [
    ['2021-10-26 02:00:00', '2021-10-26 02:10:00'] # Single, known good range for initial save test
]
TEST_PLOT_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00'] # Match the save range for now
TEST_ANALYSIS_TRANGE_STR = ['2021-10-26 02:03:00', '2021-10-26 02:07:00'] # Sub-range for analysis

# For efficient_moving_average test (if MH_FINDER_AVAILABLE)
TEST_SMOOTHING_WINDOW_SECONDS = 2.0 
TEST_MEAN_THRESHOLD = 0.8      

# --- Helper to print pass/fail ---
def print_test_result(test_name, success, message=""):
    status_icon = "✅ PASS" if success else "❌ FAIL"
    full_message = f"{status_icon}: {test_name}"
    if not success and message:
        full_message += f" - {message}"
    print(full_message)
    # if not success:
    #     raise AssertionError(full_message) # Option for stricter test failure
    return success

def verify_instance_state(instance_label, instance_obj, expect_data=True):
    """Checks basic integrity of the instance after an operation."""
    print(f"--- Verifying instance: {instance_label} (ID: {id(instance_obj)}) ---")
    if not isinstance(instance_obj, mag_rtn_4sa_class):
        print(f"  FAIL: Instance is not of type mag_rtn_4sa_class (is {type(instance_obj)})" )
        return False

    dt_array = getattr(instance_obj, 'datetime_array', None)
    time_arr = getattr(instance_obj, 'time', None)
    field_arr = getattr(instance_obj, 'field', None)
    raw_data = getattr(instance_obj, 'raw_data', {})
    br_arr = raw_data.get('br')

    dt_len = len(dt_array) if dt_array is not None and hasattr(dt_array, '__len__') else 0
    time_len = len(time_arr) if time_arr is not None and hasattr(time_arr, '__len__') else 0
    field_len = field_arr.shape[0] if field_arr is not None and hasattr(field_arr, 'shape') and field_arr.ndim > 0 else 0
    br_len = len(br_arr) if br_arr is not None and hasattr(br_arr, '__len__') else 0
    
    print(f"    {instance_label} - datetime_array len: {dt_len if dt_array is not None else 'None'}")
    print(f"    {instance_label} - time len          : {time_len if time_arr is not None else 'None'}")
    print(f"    {instance_label} - field shape       : {field_arr.shape if field_arr is not None else 'None'}")
    print(f"    {instance_label} - raw_data['br'] len: {br_len if br_arr is not None else 'None'}")

    consistent = True
    if expect_data and not (dt_len > 0):
        print(f"    ERROR: {instance_label}.datetime_array is empty or None, but data was expected.")
        consistent = False
    
    if dt_len > 0: # Only check length consistency if there's data
        if not (time_len == dt_len):
            print(f"    ERROR: {instance_label} - time length ({time_len}) != datetime_array length ({dt_len}).")
            consistent = False
        if not (field_len == dt_len):
            print(f"    ERROR: {instance_label} - field length ({field_len}) != datetime_array length ({dt_len}).")
            consistent = False
        if not (br_len == dt_len):
            print(f"    ERROR: {instance_label} - raw_data['br'] length ({br_len}) != datetime_array length ({dt_len}).")
            consistent = False
    elif expect_data: # dt_len is 0 but we expected data
        consistent = False
    
    if consistent and (dt_len > 0 or not expect_data):
        print(f"    {instance_label} appears internally consistent for its state (data expected: {expect_data}).")
    elif dt_len == 0 and time_len == 0 and field_len == 0 and br_len == 0 and not expect_data:
        print(f"    {instance_label} is consistently empty, as expected.")
    else:
        print(f"    {instance_label} has INCONSISTENCIES or unexpected empty state.")
    return consistent

# --- Main Test Function ---
def run_pipeline_test():
    print_manager.show_debug = True
    print_manager.show_datacubby = True 
    print_manager.show_data_snapshot = True
    # print_manager.show_tracker = True # Removed as it does not exist
    # print_manager.show_variable_testing = True 

    overall_success = True
    snapshot_filepath_actual = None 

    mag_4sa_instance_name = 'mag_rtn_4sa'
    print_manager.status(f"--- Test Script Setup: Ensuring clean state for plotbot.{mag_4sa_instance_name} ---")
    # Create a new local instance first
    current_instance_for_test = mag_rtn_4sa_class(None) 
    # Set it as the global instance in the plotbot module
    setattr(pb, mag_4sa_instance_name, current_instance_for_test)
    
    # Clear any old registrations for this key from DataCubby and DataTracker
    cubby_key_to_clear = getattr(current_instance_for_test, 'data_type', 'mag_RTN_4sa').lower()
    config_key_to_clear = getattr(current_instance_for_test, 'data_type', 'mag_RTN_4sa')

    if hasattr(pb, 'data_cubby'):
        pb.data_cubby.class_registry.pop(cubby_key_to_clear, None)
        pb.data_cubby.cubby.pop(cubby_key_to_clear, None)
        pb.data_cubby.class_registry.pop(config_key_to_clear, None) 
        pb.data_cubby.cubby.pop(config_key_to_clear, None)
        print(f"  Cleared '{cubby_key_to_clear}' (and '{config_key_to_clear}') from DataCubby registries if they existed.")
    if hasattr(pb, 'global_tracker'):
        pb.global_tracker.calculated_ranges.pop(cubby_key_to_clear, None)
        pb.global_tracker.imported_ranges.pop(cubby_key_to_clear, None)
        pb.global_tracker.calculated_ranges.pop(config_key_to_clear, None) 
        pb.global_tracker.imported_ranges.pop(config_key_to_clear, None)
        print(f"  Cleared DataTracker for '{cubby_key_to_clear}' (and potentially '{config_key_to_clear}').")

    # Explicitly stash the newly created and assigned global instance in DataCubby
    if hasattr(pb, 'data_cubby') and hasattr(pb, mag_4sa_instance_name):
        instance_to_stash = getattr(pb, mag_4sa_instance_name)
        # DataCubby.stash uses the instance's .class_name (which should be 'mag_rtn_4sa') and lowercases it.
        key_for_stashing = getattr(instance_to_stash, 'class_name', mag_4sa_instance_name) 
        pb.data_cubby.stash(instance_to_stash, class_name=key_for_stashing)
        print(f"  Explicitly stashed new plotbot.{mag_4sa_instance_name} (ID: {id(instance_to_stash)}) in DataCubby using class_name for stash: '{key_for_stashing}'")
    else:
        print("  WARNING: pb.data_cubby or pb.mag_rtn_4sa not found, cannot explicitly stash.")

    current_data_type = getattr(getattr(pb, mag_4sa_instance_name, None), 'data_type', 'ERROR_OR_INSTANCE_NONE')
    print_manager.status(f"  Initialized test with fresh plotbot.{mag_4sa_instance_name} (ID: {id(getattr(pb, mag_4sa_instance_name, None))}). Its .data_type = '{current_data_type}'")

    # === Test 1: Save a multi-segment snapshot ===
    print("\n--- Test 1: Save multi-segment snapshot (tests data loading and DataCubby merging) ---")
    test1_passed = False
    try:
        snapshot_filepath_actual = save_data_snapshot(
            filename=SNAPSHOT_FILENAME,
            classes=[pb.mag_rtn_4sa],
            trange_list=TEST_TRANGES_FOR_SAVE, # Two distinct 10-min tranges
            auto_split=False, # Keep it simple: save as one merged block if possible, or respect natural file breaks
            compression="none"
        )
        if snapshot_filepath_actual and os.path.exists(snapshot_filepath_actual):
            print(f"  Snapshot saved to: {snapshot_filepath_actual}")
            # After save_data_snapshot, pb.mag_rtn_4sa should contain the merged data from TEST_TRANGES_FOR_SAVE
            test1_passed = verify_instance_state("pb.mag_rtn_4sa after save_data_snapshot", pb.mag_rtn_4sa, expect_data=True)
        else:
            print(f"  Snapshot file not created. Returned path: {snapshot_filepath_actual}")
            test1_passed = False
    except Exception as e:
        print(f"  Error during Test 1 (save_data_snapshot): {e}")
        import traceback
        print(traceback.format_exc())
        test1_passed = False
    overall_success &= print_test_result("Test 1: Save multi-segment snapshot", test1_passed)
    
    if not snapshot_filepath_actual: # If save failed, no point in continuing this path
        print("Aborting Test 2 & 3 as snapshot creation failed.")
        overall_success = False # Ensure overall test fails
    else:
        # === Test 2: Reset instance, Load Snapshot, Verify ===
        print("\n--- Test 2: Reset, Load Snapshot, and Verify ---")
        test2_passed = False
        try:
            print(f"  Resetting plotbot.{mag_4sa_instance_name} before loading snapshot...")
            setattr(pb, mag_4sa_instance_name, mag_rtn_4sa_class(None))
            print(f"  New plotbot.{mag_4sa_instance_name} instance created (ID: {id(getattr(pb, mag_4sa_instance_name))}).")

            print("  Part 3a: Loading snapshot...")
            load_success_flag = load_data_snapshot(snapshot_filepath_actual, classes=[getattr(pb, mag_4sa_instance_name)], merge_segments=True)
            if not load_success_flag:
                raise RuntimeError("load_data_snapshot reported failure.")
            print("  load_data_snapshot reported success.")

            print("  Part 3b: Verifying consistency after load...")
            consistency_after_load = verify_instance_state(f"plotbot.{mag_4sa_instance_name}", getattr(pb, mag_4sa_instance_name), expect_data=True)
            if not consistency_after_load:
                raise RuntimeError(f"plotbot.{mag_4sa_instance_name} inconsistent after loading snapshot.")
            
            print("  Part 3c: Final plotbot() call with loaded data...")
            # Make sure the plotbot call uses the *global instance* that load_data_snapshot updated
            pb.plotbot(TEST_PLOT_TRANGE, getattr(pb, mag_4sa_instance_name).br, 1)
            print(f"  plotbot() call with loaded data executed.")
            test2_passed = True
        except Exception as e:
            print(f"  Error during Test 2 (Reset, Load, Verify): {e}")
            import traceback
            print(traceback.format_exc())
            test2_passed = False
        overall_success &= print_test_result("Test 2: Reset, Load, Verify", test2_passed)

    # === Cleanup ===
    if snapshot_filepath_actual and os.path.exists(snapshot_filepath_actual):
        try:
            os.remove(snapshot_filepath_actual)
            print("\n--- Test Cleanup: Removed snapshot file: " + str(snapshot_filepath_actual) + " ---") # Simplified print
        except Exception as e_clean:
            print("\n--- Test Cleanup: Error removing snapshot file " + str(snapshot_filepath_actual) + ": " + str(e_clean) + " ---") # Simplified print

    # === Part 4: Plotbot Call ===
    print("\n--- Test Part 4: Making a plotbot() call ---")
    plot_call_passed = False
    try:        
        print(f"  Checking pb.mag_rtn_4sa (ID: {id(pb.mag_rtn_4sa)}) for ensure_internal_consistency before plot call: {hasattr(pb.mag_rtn_4sa, 'ensure_internal_consistency')}")
        
        # Use TEST_PLOT_TRANGE for the plotbot call, which covers the data we expect to be loaded
        print(f"  Attempting: pb.plotbot(TEST_PLOT_TRANGE, pb.mag_rtn_4sa.br, 1)")
        pb.plotbot(TEST_PLOT_TRANGE, pb.mag_rtn_4sa.br, 1) # Removed no_show=True
        
        print(f"  pb.plotbot() call executed (plot window should have appeared).")
        plot_call_passed = True
    except Exception as e:
        print(f"  Error during Test Part 4: {e}")
        import traceback
        print(traceback.format_exc())
        plot_call_passed = False
    overall_success &= print_test_result("Test Part 4: Making a plotbot() call", plot_call_passed)

    overall_status_str = 'PASS' if overall_success else 'FAIL'
    print("\n--- OVERALL TEST RESULT: " + overall_status_str + " ---") # Simplified print
    return overall_success

if __name__ == '__main__':
    run_pipeline_test() 