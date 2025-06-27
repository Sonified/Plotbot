"""
Simple WIND 3DP PM plasma moments integration test following the working pattern from test_wind_mfi_simple.py
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to allow imports from plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import config
from plotbot.plotbot_main import plotbot
from plotbot.print_manager import print_manager

@pytest.mark.mission("WIND 3DP PM Test")
def test_wind_3dp_pm_download():
    """
    Tests the WIND 3DP PM plasma moments download functionality.
    1. Sets the data server to 'dynamic' (which should try SPDF first).
    2. Attempts to plot WIND 3DP PM data, which should trigger a download.
    3. Verifies that the plotbot call completes without error.
    """
    
    # Set print_manager verbosity for detailed test output
    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True
    print_manager.show_test = True
    
    print_manager.test(f"\n========================= TEST START: WIND 3DP PM =========================")
    print_manager.test("Testing WIND 3DP PM plasma moments data download and plotting.")
    print_manager.test("===========================================================================\n")

    # Define a time range that has both WIND and PSP data coverage  
    trange_strings = ['2022/06/01 20:00:00.000', '2022/06/02 02:00:00.000']
    print_manager.test(f"Using trange for WIND 3DP PM: {trange_strings}")
    
    # Configure server
    print_manager.test(f"\n--- Phase 1: Configuring server for WIND 3DP PM download ---")
    original_server = config.data_server
    config.data_server = 'spdf'  # WIND data comes from SPDF
    print_manager.test(f"Set config.data_server to: {config.data_server}")

    try:
        # Import WIND 3DP PM class and PSP proton components for comprehensive comparison
        from plotbot.data_classes.wind_3dp_pm_classes import wind_3dp_pm
        from plotbot import proton
        
        print_manager.test(f"Calling plotbot to test WIND 3DP PM plasma moments and PSP proton comparison...")
        # Plot comprehensive plasma moments comparison: WIND 3DP PM + PSP proton
        plotbot(trange_strings, 
                wind_3dp_pm.all_v, 1,        # WIND velocity components (vx, vy, vz)
                wind_3dp_pm.v_mag, 2,        # WIND velocity magnitude
                wind_3dp_pm.p_dens, 3,       # WIND proton density
                wind_3dp_pm.p_temp, 4,       # WIND proton temperature
                wind_3dp_pm.a_dens, 5,       # WIND alpha density
                wind_3dp_pm.a_temp, 6,       # WIND alpha temperature
                proton.density, 7,           # PSP proton density
                proton.temperature, 8)       # PSP proton temperature
        print_manager.test("Plotbot call completed successfully.")
        
    except Exception as e:
        print_manager.test(f"ERROR during plotbot call for WIND 3DP PM: {e}")
        config.data_server = original_server
        pytest.fail(f"Test failed during plotbot call for WIND 3DP PM: {e}")
    finally:
        config.data_server = original_server
        print_manager.test(f"Restored config.data_server to: {config.data_server}")
    
    print_manager.test(f"SUCCESS: WIND 3DP PM test passed. Plotbot call completed without error.")

if __name__ == "__main__":
    test_wind_3dp_pm_download() 