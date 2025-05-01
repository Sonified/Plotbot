import pytest
import cdflib
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Define paths for the test CDF file
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
CDF_DIR = TEST_DATA_DIR / 'psp_cdf_fits'
CDF_SF00_FILE = CDF_DIR / 'spp_swp_spi_sf00_fits_2024-04-01_v00.cdf'

@pytest.mark.skipif(not CDF_SF00_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF00_FILE}")
def test_direct_cdf_import():
    """Test direct CDF import to check if we can load the data correctly"""
    print(f"\nOpening CDF file: {CDF_SF00_FILE}")
    
    try:
        # Open the CDF file
        cdf = cdflib.CDF(CDF_SF00_FILE)
        
        # Get metadata
        info = cdf.cdf_info()
        print(f"CDF variables: {info.zVariables}")
        
        # Read the Epoch (time) data
        epoch_data = cdf.varget('Epoch')
        print(f"Epoch data type: {type(epoch_data)}")
        print(f"Epoch data shape: {epoch_data.shape}")
        print(f"First few Epoch values: {epoch_data[:5]}")
        
        # Convert to datetime
        epoch_datetime = cdflib.cdfepoch.to_datetime(epoch_data)
        print(f"Epoch datetime type: {type(epoch_datetime)}")
        print(f"First few datetime values: {epoch_datetime[:5]}")
        
        # Read n_tot data
        n_tot = cdf.varget('n_tot')
        print(f"n_tot data type: {type(n_tot)}")
        print(f"n_tot data shape: {n_tot.shape}")
        print(f"First few n_tot values: {n_tot[:5]}")
        
        # Check for NaN values
        nan_count = np.isnan(n_tot).sum()
        print(f"NaN count in n_tot: {nan_count} out of {len(n_tot)} ({nan_count/len(n_tot)*100:.2f}%)")
        
        # Simple visualization (optional)
        plt.figure(figsize=(10, 5))
        plt.plot(epoch_datetime, n_tot, '.')
        plt.title('n_tot from CDF file')
        plt.ylabel('Density (cm$^{-3}$)')
        plt.grid(True)
        plt.savefig('n_tot_test.png')
        plt.close()
        
        # Test passes if we can load and process the data
        assert epoch_data is not None and len(epoch_data) > 0
        assert n_tot is not None and len(n_tot) > 0
        
    except Exception as e:
        pytest.fail(f"Failed to import or process CDF data: {e}") 