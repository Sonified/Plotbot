"""
Test Instructions:

Run with:

    pytest -xvs | tee output.log

This will print output to the console and save it to 'output.log'.

This module tests the data merging functionality:
1. Partial overlap merge with snapshots
2. Internal DataCubby._merge_arrays functionality through these operations
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb
from plotbot import print_manager
from plotbot.test_pilot import phase, system_check
from plotbot.data_snapshot import save_data_snapshot, load_data_snapshot
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class

# Import test helpers
from tests.utils import (
    verify_instance_state, 
    verify_data_cubby_state,
    verify_global_tracker_state, 
    reset_and_verify_empty
)

# Test Constants for Partial Overlap Merge
TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE = ['2021-10-26 02:05:00', '2021-10-26 02:15:00'] # Saved to PKL
TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP = ['2021-10-26 02:00:00', '2021-10-26 02:10:00'] # New plotbot call, overlaps 02:05-02:10 from PKL
EXPECTED_MERGED_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:15:00']

# Filename for the test
SNAPSHOT_DIR = "data_snapshots"
TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME = f"{SNAPSHOT_DIR}/test_partial_merge_snapshot_mag_rtn_4sa.pkl"

# Create snapshot directory if needed
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Test Constants for Plotbot Call Merge Test
TRANGE_A = ['2021-10-26 03:00:00', '2021-10-26 03:10:00']
TRANGE_B = ['2021-10-26 03:05:00', '2021-10-26 03:15:00']
TRANGE_C = ['2021-10-26 03:02:00', '2021-10-26 03:08:00'] # Contained within A+B
EXPECTED_MERGED_AB = ['2021-10-26 03:00:00', '2021-10-26 03:15:00']

@pytest.fixture
def mag_4sa_test_instance():
    """Provides a consistently named and reset instance for testing."""
    instance_name = 'mag_rtn_4sa'
    return reset_and_verify_empty(instance_name)

@pytest.fixture(autouse=True)
def setup_test_plots():
    """Ensure plots are closed before and after each test in this file."""
    pb.plt.close('all')
    # Ensure specific print_manager settings for these tests
    print_manager.show_debug = True
    print_manager.show_datacubby = True
    print_manager.show_data_snapshot = True
    print_manager.show_tracker = True
    yield
    pb.plt.close('all')
    # Reset print_manager settings after test
    print_manager.show_debug = False
    print_manager.show_datacubby = False
    print_manager.show_data_snapshot = False
    print_manager.show_tracker = False

@pytest.mark.mission("Core Pipeline: Partial Overlap Merge with Snapshots")
def test_partial_overlap_merge(mag_4sa_test_instance):
    """Tests the data merge logic with a snapshot and a partially overlapping new data request."""
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']

    # --- Step 1: Load initial data range and save snapshot --- 
    phase(1, f"Loading initial data ({TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE}) and saving snapshot")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Partial Overlap Merge - Initial Data"
    
    plot_initial_load_successful = pb.plotbot(TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE, mag_4sa_test_instance.br, 1)
    assert plot_initial_load_successful, "Initial plotbot call for merge test failed."
    
    pre_save_verification_passed = verify_instance_state(
        f"pb.{instance_name} after initial load for merge test", 
        mag_4sa_test_instance, 
        [TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE]
    )
    assert pre_save_verification_passed, "Instance state invalid after initial load for merge test."
    
    # Record data stats before save for later comparison
    initial_datetime_array = mag_4sa_test_instance.datetime_array.copy() if hasattr(mag_4sa_test_instance, 'datetime_array') else None
    initial_data_points = len(initial_datetime_array) if initial_datetime_array is not None else 0
    initial_min_time = np.min(initial_datetime_array) if initial_datetime_array is not None and len(initial_datetime_array) > 0 else None
    initial_max_time = np.max(initial_datetime_array) if initial_datetime_array is not None and len(initial_datetime_array) > 0 else None
    
    save_successful = save_data_snapshot(
        TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME, 
        classes=[mag_4sa_test_instance], 
        auto_split=False
    )
    assert save_successful, f"Failed to save snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} for merge test."
    
    # --- Step 2: Reset state, load snapshot, and request overlapping range --- 
    phase(2, "Resetting instance, loading snapshot, and requesting overlapping range")
    # Reset the instance to simulate starting with fresh state
    reset_and_verify_empty(instance_name)
    current_instance = getattr(pb, instance_name)
    
    # Load the snapshot
    load_successful = load_data_snapshot(
        TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME, 
        classes=[data_type_str]
    )
    assert load_successful, f"Failed to load snapshot {TEST_PARTIAL_MERGE_SNAPSHOT_FILENAME} for merge test."
    
    # Verify instance state after load matches initial state
    post_load_verification_passed = verify_instance_state(
        f"pb.{instance_name} after loading snapshot", 
        current_instance, 
        [TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE]
    )
    assert post_load_verification_passed, "Instance state mismatch after loading snapshot for merge test."
    
    # Capture state after load, before merge
    post_load_datetime_array = current_instance.datetime_array.copy() if hasattr(current_instance, 'datetime_array') else None
    post_load_data_points = len(post_load_datetime_array) if post_load_datetime_array is not None else 0
    
    if initial_data_points > 0 and post_load_data_points > 0:
        assert initial_data_points == post_load_data_points, f"Data point count mismatch after load: {initial_data_points} vs {post_load_data_points}"
        if hasattr(np, 'array_equal') and initial_datetime_array is not None and post_load_datetime_array is not None:
            assert np.array_equal(initial_datetime_array, post_load_datetime_array), "datetime_array mismatch after load"
    
    phase(3, f"Requesting partially overlapping range: {TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP}")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Partial Overlap Merge - After Merge"
    
    # This should trigger a merge, adding data for the non-overlapping portion (02:00-02:05)
    plot_overlap_successful = pb.plotbot(TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP, current_instance.br, 1)
    system_check("Plotbot call for overlapping range", plot_overlap_successful, "Plotting overlapping range should succeed.")
    assert plot_overlap_successful, "Plotbot call for overlapping range failed."

    phase(4, "Verifying merged data state")
    # Merged datetime_array should now cover the combined range
    merged_verification_passed = verify_instance_state(
        f"pb.{instance_name} after merge", 
        current_instance, 
        [EXPECTED_MERGED_TRANGE]
    )
    system_check("Instance state after merge", merged_verification_passed, f"Data should be merged to cover {EXPECTED_MERGED_TRANGE}.")
    assert merged_verification_passed, "Instance state verification failed after merge."
    
    # Additional verification of merge results
    phase(5, "Detailed verification of merge results")
    merged_datetime_array = current_instance.datetime_array if hasattr(current_instance, 'datetime_array') else None
    merged_data_points = len(merged_datetime_array) if merged_datetime_array is not None else 0
    
    # The merged data should have more points than either the initial or post-load data
    if merged_data_points > 0 and post_load_data_points > 0:
        system_check("Merged data points increased", merged_data_points > post_load_data_points, 
                    f"Merged data should have more points than before ({merged_data_points} vs {post_load_data_points}).")
    
    # Verify merged time range contains both input ranges
    if merged_datetime_array is not None and len(merged_datetime_array) > 0:
        merged_min_time = np.min(merged_datetime_array)
        merged_max_time = np.max(merged_datetime_array)
        
        # Convert expected boundaries to datetime64 for comparison
        expected_min_time = pd.to_datetime(TEST_TRANGE_FOR_PARTIAL_MERGE_LOAD_OVERLAP[0]).to_datetime64()
        expected_max_time = pd.to_datetime(TEST_TRANGE_FOR_PARTIAL_MERGE_SAVE[1]).to_datetime64()
        
        system_check("Merged min time correct", merged_min_time <= expected_min_time + pd.Timedelta(seconds=1), 
                    f"Merged min time ({merged_min_time}) should be near expected ({expected_min_time}).")
        system_check("Merged max time correct", merged_max_time >= expected_max_time - pd.Timedelta(seconds=1), 
                    f"Merged max time ({merged_max_time}) should be near expected ({expected_max_time}).")
    
    # Final check of DataCubby and Global Tracker state
    cubby_passed, cubby_issues = verify_data_cubby_state(
        current_instance,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("DataCubby state post-merge", cubby_passed, 
                f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
    
    tracker_passed, tracker_issues = verify_global_tracker_state(
        current_instance,
        EXPECTED_MERGED_TRANGE,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("Global Tracker state post-merge", tracker_passed, 
                f"Global Tracker state should be correct. {'Issues: ' + '; '.join(tracker_issues) if not tracker_passed else ''}")

@pytest.mark.mission("Core Pipeline: Plotbot Call Merging")
def test_plotbot_calls_with_overlapping_time_ranges(mag_4sa_test_instance):
    """Tests data merging through sequential plotbot() calls with overlapping time ranges."""
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']
    current_instance = mag_4sa_test_instance # Use the fixture directly

    phase(1, f"First plotbot call for TRANGE_A: {TRANGE_A}")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Plotbot Merge Test - Call A"
    plot_a_successful = pb.plotbot(TRANGE_A, current_instance.br, 1)
    system_check(f"Plotbot call for {TRANGE_A}", plot_a_successful, "Initial plotbot call should succeed.")
    assert plot_a_successful, f"Plotbot call for TRANGE_A ({TRANGE_A}) failed."
    verify_instance_state(f"pb.{instance_name} after TRANGE_A", current_instance, [TRANGE_A])
    pb.plt.close('all')

    # Capture data points after first call for comparison later
    points_after_a = len(current_instance.datetime_array) if hasattr(current_instance, 'datetime_array') else 0

    phase(2, f"Second plotbot call for TRANGE_B (overlapping): {TRANGE_B}")
    pb.plt.options.single_title_text = "Plotbot Merge Test - Call B (Overlapping)"
    plot_b_successful = pb.plotbot(TRANGE_B, current_instance.br, 1)
    system_check(f"Plotbot call for {TRANGE_B}", plot_b_successful, "Second (overlapping) plotbot call should succeed.")
    assert plot_b_successful, f"Plotbot call for TRANGE_B ({TRANGE_B}) failed."
    verify_instance_state(f"pb.{instance_name} after TRANGE_B (merged A+B)", current_instance, [EXPECTED_MERGED_AB])
    pb.plt.close('all')

    points_after_b = len(current_instance.datetime_array) if hasattr(current_instance, 'datetime_array') else 0
    system_check("Data points after TRANGE_B merge", points_after_b > points_after_a if points_after_a > 0 else True,
                 f"Expected more data points after merge (A: {points_after_a}, A+B: {points_after_b}). This check assumes TRANGE_B adds new data.")
    # Note: A strict check points_after_b > points_after_a might fail if TRANGE_B is fully contained in TRANGE_A after some internal optimization.
    # The verify_instance_state for EXPECTED_MERGED_AB is the more robust check for correct range coverage.

    phase(3, f"Third plotbot call for TRANGE_C (contained): {TRANGE_C}")
    pb.plt.options.single_title_text = "Plotbot Merge Test - Call C (Contained)"
    plot_c_successful = pb.plotbot(TRANGE_C, current_instance.br, 1)
    system_check(f"Plotbot call for {TRANGE_C}", plot_c_successful, "Third (contained) plotbot call should succeed.")
    assert plot_c_successful, f"Plotbot call for TRANGE_C ({TRANGE_C}) failed."
    
    # State should still reflect the larger merged range from A+B
    verify_instance_state(f"pb.{instance_name} after TRANGE_C (still merged A+B)", current_instance, [EXPECTED_MERGED_AB])
    points_after_c = len(current_instance.datetime_array) if hasattr(current_instance, 'datetime_array') else 0
    system_check("Data points after TRANGE_C (contained call)", points_after_c == points_after_b,
                 f"Expected same number of data points as after A+B merge (A+B: {points_after_b}, A+B+C: {points_after_c}).")
    assert points_after_c == points_after_b, "Data points changed after contained call, indicating unexpected re-processing or data loss."

    # Final checks for DataCubby and Global Tracker after all merges
    cubby_passed, cubby_issues = verify_data_cubby_state(
        current_instance,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("DataCubby state post all plotbot merges", cubby_passed, 
                f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
    assert cubby_passed, "DataCubby state verification failed after plotbot merges."

    tracker_passed, tracker_issues = verify_global_tracker_state(
        current_instance,
        EXPECTED_MERGED_AB, # The tracker should reflect the fully merged range
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("Global Tracker state post all plotbot merges", tracker_passed, 
                f"Global Tracker state should be correct. {'Issues: ' + '; '.join(tracker_issues) if not tracker_passed else ''}")
    assert tracker_passed, "Global Tracker state verification failed after plotbot merges."

    # If all assertions passed, show the final plot
    pb.plt.options.single_title_text = "Plotbot Merge Test - Final Result (A+B+C)"
    # Re-plot the final state to visualize
    pb.plotbot(EXPECTED_MERGED_AB, current_instance.br, 1) 
    pb.plt.show()

@pytest.mark.mission("Core Pipeline: Direct _merge_arrays Test")
def test_merge_arrays_directly():
    """Tests DataCubby._merge_arrays functionality directly if available."""
    # Skip if DataCubby._merge_arrays can't be accessed
    if not hasattr(pb, 'data_cubby') or not hasattr(pb.data_cubby, '_merge_arrays'):
        pytest.skip("data_cubby._merge_arrays is not accessible")
    
    phase(1, "Creating test data for direct merge test")
    # Create two overlapping time arrays
    time1_start = pd.to_datetime('2021-10-26 02:05:00')
    time1_end = pd.to_datetime('2021-10-26 02:15:00')
    time1 = pd.date_range(time1_start, time1_end, periods=100).to_numpy()
    
    time2_start = pd.to_datetime('2021-10-26 02:00:00')
    time2_end = pd.to_datetime('2021-10-26 02:10:00') 
    time2 = pd.date_range(time2_start, time2_end, periods=100).to_numpy()
    
    # Create sample data for each time array
    raw_data1 = {
        'br': np.random.rand(100),
        'bt': np.random.rand(100),
        'bn': np.random.rand(100),
        'all': np.stack([np.random.rand(100), np.random.rand(100), np.random.rand(100)])
    }
    
    raw_data2 = {
        'br': np.random.rand(100),
        'bt': np.random.rand(100),
        'bn': np.random.rand(100),
        'all': np.stack([np.random.rand(100), np.random.rand(100), np.random.rand(100)])
    }
    
    phase(2, "Calling _merge_arrays directly")
    # Call _merge_arrays directly
    merged_times, merged_raw_data = pb.data_cubby._merge_arrays(time1, raw_data1, time2, raw_data2)
    
    phase(3, "Verifying merge results")
    # Verify merged results
    assert merged_times is not None, "_merge_arrays returned None for times"
    assert merged_raw_data is not None, "_merge_arrays returned None for raw_data"
    
    # Ensure the merged array is sorted and has no duplicates
    is_sorted = np.all(merged_times[:-1] <= merged_times[1:])
    system_check("Merged times are sorted", is_sorted, "Merged datetime array should be sorted.")
    
    is_unique = len(np.unique(merged_times)) == len(merged_times)
    system_check("Merged times are unique", is_unique, "Merged datetime array should have no duplicates.")
    
    # Verify merged time range contains both input ranges
    min_time = np.min(merged_times)
    max_time = np.max(merged_times)
    
    min_time_correct = min_time <= np.min(time2)
    max_time_correct = max_time >= np.max(time1)
    
    system_check("Merged min time correct", min_time_correct, 
                f"Merged min time ({min_time}) should be <= min of time2 ({np.min(time2)}).")
    system_check("Merged max time correct", max_time_correct, 
                f"Merged max time ({max_time}) should be >= max of time1 ({np.max(time1)}).")
    
    # Verify merged data contains all expected components
    for component in ['br', 'bt', 'bn', 'all']:
        assert component in merged_raw_data, f"Component {component} missing from merged_raw_data"
        component_array = merged_raw_data[component]
        if component == 'all':
            # 'all' from _merge_arrays might be a list of arrays
            assert isinstance(component_array, list), f"'all' component should be a list, got {type(component_array)}"
            assert len(component_array) > 0, "'all' component list is empty"
            # Check the shape of the first element (assuming all elements have the same shape post-merge for time dimension)
            # And that this shape corresponds to the number of merged time points
            first_component_in_all = component_array[0]
            assert hasattr(first_component_in_all, 'shape'), "Element in 'all' component list has no shape attribute"
            assert len(first_component_in_all) == len(merged_times), f"'all' component element length mismatch: {len(first_component_in_all)} vs {len(merged_times)}"
        else:
            assert hasattr(component_array, 'shape'), f"Component {component} has no shape attribute"
            assert len(component_array) == len(merged_times), f"Component {component} length mismatch: {len(component_array)} vs {len(merged_times)}"

if __name__ == "__main__":
    import os
    os.makedirs("tests/core/logs", exist_ok=True)
    pytest.main(["-xvs", __file__, "--log-file=tests/core/logs/test_data_merging.txt"]) 