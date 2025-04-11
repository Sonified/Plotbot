import cdflib
import numpy as np
import os
import re
import pandas as pd # Added for CSV reading
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from fnmatch import fnmatch # Import for wildcard matching
from .print_manager import print_manager
from .time_utils import daterange
from .data_tracker import global_tracker
from .data_classes.psp_data_types import data_types as psp_data_types # UPDATED PATH
from .data_cubby import data_cubby
# from .plotbot_helpers import find_local_fits_csvs # This function is defined locally below

# Import the NEW calculation function
from .calculations.calculate_proton_fits import calculate_proton_fits_vars

# Attempt to import Jaye's original calculation function (legacy/backup)
# try:
#     from Jaye_fits_integration.calculations.calculate_fits_derived import calculate_sf00_fits_vars, calculate_sf01_fits_vars
# except ImportError as e:
#     print_manager.error(f"Could not import FITS calculation functions from Jaye_fits_integration: {e}")
#     # Define dummy functions if import fails, to prevent crashes
#     def calculate_sf00_fits_vars(*args, **kwargs):
#         print_manager.error("Using dummy calculate_sf00_fits_vars due to import error.")
#         return pd.DataFrame(), {}
#     def calculate_sf01_fits_vars(*args, **kwargs):
#         print_manager.error("Using dummy calculate_sf01_fits_vars due to import error.")
#         return pd.DataFrame(), {}

# Global flag for test-only mode
TEST_ONLY_MODE = False

# Function to recursively find local FITS CSV files matching patterns and date
def find_local_csvs(base_path, file_patterns, date_str):
    """Recursively search for files matching patterns and containing date_str.

    Args:
        base_path (str): The root directory to start the search.
        file_patterns (list): A list of filename patterns (e.g., ['*_sf00_*.csv']).
        date_str (str): The date string to find (e.g., '20230115' or '2023-01-15').

    Returns:
        list: A list of full paths to matching files.
    """
    found_files = []
    # Normalize date_str format (ensure YYYY-MM-DD format is checked if present)
    date_formats_to_check = [date_str] # Start with the original format
    try:
        dt_obj = datetime.strptime(date_str, '%Y%m%d')
        alt_date_str = dt_obj.strftime('%Y-%m-%d')
        if alt_date_str != date_str:
             date_formats_to_check.append(alt_date_str)
    except ValueError:
        try:
             dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
             alt_date_str = dt_obj.strftime('%Y%m%d')
             if alt_date_str != date_str:
                  date_formats_to_check.append(alt_date_str)
        except ValueError:
             pass # If neither format works, just use the original

    print_manager.debug(f"Searching for CSVs in '{base_path}' for patterns {file_patterns} and dates {date_formats_to_check}")

    if not os.path.isdir(base_path):
        print_manager.warning(f"Base path '{base_path}' does not exist or is not a directory.")
        return []

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            # Check if filename matches any of the patterns
            matches_pattern = any(fnmatch(filename, pattern) for pattern in file_patterns)
            if matches_pattern:
                # Check if any of the required date formats are in the filename or path
                full_path = os.path.join(root, filename)
                in_filename = any(d in filename for d in date_formats_to_check)
                in_path = any(d in full_path for d in date_formats_to_check)
                if in_filename or in_path:
                    found_files.append(full_path)
                    print_manager.debug(f"  Found matching file: {full_path}")

    if not found_files:
        print_manager.debug(f"  No files found matching criteria in {base_path}")

    return found_files

DataObject = namedtuple('DataObject', ['times', 'data'])  # Define DataObject structure earlier

