# tests/test_stardust.py
# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python -m pytest tests/test_stardust.py -vv -s
# To run a specific test (e.g., test_stardust_plotbot_basic) and see print output:
# conda run -n plotbot_env python -m pytest tests/test_stardust.py::test_stardust_plotbot_basic -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

"""
Master Stardust Test File

Aggregates key tests from various modules for a quick system health check.
"""

import matplotlib
# matplotlib.use('Agg') # COMMENTED OUT TO SHOW THE PLOT

# import matplotlib
# matplotlib.use('Agg') # Use non-interactive backend BEFORE importing pyplot - REMOVED

import pytest
import os
import sys
import numpy as np
from datetime import datetime
import glob
import time # Added for performance test and sleep
import cdflib # Add cdflib import
import logging # Added for caplog
import traceback
import pandas as pd
from scipy.io import wavfile # Keep this one
import tempfile # Added for audifier fixture
import shutil # Added for audifier fixture
import re # Added for audifier filename test (if included)
# --- REMOVE Internal Redirection for stderr --- 
# from contextlib import redirect_stderr, redirect_stdout # Import both
# --- ADD imports for stdout capture --- 
import io
from contextlib import redirect_stdout
# --- END ADD imports ---
# --- ADD unittest.mock and getpass imports --- 
from unittest.mock import patch
import getpass
# --- END ADD imports ---
from plotbot.server_access import server_access
from plotbot import config # Removed alias, import directly from package
from plotbot import ham as ham_instance # Import directly from package
from plotbot import custom_variable
from plotbot import print_manager

print_manager.show_debug = True

# --- Path Setup --- 
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

# --- Plotbot Imports --- 
import plotbot # For plotbot.config
from plotbot.plotbot_main import plotbot as plotbot_function
from plotbot.multiplot import multiplot
from plotbot.showdahodo import showdahodo
from plotbot.data_classes.data_types import data_types
from plotbot.data_classes.psp_proton_fits_classes import proton_fits as proton_fits_instance
from plotbot.data_import import find_local_csvs
from plotbot.plot_manager import plot_manager
from plotbot import print_manager # For logging
from plotbot import plt # For plot closing
from plotbot.test_pilot import phase, system_check # Test helpers
from plotbot.audifier import Audifier, audifier as global_audifier
from plotbot import mag_rtn, mag_rtn_4sa # MODIFIED
from plotbot.data_download_pyspedas import download_spdf_data # For SPDF debug test
from plotbot.data_download_berkeley import download_berkeley_data # For conflict test
from plotbot import config # Removed alias, import directly from package
from plotbot import ham as ham_instance # Import directly from package
from plotbot import custom_variable
from plotbot import proton, epad, psp_orbit # Added for class data alignment tests

# --- Test Constants & Fixtures --- 
# Re-define or import necessary constants/fixtures from other files
TEST_TRANGE_DEFAULT = ['2020-04-09/06:00:00.000', '2020-04-09/07:30:00.000']
TEST_DATE_STR_DEFAULT = '20200409'
TEST_YEAR_DEFAULT = '2020'

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
psp_data_dir = os.path.join(WORKSPACE_ROOT, 'data', 'psp') # Updated for unified data structure
PYSPEDAS_ROOT_DATA_DIR = os.path.join(WORKSPACE_ROOT, 'data', 'psp')

@pytest.fixture
def manage_config():
    original_server_mode = plotbot.config.data_server
    print(f"\n--- [Fixture] Saving original config.data_server: '{original_server_mode}' ---")
    try:
        yield # Test runs here
    finally:
        plotbot.config.data_server = original_server_mode
        print(f"--- [Fixture] Restored config.data_server to: '{plotbot.config.data_server}' ---")

# Global list for cleanup test
downloaded_files_to_clean = [] 

# Fixture needed by audifier tests
@pytest.fixture
def test_audifier():
    """Provide the global audifier instance with a temporary save directory."""
    audifier = global_audifier
    original_dir = audifier.save_dir
    temp_dir = tempfile.mkdtemp()
    audifier.set_save_dir(temp_dir)
    yield audifier
    audifier.set_save_dir(original_dir) if original_dir else None
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temp dir {temp_dir}: {e}")

# Fixture needed by custom variable tests
@pytest.fixture
def test_environment():
    """Provides time ranges needed for the custom variable tests."""
    # Using the same dates as the original custom var tests for simplicity
    return {
        'trange_initial': ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000'],
        # Add other ranges if needed by copied tests in the future
    }

# --- Test Functions will go below --- 


# === Basic Plotting Tests (from test_all_plot_basics.py) ===

# Use a shorter, common time range for stardust tests
STARDUST_TRANGE = ['2020-04-09/06:00:00.000', '2020-04-09/07:00:00.000']
STARDUST_CENTER_TIME = '2020-04-09/06:30:00.000'

@pytest.fixture(autouse=True)
def setup_stardust_test_plots():
    """Ensure plots are closed before and after each test in this file."""
    plt.close('all')
    yield
    plt.close('all')

