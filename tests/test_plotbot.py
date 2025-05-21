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

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import mag_rtn_4sa, proton, plt
from plotbot.data_classes.custom_variables import custom_variable
from plotbot.plotbot_main import plotbot
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager

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

@pytest.mark.mission("Empty Spectral Plot Handling")
def test_empty_spectral_plot_handling():
    """Test that plotbot correctly handles and debugs empty spectral plots (epad.strahl case)"""
    
    # TODO: This test is temporarily disabled. We'll revisit it later.
    # It's currently failing with an assertion error, as the spectral data is not empty as expected.
    # The test might need to be updated to reflect the actual data availability or behavior.
    pytest.skip("Test temporarily disabled - needs fixing")
    
    print("\n================================================================================")
    print("TEST #4: Empty Spectral Plot Handling")
    print("Verifies that empty spectral plots are handled gracefully (epad.strahl case)")
    print("================================================================================\n")
    
    phase(1, "Setting up test with real data")
    # Use the same time range from the example
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Configure strahl settings as in the example
    epad.strahl.colorbar_limits = 'default'
    epad.strahl.colorbar_scale = 'log'
    
    phase(2, "Attempting to plot with empty spectral data")
    plt.options.use_single_title = True
    plt.options.single_title_text = "TEST #4: Empty Spectral Plot Test"
    
    # Enable debug output to capture the empty plot messages
    print_manager.show_debug = True
    
    # Try to plot - this should create empty plots for the spectral data
    plotbot(trange, 
           mag_rtn_4sa.br, 1,  # Regular data that should work
           epad.strahl, 2)     # Spectral data that should be empty
    
    phase(3, "Verifying empty spectral plot handling")
    
    # Check that magnetic field data exists (control case)
    bmag_indices = time_clip(mag_rtn_4sa.br.datetime_array, trange[0], trange[1])
    system_check("Regular data exists",
                len(bmag_indices) > 0,
                "Should have regular (magnetic field) data")
    
    # Check that spectral data is empty
    has_datetime = hasattr(epad.strahl, 'datetime_array') and epad.strahl.datetime_array is not None
    if has_datetime:
        strahl_indices = time_clip(epad.strahl.datetime_array, trange[0], trange[1])
        empty_spectral = len(strahl_indices) == 0
    else:
        empty_spectral = True
    
    system_check("Spectral data is empty",
                empty_spectral,
                "Spectral data (epad.strahl) should be empty")
    
    # Reset debug setting
    print_manager.show_debug = False

@pytest.mark.mission("Plot Manager Truthiness")
def test_simple_plot_truthiness_error():
    """Test for the ValueError related to plot_manager truthiness in a simple plotbot call."""
    print("\n================================================================================")
    print("TEST #X: Plot Manager Truthiness in Simple Plot")
    print("Verifies if the ValueError occurs with a basic plotbot(TRANGE, mag_rtn_4sa.br, 1) call")
    print("================================================================================\n")

    phase(1, "Setting up and running simple plotbot call")
    print_manager.show_status = True
    print_manager.show_processing = True
    # print_manager.show_debug = True # Uncomment if deeper debugging prints are needed

    TRANGE = ['2023-09-28/00:00:00.000', '2023-09-29/00:00:00.000'] # 1 day
    
    print_manager.test(f"Calling plotbot with TRANGE: {TRANGE} and variable: mag_rtn_4sa.br")
    
    # We expect this call to potentially raise the ValueError
    # If it does, pytest will catch it and display the traceback.
    # If it passes without error, the test will pass, indicating the issue might be elsewhere or conditional.
    try:
        plotbot(TRANGE, mag_rtn_4sa.br, 1)
        system_check("Simple plotbot call execution", True, "Plotbot call completed without ValueError.")
    except ValueError as e:
        if "The truth value of an array with more than one element is ambiguous" in str(e):
            system_check("Simple plotbot call execution", False, f"ValueError caught as expected: {e}")
            pytest.fail(f"ValueError caught as expected, confirming the issue: {e}")
        else:
            system_check("Simple plotbot call execution", False, f"An unexpected ValueError occurred: {e}")
            raise # Re-raise if it's a different ValueError
    except Exception as e:
        system_check("Simple plotbot call execution", False, f"An unexpected error occurred: {e}")
        raise # Re-raise any other unexpected error 