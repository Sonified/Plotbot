import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
import os
import sys
import pandas as pd

# Attempt to import plotbot components
try:
    from plotbot import plotbot, proton, mag_rtn_4sa
    from plotbot.multiplot_options import plt
    from plotbot.print_manager import print_manager
    from plotbot.time_utils import str_to_datetime
    PLOTBOT_AVAILABLE = True
except ImportError as e:
    print(f"ImportError in test_proton_trange_updates: {e}")
    PLOTBOT_AVAILABLE = False

# Global flag for debugging
DEBUG_FORCE_STOP_IN_GET_DATA_CALL2 = False

# Helper to ensure datetime is UTC
def ensure_utc(dt_obj):
    if dt_obj is None:
        return None
    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)

# Path for the log file for this specific test
log_file_path = os.path.join(os.path.dirname(__file__), "test_logs", "test_two_call_incorrect_merged_trange.txt")

# Helper function to print to both console and log file
def dual_print(message, log_file=None):
    # Print to console
    print(message, flush=True)
    # Write to log file if provided
    if log_file:
        with open(log_file, "a") as f:
            f.write(message + "\n")

@pytest.mark.skipif(not PLOTBOT_AVAILABLE, reason="Plotbot components not available")
def test_two_call_incorrect_merged_trange(capsys):
    """
    Tests the scenario:
    1. Plot TRANGE_LATER (proton, mag)
    2. Plot TRANGE_EARLIER (proton, mag)
    Observe if get_data for proton in the second call uses an incorrectly merged trange.
    """
    global DEBUG_FORCE_STOP_IN_GET_DATA_CALL2
    print_manager.show_debug = False  # Changed from True to False
    print_manager.show_dependency_management = True
    print_manager.show_datacubby = True

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    with open(log_file_path, "w") as f:
        f.write("Log for test_two_call_incorrect_merged_trange\n")
        f.write("="*70 + "\n")

    TRANGE1_STR = ['2023-09-28/00:00:00.000', '2023-09-29/00:00:00.000']
    TRANGE2_STR = ['2023-09-26/00:00:00.000', '2023-09-26/00:01:00.000']
    
    # Using -s flag with pytest will show print output directly
    dual_print(f"\n--- CALL 1: TRANGE1_STR ({TRANGE1_STR}) with proton.sun_dist_rsun, mag_rtn_4sa.br_norm ---", log_file_path)
    plt.close('all')
    plotbot(TRANGE1_STR, proton.sun_dist_rsun, 1, mag_rtn_4sa.br_norm, 2)
    dual_print(f"Completed CALL 1.", log_file_path)

    # Capture output from first call to add to log
    captured_out1, captured_err1 = capsys.readouterr()
    with open(log_file_path, "a") as f:
        f.write("\n=== STDOUT CAPTURE FROM CALL 1 ===\n")
        f.write(captured_out1)
        if captured_err1:
            f.write("\n=== STDERR CAPTURE FROM CALL 1 ===\n")
            f.write(captured_err1)
    
    # Write captured output to console as well
    sys.stdout.write("\n=== CAPTURED OUTPUT FROM CALL 1 (re-displaying) ===\n")
    sys.stdout.write(captured_out1)
    sys.stdout.flush()
    if captured_err1:
        sys.stderr.write("\n=== CAPTURED STDERR FROM CALL 1 (re-displaying) ===\n")
        sys.stderr.write(captured_err1)
        sys.stderr.flush()

    # --- Call 2: TRANGE2_STR ---
    dual_print(f"\n--- CALL 2: TRANGE2_STR ({TRANGE2_STR}) with proton.sun_dist_rsun, mag_rtn_4sa.br_norm ---", log_file_path)
    dual_print(f"DEBUG_FORCE_STOP_IN_GET_DATA_CALL2 set to {DEBUG_FORCE_STOP_IN_GET_DATA_CALL2}", log_file_path)
    plt.close('all')
    plotbot(TRANGE2_STR, proton.sun_dist_rsun, 1, mag_rtn_4sa.br_norm, 2)
    
    # Reset the flag
    DEBUG_FORCE_STOP_IN_GET_DATA_CALL2 = False
    dual_print(f"DEBUG_FORCE_STOP_IN_GET_DATA_CALL2 reset to {DEBUG_FORCE_STOP_IN_GET_DATA_CALL2}", log_file_path)
    dual_print(f"Completed CALL 2 (or it was intelligently stopped).", log_file_path)

    # Capture output from second call 
    captured_out2, captured_err2 = capsys.readouterr()
    with open(log_file_path, "a") as f:
        f.write("\n=== STDOUT CAPTURE FROM CALL 2 ===\n")
        f.write(captured_out2)
        if captured_err2:
            f.write("\n=== STDERR CAPTURE FROM CALL 2 ===\n")
            f.write(captured_err2)
    
    # Write captured output to console as well
    sys.stdout.write("\n=== CAPTURED OUTPUT FROM CALL 2 (re-displaying) ===\n")
    sys.stdout.write(captured_out2)
    sys.stdout.flush()
    if captured_err2:
        sys.stderr.write("\n=== CAPTURED STDERR FROM CALL 2 (re-displaying) ===\n")
        sys.stderr.write(captured_err2)
        sys.stderr.flush()

    dual_print("\n--- Test sequence completed. ---", log_file_path)
    dual_print(f"Inspect log: {log_file_path}", log_file_path)
    dual_print(f"Look for '[GET_DATA_ENTRY]' calls for 'spi_sf00_l3_mom'.", log_file_path)
    dual_print(f"Check the 'trange' passed to get_data or used by DataTracker for those calls.", log_file_path)
    dual_print(f"The problematic merged trange seen in user logs was approx: ['{TRANGE2_STR[0]}', '{TRANGE1_STR[1]}']", log_file_path) 