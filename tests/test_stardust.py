# tests/test_stardust.py

"""
Master Stardust Test File

Aggregates key tests from various modules for a quick system health check.
"""

import matplotlib
matplotlib.use('Agg') # Use non-interactive backend BEFORE importing pyplot

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
from plotbot.data_classes.psp_data_types import data_types
from plotbot.data_classes.psp_proton_fits_classes import proton_fits as proton_fits_instance
from plotbot.data_import import find_local_csvs
from plotbot.plot_manager import plot_manager
from plotbot import print_manager # For logging
from plotbot import plt # For plot closing
from plotbot.test_pilot import phase, system_check # Test helpers
from plotbot.audifier import Audifier, audifier as global_audifier
from plotbot.data_classes.psp_mag_classes import mag_rtn, mag_rtn_4sa # Restore mag_rtn
from plotbot.data_download_pyspedas import download_spdf_data # For SPDF debug test
from plotbot.data_download_berkeley import download_berkeley_data # For conflict test
from plotbot import config # Removed alias, import directly from package
from plotbot import ham as ham_instance # Import directly from package
from plotbot import custom_variable

# --- Test Constants & Fixtures --- 
# Re-define or import necessary constants/fixtures from other files
TEST_TRANGE_DEFAULT = ['2020-04-09/06:00:00.000', '2020-04-09/07:30:00.000']
TEST_DATE_STR_DEFAULT = '20200409'
TEST_YEAR_DEFAULT = '2020'

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
psp_data_dir = os.path.join(WORKSPACE_ROOT, 'psp_data') # Define psp_data_dir here
PYSPEDAS_ROOT_DATA_DIR = os.path.join(WORKSPACE_ROOT, 'psp_data')

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

        plt.pause(0.5) # Restore display plot briefly

    except Exception as e:
        pytest.fail(f"Stardust Plotbot test failed: {e}")
    finally:
        # Always try to close the figure using its number
        if fig_num is not None:
            try:
                # plt.pause(0.1) # Tiny pause before closing - REMOVED
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
        # Use config directly
        config.multiplot_window = '1:00:00.000' # Match STARDUST_TRANGE duration
        config.multiplot_position = 'around'
        config.multiplot_use_single_title = True
        config.multiplot_single_title_text = "Multiplot Stardust Test"

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

        plt.pause(0.5) # Restore display plot briefly

    except Exception as e:
        pytest.fail(f"Stardust Multiplot test failed: {e}")
    finally:
        # Explicitly close the figure created by this test using its number
        if fig_num is not None:
            try:
                # plt.pause(0.1) # Tiny pause before closing - REMOVED
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

        plt.pause(0.5) # Restore display plot briefly

    except Exception as e:
        pytest.fail(f"Stardust Showdahodo test failed: {e}")
    finally:
        # Explicitly close the figure created by this test using its number
        if fig_num is not None:
            try:
                # plt.pause(0.1) # Tiny pause before closing - REMOVED
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
        
        plt.pause(0.5) # Display plot briefly

    except Exception as e:
        tb_str = traceback.format_exc()
        pytest.fail(f"Stardust HAM test failed for {var_name} with exception: {e}\nTraceback: {tb_str}")
    finally:
        # Explicitly close the figure using its number
        if fig_num is not None:
             try:
                 plt.pause(0.1) # Tiny pause before closing
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
        
        plt.pause(0.5) # Display plot briefly

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
        proton_fits_instance.vsw_mach_pfits,
        proton_fits_instance.beta_ppar_pfits,
        proton_fits_instance.beta_pperp_pfits,
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

# --- End Copied Custom Variable Tests --- 

