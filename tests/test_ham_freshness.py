#tests/test_ham_freshness.py
# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python -m pytest tests/test_ham_freshness.py -vv -s
# To run a specific test (e.g., test_plotbot_ham_group_1) and see print output:
# conda run -n plotbot_env python -m pytest tests/test_ham_freshness.py::test_plotbot_ham_group_1 -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

"""
Tests for HAM data loading, freshness, and plotting functionality.

These tests verify that HAM data can be loaded via plotbot and that the
expected variables are created as plot_manager instances with data.
It follows the grouped testing pattern seen in test_fits_integration.py.

Run tests using:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_ham_freshness.py -v -s
"""

import pytest
import numpy as np
import pandas as pd
import traceback
import matplotlib.pyplot as plt

# Import necessary components from plotbot
# Assuming these are top-level exports or accessible paths
try:
    from plotbot import plotbot, multiplot, showdahodo 
    from plotbot.data_classes.psp_ham_classes import ham as ham_instance # Import the HAM instance
    from plotbot.plot_manager import plot_manager
    from plotbot.print_manager import print_manager
    from plotbot.plotbot_helpers import time_clip # Check if this is the correct location
    from plotbot.data_cubby import data_cubby # Need cubby to check instance post-load
except ImportError as e:
    pytest.fail(f"Failed to import necessary plotbot components: {e}")

# Define the test time range for HAM data
TEST_TRANGE = ['2025-03-22/12:00:00', '2025-03-22/14:00:00']

# Helper function to run grouped HAM tests
def _run_plotbot_ham_test_group(variables_to_plot):
    """
    Helper function to run a standard plotbot test for a group of HAM variables.
    Calls plotbot with the specified variables and verifies data loading.
    """
    plot_args = [TEST_TRANGE]
    var_names = []

    # Filter out None variables and get names
    valid_variables = [v for v in variables_to_plot if v is not None and hasattr(v, 'subclass_name')]
    if len(valid_variables) != len(variables_to_plot):
        print_manager.warning("Some variables passed to _run_plotbot_ham_test_group were None or invalid.")

    var_names = [v.subclass_name for v in valid_variables]
    print(f"\n--- Testing HAM Group: {var_names} --- For trange: {TEST_TRANGE}")

    # Prepare arguments for plotbot: [trange, var1, panel1, var2, panel2, ...]
    for i, var_instance in enumerate(valid_variables):
        panel_num = i + 1
        plot_args.extend([var_instance, panel_num])

    if not valid_variables:
        print_manager.warning("No valid HAM variables provided to test group. Skipping plotbot call.")
        pytest.skip("Skipping test group due to no valid variables.") # Skip the test if no vars
        return

    try:
        print(f"Attempting plotbot call for trange: {TEST_TRANGE} with variables: {var_names}")
        # Call plotbot - this should trigger data loading internally for the ham instrument
        plotbot(*plot_args)
        print("Plotbot call completed successfully.")

        # --- Assertions to verify data was loaded into the *single* ham_instance ---
        print("--- Verifying Data Availability Post-Plotbot Call ---")
        # Check overall time array first *on the imported instance*
        assert hasattr(ham_instance, 'datetime_array') and ham_instance.datetime_array is not None, "ham_instance.datetime_array is None after plotbot call"
        assert len(ham_instance.datetime_array) > 0, "ham_instance.datetime_array is empty after plotbot call."
        print(f"ham_instance datetime_array loaded. Length: {len(ham_instance.datetime_array)}. Range: {ham_instance.datetime_array.min()} to {ham_instance.datetime_array.max()}")

        # Now check each requested variable *on the imported instance*
        for name in var_names:
            assert hasattr(ham_instance, name), f"Variable '{name}' not found as attribute on ham_instance after plotbot call."
            var_plot_manager = getattr(ham_instance, name)

            assert isinstance(var_plot_manager, plot_manager), f"Attribute '{name}' is not a plot_manager instance (Type: {type(var_plot_manager)})."

            # Check the data within the plot manager (which IS the array)
            assert var_plot_manager is not None, f"Variable '{name}' (plot_manager) is None."
            assert len(var_plot_manager) > 0, f"Variable '{name}' (plot_manager) has empty data (length 0)."

            # Check data length matches the main datetime array length
            assert len(var_plot_manager) == len(ham_instance.datetime_array), f"Data length mismatch for '{name}': {len(var_plot_manager)} vs time {len(ham_instance.datetime_array)}"

            # Optionally check for all NaNs if data is expected
            if np.all(np.isnan(var_plot_manager)):
                 print_manager.warning(f"Variable '{name}' data is all NaN.")
                 # Decide if this should be a failure:
                 # pytest.fail(f"Variable '{name}' data is all NaN.")
            else:
                 # Only print if not all NaN
                 print(f"✅ Variable '{name}' (plot_manager) verified with data (length: {len(var_plot_manager)}). First value: {var_plot_manager[0]}")

        print(f"--- HAM Group Test Passed for: {var_names} ---")

    except Exception as e:
        # Correctly format the traceback for better debugging info
        tb_str = traceback.format_exc()
        pytest.fail(f"plotbot call failed for group {var_names} with exception: {e}\nTraceback: {tb_str}")


