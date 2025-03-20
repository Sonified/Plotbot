import os
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from .print_manager import print_manager
from .data_download_helpers import check_local_files, create_pattern_string, process_directory
from .server_access import server_access
from .time_utils import daterange, get_needed_6hour_blocks
from .psp_data_types import data_types

#====================================================================
# FUNCTION: download_new_psp_data
#====================================================================
def download_new_psp_data(trange, data_type):
    """Download new PSP data for a given data type and time range."""
    
    #====================================================================
    # VALIDATE DATA TYPE AND GET CONFIG
    #====================================================================
    print_manager.variable_testing(f"download_new_psp_data called with data_type: {data_type}")
    
    if data_type not in data_types:                      # Verify the requested data type exists in our supported types dictionary
        print(f"Data type {data_type} is not recognized.")
        print_manager.variable_testing(f"Unrecognized data_type: {data_type}, not in psp_data_types")
        return
    
    print_manager.variable_testing(f"Found {data_type} in psp_data_types, retrieving configuration")
    config = data_types[data_type]                       # Extract the specific configuration settings for this data type (URLs, paths, patterns etc.)
    print_manager.variable_testing(f"Configuration keys for {data_type}: {list(config.keys())}")
        
    #====================================================================
    # PARSE TIME RANGE
    #====================================================================
    start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)    # Convert string start time to datetime obj with UTC timezone
    end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)      # Convert string end time to datetime obj with UTC timezone
    
    # Adjust end time if midnight
    if (end_time.hour == 0 and end_time.minute == 0 and             # Check if time is exactly 00:00:00.000 - this needs special handling
        end_time.second == 0 and end_time.microsecond == 0):
        end_time = end_time - timedelta(days=1)                      # Subtract 24 hours to get previous day, as midnight belongs to next day
    
    print_manager.debug(f"Downloading data for UTC time range: {start_time} to {end_time}")
    
    #====================================================================
    # CHECK LOCAL FILES
    #====================================================================
    have_all, found_files, missing_files = check_local_files(trange, data_type)
    if have_all:
        if len(found_files) == 1:
            print_manager.status(f"📡 {data_type} - A local .cdf file already exists:")
        else:
            print_manager.status(f"📡 {data_type} - Local .cdf files already exist:")
        print_manager.status("📂 " + ", ".join(found_files))
        return

    print_manager.debug(f"\nDownloading missing files for {data_type}:")
    for file in missing_files:
        if config['file_time_format'] == '6-hour':                   # For data types that split days into 6-hour chunks (e.g., 00, 06, 12, 18)
            date_str, hour_str = file.split('_')                     # Split filename into date and hour components
            pattern_str = config['file_pattern'].format(             # Create filename pattern for 6-hour format using config template
                data_level=config['data_level'],
                date_hour_str=f"{date_str}{hour_str}"
            )
        else:  # daily files
            pattern_str = config['file_pattern'].format(             # Create filename pattern for daily format using config template
                data_level=config['data_level'],
                date_str=file
            )
        pattern_str = pattern_str.split('_v')[0] + '_v*.cdf'        # Modify pattern to match any version number (v01, v02, etc.) to get latest
        print_manager.debug(f"- {pattern_str}")
    
    #====================================================================
    # SET PASSWORD TYPE
    #====================================================================
    server_access.password_type = config['password_type']

    #====================================================================
    # PROCESS FILES (6-HOUR OR DAILY)
    #====================================================================
    if config['file_time_format'] == '6-hour':
        blocks_to_download = get_needed_6hour_blocks(start_time, end_time)
        for block_date, block in blocks_to_download:
            try:
                date_info = {
                    'date_str': block_date.strftime('%Y%m%d'),
                    'is_hourly': True,
                    'hour_str': f"{block * 6:02d}",
                    'year': block_date.year
                }
                
                dir_url = f"{config['url'].format(data_level=config['data_level'])}{block_date.year}/{block_date.month:02d}/"
                pattern_str = create_pattern_string(config['file_pattern'], config['data_level'], date_info)
                
                process_directory(
                    dir_url=dir_url,
                    pattern_str=pattern_str,
                    date_info=date_info,
                    base_local_path=config['local_path'].format(data_level=config['data_level'])
                )
            except Exception as e:
                print("🤷🏾‍♂️ The data you're looking for can't be retrieved from the server, friend!")
                print(f'An error occurred: {e}')
                continue
    
    #====================================================================
    # PROCESS DAILY FILES
    #====================================================================
    elif config['file_time_format'] == 'daily':
        for single_date in daterange(start_time.date(), end_time.date()):
            try:
                date_info = {
                    'date_str': single_date.strftime('%Y%m%d'),
                    'is_hourly': False,
                    'hour_str': None,
                    'year': single_date.year
                }
                
                dir_url = f"{config['url'].format(data_level=config['data_level'])}{single_date.year}/{single_date.month:02d}/"
                pattern_str = create_pattern_string(config['file_pattern'], config['data_level'], date_info)
                
                process_directory(
                    dir_url=dir_url,
                    pattern_str=pattern_str,
                    date_info=date_info,
                    base_local_path=config['local_path'].format(data_level=config['data_level'])
                )
            except Exception as e:
                print("🤷🏾‍♂️ The data you're looking for can't be retrieved from the server, friend!")
                print(f'An error occurred: {e}')
                continue