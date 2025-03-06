import os
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .print_manager import print_manager
from .time_utils import daterange, get_needed_6hour_blocks
from .psp_data_types import data_types
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
    start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    print_manager.debug(f"Parsed start time: {start_time}")
    print_manager.debug(f"Parsed end time: {end_time}")
    print_manager.debug(f"Checking local files for time range: {trange} and data type: {data_type}")
    if data_type not in data_types:                                    # Validate requested data type exists
        print(f"Data type {data_type} is not recognized.")
        return False, [], []                                           # Return empty results if invalid type
        
    config = data_types[data_type]                                    # Get configuration for requested data type
    start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f')   # Convert start time string to datetime
    end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f')     # Convert end time string to datetime
    found_files = []                                                  # Initialize list to track existing files
    missing_files = []                                                # Initialize list to track missing files

    print_manager.debug(f"About to check dates between {start_time.date()} and {end_time.date()}")
    dates_to_check = list(daterange(start_time, end_time))
    print_manager.debug(f"Will check these dates: {dates_to_check}")
    

    for single_date in daterange(start_time, end_time): # Iterate through each day in range
        year = single_date.year                                       # Extract year for directory structure
        date_str = single_date.strftime('%Y%m%d')                    # Format date as YYYYMMDD string
        local_dir = os.path.join(config['local_path'].format(        # Construct path to year directory
            data_level=config['data_level']), str(year))
        print_manager.debug(f"Checking files for date: {date_str}")

        if config['file_time_format'] == '6-hour':                    # Handle 6-hour cadence data files
            blocks_to_check = get_needed_6hour_blocks(start_time, end_time)
            for single_date, block in blocks_to_check:
                hour = block * 6
                hour_str = f"{hour:02d}"                              # Format hour as 2-digit string
                date_str = single_date.strftime('%Y%m%d')             # Format date as YYYYMMDD string
                date_hour_str = f"{date_str}{hour_str}"              # Combine date and hour for filename
                file_pattern = config['file_pattern_import'].format(  # Create filename pattern for this interval
                    data_level=config['data_level'],
                    date_hour_str=date_hour_str
                )
                full_pattern = os.path.join(local_dir, file_pattern) # Complete path with filename pattern
                print_manager.debug(f"  Searching for files matching: {file_pattern}")
                matching_files = case_insensitive_file_search(       # Search for matching files
                    local_dir, full_pattern)
                if matching_files:                                    # If files found for this interval
                    print_manager.debug(f"  ✓ Found {len(matching_files)} file(s)")
                    found_files.extend(matching_files)               # Add to list of found files
                else:                                                # If no files found
                    print_manager.debug(f"  ✗ No files found for interval {hour_str}:00")
                    missing_files.append(f"{date_str}_{hour_str}")  # Record as missing

        elif config['file_time_format'] == 'daily':                  # Handle daily cadence data files
            file_pattern = config['file_pattern_import'].format(     # Create filename pattern for this day
                data_level=config['data_level'],
                date_str=date_str
            )
            full_pattern = os.path.join(local_dir, file_pattern)    # Complete path with filename pattern
            print_manager.debug(f"  Searching for daily files matching: {file_pattern}")
            
            matching_files = case_insensitive_file_search(          # Search for matching files
                local_dir, full_pattern)
            if matching_files:                                       # If files found for this day
                print_manager.debug(f"  ✓ Found {len(matching_files)} file(s)")
                found_files.extend(matching_files)                  # Add to list of found files
            else:                                                   # If no files found
                print_manager.debug(f"  ✗ No files found for date {date_str}")
                missing_files.append(date_str)                     # Record as missing

    have_all_files = len(missing_files) == 0                       # Check if we found all needed files
    print_manager.debug(f"\nSummary:")
    print_manager.debug(f"Found files: {len(found_files)}")
    print_manager.debug(f"Missing files: {len(missing_files)}")
    return have_all_files, found_files, missing_files             # Return results tuple

#====================================================================
# FUNCTION: case_insensitive_file_search, Finds files ignoring case
#====================================================================
def case_insensitive_file_search(directory, pattern):
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
        
        pattern_base = os.path.basename(pattern).lower()           # Extract and lowercase the filename pattern
        print_manager.debug(f"Searching for pattern: {pattern_base}")
        
        pattern_base = pattern_base.replace('_v*.cdf', '_v')      # Remove version wildcard for matching
        print_manager.debug(f"Modified pattern for matching: {pattern_base}")
        
        matching_files = [                                         # Create list of matching files
            os.path.join(directory, filename)                     # Include full path in results
            for filename in dir_contents                          # Check each file in directory
            if filename.lower().startswith(pattern_base)         # Compare lowercase versions
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

