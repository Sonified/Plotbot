import numpy as np
from .data_management import *
from .plotting import *

def analyze_derivative_zero_crossings(
    bmag, times_clipped, left_max_value_idx, right_max_value_idx,
    derivative_window_seconds, sampling_rate, mean_threshold,
    OUTPUT_ZERO_CROSSING_PLOT
):
    # print('📈📈📈📈Now INSIDE zero crossing analysis')
    
    # Calculate the smoothed bmag and derivative for the relevant section
    smoothed_bmag_for_derivative = efficient_moving_average(
        times_clipped[left_max_value_idx:right_max_value_idx + 1], 
        bmag[left_max_value_idx:right_max_value_idx + 1], 
        derivative_window_seconds, 
        sampling_rate, 
        mean_threshold
    )

    # Calculate the first derivative
    first_derivative = np.gradient(
        smoothed_bmag_for_derivative, 
        np.arange(len(smoothed_bmag_for_derivative)) / sampling_rate
    )

    # Calculate zero crossings within the relevant section
    zero_crossings_indices = np.where(np.diff(np.sign(first_derivative)))[0] + left_max_value_idx

    # Calculate the number of zero crossings
    zero_crossings = len(zero_crossings_indices)

    if OUTPUT_ZERO_CROSSING_PLOT:
        zero_crossings, zero_crossings_indices = calculate_and_plot_derivative_zero_crossings(
            bmag, times_clipped, left_max_value_idx, right_max_value_idx, 
            derivative_window_seconds, sampling_rate, mean_threshold, smoothed_bmag_for_derivative, first_derivative, 
            zero_crossings_indices, zero_crossings
        )

    # print('📈📈📈📈Now inside zero crossing analysis return')

    return zero_crossings, zero_crossings_indices
