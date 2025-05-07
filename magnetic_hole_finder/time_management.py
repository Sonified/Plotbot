#file: time_management.py
import pandas as pd
from datetime import datetime, timedelta
import sys
import math
from dateutil.parser import parse as dateutil_parse # Import dateutil parser
import numpy as np


def time_check(trange):
    """
    Checks if the end time in the trange is after the start time.
    
    Parameters:
    trange (list): A list containing two time strings in the format 'YYYY-MM-DD/HH:MM:SS.sss'.
    
    Raises:
    ValueError: If the end time is before or equal to the start time.
    """
    try:
        start_time = dateutil_parse(trange[0])
        end_time = dateutil_parse(trange[1])
    except Exception as e:
        print(f"⛔️ Error parsing time range in time_check: {trange}. Error: {e}")
        sys.exit(f"Invalid time range format for time_check: {trange}")
        raise ValueError(f"Invalid time range format for time_check: {trange}") from e

    if end_time <= start_time:
        print("⛔️ Check your time range: the end time must be after the start time.")
        sys.exit("Invalid time range: end time is before or equal to start time.")
        # raise ValueError("Invalid time range: end time is before or equal to start time.") # sys.exit is enough

# Function to convert a date to the desired format, now including milliseconds
def convert_to_trange_format(date_str):
    """Converts a flexible date string to 'YYYY-MM-DD/HH:MM:SS.sss' format for Plotbot/Pyspedas."""
    try:
        date_obj = dateutil_parse(date_str)
    except Exception as e:
        print(f"⛔️ Error parsing date string in convert_to_trange_format: {date_str}. Error: {e}")
        raise ValueError(f"Invalid date string format: {date_str}") from e
    # Outputting in the slash format as Pyspedas/Plotbot might expect this for some operations
    return date_obj.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]

def _parse_trange_string(time_str):
    """Helper to parse time strings that may or may not have microseconds."""
    try:
        return datetime.strptime(time_str, '%Y-%m-%d/%H:%M:%S.%f')
    except ValueError:
        return datetime.strptime(time_str, '%Y-%m-%d/%H:%M:%S')

def convert_time_range_to_str(trange_start, trange_stop):
    """
    Convert the time range to formatted strings, including milliseconds if present.

    Args:
        trange_start (str): Start time string, e.g., 'YYYY-MM-DD/HH:MM:SS' or 'YYYY-MM-DD/HH:MM:SS.ffffff'.
        trange_stop (str): Stop time string, similar format to trange_start.

    Returns:
        tuple: Formatted start and stop times as strings (e.g., 'YYYY_MM_DD_HHh_MMm_SSs_fffms' or 'YYYY_MM_DD_HHh_MMm_SSs').
    """
    try:
        start_datetime = dateutil_parse(trange_start)
        stop_datetime = dateutil_parse(trange_stop)
    except Exception as e:
        print(f"⛔️ Error parsing time range in convert_time_range_to_str: [{trange_start}, {trange_stop}]. Error: {e}")
        # Decide on error handling: re-raise, return None, or default strings
        raise ValueError(f"Invalid time strings for convert_time_range_to_str: {e}") from e

    # Format start time string
    if start_datetime.microsecond > 0:
        start_datetime_str = start_datetime.strftime('%Y_%m_%d_%Hh_%Mm_%Ss_%f')[:-3] + 'ms'
    else:
        start_datetime_str = start_datetime.strftime('%Y_%m_%d_%Hh_%Mm_%Ss') + 's'

    # Format stop time string
    if stop_datetime.microsecond > 0:
        stop_datetime_str = stop_datetime.strftime('%Y_%m_%d_%Hh_%Mm_%Ss_%f')[:-3] + 'ms'
    else:
        stop_datetime_str = stop_datetime.strftime('%Y_%m_%d_%Hh_%Mm_%Ss') + 's'
        
    return start_datetime_str, stop_datetime_str

# # Format start and stop strings correctly
# def format_time(time_str):
#     date_str, time_str = time_str.split('_')[0:3], time_str.split('_')[3:6]
#     formatted_time = f"{time_str[0].replace('h', '').zfill(2)}{time_str[1].replace('m', '').zfill(2)}"
#     if len(time_str) == 3 and int(time_str[2].replace('s', '')) > 0:
#         formatted_time += f"-{time_str[2].replace('s', '').zfill(2)}"
#     return '-'.join(date_str), formatted_time

# Format start and stop strings correctly
def format_time(time_str):
    date_str, time_str = time_str.split('_')[0:3], time_str.split('_')[3:6]
    formatted_time = f"{time_str[0].replace('h', '').zfill(2)}{time_str[1].replace('m', '').zfill(2)}"
    if len(time_str) == 3:
        seconds = time_str[2].replace('s', '').zfill(2)
        formatted_time += f"{seconds}"
    return '-'.join(date_str), formatted_time

# Helper function to format the datetime strings (Used in a button)
def format_datetime(datetime_str):
    date_part, time_part = datetime_str.split('_')[0:3], datetime_str.split('_')[3:]
    date_part = '-'.join(date_part)
    time_part = time_part[0].zfill(2) + time_part[1].zfill(2)
    if len(time_part) > 2:
        time_part += f"-{time_part[2].zfill(2)}"
    return date_part, time_part

