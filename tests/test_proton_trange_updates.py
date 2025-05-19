import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
import os
import sys
import pandas as pd

# Attempt to import plotbot components
try:
    from plotbot import plotbot, proton # Removed mag_rtn_4sa from this direct import
    from plotbot.multiplot_options import plt 
    from plotbot.print_manager import print_manager
    from plotbot.time_utils import str_to_datetime # Changed to str_to_datetime
    # If mag_rtn_4sa is needed as a type or for specific tests later, 
    # consider importing its class: from plotbot.data_classes.psp_mag_rtn_4sa import mag_rtn_4sa_class
    PLOTBOT_AVAILABLE = True
except ImportError as e: # Add 'as e' to see the import error if it occurs
    print(f"ImportError in test_proton_trange_updates: {e}") # Print the error
    PLOTBOT_AVAILABLE = False

# Helper to ensure datetime is UTC
def ensure_utc(dt_obj):
    if dt_obj is None:
        return None
    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)

# Path for the log file for this specific test
log_file_path = os.path.join(os.path.dirname(__file__), "test_logs", "test_proton_trange_updates.txt")

@pytest.mark.skipif(not PLOTBOT_AVAILABLE, reason="Plotbot components not available")
def test_proton_datetime_updates_with_plotbot(capsys):
    """
    Tests if the global proton instance's datetime_array is correctly updated
    when plotbot is called sequentially with different, non-overlapping time ranges.
    """
    print_manager.show_debug = True
    print_manager.show_dependency_management = True # For detailed cubby/get_data logs
    print_manager.show_datacubby = True # Enable instance-level datacubby prints
    # print_manager.DATACUBBY = True      # Enable class-level datacubby prints (just in case)

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    # Clear previous log file content for this specific test
    with open(log_file_path, "w") as f:
        f.write("Log for test_proton_datetime_updates_with_plotbot\n")
        f.write("="*50 + "\n")

    TRANGE1_STR = ['2023-09-27/00:00:00.000', '2023-09-27/01:00:00.000']
    TRANGE2_STR = ['2023-09-28/00:00:00.000', '2023-09-28/01:00:00.000']

    # Convert string tranges to datetime objects for assertions
    TRANGE1_DT = [ensure_utc(str_to_datetime(TRANGE1_STR[0])), ensure_utc(str_to_datetime(TRANGE1_STR[1]))]
    TRANGE2_DT = [ensure_utc(str_to_datetime(TRANGE2_STR[0])), ensure_utc(str_to_datetime(TRANGE2_STR[1]))]
    
    tolerance = timedelta(seconds=5) # Tolerance for time comparisons

    # --- First plotbot call ---
    print(f"\n--- Calling plotbot with TRANGE1: {TRANGE1_STR} ---")
    plt.close('all')
    plotbot(TRANGE1_STR, proton.sun_dist_rsun, 1)
    
    assert hasattr(proton, 'datetime_array'), "proton should have datetime_array after first plotbot call."
    assert proton.datetime_array is not None, "proton.datetime_array should not be None after first plotbot call."
    assert len(proton.datetime_array) > 0, "proton.datetime_array should not be empty after first plotbot call."
    
    # Convert numpy.datetime64 to Python datetime and ensure UTC for comparison
    proton_dt_min1 = ensure_utc(pd.Timestamp(proton.datetime_array.min()).to_pydatetime())
    proton_dt_max1 = ensure_utc(pd.Timestamp(proton.datetime_array.max()).to_pydatetime())
    
    print(f"TRANGE1: Start={TRANGE1_DT[0]}, End={TRANGE1_DT[1]}")
    print(f"Proton after TRANGE1: Min={proton_dt_min1}, Max={proton_dt_max1}")

    assert TRANGE1_DT[0] - tolerance <= proton_dt_min1 <= TRANGE1_DT[1] + tolerance, f"Proton min time {proton_dt_min1} out of TRANGE1 {TRANGE1_DT} (with tolerance)"
    assert TRANGE1_DT[0] - tolerance <= proton_dt_max1 <= TRANGE1_DT[1] + tolerance, f"Proton max time {proton_dt_max1} out of TRANGE1 {TRANGE1_DT} (with tolerance)"

    # --- Second plotbot call ---
    print(f"\n--- Calling plotbot with TRANGE2: {TRANGE2_STR} ---")
    plt.close('all')
    plotbot(TRANGE2_STR, proton.sun_dist_rsun, 1)

    assert hasattr(proton, 'datetime_array'), "proton should have datetime_array after second plotbot call."
    assert proton.datetime_array is not None, "proton.datetime_array should not be None after second plotbot call."
    assert len(proton.datetime_array) > 0, "proton.datetime_array should not be empty after second plotbot call."

    proton_dt_min2 = ensure_utc(pd.Timestamp(proton.datetime_array.min()).to_pydatetime())
    proton_dt_max2 = ensure_utc(pd.Timestamp(proton.datetime_array.max()).to_pydatetime())

    print(f"TRANGE2: Start={TRANGE2_DT[0]}, End={TRANGE2_DT[1]}")
    print(f"Proton after TRANGE2: Min={proton_dt_min2}, Max={proton_dt_max2}")

    assert TRANGE2_DT[0] - tolerance <= proton_dt_min2 <= TRANGE2_DT[1] + tolerance, f"Proton min time {proton_dt_min2} out of TRANGE2 {TRANGE2_DT} (with tolerance)"
    assert TRANGE2_DT[0] - tolerance <= proton_dt_max2 <= TRANGE2_DT[1] + tolerance, f"Proton max time {proton_dt_max2} out of TRANGE2 {TRANGE2_DT} (with tolerance)"

    # Crucially, assert that the new times are NOT within the old range (unless TRANGE1 and TRANGE2 overlap significantly, which they don't here)
    assert not (TRANGE1_DT[0] - tolerance <= proton_dt_min2 <= TRANGE1_DT[1] + tolerance), f"Proton min time {proton_dt_min2} after TRANGE2 call is still within TRANGE1 {TRANGE1_DT}"
    assert not (TRANGE1_DT[0] - tolerance <= proton_dt_max2 <= TRANGE1_DT[1] + tolerance), f"Proton max time {proton_dt_max2} after TRANGE2 call is still within TRANGE1 {TRANGE1_DT}"
    
    print("\n--- Test assertions passed ---")

    # Capture and save output
    captured_out, captured_err = capsys.readouterr()
    with open(log_file_path, "a") as f:
        f.write("\n=== STDOUT CAPTURE ===\n")
        f.write(captured_out)
        if captured_err:
            f.write("\n=== STDERR CAPTURE ===\n")
            f.write(captured_err)
    
    # Also print to console if pytest is run with -s
    if captured_out:
        sys.stdout.write("\n=== CAPTURED STDOUT (test_proton_trange_updates) ===\n")
        sys.stdout.write(captured_out)
    if captured_err:
        sys.stderr.write("\n=== CAPTURED STDERR (test_proton_trange_updates) ===\n")
        sys.stderr.write(captured_err) 