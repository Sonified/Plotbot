#file: multiAvg_calc.py

from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# -------- Time Parsing Helper Function -------- #
def parse_time_string(time_string):
    formats = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d/%H:%M:%S.%f', '%Y-%m-%d/%H:%M:%S']
    for fmt in formats:
        try:
            return datetime.strptime(time_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"time data '{time_string}' does not match any known formats")

#🔮 MultiAvg helper functions 🔮
# -------- Smoothing Function -------- #
def efficient_moving_average_multiAvg(times, data, window_size_seconds, sampling_rate):
    window_size_samples = int(window_size_seconds * sampling_rate)  # Calculate window size in number of samples

    # Use rolling to apply the smoothing
    smoothed_data = pd.Series(data).rolling(window=window_size_samples, center=True, min_periods=1).mean().to_numpy()
    
    return smoothed_data

# -------- Time Range Extension Function -------- #
def extend_time_range_multiAvg(trange, max_window_seconds):
    start_time = parse_time_string(trange[0]) - timedelta(seconds=max_window_seconds)
    end_time = parse_time_string(trange[1]) + timedelta(seconds=max_window_seconds)
    print(f"Extended time range: {start_time} to {end_time}")
    return [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'), end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')]

# -------- Sampling Rate Determination Function -------- #
def determine_sampling_rate_multiAvg(times, INSTRUMENT_SAMPLING_RATE, use_calculated_sampling_rate=True):
    num_samples = len(times)
    time_duration = (pd.to_datetime(times[-1]) - pd.to_datetime(times[0])).total_seconds()
    calculated_sampling_rate = num_samples / time_duration

    if use_calculated_sampling_rate:
        return calculated_sampling_rate
    else:
        return INSTRUMENT_SAMPLING_RATE

# -------- Clip Data to Original Time Range -------- #
def clip_to_original_time_range_multiAvg(times, data, trange):
    mask = (times >= pd.to_datetime(trange[0])) & (times <= pd.to_datetime(trange[1]))
    times_clipped = times[mask]
    data_clipped = data[mask]
    return times_clipped, data_clipped


current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 🔮 Multi-Average calculation initialized')
