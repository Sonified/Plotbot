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
 
    for encounter, (enc_start, enc_stop) in encounters.items():
        if enc_start <= formatted_date <= enc_stop:
            return encounter
    return "Unknown_Encounter"

#Note: we're taking a liberal definition of encounter here for the sake of making
#sure that all multiplots have informative titles. It's more helpful to know we're
#approximately closer to a given encounter than it is to be told the encounter is unknwn
#in the future we can expand this such that there's a tight encounter range and then a 
#catch all list and the titles are named differently accordingly. Here's a tighter
#list that is still quite liberal in it's interpretation of encounter:

        # 'E1': ('2018-10-31', '2018-11-11'),
        # 'E2': ('2019-03-30', '2019-04-10'),
        # 'E3': ('2019-08-17', '2019-09-18'),
        # 'E4': ('2019-12-17', '2020-02-17'),
        # 'E5': ('2020-04-25', '2020-07-07'),
        # 'E6': ('2020-08-08', '2020-10-31'),
        # 'E7': ('2020-12-11', '2021-02-19'),
        # 'E8': ('2021-04-14', '2021-05-15'),
        # 'E9': ('2021-06-20', '2021-09-10'),
        # 'E10': ('2021-11-11', '2022-01-06'),
        # 'E11': ('2022-02-04', '2022-04-14'),
        # 'E12': ('2022-05-08', '2022-06-11'),
        # 'E13': ('2022-08-17', '2022-09-27'),
        # 'E14': ('2022-12-03', '2022-12-18'),
        # 'E15': ('2023-01-17', '2023-03-24'),
        # 'E16': ('2023-06-12', '2023-07-23'),
        # 'E17': ('2023-09-22', '2023-10-04'),
        # 'E18': ('2023-12-24', '2024-01-09'),
        # 'E19': ('2024-03-25', '2024-04-09'),
        # 'E20': ('2024-05-30', '2024-07-30'),
        # 'E21': ('2024-08-30', '2024-10-30'),
        # 'E22': ('2024-11-24', '2025-01-24'),
        # 'E23': ('2025-02-22', '2025-04-22'),
        # 'E24': ('2025-05-19', '2025-07-19'),
        # 'E25': ('2025-08-15', '2025-10-15'),
        # 'E26': ('2025-11-12', '2026-01-12')