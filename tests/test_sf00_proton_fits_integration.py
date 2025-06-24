#tests/test_sf00_proton_fits_integration.py
# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python -m pytest tests/test_sf00_proton_fits_integration.py -vv -s
# To run a specific test (e.g., test_plotbot_with_scatter_and_fits) and see print output:
# conda run -n plotbot_env python -m pytest tests/test_sf00_proton_fits_integration.py::test_plotbot_with_scatter_and_fits -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

"""
Tests for Proton FITS (SF00) data integration and calculations.

This file contains tests for:
- Finding and loading SF00 FITS CSV files.
- Running calculations within the proton_fits_class (via update method).
- Integrating SF00 FITS calculations with the main plotbot function, including scatter plots.

NOTES ON TEST OUTPUT:
- Use print statements for basic info (will show with -s flag).
- To see all print statements in test output, add the -s flag when running pytest:
  e.g., cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_sf00_proton_fits_integration.py -v -s

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_sf00_proton_fits_integration.py -v

To run a specific test (e.g., test_plotbot_with_scatter_and_fits):
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_sf00_proton_fits_integration.py::TestFitsIntegration::test_plotbot_with_scatter_and_fits -v
"""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta
import traceback
import sys
import logging
import cdflib
from collections import namedtuple

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define the path to the PSP data directory relative to the workspace root
# Construct the absolute path from the test file's location
_test_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_test_dir, '..'))
psp_data_dir = os.path.join(_project_root, "data", "psp")

if not os.path.isdir(psp_data_dir):
    print(f"Warning: Default PSP data directory '{psp_data_dir}' not found. Tests requiring local data may fail.")
    # Optionally, attempt to find it elsewhere or skip tests? For now, just warn.

# Import necessary components from plotbot
from plotbot import plotbot, multiplot, showdahodo
# Import the instance, not the class definition directly for tests
from plotbot.data_classes.psp_proton_fits_classes import proton_fits as proton_fits_instance
# Import only the functions needed and available
from plotbot.data_import import find_local_csvs # Corrected: was find_local_fits_csvs
from plotbot.plot_manager import plot_manager
from plotbot.print_manager import print_manager
from plotbot.plotbot_helpers import time_clip # Corrected import location for time_clip

# Set up logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Temporarily keep old Jaye fits imports for reference/comparison --- 
# from plotbot.psp_proton_fits_classes import proton_fits # WRONG PATH - keep for context
# try:
#     from Jaye_fits_integration.calculations.calculate_fits_derived import calculate_sf00_fits_vars, calculate_sf01_fits_vars
#     # Placeholder for resampling functions - we might need to mock these or ensure they are importable
#     # from Jaye_fits_integration.functions import upsample_to_match, downsample_to_match
#     # Define dummy versions if the real ones cause issues during testing setup
#     def upsample_to_match(df, t1, t2): print("Warning: Using dummy upsample_to_match"); return df # Dummy
#     def downsample_to_match(t1, d1, t2): print("Warning: Using dummy downsample_to_match"); return d1 # Dummy
# except ImportError as e:
#     print(f"Could not import functions from Jaye_fits_integration: {e}.")
#     # Define dummy functions if import fails, to allow basic structure setup
#     # calculate_sf00_fits_vars and calculate_sf01_fits_vars should rely on the main import
#     def upsample_to_match(df, t1, t2): return df # Dummy
#     def downsample_to_match(t1, d1, t2): return d1 # Dummy
    
# --- Test Helper imports ---
from plotbot.test_pilot import phase, system_check

# --- Helper Function for Finding Files ---

