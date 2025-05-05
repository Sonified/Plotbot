import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import os
from dateutil.parser import parse as dateutil_parse

# Import everything from plotbot - adjust path if necessary
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotbot import *

def run_notebook_logic():
    """Encapsulates the logic from the notebook for easy re-execution."""
    # Reset state between runs for a cleaner test
    plt.options.reset()
    global_tracker.clear_calculation_cache() # Clear tracker state
    # Note: We are *not* clearing the data_cubby intentionally to test persistence
    
    print_manager.show_status = True
    print_manager.show_debug = False # Keep debug off for now unless needed
    print_manager.show_datacubby = True # Keep cubby prints on

    # Define encounters (using the same small subset from the log example)
    rainbow_encounters = [
        {'perihelion': '2018/11/06 03:27:00.000'}, # Enc 1
        {'perihelion': '2019/04/04 22:39:00.000'}, # Enc 2
    ]

    # Configure server (ensure it matches your notebook setting if relevant)
    # config.data_server = 'berkeley' # Or 'spdf', 'dynamic'
    # server_access.username = None # Or your username

    # Configure plot options
    plt.options.x_axis_r_sun = True
    plt.options.use_single_x_axis = True
    plt.options.use_custom_x_axis_label = False
    plt.options.custom_x_axis_label = None
    plt.options.x_axis_positional_range = None
    plt.options.constrained_layout = False
    plt.options.width = 20
    plt.options.height_per_panel = 1.3
    plt.options.hspace = .5
    plt.options.y_label_uses_encounter = True
    plt.options.y_label_includes_time = False
    plt.options.use_single_title = True
    plt.options.single_title_text = "Test Tracker State Persistence"
    plt.options.draw_vertical_line = False # Turn off plotting elements for this test
    plt.options.color_mode = 'default'
    plt.options.window = '144:00:00.000'
    plt.options.position = 'around'

    # Select variable
    plot_variable = mag_rtn_4sa.br # Using the variable from the log

    # Create plot data list
    plot_data = [(encounter['perihelion'], plot_variable) for encounter in rainbow_encounters]

    # Simulate the data loading part of multiplot
    print_manager.status(f"--- Processing {len(plot_data)} encounters --- ")
    for i, (center_time, var) in enumerate(plot_data):
        print_manager.status(f"\n--- Encounter {i+1} ({center_time}) --- ")
        # Calculate time range for this "panel"
        if plt.options.position == 'around':
            start_time = pd.Timestamp(center_time) - pd.Timedelta(plt.options.window)/2
            end_time = pd.Timestamp(center_time) + pd.Timedelta(plt.options.window)/2
        elif plt.options.position == 'before':
            start_time = pd.Timestamp(center_time) - pd.Timedelta(plt.options.window)
            end_time = pd.Timestamp(center_time)
        else: # after
            start_time = pd.Timestamp(center_time)
            end_time = pd.Timestamp(center_time) + pd.Timedelta(plt.options.window)

        trange = [
            start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'),
            end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
        ]

        # Explicitly call get_data for the variable and time range
        print_manager.status(f"Calling get_data for trange: {trange[0]} to {trange[1]}")
        get_data(trange, var)

def test_tracker_state_persistence():
    """Runs the notebook logic twice to observe tracker/cubby state evolution."""
    print("\n" + "="*20 + " FIRST RUN START " + "="*20)
    run_notebook_logic()
    print("="*20 + " FIRST RUN END " + "="*20 + "\n")

    print("\n" + "="*20 + " SECOND RUN START " + "="*20)
    run_notebook_logic()
    print("="*20 + " SECOND RUN END " + "="*20 + "\n")

    # Add assertions here later if needed, for now just observe prints
    assert True 