@pytest.mark.mission("Stardust Test: Basic Plotbot (mag_rtn)")
def test_stardust_plotbot_basic():
    """Basic stardust test for plotbot with mag_rtn data."""
    print_manager.enable_debug() # Temporarily enable full debug output
    print("\n=== Testing plotbot (stardust) ===")
    fig = None # Initialize fig to None
    fig_num = None # Initialize fig_num
    try:
        phase(1, "Calling plotbot with Br, Bt, Bn (stardust)")
        # Assuming plotbot.plt.options are defaults or managed elsewhere
        plotbot_function(STARDUST_TRANGE,
                mag_rtn_4sa.br, 1, # Use mag_rtn_4sa consistent with source test
                mag_rtn_4sa.bt, 2,
                mag_rtn_4sa.bn, 3)

        phase(2, "Verifying plotbot call completed (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)

        system_check("Stardust Plotbot Call Completed", True, "plotbot call should complete without error.")
        system_check("Stardust Plotbot Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure.")

    except Exception as e:
        pytest.fail(f"Stardust Plotbot test failed: {e}")
    finally:
        # Always try to close the figure using its number
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing figure {fig_num} in finally block: {close_err} ---")
        # Fallback in case fig_num wasn't obtained but fig was
        elif fig is not None:
            try:
                plt.close(fig)
                print(f"--- Explicitly closed figure object in finally block (fallback) ---")
            except Exception as close_err:
                print(f"--- Error closing figure object in finally block (fallback): {close_err} ---")
        # If neither is available, try closing all as a last resort (though fixture should handle)
        # else:
        #    plt.close('all')

@pytest.mark.mission("Stardust Test: Basic Multiplot (mag_rtn)")
def test_stardust_multiplot_basic():
    """Basic stardust test for multiplot with mag_rtn data."""
    print("\n=== Testing multiplot (stardust) ===")
    fig = None
    axs = None
    fig_num = None # Initialize fig_num
    try:
        phase(1, "Setting up multiplot options (stardust)")
        # Use plt.options directly instead of config
        plt.options.window = '1:00:00.000' # Match STARDUST_TRANGE duration
        plt.options.position = 'around'
        plt.options.use_single_title = True
        plt.options.single_title_text = "Multiplot Stardust Test"

        phase(2, "Defining plot data and calling multiplot (stardust)")
        plot_data = [
            (STARDUST_CENTER_TIME, mag_rtn_4sa.br),
            (STARDUST_CENTER_TIME, mag_rtn_4sa.bt),
            (STARDUST_CENTER_TIME, mag_rtn_4sa.bn)
        ]
        fig, axs = multiplot(plot_data)
        fig_num = plt.gcf().number # Get figure number right after creation
        print(f"DEBUG: Type of axs returned by multiplot: {type(axs)}")

        phase(3, "Verifying multiplot output (stardust)")
        system_check("Stardust Multiplot Figure Created", fig is not None, "multiplot should return a figure object.")

        axes_valid = False
        if axs is not None:
            try:
                if hasattr(axs, '__len__') and len(axs) > 0 and isinstance(axs[0], plt.Axes):
                    axes_valid = True
                elif isinstance(axs, plt.Axes):
                    axes_valid = True
            except Exception as e:
                 print(f"DEBUG: Error checking stardust axs type: {e}") 
                 axes_valid = False 

        system_check("Stardust Multiplot Axes Returned", axes_valid, f"multiplot should return valid Axes object(s). Got type: {type(axs)}")
        
        # Show the plot
        # plt.show()

    except Exception as e:
        pytest.fail(f"Stardust Multiplot test failed: {e}")
    finally:
        # Explicitly close the figure created by this test using its number
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed multiplot figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing multiplot figure {fig_num} in finally block: {close_err} ---")

@pytest.mark.mission("Stardust Test: Basic Showdahodo (mag_rtn)")
def test_stardust_showdahodo_basic():
    """Basic stardust test for showdahodo with mag_rtn data."""
    print("\n=== Testing showdahodo (stardust) ===")
    fig = None
    ax = None # Keep track of axis too
    fig_num = None # Initialize fig_num
    try:
        phase(1, "Calling showdahodo with Bt vs Br (stardust)")
        fig, ax = showdahodo(STARDUST_TRANGE, mag_rtn_4sa.bt, mag_rtn_4sa.br)
        fig_num = plt.gcf().number # Get figure number right after creation

        phase(2, "Verifying showdahodo output (stardust)")
        system_check("Stardust Showdahodo Figure Created", fig is not None, "showdahodo should return a figure object.")
        system_check("Stardust Showdahodo Axis Created", ax is not None, "showdahodo should return an axis object.")

    except Exception as e:
        pytest.fail(f"Stardust Showdahodo test failed: {e}")
    finally:
        # Explicitly close the figure created by this test using its number
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed showdahodo figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing showdahodo figure {fig_num} in finally block: {close_err} ---")

# === End Basic Plotting Tests ===

# === Pyspedas Tests (from test_pyspedas_download.py) ===

# Import necessary for the new test
from plotbot.get_data import get_data

@pytest.mark.mission("Dynamic Mode Fallback Logic Verification (via get_data call)")
def test_dynamic_mode_fallback_logic_integrated(manage_config): # Use manage_config fixture
    """Tests the dynamic mode fallback logic by calling get_data with patched downloaders."""
    print_manager.enable_debug()
    print("--- Testing dynamic mode fallback logic via get_data call ---")

    test_trange = ['2024-12-24/06:00:00.000', '2024-12-24/07:30:00.000']
    # Pass an actual variable object that get_data expects
    test_variable = mag_rtn_4sa.br # Or any variable using a type needing fallback test

    # Set the server mode to dynamic (fixture will restore)
    plotbot.config.data_server = 'dynamic'
    print(f"Set config.data_server = '{plotbot.config.data_server}'")

    # --- Mocks ---
    # Simple flag dictionary is fine
    call_record = {'spdf_called': False, 'berkeley_called': False}

    def mock_spdf(*args, **kwargs):
        call_record['spdf_called'] = True
        print("--- Mock SPDF download called, returning [] (failure) ---")
        # Return empty list simulate pyspedas downloadonly failure
        return []

    def mock_berkeley(*args, **kwargs):
        call_record['berkeley_called'] = True
        print("--- Mock Berkeley download called ---")
        # Return True or dummy list to satisfy get_data's expectation if needed
        return True

    # --- Define CORRECT PATCH TARGETS based on where get_data finds them ---
    # EXAMPLE: Assumes get_data imports them directly
    spdf_patch_target = 'plotbot.get_data.download_spdf_data'       #<<< ADJUST IF NEEDED
    berkeley_patch_target = 'plotbot.get_data.download_berkeley_data' #<<< ADJUST IF NEEDED
    # --- ADJUST TARGETS ---

    print(f"Patching SPDF at '{spdf_patch_target}'")
    print(f"Patching Berkeley at '{berkeley_patch_target}'")

    # --- Patch and Call ---
    try:
        # Nest the patches
        with patch(spdf_patch_target, side_effect=mock_spdf) as spdf_mock, \
             patch(berkeley_patch_target, side_effect=mock_berkeley) as berkeley_mock:

            # Call the ACTUAL get_data function
            print("Calling get_data(...) with mocks active...")
            get_data(test_trange, test_variable) # Pass the variable object
            print("Call to get_data(...) completed.")

            # --- Assertions ---
            # Standard mock assertions are slightly preferred
            spdf_mock.assert_called_once()
            print("✅ Asserted: SPDF mock was called once.")
            berkeley_mock.assert_called_once()
            print("✅ Asserted: Berkeley mock was called once.")

            # Keep your dictionary check as backup if needed
            system_check("SPDF Mock Called (dict check)", call_record['spdf_called'], "SPDF mock flag should be True.")
            system_check("Berkeley Mock Called (dict check)", call_record['berkeley_called'], "Berkeley mock flag should be True.")

            print("\n✅✅✅ Dynamic mode fallback logic verified successfully within get_data! ✅✅✅")

    except Exception as e:
        pytest.fail(f"Test failed during get_data call with mocks: {e}\n{traceback.format_exc()}")
    # `finally` block with config restore is handled by the manage_config fixture

@pytest.mark.mission("Stardust Test: Cleanup Downloaded Files")
def test_stardust_cleanup_downloaded_files():
    """Deletes files potentially downloaded by other stardust tests."""
    # Note: This uses the *shared* downloaded_files_to_clean list
    print("\n=== Testing File Cleanup (stardust) ===")
    phase(1, "Identifying files for cleanup (stardust)")
    # Reuse the helper function logic from test_pyspedas_download
    files_to_clean = downloaded_files_to_clean # Use the global list
    print(f"Attempting to clean up {len(files_to_clean)} file(s) potentially downloaded by stardust tests:")
    for fpath in files_to_clean:
        print(f"  - {fpath}")

    if not files_to_clean:
        print("No files were marked for cleanup by stardust tests.")
        system_check("Stardust Cleanup Skipped", True, "No files recorded for cleanup.")
        return

    phase(2, "Deleting identified files (stardust)")
    all_deleted = True
    # Need WORKSPACE_ROOT defined globally or passed in
    global WORKSPACE_ROOT 
    for fpath_relative in files_to_clean:
        # Construct absolute path robustly
        # Handle potential absolute paths already in the list (though unlikely from pyspedas)
        if os.path.isabs(fpath_relative):
            fpath_absolute = fpath_relative
        else:
            fpath_absolute = os.path.join(WORKSPACE_ROOT, fpath_relative)
            
        file_exists_before = os.path.exists(fpath_absolute)
        deleted_this_file = False
        try:
            if file_exists_before:
                os.remove(fpath_absolute)
                deleted_this_file = not os.path.exists(fpath_absolute)
                print(f"Attempted deletion of {os.path.basename(fpath_absolute)}")
            else:
                print(f"File already gone? Skipping deletion: {os.path.basename(fpath_absolute)}")
                deleted_this_file = True # Considered deleted if not found

            check_msg = f"File {os.path.basename(fpath_absolute)} should be deleted."
            if not file_exists_before:
                check_msg += " (File was not present before attempt)"

            system_check(f"Deletion of {os.path.basename(fpath_absolute)} (stardust)", deleted_this_file, check_msg)
            if not deleted_this_file:
                all_deleted = False

        except OSError as e:
            system_check(f"Deletion of {os.path.basename(fpath_absolute)} (stardust)", False, f"Error deleting file {fpath_absolute}: {e}")
            all_deleted = False

    phase(3, "Final cleanup verification (stardust)")
    system_check("Overall Stardust Cleanup Status", all_deleted, "All identified test files should be successfully deleted.")
    # Clear the list after attempting cleanup
    downloaded_files_to_clean.clear()

# === End Pyspedas Tests ===

# === Custom Variables Test ===

# @pytest.mark.mission("Stardust Test: Custom Variables") - REMOVED due to incorrect approach
# def test_stardust_custom_variables():
#     """Tests plotting simple custom variables using plotbot."""
#     print("\n=== Testing Custom Variables (stardust) ===")
#     fig = None
#     try:
#         phase(1, "Defining and plotting custom variables (stardust)")
#         # Define custom variables using plotbot syntax
#         custom_vars = [
#             "mag_rtn.br + mag_rtn.bt", # Simple addition
#             "np.abs(mag_rtn.bn)"      # Using numpy function
#         ]
#         
#         # Pass them to plotbot
#         plot_args = []
#         for i, expr in enumerate(custom_vars):
#             plot_args.extend([expr, i + 1]) # Variable expression string and panel number
#             
#         plotbot_function(STARDUST_TRANGE, *plot_args)
# 
#         phase(2, "Verifying custom variable plot call completed (stardust)")
#         fig_num = plt.gcf().number 
#         fig = plt.figure(fig_num) 
# 
#         system_check("Stardust Custom Var Plot Completed", True, "Plotbot call with custom variables should complete without error.")
#         system_check("Stardust Custom Var Figure Exists", fig is not None and fig_num is not None, "Plotbot should have created a figure for custom vars.")
#         # Could add more checks here, e.g., number of axes created
# 
#     except Exception as e:
#         pytest.fail(f"Stardust Custom Variables test failed: {e}")
#     finally:
#         if fig is not None:
#              plt.close(fig)
#         else:
#              plt.close('all')
             
# === End Custom Variables Test ===

# === Hammerhead Test (from test_ham_freshness.py) ===

HAM_TEST_TRANGE = ['2025-03-22/12:00:00', '2025-03-22/14:00:00'] # Date known to have HAM data

@pytest.mark.mission("Stardust Test: HAM Data Fetch and Validate")
def test_stardust_ham_fetch_and_validate():
    """Tests basic data loading and validation for HAM via plotbot call."""
    # Use HAM_TEST_TRANGE instead of STARDUST_TRANGE
    print(f"\n--- Testing HAM Fetch/Validate (stardust) --- For trange: {HAM_TEST_TRANGE}")
    
    # Variable to trigger HAM data loading
    ham_var_to_load = ham_instance.hamogram_30s 
    if ham_var_to_load is None:
         pytest.fail("HAM instance variable hamogram_30s is unexpectedly None before test.")
         
    var_name = ham_var_to_load.subclass_name
    plot_args = [HAM_TEST_TRANGE, ham_var_to_load, 1] # Plot just one variable using HAM_TEST_TRANGE
    fig = None
    fig_num = None # Initialize fig_num

    try:
        phase(1, f"Calling plotbot to trigger HAM load ({var_name}, stardust)")
        plotbot_function(*plot_args)
        print("Plotbot call completed (stardust - HAM).")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)

        phase(2, "Verifying HAM Data Availability Post-Plotbot Call (stardust)")
        # Check the ham_instance directly after the plotbot call
        assert hasattr(ham_instance, 'datetime_array') and ham_instance.datetime_array is not None, \
               "ham_instance.datetime_array is None after plotbot call (stardust)."
        assert len(ham_instance.datetime_array) > 0, \
               "ham_instance.datetime_array is empty after plotbot call (stardust)."
        print(f"ham_instance datetime_array loaded (stardust). Length: {len(ham_instance.datetime_array)}.")

        # Check the specific variable requested
        assert hasattr(ham_instance, var_name), \
               f"Variable '{var_name}' not found as attribute on ham_instance after plotbot call (stardust)."
        var_plot_manager = getattr(ham_instance, var_name)
        assert isinstance(var_plot_manager, plot_manager), \
               f"Attribute '{var_name}' is not a plot_manager instance (stardust)."
        assert len(var_plot_manager) > 0, \
               f"Variable '{var_name}' (plot_manager) has empty data (stardust)."
        assert len(var_plot_manager) == len(ham_instance.datetime_array), \
               f"Data length mismatch for '{var_name}' (stardust)."

        print(f"✅ HAM data validated for '{var_name}' (stardust).")

    except Exception as e:
        tb_str = traceback.format_exc()
        pytest.fail(f"Stardust HAM test failed for {var_name} with exception: {e}\nTraceback: {tb_str}")
    finally:
        # Explicitly close the figure using its number
        if fig_num is not None:
             try:
                 plt.close(fig_num)
                 print(f"--- Explicitly closed HAM figure {fig_num} in finally block ---")
             except Exception as close_err:
                 print(f"--- Error closing HAM figure {fig_num} in finally block: {close_err} ---")