def find_psp_csv_files(trange, data_type):
    """
    Finds PSP SF00 CSV data files based on a time range,
    following the specified directory structure relative to the project root.
    e.g., psp_data/sf00/p2/v00/YYYY/MM/spp_swp_spi_sf00_YYYY-MM-DD_v00.csv
    """
    found_files = []
    try:
        # Use dateutil parser for flexibility if available, otherwise basic strptime
        try:
            from dateutil.parser import parse as date_parse
            start_dt = date_parse(trange[0].split('/')[0])
            end_dt = date_parse(trange[1].split('/')[0])
        except ImportError:
             print("Warning: dateutil not installed, using basic datetime parsing.")
             dt_format = '%Y-%m-%d'
             start_dt = datetime.strptime(trange[0].split('/')[0], dt_format)
             end_dt = datetime.strptime(trange[1].split('/')[0], dt_format)

    except ValueError:
        print(f"Error: Could not parse dates from trange: {trange}")
        return []

    # Define base path structure and filename components based on data_type
    if data_type == 'sf00':
        base_rel_path = Path('data/psp/sf00/p2/v00')
        prefix = 'spp_swp_spi_sf00_'
        suffix = '_v00.csv' # Based on user example path, was _v00_driftswitch.csv before
    else:
        raise ValueError("Invalid data_type specified. Must be 'sf00'.")

    # Iterate through dates in the range (inclusive)
    current_dt = start_dt
    while current_dt <= end_dt:
        year_str = current_dt.strftime('%Y')
        month_str = current_dt.strftime('%m')
        date_str_file = current_dt.strftime('%Y-%m-%d') # Format for filename

        # Construct the expected file path
        file_path = base_rel_path / year_str / month_str / f"{prefix}{date_str_file}{suffix}"

        # Check if the file exists relative to the current working directory
        # Assumes tests are run from the project root
        if file_path.exists():
            found_files.append(file_path)
        else:
            print(f"Info: File not found at expected path: {file_path}") # Use info level

        current_dt += timedelta(days=1) # Move to the next day

    return found_files


# --- Test Class ---

# Simple structure to mimic DataObject for testing internal calculation
FitsTestDataContainer = namedtuple('FitsTestDataContainer', ['times', 'data'])

