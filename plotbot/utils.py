from datetime import datetime, timedelta
import numpy as np
from plotbot.time_utils import str_to_datetime
import pandas as pd
from plotbot.print_manager import print_manager

# Perihelion times dictionary (Encounter Number: Perihelion Time String)
# Source: Examples_Multiplot.ipynb (as of 2025-05-07 - User Provided)
# Format: YYYY/MM/DD HH:MM:SS.ffffff
PERIHELION_TIMES = {
    1: '2018/11/06 03:27:00.000', # Enc 1 
    2: '2019/04/04 22:39:00.000', # Enc 2 
    3: '2019/09/01 17:50:00.000', # Enc 3 
    4: '2020/01/29 09:37:00.000', # Enc 4 
    5: '2020/06/07 08:23:00.000', # Enc 5 
    6: '2020/09/27 09:16:00.000', # Enc 6 
    7: '2021/01/17 17:40:00.000', # Enc 7 
    8: '2021/04/29 08:48:00.000', # Enc 8 
    9: '2021/08/09 19:11:00.000', # Enc 9 
    10: '2021/11/21 08:23:00.000', # Enc 10 
    11: '2022/02/25 15:38:00.000', # Enc 11 
    12: '2022/06/01 22:51:00.000', # Enc 12 
    13: '2022/09/06 06:04:00.000', # Enc 13 
    14: '2022/12/11 13:16:00.000', # Enc 14 
    15: '2023/03/17 20:30:00.000', # Enc 15 
    16: '2023/06/22 03:46:00.000', # Enc 16 
    17: '2023/09/27 23:28:00.000', # Enc 17 
    18: '2023/12/29 00:56:00.000', # Enc 18 
    19: '2024/03/30 02:21:00.000', # Enc 19 
    20: '2024/06/30 03:47:00.000', # Enc 20 
    21: '2024/09/30 05:15:00.000', # Enc 21 
    22: '2024/12/24 11:53:00.000', # Enc 22 
    23: '2025/03/22 22:42:00.000', # Enc 23 
}

def get_encounter_number(date_str):
    """
    Determine the Parker Solar Probe (PSP) encounter number based on a given date.

    This function takes a date string, converts it to a datetime object, and then 
    compares it against predefined encounter start and end dates to identify 
    which encounter the date falls into.

    Parameters
    ----------
    date_str : str
        A date string in the format 'YYYY-MM-DD'.

    Returns
    -------
    str or None
        The encounter number (e.g., 'E1', 'E2', etc.) if the date falls within
        a defined encounter period. Returns None if the date does not fall
        within any defined encounter or if the input format is incorrect.
        
    Raises
    ------
    ValueError
        If the input date_str is not in the expected 'YYYY-MM-DD' format.
    """
    try:
        # Convert input date string to datetime object for comparison
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Please use 'YYYY-MM-DD'.")
        return None

    # Define encounter periods with start and end dates
    encounters = { #expanded encounter list
        'E1': ('2018-10-31', '2019-02-13'),
        'E2': ('2019-02-14', '2019-06-01'),
        'E3': ('2019-06-02', '2019-10-16'),
        'E4': ('2019-10-17', '2020-03-10'),
        'E5': ('2020-03-11', '2020-06-07'),
        'E6': ('2020-06-08', '2020-10-09'),
        'E7': ('2020-10-10', '2021-03-13'),
        'E8': ('2021-03-14', '2021-05-17'),
        'E9': ('2021-05-18', '2021-10-10'),
        'E10': ('2021-10-11', '2021-12-19'),
        'E11': ('2021-12-20', '2022-04-25'),
        'E12': ('2022-04-26', '2022-07-12'),
        'E13': ('2022-07-13', '2022-11-09'),
        'E14': ('2022-11-10', '2022-12-27'),
        'E15': ('2022-12-28', '2023-05-11'),
        'E16': ('2023-05-12', '2023-08-16'),
        'E17': ('2023-08-17', '2023-11-22'),
        'E18': ('2023-11-23', '2024-02-23'),
        'E19': ('2024-02-24', '2024-04-29'),
        'E20': ('2024-04-30', '2024-08-14'),
        'E21': ('2024-08-15', '2024-10-27'),
        'E22': ('2024-10-28', '2025-02-07'),
        'E23': ('2025-02-08', '2025-05-05'),
        'E24': ('2025-05-06', '2025-08-01'),
        'E25': ('2025-08-02', '2025-10-28'),
        'E26': ('2025-10-29', '2026-01-12')
    }
    
    # Iterate through encounters to find where the date falls
    for encounter, (start_str, end_str) in encounters.items():
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
        
        # Check if the target date is within the encounter period
        if start_date <= target_date <= end_date:
            return encounter # Return the encounter number (e.g., 'E1')
            
    # If no encounter matches, return None
    print(f"Date {date_str} does not fall within any defined encounter period.")
    return None

