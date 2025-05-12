#File: data_management.py
#Data_Downloading + Management + Audification

import os
from datetime import datetime, timedelta
from tkinter import Tk, filedialog
import pickle #for saving data locally
import pandas as pd
import numpy as np
from .time_management import *

#Import Libraries
# Scientific Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib import ticker, cm
from scipy.io import readsav, wavfile
from scipy.io.wavfile import write
from scipy import interpolate
import bisect

# PySPEDAS and PyTPlot Libraries
import pyspedas
from pyspedas import time_string, time_double, tinterpol, tdpwrspc
import pytplot
from pytplot import (
    tplot, store_data, get_data, tlimit, xlim, ylim, tplot_options, options,
    split_vec, cdf_to_tplot, divide, tplot_names, get_timespan, tplot_rename,
    time_datetime
)

# System and File Operations
import os
import sys
import contextlib
import cdflib
from datetime import datetime, timedelta
from tkinter import Tk, filedialog
import pickle #for saving data locally
import time

# IPython Widgets
import ipywidgets as widgets
from IPython.display import display

# --- Plotbot Imports ---
try:
    from plotbot import get_data as plotbot_get_data
    from plotbot.data_classes.psp_mag_classes import mag_rtn_class 
    from plotbot import print_manager as plotbot_print_manager
    from plotbot import data_cubby # Import DataCubby to grab the instance
    from plotbot import mag_rtn as global_plotbot_mag_rtn # Import the global instance directly
except ImportError:
    print("Warning: Could not import Plotbot modules. Ensure Plotbot is in PYTHONPATH or installed.")
    plotbot_get_data = None
    mag_rtn_class = None 
    plotbot_print_manager = None # Fallback will be set in the function if this is None
    data_cubby = None
    global_plotbot_mag_rtn = None
# --- End Plotbot Imports ---


# Global Variables
global save_dir
chunk_size_hours = 6  # Set the chunk size for downloading data
pickle_cache_dir = 'pickle_cache'  # Directory to store cached pickle files

#PICKLE Local Data Saving

# Ensure the pickle cache directory exists
pickle_cache_dir = 'pickle_cache'
if not os.path.exists(pickle_cache_dir):
    os.makedirs(pickle_cache_dir)