class TestFitsIntegration:
    """Test suite for FITS data integration, calculation, and plotting."""

    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data', 'psp_fits')
    TEST_TRANGE = ['2024-09-30/11:45:00.000', '2024-09-30/12:45:00.000']
    TEST_DAY = '20240930'

    @classmethod
    def setup_class(cls):
        """Set up for the test class. Ensures FITS data exists and re-initializes plot options."""
        print("\n--- TestFitsIntegration Class Setup ---")
        # Removed the check for TEST_DATA_DIR as tests use find_psp_csv_files or direct import
        # if not os.path.exists(cls.TEST_DATA_DIR):
        #     pytest.skip("Test data directory not found, skipping FITS integration tests.")
        
        # --- Explicitly re-run set_ploptions for the proton_fits instance ---
        # This ensures the instance uses the latest definitions from the class file
        try:
            print("Re-running proton_fits.set_ploptions() to ensure fresh options...")
            # Ensure we use the correct imported instance name
            proton_fits_instance.set_ploptions() 
            print("proton_fits.set_ploptions() completed.")
        except Exception as e:
            pytest.fail(f"Failed to re-run proton_fits.set_ploptions() during setup: {e}")
        # ---------------------------------------------------------------------
        print("--- End TestFitsIntegration Class Setup ---")

    # Define the test time range
    EXPECTED_DATE_STR = '2024-09-30'

    # --- Test: Calculate SF00 Variables --- 
    @pytest.fixture(scope='class')
    def sf00_test_data(self):
        """Fixture to load raw SF00 CSV data for calculation tests."""
        print("--- Loading SF00 Test Data Fixture ---")
        # Find files using the utility from data_import
        found_files = find_local_csvs(psp_data_dir, ['*sf00*.csv'], self.TEST_DAY) # Assuming psp_data_dir is defined globally or accessible
        if not found_files:
            pytest.skip("Skipping SF00 calculation test: No input files found.")
            return None # Return None if skipping
        try:
            # Read and concatenate found files
            df_sf00_raw = pd.concat((pd.read_csv(f) for f in found_files), ignore_index=True)
            if df_sf00_raw.empty:
                 pytest.skip("Skipping SF00 calculation test: Loaded DataFrame is empty.")
                 return None # Return None if skipping
            print(f"Loaded SF00 test data, shape: {df_sf00_raw.shape}")
            print(f"SF00 Test Data Columns: {df_sf00_raw.columns.tolist()}")
            return df_sf00_raw
        except Exception as e:
            pytest.fail(f"Failed to load/concat SF00 CSVs {found_files}: {e}")
            return None # Return None on failure

    @pytest.mark.skip(reason="File finding logic in this test needs update or removal")
    def test_find_and_load_sf00_csv(self):
        """Tests finding and loading SF00 (proton) CSV files for the test trange."""
        found_files = find_psp_csv_files(self.TEST_TRANGE, 'sf00')

        assert len(found_files) > 0, f"No SF00 CSV files found for trange {self.TEST_TRANGE}. Expected at least one file containing date {self.EXPECTED_DATE_STR}. Searched paths like psp_data/sf00/p2/v00/YYYY/MM/..."

        try:
            # Load and concatenate files found
            df_sf00 = pd.concat((pd.read_csv(f) for f in found_files), ignore_index=True)
            assert not df_sf00.empty
            print(f"Successfully loaded {len(found_files)} SF00 file(s) for {self.TEST_TRANGE}")
            print(df_sf00.head())
            # TODO: Add more specific assertions based on expected columns/data
        except Exception as e:
            pytest.fail(f"Failed to load/concat SF00 CSVs {found_files}: {e}")

    def test_calculate_sf00_vars(self, sf00_test_data):
        """Test the calculation of derived variables triggered by updating the proton_fits_instance."""
        assert sf00_test_data is not None, "Test setup failed: sf00_test_data fixture did not return data"
        assert not sf00_test_data.empty, "Test setup failed: sf00_test_data DataFrame provided by fixture is empty"

        print("--- Running SF00 Internal Calculation Test ---")

        # --- Prepare DataObject ---
        try:
            # Assume 'time' column is Unix epoch seconds
            unix_times = sf00_test_data['time'].to_numpy()
            
            # Convert Unix times to datetime objects (UTC)
            datetime_objs_pd = pd.to_datetime(unix_times, unit='s', utc=True)
            
            # Extract components into a list of lists
            datetime_components_list = [
                [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)]
                for dt in datetime_objs_pd # Iterate over pandas Timestamps
            ]
            
            # Compute TT2000 from the list of components
            tt2000_times = cdflib.cdfepoch.compute_tt2000(datetime_components_list)
            
            # --- DEBUGGING --- 
            # print(f"DEBUG: tt2000_result = {tt2000_times}") # Keep result name consistent if debugging again
            # print(f"DEBUG: type(tt2000_result) = {type(tt2000_times)}")
            # --- END DEBUGGING --- 

            # Ensure it's a numpy array (should be returned as one from list input)
            if not isinstance(tt2000_times, np.ndarray):
                tt2000_times = np.array(tt2000_times)
            
            # Create data dictionary from DataFrame columns
            data_dict = {col: sf00_test_data[col].to_numpy() for col in sf00_test_data.columns if col != 'time'}
            
            # Convert lists to numpy arrays in the dictionary
            for key in data_dict:
                 data_dict[key] = np.array(data_dict[key])
            test_data_obj = FitsTestDataContainer(times=tt2000_times, data=data_dict)
            print(f"Prepared TestDataObject with {len(tt2000_times)} time points.")

        except Exception as e:
            pytest.fail(f"Failed to prepare TestDataObject: {e}")

        # --- Trigger Calculation via Update ---
        try:
            # Reset the instance just in case? Or rely on update overwriting? Let's update.
            proton_fits_instance.update(test_data_obj)
            print("Called proton_fits_instance.update()")
        except Exception as e:
             pytest.fail(f"proton_fits_instance.update() failed: {e}\\nTraceback: {traceback.format_exc()}")

        # --- Assertions ---
        # Check that specific calculated attributes now have data
        assert hasattr(proton_fits_instance, 'beta_ppar_pfits'), "Attribute 'beta_ppar_pfits' not found on instance."
        assert proton_fits_instance.beta_ppar_pfits.data is not None, "beta_ppar_pfits.data is None after update."
        assert not np.all(np.isnan(proton_fits_instance.beta_ppar_pfits.data)), "beta_ppar_pfits.data contains only NaNs."
        
        assert hasattr(proton_fits_instance, 'valfven_pfits'), "Attribute 'valfven_pfits' not found on instance."
        assert proton_fits_instance.valfven_pfits.data is not None, "valfven_pfits.data is None after update."
        assert not np.all(np.isnan(proton_fits_instance.valfven_pfits.data)), "valfven_pfits.data contains only NaNs."

        # Optional: Check datetime array length matches input
        assert len(proton_fits_instance.datetime_array) == len(tt2000_times), \
               f"datetime_array length ({len(proton_fits_instance.datetime_array)}) doesn't match input ({len(tt2000_times)})."

        print("SF00 internal calculations appear successful. Data populated.")
        # Can add more checks here for other variables if needed

    def test_plotbot_with_scatter_and_fits(self):
        """Tests calling the main plotbot function with FITS variable class instances,
           assuming plotbot or the class properties handle data loading/calculation."""
        # Use the class TEST_TRANGE which has known data
        test_trange = self.TEST_TRANGE

        # Now attempt the plotbot call directly with class instances.
        # Accessing these properties (e.g., proton_fits.np1) or plotbot itself
        # is assumed to trigger necessary data loading/calculation for the trange.
        try:
            print(f"Attempting plotbot call for trange: {test_trange} with class instances proton_fits.np1, proton_fits.valfven_pfits, proton_fits.beta_ppar_pfits, proton_fits.chi_p")
            # Call plotbot directly with class instances and panel numbers
            # Add chi_p to a new panel (panel 4)
            plotbot(test_trange, 
                    proton_fits_instance.np1, 1, 
                    proton_fits_instance.valfven_pfits, 2,
                    proton_fits_instance.beta_ppar_pfits, 3,
                    proton_fits_instance.chi_p, 4)
            print("Plotbot call completed successfully.")
            # If plotbot runs without error, the test passes implicitly
            assert True

            # --- Assertions to verify data was loaded --- 
            print("--- Verifying Data Availability Post-Plotbot Call ---")
            vars_to_check = {
                'np1': proton_fits_instance.np1,
                'valfven': proton_fits_instance.valfven_pfits,
                'beta_ppar': proton_fits_instance.beta_ppar_pfits,
                'chi_p': proton_fits_instance.chi_p
            }
            for name, var_instance in vars_to_check.items():
                # Check if the instance and its necessary attributes exist
                assert var_instance is not None, f"proton_fits.{name} instance is None after plotbot call"
                assert hasattr(var_instance, 'datetime_array') and var_instance.datetime_array is not None, f"proton_fits.{name}.datetime_array is None after plotbot call"
                assert hasattr(var_instance, 'data') and var_instance.data is not None, f"proton_fits.{name}.data is None after plotbot call"
                
                # Use time_clip to find indices within the test time range
                try:
                    indices = time_clip(var_instance.datetime_array, test_trange[0], test_trange[1])
                except Exception as e:
                     pytest.fail(f"time_clip failed for {name}: {e}\nDatetime array: {var_instance.datetime_array[:10]}...\nTrange: {test_trange}")

                assert len(indices) > 0, f"Variable '{name}' found 0 data points in range {test_trange} after plotbot call. Datetime array length: {len(var_instance.datetime_array)}"
                
                # Check if data for these indices is all NaN
                try:
                     # Ensure data is a numpy array for isnan check
                     clipped_data = np.array(var_instance.data)[indices]
                     assert not np.all(np.isnan(clipped_data)), f"Variable '{name}' has only NaN values in range {test_trange} after plotbot call."
                except IndexError as e:
                     pytest.fail(f"IndexError accessing data for '{name}' at indices {indices}. Data shape: {np.shape(var_instance.data)}. Error: {e}")
                except Exception as e:
                     pytest.fail(f"Error checking NaN for '{name}': {e}. Data type: {type(var_instance.data)}. Clipped data: {clipped_data}")

                print(f"✅ Variable '{name}' has data and {len(indices)} valid points in the specified time range after plotbot call.")
            print("--- End Data Availability Verification ---")

        except Exception as e:
            # Use pytest.fail for better error reporting in tests
            pytest.fail(f"plotbot call failed with exception: {e}\nTraceback: {traceback.format_exc()}")

    # --- Helper for Grouped Tests --- 
    def _run_plotbot_test_group(self, variables_to_plot):
        """Helper function to run a standard plotbot test for a group of variables."""
        test_trange = self.TEST_TRANGE
        plot_args = [test_trange]
        var_names = []
    
        # Filter out None variables just in case, though they shouldn't be passed
        valid_variables = [v for v in variables_to_plot if v is not None and hasattr(v, 'subclass_name')]
        if len(valid_variables) != len(variables_to_plot):
            print("Warning: Some variables passed to _run_plotbot_test_group were None or invalid.")
    
        # Store the names of the variables we intend to plot
        var_names = [v.subclass_name for v in valid_variables]
        print(f"\n--- Testing Group: {var_names} ---")
    
        # Prepare arguments for plotbot using the initial (potentially empty) instances
        for i, var_instance in enumerate(valid_variables):
            panel_num = i + 1
            plot_args.extend([var_instance, panel_num])
    
        if not valid_variables: # Don't run if no valid vars provided
            print("No valid variables provided to test group. Skipping plotbot call.")
            return
    
        try:
            print(f"Attempting plotbot call for trange: {test_trange} with variables: {var_names}")
            plotbot(*plot_args)
            print("Plotbot call completed successfully.")
    
            # --- Assertions to verify data was loaded ---
            print("--- Verifying Data Availability Post-Plotbot Call ---")
            # --- Retrieve the *updated* instances AFTER plotbot call --- 
            vars_to_check = {}
            for name in var_names:
                try:
                    updated_instance = getattr(proton_fits_instance, name)
                    vars_to_check[name] = updated_instance
                except AttributeError:
                    pytest.fail(f"Could not retrieve proton_fits_instance.{name} after plotbot call.")
            # ------------------------------------------------------------

            for name, var_instance in vars_to_check.items():
                # Check if the instance and its necessary attributes exist
                assert var_instance is not None, f"proton_fits.{name} instance is None after plotbot call"
                assert hasattr(var_instance, 'datetime_array') and var_instance.datetime_array is not None, f"proton_fits.{name}.datetime_array is None after plotbot call"
                assert hasattr(var_instance, 'data') and var_instance.data is not None, f"proton_fits.{name}.data is None after plotbot call"
                
                # Use time_clip to find indices within the test time range
                try:
                    indices = time_clip(var_instance.datetime_array, test_trange[0], test_trange[1])
                except Exception as e:
                     pytest.fail(f"time_clip failed for {name}: {e}\nDatetime array: {var_instance.datetime_array[:10]}...\nTrange: {test_trange}")

                assert len(indices) > 0, f"Variable '{name}' found 0 data points in range {test_trange} after plotbot call. Datetime array length: {len(var_instance.datetime_array)}"
                
                # Check if data for these indices is all NaN
                try:
                     # Ensure data is a numpy array for isnan check
                     clipped_data = np.array(var_instance.data)[indices]
                     assert not np.all(np.isnan(clipped_data)), f"Variable '{name}' has only NaN values in range {test_trange} after plotbot call."
                except IndexError as e:
                     pytest.fail(f"IndexError accessing data for '{name}' at indices {indices}. Data shape: {np.shape(var_instance.data)}. Error: {e}")
                except Exception as e:
                     pytest.fail(f"Error checking NaN for '{name}': {e}. Data type: {type(var_instance.data)}. Clipped data: {clipped_data}")

                print(f"✅ Variable '{name}' has data and {len(indices)} valid points in the specified time range after plotbot call.")
            print("--- End Data Availability Verification ---")

        except Exception as e:
            # Use pytest.fail for better error reporting in tests
            pytest.fail(f"plotbot call failed with exception: {e}\nTraceback: {traceback.format_exc()}")

    # --- Grouped FITS Variable Tests ---
    def test_plotbot_fits_group_1(self):
        """Tests FITS variables: qz_p, vsw_mach_pfits, beta_ppar_pfits, beta_pperp_pfits, ham_param"""
        vars_to_test = [
            proton_fits_instance.qz_p,
            proton_fits_instance.vsw_mach_pfits,
            proton_fits_instance.beta_ppar_pfits,
            proton_fits_instance.beta_pperp_pfits,
            proton_fits_instance.ham_param
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_2(self):
        """Tests FITS variables: np1, np2, n_tot, np2_np1_ratio, vp1_x"""
        vars_to_test = [
            proton_fits_instance.np1,
            proton_fits_instance.np2,
            proton_fits_instance.n_tot,
            proton_fits_instance.np2_np1_ratio,
            proton_fits_instance.vp1_x
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_3(self):
        """Tests FITS variables: vp1_y, vp1_z, vp1_mag, vcm_x, vcm_y"""
        vars_to_test = [
            proton_fits_instance.vp1_y,
            proton_fits_instance.vp1_z,
            proton_fits_instance.vp1_mag,
            proton_fits_instance.vcm_x,
            proton_fits_instance.vcm_y
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_4(self):
        """Tests FITS variables: vcm_z, vcm_mag, vdrift, vdrift_abs, vdrift_va_pfits"""
        vars_to_test = [
            proton_fits_instance.vcm_z,
            proton_fits_instance.vcm_mag,
            proton_fits_instance.vdrift,
            proton_fits_instance.vdrift_abs,
            proton_fits_instance.vdrift_va_pfits
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_5(self):
        """Tests FITS variables: Trat1, Trat2, Trat_tot, Tpar1, Tpar2"""
        vars_to_test = [
            proton_fits_instance.Trat1,
            proton_fits_instance.Trat2,
            proton_fits_instance.Trat_tot,
            proton_fits_instance.Tpar1,
            proton_fits_instance.Tpar2
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_6(self):
        """Tests FITS variables: Tpar_tot, Tperp1, Tperp2, Tperp_tot, Temp_tot"""
        vars_to_test = [
            proton_fits_instance.Tpar_tot,
            proton_fits_instance.Tperp1,
            proton_fits_instance.Tperp2,
            proton_fits_instance.Tperp_tot,
            proton_fits_instance.Temp_tot
        ]
        self._run_plotbot_test_group(vars_to_test)

    def test_plotbot_fits_group_7(self):
        """Tests FITS variables: abs_qz_p, chi_p, chi_p_norm, valfven_pfits"""
        vars_to_test = [
            proton_fits_instance.abs_qz_p,
            proton_fits_instance.chi_p,
            proton_fits_instance.chi_p_norm,
            proton_fits_instance.valfven_pfits
        ]
        self._run_plotbot_test_group(vars_to_test)

    # --- Test Multiplot and Showdahodo with FITS --- 
    def test_fits_with_multiplot_and_showdahodo(self):
        """Tests calling multiplot and showdahodo with FITS variable instances."""
        test_trange = self.TEST_TRANGE
        
        # Define a center time for our plots (midpoint of the test range)
        center_time = pd.Timestamp(test_trange[0]) + (pd.Timestamp(test_trange[1]) - pd.Timestamp(test_trange[0])) / 2
        center_time_str = center_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
        
        # Select a few FITS variables to test
        vars_to_test = [
            proton_fits_instance.np1,            # Core density
            proton_fits_instance.vp1_mag,        # Core velocity magnitude
            proton_fits_instance.Temp_tot        # Total temperature
        ]
        var_names = [v.subclass_name for v in vars_to_test if v is not None]
        
        # Create the plot_list for multiplot - list of (time, variable) tuples
        plot_list = [(center_time_str, var) for var in vars_to_test]

        # Test multiplot
        try:
            print(f"\n--- Testing multiplot with {var_names} for center time: {center_time_str} ---")
            multiplot(plot_list)  # Pass list of tuples [(time, var), ...]
            print("multiplot call completed successfully.")
            assert True  # Pass if no exception
        except Exception as e:
            pytest.fail(f"multiplot call failed with exception: {e}")

        # Test showdahodo - For this we need x and y variables
        try:
            print(f"\n--- Testing showdahodo with x={var_names[0]}, y={var_names[1]} for trange: {test_trange} ---")
            # showdahodo takes time range and variable instances directly
            showdahodo(test_trange, vars_to_test[0], vars_to_test[1]) 
            print("showdahodo call completed successfully.")
            assert True  # Pass if no exception
        except Exception as e:
            pytest.fail(f"showdahodo call failed with exception: {e}")

    def test_multiplot_and_showdahodo_with_fits(self):
        """Test multiplot and showdahodo functions with FITS variables."""
        # Use the proper test time range that's already defined
        test_trange = self.TEST_TRANGE  # ['2024-09-30/11:45:00.000', '2024-09-30/12:45:00.000']
        
        # First ensure we have data loaded by using plotbot
        plotbot(test_trange, proton_fits_instance.np1, 1)
        
        # Test multiplot with a list of (time, variable) tuples
        try:
            # Calculate a center time
            center_time = pd.Timestamp(test_trange[0]) + (pd.Timestamp(test_trange[1]) - pd.Timestamp(test_trange[0])) / 2
            center_time_str = center_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
            
            # Create data for multiplot using existing variables
            plot_list = [
                (center_time_str, proton_fits_instance.np1),
                (center_time_str, proton_fits_instance.beta_ppar_pfits)
            ]
            
            print(f"\n--- Testing multiplot with FITS variables for center time: {center_time_str} ---")
            multiplot(plot_list)
            print("multiplot call completed successfully.")
            assert True
        except Exception as e:
            pytest.fail(f"multiplot failed with exception: {e}")
        
        # Test showdahodo with x and y variables
        try:
            print(f"\n--- Testing showdahodo with FITS variables for trange: {test_trange} ---")
            showdahodo(test_trange, proton_fits_instance.np1, proton_fits_instance.beta_ppar_pfits)
            print("showdahodo call completed successfully.")
            assert True
        except Exception as e:
            pytest.fail(f"showdahodo failed with exception: {e}")

    def test_simple_datetime_deprecation(self):
        """
        Simple test to isolate and debug datetime deprecation warnings.
        Uses a short 10-minute time range and a single variable.
        """
        # Define a short 10-minute time range in the middle of our test day
        short_trange = ['2024-09-30/12:00:00.000', '2024-09-30/12:10:00.000']
        
        print(f"\n--- Starting simple datetime deprecation test with trange: {short_trange} ---")
        
        # Just call plotbot with a single variable to trigger the datetime conversion code
        try:
            # This will trigger the date handling code that produces the warnings
            plotbot(short_trange, proton_fits_instance.np1, 1) 
            print("Plotbot call completed successfully")
            
            # That's it! We're just looking at the warnings that get printed,
            # not analyzing the data
            
        except Exception as e:
            pytest.fail(f"Plotbot call failed with exception: {e}")

# Example: Add a simple test to check if the test file itself runs
def test_sanity():
    assert True 