def import_data_function(trange, data_type):
    """Import data function that reads CDF or calculates FITS CSV data within the specified time range."""
    
    print_manager.debug('Import data function called')
    print_manager.debug(f"Input trange: {trange}")
    print_manager.variable_testing(f"import_data_function called for data_type: {data_type}")
    
    # Add time tracking for function entry
    print_manager.time_input("import_data_function", trange)
    
    # Determine if this is a request for calculated FITS data
    # We'll use a placeholder data_type like 'fits_calculated' for now
    # OR check if requested data_type requires sf00/sf01 calculation
    # For simplicity, let's assume a specific trigger type for now.
    # We need a clear way to know when to perform the FITS calculation.
    # Maybe check if data_type is NOT in data_types but is a known calculated product?
    # Let's refine this trigger logic. How should plotbot request this calculation?
    #
    # --> TEMPORARY APPROACH: Define a specific data_type trigger
    FITS_CALCULATED_TRIGGER = 'fits_calculated' # Define a trigger name

    is_fits_calculation = (data_type == FITS_CALCULATED_TRIGGER)

    if not is_fits_calculation and data_type not in psp_data_types:
        print_manager.variable_testing(f"Error: {data_type} not found in psp_data_types and is not the FITS calculation trigger.")
        print_manager.time_output("import_data_function", "error: invalid data_type")
        return None
    
    # Get config - if it's a standard type, get its config.
    # If it's the FITS calculation, we'll fetch sf00/sf01 configs later.
    if not is_fits_calculation:
        print_manager.variable_testing(f"Getting configuration for standard data type: {data_type}")
        config = psp_data_types[data_type]
    else:
        # config = None # Explicitly set config to None or handle later
        print_manager.variable_testing(f"Recognized request for calculated FITS data.")
    
    # Parse times using flexible parser and ensure UTC timezone
    try:
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc) # Ensure UTC
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)   # Ensure UTC
        print_manager.time_tracking(f"Parsed time range: {start_time} to {end_time}")
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        print_manager.time_output("import_data_function", "error: time parsing failed")
        return None
    
    print_manager.debug(f"\nImporting data for UTC time range: {trange}")

    #====================================================================
    # CHECK DATA SOURCE TYPE (FITS Calculation vs CDF vs Other Local CSV)
    #====================================================================

    if is_fits_calculation:
        # --- FITS Data Loading Logic (Modified) ---
        print_manager.debug(f"\n=== Starting FITS Raw Data Import for {trange} ===")

        # Get config for the required input type (sf00 only needed now)
        try:
            sf00_config = psp_data_types['sf00_fits']
        except KeyError as e:
            print_manager.error(f"Configuration error: Missing 'sf00_fits' data type definition in psp_data_types.py")
            print_manager.time_output("import_data_function", "error: config error")
            return None

        if not sf00_config:
            print_manager.error(f"Configuration error: Could not load config for sf00_fits.")
            print_manager.time_output("import_data_function", "error: config error")
            return None

        sf00_base_path = sf00_config.get('local_path')
        sf00_patterns = sf00_config.get('file_pattern_import')

        if not sf00_base_path or not sf00_patterns:
            print_manager.error(f"Configuration error: Missing 'local_path' or 'file_pattern_import' for sf00.")
            print_manager.time_output("import_data_function", "error: config error")
            return None

        # Define the raw columns needed by proton_fits_class internal calculation
        raw_cols_needed = [
            'time', 'np1', 'np2', 'Tperp1', 'Tperp2', 'Trat1', 'Trat2',
            'vdrift', 'B_inst_x', 'B_inst_y', 'B_inst_z', 'vp1_x', 'vp1_y', 'vp1_z',
            'chi' # ADDED chi column
            # Add any other raw columns identified as necessary from calculate_proton_fits_vars
        ]

        all_raw_data_list = [] # List to store DataFrames from each file
        dates_processed = []
        dates_missing_files = []

        for single_date in daterange(start_time, end_time):
            date_str = single_date.strftime('%Y%m%d')
            print_manager.debug(f"Searching for SF00 FITS CSV for date: {date_str}")

            # Find sf00 file(s) for the date
            print_manager.debug(f" Searching sf00 in: {sf00_base_path} with patterns: {sf00_patterns}")
            sf00_files = find_local_csvs(sf00_base_path, sf00_patterns, date_str)

            if sf00_files:
                # Assuming only one match per pattern per day is expected
                if len(sf00_files) > 1:
                     print_manager.warning(f"Multiple sf00 files found for {date_str}, using first: {sf00_files[0]}")

                sf00_path = sf00_files[0]
                print_manager.debug(f"  Found sf00 file: '{os.path.basename(sf00_path)}'")

                try:
                    print_manager.processing(f"Loading raw FITS data from {os.path.basename(sf00_path)}...")
                    # --- Read CSV file, selecting only needed columns ---
                    try:
                        # Use 'usecols' to load only necessary data
                        df_sf00_raw = pd.read_csv(sf00_path, usecols=lambda col: col in raw_cols_needed)
                        # Check if all needed columns were actually present
                        missing_cols = [col for col in raw_cols_needed if col not in df_sf00_raw.columns]
                        if missing_cols:
                             print_manager.warning(f"  ! Missing required columns in {os.path.basename(sf00_path)}: {missing_cols}. Skipping file.")
                             dates_missing_files.append(date_str)
                             continue
                    except FileNotFoundError:
                         print_manager.error(f"  ✗ Could not find CSV file: {sf00_path}")
                         dates_missing_files.append(date_str)
                         continue # Skip to next date
                    except pd.errors.EmptyDataError:
                         print_manager.warning(f"  ✗ CSV file is empty: {sf00_path}")
                         dates_missing_files.append(date_str)
                         continue # Skip to next date
                    except ValueError as ve: # Catches errors from usecols if a required col doesn't exist
                         print_manager.error(f"  ✗ Error reading specific columns from {sf00_path}: {ve}. Check if required columns exist.")
                         dates_missing_files.append(date_str)
                         continue
                    except Exception as read_e:
                         print_manager.error(f"  ✗ Error reading CSV file {sf00_path}: {read_e}")
                         dates_missing_files.append(date_str)
                         continue # Skip to next date

                    if not df_sf00_raw.empty:
                        all_raw_data_list.append(df_sf00_raw)
                        dates_processed.append(date_str)
                        print_manager.processing(f"  ✓ Raw data loaded for {date_str}")
                    else:
                        print_manager.warning(f"  ✗ DataFrame empty after loading {sf00_path}")
                        dates_missing_files.append(date_str)

                except Exception as e:
                    print_manager.error(f"  ✗ Error during FITS data loading for {date_str}: {e}")
                    import traceback
                    print_manager.debug(traceback.format_exc())
                    dates_missing_files.append(date_str)
            else:
                print_manager.debug(f"  ✗ Missing sf00 file for date {date_str}")
                dates_missing_files.append(date_str)

        if not all_raw_data_list:
            print_manager.warning(f"No raw FITS data could be loaded for the time range {trange}. Missing files for dates: {dates_missing_files}")
            print_manager.time_output("import_data_function", "no raw data loaded")
            return None

        # Consolidate raw data
        print_manager.debug("Consolidating raw FITS data...")
        try:
            final_raw_df = pd.concat(all_raw_data_list, ignore_index=True)
        except Exception as concat_e:
            print_manager.error(f"Error concatenating raw FITS DataFrames: {concat_e}")
            return None

        # Convert time to datetime objects, then to TT2000
        try:
            # Assuming 'time' column contains Unix epoch seconds
            # Using to_numpy() to directly get numpy arrays, avoiding to_pydatetime() completely
            datetime_series = pd.to_datetime(final_raw_df['time'], unit='s', utc=True)
            # Convert to numpy array of datetime64 objects
            datetime_objs = datetime_series.to_numpy()
            # Convert to Python datetime objects for components extraction
            datetime_components_list = [
                [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)]
                for dt in datetime_objs
            ]
            tt2000_array = cdflib.cdfepoch.compute_tt2000(datetime_components_list)
            print_manager.debug(f"Converted final times to TT2000 (Length: {len(tt2000_array)})")
        except Exception as time_e:
            print_manager.error(f"Error converting FITS time column to TT2000: {time_e}")
            return None

        # Create final data dictionary with NumPy arrays
        final_data = {}
        for col in raw_cols_needed:
            if col != 'time': # Exclude the original time column
                try:
                    # Convert column to numpy array, handling potential errors
                    final_data[col] = final_raw_df[col].to_numpy()
                except KeyError:
                    print_manager.warning(f"Column '{col}' not found during final conversion, filling with NaNs.")
                    final_data[col] = np.full(len(tt2000_array), np.nan)
                except Exception as np_e:
                    print_manager.error(f"Error converting column '{col}' to NumPy array: {np_e}")
                    final_data[col] = np.full(len(tt2000_array), np.nan)


        # Sort based on TT2000 times
        try:
            sort_indices = np.argsort(tt2000_array)
            times_sorted = tt2000_array[sort_indices]
            data_sorted = {}
            for var_name in final_data:
                 if final_data[var_name] is not None:
                     # Ensure the data array exists and is not empty before trying to sort
                     if isinstance(final_data[var_name], np.ndarray) and final_data[var_name].size > 0:
                         try:
                             data_sorted[var_name] = final_data[var_name][sort_indices]
                         except IndexError as ie:
                             print_manager.error(f"Sorting IndexError for '{var_name}': {ie}")
                             print_manager.error(f"  Data shape: {final_data[var_name].shape}, Sort indices length: {len(sort_indices)}")
                             # Fill with NaNs as a fallback
                             data_sorted[var_name] = np.full(len(times_sorted), np.nan)
                     else:
                          # Handle cases where data might be None or empty after potential errors
                          print_manager.warning(f"Data for '{var_name}' is empty or None before sorting, filling with NaNs.")
                          data_sorted[var_name] = np.full(len(times_sorted), np.nan)
                 else:
                     data_sorted[var_name] = None # Keep None if it was None
        except Exception as sort_e:
            print_manager.error(f"Error during sorting of raw FITS data: {sort_e}")
            return None

        print_manager.debug(f"Sorted all raw FITS data based on time.")

        # Create and return DataObject containing RAW data
        data_object = DataObject(times=times_sorted, data=data_sorted)
        global_tracker.update_imported_range(trange, data_type) # Track successful import
        print_manager.status(f"✅ - FITS raw data import complete for range {trange}.\n")
        # Calculate output range based on sorted times
        output_range_dt = cdflib.epochs.CDFepoch.to_datetime(times_sorted[[0, -1]])
        print_manager.time_output("import_data_function", output_range_dt.tolist())
        return data_object

    # --- Handle Hammerhead (ham) CSV Loading ---
    elif data_type == 'ham':
        print_manager.debug(f"\n=== Starting Hammerhead CSV Data Import for {trange} ===")

        # Get config for the ham data type
        config = psp_data_types['ham']
        if not config:
            print_manager.error(f"Configuration error: Missing 'ham' data type definition in psp_data_types.py")
            print_manager.time_output("import_data_function", "error: config error")
            return None

        ham_base_path = config.get('local_path')
        ham_patterns = config.get('file_pattern_import', ['*.csv'])  # Default to all CSVs if not specified
        datetime_column = config.get('datetime_column', 'datetime')  # Get datetime column name

        if not ham_base_path:
            print_manager.error(f"Configuration error: Missing 'local_path' for ham.")
            print_manager.time_output("import_data_function", "error: config error")
            return None

        # List to store all loaded data
        all_raw_data_list = []
        all_times = []
        
        for single_date in daterange(start_time, end_time):
            date_str = single_date.strftime('%Y%m%d')
            print_manager.debug(f"Searching for Hammerhead CSV for date: {date_str}")

            # Find Hammerhead file(s) for the date
            print_manager.debug(f" Searching ham in: {ham_base_path} with patterns: {ham_patterns}")
            ham_files = find_local_csvs(ham_base_path, ham_patterns, date_str)

            if ham_files:
                # Assuming only one match per pattern per day is expected
                if len(ham_files) > 1:
                    print_manager.warning(f"Multiple ham files found for {date_str}, using first: {ham_files[0]}")

                ham_path = ham_files[0]
                print_manager.debug(f"  Found ham file: '{os.path.basename(ham_path)}'")

                try:
                    print_manager.processing(f"Loading Hammerhead data from {os.path.basename(ham_path)}...")
                    # Read the CSV file
                    try:
                        # --- MODIFIED: Read without parse_dates ---
                        # ham_df = pd.read_csv(ham_path, parse_dates=[datetime_column])
                        ham_df = pd.read_csv(ham_path)

                        # --- ADDED: Define which column NOT to include in data dict ---
                        # Default to 'datetime' if it exists, otherwise 'time' if it exists
                        exclude_column = None
                        if 'datetime' in ham_df.columns:
                             exclude_column = 'datetime'
                        elif 'time' in ham_df.columns:
                             exclude_column = 'time'
                        else:
                             print_manager.warning("Could not find 'datetime' or 'time' column for exclusion.")
                             # Fallback or specific error handling might be needed

                        # --- ADDED: Convert 'time' (Unix epoch) to TT2000 ---
                        if 'time' in ham_df.columns:
                            try:
                                # Using to_numpy() to directly get numpy arrays
                                datetime_series = pd.to_datetime(ham_df['time'], unit='s', utc=True)
                                datetime_objs = datetime_series.to_numpy() # numpy array of datetime64[ns]

                                # Convert numpy datetime64 to components list for TT2000
                                # Need to handle potential NaT values if any times failed parsing
                                datetime_components_list = []
                                valid_time_mask = pd.notna(datetime_objs) # Mask for valid times
                                temp_dt_objs = datetime_objs[valid_time_mask].astype('datetime64[us]').tolist() # Convert valid ones to Python datetimes via intermediate type

                                comp_idx = 0 # Index for temp_dt_objs
                                for is_valid in valid_time_mask:
                                     if is_valid:
                                         dt = temp_dt_objs[comp_idx]
                                         datetime_components_list.append(
                                              [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)]
                                         )
                                         comp_idx += 1
                                     else:
                                         # Append placeholder for invalid times? Or handle later?
                                         # For now, let TT2000 handle it, might result in errors if list is jagged
                                         # Or maybe just skip? Let's try skipping for now, filtering applies mask later
                                         datetime_components_list.append(None) # Placeholder might cause issues

                                # Filter out None placeholders before computing TT2000
                                valid_components_list = [comp for comp in datetime_components_list if comp is not None]
                                if valid_components_list:
                                     tt2000_array_full = cdflib.cdfepoch.compute_tt2000(valid_components_list)
                                else:
                                     tt2000_array_full = np.array([], dtype=np.int64) # Empty if no valid times

                                # Create a full TT2000 array with NaNs (or appropriate fill) for invalid times
                                tt2000_nan = np.iinfo(np.int64).min # Use min int64 as fill for TT2000 NaNs
                                tt2000_with_nans = np.full(len(valid_time_mask), tt2000_nan, dtype=np.int64)
                                tt2000_with_nans[valid_time_mask] = tt2000_array_full

                                print_manager.debug(f"Converted HAM 'time' to TT2000 (Length: {len(tt2000_with_nans)})")
                                times_tt2000 = tt2000_with_nans # Use the array with NaNs for indexing alignment

                            except Exception as time_e:
                                print_manager.error(f"Error converting HAM 'time' column: {time_e}")
                                import traceback
                                print_manager.debug(traceback.format_exc())
                                continue # Skip this file if time conversion fails
                        else:
                            print_manager.error(f"'time' column not found in {ham_path}")
                            continue # Skip file

                        # --- MODIFIED: Filter by time range using TT2000 ---
                        # Convert requested range to TT2000
                        start_tt2000_req = cdflib.cdfepoch.compute_tt2000(
                            [start_time.year, start_time.month, start_time.day,
                             start_time.hour, start_time.minute, start_time.second,
                             int(start_time.microsecond/1000)]
                        )
                        end_tt2000_req = cdflib.cdfepoch.compute_tt2000(
                            [end_time.year, end_time.month, end_time.day,
                             end_time.hour, end_time.minute, end_time.second,
                             int(end_time.microsecond/1000)]
                        )

                        # Create mask for valid times within the range
                        valid_range_mask = (times_tt2000 >= start_tt2000_req) & (times_tt2000 <= end_tt2000_req)

                        if not np.any(valid_range_mask):
                            print_manager.warning(f"No data in TT2000 time range for {os.path.basename(ham_path)}")
                            continue

                        # Apply mask to TT2000 times
                        times_in_range = times_tt2000[valid_range_mask]
                        all_times.extend(times_in_range) # Extend with TT2000 values

                        # --- MODIFIED: Convert DataFrame to dictionary, excluding the chosen time column ---
                        ham_data = {col: ham_df[col].values[valid_range_mask] # Apply mask to data columns too
                                    for col in ham_df.columns if col != exclude_column}
                        all_raw_data_list.append(ham_data)
                        
                    except Exception as e:
                        print_manager.error(f"Error reading ham CSV file: {e}")
                        import traceback
                        print_manager.debug(traceback.format_exc())
                        continue
                        
                except Exception as e:
                    print_manager.error(f"Error processing {ham_path}: {e}")
                    continue
            else:
                print_manager.warning(f"No Hammerhead files found for date {date_str}")
        
        # Merge data from all files
        combined_data = {}
        if not all_times: # Check if all_times list is empty
             print_manager.warning(f"No Hammerhead data found within time range after processing files.")
             print_manager.time_output("import_data_function", "error: no ham data found")
             return None

        # Ensure all_times is a numpy array for sorting
        all_times_np = np.array(all_times, dtype=np.int64)

        # Sort based on TT2000 times
        sort_indices = np.argsort(all_times_np)
        times_sorted = all_times_np[sort_indices]

        # Concatenate and sort data arrays
        first_data_dict = all_raw_data_list[0] # Use the first dict to get keys
        for key in first_data_dict.keys():
             # Concatenate arrays from all dictionaries for the current key
             try:
                 concatenated_array = np.concatenate([data[key] for data in all_raw_data_list if key in data])
                 # Sort the concatenated array using the same indices
                 combined_data[key] = concatenated_array[sort_indices]
             except ValueError as ve:
                  print_manager.error(f"Error concatenating/sorting HAM data for key '{key}': {ve}")
                  # Handle potential shape mismatches - fill with NaNs
                  combined_data[key] = np.full(len(times_sorted), np.nan)
             except KeyError:
                  # Should not happen if all files have same columns, but handle just in case
                  print_manager.warning(f"Key '{key}' missing in some HAM files during concatenation.")
                  combined_data[key] = np.full(len(times_sorted), np.nan)

        # Create DataObject with sorted TT2000 times and sorted data dictionary
        data_obj = DataObject(times=times_sorted, data=combined_data)
        print_manager.status(f"Successfully loaded Hammerhead data with {len(times_sorted)} time points")
        # Calculate output range from sorted TT2000 times
        if len(times_sorted) > 0:
            output_range_dt = cdflib.epochs.CDFepoch.to_datetime(times_sorted[[0, -1]])
            print_manager.time_output("import_data_function", output_range_dt.tolist())
        else:
             print_manager.time_output("import_data_function", "success - empty range") # Or error?
        return data_obj
        
    else:
        # --- Existing CDF Processing Logic ---
        print_manager.debug(f"\n=== Starting import for {data_type} (CDF) ===")

        # Format dates for TT2000 conversion (needed for CDF processing)
        start_tt2000 = cdflib.cdfepoch.compute_tt2000(
            [start_time.year, start_time.month, start_time.day,
             start_time.hour, start_time.minute, start_time.second,
             int(start_time.microsecond/1000)]
        )
        end_tt2000 = cdflib.cdfepoch.compute_tt2000(
            [end_time.year, end_time.month, end_time.day,
             end_time.hour, end_time.minute, end_time.second,
             int(end_time.microsecond/1000)]
        )

        variables = config.get('data_vars', [])     # Get list of variables to extract

        # FILE SEARCH AND COLLECTION (CDF specific)
        found_files = []
        for single_date in daterange(start_time, end_time):
            year = single_date.year
            date_str = single_date.strftime('%Y%m%d')
            local_dir = os.path.join(config['local_path'].format(data_level=config['data_level']), str(year))

            if config['file_time_format'] == '6-hour':
                # Determine relevant blocks (same logic as check_local_files)
                relevant_blocks_for_date = []
                for hour_block in range(4):
                    block_start_hour = hour_block * 6
                    block_start_dt = datetime.combine(single_date, datetime.min.time(), tzinfo=timezone.utc).replace(hour=block_start_hour)
                    block_end_dt = block_start_dt + timedelta(hours=6)
                    if max(start_time, block_start_dt) < min(end_time, block_end_dt):
                        relevant_blocks_for_date.append(hour_block)

                if not relevant_blocks_for_date: continue

                for block in relevant_blocks_for_date:
                    hour_str = f"{block * 6:02d}"
                    date_hour_str = date_str + hour_str
                    file_pattern = config['file_pattern_import'].format(
                        data_level=config['data_level'],
                        date_hour_str=date_hour_str # Use combined date_hour_str
                    )
                    if os.path.exists(local_dir):
                        pattern = file_pattern.replace('*', '.*') # Glob to regex
                        regex = re.compile(pattern, re.IGNORECASE)
                        matching = [os.path.join(local_dir, f) for f in os.listdir(local_dir) if regex.match(f)]
                        found_files.extend(matching)

            elif config['file_time_format'] == 'daily':
                file_pattern = config['file_pattern_import'].format(
                    data_level=config['data_level'],
                    date_str=date_str
                )
                if os.path.exists(local_dir):
                    pattern = file_pattern.replace('*', '.*') # Glob to regex
                    regex = re.compile(pattern, re.IGNORECASE)
                    matching = [os.path.join(local_dir, f) for f in os.listdir(local_dir) if regex.match(f)]
                    found_files.extend(matching)

        if not found_files:
            print_manager.warning(f"No CDF data files found for {data_type} in the specified time range.")
            print_manager.time_output("import_data_function", "no files found")
            return None

        found_files = sorted(list(set(found_files))) # Get unique sorted list
        print_manager.debug(f"Found {len(found_files)} unique CDF files to process.")

        # DATA EXTRACTION AND PROCESSING (CDF specific)
        times_list = []
        data_dict = {var: [] for var in variables}

        for file_path in found_files:
            print_manager.debug(f"\nProcessing CDF file: {file_path}")
            try:
                with cdflib.CDF(file_path) as cdf_file:
                    print_manager.debug("Successfully opened CDF file")
                    time_vars = [var for var in cdf_file.cdf_info().zVariables if 'epoch' in var.lower()]
                    if not time_vars:
                        print_manager.warning(f"No time variable found in {os.path.basename(file_path)} - skipping")
                        continue # Skip this file if no time var
                    time_var = time_vars[0]
                    print_manager.debug(f"Using time variable: {time_var}")

                    # Quick check of file time boundaries using attributes if possible
                    # This avoids reading full time data just to skip the file
                    global_attrs = cdf_file.globalattsget()
                    file_start_str = global_attrs.get('Time_resolution_start') # Example attribute
                    file_end_str = global_attrs.get('Time_resolution_stop') # Example attribute
                    can_skip_early = False
                    # Add logic here to parse file_start_str/file_end_str and compare with start_tt2000/end_tt2000 if attributes exist
                    # If file range doesn't overlap requested range based on attributes, set can_skip_early = True

                    # if can_skip_early:
                    #     print_manager.debug("Skipping file based on global attribute time range.")
                    #     continue

                    # Get number of records for boundary check
                    var_info = cdf_file.varinq(time_var)
                    n_records = var_info.Last_Rec + 1
                    if n_records <= 0:
                        print_manager.debug("File contains no records - skipping")
                        continue

                    # Read only first and last time points for boundary check
                    first_time_data = cdf_file.varget(time_var, startrec=0, endrec=0)           # Get first time point
                    last_time_data = cdf_file.varget(time_var, startrec=n_records-1, endrec=n_records-1)  # Get last time point
                    if first_time_data is None or last_time_data is None:
                        print_manager.warning(f"Could not read time boundaries for {os.path.basename(file_path)} - skipping")
                        continue

                    print_manager.debug(f"File time range (TT2000): {first_time_data[0]} to {last_time_data[0]}")
                    # Compare TT2000 times directly
                    if last_time_data[0] < start_tt2000 or first_time_data[0] > end_tt2000:
                        print_manager.debug("File outside requested time range - skipping")
                        continue

                    # Read full time data ONLY if file potentially overlaps
                    print_manager.debug("Reading full time data array...")
                    time_data = cdf_file.varget(time_var, epoch=True)
                    if time_data is None or len(time_data) == 0:
                        print_manager.warning(f"Time data is empty in {os.path.basename(file_path)} - skipping")
                        continue
                    print_manager.debug(f"Read {len(time_data)} time points")

                    # Find relevant data indices using TT2000
                    start_idx = np.searchsorted(time_data, start_tt2000, side='left')
                    end_idx = np.searchsorted(time_data, end_tt2000, side='right')
                    print_manager.debug(f"Time indices: {start_idx} to {end_idx}")

                    if start_idx >= end_idx:
                        print_manager.debug("No data within time range for this file after indexing - skipping")
                        continue

                    # Extract time slice (TT2000)
                    time_slice = time_data[start_idx:end_idx]
                    times_list.append(time_slice)
                    print_manager.debug(f"Extracted {len(time_slice)} time points within requested range")

                    # Extract variable data slices
                    for var_name in variables:
                        try:
                            print_manager.debug(f"\nReading variable: {var_name}")
                            # Read only the required slice
                            var_data = cdf_file.varget(var_name, startrec=start_idx, endrec=end_idx-1)
                            if var_data is None:
                                print_manager.warning(f"Could not read data for {var_name} - filling with NaNs")
                                # Create an array of NaNs with the expected shape
                                # Determine expected shape: (len(time_slice), ...) based on var inquiry?
                                # For simplicity, assume shape based on time slice length for now
                                var_data = np.full(len(time_slice), np.nan) # Adjust shape if needed
                            else:
                                print_manager.debug(f"Raw data shape: {var_data.shape}")

                                # Handle fill values
                                var_atts = cdf_file.varattsget(var_name)
                                if "FILLVAL" in var_atts:
                                    fill_val = var_atts["FILLVAL"]
                                    if np.issubdtype(var_data.dtype, np.floating) or np.issubdtype(var_data.dtype, np.integer):
                                        fill_mask = (var_data == fill_val)
                                        if np.any(fill_mask):
                                            # Ensure var_data is float before assigning NaN
                                            if not np.issubdtype(var_data.dtype, np.floating):
                                                var_data = var_data.astype(float)
                                            var_data[fill_mask] = np.nan
                                            print_manager.debug(f"Replaced {np.sum(fill_mask)} fill values ({fill_val}) with NaN")
                                    else:
                                        print_manager.debug("Skipping fill value check for non-numeric data type.")
                                else:
                                    print_manager.debug("No FILLVAL attribute found.")

                                data_dict[var_name].append(var_data)
                                print_manager.debug(f"Successfully stored data slice for {var_name}")

                        except Exception as e:
                            print_manager.warning(f"Error processing {var_name} in {os.path.basename(file_path)}: {e}")
                            # Append NaNs of the correct length if a variable fails
                            data_dict[var_name].append(np.full(len(time_slice), np.nan))
            except Exception as e:
                print_manager.error(f"Error processing CDF file {file_path}: {e}")
                import traceback
                print_manager.debug(traceback.format_exc())
                continue # Skip to next file if this one fails

        # DATA CONSOLIDATION AND CLEANUP (CDF specific)
        if not times_list:
            print_manager.warning(f"No CDF data found in the specified time range after processing files for {data_type}.")
            print_manager.time_output("import_data_function", "no data found")
            return None

        times = np.concatenate(times_list)
        concatenated_data = {}
        print_manager.debug("\nConcatenating CDF data...")
        for var_name in variables:
            data_list = data_dict[var_name]
            if data_list:
                try:
                    # Attempt to concatenate, handle potential shape mismatches
                    concatenated_data[var_name] = np.concatenate(data_list)
                    print_manager.debug(f"  Concatenated {var_name} (Shape: {concatenated_data[var_name].shape})")
                except ValueError as ve:
                    print_manager.error(f"Error concatenating {var_name} from CDFs: {ve}. Filling with NaNs.")
                    concatenated_data[var_name] = np.full(len(times), np.nan)
            else:
                print_manager.warning(f"No data collected for {var_name}, filling with NaNs.")
                concatenated_data[var_name] = np.full(len(times), np.nan) # Store NaNs if no data

        print_manager.debug(f"\nTotal CDF data points after concatenation: {len(times)}")

        # Sort based on time (already TT2000)
        sort_indices = np.argsort(times)
        times_sorted = times[sort_indices]
        data_sorted = {}
        for var_name in variables:
            if concatenated_data[var_name] is not None:
                try:
                    data_sorted[var_name] = concatenated_data[var_name][sort_indices]
                except IndexError as ie:
                    print_manager.error(f"Sorting IndexError for CDF var '{var_name}': {ie}")
                    data_sorted[var_name] = np.full(len(times_sorted), np.nan)
            else:
                data_sorted[var_name] = None

        # Create and return DataObject for CDF
        data_object = DataObject(times=times_sorted, data=data_sorted)
        global_tracker.update_imported_range(trange, data_type)
        print_manager.status(f"✅ - CDF Data import complete for {data_type} range {trange}.\n")
        output_range = [cdflib.epochs.CDFepoch.to_datetime(times_sorted[0]),
                        cdflib.epochs.CDFepoch.to_datetime(times_sorted[-1])]
        print_manager.time_output("import_data_function", output_range)
        return data_object