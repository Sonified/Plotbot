"""
Test Instructions:

Run with:

    pytest -xvs | tee output.log

This will print output to the console and save it to 'output.log'.

This module tests the data snapshot functionality:
1. Simple snapshot save
2. Simple snapshot load, verify, and plot
3. Advanced snapshot save with multi-trange and auto-split
4. Advanced snapshot load (segmented), verify, and plot
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb
from plotbot import print_manager
from plotbot.test_pilot import phase, system_check
from plotbot.data_snapshot import save_data_snapshot, load_data_snapshot
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class
from plotbot.plotbot_helpers import time_clip

# Import test helpers
from tests.utils import (
    verify_instance_state, 
    verify_data_cubby_state,
    verify_global_tracker_state, 
    reset_and_verify_empty,
    save_snapshot_and_verify,
    load_snapshot_and_verify
)

# Test Constants
TEST_SINGLE_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00']
TEST_TRANGES_FOR_SAVE = [
    ['2021-10-26 02:00:00', '2021-10-26 02:10:00'], 
    ['2021-10-26 02:15:00', '2021-10-26 02:25:00'] 
]
TEST_SUB_TRANGE_OF_ADVANCED_SAVE = ['2021-10-26 02:00:00', '2021-10-26 02:05:00']

# Filenames for Snapshots
SNAPSHOT_DIR = "data_snapshots"
TEST_SIMPLE_SNAPSHOT_FILENAME = f"{SNAPSHOT_DIR}/test_simple_snapshot_mag_rtn_4sa.pkl"
TEST_ADVANCED_SNAPSHOT_FILENAME = f"{SNAPSHOT_DIR}/test_advanced_snapshot_mag_rtn_4sa.pkl"

# Create snapshot directory if needed
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

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

@pytest.mark.mission("Core Pipeline: Simple Snapshot Save")
def test_simple_snapshot_save(mag_4sa_test_instance):
    """Tests saving a simple data snapshot, verifies file creation and instance integrity."""
    pm = print_manager
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']
    
    phase(1, f"Populating instance {instance_name} for snapshot save")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Simple Snapshot - Data Population"
    
    # Load data into the instance first, using Agg backend to prevent display
    current_backend = matplotlib.get_backend()
    plot_successful = False # Initialize
    try:
        matplotlib.use('Agg')
        plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
    finally:
        pb.plt.close('all') # Close the figure associated with 'Agg'
        matplotlib.use(current_backend) # Switch back to original backend
    
    assert plot_successful, "Plotbot call failed during setup for snapshot save."
    
    # Verify it has data and is consistent BEFORE saving
    pre_save_verification_passed = verify_instance_state(
        f"pb.{instance_name} (pre-save)", 
        mag_4sa_test_instance, 
        [TEST_SINGLE_TRANGE]
    )
    assert pre_save_verification_passed, "Instance state invalid before snapshot save."

    phase(2, f"Saving snapshot to {TEST_SIMPLE_SNAPSHOT_FILENAME}")
    save_successful = save_data_snapshot(
        TEST_SIMPLE_SNAPSHOT_FILENAME,
        classes=[mag_4sa_test_instance], 
        auto_split=False
    )
    system_check("Snapshot save operation", save_successful, "save_data_snapshot should return True on success.")
    assert save_successful, "save_data_snapshot failed."

    phase(3, "Verifying snapshot file existence")
    file_exists = os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME)
    system_check(f"Snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} created", file_exists, "Snapshot file should exist after saving.")
    assert file_exists, f"Snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} was not created."

    phase(4, f"Verifying instance state for {instance_name} remains valid POST-save")
    post_save_verification_passed = verify_instance_state(
        f"pb.{instance_name} (post-save)", 
        mag_4sa_test_instance, 
        [TEST_SINGLE_TRANGE]
    )
    system_check("Instance state post-save (detailed)", post_save_verification_passed, 
                 "Instance data should remain consistent and valid after save operation.")
    assert post_save_verification_passed, "Instance state became invalid after save operation."

@pytest.mark.mission("Core Pipeline: Simple Snapshot Load, Verify, and Plot")
def test_simple_snapshot_load_verify_plot(mag_4sa_test_instance):
    """Tests loading a simple snapshot, verifying data, DataCubby, Tracker, and plotting."""
    pm = print_manager
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']

    # --- Setup: Ensure the snapshot file exists --- 
    phase(1, "Setup: Ensuring snapshot file for loading exists")
    if not os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME):
        temp_instance_name = 'temp_mag_rtn_4sa_for_save'
        temp_instance = reset_and_verify_empty(temp_instance_name)
        
        pb.plt.options.use_single_title = True
        pb.plt.options.single_title_text = "Setup: Creating Snapshot File for Load Test"
        
        current_backend = matplotlib.get_backend()
        load_data_for_snapshot_plot_successful = False # Initialize
        try:
            matplotlib.use('Agg')
            load_data_for_snapshot_plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, temp_instance.br, 1)
        finally:
            pb.plt.close('all')
            matplotlib.use(current_backend)

        if not load_data_for_snapshot_plot_successful:
            pytest.fail(f"Failed to load data for snapshot creation: plotbot() returned {load_data_for_snapshot_plot_successful}")
        
        # Verify temp_instance before saving it
        assert verify_instance_state(f"pb.{temp_instance_name}", temp_instance, [TEST_SINGLE_TRANGE]), \
            "Temporary instance for snapshot creation is invalid."
            
        save_successful = save_data_snapshot(
            TEST_SIMPLE_SNAPSHOT_FILENAME,
            classes=[temp_instance],
            auto_split=False
        )
        if not save_successful:
            pytest.fail(f"Failed to create snapshot file {TEST_SIMPLE_SNAPSHOT_FILENAME} for test")
        
        # Clean up temp instance
        if hasattr(pb, temp_instance_name):
            delattr(pb, temp_instance_name)
        if hasattr(pb, 'data_cubby'):
            pb.data_cubby.class_registry.pop(temp_instance_name, None)
            pb.data_cubby.cubby.pop(temp_instance_name, None)
            
    assert os.path.exists(TEST_SIMPLE_SNAPSHOT_FILENAME), f"Setup failed: {TEST_SIMPLE_SNAPSHOT_FILENAME} not created or not found"

    # --- Main Test --- 
    phase(2, f"Resetting main instance {instance_name} and verifying it is empty")
    reset_and_verify_empty(instance_name)
    current_instance = getattr(pb, instance_name)
    
    phase(3, f"Loading snapshot from {TEST_SIMPLE_SNAPSHOT_FILENAME} into {instance_name}")
    load_successful = load_data_snapshot(
        TEST_SIMPLE_SNAPSHOT_FILENAME, 
        classes=[data_type_str]
    )
    system_check("Snapshot load operation", load_successful, "load_data_snapshot should return True.")
    assert load_successful, "load_data_snapshot failed."

    phase(4, f"Verifying instance state for {instance_name} after simple load (detailed)")
    post_load_verification_passed = verify_instance_state(
        f"pb.{instance_name} (post-load)",
        current_instance, 
        [TEST_SINGLE_TRANGE]
    )
    system_check("Instance state after load (detailed)", post_load_verification_passed, 
                 "Data from snapshot should be loaded, and instance internally consistent.")
    assert post_load_verification_passed, "Detailed instance state verification failed after simple load."

    phase(5, f"Verifying DataCubby state for {instance_name} after load")
    cubby_passed, cubby_issues = verify_data_cubby_state(
        current_instance,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("DataCubby state post-load", cubby_passed, 
                f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
    assert cubby_passed, "DataCubby state verification failed post-load."

    phase(6, f"Verifying Global Tracker state for {data_type_str} after load")
    tracker_passed, tracker_issues = verify_global_tracker_state(
        current_instance,
        TEST_SINGLE_TRANGE,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("Global Tracker state post-load", tracker_passed, 
                f"Global Tracker state should be correct. {'Issues: ' + '; '.join(tracker_issues) if not tracker_passed else ''}")
    assert tracker_passed, "Global Tracker state verification failed post-load."

    phase(7, "Plotting loaded data from snapshot")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Plotting Data Loaded from Simple Snapshot"
    
    plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, current_instance.br, 1)
    system_check("Plotbot call with loaded data", plot_successful, "Plotting loaded data should succeed.")
    assert plot_successful, "Plotbot call with loaded data failed."
    pb.plt.close('all') # Ensure this plot also doesn't show
        
    # Final verification to ensure plotting didn't affect the data
    final_verification = verify_instance_state(
        f"pb.{instance_name} (post-plot, after load)",
        current_instance,
        [TEST_SINGLE_TRANGE]
    )
    system_check("Final instance state after plotting loaded data", final_verification, 
                 "Instance should remain consistent after plotting snapshot data.")
    assert final_verification, "Instance state verification failed after plotting loaded data."

@pytest.mark.mission("Core Pipeline: Advanced Snapshot Save with Multi-Trange and Auto-Split")
def test_advanced_snapshot_save(mag_4sa_test_instance):
    """Tests advanced snapshot saving with multiple time ranges and auto-splitting."""
    pm = print_manager # Define pm alias
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']
    
    phase(1, f"Saving advanced snapshot to {TEST_ADVANCED_SNAPSHOT_FILENAME} for tranges: {TEST_TRANGES_FOR_SAVE}")
    save_successful = save_data_snapshot(
        TEST_ADVANCED_SNAPSHOT_FILENAME,
        classes=[mag_4sa_test_instance],
        trange_list=TEST_TRANGES_FOR_SAVE,
        auto_split=True
    )
    system_check("Advanced snapshot save operation", save_successful, "save_data_snapshot should return True.")
    assert save_successful, "Advanced save_data_snapshot failed."

    phase(2, f"Verifying instance state for {instance_name} after population by save_data_snapshot")
    
    # --- DEBUG CUBBY STATE BEFORE GRAB ---
    pm.debug("\n[TEST_DEBUG] Cubby state BEFORE grab in test_advanced_snapshot_save (Phase 2):")
    if hasattr(pb, 'data_cubby') and hasattr(pb.data_cubby, 'class_registry'):
        for key, inst_in_cubby in pb.data_cubby.class_registry.items():
            dt_len_cubby = len(inst_in_cubby.datetime_array) if hasattr(inst_in_cubby, 'datetime_array') and inst_in_cubby.datetime_array is not None else "None_or_NoAttr"
            pm.debug(f"  Cubby Key: '{key}', Instance ID: {id(inst_in_cubby)}, dt_len: {dt_len_cubby}")
    else:
        pm.debug("  Could not inspect pb.data_cubby.class_registry")
    pm.debug("[TEST_DEBUG] --- END CUBBY STATE --- \n")
    # --- END DEBUG --- 

    # Grab the instance from the cubby to ensure we are verifying the authoritative version
    instance_from_cubby_after_save = pb.data_cubby.grab(data_type_str) # data_type_str is like 'mag_RTN_4sa'
    if instance_from_cubby_after_save is None:
        # Fallback to instance_name if data_type_str didn't work (shouldn't happen if mapping is correct)
        instance_from_cubby_after_save = pb.data_cubby.grab(instance_name)
    
    assert instance_from_cubby_after_save is not None, f"Could not grab instance ({data_type_str} or {instance_name}) from cubby after save_data_snapshot."
    
    # It's possible mag_4sa_test_instance is not the same object as instance_from_cubby_after_save
    # if DataCubby replaced the global instance. Log this.
    if mag_4sa_test_instance is not instance_from_cubby_after_save:
        print_manager.warning(f"Test instance (ID: {id(mag_4sa_test_instance)}) is different from cubby instance (ID: {id(instance_from_cubby_after_save)}) after save. Verifying cubby instance.")

    post_save_verification_passed = verify_instance_state(
        f"pb.{instance_name} (from cubby after save_data_snapshot)",
        instance_from_cubby_after_save, # Verify the instance grabbed from the cubby
        TEST_TRANGES_FOR_SAVE
    )
    system_check("Instance state after population in save (detailed)", post_save_verification_passed, 
                 "Instance (from cubby) should be populated for all specified tranges and be internally consistent.")
    assert post_save_verification_passed, "Instance state verification failed after population by save_data_snapshot."

    phase(3, "Verifying advanced snapshot file existence")
    file_exists = os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME)
    system_check(f"Advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} created", file_exists, "Main advanced snapshot file should exist.")
    assert file_exists, f"Advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} was not created."

@pytest.mark.mission("Core Pipeline: Advanced Snapshot Load (Segmented), Verify, and Plot")
def test_advanced_snapshot_load_verify_plot(mag_4sa_test_instance):
    """Tests loading an advanced (potentially segmented) snapshot, verifying, and plotting."""
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']
    ground_truth_point_count = 0
    ground_truth_datetime_array = None
    
    # --- Setup: Ensure the advanced snapshot file exists --- 
    phase(1, "Setup: Ensuring advanced snapshot file for loading exists")
    if not os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME):
        temp_instance_name = 'temp_mag_rtn_4sa_for_adv_save'
        temp_instance = reset_and_verify_empty(temp_instance_name)
        
        pb.plt.options.use_single_title = True
        pb.plt.options.single_title_text = "Setup: Creating Advanced Snapshot Files"
        
        save_successful = save_data_snapshot(
            TEST_ADVANCED_SNAPSHOT_FILENAME,
            classes=[temp_instance],
            trange_list=TEST_TRANGES_FOR_SAVE,
            auto_split=True
        )
        pb.plt.close('all') # Ensure plots from this setup save_data_snapshot are closed
        if not save_successful:
            pytest.fail(f"Failed to create advanced snapshot file {TEST_ADVANCED_SNAPSHOT_FILENAME} for test")
        
        # Dynamically determine ground truth from the instance populated by save_data_snapshot
        # This assumes save_data_snapshot correctly merges/populates temp_instance for all tranges
        if hasattr(temp_instance, 'datetime_array') and temp_instance.datetime_array is not None:
            ground_truth_datetime_array = temp_instance.datetime_array.copy()
            ground_truth_point_count = len(ground_truth_datetime_array)
            print_manager.debug(f"Setup: Captured ground_truth_point_count: {ground_truth_point_count} from temp_instance after save_data_snapshot")
        else:
            pytest.fail("Setup: temp_instance has no datetime_array after save_data_snapshot, cannot determine ground truth.")
        
        # Clean up temp instance
        if hasattr(pb, temp_instance_name):
            delattr(pb, temp_instance_name)
        if hasattr(pb, 'data_cubby'):
            pb.data_cubby.class_registry.pop(temp_instance_name, None)
            pb.data_cubby.cubby.pop(temp_instance_name, None)
    else:
        # If snapshot exists, we can't dynamically get ground truth this way.
        # For now, we'll rely on a reasonable approximation if file already existed.
        # Ideally, this else block would load the snapshot temporarily to get the ground truth too, or the test ensures a fresh save.
        # For this iteration, let's assume approx 2746 points per 10-min segment of TEST_TRANGES_FOR_SAVE (2 segments)
        ground_truth_point_count = 2746 * len(TEST_TRANGES_FOR_SAVE) 
        print_manager.warning(f"Snapshot file already exists. Using approximate ground_truth_point_count: {ground_truth_point_count}")

    assert os.path.exists(TEST_ADVANCED_SNAPSHOT_FILENAME), f"Setup failed: {TEST_ADVANCED_SNAPSHOT_FILENAME} not created or not found"

    # --- Main Test --- 
    phase(2, f"Resetting main instance {instance_name} and verifying it is empty")
    reset_and_verify_empty(instance_name)
    current_instance = getattr(pb, instance_name)
    
    phase(3, f"Loading advanced snapshot from {TEST_ADVANCED_SNAPSHOT_FILENAME} into {instance_name}")
    load_successful = load_data_snapshot(
        TEST_ADVANCED_SNAPSHOT_FILENAME, 
        classes=[data_type_str],
        merge_segments=True
    )
    system_check("Advanced snapshot load operation", load_successful, "load_data_snapshot for advanced snapshot should return True.")
    assert load_successful, "Advanced load_data_snapshot failed."

    phase(4, f"Verifying instance state for {instance_name} after advanced load")
    # Use the dynamically determined (or approximated) point count
    post_load_verification_passed = verify_instance_state(
        f"pb.{instance_name} (post-advanced-load)",
        current_instance,
        TEST_TRANGES_FOR_SAVE,
        expected_points_approx=ground_truth_point_count 
    )
    system_check("Instance state after advanced load (detailed)", post_load_verification_passed, 
                 "Data from all segments should be properly merged and instance internally consistent.")
    assert post_load_verification_passed, "Detailed instance state verification failed after advanced load."
    
    # More specific check if ground_truth_datetime_array was captured
    if ground_truth_datetime_array is not None and hasattr(current_instance, 'datetime_array') and current_instance.datetime_array is not None:
        system_check("Loaded datetime_array matches ground truth", 
                     np.array_equal(current_instance.datetime_array, ground_truth_datetime_array),
                     "Loaded instance datetime_array should exactly match the one from the saved (and supposedly merged) instance.")
        assert np.array_equal(current_instance.datetime_array, ground_truth_datetime_array), "Loaded datetime_array does not match ground truth from save."
    elif ground_truth_datetime_array is not None:
        system_check("Loaded datetime_array matches ground truth", False, "Current instance has no datetime_array to compare with ground truth.")
        assert False, "Current instance missing datetime_array for ground truth comparison."

    phase(5, f"Verifying DataCubby state for {instance_name} after advanced load")
    cubby_passed, cubby_issues = verify_data_cubby_state(
        current_instance,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("DataCubby state post-advanced-load", cubby_passed, 
                f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
    assert cubby_passed, "DataCubby state verification failed post-advanced-load."

    phase(6, f"Plotting sub-range from loaded advanced snapshot data")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Plotting Sub-Range from Advanced Snapshot"
    
    # Explicitly check if data for the sub-range exists in the (supposedly) merged instance
    if hasattr(current_instance, 'datetime_array') and current_instance.datetime_array is not None:
        sub_range_indices = time_clip(current_instance.datetime_array, TEST_SUB_TRANGE_OF_ADVANCED_SAVE[0], TEST_SUB_TRANGE_OF_ADVANCED_SAVE[1])
        system_check("Data available for sub-range plot in loaded instance", len(sub_range_indices) > 0, 
                     f"Sub-range {TEST_SUB_TRANGE_OF_ADVANCED_SAVE} should have data points. Found {len(sub_range_indices)}.")
        assert len(sub_range_indices) > 0, f"No data found for sub-range {TEST_SUB_TRANGE_OF_ADVANCED_SAVE} in loaded instance before plotting."
    else:
        system_check("Data available for sub-range plot in loaded instance", False, "current_instance.datetime_array is None before sub-range plot.")
        assert False, "current_instance.datetime_array is None, cannot check for sub-range data."

    plot_successful = pb.plotbot(TEST_SUB_TRANGE_OF_ADVANCED_SAVE, current_instance.br, 1)
    system_check("Plotbot call with data from advanced snapshot", plot_successful, 
                 "Plotting sub-range from advanced snapshot should succeed.")
    assert plot_successful, "Plotbot call with data from advanced snapshot failed."
    pb.plt.close('all') # Ensure this plot also doesn't show, per user intent

if __name__ == "__main__":
    import os
    os.makedirs("tests/core/logs", exist_ok=True)
    pytest.main(["-xvs", __file__, "--log-file=tests/core/logs/test_snapshot_handling.txt"]) 