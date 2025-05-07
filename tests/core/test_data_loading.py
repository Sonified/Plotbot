"""
Test Instructions:

Run with:

    pytest -xvs | tee output.log

This will print output to the console and save it to 'output.log'.

This module tests the core data loading functionality:
1. Initial data load via plotbot()
2. Cached data retrieval for the same time range
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
import time as pytime

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb
from plotbot import print_manager
from plotbot.test_pilot import phase, system_check
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class

# Import test helpers
from tests.utils import (
    verify_instance_state, 
    verify_data_cubby_state,
    verify_global_tracker_state, 
    reset_and_verify_empty
)

# Test Constants
TEST_SINGLE_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00']

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
    if hasattr(pb, 'global_tracker') and hasattr(pb.global_tracker, 'calculated_ranges'):
        pb.global_tracker.calculated_ranges.clear() # Reset tracker for each test
    yield
    pb.plt.close('all')
    # Reset print_manager settings after test
    print_manager.show_debug = False
    print_manager.show_datacubby = False
    print_manager.show_data_snapshot = False
    print_manager.show_tracker = False

@pytest.mark.skip(reason="Skipping as per Robert's request to focus on other tests.")
@pytest.mark.mission("Core Pipeline: Initial Data Load and Plot")
def test_initial_data_load(mag_4sa_test_instance):
    """Tests the initial data load via plotbot() and verifies instance state and DataCubby."""
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']

    phase(1, "Setting plot options for initial load")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Initial Data Load and Plot"

    phase(2, f"Calling plotbot for {TEST_SINGLE_TRANGE} with {instance_name}.br on panel 1")
    plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
    system_check("Plotbot call successful", plot_successful, "plotbot() should return True on success.")
    assert plot_successful, "Plotbot call for initial load failed."

    phase(3, f"Verifying instance state for pb.{instance_name} after initial load")
    verification_passed = verify_instance_state(
        f"pb.{instance_name}",
        mag_4sa_test_instance,
        [TEST_SINGLE_TRANGE]
    )
    system_check("Instance state verification (detailed)", verification_passed, 
                 "Instance data should be loaded and internally consistent.")
    assert verification_passed, "Detailed instance state verification failed after initial load."

    phase(4, f"Verifying DataCubby state for {instance_name}")
    cubby_passed, cubby_issues = verify_data_cubby_state(
        mag_4sa_test_instance,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("DataCubby state verification", cubby_passed, 
                f"DataCubby state should be correct. {'Issues: ' + '; '.join(cubby_issues) if not cubby_passed else ''}")
    assert cubby_passed, "DataCubby state verification failed."

    phase(5, f"Verifying Global Tracker state for {instance_name}")
    tracker_passed, tracker_issues = verify_global_tracker_state(
        mag_4sa_test_instance,
        TEST_SINGLE_TRANGE,
        instance_name=instance_name,
        data_type_str=data_type_str
    )
    system_check("Global Tracker state verification", tracker_passed, 
                f"Global Tracker state should be correct. {'Issues: ' + '; '.join(tracker_issues) if not tracker_passed else ''}")
    assert tracker_passed, "Global Tracker state verification failed."

@pytest.mark.skip(reason="Skipping as per Robert's request to focus on other tests.")
@pytest.mark.mission("Core Pipeline: Cached Data Retrieval and Plot")
def test_cached_data_retrieval(mag_4sa_test_instance):
    """Tests that a second plotbot() call for the same data uses cached data and instance remains valid."""
    instance_name = mag_4sa_test_instance.class_name
    data_type_str = pb.CLASS_NAME_MAPPING[instance_name]['data_type']

    phase(1, "Setting plot options for cached data test")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Cached Data Retrieval - Initial Load" # Indicate this is the setup plot

    phase(2, f"First plotbot call to populate cache for {TEST_SINGLE_TRANGE} with {instance_name}.br")
    initial_plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1) 
    assert initial_plot_successful, "Initial plotbot call failed in cached data test setup."
    
    # Record state after initial load
    initial_verification_passed = verify_instance_state(
        f"pb.{instance_name} after initial load for cache test",
        mag_4sa_test_instance,
        [TEST_SINGLE_TRANGE]
    )
    assert initial_verification_passed, "Instance state verification failed after initial load in cache test."
    
    # Close the plot from the first call so it's not displayed
    pb.plt.close('all') 

    # Capture state of Global Tracker and DataCubby object ID before second call to compare later
    initial_ranges = []
    cubby_obj_id = None
    if hasattr(pb, 'global_tracker') and hasattr(pb.global_tracker, 'calculated_ranges'):
        if data_type_str in pb.global_tracker.calculated_ranges:
            initial_ranges = pb.global_tracker.calculated_ranges[data_type_str].copy()
    if hasattr(pb, 'data_cubby'):
        cubby_instance = pb.data_cubby.class_registry.get(data_type_str, None) # Use data_type_str for consistency
        if cubby_instance is not None: # Ensure instance exists before getting id
             cubby_obj_id = id(cubby_instance)

    phase(3, f"Second plotbot call (should use cache) for {TEST_SINGLE_TRANGE} with {instance_name}.br")
    # Update title for the cached plot that might be shown
    pb.plt.options.single_title_text = "Cached Data Retrieval - Verified Cached Plot" 
    cached_plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 1)
    system_check("Cached plotbot call successful", cached_plot_successful, "plotbot() using cache should return True.")
    assert cached_plot_successful, "Cached plotbot call failed."

    phase(4, f"Verifying instance state for {instance_name} remains consistent after cached call")
    cached_verification_passed = verify_instance_state(
        f"pb.{instance_name} after cached call",
        mag_4sa_test_instance,
        [TEST_SINGLE_TRANGE]
    )
    system_check("Instance state verification after cached call", cached_verification_passed, 
                 "Instance data should remain consistent after cached call.")
    assert cached_verification_passed, "Instance state verification failed after cached call."
    
    phase(5, "Verifying cache was used (no redundant processing)")
    cache_was_used = True
    cache_issues = []
    
    # Check Global Tracker wasn't modified by second call (same ranges)
    if hasattr(pb, 'global_tracker') and hasattr(pb.global_tracker, 'calculated_ranges'):
        current_ranges = []
        if data_type_str in pb.global_tracker.calculated_ranges:
            current_ranges = pb.global_tracker.calculated_ranges[data_type_str]
        
        if len(current_ranges) != len(initial_ranges):
            cache_was_used = False
            cache_issues.append(f"Tracker ranges count changed: initial {len(initial_ranges)}, current {len(current_ranges)} (expected same).")
        elif initial_ranges and current_ranges and not all(sr == cr for sr, cr in zip(initial_ranges, current_ranges)):
            cache_was_used = False
            cache_issues.append(f"Tracker ranges content changed. Initial: {initial_ranges}, Current: {current_ranges}")

    # Verify cubby object identity didn't change
    if hasattr(pb, 'data_cubby') and cubby_obj_id is not None:
        current_cubby_instance = pb.data_cubby.class_registry.get(data_type_str, None)
        current_obj_id = id(current_cubby_instance) if current_cubby_instance is not None else None
        if current_obj_id != cubby_obj_id:
            cache_was_used = False
            cache_issues.append(f"DataCubby object ID changed: initial {cubby_obj_id}, current {current_obj_id} (expected same).")
    elif hasattr(pb, 'data_cubby') and cubby_obj_id is None and pb.data_cubby.class_registry.get(data_type_str, None) is not None:
        cache_was_used = False
        cache_issues.append(f"DataCubby object was initially None but now exists (unexpected recreation).")

    system_check("Cache was used (tracker and cubby state consistent)", cache_was_used, 
                f"Second call should use cached data. {'Issues: ' + '; '.join(cache_issues) if not cache_was_used else 'No redundant processing detected.'}")
    assert cache_was_used, "Cache use verification failed. Issues: " + '; '.join(cache_issues)

    # If all assertions passed, show the plot from the second (cached) call
    pb.plt.show()

if __name__ == "__main__":
    import os
    os.makedirs("tests/core/logs", exist_ok=True)
    pytest.main(["-xvs", __file__, "--log-file=tests/core/logs/test_data_loading.txt"]) 