# --- Grouped HAM Variable Tests ---

# Note: We refer to attributes of the imported `ham_instance` singleton.

def test_plotbot_ham_group_1():
    """Tests HAM variables: hamogram_30s, hamogram_og_30s, hamogram_2m, hamogram_og_2m, hamogram_20m"""
    vars_to_test = [
        ham_instance.hamogram_30s,
        ham_instance.hamogram_og_30s,
        ham_instance.hamogram_2m,
        ham_instance.hamogram_og_2m,
        ham_instance.hamogram_20m
    ]
    _run_plotbot_ham_test_group(vars_to_test)

def test_plotbot_ham_group_2():
    """Tests HAM variables: hamogram_90m, hamogram_4h, hamogram_og_4h, trat_ham, trat_ham_og"""
    vars_to_test = [
        ham_instance.hamogram_90m,
        ham_instance.hamogram_4h,
        ham_instance.hamogram_og_4h,
        ham_instance.trat_ham,
        ham_instance.trat_ham_og
    ]
    _run_plotbot_ham_test_group(vars_to_test)

def test_plotbot_ham_group_3():
    """Tests HAM variables: ham_core_drift, ham_core_drift_va, Nham_div_Ncore, Nham_div_Ncore_og, Nham_div_Ntot"""
    # Note: Using attribute names matching the class definition (Nham_div_Ncore, etc.)
    vars_to_test = [
        ham_instance.ham_core_drift,
        ham_instance.ham_core_drift_va,
        ham_instance.Nham_div_Ncore,
        ham_instance.Nham_div_Ncore_og,
        ham_instance.Nham_div_Ntot
    ]
    _run_plotbot_ham_test_group(vars_to_test)

def test_plotbot_ham_group_4():
    """Tests HAM variables: Nham_div_Ntot_og, Tperp_ham_div_core, Tperp_ham_div_core_og, Tperprat_driftva_hc, Tperprat_driftva_hc_og"""
    vars_to_test = [
        ham_instance.Nham_div_Ntot_og,
        ham_instance.Tperp_ham_div_core,
        ham_instance.Tperp_ham_div_core_og,
        ham_instance.Tperprat_driftva_hc,
        ham_instance.Tperprat_driftva_hc_og
    ]
    _run_plotbot_ham_test_group(vars_to_test)

# --- Tests for other plotting functions with HAM variables ---

