import os
import re
import glob
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from bs4 import BeautifulSoup
from .print_manager import print_manager
from .time_utils import daterange, get_needed_6hour_blocks
from .data_classes.psp_data_types import data_types
from .server_access import server_access

#====================================================================
# FUNCTION: _ensure_spdf_casing
#====================================================================
def _ensure_spdf_casing(filename, plotbot_key):
    """
    Ensures a given filename conforms to the SPDF naming convention casing.

    Looks up the plotbot_key in data_types. If an 'spdf_file_pattern' exists,
    it applies the necessary case transformations. Otherwise, returns the 
    original filename.

    Args:
        filename (str): The input filename (potentially with Berkeley casing).
        plotbot_key (str): The Plotbot data type key.

    Returns:
        str: The filename adjusted to SPDF casing, or the original filename.
    """
    config = data_types.get(plotbot_key)
    
    # Only proceed if config exists and spdf pattern is defined
    if not config or 'spdf_file_pattern' not in config:
        print_manager.debug(f"No SPDF casing specified for {plotbot_key}, returning original: {filename}")
        return filename

    spdf_filename = filename # Start with the original name

    # Apply specific transformations based on the key
    # These rules mimic the logic previously in download_spdf_data.py
    if plotbot_key == 'mag_RTN_4sa':
        spdf_filename = spdf_filename.replace('RTN', 'rtn').replace('Sa', 'sa').replace('Cyc', 'cyc')
    elif plotbot_key == 'mag_SC_4sa':
        spdf_filename = spdf_filename.replace('SC', 'sc').replace('Sa', 'sa').replace('Cyc', 'cyc')
    elif plotbot_key == 'spi_sf00_l3_mom':
        spdf_filename = spdf_filename.replace('L3', 'l3') # Case sensitive replace
    elif plotbot_key == 'spe_sf0_pad':
        spdf_filename = spdf_filename.replace('L3', 'l3') # Case sensitive replace
    # Add more rules here if other types need specific case adjustments defined by spdf_file_pattern

    if spdf_filename != filename:
        print_manager.debug(f"Adjusted filename casing for SPDF standard ({plotbot_key}): {filename} -> {spdf_filename}")
    else:
        print_manager.debug(f"Filename already matches SPDF casing for {plotbot_key}: {filename}")
        
    return spdf_filename