def download_and_prepare_high_res_mag_data(trange):
    pm = plotbot_print_manager if 'plotbot_print_manager' in globals() and plotbot_print_manager is not None else FallbackPrintManager()
    plotbot_trange = trange # Use the trange directly as passed

    if plotbot_get_data is None or global_plotbot_mag_rtn is None:
        pm.error("Plotbot's get_data or the global mag_rtn instance is not available.")
        return None, None, None, None, None

    pm.status(f"Fetching MAG data (standard res) for {plotbot_trange} using Plotbot and global instance.")
    
    try:
        # 1. Call plotbot.get_data, passing the ACTUAL global plotbot.mag_rtn instance.
        #    This should trigger the download and update that specific instance.
        pm.status(f"[MH_DM_DEBUG] >>> Calling plotbot_get_data with trange={plotbot_trange} and passing the global_plotbot_mag_rtn instance (id={id(global_plotbot_mag_rtn)}).")
        plotbot_get_data(plotbot_trange, global_plotbot_mag_rtn) # Pass the actual global instance
        pm.status(f"[MH_DM_DEBUG] <<< Returned from plotbot_get_data.")

        # 2. Use the imported global instance (which should now be populated)
        #    Alternatively, one could use data_cubby.grab('mag_rtn') but direct import is cleaner if available.
        mag_instance_to_use = global_plotbot_mag_rtn
        pm.status(f"[MH_DM_DEBUG] Using global_plotbot_mag_rtn instance (id={id(mag_instance_to_use)}).")

        # Debug prints for the used instance
        pm.status(f"[MH_DM_DEBUG] Instance dir(): {dir(mag_instance_to_use)[:15]}... (first 15)")
        if hasattr(mag_instance_to_use, 'datetime_array'):
            pm.status(f"[MH_DM_DEBUG] Instance.datetime_array type: {type(mag_instance_to_use.datetime_array)}")
            if mag_instance_to_use.datetime_array is not None:
                pm.status(f"[MH_DM_DEBUG] Instance.datetime_array len: {len(mag_instance_to_use.datetime_array)}")
                if len(mag_instance_to_use.datetime_array) > 0:
                    pm.status(f"[MH_DM_DEBUG] Instance.datetime_array first val: {mag_instance_to_use.datetime_array[0]}")
            else:
                pm.status(f"[MH_DM_DEBUG] Instance.datetime_array is None")
        else:
            pm.status(f"[MH_DM_DEBUG] Instance does NOT have datetime_array attribute.")

        # --- ADDED: Explicit Clipping ---
        # Ensure we are using data ONLY within the extended_trange, even if cache provided more.
        # The `trange` argument to this function IS the extended_trange.
        if hasattr(mag_instance_to_use, 'datetime_array') and mag_instance_to_use.datetime_array is not None and len(mag_instance_to_use.datetime_array) > 0:
            pm.status(f"[MH_DM_DEBUG] Clipping data from instance (ID: {id(mag_instance_to_use)}) to extended_trange: {trange}")
            
            from .time_management import clip_to_original_time_range 

            clipped_times, clipped_bmag = clip_to_original_time_range(
                mag_instance_to_use.datetime_array, 
                mag_instance_to_use.raw_data.get('bmag'), 
                trange # Use the `trange` argument passed to this function, which is the extended_trange
            )
            _, clipped_br = clip_to_original_time_range(mag_instance_to_use.datetime_array, mag_instance_to_use.raw_data.get('br'), trange)
            _, clipped_bt = clip_to_original_time_range(mag_instance_to_use.datetime_array, mag_instance_to_use.raw_data.get('bt'), trange)
            _, clipped_bn = clip_to_original_time_range(mag_instance_to_use.datetime_array, mag_instance_to_use.raw_data.get('bn'), trange)
            
            pm.status(f"[MH_DM_DEBUG] Clipping complete. Resulting points: {len(clipped_times) if clipped_times is not None else 'None'}")
            
            if clipped_times is None or clipped_bmag is None:
                pm.error(f"[MH_DM_DEBUG] Clipping resulted in None for times or bmag. Original points: {len(mag_instance_to_use.datetime_array) if mag_instance_to_use.datetime_array is not None else 'None'}. Trange: {trange}")
                return None, None, None, None, None

            pm.status(f"Successfully prepared MAG data using Plotbot for {trange}. Points: {len(clipped_times)}.")
            return clipped_times, clipped_br, clipped_bt, clipped_bn, clipped_bmag
        else:
            pm.warning("[MH_DM_DEBUG] Cannot perform clipping: Instance lacks valid datetime_array or raw_data.")
            pm.error("Failed to prepare MAG data (clipping step failed).")
            return None, None, None, None, None
        # --- END ADDED Clipping ---

    except Exception as e:
        pm.error(f"An unexpected error occurred in download_and_prepare_high_res_mag_data: {e}")
        import traceback
        pm.error(traceback.format_exc())
        return None, None, None, None, None

def download_and_process_mag_data(rangeStart, rangeStop, mag_datatype='mag_rtn_4_sa_per_cyc'):
    """
    Download and process magnetic field data for a given time range.

    Parameters:
    rangeStart (str): Start time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    rangeStop (str): Stop time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    mag_datatype (str): The datatype for magnetic field data. Default is 'mag_rtn_4_sa_per_cyc'.

    Returns:
    tuple: Start and stop time in trange format.
    """
    # Convert dates
    trange_start = convert_to_trange_format(rangeStart)
    trange_stop = convert_to_trange_format(rangeStop)
    trange = [trange_start, trange_stop]

    # Download magnetic field data
    pyspedas.psp.fields(trange=trange, datatype=mag_datatype, level='l2', time_clip=True, get_support_data=True)

    # Split magnetic field vector into 3 separate tplot variables (xyz = rtn)
    split_vec('psp_fld_l2_mag_RTN_4_Sa_per_Cyc')

    # Access data in magnetic field components
    br = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_x')
    bt = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_y')
    bn = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_z')

    # Store Br, Bt, Bn in separate panels
    store_data('Br', data={'x': br.times, 'y': br.y})
    store_data('Bt', data={'x': bt.times, 'y': bt.y})
    store_data('Bn', data={'x': bn.times, 'y': bn.y})

    # Calculate the magnitude of the magnetic field
    bmag = np.sqrt(br.y**2 + bt.y**2 + bn.y**2)
    store_data('|B|', data={'x': br.times, 'y': bmag})

    # Rename variables to apply metadata
    [tplot_rename(f'psp_fld_l2_mag_RTN_4_Sa_per_Cyc_{axis}', name) for axis, name in zip(['x', 'y', 'z'], ['Br', 'Bt', 'Bn'])]

    return trange_start, trange_stop  # Return the time range for use in the main script

