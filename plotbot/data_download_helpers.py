import os
import re
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from bs4 import BeautifulSoup
from .print_manager import print_manager
from .time_utils import daterange, get_needed_6hour_blocks
from .data_classes.psp_data_types import data_types
from .server_access import server_access

#====================================================================
# FUNCTION: check_local_files, Verifies data file availability locally
#====================================================================
def check_local_files(trange: tuple, data_type: str) -> tuple[bool, list, list]:
    """
    Check if files exist locally for given time range and data type.
    Returns:
        - bool: True if we have complete coverage
        - list: Found files
        - list: Missing files
    """
    print_manager.debug("Local Files Time Debug")
    print_manager.debug(f"Input trange: {trange}")
    # Validate time range and ensure UTC timezone
    try:
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        return False, [], []
    print_manager.debug(f"Parsed start time: {start_time}")
    print_manager.debug(f"Parsed end time: {end_time}")
    print_manager.debug(f"Checking local files for time range: {trange} and data type: {data_type}")
    if data_type not in data_types:                                    # Validate requested data type exists
        print(f"Data type {data_type} is not recognized.")
        return False, [], []                                           # Return empty results if invalid type
        
    config = data_types[data_type]                                    # Get configuration for requested data type
    try:
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)   # Convert start time string to datetime
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)     # Convert end time string to datetime
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        return False, [], []
    found_files = []                                                  # Initialize list to track existing files
    missing_files = []                                                # Initialize list to track missing files

    print_manager.debug(f"About to check dates between {start_time.date()} and {end_time.date()}")
    dates_to_check = list(daterange(start_time, end_time))
    print_manager.debug(f"Will check these dates: {dates_to_check}")
    
    # Check if this data type uses local CSV files
    if config.get('file_source') == 'local_csv':
        print_manager.debug(f"Data type {data_type} uses local CSV source. Searching recursively.")
        base_path = config.get('local_path')
        # Ensure file_pattern_import exists and is a list (even if single pattern)
        file_patterns = config.get('file_pattern_import')
        if isinstance(file_patterns, str):
             file_patterns = [file_patterns]

        if not base_path or not isinstance(file_patterns, list):
            print_manager.error(f"Configuration error for {data_type}: Missing 'local_path' or 'file_pattern_import' (must be a list).")
            # Return True for have_all_files but empty found/missing lists if config is bad?
            # Or mark all dates as missing?
            return False, [], list(d.strftime('%Y%m%d') for d in dates_to_check) # Mark all as missing

        # Use a temporary list to store files found via local search for this type
        local_found_files = []
        dates_missing_local_files = []

        for single_date in dates_to_check:
            date_str = single_date.strftime('%Y%m%d')
            print_manager.debug(f"Checking FITS CSVs for date: {date_str}")
            # Use the new recursive search function
            files_for_date = find_local_fits_csvs(base_path, file_patterns, date_str)
            if files_for_date:
                print_manager.debug(f"  ✓ Found {len(files_for_date)} FITS CSV file(s) for {date_str}")
                local_found_files.extend(files_for_date)
            else:
                print_manager.debug(f"  ✗ No FITS CSV files found for date {date_str}")
                dates_missing_local_files.append(date_str)

        # Determine coverage based ONLY on the local search for this type
        have_all_files_local = len(dates_missing_local_files) == 0
        print_manager.debug(f"\nSummary (local CSV {data_type}):")
        print_manager.debug(f"Found files: {len(local_found_files)}")
        print_manager.debug(f"Missing dates: {len(dates_missing_local_files)}")
        # Return the results from the local search
        return have_all_files_local, local_found_files, dates_missing_local_files

    else:
        # --- Existing logic for downloaded CDF files (UNCHANGED) ---
        print_manager.debug(f"Data type {data_type} uses downloaded CDF source.")
        for single_date in daterange(start_time, end_time): # Iterate through each day in range
            year = single_date.year                                       # Extract year for directory structure
            date_str = single_date.strftime('%Y%m%d')                    # Format date as YYYYMMDD string
            local_dir = os.path.join(config['local_path'].format(        # Construct path to year directory
                data_level=config['data_level']), str(year))
            print_manager.debug(f"Checking files for date: {date_str} in {local_dir}")

            if config['file_time_format'] == '6-hour':                    # Handle 6-hour cadence data files
                # Determine which 6-hour blocks are relevant for this specific date within the overall trange
                relevant_blocks_for_date = []
                for hour_block in range(4): # 0, 6, 12, 18 hours
                    block_start_hour = hour_block * 6
                    # Create datetime for the start of the block on single_date
                    block_start_dt = datetime.combine(single_date, datetime.min.time(), tzinfo=timezone.utc)
                    block_start_dt = block_start_dt.replace(hour=block_start_hour)
                    # Create datetime for the end of the block (exclusive)
                    block_end_dt = block_start_dt + timedelta(hours=6)

                    # Check if this block overlaps with the requested time range
                    if max(start_time, block_start_dt) < min(end_time, block_end_dt):
                        relevant_blocks_for_date.append(hour_block)

                if not relevant_blocks_for_date:
                    print_manager.debug(f"  No relevant 6-hour blocks for {date_str} within the requested time range.")
                    continue # Skip to the next date if no blocks are needed for this one

                print_manager.debug(f"  Relevant 6-hour blocks for {date_str}: {relevant_blocks_for_date}")

                for block in relevant_blocks_for_date:
                    hour = block * 6
                    hour_str = f"{hour:02d}"                              # Format hour as 2-digit string
                    date_hour_str = f"{date_str}{hour_str}"              # Combine date and hour for filename
                    # Create filename pattern for this interval - USE date_hour_str
                    file_pattern = config['file_pattern_import'].format(
                        data_level=config['data_level'],
                        date_hour_str=date_hour_str
                    )
                    # Note: full_pattern includes the year-based local_dir
                    # full_pattern = os.path.join(local_dir, file_pattern) # We pass dir and pattern separately now
                    print_manager.debug(f"  Searching for 6-hour files matching: {file_pattern} in {local_dir}")
                    matching_files = case_insensitive_file_search(       # Search for matching files
                        local_dir, file_pattern) # Pass dir and pattern separately
                    if matching_files:
                        print_manager.debug(f"  ✓ Found {len(matching_files)} file(s) for interval {hour_str}:00")
                        found_files.extend(matching_files)               # Add to list of found files
                    else:
                        print_manager.debug(f"  ✗ No files found for interval {hour_str}:00")
                        missing_files.append(f"{date_str}_{hour_str}")  # Record as missing

            elif config['file_time_format'] == 'daily':                  # Handle daily cadence data files
                file_pattern = config['file_pattern_import'].format(     # Create filename pattern for this day
                    data_level=config['data_level'],
                    date_str=date_str
                )
                # Note: full_pattern includes the year-based local_dir
                # full_pattern = os.path.join(local_dir, file_pattern) # We pass dir and pattern separately now
                print_manager.debug(f"  Searching for daily files matching: {file_pattern} in {local_dir}")

                matching_files = case_insensitive_file_search(          # Search for matching files
                    local_dir, file_pattern) # Pass dir and pattern separately
                if matching_files:
                    print_manager.debug(f"  ✓ Found {len(matching_files)} file(s) for date {date_str}")
                    found_files.extend(matching_files)                  # Add to list of found files
                else:
                    print_manager.debug(f"  ✗ No files found for date {date_str}")
                    missing_files.append(date_str)                     # Record as missing

        # --- Return logic for the CDF case ---
        have_all_files_cdf = len(missing_files) == 0                       # Check if we found all needed files
        print_manager.debug(f"\nSummary (CDF {data_type}):")
        print_manager.debug(f"Found files: {len(found_files)}")
        if found_files:
            print_manager.debug(f"First few found: {found_files[:3]}")
        print_manager.debug(f"Missing files/dates: {len(missing_files)}")
        if missing_files:
            print_manager.debug(f"First few missing: {missing_files[:3]}")
        return have_all_files_cdf, found_files, missing_files # Return results from CDF search