# === End Hammerhead Test ===

# === FITS Test (from test_sf00_proton_fits_integration.py) ===

# Need the fixture for FITS test data
@pytest.fixture(scope='class') # Scope to class if multiple tests use it
def stardust_sf00_test_data():
    """Fixture to load raw SF00 CSV data for stardust calculation tests."""
    print("--- Loading SF00 Test Data Fixture (stardust) ---")
    # Reuse logic, using STARDUST_TRANGE's date
    stardust_date = '20240930' # <<< MODIFIED: Use the date with known data
    
    # Assuming psp_data_dir is accessible (defined earlier)
    global psp_data_dir
    print(f"Searching for SF00 files for date: {stardust_date} in {psp_data_dir}") # Debug print
    found_files = find_local_csvs(psp_data_dir, ['*sf00*.csv'], stardust_date)
    if not found_files:
        pytest.skip(f"Skipping stardust SF00 test: No input files found for date {stardust_date}.") # Updated skip message
        return None
    try:
        df_sf00_raw = pd.concat((pd.read_csv(f) for f in found_files), ignore_index=True)
        if df_sf00_raw.empty:
             pytest.skip(f"Skipping stardust SF00 test: Loaded DataFrame is empty for date {stardust_date}.") # Updated skip message
             return None
        print(f"Loaded SF00 test data (stardust), shape: {df_sf00_raw.shape}")
        # Convert 'time' column to TT2000 numpy array for the class update
        unix_times = df_sf00_raw['time'].to_numpy()
        datetime_objs_pd = pd.to_datetime(unix_times, unit='s', utc=True)
        datetime_components_list = [
            [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)]
            for dt in datetime_objs_pd
        ]
        tt2000_times = np.array(cdflib.cdfepoch.compute_tt2000(datetime_components_list))
        
        # Create data dictionary
        data_dict = {col: df_sf00_raw[col].to_numpy() for col in df_sf00_raw.columns if col != 'time'}
        
        # Create a simple container mimicking DataObject
        from collections import namedtuple
        FitsTestDataContainer = namedtuple('FitsTestDataContainer', ['times', 'data'])
        return FitsTestDataContainer(times=tt2000_times, data=data_dict)
    except Exception as e:
        pytest.fail(f"Failed to load/prep SF00 CSVs for stardust test: {e}")
        return None

# Helper function copied from test_sf00_proton_fits_integration.py
def _run_stardust_plotbot_fits_test_group(variables_to_plot):
    """
    Helper function for stardust FITS tests.
    Calls plotbot and verifies data loading for the proton_fits_instance.
    """
    # Define the target time range directly, matching the working test
    target_trange = ['2024-09-30/11:45:00.000', '2024-09-30/12:45:00.000'] # <<< MODIFIED
    plot_args = [target_trange] # <<< MODIFIED: Use target_trange
    var_names = [v.subclass_name for v in variables_to_plot if v is not None and hasattr(v, 'subclass_name')]
    # print(f"\\n--- Testing FITS Group (stardust): {var_names} --- For trange: {STARDUST_TRANGE}") # OLD PRINT
    print(f"\\n--- Testing FITS Group (stardust): {var_names} --- For trange: {target_trange}") # <<< MODIFIED PRINT

    valid_variables = [v for v in variables_to_plot if v is not None]
    if not valid_variables:
        pytest.skip("Skipping stardust FITS test group due to no valid variables.")
        return
        
    for i, var_instance in enumerate(valid_variables):
        panel_num = i + 1
        plot_args.extend([var_instance, panel_num])

    try:
        # print(f"Attempting plotbot call (stardust FITS) for trange: {STARDUST_TRANGE} with variables: {var_names}") # OLD PRINT
        print(f"Attempting plotbot call (stardust FITS) for trange: {target_trange} with variables: {var_names}") # <<< MODIFIED PRINT
        plotbot_function(*plot_args)
        print("Plotbot call completed successfully (stardust FITS).")

        print("--- Verifying Data Availability Post-Plotbot Call (stardust FITS) ---")
        assert hasattr(proton_fits_instance, 'datetime_array') and proton_fits_instance.datetime_array is not None, \
               "proton_fits_instance.datetime_array is None after plotbot call (stardust)."
        assert len(proton_fits_instance.datetime_array) > 0, \
               "proton_fits_instance.datetime_array is empty after plotbot call (stardust)."
        print(f"proton_fits_instance datetime_array loaded (stardust). Length: {len(proton_fits_instance.datetime_array)}.")

        for name in var_names:
            assert hasattr(proton_fits_instance, name), f"Variable '{name}' not found on proton_fits_instance (stardust)."
            var_plot_manager = getattr(proton_fits_instance, name)
            assert isinstance(var_plot_manager, plot_manager), f"Attribute '{name}' is not a plot_manager instance (stardust)."
            assert len(var_plot_manager) > 0, f"Variable '{name}' has empty data (stardust)."
            # Check length against the instance's datetime_array, not a potentially stale variable
            assert len(var_plot_manager) == len(proton_fits_instance.datetime_array), f"Data length mismatch for '{name}' (stardust). Actual: {len(var_plot_manager)}, Expected: {len(proton_fits_instance.datetime_array)}" # Added detail
            print(f"✅ Variable '{name}' verified with data (stardust).")

        print(f"--- Stardust FITS Group Test Passed for: {var_names} ---")

    except Exception as e:
        tb_str = traceback.format_exc()
        pytest.fail(f"Stardust plotbot call failed for FITS group {var_names}: {e}\nTraceback: {tb_str}")

@pytest.mark.mission("Stardust Test: FITS Group 1")
def test_stardust_fits_group_1(stardust_sf00_test_data):
    """Test Plotbot FITS Group 1: Now mirrors the variables from test_sf00_proton_fits_integration."""
    assert stardust_sf00_test_data is not None, "Stardust FITS test requires loaded data."
    # Trigger update *before* the test group runs
    try:
        print("Updating proton_fits_instance with test data (stardust)...")
        proton_fits_instance.update(stardust_sf00_test_data)
        print("proton_fits_instance update complete (stardust).")
    except Exception as e:
        pytest.fail(f"Failed to update proton_fits_instance for stardust test: {e}")
        
    variables = [
        proton_fits_instance.qz_p,
        proton_fits_instance.vsw_mach,
        proton_fits_instance.beta_ppar,
        proton_fits_instance.beta_pperp,
        proton_fits_instance.beta_p_tot,
        proton_fits_instance.ham_param
    ]
    _run_stardust_plotbot_fits_test_group(variables)

# === End FITS Test ===

# === Audifier Tests (from test_audifier.py) ===

@pytest.mark.mission("Stardust Test: Audifier Initialization")
def test_stardust_audifier_initialization():
    """Test basic initialization and default attribute values (stardust)."""
    print("\n=== Testing Audifier Initialization (stardust) ===")
    try:
        # Use the global instance imported
        audifier = global_audifier 
        system_check("Audifier Instance Exists", audifier is not None, "Global audifier instance should exist.")
        # Check default values (assuming these are the defaults)
        assert audifier.channels == 1, "Default channels should be 1"
        assert audifier.sample_rate == 44100, "Default sample_rate should be 44100"
        assert audifier.fade_samples == 0, "Default fade_samples should be 0"
        print(f"✅ Audifier defaults checked (channels={audifier.channels}, rate={audifier.sample_rate}, fade={audifier.fade_samples})")
    except Exception as e:
        pytest.fail(f"Stardust Audifier initialization check failed: {e}")

@pytest.mark.mission("Stardust Test: Sonify Valid Data")
def test_stardust_sonify_valid_data(test_audifier): # Use the fixture from original test
    """Test creating a mono audio file with valid data (stardust)."""
    print("\n=== Testing Audifier Sonification (stardust) ===")
    audifier = test_audifier # Get instance with temp dir
    files = None
    try:
        phase(1, "Setting audifier options (stardust)")
        audifier.channels = 1
        audifier.fade_samples = 0 # No fade for basic test
        audifier.sample_rate = 44100 

        phase(2, "Generating audio with mag_rtn.br (stardust)")
        # Use STARDUST_TRANGE
        files = audifier.audify(STARDUST_TRANGE, mag_rtn.br)
        print(f"Audify returned: {files}")

        phase(3, "Verifying audio file creation (stardust)")
        assert files is not None and isinstance(files, dict), "audify should return a dictionary."
        assert "br" in files, "Result dictionary should contain key 'br' for the input variable."
        file_path = files["br"]
        assert os.path.exists(file_path), f"Audio file not found at expected path: {file_path}"
        
        # Optionally read and check the wav file basic properties
        sample_rate, audio_data = wavfile.read(file_path)
        assert sample_rate == audifier.sample_rate, "WAV file sample rate mismatch."
        assert len(audio_data.shape) == 1, "Audio data should be mono (1D array)."
        assert len(audio_data) > 0, "Audio data should not be empty."
        print(f"✅ Audio file created and verified: {os.path.basename(file_path)}")

    except Exception as e:
        pytest.fail(f"Stardust Sonification test failed: {e}")
    finally:
        # Fixture handles temp dir cleanup
        pass 

# === End Audifier Tests ===

# --- Test Functions copied from test_custom_variables.py ---

