"""
Tests for Alpha FITS data integration and calculations.

Focuses on:
- Finding and loading SF01 FITS CSV files.
- Running calculations within the alpha_fits_class.
- Integrating alpha_fits variables with plotbot, multiplot, and showdahodo.
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

# Define path relative to workspace root
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
psp_data_dir = os.path.join(_project_root, "psp_data")

if not os.path.isdir(psp_data_dir):
    print(f"Warning: Default PSP data directory '{psp_data_dir}' not found. Tests requiring local data may fail.")

# Import necessary components from plotbot
from plotbot import plotbot, multiplot, showdahodo
# Import the ALPHA FITS instance
from plotbot.data_classes.psp_alpha_fits_classes import alpha_fits as alpha_fits_instance
from plotbot.data_import import find_local_csvs
from plotbot.plot_manager import plot_manager
from plotbot.print_manager import print_manager
from plotbot.plotbot_helpers import time_clip

# Set up logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Test Helper Function (Copied from test_fits_integration) ---

def find_psp_csv_files(trange, data_type):
    """
    Finds PSP CSV data files based on a time range and data type ('sf00' or 'sf01'),
    following the specified directory structure relative to the project root.
    e.g., psp_data/sweap/spi_fits/sf01/p3/v00/YYYY/MM/spp_swp_spi_sf01_YYYY-MM-DD_v00.csv
    """
    found_files = []
    try:
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
    if data_type == 'sf00': # Kept for potential future use, but focus is sf01
        base_rel_path = Path('psp_data/sweap/spi_fits/sf00/p2/v00')
        prefix = 'spp_swp_spi_sf00_'
        suffix = '_v00.csv'
    elif data_type == 'sf01':
        base_rel_path = Path('psp_data/sweap/spi_fits/sf01/p3/v00')
        prefix = 'spp_swp_spi_sf01_'
        suffix = '_v00.csv'
    else:
        raise ValueError("Invalid data_type specified. Must be 'sf00' or 'sf01'.")

    # Iterate through dates in the range (inclusive)
    current_dt = start_dt
    while current_dt <= end_dt:
        year_str = current_dt.strftime('%Y')
        month_str = current_dt.strftime('%m')
        date_str_file = current_dt.strftime('%Y-%m-%d') # Format for filename

        # Construct the expected file path relative to project root
        file_path = _project_root / base_rel_path / year_str / month_str / f"{prefix}{date_str_file}{suffix}"

        if file_path.exists():
            found_files.append(str(file_path)) # Store as string
        else:
            print(f"Info: File not found at expected path: {file_path}")

        current_dt += timedelta(days=1)

    return found_files


# Simple structure to mimic DataObject for testing internal calculation
AlphaFitsTestDataContainer = namedtuple('AlphaFitsTestDataContainer', ['times', 'data'])

class TestAlphaFitsIntegration:
    """Test suite for Alpha FITS data integration, calculation, and plotting."""

    # Use the same test range as proton fits for consistency
    TEST_TRANGE = ['2024-09-30/11:45:00.000', '2024-09-30/12:45:00.000']
    TEST_DAY = '20240930'
    EXPECTED_DATE_STR = '2024-09-30'

    @classmethod
    def setup_class(cls):
        """Set up for the test class. Ensures alpha_fits instance options are fresh."""
        print("\n--- TestAlphaFitsIntegration Class Setup ---")
        try:
            print("Re-running alpha_fits_instance.set_ploptions() to ensure fresh options...")
            alpha_fits_instance.set_ploptions()
            print("alpha_fits_instance.set_ploptions() completed.")
        except Exception as e:
            pytest.fail(f"Failed to re-run alpha_fits_instance.set_ploptions() during setup: {e}")
        print("--- End TestAlphaFitsIntegration Class Setup ---")

    # --- Test: Finding and Loading SF01 --- 
    def test_find_and_load_sf01_csv(self):
        """Tests finding and loading SF01 (alpha) CSV files for the test trange."""
        found_files = find_psp_csv_files(self.TEST_TRANGE, 'sf01')
        assert len(found_files) > 0, f"No SF01 CSV files found for trange {self.TEST_TRANGE}. Expected at least one file containing date {self.EXPECTED_DATE_STR}. Searched paths like psp_data/sweap/spi_fits/sf01/p3/v00/YYYY/MM/..."
        try:
            df_sf01 = pd.concat((pd.read_csv(f) for f in found_files), ignore_index=True)
            assert not df_sf01.empty
            print(f"Successfully loaded {len(found_files)} SF01 file(s) for {self.TEST_TRANGE}")
            print(df_sf01.head())
        except Exception as e:
            pytest.fail(f"Failed to load/concat SF01 CSVs {found_files}: {e}")

    # --- Test: Calculate Alpha Variables --- 
    @pytest.fixture(scope='class')
    def sf01_test_data(self):
        """Fixture to load raw SF01 CSV data for calculation tests."""
        print("--- Loading SF01 Test Data Fixture ---")
        # Use the helper function defined within this test file
        found_files = find_psp_csv_files(self.TEST_TRANGE, 'sf01')
        if not found_files:
            pytest.skip("Skipping SF01 calculation test: No input files found.")
            return None
        try:
            df_sf01_raw = pd.concat((pd.read_csv(f) for f in found_files), ignore_index=True)
            if df_sf01_raw.empty:
                 pytest.skip("Skipping SF01 calculation test: Loaded DataFrame is empty.")
                 return None
            print(f"Loaded SF01 test data, shape: {df_sf01_raw.shape}")
            return df_sf01_raw
        except Exception as e:
            pytest.fail(f"Failed to load/concat SF01 CSVs {found_files}: {e}")
            return None

    def test_calculate_alpha_vars(self, sf01_test_data):
        """Test the calculation of derived variables triggered by updating the alpha_fits_instance."""
        assert sf01_test_data is not None, "Test setup failed: sf01_test_data fixture did not return data"
        assert not sf01_test_data.empty, "Test setup failed: sf01_test_data DataFrame provided by fixture is empty"
        print("--- Running Alpha Internal Calculation Test ---")

        # --- Prepare DataObject --- (Similar to proton fits, using sf01 data)
        try:
            unix_times = sf01_test_data['time'].to_numpy()
            datetime_objs_pd = pd.to_datetime(unix_times, unit='s', utc=True)
            datetime_components_list = [
                [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)]
                for dt in datetime_objs_pd
            ]
            tt2000_times = cdflib.cdfepoch.compute_tt2000(datetime_components_list)
            if not isinstance(tt2000_times, np.ndarray):
                tt2000_times = np.array(tt2000_times)
            
            # Create data dict specifically from SF01 columns
            data_dict = {col: sf01_test_data[col].to_numpy() for col in sf01_test_data.columns if col != 'time'}
            for key in data_dict:
                 data_dict[key] = np.array(data_dict[key])
            
            test_data_obj = AlphaFitsTestDataContainer(times=tt2000_times, data=data_dict)
            print(f"Prepared Alpha TestDataObject with {len(tt2000_times)} time points.")
        except Exception as e:
            pytest.fail(f"Failed to prepare Alpha TestDataObject: {e}")

        # --- Trigger Calculation via Update --- 
        try:
            alpha_fits_instance.update(test_data_obj)
            print("Called alpha_fits_instance.update()")
        except Exception as e:
             pytest.fail(f"alpha_fits_instance.update() failed: {e}\nTraceback: {traceback.format_exc()}")

        # --- Assertions --- 
        # Check that specific calculated alpha attributes now have data
        assert hasattr(alpha_fits_instance, 'va_mag'), "Attribute 'va_mag' not found on instance."
        assert alpha_fits_instance.va_mag.data is not None, "va_mag.data is None after update."
        assert not np.all(np.isnan(alpha_fits_instance.va_mag.data)), "va_mag.data contains only NaNs."
        
        assert hasattr(alpha_fits_instance, 'Tpara'), "Attribute 'Tpara' not found on instance."
        assert alpha_fits_instance.Tpara.data is not None, "Tpara.data is None after update."
        assert not np.all(np.isnan(alpha_fits_instance.Tpara.data)), "Tpara.data contains only NaNs."

        # Check chi_a was populated (assuming 'chi' was in source CSV)
        if 'chi' in sf01_test_data.columns:
            assert hasattr(alpha_fits_instance, 'chi_a'), "Attribute 'chi_a' not found on instance."
            assert alpha_fits_instance.chi_a.data is not None, "chi_a.data is None after update."
            # assert not np.all(np.isnan(alpha_fits_instance.chi_a.data)), "chi_a.data contains only NaNs."
        else:
            print("Skipping chi_a check as 'chi' not in source test data.")

        assert len(alpha_fits_instance.datetime_array) == len(tt2000_times), \
               f"datetime_array length ({len(alpha_fits_instance.datetime_array)}) doesn't match input ({len(tt2000_times)})."

        print("Alpha internal calculations appear successful. Data populated.")

    # --- Test Plotbot with Alpha FITS Variables --- 
    def test_plotbot_with_alpha_fits(self):
        """Tests calling plotbot with alpha_fits variable instances."""
        test_trange = self.TEST_TRANGE
        try:
            print(f"Attempting plotbot call for trange: {test_trange} with alpha_fits.na and alpha_fits.va_mag")
            # Call plotbot with alpha FITS instances
            plotbot(test_trange,
                    alpha_fits_instance.na, 1,
                    alpha_fits_instance.va_mag, 2,
                    alpha_fits_instance.Tperpa, 3 # Using Tperpa from sf01 (mapped from Ta_perp)
                   )
            print("Plotbot call completed successfully.")
            assert True

            # --- Verify Data Availability --- 
            print("--- Verifying Alpha Data Availability Post-Plotbot Call ---")
            vars_to_check = {
                'na': alpha_fits_instance.na,
                'va_mag': alpha_fits_instance.va_mag,
                'Tperpa': alpha_fits_instance.Tperpa
            }
            for name, var_instance in vars_to_check.items():
                assert var_instance is not None, f"alpha_fits.{name} instance is None"
                assert hasattr(var_instance, 'datetime_array') and var_instance.datetime_array is not None, f"alpha_fits.{name}.datetime_array is None"
                assert hasattr(var_instance, 'data') and var_instance.data is not None, f"alpha_fits.{name}.data is None"
                try:
                    indices = time_clip(var_instance.datetime_array, test_trange[0], test_trange[1])
                except Exception as e:
                     pytest.fail(f"time_clip failed for {name}: {e}")
                assert len(indices) > 0, f"Variable '{name}' found 0 data points in range {test_trange}"
                try:
                     clipped_data = np.array(var_instance.data)[indices]
                     assert not np.all(np.isnan(clipped_data)), f"Variable '{name}' has only NaN values in range {test_trange}"
                except Exception as e:
                     pytest.fail(f"Error checking NaN for '{name}': {e}")
                print(f"✅ Variable '{name}' has data and {len(indices)} valid points in range.")
            print("--- End Alpha Data Availability Verification ---")

        except Exception as e:
            pytest.fail(f"plotbot call failed with exception: {e}\nTraceback: {traceback.format_exc()}")

    # --- Test Multiplot and Showdahodo with Alpha FITS --- 
    def test_multiplot_and_showdahodo_with_alpha_fits(self):
        """Test multiplot and showdahodo functions with alpha FITS variables."""
        test_trange = self.TEST_TRANGE
        # Ensure data is loaded first
        plotbot(test_trange, alpha_fits_instance.na, 1)
        
        # Test multiplot
        try:
            center_time = pd.Timestamp(test_trange[0]) + (pd.Timestamp(test_trange[1]) - pd.Timestamp(test_trange[0])) / 2
            center_time_str = center_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
            plot_list = [
                (center_time_str, alpha_fits_instance.na),
                (center_time_str, alpha_fits_instance.va_mag) 
            ]
            print(f"\n--- Testing multiplot with Alpha FITS variables for center time: {center_time_str} ---")
            multiplot(plot_list)
            print("multiplot call completed successfully.")
            assert True
        except Exception as e:
            pytest.fail(f"multiplot failed with exception: {e}")
        
        # Test showdahodo
        try:
            print(f"\n--- Testing showdahodo with Alpha FITS variables for trange: {test_trange} ---")
            showdahodo(test_trange, alpha_fits_instance.na, alpha_fits_instance.va_mag)
            print("showdahodo call completed successfully.")
            assert True
        except Exception as e:
            pytest.fail(f"showdahodo failed with exception: {e}")

# Simple sanity check
def test_sanity_alpha():
    assert True 