#====================================================================
# FUNCTION: case_insensitive_file_search, Finds files ignoring case
#====================================================================
def case_insensitive_file_search(directory, pattern_base):
    """Perform a case-insensitive file search in the given directory."""
    try:
        if not os.path.exists(directory):
            print_manager.debug(f"Directory does not exist: {directory}")
            return []
            
        print_manager.debug(f"\nSearching directory: {directory}")
        dir_contents = os.listdir(directory)                        # Get list of files in directory
        print_manager.debug(f"Found {len(dir_contents)} total files in directory")
        if len(dir_contents) > 0:
            print_manager.debug(f"First few files: {dir_contents[:3]}")
        
        print_manager.debug(f"Searching for pattern: {pattern_base}")
        
        pattern_base = pattern_base.replace('_v*.cdf', '_v')      # Remove version wildcard for matching
        print_manager.debug(f"Modified pattern for matching: {pattern_base}")
        
        matching_files = [                                         # Create list of matching files
            os.path.join(directory, filename)                     # Include full path in results
            for filename in dir_contents                          # Check each file in directory
            if filename.lower().startswith(pattern_base.lower())         # Compare lowercase versions
        ]
        
        print_manager.debug(f"Found {len(matching_files)} matching files")
        for file in matching_files:
            print_manager.debug(f"  - {os.path.basename(file)}")
            
        return matching_files                                     # Return list of matching files
    except Exception as e:                                        # Handle any filesystem errors
        print_manager.debug(f"Error listing directory {directory}: {str(e)}")
        import traceback
        print_manager.debug(f"Full error: {traceback.format_exc()}")
        return []                   
    
