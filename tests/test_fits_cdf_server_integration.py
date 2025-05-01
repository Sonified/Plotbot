import pytest
import cdflib
import pandas as pd
from pathlib import Path
import os

# Define paths relative to the test file location or project root
# Assuming tests run from project root
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
CDF_DIR = TEST_DATA_DIR / 'psp_cdf_fits'
LOCAL_CSV_DIR_BASE = Path('psp_data/sweap/spi_fits') # Relative to project root

# Example CDF files (Manually added by user)
CDF_SF00_FILE = CDF_DIR / 'spp_swp_spi_sf00_fits_2024-04-01_v00.cdf'
CDF_SF01_FILE = CDF_DIR / 'spp_swp_spi_sf01_fits_2024-04-01_v00.cdf'

# Example local CSV files (adjust date/path as needed)
# Using the 2024-09-30 files we found
LOCAL_CSV_SF00_FILE = LOCAL_CSV_DIR_BASE / 'sf00/p2/v00/2024/09/spp_swp_spi_sf00_2024-09-30_v00.csv'
LOCAL_CSV_SF01_FILE = LOCAL_CSV_DIR_BASE / 'sf01/p3/v00/2024/09/spp_swp_spi_sf01_2024-09-30_v00.csv'

# Reinstated skipif checks for CDF files
@pytest.mark.skipif(not CDF_SF00_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF00_FILE}")
@pytest.mark.skipif(not CDF_SF01_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF01_FILE}")
@pytest.mark.skipif(not LOCAL_CSV_SF00_FILE.exists(), reason=f"Test CSV file not found: {LOCAL_CSV_SF00_FILE}")
@pytest.mark.skipif(not LOCAL_CSV_SF01_FILE.exists(), reason=f"Test CSV file not found: {LOCAL_CSV_SF01_FILE}")
class TestFitsCdfIntegration:

    def test_placeholder(self):
        """Placeholder test to ensure the file runs."""
        assert True

    def test_compare_cdf_csv_variables(self):
        """Compares variable names from manually added CDFs and column headers from local CSVs."""
        print("\n--- Comparing SF00 Variables ---")
        
        # Read SF00 CDF Variables
        try:
            cdf_sf00 = cdflib.CDF(CDF_SF00_FILE)
            cdf_sf00_vars = list(cdf_sf00.cdf_info().zVariables) + list(cdf_sf00.cdf_info().rVariables)
            print(f"CDF SF00 Variables ({len(cdf_sf00_vars)}):\n{sorted(cdf_sf00_vars)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF00 CDF variables from {CDF_SF00_FILE}: {e}")

        # Read SF00 CSV Headers
        try:
            csv_sf00_headers = pd.read_csv(LOCAL_CSV_SF00_FILE, nrows=0).columns.tolist()
            print(f"\nCSV SF00 Headers ({len(csv_sf00_headers)}):\n{sorted(csv_sf00_headers)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF00 CSV headers: {e}")

        # --- Comparison for SF00 (Placeholder) ---
        # TODO: Add assertions later based on comparison
        print("\n[SF00 Comparison Pending]")
        
        print("\n\n--- Comparing SF01 Variables ---")
        
        # Read SF01 CDF Variables
        try:
            cdf_sf01 = cdflib.CDF(CDF_SF01_FILE)
            cdf_sf01_vars = list(cdf_sf01.cdf_info().zVariables) + list(cdf_sf01.cdf_info().rVariables)
            print(f"CDF SF01 Variables ({len(cdf_sf01_vars)}):\n{sorted(cdf_sf01_vars)}")
            
            # --- START TEMPORARY CODE TO INSPECT EPOCH vs EPOCH_1 ---
            print("\n--- Inspecting Epoch vs Epoch_1 ---")
            epoch_data = cdf_sf01.varget('Epoch')
            epoch1_data = cdf_sf01.varget('Epoch_1')
            
            if epoch_data is not None:
                print(f"Epoch (Type: {type(epoch_data)}, Shape: {epoch_data.shape}, DType: {epoch_data.dtype}):")
                print(f"  First 5 values: {epoch_data[:5]}")
                # Optional: Convert to datetime
                # epoch_dt = cdflib.cdfepoch.to_datetime(epoch_data[:5])
                # print(f"  First 5 datetimes: {epoch_dt}")
            else:
                print("Epoch data not found.")
                
            if epoch1_data is not None:
                print(f"\nEpoch_1 (Type: {type(epoch1_data)}, Shape: {epoch1_data.shape}, DType: {epoch1_data.dtype}):")
                print(f"  First 5 values: {epoch1_data[:5]}")
                # Optional: Convert to datetime
                # epoch1_dt = cdflib.cdfepoch.to_datetime(epoch1_data[:5])
                # print(f"  First 5 datetimes: {epoch1_dt}")
            else:
                print("Epoch_1 data not found.")
            print("--- END TEMPORARY CODE --- \n")
            # --- END TEMPORARY CODE ---
            
        except Exception as e:
            pytest.fail(f"Failed to read SF01 CDF variables from {CDF_SF01_FILE}: {e}")

        # Read SF01 CSV Headers
        try:
            csv_sf01_headers = pd.read_csv(LOCAL_CSV_SF01_FILE, nrows=0).columns.tolist()
            print(f"\nCSV SF01 Headers ({len(csv_sf01_headers)}):\n{sorted(csv_sf01_headers)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF01 CSV headers: {e}")
            
        # --- Comparison for SF01 (Placeholder) ---
        # TODO: Add assertions later based on comparison
        print("\n[SF01 Comparison Pending]")

        # Keep test passing for now until we analyze output
        assert True 