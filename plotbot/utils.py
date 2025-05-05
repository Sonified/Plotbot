from datetime import datetime
import numpy as np
from plotbot.time_utils import ensure_datetime_objects

def get_encounter_number(start_date):
    """
    Get the PSP encounter number based on the date.
    
    Parameters
    ----------
    start_date : str
        Date string in format 'YYYY-MM-DD'
        
    Returns
    -------
    str
        Encounter number (e.g., 'E1', 'E2', etc.)
    """
    # Convert date string to datetime object
    date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Define encounter dates
    encounters = {
        'E1': datetime(2018, 10, 31),
        'E2': datetime(2019, 3, 30),
        'E3': datetime(2019, 8, 27),
        'E4': datetime(2020, 1, 23),
        'E5': datetime(2020, 6, 7),
        'E6': datetime(2020, 9, 27),
        'E7': datetime(2021, 1, 17),
        'E8': datetime(2021, 4, 29),
        'E9': datetime(2021, 8, 9),
        'E10': datetime(2021, 11, 21),
        'E11': datetime(2022, 2, 25),
        'E12': datetime(2022, 6, 1),
        'E13': datetime(2022, 9, 6),
        'E14': datetime(2023, 1, 1),
        'E15': datetime(2023, 4, 10),
        'E16': datetime(2023, 6, 17),
        'E17': datetime(2023, 9, 27),
        'E18': datetime(2024, 1, 4)
    }
    
    # Find the closest encounter before the given date
    closest_encounter = None
    min_diff = float('inf')
    
    for encounter, encounter_date in encounters.items():
        diff = (date - encounter_date).total_seconds()
        if 0 <= diff < min_diff:
            min_diff = diff
            closest_encounter = encounter
            
    return closest_encounter 

def print_memory_usage():
    """Prints the current memory usage of the process."""
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"Current memory usage: {mem_info.rss / (1024 * 1024):.2f} MB")

def calculate_degrees_from_perihelion(target_times, perihelion_time_str, positional_data_path):
    """Calculates Carrington longitude relative to the longitude at a specific perihelion time.

    Args:
        target_times (list or np.ndarray): Array of datetime objects for which to calculate relative longitude.
        perihelion_time_str (str): The perihelion time string (e.g., 'YYYY/MM/DD HH:MM:SS.fff').
        positional_data_path (str): Path to the .npz file containing 'times' and 'lon_carr' arrays.

    Returns:
        np.ndarray: Array of longitudes relative to the perihelion longitude, corresponding to target_times.
        Returns None if calculation fails (e.g., file not found, time not found).
    """
    try:
        data = np.load(positional_data_path)
        # Assuming times in the npz file are stored as datetime64[ns]
        # Convert them to datetime objects for easier comparison
        file_times_dt = ensure_datetime_objects(data['times'])
        file_lon_carr = data['lon_carr']
    except FileNotFoundError:
        print(f"Error: Positional data file not found at {positional_data_path}")
        return None
    except KeyError:
        print(f"Error: Required keys ('times', 'lon_carr') not found in {positional_data_path}")
        return None

    try:
        # Parse perihelion time string to datetime object
        perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
    except ValueError:
        try:
            perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            print(f"Error: Could not parse perihelion_time_str: {perihelion_time_str}. Use format 'YYYY/MM/DD HH:MM:SS.fff' or 'YYYY/MM/DD HH:MM:SS'")
            return None

    # Find the index in file_times_dt closest to perihelion_dt
    # Calculate time differences in seconds for accurate comparison
    perihelion_ts = perihelion_dt.timestamp()
    file_times_ts = np.array([t.timestamp() for t in file_times_dt])
    time_diffs_peri = np.abs(file_times_ts - perihelion_ts)
    closest_peri_idx = np.argmin(time_diffs_peri)

    # Check if the closest time is reasonably close (e.g., within a few minutes)
    # This threshold might need adjustment depending on data cadence
    if time_diffs_peri[closest_peri_idx] > 300: # 5 minutes threshold
         print(f"Warning: Closest time found ({file_times_dt[closest_peri_idx]}) is more than 5 minutes away from requested perihelion time ({perihelion_dt}).")
         # Decide if you want to proceed or return None/raise error
         # Proceeding for now...

    perihelion_lon_deg = file_lon_carr[closest_peri_idx]

    # Ensure target_times are also datetime objects
    target_times_dt = ensure_datetime_objects(target_times)
    target_times_ts = np.array([t.timestamp() for t in target_times_dt])

    # Find the indices in file_times_ts that correspond to target_times_ts
    # Use searchsorted for efficiency, assuming file_times_ts is sorted
    # Note: This finds the insertion points, which might need adjustment for exact matches
    # For simplicity, let's find the closest index for each target time
    relative_lon_deg = [] # List to store results
    output_times = [] # List to store corresponding times
    target_indices = np.searchsorted(file_times_ts, target_times_ts, side='left')

    # Ensure indices are within bounds and adjust for closest match if necessary
    for i, target_idx in enumerate(target_indices):
        best_idx = -1
        min_diff = float('inf')

        # Check index itself if within bounds
        if target_idx < len(file_times_ts):
            diff = abs(file_times_ts[target_idx] - target_times_ts[i])
            if diff < min_diff:
                min_diff = diff
                best_idx = target_idx

        # Check previous index if within bounds
        if target_idx > 0:
            diff = abs(file_times_ts[target_idx - 1] - target_times_ts[i])
            if diff < min_diff:
                min_diff = diff
                best_idx = target_idx - 1
        
        if best_idx != -1:
             # Potentially add a check here for max allowed time difference?
            lon = file_lon_carr[best_idx]
            # Simple subtraction for relative longitude
            # Handling wrap-around might be needed depending on usage
            # Example: if peri_lon=350, lon=10, result= -340. Might prefer +20.
            # For now, simple difference:
            relative_lon = lon - perihelion_lon_deg
            
            # Basic wrap-around handling (adjust to be within +/- 180)
            if relative_lon > 180:
                relative_lon -= 360
            elif relative_lon <= -180:
                relative_lon += 360
                
            relative_lon_deg.append(relative_lon)
            output_times.append(file_times_dt[best_idx]) # Store the actual time used
        else:
            # Handle cases where no suitable index was found (e.g., target time out of range)
            # Could append NaN, raise an error, or skip
            print(f"Warning: Could not find matching time for {target_times_dt[i]}")
            # Appending NaN for now, requires handling downstream
            relative_lon_deg.append(np.nan)
            output_times.append(target_times_dt[i]) # Append original target time


    # Return both the relative longitudes and the times they correspond to
    # Returning the times is important because we matched to the *closest* time in the file
    return np.array(output_times), np.array(relative_lon_deg) 