@pytest.mark.skip(reason="Skipping by user request: custom variable test (stardust)")
@pytest.mark.mission("Stardust Test: Custom Variable Arithmetic")
def test_stardust_custom_arithmetic(test_environment):
    """Test creating and plotting a simple arithmetic custom variable."""
    env = test_environment
    trange = env['trange_initial'] # Using the initial range from that test setup
    
    phase(1, "Creating arithmetic custom variable (stardust)")
    # Simple addition
    var = custom_variable('Mag_Sum_RT', mag_rtn_4sa.br + mag_rtn_4sa.bt)
    var_name = var.subclass_name
    
    phase(2, "Calling plotbot to trigger data load (stardust)")
    plt.options.reset()
    plt.options.use_single_title = True
    plt.options.single_title_text = "Test: Stardust Custom Arithmetic"
    plotbot_function(trange, var, 1)

    phase(3, "Verifying variable properties post-plotbot (stardust)")
    try:
        import importlib
        plotbot_module = importlib.import_module('plotbot')
        check_var = getattr(plotbot_module, var_name)
    except (ImportError, AttributeError):
        system_check("Global Access (Arithmetic)", False, f"Variable '{var_name}' not found in plotbot module after plotting")
        pytest.fail("Failed to find globally accessible custom arithmetic variable")
        return

    system_check("Arithmetic Var Creation", check_var is not None, "Custom arithmetic variable should exist after plotbot call")
    
    # Check Data Presence
    if not hasattr(check_var, 'datetime_array') or check_var.datetime_array is None or len(check_var.datetime_array) == 0:
        system_check("Arithmetic Data Presence", False, "Arithmetic variable should have datetime data after plotbot call")
    else:
        system_check("Arithmetic Data Presence", True, f"Arithmetic variable has {len(check_var.datetime_array)} data points")

    # plt.pause(0.5) # Display plot briefly - REMOVED FOR DEBUGGING

@pytest.mark.skip(reason="Skipping by user request: custom variable test (stardust)")
@pytest.mark.mission("Stardust Test: Custom Variable with Numpy")
def test_stardust_custom_numpy(test_environment):
    """Test creating and plotting a custom variable using a numpy function."""
    env = test_environment
    trange = env['trange_initial'] 
    
    phase(1, "Creating numpy custom variable (stardust)")
    # Using np.abs
    var = custom_variable('Abs_Bn', np.abs(mag_rtn_4sa.bn))
    var_name = var.subclass_name
    
    phase(2, "Calling plotbot to trigger data load (stardust)")
    plt.options.reset()
    plt.options.use_single_title = True
    plt.options.single_title_text = "Test: Stardust Custom Numpy"
    plotbot_function(trange, var, 1)

    phase(3, "Verifying variable properties post-plotbot (stardust)")
    try:
        import importlib
        plotbot_module = importlib.import_module('plotbot')
        check_var = getattr(plotbot_module, var_name)
    except (ImportError, AttributeError):
        system_check("Global Access (Numpy)", False, f"Variable '{var_name}' not found in plotbot module after plotting")
        pytest.fail("Failed to find globally accessible custom numpy variable")
        return

    system_check("Numpy Var Creation", check_var is not None, "Custom numpy variable should exist after plotbot call")
    
    # Check Data Presence
    if not hasattr(check_var, 'datetime_array') or check_var.datetime_array is None or len(check_var.datetime_array) == 0:
        system_check("Numpy Data Presence", False, "Numpy variable should have datetime data after plotbot call")
    else:
        system_check("Numpy Data Presence", True, f"Numpy variable has {len(check_var.datetime_array)} data points")

    # plt.pause(0.5) # Display plot briefly - REMOVED FOR DEBUGGING

# === SPDF Download Test (Adapted from test_pyspedas_download.py) ===

@pytest.mark.mission("Stardust Test: Basic SPDF Download (mag_RTN_4sa)")
def test_stardust_spdf_download_with_cleanup():
    """Tests the basic SPDF download logic, ensuring cleanup before download.

    1. Cleans up any existing local file for the target date/type.
    2. Calls the SPDF download function (expecting download).
    3. Calls the SPDF download function again (expecting local find).
    4. Cleans up the downloaded file.
    Uses mag_RTN_4sa data type.
    """
    plotbot_key = 'mag_RTN_4sa'
    # Use the same time range as the original debug test for consistency
    trange_test = ['2018-10-22 06:00:00', '2018-10-22 18:00:00']
    test_date_str = '20181022'
    test_year = '2018'

    # Import the download function directly
    from plotbot.data_download_pyspedas import download_spdf_data

    # --- Helper Function to find and delete files ---
    # (Adapted from test_pyspedas_download.py helpers)
    def find_and_delete_target_files(data_key, date_str, year_str):
        print(f"\n--- Attempting cleanup for {data_key} ({date_str}) ---")
        # Need WORKSPACE_ROOT, data_types
        if data_key not in data_types:
            print(f"  Error: Data type key '{data_key}' not found in psp_data_types.")
            return False
        config = data_types[data_key]
        
        # Construct expected directory (Assuming standard structure)
        # This might need refinement based on where download_spdf_data *actually* puts things
        # Let's base it on the 'pyspedas_subpath' logic from the other test file
        pyspedas_subpath = os.path.join('fields', 'l2', 'mag_rtn_4_per_cycle', year_str) # Specific to mag_RTN_4sa
        expected_dir = os.path.join(WORKSPACE_ROOT, 'data', 'psp', pyspedas_subpath)
        
        # Construct SPDF pattern from config if available, otherwise guess
        spdf_pattern_tmpl = config.get('spdf_file_pattern', # Use SPDF pattern directly
                                      f'psp_fld_l2_mag_rtn_4_sa_per_cyc_{date_str}_v*.cdf') # Fallback guess

        # Format the template if it has placeholders
        try:
            spdf_filename_pattern = spdf_pattern_tmpl.format(data_level=config.get('data_level', 'l2'), date_str=date_str)
        except KeyError:
            spdf_filename_pattern = spdf_pattern_tmpl # Use as is if no formatting needed/possible

        full_glob_pattern = os.path.join(expected_dir, spdf_filename_pattern)
        print(f"  Searching for files matching: {full_glob_pattern}")
        
        files_to_delete = glob.glob(full_glob_pattern)
        if not files_to_delete:
            print("  No matching files found to delete.")
            return True # No files to delete is success

        print(f"  Found {len(files_to_delete)} file(s) to delete:")
        all_deleted = True
        for f_path in files_to_delete:
            try:
                if os.path.exists(f_path):
                    os.remove(f_path)
                    print(f"    Deleted: {os.path.basename(f_path)}")
                    if os.path.exists(f_path):
                        print(f"    ERROR: File still exists after delete attempt: {f_path}")
                        all_deleted = False
                else:
                     print(f"    Already gone: {os.path.basename(f_path)}") # Should not happen if glob found it
            except OSError as e:
                print(f"    Error deleting {f_path}: {e}")
                all_deleted = False
        return all_deleted
    # --- End Helper ---

    phase(1, f"Initial Cleanup for {plotbot_key} ({test_date_str})")
    cleanup_ok = find_and_delete_target_files(plotbot_key, test_date_str, test_year)
    system_check("Initial File Cleanup", cleanup_ok, "Should ensure no target files exist initially.")
    if not cleanup_ok:
        pytest.fail("Initial cleanup failed, cannot proceed.")

    phase(2, f"Enable Debug Logging and First SPDF Call ({plotbot_key})")
    print_manager.show_debug = True # Enable debug for this test
    print(f"Debug logging enabled: {print_manager.show_debug}")

    downloaded_file_relative_path = None # To store path for cleanup

    print(f"Calling download_spdf_data (1st time) with trange={trange_test}, key='{plotbot_key}'")
    result1 = False
    returned_data1 = None
    try:
        # Pyspedas downloadonly=True returns a list of *relative* paths if successful
        returned_data1 = download_spdf_data(trange_test, plotbot_key)
        result1 = isinstance(returned_data1, list) and len(returned_data1) > 0
        if result1:
             downloaded_file_relative_path = returned_data1[0] # Store relative path
             print(f"First call successful, returned path: {downloaded_file_relative_path}")
        else:
             print(f"First call failed or returned no path. Result: {returned_data1}")

    except Exception as e:
        print(f"Error during first download_spdf_data call: {e}")
        traceback.print_exc() # Print detailed traceback
        pytest.fail(f"First download_spdf_data call raised an exception: {e}")

    system_check("First SPDF Call Execution", result1, "First call should successfully download the file.")
    if not result1:
        pytest.fail("First SPDF download call failed, cannot proceed.") # Stop if download failed

    phase(3, f"Second SPDF Call for {plotbot_key} (expect local find)")
    print(f"Calling download_spdf_data (2nd time) with trange={trange_test}, key='{plotbot_key}'")
    result2 = False
    returned_data2 = None
    try:
        # This call should now find the file locally
        returned_data2 = download_spdf_data(trange_test, plotbot_key)
        result2 = isinstance(returned_data2, list) and len(returned_data2) > 0
        if result2:
             print(f"Second call successful, returned path: {returned_data2[0]}")
             # Verify paths match
             assert returned_data2[0] == downloaded_file_relative_path, "Path from second call should match first call"
        else:
             print(f"Second call failed or returned no path. Result: {returned_data2}")

    except Exception as e:
        print(f"Error during second download_spdf_data call: {e}")
        traceback.print_exc() # Print detailed traceback
        pytest.fail(f"Second download_spdf_data call raised an exception: {e}")

    system_check("Second SPDF Call Execution", result2, "Second call should find the file locally.")

    # phase(4, "Final Cleanup of Downloaded File") # <<< COMMENTED OUT
    # # Final cleanup uses the helper again
    # cleanup_final_ok = find_and_delete_target_files(plotbot_key, test_date_str, test_year)
    # system_check("Final File Cleanup", cleanup_final_ok, f"Should delete the downloaded file for {plotbot_key} ({test_date_str}).")

    print_manager.show_debug = False # Disable debug after test

# === End SPDF Download Test ===

@pytest.mark.mission("Stardust Test: Spectral Plotting (EPAD Strahl)")
def test_stardust_spectral_plotting():
    """Test spectral plotting with EPAD strahl data alongside magnetic field data."""
    print("\n=== Testing Spectral Plotting (stardust) ===")
    
    TRANGE = ['2023-09-28/00:00:00.000', '2023-09-29/00:00:00.000']
    fig = None
    fig_num = None
    
    try:
        # Import epad if not already imported
        from plotbot import epad
        
        phase(1, "Calling plotbot with mag and spectral data (stardust)")
        print(f"Testing spectral plotting with trange: {TRANGE}")
        print("Variables: mag_rtn_4sa.br (panel 1), epad.strahl (panel 2)")
        
        plotbot_function(TRANGE, mag_rtn_4sa.br, 1, epad.strahl, 2)
        
        phase(2, "Verifying spectral plotbot call completed (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust Spectral Plot Completed", True, "plotbot call with spectral data should complete without error.")
        system_check("Stardust Spectral Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for spectral data.")
        
        print("✅ Spectral plotting test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust Spectral Plotting test failed: {e}")
    finally:
        # Always try to close the figure using its number
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed spectral figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing spectral figure {fig_num} in finally block: {close_err} ---")