def download_and_cache_data(trange):
    """Download magnetic field data and cache it using pickle."""
    filename = f"data_{trange[0].replace('/', '_').replace(':', '')}_to_{trange[1].replace('/', '_').replace(':', '')}.pkl"
    cache_path = os.path.join(pickle_cache_dir, filename)

    if os.path.exists(cache_path):
        print(f"Loading data from pickle cache: {cache_path}")
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
    else:
        print(f"Downloading data for time range: {trange}")
        start_time = time.time()
        data_quants = pyspedas.psp.fields(trange=trange, datatype='mag_rtn', level='l2', time_clip=True, get_support_data=True, notplot=True)
        download_time = time.time() - start_time
        print(f"Time to download data: {download_time} seconds")

        mag_data = data_quants['psp_fld_l2_mag_RTN']
        data = {
            'times': np.array(mag_data['x']),
            'Br': mag_data['y'][:, 0],
            'Bt': mag_data['y'][:, 1],
            'Bn': mag_data['y'][:, 2],
            'Bmag': np.sqrt(mag_data['y'][:, 0]**2 + mag_data['y'][:, 1]**2 + mag_data['y'][:, 2]**2)
        }

        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Data saved to pickle cache: {cache_path}")

    return data

def load_subregion(data, start_time, end_time):
    """Load a sub-region of the data and measure how long it takes."""
    start_loading = time.time()
    time_indices = (data['times'] >= start_time) & (data['times'] <= end_time)
    subregion = {
        'times': data['times'][time_indices],
        'Br': data['Br'][time_indices],
        'Bt': data['Bt'][time_indices],
        'Bn': data['Bn'][time_indices],
        'Bmag': data['Bmag'][time_indices]
    }
    load_time = time.time() - start_loading
    print(f"Time to load subregion: {load_time} seconds")
    return subregion


# Ensure pickle cache directory exists
if not os.path.exists(pickle_cache_dir):
    os.makedirs(pickle_cache_dir)

def generate_chunk_filename(start_time):
    """Generate a filename based on the 6-hour chunk containing the start time."""
    chunk_start_time = start_time.replace(minute=0, second=0, microsecond=0)
    hours = chunk_start_time.hour // chunk_size_hours * chunk_size_hours
    chunk_start_time = chunk_start_time.replace(hour=hours)
    chunk_end_time = chunk_start_time + timedelta(hours=chunk_size_hours)
    filename = f"data_{chunk_start_time.strftime('%Y%m%d_%H%M%S')}_to_{chunk_end_time.strftime('%Y%m%d_%H%M%S')}.pkl"
    return filename, chunk_start_time, chunk_end_time

def save_data_to_pickle(file_name, trange, times, br, bt, bn, bmag):
    """Save the magnetic field data to a pickle file."""
    file_path = os.path.join(pickle_cache_dir, file_name)
    
    # Prepare the data dictionary
    data = {
        'times': times,
        'Br': br,
        'Bt': bt,
        'Bn': bn,
        'Bmag': bmag
    }
    
    # Save to pickle file
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Data successfully saved to {file_path}")

def load_data_from_pickle(file_name):
    """Load data from a pickle file."""
    file_path = os.path.join(pickle_cache_dir, file_name)
    if os.path.exists(file_path):
        print(f"Loading data from pickle cache: {file_path}")
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
    else:
        print(f"Pickle file {file_name} does not exist.")
        return None

