import pytest
import cdflib
import numpy as np
import os
from pathlib import Path
import matplotlib.dates as mdates

# Define path relative to workspace root
# Assuming tests run from project root /Users/robertalexander/GitHub/Plotbot
FILE_PATH_STR = "tests/test_data/psp_cdf_fits/spp_swp_spi_sf00_fits_2024-04-01_v00.cdf"
FILE_PATH_ABS = os.path.abspath(FILE_PATH_STR)

@pytest.mark.skipif(not os.path.exists(FILE_PATH_ABS), reason=f"Test CDF file not found: {FILE_PATH_ABS}")
def test_check_fits_cdf_time_range():
    """Checks the actual time range within the sf00_fits test CDF file."""
    try:
        print(f"\n--- Checking Time Range in CDF: {FILE_PATH_ABS} ---")
        with cdflib.CDF(FILE_PATH_ABS) as cdf_file:
            print("CDF file opened successfully.")
            
            if 'Epoch' in cdf_file.cdf_info().zVariables:
                print("Reading 'Epoch' variable...")
                epoch_data_tt2000 = cdf_file.varget('Epoch')
                
                if epoch_data_tt2000 is not None and len(epoch_data_tt2000) > 0:
                    print(f"Read {len(epoch_data_tt2000)} epoch values.")
                    print("Converting Epoch to datetime...")
                    epoch_datetime = cdflib.cdfepoch.to_datetime(epoch_data_tt2000)
                    print("Conversion complete.")

                    min_time = np.min(epoch_datetime)
                    max_time = np.max(epoch_datetime)
                    
                    print(f"Min time in CDF: {min_time}")
                    print(f"Max time in CDF: {max_time}")
                    
                    # Add an assertion just to make it a real test
                    assert min_time < max_time, "Min time should be less than max time"
                    
                else:
                    pytest.fail("Epoch variable is empty or could not be read.")
            else:
                pytest.fail("'Epoch' variable not found in the CDF file.")
            
    except Exception as e:
        pytest.fail(f"Error processing CDF file: {e}")

# <<< NEW TEST >>>
def test_direct_matplotlib_scatter():
    """Directly plots n_tot vs Epoch from the test CDF using Matplotlib."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    print(f"\n--- Testing Direct Matplotlib Scatter from CDF: {FILE_PATH_ABS} ---")
    
    try:
        with cdflib.CDF(FILE_PATH_ABS) as cdf_file:
            print("Reading Epoch and n_tot...")
            epoch_tt2000 = cdf_file.varget('Epoch')
            n_tot_data = cdf_file.varget('n_tot')
            
            if epoch_tt2000 is None or n_tot_data is None:
                pytest.fail("Could not read Epoch or n_tot from CDF.")
                
            print("Converting Epoch...")
            # Ensure datetime64[ns] for consistency with plotbot
            epoch_dt64 = np.array(cdflib.cdfepoch.to_datetime(epoch_tt2000), dtype='datetime64[ns]')
            
            print(f"Data shapes - Time: {epoch_dt64.shape}, n_tot: {n_tot_data.shape}")
            assert epoch_dt64.shape == n_tot_data.shape, "Time and data shape mismatch"
            
            # <<< CHANGE: Convert datetime64 to numerical format for plotting >>>
            epoch_nums = mdates.date2num(epoch_dt64)
            print(f"Converted datetimes to numbers (dtype: {epoch_nums.dtype}). First few: {epoch_nums[:3]}")
            
            # Create plot directly
            print("Creating plot with plt.scatter...")
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # Use large markers like we tried in plotbot
            ax.scatter(epoch_nums, n_tot_data, label='n_tot (Direct)', color='red', s=25, alpha=1.0, marker='o')
            
            ax.set_xlabel("Time (Epoch)")
            ax.set_ylabel("n_tot")
            ax.set_title("Direct Matplotlib Scatter Test")
            ax.legend()
            
            # Format x-axis for dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            fig.autofmt_xdate()
            
            save_path = Path(__file__).parent / "test_direct_matplotlib_scatter.png"
            plt.savefig(save_path)
            print(f"Direct scatter plot saved to: {save_path}")
            plt.close(fig) # Close the figure
            
            # Simple assertion
            assert True
            
    except Exception as e:
        pytest.fail(f"Error during direct scatter plot test: {e}") 