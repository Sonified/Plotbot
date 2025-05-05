import matplotlib
# matplotlib.use('Agg') # Uncomment if you want to suppress plot windows

import pytest
import os
import sys
import numpy as np
import time
from datetime import datetime
import glob
import matplotlib.pyplot as plt

# --- Path Setup --- 
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

# --- Plotbot Imports --- 
import plotbot as pb
from plotbot.plotbot_main import plotbot # Import the plotbot function
from plotbot.data_cubby import data_cubby # Import data_cubby
from plotbot import config # Import config to modify server setting
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from plotbot.data_classes.psp_proton_classes import proton, proton_hr
from plotbot.data_classes.psp_proton_fits_classes import proton_fits
from plotbot.data_classes.psp_ham_classes import ham
from plotbot.data_classes.psp_electron_classes import epad, epad_hr
# Excluded alpha_fits as requested
# from plotbot.data_classes.psp_alpha_fits_classes import alpha_fits_class 
# from plotbot.data_classes.custom_variables import CustomVariablesContainer

# Set up test log dir
os.makedirs('tests/test_logs', exist_ok=True)

trange = ['2024-09-30/11:45:00.000', '2024-09-30/12:45:00.000']

# Store (class, variable_attribute, name_str, var_name_str)
data_types_params = [
    pytest.param(mag_rtn_4sa.__class__, mag_rtn_4sa.br, 'mag_rtn_4sa', 'br', id="mag_rtn_4sa_br"),
    pytest.param(mag_rtn.__class__, mag_rtn.bt, 'mag_rtn', 'bt', id="mag_rtn_bt"),
    pytest.param(mag_sc_4sa.__class__, mag_sc_4sa.bx, 'mag_sc_4sa', 'bx', id="mag_sc_4sa_bx"),
    pytest.param(mag_sc.__class__, mag_sc.by, 'mag_sc', 'by', id="mag_sc_by"),
    pytest.param(proton.__class__, proton.density, 'proton', 'density', id="proton_density"),
    pytest.param(proton_hr.__class__, proton_hr.density, 'proton_hr', 'density', id="proton_hr_density"),
    pytest.param(proton_fits.__class__, proton_fits.qz_p, 'proton_fits', 'qz_p', id="proton_fits_qz_p"), # Uses SF00 CSV
    pytest.param(ham.__class__, ham.hamogram_30s, 'ham', 'hamogram_30s', id="ham_hamogram_30s"),         # Uses HAM CSV
    pytest.param(epad.__class__, epad.strahl, 'epad', 'strahl', id="epad_strahl"),
    pytest.param(epad_hr.__class__, epad_hr.strahl, 'epad_hr', 'strahl', id="epad_hr_strahl"),
    # Removed alpha_fits entry
]

# --- Pytest Fixtures ---

@pytest.fixture(autouse=True)
def ensure_plots_closed():
    """Ensure plots are closed before and after each test function."""
    plt.close('all')
    yield
    plt.close('all')

@pytest.fixture(autouse=True) # Apply automatically to all tests in this module
def set_berkeley_server():
    """Fixture to temporarily set the data server to Berkeley for tests."""
    original_server = config.data_server
    print(f"\n--- [Fixture] Setting config.data_server to 'berkeley' (was '{original_server}') ---")
    config.data_server = 'berkeley'
    yield # Run the test
    print(f"--- [Fixture] Restoring config.data_server to '{original_server}' ---")
    config.data_server = original_server


# --- Test Function (Parametrized) ---

@pytest.mark.parametrize("cls, var_attr, name, var_name", data_types_params)
def test_snapshot_save_load_per_type(cls, var_attr, name, var_name):
    print(f'\n=== [START] Testing Snapshot Save/Load for {name}.{var_name} ===')

    # 1. Standard Load & Plot using plotbot function
    print(f"--- [Step 1] Calling plotbot for {name}.{var_name} (Standard Load) ---")
    try:
        # Pass panel number as positional argument, remove title
        plotbot(trange, var_attr, 1)
        print(f"--- [Step 1a] plotbot call completed for {name}.{var_name}. Saving plot... ---")
        plot_path = f'tests/test_logs/{name}_{var_name}_standard_load.png'
        plt.savefig(plot_path)
        print(f'Saved standard load plot to {plot_path}')
    except Exception as e:
        pytest.fail(f"ERROR plotting standard load for {name}.{var_name}: {e}") # Fail test on error
    finally:
        plt.close() # Ensure plot is closed
        print(f"--- [Step 1b] Closed plot figure for {name}.{var_name} (Standard) ---")

    # 2. Save Snapshot (only the current class)
    snapshot_file = f'test_snapshot_{name}.pkl'
    print(f"--- [Step 2] Saving Snapshot for {name} --- ({snapshot_file})")
    try:
        pb.data_snapshot.save_data_snapshot(snapshot_file, classes=[cls])
        print(f'Saved snapshot.')
    except Exception as e:
        pytest.fail(f"ERROR saving snapshot for {name}: {e}") # Fail test on error

    # 3. Clear Data for this specific instance
    print(f"--- [Step 3] Clearing Data for {name} --- ({name})")
    instance = data_cubby.grab(name) # Get the instance associated with the name string
    if instance:
        # Directly clear raw_data if possible
        if hasattr(instance, 'raw_data') and isinstance(instance.raw_data, dict):
            for k in list(instance.raw_data.keys()): # Iterate over keys copy
                instance.raw_data[k] = None
            print(f"Cleared raw_data for {name}")
            # Removed plot_manager cache clearing
        else:
            print(f"Warning: Could not find raw_data dict to clear data for {name}")
    else:
        print(f"Warning: Could not grab instance '{name}' from data_cubby to clear.")

    # 4. Load from Snapshot
    print(f"--- [Step 4] Loading Snapshot {snapshot_file} ---")
    try:
        pb.data_snapshot.load_data_snapshot(snapshot_file)
        print("Snapshot loaded.")
    except Exception as e:
        pytest.fail(f"ERROR loading snapshot {snapshot_file}: {e}") # Fail test on error

    # 5. Snapshot Load & Plot using the same plotbot call
    print(f"--- [Step 5] Calling plotbot for {name}.{var_name} (Snapshot Load) ---")
    try:
        # Pass panel number as positional argument, remove title
        plotbot(trange, var_attr, 1)
        print(f"--- [Step 5a] plotbot call completed for {name}.{var_name} (Snapshot). Saving plot... ---")
        plot_path2 = f'tests/test_logs/{name}_{var_name}_snapshot_load.png'
        plt.savefig(plot_path2)
        print(f'Saved snapshot load plot to {plot_path2}')
    except Exception as e:
        pytest.fail(f"ERROR plotting snapshot load for {name}.{var_name}: {e}") # Fail test on error
    finally:
        plt.close()
        print(f"--- [Step 5b] Closed plot figure for {name}.{var_name} (Snapshot) ---")

    # 6. Cleanup snapshot file (optional but good practice)
    print(f"--- [Step 6] Cleaning up {snapshot_file} ---")
    try:
        if os.path.exists(snapshot_file):
            os.remove(snapshot_file)
            print(f"Cleaned up {snapshot_file}")
        else:
            print(f"Snapshot file {snapshot_file} not found for cleanup.")
    except OSError as e:
        print(f"Error removing snapshot file {snapshot_file}: {e}")
    
    print(f'=== [PASS] Testing Snapshot Save/Load for {name}.{var_name} ===')

# Keep a simple sanity test to ensure the file is runnable
def test_sanity_check():
    assert True 