# -------- Helper Functions -------- #
def extend_time_range(trange, max_window_seconds):
    try:
        # Use dateutil.parser.parse for flexibility
        start_time = dateutil_parse(trange[0])
        end_time = dateutil_parse(trange[1])
    except Exception as e:
        print(f"⛔️ Error parsing time range in extend_time_range: {trange}. Error: {e}")
        # Handle error appropriately, e.g., re-raise or return original trange
        raise ValueError(f"Invalid time range format for extend_time_range: {trange}") from e

    start_time_extended = start_time - timedelta(seconds=max_window_seconds)
    end_time_extended = end_time + timedelta(seconds=max_window_seconds)
    
    print(f"Extended time range: {start_time_extended.strftime('%Y-%m-%d %H:%M:%S.%f')} to {end_time_extended.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    # Output in the original flexible format (space separated, with ms if present)
    # or convert to the YYYY-MM-DD/HH:MM:SS.ffffff format if downstream Plotbot functions strictly need it.
    # For now, assume downstream can handle the flexible format that dateutil_parse itself outputs by default with str()
    # Let's standardize to the YYYY-MM-DD/HH:MM:SS.ffffff format for Plotbot consistency for now.
    return [start_time_extended.strftime('%Y-%m-%d/%H:%M:%S.%f'), 
            end_time_extended.strftime('%Y-%m-%d/%H:%M:%S.%f')]

def clip_to_original_time_range(times, data, trange):
    try:
        # Use dateutil.parser.parse for flexibility and convert to pandas Timestamp for comparison
        trange_start_dt = pd.Timestamp(dateutil_parse(trange[0]))
        trange_end_dt = pd.Timestamp(dateutil_parse(trange[1]))
    except Exception as e:
        print(f"⛔️ Error parsing time range in clip_to_original_time_range: {trange}. Error: {e}")
        raise ValueError(f"Invalid time range format for clip_to_original_time_range: {trange}") from e

    # Assuming 'times' is already a pandas Series of Timestamps or numpy array of datetime64
    # If 'times' is not already datetime-like, it needs conversion: times_dt = pd.to_datetime(times)
    mask = (times >= trange_start_dt) & (times <= trange_end_dt)
    times_clipped = times[mask]
    data_clipped = data[mask]
    return times_clipped, data_clipped


def determine_sampling_rate(times, INSTRUMENT_SAMPLING_RATE, use_calculated_sampling_rate=True):
    # Print the number of data samples
    num_samples = len(times)
    # print(f"Number of data samples: {num_samples}")

    # Calculate the sampling rate in samples per second
    time_duration = (pd.to_datetime(times[-1]) - pd.to_datetime(times[0])).total_seconds()
    calculated_sampling_rate = num_samples / time_duration
    # print(f"Calculated sampling rate: {calculated_sampling_rate} samples/second")

    # Use the calculated sampling rate if the flag is set
    if use_calculated_sampling_rate:
        return calculated_sampling_rate
    else:
        return INSTRUMENT_SAMPLING_RATE

# 😎 -------- Smoothing Function -------- 😎 #
def efficient_moving_average(times, data, window_size_seconds, sampling_rate, mean_threshold):
    # Ensure sampling_rate is valid
    if sampling_rate <= 0 or not np.isfinite(sampling_rate):
        print_manager.error(f"Invalid sampling_rate ({sampling_rate}) in efficient_moving_average. Cannot proceed.")
        return data # Or raise error, or return None, or np.full_like(data, np.nan)

    # Calculate window size in number of samples
    # Ensure that window_size_samples is at least 1 for pd.rolling if min_periods is 1
    calculated_raw_samples = window_size_seconds * sampling_rate
    window_size_samples_for_rolling = max(1, int(round(calculated_raw_samples))) # Round before int, ensure at least 1

    print(f"EFFICIENT_MOVING_AVG_DEBUG: window_sec={window_size_seconds}, sr={sampling_rate:.2f}, raw_samples_calc={calculated_raw_samples:.2f}, rolling_window_arg={window_size_samples_for_rolling}")

    if len(data) < window_size_samples_for_rolling:
        print_manager.warning(f"Data length ({len(data)}) is less than rolling window size ({window_size_samples_for_rolling}). Result may be all NaNs or affect edge cases.")
        # Pandas rolling with min_periods=1 will handle this by producing what it can.

    # Use rolling to apply the smoothing
    try:
        smoothed_data = pd.Series(data).rolling(window=window_size_samples_for_rolling, center=True, min_periods=1).mean().to_numpy()
    except ValueError as ve:
        print_manager.error(f"ValueError in pd.Series.rolling: {ve}")
        print_manager.error(f"  Inputs were: data len={len(data)}, window={window_size_samples_for_rolling}, center=True, min_periods=1")
        # Depending on desired behavior, could return original data or NaNs
        return np.full_like(data, np.nan, dtype=np.float64) # Return NaNs on error

    # Apply the mean threshold multiplier
    smoothed_data = smoothed_data * mean_threshold
    
    # The loop for printing individual smoothed values was mostly for deep debug and can be removed for now
    # print(f"Computed moving average with {window_size_seconds}-second window:")
    
    return smoothed_data

def efficient_moving_average_for_heatmap(times, data, window_size_seconds, sampling_rate):
    # Ensure that window_size_samples is at least 1 sample
    window_size_samples = max(1, math.ceil(window_size_seconds * sampling_rate))  # Use math.ceil to avoid window size 0

    # Debugging print to verify window size
    print(f"Window size (seconds): {window_size_seconds}, Window size (samples): {window_size_samples}")

    # Use rolling to apply the smoothing
    smoothed_data = pd.Series(data).rolling(window=window_size_samples, center=True, min_periods=1).mean().to_numpy()

    return smoothed_data




current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f'{current_time} - ⏱️ time management initialized')