def find_existing_data_files(trange_start, trange_stop):
    """Find existing data files that cover the requested time range and download missing data if necessary."""
    existing_files = []
    current_time = trange_start
    expected_chunk_count = 0

    while current_time < trange_stop:
        expected_chunk_count += 1  # Count expected chunks
        filename, chunk_start_time, chunk_end_time = generate_chunk_filename(current_time)
        
        # print(f"Checking chunk: {chunk_start_time} to {chunk_end_time}")  # Print the chunk being checked
        
        file_path = os.path.join(pickle_cache_dir, filename)
        if os.path.exists(file_path):
            # print(f"Chunk data already exists: {filename}")  # Clearly state if the chunk exists
            existing_files.append(file_path)
        else:
            # print(f"Chunk data does not exist. Downloading: {filename}")  # Indicate if the chunk is being downloaded
            data = download_and_save_data(chunk_start_time, chunk_end_time)
            if data is not None:
                save_data_to_pickle(filename, trange_start, *data)
                existing_files.append(file_path)
        
        # Move to the next chunk
        current_time = chunk_end_time  # Update the loop to move to the next chunk

    # print(f"Total existing files found: {len(existing_files)}")  # Summary of found files
    
    # Show a warning only if the number of files found is less than expected and more than 1 was expected
    if expected_chunk_count > 1 and len(existing_files) < expected_chunk_count:
        print(f"Warning: Only {len(existing_files)} chunk(s) found when {expected_chunk_count} were expected.")
    
    return existing_files

def load_and_clip_data(trange_start, trange_stop):
    """Load and clip data from multiple files to fit within the requested time range, downloading missing data if necessary."""
    # print(f"Loading and clipping data for range: {trange_start} to {trange_stop}")
    file_paths = find_existing_data_files(trange_start, trange_stop)

    all_times = []
    all_data = []

    for file_path in file_paths:
        # print(f"Loading data from file: {file_path}")
        data = load_data_from_pickle(os.path.basename(file_path))
        if data is None:
            print(f"Warning: No data found in {file_path}")
            continue
        
        # Ensure that times are datetime objects
        times = pd.to_datetime(data['times'])
        
        # Now you can safely compare times with datetime objects
        time_indices = (times >= trange_start) & (times <= trange_stop)
        clipped_times = times[time_indices]
        clipped_data = data['Br'][time_indices], data['Bt'][time_indices], data['Bn'][time_indices], data['Bmag'][time_indices]

        # print(f"Adding {len(clipped_times)} data points from {file_path}")
        all_times.extend(clipped_times)
        all_data.append(clipped_data)

    # if len(all_times) > 0:
    #     # print(f"Data successfully clipped to range: {trange_start} to {trange_stop}")
    #     else:
    #         print(f"No data found for range: {trange_start} to {trange_stop}")

    all_times = np.array(all_times)
    all_data = [np.concatenate(data_component) for data_component in zip(*all_data)]

    return all_times, all_data
    