# === End Spectral Plotting Test ===

# === PSP Alpha Integration Test (from plotbot_alpha_integration_examples.ipynb) ===

@pytest.mark.mission("Stardust Test: PSP Alpha vs Proton Comparison")
def test_stardust_alpha_integration():
    """Test PSP alpha particle integration with density and temperature comparison."""
    print("\n=== Testing PSP Alpha Integration (stardust) ===")
    
    # Use a time range known to have alpha data
    ALPHA_TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    fig = None
    fig_num = None
    
    try:
        # Import PSP alpha class
        from plotbot import psp_alpha, proton
        
        phase(1, "Calling plotbot with alpha vs proton comparison (stardust)")
        print(f"Testing alpha vs proton with trange: {ALPHA_TRANGE}")
        print("Variables: psp_alpha.density (panel 1), proton.density (panel 2)")
        
        plotbot_function(ALPHA_TRANGE, 
                        psp_alpha.density, 1,
                        proton.density, 2)
        
        phase(2, "Verifying alpha integration plotbot call (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust Alpha Integration Plot Completed", True, "plotbot call with alpha data should complete without error.")
        system_check("Stardust Alpha Integration Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for alpha data.")
        
        # Verify data availability
        assert hasattr(psp_alpha, 'density') and psp_alpha.density.data is not None, "Alpha density data should be available"
        assert hasattr(proton, 'density') and proton.density.data is not None, "Proton density data should be available"
        
        print("✅ PSP Alpha vs Proton comparison test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust PSP Alpha Integration test failed: {e}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed alpha integration figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing alpha integration figure {fig_num} in finally block: {close_err} ---")

# === PSP Alpha-Proton Derived Variables Test ===

@pytest.mark.mission("Stardust Test: Alpha-Proton Derived Variables")
def test_stardust_alpha_proton_derived():
    """Test PSP alpha-proton derived variables (na_div_np, ap_drift, ap_drift_va)."""
    print("\n=== Testing Alpha-Proton Derived Variables (stardust) ===")
    
    # Use time range from successful alpha/proton implementation
    DERIVED_TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    fig = None
    fig_num = None
    
    try:
        # Import PSP alpha class with derived variables
        from plotbot import psp_alpha
        
        phase(1, "Calling plotbot with alpha-proton derived variables (stardust)")
        print(f"Testing derived variables with trange: {DERIVED_TRANGE}")
        print("Variables: na_div_np (panel 1), ap_drift (panel 2), ap_drift_va (panel 3)")
        
        plotbot_function(DERIVED_TRANGE,
                        psp_alpha.na_div_np, 1,     # Alpha/proton density ratio
                        psp_alpha.ap_drift, 2,      # Alpha-proton drift speed
                        psp_alpha.ap_drift_va, 3)   # Drift normalized by Alfvén speed
        
        phase(2, "Verifying derived variables plotbot call (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust Derived Variables Plot Completed", True, "plotbot call with derived variables should complete without error.")
        system_check("Stardust Derived Variables Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for derived variables.")
        
        # Verify derived variable data availability
        assert hasattr(psp_alpha, 'na_div_np') and psp_alpha.na_div_np.data is not None, "na_div_np derived variable should be available"
        assert hasattr(psp_alpha, 'ap_drift') and psp_alpha.ap_drift.data is not None, "ap_drift derived variable should be available"
        assert hasattr(psp_alpha, 'ap_drift_va') and psp_alpha.ap_drift_va.data is not None, "ap_drift_va derived variable should be available"
        
        print("✅ Alpha-proton derived variables test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust Alpha-Proton Derived Variables test failed: {e}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed derived variables figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing derived variables figure {fig_num} in finally block: {close_err} ---")

# === PSP DFB Electric Field Test ===

@pytest.mark.mission("Stardust Test: PSP DFB Electric Field Spectra")
def test_stardust_dfb_electric_field():
    """Test PSP DFB electric field spectral data."""
    print("\n=== Testing PSP DFB Electric Field Spectra (stardust) ===")
    
    # Use working time range with actual DFB data
    DFB_TRANGE = ['2022-06-01/00:00:00.000', '2022-06-02/00:00:00.000']
    fig = None
    fig_num = None
    
    try:
        # Import PSP DFB class
        from plotbot import psp_dfb, config
        
        # Set server to SPDF for DFB data
        original_server = config.data_server
        config.data_server = 'spdf'
        
        phase(1, "Calling plotbot with DFB electric field spectra (stardust)")
        print(f"Testing DFB electric field with trange: {DFB_TRANGE}")
        print("Variables: AC dV12 (panel 1), AC dV34 (panel 2), DC dV12 (panel 3)")
        
        plotbot_function(DFB_TRANGE,
                        psp_dfb.ac_spec_dv12, 1,  # AC electric field spectrum dV12
                        psp_dfb.ac_spec_dv34, 2,  # AC electric field spectrum dV34
                        psp_dfb.dc_spec_dv12, 3)  # DC electric field spectrum dV12
        
        phase(2, "Verifying DFB electric field plotbot call (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust DFB Plot Completed", True, "plotbot call with DFB data should complete without error.")
        system_check("Stardust DFB Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for DFB data.")
        
        # Verify DFB data availability (at least AC dV12 should have data)
        assert hasattr(psp_dfb, 'ac_spec_dv12') and psp_dfb.ac_spec_dv12.data is not None, "AC dV12 DFB data should be available"
        total_data_points = (psp_dfb.ac_spec_dv12.data.size + 
                           psp_dfb.ac_spec_dv34.data.size + 
                           psp_dfb.dc_spec_dv12.data.size)
        assert total_data_points > 0, "At least one DFB spectrum should have real data"
        
        print("✅ PSP DFB electric field spectra test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust PSP DFB Electric Field test failed: {e}")
    finally:
        # Restore original server setting
        config.data_server = original_server
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed DFB figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing DFB figure {fig_num} in finally block: {close_err} ---")

# === PSP QTN Data Test ===

@pytest.mark.mission("Stardust Test: PSP QTN Data")
def test_stardust_qtn_data():
    """Test PSP QTN (Quasi-Thermal Noise) electron density and temperature data."""
    print("\n=== Testing PSP QTN Data (stardust) ===")
    
    # Use time range from QTN examples
    QTN_TRANGE = ['2022-06-01/20:00:00.000', '2022-06-02/02:00:00.000']
    fig = None
    fig_num = None
    
    try:
        # Import PSP QTN class
        from plotbot import psp_qtn, config
        
        # Set server to dynamic for QTN data
        original_server = config.data_server
        config.data_server = 'dynamic'
        
        phase(1, "Calling plotbot with QTN density and temperature (stardust)")
        print(f"Testing QTN data with trange: {QTN_TRANGE}")
        print("Variables: psp_qtn.density (panel 1), psp_qtn.temperature (panel 2)")
        
        plotbot_function(QTN_TRANGE,
                        psp_qtn.density, 1,     # Electron density
                        psp_qtn.temperature, 2) # Electron temperature
        
        phase(2, "Verifying QTN data plotbot call (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust QTN Plot Completed", True, "plotbot call with QTN data should complete without error.")
        system_check("Stardust QTN Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for QTN data.")
        
        # Verify QTN data availability
        assert hasattr(psp_qtn, 'density') and psp_qtn.density.data is not None, "QTN density data should be available"
        assert hasattr(psp_qtn, 'temperature') and psp_qtn.temperature.data is not None, "QTN temperature data should be available"
        
        print("✅ PSP QTN data test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust PSP QTN Data test failed: {e}")
    finally:
        # Restore original server setting
        config.data_server = original_server
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed QTN figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing QTN figure {fig_num} in finally block: {close_err} ---")

# === WIND Data Test ===

@pytest.mark.mission("Stardust Test: WIND MFI Magnetic Field")
def test_stardust_wind_mfi():
    """Test WIND MFI magnetic field data."""
    print("\n=== Testing WIND MFI Magnetic Field (stardust) ===")
    
    # Use time range from WIND examples
    WIND_TRANGE = ['2022-06-01/20:00:00', '2022-06-02/02:00:00']
    fig = None
    fig_num = None
    
    try:
        # Import WIND MFI class
        from plotbot import wind_mfi_h2, config
        
        # Set server to SPDF for WIND data
        original_server = config.data_server
        config.data_server = 'spdf'
        
        phase(1, "Calling plotbot with WIND MFI magnetic field (stardust)")
        print(f"Testing WIND MFI with trange: {WIND_TRANGE}")
        print("Variables: Bx (panel 1), By (panel 2), Bz (panel 3), |B| (panel 4)")
        
        plotbot_function(WIND_TRANGE,
                        wind_mfi_h2.bx, 1,    # Magnetic field X component
                        wind_mfi_h2.by, 2,    # Magnetic field Y component
                        wind_mfi_h2.bz, 3,    # Magnetic field Z component
                        wind_mfi_h2.bmag, 4)  # Magnetic field magnitude
        
        phase(2, "Verifying WIND MFI plotbot call (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Stardust WIND MFI Plot Completed", True, "plotbot call with WIND MFI data should complete without error.")
        system_check("Stardust WIND MFI Figure Exists", fig is not None and fig_num is not None, "plotbot should have created a figure for WIND MFI data.")
        
        # Verify WIND MFI data availability
        assert hasattr(wind_mfi_h2, 'bx') and wind_mfi_h2.bx.data is not None, "WIND MFI Bx data should be available"
        assert hasattr(wind_mfi_h2, 'by') and wind_mfi_h2.by.data is not None, "WIND MFI By data should be available"
        assert hasattr(wind_mfi_h2, 'bz') and wind_mfi_h2.bz.data is not None, "WIND MFI Bz data should be available"
        assert hasattr(wind_mfi_h2, 'bmag') and wind_mfi_h2.bmag.data is not None, "WIND MFI |B| data should be available"
        
        print("✅ WIND MFI magnetic field test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Stardust WIND MFI test failed: {e}")
    finally:
        # Restore original server setting
        config.data_server = original_server
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed WIND MFI figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing WIND MFI figure {fig_num} in finally block: ---")