def print_memory_usage():
    """Prints the current memory usage of the process."""
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"Current memory usage: {mem_info.rss / (1024 * 1024):.2f} MB")

def get_perihelion_time(center_time):
    """Finds the perihelion time closest to the given center_time."""
    # Validate and convert input time to datetime object
    if isinstance(center_time, str):
        center_dt = str_to_datetime(center_time)
        if center_dt is None:
            print_manager.error(f"Invalid center_time format: {center_time}. Cannot determine perihelion.")
            return None
    elif isinstance(center_time, np.datetime64):
        center_dt = pd.Timestamp(center_time).to_pydatetime()
    elif isinstance(center_time, datetime):
        center_dt = center_time
    else:
        print_manager.error(f"Unsupported center_time type: {type(center_time)}.")
        return None

    # Find the closest perihelion time
    closest_peri_time_str = None
    min_time_diff = timedelta.max # Initialize with a very large difference

    for enc_num, peri_time_str in PERIHELION_TIMES.items():
        try:
            peri_dt = datetime.strptime(peri_time_str, '%Y/%m/%d %H:%M:%S.%f')
            # Calculate absolute difference
            time_diff = abs(center_dt - peri_dt)
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_peri_time_str = peri_time_str
                closest_enc_num = enc_num # Store the encounter number too
                
        except ValueError:
            print_manager.warning(f"Could not parse perihelion time for Encounter {enc_num}: {peri_time_str}")
            continue # Skip this entry if parsing fails

    if closest_peri_time_str:
        print_manager.debug(f"Closest perihelion to {center_dt} is E{closest_enc_num}: {closest_peri_time_str}")
        return closest_peri_time_str
    else:
        print_manager.warning(f"Could not find any valid perihelion time near {center_dt}.")
        return None

# Mapping of source data types to Plotbot classes
source_data_type_to_plotbot_class = {
    "mag_RTN": "mag_rtn_class",
    "mag_RTN_4sa": "mag_rtn_4sa_class",
    "mag_SC": "mag_sc_class",
    "mag_SC_4sa": "mag_sc_4sa_class",
    "spe_sf0_pad": "epad_strahl_class",
    "spe_af0_pad": "epad_strahl_high_res_class",
    "spi_sf00_l3_mom": "proton_class",
    "spi_af00_L3_mom": "proton_hr_class",
    "sf00_fits": "proton_fits_class",
    "sf01_fits": "proton_fits_class",
    "ham": "ham_class",
}

# Mapping of Plotbot classes to source data types
class_to_plotbot_data_type = {
    "mag_rtn_class": ["mag_RTN"],
    "mag_rtn_4sa_class": ["mag_RTN_4sa"],
    "mag_sc_class": ["mag_SC"],
    "mag_sc_4sa_class": ["mag_SC_4sa"],
    "epad_strahl_class": ["spe_sf0_pad"],
    "epad_strahl_high_res_class": ["spe_af0_pad"],
    "proton_class": ["spi_sf00_l3_mom"],
    "proton_hr_class": ["spi_af00_L3_mom"],
    "proton_fits_class": ["sf00_fits", "sf01_fits"],
    "ham_class": ["ham"],
}