def download_and_save_data(start_time, end_time):
    """Download and save magnetic field data for a specified time range using Plotbot's infrastructure."""
    trange_plotbot_format = [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'), 
                            end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')]
    
    # Use a descriptive name for the print_manager
    pm = plotbot_print_manager if 'plotbot_print_manager' in globals() and plotbot_print_manager is not None else FallbackPrintManager() # Use fallback if main is None
    
    pm.status(f"Fetching data for chunk: {trange_plotbot_format[0]} to {trange_plotbot_format[1]} using Plotbot's get_data.")

    if plotbot_get_data is None or global_plotbot_mag_rtn is None: # Check for the global instance
        pm.error("Plotbot's get_data or the global mag_rtn instance is not available. Cannot download.")
        return None

    try:
        # 1. Call plotbot.get_data with the string name for the data type.
        #    This will trigger the download and update the global plotbot.mag_rtn instance.
        pm.status(f"[MH_DM_DEBUG] >>> Calling plotbot_get_data with trange={trange_plotbot_format} and passing the global_plotbot_mag_rtn instance (id={id(global_plotbot_mag_rtn)}).")
        plotbot_get_data(trange_plotbot_format, global_plotbot_mag_rtn) # Pass the actual global instance
        pm.status(f"[MH_DM_DEBUG] <<< Returned from plotbot_get_data.")

        # 2. Use the imported global instance (which should now be populated)
        #    Alternatively, one could use data_cubby.grab('mag_rtn') but direct import is cleaner if available.
        mag_instance_to_use = global_plotbot_mag_rtn
        pm.status(f"[MH_DM_DEBUG] Using global_plotbot_mag_rtn instance (id={id(mag_instance_to_use)}).")

        # Debug prints for the used instance
        pm.status(f"[MH_DM_DEBUG] Instance dir(): {dir(mag_instance_to_use)[:15]}... (first 15)")
        if hasattr(mag_instance_to_use, 'datetime_array'):
            pm.status(f"[MH_DM_DEBUG] Instance.datetime_array type: {type(mag_instance_to_use.datetime_array)}")
            if mag_instance_to_use.datetime_array is not None:
                pm.status(f"[MH_DM_DEBUG] Instance.datetime_array len: {len(mag_instance_to_use.datetime_array)}")
                if len(mag_instance_to_use.datetime_array) > 0:
                    pm.status(f"[MH_DM_DEBUG] Instance.datetime_array first val: {mag_instance_to_use.datetime_array[0]}")
            else:
                pm.status(f"[MH_DM_DEBUG] Instance.datetime_array is None")
        else:
            pm.status(f"[MH_DM_DEBUG] Instance does NOT have datetime_array attribute.")

        if not hasattr(mag_instance_to_use, 'datetime_array') or mag_instance_to_use.datetime_array is None or len(mag_instance_to_use.datetime_array) == 0:
            pm.warning(f"Plotbot did NOT populate the global mag_RTN instance for {trange_plotbot_format}. datetime_array is missing or empty.")
            return None

        times_to_return = mag_instance_to_use.datetime_array 
        
        br = mag_instance_to_use.br.data if hasattr(mag_instance_to_use.br, 'data') else np.array([])
        bt = mag_instance_to_use.bt.data if hasattr(mag_instance_to_use.bt, 'data') else np.array([])
        bn = mag_instance_to_use.bn.data if hasattr(mag_instance_to_use.bn, 'data') else np.array([])
        bmag_data = mag_instance_to_use.bmag.data if hasattr(mag_instance_to_use.bmag, 'data') else np.array([])
        
        if bmag_data is not None and len(bmag_data) == len(times_to_return):
            bmag = bmag_data
        elif len(br) == len(times_to_return) and len(bt) == len(times_to_return) and len(bn) == len(times_to_return) and np.all(np.isfinite(br)) and np.all(np.isfinite(bt)) and np.all(np.isfinite(bn)):
            # Only calculate if components are valid and lengths match
            bmag = np.sqrt(br**2 + bt**2 + bn**2)
        else: 
            # Fallback if component lengths don't match time, or bmag cannot be calculated, or components are not finite
            if not (len(br) == len(times_to_return) and len(bt) == len(times_to_return) and len(bn) == len(times_to_return)):
                pm.warning("Component length mismatch, returning empty Bmag.")
            elif not (np.all(np.isfinite(br)) and np.all(np.isfinite(bt)) and np.all(np.isfinite(bn))):
                 pm.warning("Non-finite values in B components, cannot calculate Bmag reliably.")
            else:
                pm.warning("Bmag unavailable or cannot be calculated, returning empty Bmag.")
            bmag = np.full(len(times_to_return), np.nan)

        pm.status(f"Data fetched successfully via Plotbot for range {trange_plotbot_format}")
        return times_to_return, br, bt, bn, bmag
    except Exception as e:
        pm.error(f"Error using Plotbot's get_data for range {trange_plotbot_format}: {str(e)}")
        import traceback
        pm.error(traceback.format_exc())
        return None    

def set_save_directory(last_dir_file=None):
    import os
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'MH_Scan_Output'))
    os.makedirs(save_dir, exist_ok=True)
    print(f"Save directory set to: {save_dir}")
    return save_dir

# Function to open a folder dialog and return the selected directory
def select_directory(start_dir=None):
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring the dialog to the front
    if start_dir and os.path.exists(start_dir):
        folder_selected = filedialog.askdirectory(initialdir=start_dir)
    else:
        folder_selected = filedialog.askdirectory()
    if not folder_selected:
        raise Exception("No directory selected. Exiting.")
    #print(f"Directory selected: {folder_selected}")
    return folder_selected