#====================================================================
# FUNCTION: check_local_files, Verifies data file availability locally
#====================================================================
def check_local_files(trange: tuple, data_type: str) -> tuple[bool, list, list]:
    """
    Check if required data files for a specific data type exist locally 
    within the expected directory structure for a given time range.

    Determines file coverage based on the data type's time granularity 
    (daily or 6-hour).

    Args:
        trange: A tuple containing two strings representing the start and end 
                of the time range (e.g., ('YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS')).
        data_type: The key corresponding to the data type in the 
                   `plotbot.data_classes.psp_data_types.data_types` dictionary.

    Returns:
        A tuple containing:
        - bool: True if all expected files for the `trange` are found locally, 
                False otherwise.
        - list: A list of strings containing the full paths to the local files 
                that were found.
        - list: A list of strings representing the expected base filenames 
                (without version or extension) that were *not* found locally.
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
    
#====================================================================
# FUNCTION: process_directory, Orchestrates Downloading of latest file version from a directory
#====================================================================
def process_directory(dir_url, pattern_str, date_info, base_local_path, plotbot_key):
    """
    Orchestrate the process of accessing a remote directory and downloading the 
    latest version of a needed file, ensuring SPDF filename casing.

    Handles authentication, file listing, version comparison, local path setup, 
    and initiates the download. Saves the file using SPDF standard casing.

    Args:
        dir_url: The URL of the remote directory containing the data file.
        pattern_str: The regex pattern for matching the desired file and 
                     extracting its version number (Berkeley pattern).
        date_info: A dictionary containing date details used for logging and 
                   path construction: {'year': YYYY, ...}.
        base_local_path: The base local directory path template for saving the file.
        plotbot_key (str): The Plotbot data type key (used for casing).

    Returns:
        tuple[bool, str | None]: A tuple containing:
            - bool: True if the file was successfully downloaded, False otherwise.
            - str | None: The SPDF-cased filename if successful, None otherwise.
    """
    response = authenticate_session(dir_url)  # Attempt to access the directory, handling login if needed.
    
    if response.status_code == 404: # Check if the directory itself wasn't found.
        print(f"\nERROR: No data available at {dir_url}") # Indicate directory not found.
        return (False, None) # Step out of function.
    
    if response.status_code != 200: # Check for other access errors (like permission denied after auth).
        print(f"Failed to access {dir_url} with status code {response.status_code}") # Indicate generic access failure.
        return (False, None) # Step out of function.
        
    # If directory accessed successfully, parse the HTML listing.
    # Find the filename with the highest version number (might have Berkeley casing)
    latest_file_berkeley_case = process_file_listing(response.text, pattern_str, date_info) 
    
    if not latest_file_berkeley_case: # Check if any matching file was found in the listing.
        return (False, None) # Step out of function.
        
    # Ensure the filename uses SPDF standard casing BEFORE checking local existence or downloading
    latest_file_spdf_case = _ensure_spdf_casing(latest_file_berkeley_case, plotbot_key)

    # Prepare the local save location USING THE SPDF-CASED FILENAME.
    # This checks if a file with the SPDF name already exists.
    local_file_path = setup_local_path(base_local_path, date_info['year'], latest_file_spdf_case) 
    
    if not local_file_path:  # Check if setup_local_path returned None (meaning file already exists).
        print_manager.debug(f"File {latest_file_spdf_case} already exists locally (SPDF case check).")
        return (False, None) # Indicate file exists, return None for filename
        
    # Construct the full URL for the specific file to download (using the original Berkeley-cased name)
    file_url = dir_url + latest_file_berkeley_case # Download URL must match server's filename
    
    # Initiate the actual download process, saving to the SPDF-cased local path.
    download_success = download_file(server_access.session, file_url, local_file_path) 
    
    if download_success:
        return (True, latest_file_spdf_case) # Return True and the SPDF-cased filename
    else:
        return (False, None) # Return False and None for filename

#====================================================================
# FUNCTION: download_file, ✨ Downloads a single file and saves it locally ✨
#====================================================================
def download_file(session, file_url, local_file_path):
    """
    Download a single file from a URL and save it locally.

    Uses the provided requests session to perform the download.

    Args:
        session: The `requests.Session` object to use for the download 
                 (should be authenticated if necessary).
        file_url: The full URL of the file to download.
        local_file_path: The full local path where the file should be saved.

    Returns:
        True if the download and saving were successful (HTTP status 200), 
        False otherwise.
    """
    print_manager.status(f'Downloading {file_url}')
    # Send the HTTP GET request to download the file content:
    file_response = session.get(file_url) #<--- ✨This is where the download happens ✨
    
    if file_response.status_code == 200:
        with open(local_file_path, 'wb') as f:
            f.write(file_response.content)
        print_manager.status(f'File {local_file_path} downloaded successfully.')
        return True
    else:
        print_manager.status(f'Error downloading {file_url}, status code {file_response.status_code}')
        return False

#====================================================================
# FUNCTION: authenticate_session, Handles authentication for accessing URLs
#====================================================================
def authenticate_session(dir_url):
    """
    Attempt to access a directory URL, handling authentication if required.

    Uses the global `server_access` object to manage credentials and the 
    requests session. Prompts for username/password via `getpass` if the 
    server returns a 401 Unauthorized status.

    Args:
        dir_url: The URL of the remote directory to access.

    Returns:
        The `requests.Response` object from the successful GET request, or 
        the response object from the final failed attempt (e.g., 401, 404).
    """
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

    return response # Return the final response, successful or not

#====================================================================
# FUNCTION: process_file_listing, Finds latest file version from HTML listing
#====================================================================
def process_file_listing(html_content, pattern_str, date_info):
    """
    Extract filenames from an HTML directory listing and find the latest version.

    Parses the HTML, finds links matching the provided regex pattern, 
    extracts version numbers, and returns the filename with the highest version.

    Args:
        html_content: A string containing the HTML source of the directory listing page.
        pattern_str: The regex pattern string (created by `create_pattern_string`) 
                     to match filenames and capture the version number.
        date_info: A dictionary containing date details for logging purposes:
                   {'date_str': 'YYYYMMDD', 'is_hourly': bool, 'hour_str': 'HH' or None}.

    Returns:
        A string containing the filename of the latest version found, or None if 
        no matching files are found.
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