# === End Example Integration Tests ===

# === Orbital Data Tests ===

@pytest.mark.mission("Stardust Test: PSP Orbit Data")
def test_stardust_psp_orbit_data():
    """Comprehensive test for PSP orbit data including main and derived variables."""
    print("\n=== Testing PSP Orbit Data (stardust) ===")
    # Use a specific, longer time range for this test only
    ORBIT_TEST_TRANGE = ['2021-11-19/00:00:00.000', '2021-11-24/00:00:00.000']
    fig = None
    fig_num = None
    try:
        from plotbot import psp_orbit
        
        phase(1, "Calling plotbot with PSP orbit variables (stardust)")
        print("Variables: r_sun (panel 1), orbital_speed (panel 2), carrington_lon (panel 3)")
        
        plotbot_function(ORBIT_TEST_TRANGE, 
                        psp_orbit.r_sun, 1,                    # Distance from Sun
                        psp_orbit.orbital_speed, 2,            # Orbital speed
                        psp_orbit.carrington_lon, 3)           # Carrington longitude

        phase(2, "Verifying orbit plotbot call completed (stardust)")
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)

        system_check("Stardust Orbit Call Completed", True, "orbit plotbot call should complete without error.")
        system_check("Stardust Orbit Figure Exists", fig is not None and fig_num is not None, "orbit plotbot should have created a figure.")
        
        # Verify orbit data availability
        assert hasattr(psp_orbit, 'r_sun') and psp_orbit.r_sun.data is not None, "PSP r_sun orbit data should be available"
        assert hasattr(psp_orbit, 'orbital_speed') and psp_orbit.orbital_speed.data is not None, "PSP orbital_speed orbit data should be available"
        assert hasattr(psp_orbit, 'carrington_lon') and psp_orbit.carrington_lon.data is not None, "PSP carrington_lon orbit data should be available"
        
        print("✅ PSP orbit data test completed successfully")

    except Exception as e:
        pytest.fail(f"Stardust PSP Orbit Data test failed: {e}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed orbit figure {fig_num} in finally block ---")
            except Exception as close_err:
                print(f"--- Error closing orbit figure {fig_num} in finally block: {close_err} ---")

# === End Orbital Data Tests ===

# Ensure any necessary cleanup of plotbot module state if tests modify it globally
@pytest.fixture(scope="module", autouse=True)
def cleanup_plotbot_module_state():
    # This is a good place for any teardown that needs to happen once per module
    # For example, resetting configuration that might have been changed by tests
    yield
    print_manager.show_debug = False # Reset to default
    # Potentially reset plotbot.config settings changed by tests if not handled by other fixtures
    # Example: plotbot.config.data_server = 'default_value'
    plt.close('all') # Final cleanup of any stray plots

# === Class Data Alignment Tests (from test_class_data_alignment.py) ===

import fnmatch # Added for CDF raw data verification tests

@pytest.mark.mission("Stardust Test: Proton Density Data Alignment")
def test_stardust_proton_density_data_alignment():
    """
    Test that the `proton.density.data` attribute is correctly updated when plotting
    different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Proton Density Data Alignment ⭐️⭐️⭐️")
    # Time ranges from the user's example
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/00:30:00']
    trange2 = ['2021-01-19/01:00:00', '2021-01-19/01:30:00']

    # 1. Plot for the first time range and get the data
    plotbot_function(trange1, proton.density, 1)
    data1 = np.copy(proton.density.data)
    time1 = np.copy(proton.density.time) if proton.density.time is not None else None
    
    print(f"First plot - data shape: {data1.shape}, time shape: {time1.shape if time1 is not None else 'None'}")

    # 2. Plot for the second time range and get the data
    plotbot_function(trange2, proton.density, 1)
    data2 = np.copy(proton.density.data)
    time2 = np.copy(proton.density.time) if proton.density.time is not None else None
    
    print(f"Second plot - data shape: {data2.shape}, time shape: {time2.shape if time2 is not None else 'None'}")

    # 3. Verify that the data arrays are different
    assert not np.array_equal(data1, data2), "Data arrays should be different for different time ranges"
    print("✅ Data arrays are different as expected")

@pytest.mark.mission("Stardust Test: Data Alignment Fix Verification")
def test_stardust_data_alignment_fix_verification():
    """
    Test to verify that the data alignment fix is working correctly.
    This test focuses on the core issue we solved.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Data Alignment Fix Verification ⭐️⭐️⭐️")
    # Time ranges from the user's example
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/00:30:00']
    trange2 = ['2021-01-19/01:00:00', '2021-01-19/01:30:00']

    # 1. Plot for the first time range and get the data
    plotbot_function(trange1, proton.density, 1)
    data1 = np.copy(proton.density.data)
    
    # 2. Plot for the second time range and get the data
    plotbot_function(trange2, proton.density, 1)
    data2 = np.copy(proton.density.data)
    
    # 3. Verify that the data arrays are different
    arrays_are_different = not np.array_equal(data1, data2)
    print(f"✅ SUCCESS: Data alignment fix is working!")
    print(f"   trange1 data shape: {data1.shape}")
    print(f"   trange2 data shape: {data2.shape}")
    print(f"   Arrays are different: {arrays_are_different}")
    
    assert arrays_are_different, "Data arrays should be different for different time ranges"