def test_showdahodo_with_ham_vars():
    """Tests using two HAM variables in showdahodo."""
    print(f"\n--- Testing showdahodo with HAM variables --- For trange: {TEST_TRANGE}")
    # Select two variables (e.g., trat_ham vs ham_core_drift_va)
    var_x = ham_instance.trat_ham
    var_y = ham_instance.ham_core_drift_va

    if var_x is None or var_y is None:
        pytest.fail("Failed to retrieve HAM variables for showdahodo test.")

    try:
        print(f"Attempting showdahodo call for trange: {TEST_TRANGE} with x={var_x.subclass_name}, y={var_y.subclass_name}")
        fig, ax = showdahodo(TEST_TRANGE, var_x, var_y)
        print("Showdahodo call completed successfully.")

        # --- Assertions ---
        assert fig is not None, "showdahodo should return a figure object."
        assert ax is not None, "showdahodo should return an axes object."

        # Check for scatter data (hodograms use scatter)
        scatter_plots = [child for child in ax.get_children() if isinstance(child, plt.matplotlib.collections.PathCollection)]
        assert len(scatter_plots) > 0, "Plot should contain scatter plot data."
        assert len(scatter_plots[0].get_paths()) > 0, "Scatter plot should have data points."

        assert ax.get_xlabel() == var_x.legend_label, f"X-axis label mismatch. Expected: {var_x.legend_label}, Got: {ax.get_xlabel()}"
        assert ax.get_ylabel() == var_y.legend_label, f"Y-axis label mismatch. Expected: {var_y.legend_label}, Got: {ax.get_ylabel()}"

        print(f"✅ Showdahodo test passed for {var_x.subclass_name} vs {var_y.subclass_name}")

    except Exception as e:
        tb_str = traceback.format_exc()
        pytest.fail(f"showdahodo call failed for HAM variables with exception: {e}\nTraceback: {tb_str}")
    finally:
        if 'fig' in locals() and fig is not None:
            plt.close(fig) # Close plot

def test_multiplot_with_ham_vars():
    """Tests using two HAM variables in multiplot."""
    print(f"\n--- Testing multiplot with HAM variables --- For trange: {TEST_TRANGE}")
    # Select two variables (e.g., hamogram_30s and Nham_div_Ntot)
    var1 = ham_instance.hamogram_30s
    var2 = ham_instance.Nham_div_Ntot

    if var1 is None or var2 is None:
        pytest.fail("Failed to retrieve HAM variables for multiplot test.")

    # Calculate center time for multiplot
    try:
        center_time = pd.Timestamp(TEST_TRANGE[0]) + (pd.Timestamp(TEST_TRANGE[1]) - pd.Timestamp(TEST_TRANGE[0])) / 2
        center_time_str = center_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
    except Exception as e:
        pytest.fail(f"Failed to calculate center time for multiplot: {e}")

    # Create plot_data list for multiplot
    plot_data = [
        (center_time_str, var1),
        (center_time_str, var2)
    ]

    try:
        print(f"Attempting multiplot call for center time: {center_time_str} with variables: {var1.subclass_name}, {var2.subclass_name}")
        # Assuming multiplot handles data loading internally if not already loaded
        fig, axs = multiplot(plot_data)
        print("Multiplot call completed successfully.")

        # --- Assertions ---
        assert fig is not None, "multiplot should return a figure object."
        assert axs is not None, "multiplot should return axes objects."
        assert len(axs) == 2, f"Expected 2 panels for multiplot, got {len(axs)}."

        # Check if each panel has data
        panel1_has_data = len(axs[0].get_lines()) > 0
        panel2_has_data = len(axs[1].get_lines()) > 0 or len([child for child in axs[1].get_children() if isinstance(child, plt.matplotlib.collections.PathCollection)]) > 0 # Check for scatter too

        assert panel1_has_data, f"Panel 1 (for {var1.subclass_name}) should have data lines."
        assert panel2_has_data, f"Panel 2 (for {var2.subclass_name}) should have data lines/points."

        # Optionally check y-labels if needed
        # assert axs[0].get_ylabel() == var1.y_label
        # assert axs[1].get_ylabel() == var2.y_label

        print(f"✅ Multiplot test passed for {var1.subclass_name} and {var2.subclass_name}")

    except Exception as e:
        tb_str = traceback.format_exc()
        pytest.fail(f"multiplot call failed for HAM variables with exception: {e}\nTraceback: {tb_str}")
    finally:
        if 'fig' in locals() and fig is not None:
            plt.close(fig) # Close plot

# --- Sanity Check ---
def test_sanity():
    """Basic check to ensure the test file itself is runnable."""
    assert True 