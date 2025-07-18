"""
Simple WIND MFI integration test following the working pattern from test_data_download.py
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to allow imports from plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import config
from plotbot.plotbot_main import plotbot
from plotbot.print_manager import print_manager

@pytest.mark.mission("WIND MFI Test")
def test_wind_mfi_download():
    """
    Tests the WIND MFI download functionality.
    1. Sets the data server to 'dynamic' (which should try SPDF first).
    2. Attempts to plot WIND MFI data, which should trigger a download.
    3. Verifies that the plotbot call completes without error.
    """
    
    # Set print_manager verbosity for detailed test output
    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True
    print_manager.show_test = True
    
    print_manager.test(f"\n========================= TEST START: WIND MFI =========================")
    print_manager.test("Testing WIND MFI data download and plotting.")
    print_manager.test("========================================================================\n")

    # Define a time range that has both WIND and PSP data coverage  
    trange_strings = ['2022/06/01 20:00:00.000', '2022/06/02 02:00:00.000']
    print_manager.test(f"Using trange for WIND MFI: {trange_strings}")
    
    # Configure server
    print_manager.test(f"\n--- Phase 1: Configuring server for WIND MFI download ---")
    original_server = config.data_server
    config.data_server = 'dynamic'  # This should try SPDF first
    print_manager.test(f"Set config.data_server to: {config.data_server}")

    try:
        # Import WIND MFI class and PSP mag components for comprehensive comparison
        from plotbot.data_classes.wind_mfi_classes import wind_mfi_h2
        from plotbot import mag_rtn_4sa
        
        print_manager.test(f"Calling plotbot to test all WIND xyz+mag and PSP rtn+mag components...")
        # Plot comprehensive comparison: WIND (x,y,z,mag) + PSP (r,t,n,mag)
        plotbot(trange_strings, 
                wind_mfi_h2.bx, 1,      # WIND Bx
                wind_mfi_h2.by, 2,      # WIND By  
                wind_mfi_h2.bz, 3,      # WIND Bz
                wind_mfi_h2.bmag, 4,    # WIND |B|
                mag_rtn_4sa.br, 5,      # PSP Br
                mag_rtn_4sa.bt, 6,      # PSP Bt
                mag_rtn_4sa.bn, 7,      # PSP Bn
                mag_rtn_4sa.bmag, 8)    # PSP |B|
        print_manager.test("Plotbot call completed successfully.")
        
    except Exception as e:
        print_manager.test(f"ERROR during plotbot call for WIND MFI: {e}")
        config.data_server = original_server
        pytest.fail(f"Test failed during plotbot call for WIND MFI: {e}")
    finally:
        config.data_server = original_server
        print_manager.test(f"Restored config.data_server to: {config.data_server}")
    
    print_manager.test(f"SUCCESS: WIND MFI test passed. Plotbot call completed without error.")

if __name__ == "__main__":
    test_wind_mfi_download() 