from datetime import datetime
import numpy as np
from plotbot.time_utils import str_to_datetime
import pandas as pd
from plotbot.print_manager import print_manager

# Perihelion times dictionary (Encounter Number: Perihelion Time String)
# Source: Examples_Multiplot.ipynb (as of 2025-05-05)
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

def get_perihelion_time(center_time):
    # Validate the input center_time
    if isinstance(center_time, str):
        center_dt = str_to_datetime(center_time) # Convert string to datetime
        if center_dt is None:
            print_manager.error(f"Invalid center_time format: {center_time}. Cannot determine perihelion.")
            return None
    elif isinstance(center_time, np.datetime64):
        # Convert numpy datetime64 to Python datetime
        center_dt = pd.Timestamp(center_time).to_pydatetime()
    elif isinstance(center_time, datetime):
        center_dt = center_time # Already a datetime object
    else:
        print_manager.error(f"Unsupported center_time type: {type(center_time)}. Expected string, datetime, or numpy.datetime64.")
        return None

    # Get encounter number (adjusting logic if needed)
    # Assuming get_encounter_number works with datetime objects or can be adapted
    try:
        # Need to handle potential timezone issues if center_dt is timezone-aware
        # get_encounter_number expects YYYY-MM-DD string
        center_date_str = center_dt.strftime('%Y-%m-%d') 
        enc_num_str = get_encounter_number(center_date_str)
        if enc_num_str:
            # Extract numeric part (e.g., 'E17' -> 17)
            enc_num = int(enc_num_str[1:]) 
            peri_time = PERIHELION_TIMES.get(enc_num)
            if peri_time:
                 print_manager.debug(f"Found perihelion time {peri_time} for encounter {enc_num}")
                 return peri_time
            else:
                 print_manager.warning(f"Perihelion time not defined for encounter {enc_num}.")
                 return None
        else:
             print_manager.warning(f"Could not determine encounter number for date {center_date_str}.")
             return None
    except Exception as e:
         print_manager.error(f"Error determining encounter or looking up perihelion time: {e}")
         return None