# Ensure the directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    #print(f"Ensured the directory exists: {directory}")

def open_file(file_path):
    """
    Open the specified file using the operating system's default application.
    
    Parameters:
    file_path (str): The path to the file to open.
    """
    #print(f"Attempting to open file: {file_path}")  # Debug print
    if os.name == 'nt':  # For Windows
        os.startfile(file_path)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f'open "{file_path}"')        
    
# def open_directory(directory):
#     if os.name == 'nt':  # For Windows
#         os.startfile(directory)
#     elif os.name == 'posix':  # For macOS and Linux
#         os.system(f'open "{directory}"')
#     #print(f"Directory opened: {directory}")

def get_encounter_number(start_date):
    """
    Determine the encounter number based on the provided start date.

    Parameters:
    start_date (str): Start date in the format 'YYYY-MM-DD'

    Returns:
    str: Encounter number (e.g., 'E1', 'E2')
    """
    encounters = {
        'E1': ('2018-10-31', '2018-11-11'),
        'E2': ('2019-03-30', '2019-04-10'),
        'E3': ('2019-08-17', '2019-09-18'),
        'E4': ('2019-12-17', '2020-02-17'),
        'E5': ('2020-04-25', '2020-07-07'),
        'E6': ('2020-08-08', '2020-10-31'),
        'E7': ('2020-12-11', '2021-02-19'),
        'E8': ('2021-04-14', '2021-05-15'),
        'E9': ('2021-06-20', '2021-09-10'),
        'E10': ('2021-11-11', '2022-01-06'),
        'E11': ('2022-02-04', '2022-04-14'),
        'E12': ('2022-05-08', '2022-06-11'),
        'E13': ('2022-08-17', '2022-09-27'),
        'E14': ('2022-12-03', '2022-12-18'),
        'E15': ('2023-01-17', '2023-03-24'),
        'E16': ('2023-06-12', '2023-07-23'),
        'E17': ('2023-09-22', '2023-10-04')
    }
    
    for encounter, (enc_start, enc_stop) in encounters.items():
        if enc_start <= start_date <= enc_stop:
            return encounter
    return "Unknown_Encounter"


def setup_output_directory(trange, base_save_dir):
    print(f"Entering setup_output_directory with base_save_dir: {base_save_dir}")

    # Extract start and end times from trange
    start_date_str = trange[0].split('/')[0]
    encounter_number = get_encounter_number(start_date_str)
    
    # Step 1: Construct the path for the encounter directory (e.g., E17)
    encounter_dir = os.path.join(base_save_dir, encounter_number)
    print(f"Encounter directory path: {encounter_dir}")

    # Check if we're already in an encounter directory
    if os.path.basename(base_save_dir) == encounter_number:
        print("😎😎😎Already in the correct encounter directory")
        encounter_dir = base_save_dir
    else:
        print(f"Creating encounter directory: {encounter_dir}")
        ensure_directory_exists(encounter_dir)

    # Step 2: Create the subdirectory name
    start_datetime_str, stop_datetime_str = convert_time_range_to_str(trange[0], trange[1])
    start_date, start_time = format_time(start_datetime_str)
    stop_date, stop_time = format_time(stop_datetime_str)

    if start_date == stop_date:
        stop_time_formatted = f"{stop_time}"
    else:
        if start_date[:4] == stop_date[:4]:
            stop_time_formatted = f"{stop_date[5:]}_{stop_time}"
        else:
            stop_time_formatted = f"{stop_date}_{stop_time}"

    sub_dir_name = f"{encounter_number}_PSP_FIELDS_{start_date}_{start_time}_to_{stop_time_formatted}_Bmag_Holes"
    sub_dir_path = os.path.join(encounter_dir, sub_dir_name)
    print(f"Final subdirectory path: {sub_dir_path}")
    
    ensure_directory_exists(sub_dir_path)
    
    print(f"Exiting setup_output_directory, returning: {sub_dir_path}")
    return sub_dir_path

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 📈 Data Management Initialized')