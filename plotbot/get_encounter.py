from dateutil.parser import parse

def get_encounter_number(start_date):
    """
    Determine the encounter number based on the provided start date.

    Parameters:
    start_date (str): Start date in any standard format

    Returns:
    str: Encounter number (e.g., 'E1', 'E2')
    """
    # Convert input date to datetime object first
    if isinstance(start_date, str):
        # Use dateutil.parser to handle a wide variety of date formats
        try:
            date_obj = parse(start_date)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse date {start_date}")
            return "Unknown_Encounter"
    else:
        date_obj = start_date
    
    # Convert to YYYY-MM-DD format for comparison
    formatted_date = date_obj.strftime('%Y-%m-%d')
    
    encounters = { #expanded encounter list
        'E1': ('2018-10-31', '2018-11-11'),
        'E2': ('2019-03-30', '2019-04-10'),
        'E3': ('2019-08-17', '2019-09-18'),
        'E4': ('2019-12-17', '2020-02-17'),
        'E5': ('2020-04-25', '2020-07-07'),
        'E6': ('2020-08-08', '2020-10-31'),
        'E7': ('2020-12-11', '2021-02-19'),
        'E8': ('2021-04-14', '2021-05-15'),
        'E9': ('2021-06-20', '2021-09-10'),
        'E10': ('2021-11-11', '2022-01-06'),
        'E11': ('2022-02-04', '2022-04-14'),
        'E12': ('2022-05-08', '2022-06-11'),
        'E13': ('2022-08-17', '2022-09-27'),
        'E14': ('2022-12-03', '2022-12-18'),
        'E15': ('2023-01-17', '2023-03-24'),
        'E16': ('2023-06-12', '2023-07-23'),
        'E17': ('2023-09-22', '2023-10-04'),
        'E18': ('2023-12-24', '2024-01-09'),
        'E19': ('2024-03-25', '2024-04-09'),
        'E20': ('2024-05-30', '2024-07-30'),
        'E21': ('2024-08-30', '2024-10-30'),
        'E22': ('2024-11-24', '2025-01-24'),
        'E23': ('2025-02-22', '2025-04-22'),
        'E24': ('2025-05-19', '2025-07-19'),
        'E25': ('2025-08-15', '2025-10-15'),
        'E26': ('2025-11-12', '2026-01-12')
    }
 
    for encounter, (enc_start, enc_stop) in encounters.items():
        if enc_start <= formatted_date <= enc_stop:
            return encounter
    return "Unknown_Encounter"