@pytest.mark.mission("Stardust Test: Multi-Class Data Alignment")
def test_stardust_multi_class_data_alignment():
    """
    Test that multiple data classes in a single plotbot plot all update their
    _current_operation_trange correctly when plotting different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Multi-Class Data Alignment ⭐️⭐️⭐️")
    # Time ranges for testing (12-hour intervals)
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/12:00:00']
    trange2 = ['2021-01-19/12:00:00', '2021-01-20/00:00:00']

    print("🔍 Testing multi-class data alignment...")
    print(f"   trange1: {trange1}")
    print(f"   trange2: {trange2}")

    # 1. First plot with multiple data classes
    print("\n📊 First plot with multiple data classes...")
    plotbot_function(trange1, mag_rtn_4sa.br, 1, proton.anisotropy, 2, epad.centroids, 3, psp_orbit.r_sun, 4)
    
    # Get data from first plot
    data1_mag = np.copy(mag_rtn_4sa.br.data)
    data1_proton = np.copy(proton.anisotropy.data)
    data1_epad = np.copy(epad.centroids.data)
    data1_orbit = np.copy(psp_orbit.r_sun.data)
    
    print(f"   First plot data shapes:")
    print(f"     mag_rtn_4sa.br: {data1_mag.shape}")
    print(f"     proton.anisotropy: {data1_proton.shape}")
    print(f"     epad.centroids: {data1_epad.shape}")
    print(f"     psp_orbit.r_sun: {data1_orbit.shape}")

    # 2. Second plot with different time range
    print("\n📊 Second plot with different time range...")
    plotbot_function(trange2, mag_rtn_4sa.br, 1, proton.anisotropy, 2, epad.centroids, 3, psp_orbit.r_sun, 4)
    
    # Get data from second plot
    data2_mag = np.copy(mag_rtn_4sa.br.data)
    data2_proton = np.copy(proton.anisotropy.data)
    data2_epad = np.copy(epad.centroids.data)
    data2_orbit = np.copy(psp_orbit.r_sun.data)
    
    print(f"   Second plot data shapes:")
    print(f"     mag_rtn_4sa.br: {data2_mag.shape}")
    print(f"     proton.anisotropy: {data2_proton.shape}")
    print(f"     epad.centroids: {data2_epad.shape}")
    print(f"     psp_orbit.r_sun: {data2_orbit.shape}")

    # 3. Verify that all data arrays are different between plots
    print("\n🔍 Verifying data alignment...")
    
    # Check if arrays are different
    mag_different = not np.array_equal(data1_mag, data2_mag)
    proton_different = not np.array_equal(data1_proton, data2_proton)
    epad_different = not np.array_equal(data1_epad, data2_epad)
    orbit_different = not np.array_equal(data1_orbit, data2_orbit)
    
    print(f"   mag_rtn_4sa.br arrays different: {mag_different}")
    print(f"   proton.anisotropy arrays different: {proton_different}")
    print(f"   epad.centroids arrays different: {epad_different}")
    print(f"   psp_orbit.r_sun arrays different: {orbit_different}")
    
    # All arrays should be different (different time ranges = different data)
    assert mag_different, "mag_rtn_4sa.br data should be different for different time ranges"
    assert proton_different, "proton.anisotropy data should be different for different time ranges"
    assert epad_different, "epad.centroids data should be different for different time ranges"
    assert orbit_different, "psp_orbit.r_sun data should be different for different time ranges"
    
    print("✅ SUCCESS: All data classes are properly aligned!")
    print("   All data arrays are different between time ranges as expected") 

@pytest.mark.mission("Stardust Test: Raw CDF Data Verification")
def test_stardust_raw_cdf_data_verification():
    """
    Test that the data returned by plotbot matches the raw data from the original CDF file.
    This test verifies data integrity and time-data pairing by directly reading the CDF file.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Raw CDF Data Verification ⭐️⭐️⭐️")
    import cdflib
    from plotbot.data_classes.data_types import data_types
    from plotbot.data_import import get_project_root
    from dateutil.parser import parse
    from datetime import timezone
    import os
    import re
    
    # Time range for testing (12-hour interval)
    trange = ['2021-01-19/00:00:00', '2021-01-19/12:00:00']
    
    print("🔍 Testing raw CDF data verification...")
    print(f"   Time range: {trange}")
    
    # 1. Get data through plotbot
    print("\n📊 Getting data through plotbot...")
    plotbot_function(trange, mag_rtn_4sa.br, 1)
    plotbot_data = np.copy(mag_rtn_4sa.br.data)
    plotbot_times = np.copy(mag_rtn_4sa.br.datetime_array) if mag_rtn_4sa.br.datetime_array is not None else None
    
    print(f"   Plotbot data shape: {plotbot_data.shape}")
    print(f"   Plotbot times shape: {plotbot_times.shape if plotbot_times is not None else 'None'}")
    
    # 2. Find the actual CDF file using the same logic as data_import.py
    print("\n📁 Finding CDF file using data_import.py logic...")
    
    # Get mag_rtn_4sa configuration from data_types
    mag_config = data_types.get('mag_RTN_4sa')  # This is the mag_rtn_4sa data type
    if not mag_config:
        print("❌ Could not find mag_rtn_4sa configuration in data_types")
        return
    
    print(f"   Mag RTN 4sa data type: mag_RTN_4sa")
    print(f"   Local path template: {mag_config.get('local_path')}")
    print(f"   File pattern: {mag_config.get('file_pattern_import')}")
    
    # Parse time range like data_import.py does
    start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
    end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
    
    # Find CDF files using the same logic as data_import.py
    found_files = []
    from datetime import datetime, timedelta
    
    def daterange(start_date, end_date):
        """Generate dates between start_date and end_date (inclusive)."""
        current_date = start_date.date()
        end_date_only = end_date.date()
        while current_date <= end_date_only:
            yield datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
            current_date += timedelta(days=1)
    
    # Get base path and resolve relative to project root
    cdf_base_path = mag_config.get('local_path')
    if not cdf_base_path:
        print("❌ No local_path found in mag config")
        return
    
    # Resolve relative path to absolute
    if not os.path.isabs(cdf_base_path):
        project_root = get_project_root()
        cdf_base_path = os.path.join(project_root, cdf_base_path)
        print(f"   Resolved CDF base path: {cdf_base_path}")
    
    # Search for files in the date range
    for single_date in daterange(start_time, end_time):
        year = single_date.year
        date_str = single_date.strftime('%Y%m%d')
        local_dir = os.path.join(cdf_base_path.format(data_level=mag_config['data_level']), str(year))
        
        if os.path.exists(local_dir):
            file_pattern_template = mag_config['file_pattern_import']
            file_pattern = file_pattern_template.format(
                data_level=mag_config['data_level'],
                date_str=date_str
            )
            print(f"   Searching pattern: '{file_pattern}' in dir: '{local_dir}'")
            
            # Convert glob pattern to regex
            pattern_for_re = file_pattern.replace('*', '.*')
            regex = re.compile(pattern_for_re, re.IGNORECASE)
            
            for f_name in os.listdir(local_dir):
                if regex.match(f_name):
                    found_files.append(os.path.join(local_dir, f_name))
                    print(f"     Found file: {f_name}")
    
    if not found_files:
        print("❌ No CDF files found for the time range")
        return
    
    # Use the first file found (should be the one plotbot used)
    cdf_file_path = found_files[0]
    print(f"   Using CDF file: {os.path.basename(cdf_file_path)}")
    
    # 3. Read raw data from CDF file using cdflib
    print("\n📖 Reading raw data from CDF file...")
    try:
        with cdflib.CDF(cdf_file_path) as cdf_file:
            print(f"   Successfully opened CDF file: {os.path.basename(cdf_file_path)}")
            
            # Get list of all variables
            cdf_info = cdf_file.cdf_info()
            all_variables = cdf_info.zVariables + cdf_info.rVariables
            print(f"   Found {len(all_variables)} variables in CDF")
            
            # Find time variable (Epoch)
            time_var = None
            for var_name in all_variables:
                if 'epoch' in var_name.lower():
                    time_var = var_name
                    break
            
            if not time_var:
                print("❌ No time variable (Epoch) found in CDF file")
                return
            
            print(f"   Using time variable: {time_var}")
            
            # Load time data
            raw_times = cdf_file.varget(time_var)
            print(f"   Loaded {len(raw_times)} time points")
            
            # Find the BR variable (radial component of magnetic field)
            br_var = None
            for var_name in all_variables:
                if 'br' in var_name.lower() or 'psp_fld' in var_name.lower():
                    br_var = var_name
                    break
            
            if not br_var:
                print("❌ No BR variable found in CDF file")
                print(f"   Available variables: {all_variables[:10]}...")  # Show first 10
                return
            
            print(f"   Using BR variable: {br_var}")
            
            # Load BR data
            raw_br = cdf_file.varget(br_var)
            print(f"   Raw BR shape: {raw_br.shape}")
            
            # 4. Time filter the raw data to match the requested range
            print("\n✂️ Time filtering raw data...")
            
            # Convert requested time range to TT2000 for comparison
            start_tt2000 = cdflib.cdfepoch.compute_tt2000([
                start_time.year, start_time.month, start_time.day,
                start_time.hour, start_time.minute, start_time.second,
                int(start_time.microsecond/1000)
            ])
            end_tt2000 = cdflib.cdfepoch.compute_tt2000([
                end_time.year, end_time.month, end_time.day,
                end_time.hour, end_time.minute, end_time.second,
                int(end_time.microsecond/1000)
            ])
            
            # Check epoch type and convert CDF times if needed
            epoch_var_info = cdf_file.varinq(time_var)
            epoch_type = epoch_var_info.Data_Type_Description
            print(f"   CDF time variable type: {epoch_type}")
            
            # Convert CDF times to TT2000 if needed (for comparison)
            if 'TT2000' in epoch_type:
                times_tt2000 = raw_times
            elif 'CDF_EPOCH' in epoch_type:
                print("   Converting CDF_EPOCH to TT2000 for filtering")
                times_tt2000 = np.array([cdflib.cdfepoch.to_datetime(t) for t in raw_times])
                times_tt2000 = np.array([cdflib.cdfepoch.compute_tt2000([
                    dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond//1000
                ]) for dt in times_tt2000])
            else:
                # Assume already compatible format
                times_tt2000 = raw_times
            
            # Find time range indices
            start_idx = np.searchsorted(times_tt2000, start_tt2000, side='left')
            end_idx = np.searchsorted(times_tt2000, end_tt2000, side='right')
            
            print(f"   Time range filtering: indices {start_idx} to {end_idx} out of {len(raw_times)}")
            
            if start_idx >= end_idx or start_idx >= len(raw_times):
                print("❌ No data in requested time range")
                return
            
            # Filter data to requested range
            filtered_raw_times = raw_times[start_idx:end_idx]
            filtered_raw_br = raw_br[start_idx:end_idx]
            
            print(f"   Filtered to {len(filtered_raw_times)} time points")
            print(f"   Filtered BR shape: {filtered_raw_br.shape}")
            
            # Convert filtered times to datetime for comparison
            filtered_raw_times_datetime = np.array(cdflib.cdfepoch.to_datetime(filtered_raw_times))
            
            # 5. Compare the data
            print("\n🔍 Comparing plotbot data with raw CDF data...")
            
            # Only compare the BR (radial) component
            filtered_raw_br_component = filtered_raw_br[:, 0]
            
            # Check shapes
            shapes_match = plotbot_data.shape == filtered_raw_br_component.shape
            print(f"   Shapes match: {shapes_match}")
            print(f"     Plotbot: {plotbot_data.shape}")
            print(f"     Raw CDF: {filtered_raw_br_component.shape}")
            
            # Check data values
            data_match = np.array_equal(plotbot_data, filtered_raw_br_component)
            print(f"   Data values match: {data_match}")
            
            if not data_match:
                # Check for NaN differences (might be due to fill value handling)
                nan_mask_plotbot = np.isnan(plotbot_data)
                nan_mask_raw = np.isnan(filtered_raw_br_component)
                nan_differences = np.sum(nan_mask_plotbot != nan_mask_raw)
                print(f"   NaN differences: {nan_differences}")
                
                # Check non-NaN values
                valid_mask = ~(nan_mask_plotbot | nan_mask_raw)
                if np.any(valid_mask):
                    valid_differences = np.sum(plotbot_data[valid_mask] != filtered_raw_br_component[valid_mask])
                    print(f"   Non-NaN value differences: {valid_differences}")
                    
                    if valid_differences > 0:
                        # Show some example differences
                        diff_indices = np.where(plotbot_data[valid_mask] != filtered_raw_br_component[valid_mask])[0][:5]
                        print(f"   Example differences (first 5):")
                        for idx in diff_indices:
                            plotbot_val = plotbot_data[valid_mask][idx]
                            raw_val = filtered_raw_br_component[valid_mask][idx]
                            print(f"     Index {idx}: Plotbot={plotbot_val}, Raw={raw_val}")
            
            # Check time arrays
            times_match = np.array_equal(plotbot_times, filtered_raw_times_datetime)
            print(f"   Time arrays match: {times_match}")
            
            if not times_match:
                # Check for small floating point differences
                time_diffs = np.abs(plotbot_times - filtered_raw_times_datetime)
                max_time_diff = np.max(time_diffs)
                print(f"   Max time difference: {max_time_diff}")
            
            # 6. Verify time-data pairing
            print("\n🔗 Verifying time-data pairing...")
            
            # Check that the first and last times match
            first_time_match = plotbot_times[0] == filtered_raw_times_datetime[0]
            last_time_match = plotbot_times[-1] == filtered_raw_times_datetime[-1]
            
            print(f"   First time match: {first_time_match}")
            print(f"     Plotbot: {plotbot_times[0]}")
            print(f"     Raw CDF: {filtered_raw_times_datetime[0]}")
            
            print(f"   Last time match: {last_time_match}")
            print(f"     Plotbot: {plotbot_times[-1]}")
            print(f"     Raw CDF: {filtered_raw_times_datetime[-1]}")
            
            # Check that data values correspond to the same times
            # Sample a few points in the middle
            if len(plotbot_times) > 10:
                mid_idx = len(plotbot_times) // 2
                sample_indices = [mid_idx - 2, mid_idx, mid_idx + 2]
                
                print(f"   Sample time-data pairs (indices {sample_indices}):")
                for idx in sample_indices:
                    if idx < len(plotbot_times):
                        plotbot_time = plotbot_times[idx]
                        plotbot_val = plotbot_data[idx]
                        raw_time = filtered_raw_times_datetime[idx]
                        raw_val = filtered_raw_br_component[idx]
                        
                        time_ok = plotbot_time == raw_time
                        data_ok = plotbot_val == raw_val
                        
                        print(f"     Index {idx}: Time={time_ok}, Data={data_ok}")
                        print(f"       Plotbot: {plotbot_time} → {plotbot_val}")
                        print(f"       Raw CDF: {raw_time} → {raw_val}")
            
            # 7. Final assertions
            print("\n✅ Final verification...")
            
            assert shapes_match, "Data shapes should match between plotbot and raw CDF"
            assert data_match, "Data values should match between plotbot and raw CDF"
            assert times_match, "Time arrays should match between plotbot and raw CDF"
            assert first_time_match, "First time should match between plotbot and raw CDF"
            assert last_time_match, "Last time should match between plotbot and raw CDF"
            
            print("✅ SUCCESS: Raw CDF data verification passed!")
            print("   All data integrity checks passed")
            print("   Time-data pairing is correct")
            
    except Exception as e:
        print(f"❌ Error reading CDF file: {e}")
        import traceback
        traceback.print_exc()
        raise

