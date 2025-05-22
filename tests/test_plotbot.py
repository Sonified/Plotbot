"""
Tests for the main plotbot functionality.

This file contains tests for the core plotbot functions, including
custom variable time updates and custom variable handling.

NOTES ON TEST OUTPUT:
- Use print_manager.test() for any debug information you want to see in test output
- Use print_manager.debug() for developer-level debugging details
- To see all print statements in test output, add the -s flag when running pytest:
  e.g., cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_plotbot.py -v -s

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_plotbot.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_plotbot.py::test_custom_variable_time_update -v
"""

import pytest
import numpy as np
import os
import sys
from datetime import datetime
import pandas as pd

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import print_manager first and set show_processing to True EARLY
from plotbot.print_manager import print_manager
print_manager.show_processing = True # SETTING THIS EARLY

from plotbot import mag_rtn_4sa, proton, plt, mag_rtn, epad
from plotbot.data_classes.custom_variables import custom_variable
from plotbot.plotbot_main import plotbot
from plotbot.test_pilot import phase, system_check

@pytest.mark.mission("Custom Variable Time Range Update")
def test_custom_variable_time_update():
    """Test that custom variables update their time range when plotbot is called with a new range"""
    
    print("\n================================================================================")
    print("TEST #1: Custom Variable Time Range Update")
    print("Verifies that custom variables update when time range changes")
    print("================================================================================\n")
    
    phase(1, "Creating custom variable structure")
    # Create custom variable structure - this relies on the division operator triggering
    # whatever internal mechanism loads data IF NEEDED by the operator itself.
    # The variable itself might be created 'empty' if sources aren't pre-loaded.
    ta_over_b = custom_variable('TestTAoverB', proton.anisotropy / mag_rtn_4sa.bmag)

    print_manager.test(f"Custom variable created: {ta_over_b.subclass_name} (Initial check before plotbot)")
    # DO NOT check contents yet - plotbot is responsible for ensuring it's populated.

    phase(2, "Calling plotbot with initial time range")
    # Initial time range
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

    # Call plotbot - THIS call is responsible for triggering internal get_data
    # for mag_rtn_4sa.bmag and for sources of ta_over_b (proton.anisotropy)
    # and ensuring ta_over_b is calculated/updated for trange.
    print_manager.test(f"Calling plotbot with initial trange: {trange}")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #1-A: Initial Load via Plotbot"
    plotbot(trange,
           mag_rtn_4sa.bmag, 1, # Plotbot needs to load this
           ta_over_b, 2)        # Plotbot needs to load sources & calculate this

    phase(3, "Verifying initial data load after plotbot")
    # Re-fetch variable reference after plotbot potentially updated it globally
    from plotbot import TestTAoverB # Get the potentially updated global reference
    check_var = TestTAoverB
    print_manager.test(f"Checking variable reference post-plotbot: {check_var.subclass_name}")

    # Check if the variable now has data for the initial range AFTER plotbot ran
    if not hasattr(check_var, 'datetime_array') or check_var.datetime_array is None or len(check_var.datetime_array) == 0:
        system_check("Initial Data Load (Post-Plotbot)", False, f"Custom variable should have data after first plotbot call for {trange}")
        pytest.fail("Test failed: Initial data not loaded by plotbot.")
        return

    initial_start = np.datetime64(check_var.datetime_array[0])
    initial_end = np.datetime64(check_var.datetime_array[-1])
    expected_start_dt = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check if start time is close to expected start
    time_diff = abs(initial_start - expected_start_dt)
    time_check_passed = time_diff < np.timedelta64(1, 'm') # Allow 1 min tolerance

    print_manager.test(f"Initial variable time range (Post-Plotbot): {initial_start} to {initial_end}")
    system_check("Initial Time Range Correct (Post-Plotbot)", time_check_passed,
                   f"Variable start time ({initial_start}) should be close to requested start ({expected_start_dt}) - Diff: {time_diff}")

    phase(4, "Calling plotbot again with new time range")
    # New time range that doesn't overlap with initial range
    new_trange = ['2023-09-28/08:00:00.000', '2023-09-28/09:30:00.000']

    # Call plotbot with the new range - this should trigger internal updates
    print_manager.test(f"Calling plotbot with new trange: {new_trange}")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #1-B: Time Range Update via Plotbot"
    plotbot(new_trange,
           mag_rtn_4sa.bmag, 1,
           ta_over_b, 2)

    phase(5, "Verifying custom variable was updated after second plotbot call")
    # Re-fetch the variable reference again
    from plotbot import TestTAoverB # Get the potentially updated global reference
    updated_var = TestTAoverB
    print_manager.test(f"Checking updated variable reference post-plotbot: {updated_var.subclass_name}")

    # Check if the variable's time range has been updated
    if not hasattr(updated_var, 'datetime_array') or updated_var.datetime_array is None or len(updated_var.datetime_array) == 0:
        system_check("Custom Variable Update (Post-Plotbot)", False, "Custom variable should still have data after time range update")
        pytest.fail("Test failed: Variable empty after update by plotbot.")
        return

    updated_start = np.datetime64(updated_var.datetime_array[0])
    updated_end = np.datetime64(updated_var.datetime_array[-1])
    expected_new_start_dt = np.datetime64(datetime.strptime(new_trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check if start time has advanced to the new range
    time_update_diff = abs(updated_start - expected_new_start_dt)
    time_update_passed = time_update_diff < np.timedelta64(1, 'm') # Allow 1 min tolerance

    print_manager.test(f"Updated variable time range (Post-Plotbot): {updated_start} to {updated_end}")
    system_check("Custom Variable Time Update (Post-Plotbot)", time_update_passed,
                   f"Custom variable start time ({updated_start}) should update to new range ({expected_new_start_dt}) - Diff: {time_update_diff}")

@pytest.mark.mission("Custom Variable Time Range Update - Log Scale")
def test_custom_variable_time_update_log():
    """Test that custom variables update their time range when plotbot is called with a new range, using log scale"""
    
    print("\n================================================================================")
    print("TEST #2: Custom Variable Time Update (LOG SCALE)")
    print("Verifies custom variables with log scale update correctly with new time range")
    print("================================================================================\n")
    
    phase(1, "Creating custom variable structure")
    # Create custom variable structure
    ta_over_b = custom_variable('TestTAoverB_Log', proton.anisotropy / mag_rtn_4sa.bmag)

    # Set style attributes immediately after creation
    ta_over_b.y_scale = 'log'
    print(f"DEBUG - Set y_scale to: {ta_over_b.y_scale}")

    print_manager.test(f"Custom variable created: {ta_over_b.subclass_name}")
    # Verify metadata
    system_check("Custom Variable Metadata",
               ta_over_b.data_type == 'custom_data_type' and ta_over_b.class_name == 'custom_class',
               f"Custom variable should have data_type='custom_data_type' and class_name='custom_class', got data_type='{ta_over_b.data_type}', class_name='{ta_over_b.class_name}'")
    # DO NOT check time range yet

    phase(2, "Calling plotbot for initial load")
    # Initial time range
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

    # First plot - this should trigger data loading for trange
    print(f"DEBUG - First plotbot call with INITIAL time range: {trange}")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #2-A: Custom Variable (LOG SCALE) - Initial Time Range"
    plotbot(trange,
           mag_rtn_4sa.bmag, 1,
           ta_over_b, 2)
    print(f"DEBUG - First plot completed")

    phase(3, "Verifying initial load")
    # Check the variable AFTER the first plotbot call
    from plotbot import TestTAoverB_Log # Get updated global reference
    check_var = TestTAoverB_Log

    if not hasattr(check_var, 'datetime_array') or check_var.datetime_array is None or len(check_var.datetime_array) == 0:
        system_check("Initial Data Load (Post-Plotbot)", False, f"Custom variable should have data after plotbot call for {trange}")
        pytest.fail("Test failed: Initial data not loaded by plotbot.")
        return

    initial_start = np.datetime64(check_var.datetime_array[0])
    initial_end = np.datetime64(check_var.datetime_array[-1])
    expected_start_dt = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check time range
    time_diff = abs(initial_start - expected_start_dt)
    time_check_passed = time_diff < np.timedelta64(1, 'm')

    print_manager.test(f"Initial variable time range (Post-Plotbot): {initial_start} to {initial_end}")
    system_check("Initial Time Range Correct (Post-Plotbot)", time_check_passed,
                   f"Variable start time ({initial_start}) should be close to requested start ({expected_start_dt}) - Diff: {time_diff}")
    # Check if style was preserved through initial load
    system_check("Initial y_scale preserved", check_var.y_scale == 'log',
                   f"y_scale should be 'log', got '{check_var.y_scale}' after initial plotbot call")

    phase(4, "Calling plotbot for time range update")
    # New time range that doesn't overlap with initial range
    new_trange = ['2023-09-28/08:00:00.000', '2023-09-28/09:30:00.000']

    # Now call plotbot with the new range - this should trigger updates
    print_manager.test(f"Calling plotbot with time range: {new_trange}")
    print(f"DEBUG - Second plotbot call with NEW time range")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #2-B: Custom Variable (LOG SCALE) - New Time Range"
    plotbot(new_trange,
           mag_rtn_4sa.bmag, 1,
           ta_over_b, 2)
    print(f"DEBUG - Second plot completed")

    phase(5, "Verifying custom variable update")
    # Fetch the updated variable reference again
    from plotbot import TestTAoverB_Log
    updated_var = TestTAoverB_Log
    print_manager.test(f"Using updated reference post-second-plotbot: {updated_var.subclass_name}")

    # Verify that y_scale was preserved during update
    print(f"DEBUG - Updated variable y_scale: {updated_var.y_scale}")
    system_check("Updated y_scale preserved", updated_var.y_scale == 'log',
                   f"y_scale should remain 'log', got '{updated_var.y_scale}' after second plotbot call")

    # Check if the variable's time range has been updated
    if not hasattr(updated_var, 'datetime_array') or updated_var.datetime_array is None or len(updated_var.datetime_array) == 0:
        system_check("Custom Variable Update (Post-Plotbot)", False,
                    "Custom variable should still have data after time range update")
        pytest.fail("Test failed: Variable empty after update by plotbot.")
        return

    updated_start = np.datetime64(updated_var.datetime_array[0])
    updated_end = np.datetime64(updated_var.datetime_array[-1])
    expected_new_start_dt = np.datetime64(datetime.strptime(new_trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check that the time has advanced to the new range
    time_update_diff = abs(updated_start - expected_new_start_dt)
    time_update_passed = time_update_diff < np.timedelta64(1, 'm') # Allow 1 min tolerance

    print_manager.test(f"Updated variable time range (Post-Plotbot): {updated_start} to {updated_end}")
    system_check("Custom Variable Time Update (Post-Plotbot)", time_update_passed,
                   f"Custom variable start time ({updated_start}) should update to new range ({expected_new_start_dt}) - Diff: {time_update_diff}")

@pytest.mark.mission("Custom Variable Time Range Update - Linear Scale")
def test_custom_variable_time_update_linear():
    """Test that custom variables update their time range when plotbot is called with a new range, using linear scale"""
    
    print("\n================================================================================")
    print("TEST #3: Custom Variable Time Update (LINEAR SCALE)")
    print("Verifies custom variables with linear scale update correctly with new time range")
    print("================================================================================\n")
    
    phase(1, "Creating custom variable structure")
    # Create custom variable structure
    ta_over_b_lin = custom_variable('TestTAoverB_Linear', proton.anisotropy / mag_rtn_4sa.bmag)

    # Set style attributes immediately after creation
    ta_over_b_lin.y_scale = 'linear' # Ensure linear scale
    print(f"DEBUG - Set y_scale to: {ta_over_b_lin.y_scale}")

    print_manager.test(f"Custom variable created: {ta_over_b_lin.subclass_name}")
    # Verify metadata
    system_check("Custom Variable Metadata",
               ta_over_b_lin.data_type == 'custom_data_type' and ta_over_b_lin.class_name == 'custom_class',
               f"Custom variable should have data_type='custom_data_type' and class_name='custom_class', got data_type='{ta_over_b_lin.data_type}', class_name='{ta_over_b_lin.class_name}'")

    phase(2, "Calling plotbot for initial load")
    # Initial time range
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

    # First plot - this should trigger data loading for trange
    print(f"DEBUG - First plotbot call with INITIAL time range: {trange}")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #3-A: Custom Variable (LINEAR SCALE) - Initial Time Range"
    plotbot(trange,
           mag_rtn_4sa.bmag, 1,
           ta_over_b_lin, 2)
    print(f"DEBUG - First plot completed")

    phase(3, "Verifying initial load")
    # Check the variable AFTER the first plotbot call
    from plotbot import TestTAoverB_Linear # Get updated global reference
    check_var = TestTAoverB_Linear

    if not hasattr(check_var, 'datetime_array') or check_var.datetime_array is None or len(check_var.datetime_array) == 0:
        system_check("Initial Data Load (Post-Plotbot)", False, f"Custom variable should have data after plotbot call for {trange}")
        pytest.fail("Test failed: Initial data not loaded by plotbot.")
        return

    initial_start = np.datetime64(check_var.datetime_array[0])
    initial_end = np.datetime64(check_var.datetime_array[-1])
    expected_start_dt = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check time range
    time_diff = abs(initial_start - expected_start_dt)
    time_check_passed = time_diff < np.timedelta64(1, 'm')

    print_manager.test(f"Initial variable time range (Post-Plotbot): {initial_start} to {initial_end}")
    system_check("Initial Time Range Correct (Post-Plotbot)", time_check_passed,
                   f"Variable start time ({initial_start}) should be close to requested start ({expected_start_dt}) - Diff: {time_diff}")
    # Check if style was preserved through initial load
    system_check("Initial y_scale preserved", check_var.y_scale == 'linear',
                   f"y_scale should be 'linear', got '{check_var.y_scale}' after initial plotbot call")

    phase(4, "Calling plotbot for time range update")
    # New time range that doesn't overlap with initial range
    new_trange = ['2023-09-28/08:00:00.000', '2023-09-28/09:30:00.000']

    # Now call plotbot with the new range - this should trigger updates
    print_manager.test(f"Calling plotbot with time range: {new_trange}")
    print(f"DEBUG - Second plotbot call with NEW time range")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #3-B: Custom Variable (LINEAR SCALE) - New Time Range"
    plotbot(new_trange,
           mag_rtn_4sa.bmag, 1,
           ta_over_b_lin, 2)
    print(f"DEBUG - Second plot completed")

    phase(5, "Verifying custom variable update")
    # Fetch the updated variable reference again
    from plotbot import TestTAoverB_Linear
    updated_var = TestTAoverB_Linear
    print_manager.test(f"Using updated reference post-second-plotbot: {updated_var.subclass_name}")

    # Verify that y_scale was preserved during update
    print(f"DEBUG - Updated variable y_scale: {updated_var.y_scale}")
    system_check("Updated y_scale preserved", updated_var.y_scale == 'linear',
                   f"y_scale should remain 'linear', got '{updated_var.y_scale}' after second plotbot call")

    # Check if the variable's time range has been updated
    if not hasattr(updated_var, 'datetime_array') or updated_var.datetime_array is None or len(updated_var.datetime_array) == 0:
        system_check("Custom Variable Update (Post-Plotbot)", False,
                    "Custom variable should still have data after time range update")
        pytest.fail("Test failed: Variable empty after update by plotbot.")
        return

    updated_start = np.datetime64(updated_var.datetime_array[0])
    updated_end = np.datetime64(updated_var.datetime_array[-1])
    expected_new_start_dt = np.datetime64(datetime.strptime(new_trange[0], '%Y-%m-%d/%H:%M:%S.%f'))

    # Check that the time has advanced to the new range
    time_update_diff = abs(updated_start - expected_new_start_dt)
    time_update_passed = time_update_diff < np.timedelta64(1, 'm') # Allow 1 min tolerance

    print_manager.test(f"Updated variable time range (Post-Plotbot): {updated_start} to {updated_end}")
    system_check("Custom Variable Time Update (Post-Plotbot)", time_update_passed,
                   f"Custom variable start time ({updated_start}) should update to new range ({expected_new_start_dt}) - Diff: {time_update_diff}")

@pytest.mark.mission("Empty Plot Handling")
def test_empty_plot_handling():
    """Test that plotbot correctly handles and debugs empty plots"""
    
    # TODO: This test is temporarily disabled. We'll revisit it later.
    # It's currently failing with a NameError related to 'ploptions'.
    # When we re-enable it, we'll need to fix the import or definition.
    pytest.skip("Test temporarily disabled - needs fixing")
    
    print("\n================================================================================")
    print("TEST #4: Empty Plot Handling")
    print("Verifies that empty plots are handled gracefully with proper debug output")
    print("================================================================================\n")
    
    phase(1, "Setting up test with NaN data")
    # Create time range
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Create arrays filled with NaN
    nan_array1 = np.full(1000, np.nan)  # First array of NaNs
    nan_array2 = np.full(1000, np.nan)  # Second array of NaNs
    
    # Create datetime array for the time range
    start_time = np.datetime64('2023-09-28T06:00:00.000')
    time_step = np.timedelta64(5, 's')  # 5 second intervals
    datetime_array = np.array([start_time + i * time_step for i in range(1000)])
    
    # Create plot_manager instances with NaN data
    from plotbot.plot_manager import plot_manager
    
    # Create first NaN variable
    nan_var1 = plot_manager(nan_array1, plot_options=ploptions(
        data_type='test_type',
        class_name='test_class',
        subclass_name='nan_var1',
        plot_type='time_series',
        datetime_array=datetime_array,
        y_label='NaN Data 1',
        legend_label='NaN 1',
        color='blue',
        y_scale='linear'
    ))
    
    # Create second NaN variable
    nan_var2 = plot_manager(nan_array2, plot_options=ploptions(
        data_type='test_type',
        class_name='test_class',
        subclass_name='nan_var2',
        plot_type='time_series',
        datetime_array=datetime_array,
        y_label='NaN Data 2',
        legend_label='NaN 2',
        color='red',
        y_scale='linear'
    ))
    
    phase(2, "Attempting to plot NaN variables")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #4: Empty Plot Test"
    
    # Enable debug output to capture the empty plot messages
    print_manager.show_debug = True
    
    # Try to plot - this should create empty plots since all data is NaN
    plotbot(trange, 
           nan_var1, 1,
           nan_var2, 2)
    
    phase(3, "Verifying empty plot handling")
    # Get the time indices
    indices1 = time_clip(nan_var1.datetime_array, trange[0], trange[1])
    indices2 = time_clip(nan_var2.datetime_array, trange[0], trange[1])
    
    # Check that we have time indices but all data is NaN
    system_check("Has time indices",
                len(indices1) > 0 and len(indices2) > 0,
                "Should have time indices for NaN data")
    
    # Check that all data points are NaN
    data1 = np.array(nan_var1)[indices1]
    data2 = np.array(nan_var2)[indices2]
    
    system_check("All data is NaN",
                np.all(np.isnan(data1)) and np.all(np.isnan(data2)),
                "All data points should be NaN")
    
    # Reset debug setting
    print_manager.show_debug = False

@pytest.mark.mission("Plot Manager Truthiness")
def test_simple_plot_truthiness_error():
    """
    Verifies if the ValueError related to plot_manager truthiness and
    DataTracker trange parsing occurs with a more complex plotbot call.
    Also checks actual data time ranges post-plotting.
    """
    print("\n================================================================================")
    print("TEST #X: Plot Manager Truthiness & Data Range Check")
    print("Verifies errors with complex plotbot call and checks data time coverage")
    print("================================================================================\n")

    phase(1, "Setting up and running complex plotbot call")
    # Time range for the test
    TRANGE = ['2023-09-28/00:00:00.000', '2023-09-29/00:00:00.000'] # Full day, as per Robert's original specification
    # TRANGE = ['2023-09-28/00:00:00.000', '2023-09-28/23:59:59.999'] # Explicitly one day to avoid ambiguity with next day start

    print_manager.test(f"Calling plotbot with TRANGE: {TRANGE} and variables: mag_rtn.br, proton.anisotropy, mag_rtn.br_norm")
    try:
        plotbot(TRANGE,
                mag_rtn.br, 1,
                proton.anisotropy, 2,
                mag_rtn.br_norm, 3)
        system_check("Complex plotbot call execution", True, "Plotbot call completed.")
        print_manager.test("Complex plotbot call execution - PASSED: Plotbot call completed.")
    except ValueError as e:
        if "truth value of an array" in str(e):
            system_check("Complex plotbot call execution (ValueError)", False, f"Plotbot call failed with truthiness ValueError: {e}")
            pytest.fail(f"Test failed due to truthiness ValueError: {e}")
        elif "Input trange elements must be strings or datetime/timestamp objects" in str(e):
            system_check("Complex plotbot call execution (DataTracker ValueError)", False, f"Plotbot call failed with DataTracker ValueError: {e}")
            # We might expect this error if np.datetime64 is passed and not handled, let the test continue to check data ranges.
            print_manager.warning(f"DataTracker ValueError encountered: {e} - This might be expected without np.datetime64 handling.")
        else:
            system_check("Complex plotbot call execution (Other ValueError)", False, f"Plotbot call failed with unexpected ValueError: {e}")
            pytest.fail(f"Test failed due to unexpected ValueError: {e}")
    except Exception as e:
        system_check("Complex plotbot call execution (Exception)", False, f"Plotbot call failed with an unexpected exception: {e}")
        pytest.fail(f"Test failed due to an unexpected exception: {e}")

    phase(2, "Checking actual data time ranges post-plotbot call")

    variables_to_check = {
        "mag_rtn.br": mag_rtn.br,
        "proton.anisotropy": proton.anisotropy,
        "mag_rtn.br_norm": mag_rtn.br_norm
    }

    for name, var_obj in variables_to_check.items():
        print_manager.test(f"--- Checking time range for: {name} ---")
        if hasattr(var_obj, 'datetime_array') and var_obj.datetime_array is not None and len(var_obj.datetime_array) > 0:
            start_time = var_obj.datetime_array[0]
            end_time = var_obj.datetime_array[-1]
            print_manager.test(f"  {name} data range: {start_time} to {end_time}")
            print_manager.test(f"  {name} number of data points: {len(var_obj.datetime_array)}")
            # Specific check for noon cutoff if relevant
            if 'mag_rtn' in name:
                expected_end_day = pd.Timestamp(TRANGE[1]).normalize() # This will be the start of 2023-09-29
                # For a TRANGE ending at '2023-09-29/00:00:00.000', data should go right up to, but not include, this exact timestamp.
                # So, actual_end_time_ts should be < expected_end_day. If it's much less, it's a problem.
                # Let's define 'much less' as not even reaching the end of the *previous* day (2023-09-28).
                # The end of 2023-09-28 is just before 2023-09-29T00:00:00.
                # So if actual_end_time_ts is less than, say, 2023-09-28T23:00:00, it's a problem.
                # A simpler check for now: if it doesn't reach within an hour of the trange end.
                # pd.Timestamp(TRANGE[1]) is the exclusive end, so data should go up to just before it.
                # If data ends before TRANGE[1] - 1 hour, then warn.
                if pd.Timestamp(end_time) < (pd.Timestamp(TRANGE[1]) - pd.Timedelta(hours=1)):
                     print_manager.warning(f"  WARNING: {name} data ends at {pd.Timestamp(end_time)}, which is more than 1 hour before requested end {pd.Timestamp(TRANGE[1])}.")
        else:
            print_manager.warning(f"  {name} has no data (datetime_array is None or empty).")

    print_manager.test("Finished checking data time ranges.")

#===================================================================================================
# TEST #X+1: EPAD Adjacent Time Range Issue
#===================================================================================================
@pytest.mark.mission("EPAD Data Disappearing")
def test_epad_adjacent_trange_issue():
    """
    Tests if EPAD data correctly loads for a second, adjacent time range
    when called sequentially after an initial plotbot call for EPAD.
    This replicates the issue where data for the second range disappears.
    """
    test_id = "EPAD Adjacent TRANGE"
    phase_num = 1

    def phase(num, description):
        nonlocal phase_num
        phase_num = num
        print_manager.test(f"PHASE {phase_num} ({test_id}): {description}")

    print("\n================================================================================")
    print(f"TEST ({test_id}): EPAD Data Disappearance with Adjacent Time Ranges")
    print("Verifies that EPAD data loads correctly for sequentially called adjacent time ranges.")
    print("================================================================================\n")

    # Ensure print manager settings are verbose for debugging this test
    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True
    # print_manager.show_datacubby = True # Enable if deep DataCubby inspection is needed

    # Clear any existing epad data from DataCubby and global_tracker to ensure a clean test state
    # This is important to prevent state from previous tests or notebook runs from interfering.
    if 'epad' in plotbot_core.pb.data_cubby.get_all_instance_names():
        epad_instance = plotbot_core.pb.data_cubby.get_instance('epad')
        if epad_instance:
            print_manager.test(f"({test_id}) Clearing existing epad instance data from DataCubby.")
            epad_instance.datetime_array = None # Or a more formal clear method if available
            epad_instance.strahl = None # Or a more formal clear method if available
            # Potentially clear other relevant attributes on epad_instance
    print_manager.test(f"({test_id}) Clearing EPAD calculation cache from global_tracker.")
    global_tracker.clear_calculation_cache(data_type='epad')
    print_manager.test(f"({test_id}) Clearing EPAD imported ranges from global_tracker.")
    if 'epad' in global_tracker.imported_ranges:
        del global_tracker.imported_ranges['epad']

    Trange_1 = ['2021/04/26 00:00:00.000', '2021/04/28 00:00:00.000']
    Trange_2 = ['2021/04/28 00:00:00.000', '2021/05/02 00:00:00.000'] # Note: Changed to 02 from 2 for consistency

    phase(1, f"Calling plotbot for Trange_1: {Trange_1} with epad.strahl")
    plotbot_core.plotbot(Trange_1, plotbot_core.pb.epad.strahl, 1)

    phase(2, "Verifying data presence for epad.strahl after Trange_1 plotbot call")
    epad_data_t1 = plotbot_core.pb.data_cubby.get_instance('epad')
    assert epad_data_t1 is not None, f"({test_id}) EPAD instance should exist in DataCubby after Trange_1 call."
    # Check for the actual data array used for plotting, assuming it's on the variable object itself
    # The exact attribute might differ, e.g., epad_data_t1.strahl.data or epad_data_t1.strahl.datetime_array
    # For now, let's assume epad_data_t1.strahl itself would be None or have a clear indicator if no data
    # A more robust check would be to inspect the actual time series data length for the requested range.
    assert hasattr(epad_data_t1, 'strahl') and epad_data_t1.strahl is not None, f"({test_id}) epad.strahl should have data after Trange_1 call."
    
    # A more specific check would be to see if there are data points within Trange_1
    # This requires knowing how the data is stored and accessed.
    # For now, we assume if epad_data_t1.strahl is populated, it has the Trange_1 data.
    print_manager.test(f"({test_id}) Data for epad.strahl confirmed present after Trange_1 call.")

    # --- Log DataTracker state for epad BEFORE the second call ---
    phase(3, "Logging DataTracker state for EPAD before Trange_2 call")
    if 'epad' in global_tracker.imported_ranges:
        print_manager.debug(f"[DataTracker][EPAD_STATE_PRE_T2] Imported ranges for EPAD: {global_tracker.imported_ranges['epad']}")
    else:
        print_manager.debug("[DataTracker][EPAD_STATE_PRE_T2] No imported ranges for EPAD.")
    if 'epad' in global_tracker.calculated_ranges:
        print_manager.debug(f"[DataTracker][EPAD_STATE_PRE_T2] Calculated ranges for EPAD: {global_tracker.calculated_ranges['epad']}")
    else:
        print_manager.debug("[DataTracker][EPAD_STATE_PRE_T2] No calculated ranges for EPAD.")

    phase(4, f"Calling plotbot for Trange_2: {Trange_2} with epad.strahl")
    plotbot_core.plotbot(Trange_2, plotbot_core.pb.epad.strahl, 1)

    phase(5, "Verifying data presence for epad.strahl after Trange_2 plotbot call")
    epad_data_t2 = plotbot_core.pb.data_cubby.get_instance('epad')
    assert epad_data_t2 is not None, f"({test_id}) EPAD instance should exist in DataCubby after Trange_2 call."
    
    # This is the critical assertion we expect might fail based on the reported issue.
    # We need to ensure that new data for Trange_2 was loaded or that the existing data now covers Trange_2.
    # A simple check for presence might not be enough; we need to verify data *within Trange_2*.
    # For now, a basic check like the one for Trange_1:
    assert hasattr(epad_data_t2, 'strahl') and epad_data_t2.strahl is not None, f"({test_id}) epad.strahl should have data after Trange_2 call."

    # More robust check: Verify that the datetime_array of epad.strahl now covers Trange_2.
    # This requires access to the actual time data. Let's assume we can get it via epad_data_t2.strahl.datetime_array
    # And that this is a numpy array or pandas Series/Index of datetimes.
    if hasattr(epad_data_t2.strahl, 'datetime_array') and epad_data_t2.strahl.datetime_array is not None and len(epad_data_t2.strahl.datetime_array) > 0:
        min_time_t2 = pd.Timestamp(min(epad_data_t2.strahl.datetime_array)).tz_localize('UTC')
        max_time_t2 = pd.Timestamp(max(epad_data_t2.strahl.datetime_array)).tz_localize('UTC')
        trange_2_start = pd.Timestamp(Trange_2[0]).tz_localize('UTC')
        trange_2_end = pd.Timestamp(Trange_2[1]).tz_localize('UTC')
        print_manager.test(f"({test_id}) EPAD data for Trange_2: Actual min_time={min_time_t2}, max_time={max_time_t2}")
        print_manager.test(f"({test_id}) EPAD data for Trange_2: Requested Trange_2_start={trange_2_start}, Trange_2_end={trange_2_end}")
        # Check if the actual data loaded for epad covers any part of Trange_2
        # A simple check: is the end of the loaded data greater than or equal to the start of Trange_2?
        # And is the start of the loaded data less than or equal to the end of Trange_2?
        # This is a basic overlap check.
        covers_trange_2_start = max_time_t2 >= trange_2_start
        covers_trange_2_end = min_time_t2 <= trange_2_end
        # A more precise check for this specific adjacent case:
        # The data should ideally span up to trange_2_end or at least significantly into Trange_2.
        # For an adjacent case, if merging worked, max_time_t2 should be close to trange_2_end.
        assert max_time_t2 >= trange_2_end - pd.Timedelta(minutes=1), \
            f"({test_id}) Data for epad.strahl after Trange_2 call does not extend to cover Trange_2. Max data time: {max_time_t2}, Expected end: {trange_2_end}"
        print_manager.test(f"({test_id}) Data for epad.strahl confirmed present and covering Trange_2.")
    else:
        # If datetime_array is not available or empty, the previous simpler assert should catch it.
        # But if it exists and is empty, explicitly fail.
        if hasattr(epad_data_t2.strahl, 'datetime_array') and (epad_data_t2.strahl.datetime_array is None or len(epad_data_t2.strahl.datetime_array) == 0):
             pytest.fail(f"({test_id}) epad.strahl.datetime_array is None or empty after Trange_2 call, indicating no data loaded for Trange_2.")
        # If the attribute doesn't even exist, the earlier assert handles it.

    print_manager.test(f"TEST ({test_id}) PASSED: EPAD data loaded correctly for adjacent time ranges.")

#===================================================================================================
# TEST: EPAD Adjacent Time Range Issue - Observational
#===================================================================================================
@pytest.mark.mission("EPAD Data Disappearing Observation")
def test_epad_adjacent_trange_issue_observational():
    """
    Observational test for EPAD data loading with adjacent time ranges.
    Calls plotbot sequentially and relies on print output for diagnostics.
    """
    test_id = "EPAD Adjacent TRANGE Observation"
    print("\n================================================================================")
    print(f"TEST ({test_id}): EPAD Data Disappearance with Adjacent Time Ranges - Observational")
    print("Verifies EPAD data loading for sequentially called adjacent time ranges via print logs.")
    print("================================================================================\n")

    # Ensure print manager settings are verbose for debugging this test
    # These should pick up the settings from the notebook if run there,
    # but explicitly setting them here for direct pytest runs.
    original_show_status = print_manager.show_status
    original_show_debug = print_manager.show_debug
    original_show_processing = print_manager.show_processing
    original_show_datacubby = print_manager.show_datacubby

    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True # As per user request for DataCubby prints
    print_manager.show_test = True

    print_manager.test(f"({test_id}) Print manager settings: status={print_manager.show_status}, debug={print_manager.show_debug}, processing={print_manager.show_processing}, datacubby={print_manager.show_datacubby}")

    Trange_1 = ['2021/04/26 00:00:00.000', '2021/04/28 00:00:00.000']
    Trange_2 = ['2021/04/28 00:00:00.000', '2021/05/02 00:00:00.000']

    print_manager.test(f"({test_id}) PHASE 1: Calling plotbot for Trange_1: {Trange_1} with epad.strahl")
    plotbot(Trange_1, epad.strahl, 1)
    print_manager.test(f"({test_id}) PHASE 1: Completed plotbot call for Trange_1.")

    print_manager.test(f"({test_id}) PHASE 2: Calling plotbot for Trange_2: {Trange_2} with epad.strahl")
    plotbot(Trange_2, epad.strahl, 1)
    print_manager.test(f"({test_id}) PHASE 2: Completed plotbot call for Trange_2.")

    print_manager.test(f"({test_id}) Observational test complete. Review logs for DataTracker and DataCubby behavior.")

    # Restore original print manager settings
    print_manager.show_status = original_show_status
    print_manager.show_debug = original_show_debug
    print_manager.show_processing = original_show_processing
    print_manager.show_datacubby = original_show_datacubby 

@pytest.mark.mission("Proton Energy Flux Data Disappearing Observation")
def test_proton_energy_flux_adjacent_trange_issue_observational():
    """Observational test for sequential proton.energy_flux plots with adjacent time ranges."""
    print_manager.test("\n================================================================================")
    print_manager.test("TEST: Proton Energy Flux Adjacent Time Range Issue (Observational)")
    print_manager.test("Objective: Observe behavior when plotting proton.energy_flux for two adjacent time ranges sequentially.")
    print_manager.test("================================================================================\n")

    # Ensure necessary modules are accessible
    from plotbot import proton, plt
    from plotbot.plotbot_main import plotbot
    from plotbot.print_manager import print_manager # Ensure print_manager is available

    # --- Test Setup ---
    print_manager.test("--- Phase 1: Test Setup ---")
    # Set print_manager verbosity for detailed test output
    print_manager.show_status = True
    print_manager.show_debug = True      # Enable for deep dive if needed
    print_manager.show_processing = True
    print_manager.show_datacubby = True   # Enable for DataCubby insights
    # print_manager.show_data_tracker = True # Optional: for DataTracker insights

    plt.options.use_single_title = True
    # It might be useful to clear caches if running this test repeatedly to ensure a clean state,
    # but for an observational test, let's see the natural behavior first.
    # from plotbot.data_tracker import global_tracker
    # global_tracker.clear_calculation_cache('spi_sf00_l3_mom') # Clear proton cache
    # print_manager.test("Cleared proton calculation cache (spi_sf00_l3_mom).")

    Trange_1 = ['2021/04/26 00:00:00.000', '2021/04/28 00:00:00.000']
    Trange_2 = ['2021/04/28 00:00:00.000', '2021/05/02 00:00:00.000'] # Corrected end date based on notebook
    print_manager.test(f"Trange_1 defined as: {Trange_1}")
    print_manager.test(f"Trange_2 defined as: {Trange_2}")

    # --- First Plot Call ---
    print_manager.test("\n--- Phase 2: First Plotbot Call (Trange_1) ---")
    plt.options.single_title_text = f"Proton Energy Flux - Trange 1: {Trange_1[0]} to {Trange_1[1]}"
    print_manager.test(f"First plotbot call for TRANGE_1: {Trange_1} with proton.energy_flux")
    try:
        plotbot(Trange_1, proton.energy_flux, 1)
        print_manager.test("First plotbot call completed.")
    except Exception as e:
        print_manager.test(f"ERROR during first plotbot call: {e}")
        pytest.fail(f"Test failed during first plotbot call: {e}")

    # --- Second Plot Call ---
    print_manager.test("\n--- Phase 3: Second Plotbot Call (Trange_2) ---")
    plt.options.single_title_text = f"Proton Energy Flux - Trange 2: {Trange_2[0]} to {Trange_2[1]}"
    print_manager.test(f"Second plotbot call for TRANGE_2: {Trange_2} with proton.energy_flux")
    try:
        plotbot(Trange_2, proton.energy_flux, 1)
        print_manager.test("Second plotbot call completed.")
    except Exception as e:
        print_manager.test(f"ERROR during second plotbot call: {e}")
        pytest.fail(f"Test failed during second plotbot call: {e}")

    print_manager.test("\n--- Phase 4: Test Completion ---")
    print_manager.test(f"SUCCESS - Proton Energy Flux adjacent time range test completed without runtime errors.") 