#====================================================================
# FUNCTION: setup_local_path, Constructs local path and checks existence
#====================================================================
def setup_local_path(base_local_path, year, filename):
    """
    Construct the full local path for a file and check if it exists.

    Ensures the target directory exists before checking for the file. 
    Uses case-insensitive check for existing files.

    Args:
        base_local_path: The base directory path template from the 
                         `psp_data_types` configuration (e.g., 
                         `"psp_data/fields/l2/{data_level}/"`).
        year: The year (integer or string) corresponding to the file's date.
        filename: The name of the file (e.g., 
                  `"psp_fld_l2_mag_rtn_4sa_per_cyc_20230101_v02.cdf"`). Should be SPDF-cased.

    Returns:
        The full local path string if the file does *not* already exist (case-insensitive), 
        otherwise returns None.
    """
    local_dir = os.path.join(base_local_path, str(year))
    if not os.path.exists(local_dir):
        try:
            os.makedirs(local_dir)
            print_manager.debug(f"Created directory: {local_dir}")
        except OSError as e:
            print_manager.error(f"Failed to create directory {local_dir}: {e}")
            return None # Cannot proceed if directory creation fails

    local_file_path = os.path.join(local_dir, filename) # Full target path with SPDF case
    
    # Perform a case-insensitive check for file existence
    target_filename_lower = filename.lower()
    exists_case_insensitive = False
    try:
        if os.path.exists(local_dir): # Check again in case of race condition
             dir_contents = os.listdir(local_dir)
             for item in dir_contents:
                 if item.lower() == target_filename_lower:
                     exists_case_insensitive = True
                     existing_file_path = os.path.join(local_dir, item) # Get path of actual existing file
                     print_manager.debug(f"File already exists (case-insensitive check): {existing_file_path}. Target: {local_file_path}")
                     break
    except Exception as e:
        print_manager.warning(f"Error checking directory {local_dir} for case-insensitive existence: {e}")
        # Fallback to simple existence check if listing fails
        if os.path.exists(local_file_path):
             exists_case_insensitive = True
             print_manager.debug(f"File already exists (fallback check): {local_file_path}")

    if exists_case_insensitive:
        return None # File exists (case-insensitively), skipping download/overwrite.
        
    # If we reach here, the file does not exist case-insensitively
    return local_file_path # Return the target SPDF-cased path

#====================================================================
# FUNCTION: create_pattern_string, Creates regex pattern for matching data files
#====================================================================
def create_pattern_string(pattern_template, data_level, date_info):
    """
    Create a regex pattern string for matching specific data files.

    Constructs the pattern based on whether the data type uses daily or 
    6-hour file granularity.

    Args:
        pattern_template: The filename pattern string template from the 
                          `psp_data_types` configuration (e.g., 
                          `"psp_fld_l2_{data_level}_{date_str}_v*.cdf"`).
        data_level: The data level string (e.g., 'mag_rtn_4sa') from the config.
        date_info: A dictionary containing date details:
                   {'date_str': 'YYYYMMDD', 'is_hourly': bool, 'hour_str': 'HH' or None}.

    Returns:
        A string containing the compiled regex pattern ready for matching.
        Example: 'psp_fld_l2_mag_rtn_4sa_20230101_v(\d+).cdf'
    """
    if date_info['is_hourly']:
        date_hour_str = f"{date_info['date_str']}{date_info['hour_str']}"
        return pattern_template.format(data_level=data_level, date_hour_str=date_hour_str)
    return pattern_template.format(data_level=data_level, date_str=date_info['date_str'])
    
