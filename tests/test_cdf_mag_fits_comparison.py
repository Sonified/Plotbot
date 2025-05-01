import pytest
import cdflib
import numpy as np
import os

# --- Configuration ---

# Use environment variable or default path
PLOTBOT_DATA_ROOT = os.environ.get("PLOTBOT_DATA_DIR", "/Users/robertalexander/GitHub/Plotbot/psp_data") 

FITS_CDF_REL_PATH = "sweap/spi_fits/sf00/p2/v00/2024/spp_swp_spi_sf00_fits_2024-04-01_v00.cdf"
MAG_CDF_REL_PATH = "fields/l2/mag_rtn_4_per_cycle/2024/psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20240327_v02.cdf"

FITS_CDF_PATH = os.path.join(PLOTBOT_DATA_ROOT, FITS_CDF_REL_PATH)
MAG_CDF_PATH = os.path.join(PLOTBOT_DATA_ROOT, MAG_CDF_REL_PATH)


FITS_TIME_VAR = 'Epoch'         # Time variable for FITS
MAG_TIME_VAR = 'epoch_mag_RTN_4_Sa_per_Cyc' # Corrected time variable for MAG
FITS_DATA_VAR = 'n_tot'       # Data variable for the FITS file
MAG_DATA_VAR = 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc' # Primary data variable for the MAG file

# Helper function to print details cleanly
def print_var_details(file_label, cdf_obj, var_name):
    print(f"--- Details for: {file_label} - Variable: '{var_name}' ---")
    if not isinstance(cdf_obj, cdflib.CDF):
        print("  ERROR: Invalid CDF object provided.")
        return
    try:
        var_info = cdf_obj.varinq(var_name)
        print(f"  varinq():")
        # <<< CORRECTED >>> Print attributes directly from namedtuple
        # Print varinq attributes neatly
        # Use vars() or dir() and getattr() for namedtuples
        for attr in var_info._fields: 
             value = getattr(var_info, attr)
             print(f"    {attr}: {value}")
             
        var_data = cdf_obj.varget(var_name)
        print(f"\n  varget() Results:")
        print(f"    Python Type: {type(var_data)}")
        if isinstance(var_data, np.ndarray):
            print(f"    Numpy dtype: {var_data.dtype}")
            print(f"    Shape: {var_data.shape}")
            if var_data.size > 0:
                # Handle multi-dimensional arrays for preview
                preview = var_data.reshape(-1)[:3] 
                print(f"    First 3 Values (flattened): {preview}")
            else:
                print("    Data Array is Empty.")
        elif var_data is None:
             print("    Data is None.")
        else:
            # Should typically be numpy array for scientific data
            print(f"    Value (if not array): {var_data}") 
            
    except Exception as e:
        print(f"  ERROR retrieving details for '{var_name}': {e}")
    finally:
        print("-" * 60) # Divider

# The actual test function
def test_compare_cdf_structure_and_data():
    print("\n=== Comparing CDF Structures and Data ===")
    fits_cdf = None
    mag_cdf = None

    # --- Load Files ---
    print(f"Attempting to load FITS CDF: {FITS_CDF_PATH}")
    if not os.path.exists(FITS_CDF_PATH):
         pytest.fail(f"FITS CDF file not found at: {FITS_CDF_PATH}")
    try:
        fits_cdf = cdflib.CDF(FITS_CDF_PATH)
        print("FITS CDF Loaded Successfully.")
    except Exception as e:
        pytest.fail(f"Failed to load FITS CDF '{FITS_CDF_PATH}': {e}")

    print(f"\nAttempting to load MAG CDF: {MAG_CDF_PATH}")
    if not os.path.exists(MAG_CDF_PATH):
         pytest.fail(f"MAG CDF file not found at: {MAG_CDF_PATH}")
    try:
        mag_cdf = cdflib.CDF(MAG_CDF_PATH)
        print("MAG CDF Loaded Successfully.")
        
        # <<< ADDED: Inspect MAG CDF Variables >>>
        mag_info = mag_cdf.cdf_info()
        print("\n--- MAG CDF Variables --- ")
        mag_vars = mag_info.zVariables + mag_info.rVariables 
        if mag_vars:
            print("Available variables:", mag_vars)
        else:
            print("Could not retrieve variable list from MAG CDF.")
        # <<< END ADDED >>>
            
    except Exception as e:
        pytest.fail(f"Failed to load MAG CDF '{MAG_CDF_PATH}': {e}")

    # --- Compare TIME Variable ---
    print(f"\n=== Comparing TIME Variables ('{FITS_TIME_VAR}' vs '{MAG_TIME_VAR}') ===")
    print_var_details("FITS CDF", fits_cdf, FITS_TIME_VAR)
    print_var_details("MAG CDF", mag_cdf, MAG_TIME_VAR)

    # --- Compare DATA Variables ---
    print(f"\n=== Comparing DATA Variables ('{FITS_DATA_VAR}' vs '{MAG_DATA_VAR}') ===")
    print_var_details("FITS CDF", fits_cdf, FITS_DATA_VAR)
    print_var_details("MAG CDF", mag_cdf, MAG_DATA_VAR)

    # --- Add Basic Assertions ---
    print("\n=== Basic Assertions ===")
    try:
        fits_epoch_info = fits_cdf.varinq(FITS_TIME_VAR)
        mag_epoch_info = mag_cdf.varinq(MAG_TIME_VAR)
        
        # Assert both Epoch variables are CDF_EPOCH type
        assert fits_epoch_info.Data_Type == 31, f"FITS Epoch Data_Type is {fits_epoch_info.Data_Type}, expected 31 (CDF_EPOCH)"
        print("✅ FITS Epoch Data_Type is CDF_EPOCH (31).")
        assert mag_epoch_info.Data_Type == 31, f"MAG Epoch Data_Type is {mag_epoch_info.Data_Type}, expected 31 (CDF_EPOCH)"
        print("✅ MAG Epoch Data_Type is CDF_EPOCH (31).")

        # Assert both Epoch variables are record-varying
        assert fits_epoch_info.Rec_Vary is True, "FITS Epoch should be Record Varying (True)"
        print("✅ FITS Epoch Rec_Vary is True.")
        assert mag_epoch_info.Rec_Vary is True, "MAG Epoch should be Record Varying (True)"
        print("✅ MAG Epoch Rec_Vary is True.")

        # Check data types of retrieved Epoch arrays
        fits_epoch_data = fits_cdf.varget(FITS_TIME_VAR)
        mag_epoch_data = mag_cdf.varget(MAG_TIME_VAR)
        assert isinstance(fits_epoch_data, np.ndarray), "FITS Epoch data should be a numpy array"
        print("✅ FITS Epoch data is numpy array.")
        assert isinstance(mag_epoch_data, np.ndarray), "MAG Epoch data should be a numpy array"
        print("✅ MAG Epoch data is numpy array.")
        
        # Note: We don't assert dtype equality here as cdflib might return different
        # precision float types depending on the underlying CDF EPOCH type. 
        # The key is that cdflib.cdfepoch.to_datetime handles them.

    except Exception as e:
        pytest.fail(f"Assertion error during checks: {e}")

    print("\nComparison Test Completed.")
    # No cdf.close() needed based on previous findings 