def test_datetime_comparison_logic():
    """Tests different methods of parsing and comparing datetime strings from logs."""
    print("\n" + "="*20 + " DATETIME COMPARISON TEST START " + "="*20)

    # Exact strings from logs
    nov_start_str = '2018-11-03T03:27:00.001528576'
    nov_end_str = '2018-11-09T03:26:59.968727424'
    apr_start_str = '2019-04-01T22:39:00.068228864'
    apr_end_str = '2019-04-07T22:38:59.947158272'

    print(f"Nov Start Str: {nov_start_str}")
    print(f"Nov End Str:   {nov_end_str}")
    print(f"Apr Start Str: {apr_start_str}")
    print(f"Apr End Str:   {apr_end_str}")

    # --- Method 1: Numpy datetime64 (Current approach) ---
    print("\n--- Testing with np.datetime64 ---")
    try:
        nov_start_np = np.datetime64(nov_start_str)
        nov_end_np = np.datetime64(nov_end_str)
        apr_start_np = np.datetime64(apr_start_str)
        apr_end_np = np.datetime64(apr_end_str)

        print(f"Parsed Nov Start (np): {nov_start_np} (type: {type(nov_start_np)}) (dtype: {nov_start_np.dtype})")
        print(f"Parsed Nov End (np):   {nov_end_np} (type: {type(nov_end_np)}) (dtype: {nov_end_np.dtype})")
        print(f"Parsed Apr Start (np): {apr_start_np} (type: {type(apr_start_np)}) (dtype: {apr_start_np.dtype})")
        print(f"Parsed Apr End (np):   {apr_end_np} (type: {type(apr_end_np)}) (dtype: {apr_end_np.dtype})")

        # Replicate merge logic comparisons
        print("Merge Logic Conditions (np.datetime64):")
        print(f"  apr_end_np < nov_start_np : {apr_end_np < nov_start_np}") # Should be False
        print(f"  apr_start_np > nov_end_np : {apr_start_np > nov_end_np}") # <<< SHOULD BE TRUE >>>
        print(f"  apr_start_np < nov_start_np : {apr_start_np < nov_start_np}") # Should be False
        print(f"  apr_end_np > nov_end_np : {apr_end_np > nov_end_np}") # Should be True

        # Assert expected outcome
        assert apr_start_np > nov_end_np, "Numpy comparison failed: Apr Start should be > Nov End"
        print("Numpy comparison assertion passed.")

    except Exception as e:
        print(f"Error during Numpy datetime64 test: {e}")

    # --- Method 2: Pandas Timestamp ---
    print("\n--- Testing with pd.Timestamp ---")
    try:
        nov_start_pd = pd.Timestamp(nov_start_str)
        nov_end_pd = pd.Timestamp(nov_end_str)
        apr_start_pd = pd.Timestamp(apr_start_str)
        apr_end_pd = pd.Timestamp(apr_end_str)

        print(f"Parsed Nov Start (pd): {nov_start_pd} (type: {type(nov_start_pd)})")
        print(f"Parsed Nov End (pd):   {nov_end_pd} (type: {type(nov_end_pd)})")
        print(f"Parsed Apr Start (pd): {apr_start_pd} (type: {type(apr_start_pd)})")
        print(f"Parsed Apr End (pd):   {apr_end_pd} (type: {type(apr_end_pd)})")

        # Replicate merge logic comparisons
        print("Merge Logic Conditions (pd.Timestamp):")
        print(f"  apr_end_pd < nov_start_pd : {apr_end_pd < nov_start_pd}") # Should be False
        print(f"  apr_start_pd > nov_end_pd : {apr_start_pd > nov_end_pd}") # <<< SHOULD BE TRUE >>>
        print(f"  apr_start_pd < nov_start_pd : {apr_start_pd < nov_start_pd}") # Should be False
        print(f"  apr_end_pd > nov_end_pd : {apr_end_pd > nov_end_pd}") # Should be True

        # Assert expected outcome
        assert apr_start_pd > nov_end_pd, "Pandas comparison failed: Apr Start should be > Nov End"
        print("Pandas comparison assertion passed.")

    except Exception as e:
        print(f"Error during Pandas Timestamp test: {e}")

    # --- Method 3: Python datetime (dateutil) ---
    print("\n--- Testing with Python datetime (dateutil) ---")
    try:
        nov_start_dt = dateutil_parse(nov_start_str)
        nov_end_dt = dateutil_parse(nov_end_str)
        apr_start_dt = dateutil_parse(apr_start_str)
        apr_end_dt = dateutil_parse(apr_end_str)

        print(f"Parsed Nov Start (dt): {nov_start_dt} (type: {type(nov_start_dt)})")
        print(f"Parsed Nov End (dt):   {nov_end_dt} (type: {type(nov_end_dt)})")
        print(f"Parsed Apr Start (dt): {apr_start_dt} (type: {type(apr_start_dt)})")
        print(f"Parsed Apr End (dt):   {apr_end_dt} (type: {type(apr_end_dt)})")

        # Replicate merge logic comparisons
        print("Merge Logic Conditions (datetime):")
        print(f"  apr_end_dt < nov_start_dt : {apr_end_dt < nov_start_dt}") # Should be False
        print(f"  apr_start_dt > nov_end_dt : {apr_start_dt > nov_end_dt}") # <<< SHOULD BE TRUE >>>
        print(f"  apr_start_dt < nov_start_dt : {apr_start_dt < nov_start_dt}") # Should be False
        print(f"  apr_end_dt > nov_end_dt : {apr_end_dt > nov_end_dt}") # Should be True

        # Assert expected outcome
        assert apr_start_dt > nov_end_dt, "Datetime comparison failed: Apr Start should be > Nov End"
        print("Datetime comparison assertion passed.")

    except Exception as e:
        print(f"Error during Python datetime test: {e}")


    print("="*20 + " DATETIME COMPARISON TEST END " + "="*20 + "\n") 