def authenticate_session(dir_url):
    """Handle authentication for PSP data access."""
    print_manager.debug("🔍 Starting authentication attempt")
    print_manager.debug(f"🔑 Password type: {server_access._password_type}")
    response = server_access.session.get(dir_url)
    print_manager.debug(f"📡 Initial response code: {response.status_code}")
    
    if response.status_code == 200:
        return response
        
    if response.status_code == 401:
        for attempt in range(2):
            print(f"Authentication required for {dir_url}")
            print_manager.debug(f"🔄 Attempt {attempt + 1} of 2")
            
            # Clear password before each attempt
            server_access._password = None
            
            # Debug the auth setup
            print_manager.debug("🔐 Setting up authentication...")
            username = server_access.username
            password = server_access.password  # This should trigger the password prompt
            server_access.session.auth = (username, password)
            
            response = server_access.session.get(dir_url)
            print_manager.debug(f"📡 Response code after auth attempt: {response.status_code}")
            
            if response.status_code == 200:
                return response
                
            if response.status_code == 401 and attempt < 1:
                print_manager.debug("❌ Authentication failed - please try again")

def process_file_listing(html_content, pattern_str, date_info):
    """Extract and sort filenames from directory listing.
    
    Args:
        html_content: HTML response from server
        pattern_str: Regex pattern for matching files
        date_info: Dict with keys:
            - date_str: Formatted date string
            - is_hourly: Boolean for 6-hour vs daily files
            - hour_str: Hour string (for 6-hour files)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')
    filenames = [link.get('href') for link in links if link.get('href')]
    
    pattern = re.compile(pattern_str)
    files_with_versions = [(fname, int(m.group(1)))
                          for fname in filenames
                          if (m := pattern.match(fname))]
    
    if not files_with_versions:
        if date_info['is_hourly']:
            print(f'No files found for date {date_info["date_str"]} hour {date_info["hour_str"]}')
        else:
            print(f'No files found for date {date_info["date_str"]}')
        return None
        
    return max(files_with_versions, key=lambda x: x[1])[0]

def download_file(session, file_url, local_file_path):
    """Download and save a file."""
    print_manager.status(f'Downloading {file_url}')
    file_response = session.get(file_url)
    
    if file_response.status_code == 200:
        with open(local_file_path, 'wb') as f:
            f.write(file_response.content)
        print_manager.status(f'File {local_file_path} downloaded successfully.')
        return True
    else:
        print_manager.status(f'Error downloading {file_url}, status code {file_response.status_code}')
        return False

def setup_local_path(base_local_path, year, filename):
    """Setup local directory and return full file path."""
    local_dir = os.path.join(base_local_path, str(year))
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    local_file_path = os.path.join(local_dir, filename)
    
    # Check if file already exists
    if os.path.exists(local_file_path):
        print_manager.debug(f'File {local_file_path} already exists, skipping download.')
        return None
    return local_file_path

def create_pattern_string(template, data_level, date_info):
    """Create pattern string based on file type."""
    if date_info['is_hourly']:
        date_hour_str = f"{date_info['date_str']}{date_info['hour_str']}"
        return template.format(data_level=data_level, date_hour_str=date_hour_str)
    return template.format(data_level=data_level, date_str=date_info['date_str'])
    
def process_directory(dir_url, pattern_str, date_info, base_local_path):
    """Handle the entire directory processing workflow."""
    response = authenticate_session(dir_url)  # Removed password_type parameter
    
    if response.status_code == 404:
        print(f"\nERROR: No data available at {dir_url}")
        return None
    if response.status_code != 200:
        print(f"Failed to access {dir_url} with status code {response.status_code}")
        return None
        
    latest_file = process_file_listing(response.text, pattern_str, date_info)
    if not latest_file:
        return None
        
    local_file_path = setup_local_path(base_local_path, date_info['year'], latest_file)
    if not local_file_path:  # File already exists
        return None
        
    file_url = dir_url + latest_file
    return download_file(server_access.session, file_url, local_file_path)

