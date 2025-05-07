#file: printing.py

from datetime import datetime, timedelta
import pandas as pd

# Generate the start and stop time based on left and right max indices
def print_time_range(times_clipped, left_max_value_idx, right_max_value_idx):
    """
    Generates the start and stop time range based on left and right max indices.

    Parameters:
    times_clipped (array-like): The array of clipped times.
    left_max_value_idx (int): The index of the left maximum value.
    right_max_value_idx (int): The index of the right maximum value.

    Returns:
    list: The start and stop time range in the format 'YYYY-MM-DD/HH:MM:SS.sss'.
    """
    start_time = pd.to_datetime(times_clipped[left_max_value_idx])
    end_time = pd.to_datetime(times_clipped[right_max_value_idx])
    time_range = [start_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3],  # Include milliseconds
                  end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]]
    print(f"⏱️ Hole time range based on peaks = {time_range} ")
    return time_range

# time_range = print_time_range(times_clipped, left_max_value_idx, right_max_value_idx)


current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 📃 printing manager initialized')