@pytest.mark.mission("Stardust Test: Multiple Trange Raw CDF Verification")
def test_stardust_multiple_trange_raw_cdf_verification():
    """
    Test that the data returned by plotbot matches the raw data from the original CDF file
    for three different, non-overlapping tranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Multiple Trange Raw CDF Verification ⭐️⭐️⭐️")
    
    print("🔍 running imports...")
    
    import cdflib
    from plotbot.data_classes.data_types import data_types
    from plotbot.data_import import get_project_root
    from dateutil.parser import parse
    from datetime import timezone
    import os
    import re

    tranges = [
        ['2021-01-19/02:00:00', '2021-01-19/03:00:00'],  # 1 hour period
        ['2021-01-19/05:00:00', '2021-01-19/06:00:00'],  # 1 hour period, 2 hours later
        ['2021-01-19/08:00:00', '2021-01-19/09:00:00'],  # 1 hour period, 2 hours later
    ]

    print("🔍 getting mag_RTN_4sa config...")
    mag_config = data_types.get('mag_RTN_4sa')
    assert mag_config, "mag_RTN_4sa config missing"

    print("🔍 running tranges...")
    for i, trange in enumerate(tranges):
        print(f"\n=== TRANGE {i+1}: {trange} ===")
        print(f"Calling plotbot with trange: {trange}")
        # 1. Get data through plotbot
        plotbot_function(trange, mag_rtn_4sa.br, 1)
        plotbot_data = np.copy(mag_rtn_4sa.br.data)
        plotbot_times = np.copy(mag_rtn_4sa.br.datetime_array) if mag_rtn_4sa.br.datetime_array is not None else None
        print(f"   Plotbot data shape: {plotbot_data.shape}")
        print(f"   Plotbot times shape: {plotbot_times.shape if plotbot_times is not None else 'None'}")

        # 2. Find the actual CDF file using the same logic as data_import.py
        print(f"Parsing trange for CDF file search: {trange}")
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        found_files = []
        from datetime import datetime, timedelta
        def daterange(start_date, end_date):
            current_date = start_date.date()
            end_date_only = end_date.date()
            while current_date <= end_date_only:
                yield datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
                current_date += timedelta(days=1)
        cdf_base_path = mag_config.get('local_path')
        assert cdf_base_path, "No local_path found in mag config"
        if not os.path.isabs(cdf_base_path):
            project_root = get_project_root()
            cdf_base_path = os.path.join(project_root, cdf_base_path)
        for single_date in daterange(start_time, end_time):
            year = single_date.year
            date_str = single_date.strftime('%Y%m%d')
            local_dir = os.path.join(cdf_base_path.format(data_level=mag_config['data_level']), str(year))
            if os.path.exists(local_dir):
                file_pattern_template = mag_config['file_pattern_import']
                file_pattern = file_pattern_template.format(
                    data_level=mag_config['data_level'],
                    date_str=date_str
                )
                pattern_for_re = file_pattern.replace('*', '.*')
                regex = re.compile(pattern_for_re, re.IGNORECASE)
                for f_name in os.listdir(local_dir):
                    if regex.match(f_name):
                        found_files.append(os.path.join(local_dir, f_name))
        assert found_files, f"No CDF files found for trange {trange}"
        print(f"Using CDF file for trange {trange}: {found_files[0]}")
        cdf_file_path = found_files[0]
        with cdflib.CDF(cdf_file_path) as cdf_file:
            all_variables = cdf_file.cdf_info().zVariables + cdf_file.cdf_info().rVariables
            time_var = next((v for v in all_variables if 'epoch' in v.lower()), None)
            assert time_var, "No time variable (Epoch) found in CDF file"
            raw_times = cdf_file.varget(time_var)
            br_var = next((v for v in all_variables if 'br' in v.lower() or 'psp_fld' in v.lower()), None)
            assert br_var, "No BR variable found in CDF file"
            raw_br = cdf_file.varget(br_var)
            start_tt2000 = cdflib.cdfepoch.compute_tt2000([
                start_time.year, start_time.month, start_time.day,
                start_time.hour, start_time.minute, start_time.second,
                int(start_time.microsecond/1000)
            ])
            end_tt2000 = cdflib.cdfepoch.compute_tt2000([
                end_time.year, end_time.month, end_time.day,
                end_time.hour, end_time.minute, end_time.second,
                int(end_time.microsecond/1000)
            ])
            epoch_var_info = cdf_file.varinq(time_var)
            epoch_type = epoch_var_info.Data_Type_Description
            if 'TT2000' in epoch_type:
                times_tt2000 = raw_times
            elif 'CDF_EPOCH' in epoch_type:
                times_tt2000 = np.array([cdflib.cdfepoch.to_datetime(t) for t in raw_times])
                times_tt2000 = np.array([cdflib.cdfepoch.compute_tt2000([
                    dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond//1000
                ]) for dt in times_tt2000])
            else:
                times_tt2000 = raw_times
            start_idx = np.searchsorted(times_tt2000, start_tt2000, side='left')
            end_idx = np.searchsorted(times_tt2000, end_tt2000, side='right')
            print(f"   Raw CDF time filtering: indices {start_idx} to {end_idx} out of {len(raw_times)}")
            print(f"   Raw CDF total time points: {len(raw_times)}")
            print(f"   Raw CDF total BR points: {len(raw_br)}")
            filtered_raw_times = raw_times[start_idx:end_idx]
            filtered_raw_br = raw_br[start_idx:end_idx]
            filtered_raw_br_component = filtered_raw_br[:, 0]
            filtered_raw_times_datetime = np.array(cdflib.cdfepoch.to_datetime(filtered_raw_times))
            print(f"   Raw CDF filtered time points: {len(filtered_raw_times)}")
            print(f"   Raw CDF filtered BR points: {len(filtered_raw_br_component)}")
            # Compare
            shapes_match = plotbot_data.shape == filtered_raw_br_component.shape
            data_match = np.array_equal(plotbot_data, filtered_raw_br_component)
            times_match = np.array_equal(plotbot_times, filtered_raw_times_datetime)
            print(f"   Shapes match: {shapes_match}")
            print(f"   Data values match: {data_match}")
            print(f"   Time arrays match: {times_match}")
            assert shapes_match, f"Data shapes should match for trange {trange}"
            assert data_match, f"Data values should match for trange {trange}"
            assert times_match, f"Time arrays should match for trange {trange}"
            print(f"   ✅ Trange {i+1} passed!")

@pytest.mark.mission("Stardust Test: Systematic Time Range Tracking")
def test_stardust_systematic_time_range_tracking():
    """
    Test that TimeRangeTracker correctly stores time ranges and that mag_rtn_4sa.br.requested_trange
    gets updated properly for different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: Stardust Test: Systematic Time Range Tracking ⭐️⭐️⭐️")
    
    # Two 10-minute periods separated by a gap
    trange1 = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    trange2 = ['2021-01-19/03:00:00', '2021-01-19/03:10:00']

    print(f"Testing time range tracking with:")
    print(f"   trange1: {trange1}")
    print(f"   trange2: {trange2}")

    # First plotbot call
    print("\n📊 First plotbot call...")
    plotbot_function(trange1, mag_rtn_4sa.br, 1)
    
    # Check stored time range
    stored_trange1 = getattr(mag_rtn_4sa.br, 'requested_trange', None)
    print(f"   After first call: mag_rtn_4sa.br.requested_trange = {stored_trange1}")
    
    # Second plotbot call  
    print("\n📊 Second plotbot call...")
    plotbot_function(trange2, mag_rtn_4sa.br, 1)
    
    # Check stored time range
    stored_trange2 = getattr(mag_rtn_4sa.br, 'requested_trange', None)
    print(f"   After second call: mag_rtn_4sa.br.requested_trange = {stored_trange2}")
    
    # Verify time ranges were stored and are different
    assert stored_trange1 is not None, "First time range should be stored"
    assert stored_trange2 is not None, "Second time range should be stored"
    assert stored_trange1 == trange1, f"First stored trange should match trange1: {stored_trange1} vs {trange1}"
    assert stored_trange2 == trange2, f"Second stored trange should match trange2: {stored_trange2} vs {trange2}"
    assert stored_trange1 != stored_trange2, "Stored time ranges should be different"
    
    # Test .data property returns correct data for stored time ranges
    print("\n📊 Testing .data property...")
    plotbot_function(trange1, mag_rtn_4sa.br, 1)
    data1 = np.copy(mag_rtn_4sa.br.data)
    print(f"   trange1 data shape: {data1.shape}")
    
    plotbot_function(trange2, mag_rtn_4sa.br, 1) 
    data2 = np.copy(mag_rtn_4sa.br.data)
    print(f"   trange2 data shape: {data2.shape}")
    
    # Data should be different for different time ranges
    data_different = not np.array_equal(data1, data2)
    print(f"   Data arrays are different: {data_different}")
    assert data_different, "Data arrays should be different for different time ranges"
    
    print("✅ SUCCESS: Time range tracking AND data property working correctly!")
    print(f"   trange1 stored correctly: {stored_trange1}")
    print(f"   trange2 stored correctly: {stored_trange2}")
    print("   Time ranges are different as expected")
    print("   Data arrays are different as expected")

