#File: data_audification.py
from .data_management import *
from .time_management import *
from .buttons import *

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
from dateutil.parser import parse as dateutil_parse

# IPython Widgets
import ipywidgets as widgets
from IPython.display import display

# Import print_manager directly
from plotbot import print_manager

# Initialize print_manager settings (optional, can be configured elsewhere)
print_manager.show_error = True

# Function to convert a date to the desired format
def convert_to_trange_format(date_str):
    """Converts a flexible date string to 'YYYY-MM-DD/HH:MM:SS.sss' format."""
    try:
        # Use dateutil.parser.parse for flexible parsing
        date_obj = dateutil_parse(date_str)
    except Exception as e:
        # If parsing fails, raise a ValueError with a more informative message
        raise ValueError(f"time data '{date_str}' does not match any expected format and could not be parsed by dateutil.parser. Error: {e}") from e
    
    # Ensure the output is always in the 'YYYY-MM-DD/HH:MM:SS.sss' format
    return date_obj.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]

def audify_high_res_mag_data_without_plot(rangeStart, rangeStop, save_dir, fsAud, sub_save_dir):
    global trange, trange_start, trange_stop

    # print('audify_high_res_mag_data_without_plot')
    # print(save_dir)
    
    # Convert dates
    trange_start = convert_to_trange_format(rangeStart)
    trange_stop = convert_to_trange_format(rangeStop)
    trange = [trange_start, trange_stop]

    print(f"Requested time range: {trange}")  # Clearly state the requested time range

    # Set up the output directory structure
    print(f"Running setup_output_directory from audify without plot")  # Debug print
    # sub_save_dir = setup_output_directory(trange, save_dir)  # Use the subdirectory for audio files

    # Find existing data files or download new data as needed
    times, br, bt, bn, bmag = download_and_prepare_high_res_mag_data(trange)

    if times is None:
        print("No magnetic field data available for the given time range.")
        return None

    # Normalize each component independently
    bmag_audio = normalize_to_int16(bmag)
    br_audio = normalize_to_int16(br)
    bt_audio = normalize_to_int16(bt)
    bn_audio = normalize_to_int16(bn)

    # Map component names to numbers
    component_mapping = {'|B|': '001', 'Br': '002', 'Bt': '003', 'Bn': '004'}

    start_datetime_str, stop_datetime_str = convert_time_range_to_str(trange[0], trange[1])

    start_date, start_time = format_time(start_datetime_str)
    stop_date, stop_time = format_time(stop_datetime_str)

    # Adjust for day-crossing in the file naming
    if start_date == stop_date:
        stop_time = f"{stop_time}"
    else:
        if start_date[:4] == stop_date[:4]:
            stop_time = f"{stop_date[5:]}_{stop_time}"
        else:
            stop_time = f"{stop_date}_{stop_time}"

    # Get the encounter number
    encounter_number = get_encounter_number(start_date)

    # Generate file names and write the audio files using the specified time range
    file_names = {
    '|B|': os.path.join(sub_save_dir, f"{encounter_number}_PSP_FIELDS_{component_mapping['|B|']}_{start_date}_{start_time}_to_{stop_time}_Bmag.wav"),
    'Br': os.path.join(sub_save_dir, f"{encounter_number}_PSP_FIELDS_{component_mapping['Br']}_{start_date}_{start_time}_to_{stop_time}_Br.wav"),
    'Bt': os.path.join(sub_save_dir, f"{encounter_number}_PSP_FIELDS_{component_mapping['Bt']}_{start_date}_{start_time}_to_{stop_time}_Bt.wav"),
    'Bn': os.path.join(sub_save_dir, f"{encounter_number}_PSP_FIELDS_{component_mapping['Bn']}_{start_date}_{start_time}_to_{stop_time}_Bn.wav")
}

    for fname, audio_data in zip(file_names.values(), [bmag_audio, br_audio, bt_audio, bn_audio]):
        write(fname, fsAud, audio_data)
        print(f"Audio file written: {fname}")

    show_directory_button(save_dir)
    show_file_buttons(file_names)  # Display buttons to open the audio files
    return file_names  # Return the file names for further use

def normalize_to_int16(data):
    data = np.array(data, dtype=np.float32)
    
    # Call the interpolation function
    data, nan_count = interpolate_and_count_nans(data)
    
    if nan_count > 0:
        print(f"NANs detected: {nan_count}. Interpolation was applied.")
    
    max_val = np.max(data)
    min_val = np.min(data)
    
    if max_val == min_val:
        return np.zeros(data.shape, dtype=np.int16)
    
    normalized_data = (2 * (data - min_val) / (max_val - min_val) - 1) * 32767
    return normalized_data.astype(np.int16)

def interpolate_and_count_nans(data):
    nan_count = np.isnan(data).sum()
    if nan_count > 0:
        mask = ~np.isnan(data)
        indices = np.arange(len(data))
        interpolated_data = np.interp(indices, indices[mask], data[mask])
    else:
        interpolated_data = data
    return interpolated_data, nan_count

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 🔊 Data Audification Initialized')