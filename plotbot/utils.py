from datetime import datetime

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