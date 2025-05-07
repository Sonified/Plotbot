#file: stdev.py

from datetime import datetime, timedelta
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

#Standard Deviation Helper Functions!
def calculate_moving_stdev(data, window_seconds, sampling_rate):
    window_size = int(window_seconds * sampling_rate)  # Calculate window size in number of samples
    # print(f"Window size (in samples): {window_size} for {window_seconds}s window")
    
    # Ensure the window size is smaller than the data length
    if window_size >= len(data):
        # print(f"Window size {window_size} is larger than data length; returning NaN array.")
        return np.full(len(data), np.nan)
    
    # Use rolling with min_periods=1 to handle edge cases
    moving_stdev = pd.Series(data).rolling(window=window_size, center=True, min_periods=1).std().to_numpy()
    
    return moving_stdev

# -------- Helper Functions -------- #
def extend_time_range_stdev(trange, max_window_seconds):
    # print(f"Extending time range: {trange} by {max_window_seconds} seconds on each side")
    start_time = pd.to_datetime(trange[0]) - pd.Timedelta(seconds=max_window_seconds)
    end_time = pd.to_datetime(trange[1]) + pd.Timedelta(seconds=max_window_seconds)
    extended_trange = [start_time.strftime('%Y-%m-%d/%H:%M:%S'), end_time.strftime('%Y-%m-%d/%H:%M:%S')]
    # print(f"Extended time range: {extended_trange}")
    return extended_trange

def clip_to_original_time_range_stdev(times, data, trange):
    # print(f"Clipping data to original time range: {trange}")
    start_time = pd.to_datetime(trange[0])
    end_time = pd.to_datetime(trange[1])
    mask = (times >= start_time) & (times <= end_time)
    times_clipped = times[mask]
    data_clipped = data[mask]
    # print(f"Clipped time range has {len(times_clipped)} data points")
    return times_clipped, data_clipped

# -------- Calculate Stdev and Bounds Function -------- #
def calculate_stdev_and_bounds(bmag, smoothing_windows, sampling_rate):
    stdev_bounds_dict = {}
    
    for window_seconds in smoothing_windows:
        print(f"\nProcessing window: {window_seconds}s")
        moving_stdev = calculate_moving_stdev(bmag, window_seconds, sampling_rate)
        moving_avg = pd.Series(bmag).rolling(window=int(window_seconds * sampling_rate), center=True, min_periods=1).mean().to_numpy()

        # Calculate the upper and lower bounds
        upper_bound = moving_avg + moving_stdev
        lower_bound = moving_avg - moving_stdev
        
        stdev_bounds_dict[window_seconds] = (upper_bound, lower_bound)
    
    return stdev_bounds_dict


current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - ⧮ Stdev calculation initialized')
