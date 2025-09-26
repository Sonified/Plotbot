# plotbot/data_import.py
import cdflib
import numpy as np
import os
import re
import pandas as pd # Added for CSV reading
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from fnmatch import fnmatch # Import for wildcard matching
import time as timer
from functools import wraps

def timer_decorator(timer_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timer.perf_counter()
            result = func(*args, **kwargs)
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"⏱️ [{timer_name}] {func.__name__}: {duration_ms:.2f}ms")
            return result
        return wrapper
    return decorator

from .print_manager import print_manager, format_datetime_for_log
from .time_utils import daterange
from .data_tracker import global_tracker
from .data_classes.data_types import data_types, get_local_path # UPDATED PATH
# from .data_cubby import data_cubby # MOVED inside import_data_function
# from .plotbot_helpers import find_local_fits_csvs # This function is defined locally below

# Import the NEW calculation function
# from .calculations.calculate_proton_fits import calculate_proton_fits_vars

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

# Utility function to get project root
def get_project_root():
    """Get the absolute path to the project root directory.
    
    This function works regardless of where the script is run from by using
    __file__ to locate the plotbot package directory and going up one level
    to find the project root.
    
    Returns:
        str: Absolute path to the project root directory
    """
    try:
        # Get the directory containing this file (plotbot/data_import.py)
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get the project root (from plotbot/ to Plotbot/)
        project_root = os.path.dirname(current_file_dir)
        return project_root
    except:
        # Fallback: use current working directory
        print_manager.warning("Could not determine project root from __file__, using current working directory as fallback")
        return os.getcwd()

# Optimized function to convert CDF_EPOCH array to TT2000 array using Numba JIT
def convert_cdf_epoch_to_tt2000_vectorized(cdf_epoch_array):
    """
    Ultra-fast conversion of CDF_EPOCH values to TT2000 using Numba JIT compilation.
    
    This function provides ~6000x speed improvement over the original vectorized approach
    while maintaining sub-millisecond accuracy (mean error: 0.5ms, max error: <1ms).
    
    Args:
        cdf_epoch_array: numpy array of CDF_EPOCH values (milliseconds since Year 0)
    
    Returns:
        numpy array of TT2000 values (nanoseconds since J2000)
    """
    import time
    start_time = timer.time()
    
    print_manager.debug(f"  Converting {len(cdf_epoch_array)} CDF_EPOCH values to TT2000 using optimized Numba method")
    
    # Use the optimized Numba conversion
    tt2000_array = _convert_cdf_epoch_to_tt2000_numba_optimized(cdf_epoch_array)
    
    end_time = timer.time()
    conversion_time = end_time - start_time
    
    print_manager.debug(f"  Numba conversion completed: {len(tt2000_array)} values converted in {conversion_time:.3f} seconds")
    if len(cdf_epoch_array) > 1000:
        rate = len(cdf_epoch_array) / conversion_time
        print_manager.debug(f"  Conversion rate: {rate:.0f} values/second")
    
    return tt2000_array

def _convert_cdf_epoch_to_tt2000_numba_optimized(cdf_epoch_array):
    """
    Optimized Numba-based CDF_EPOCH to TT2000 conversion with calibrated accuracy.
    
    This function uses a calibrated offset approach to ensure accuracy while 
    maintaining maximum performance through JIT compilation.
    """
    try:
        import numba
        from numba import njit
        NUMBA_AVAILABLE = True
    except ImportError:
        print_manager.warning("Numba not available, falling back to standard vectorized conversion")
        return _convert_cdf_epoch_to_tt2000_fallback(cdf_epoch_array)
    
    # Calibrate offset using first data point for maximum accuracy
    test_epoch = cdf_epoch_array[0]
    ref_components = cdflib.cdfepoch.breakdown_epoch([test_epoch])
    year, month, day, hour, minute, second, millisecond = ref_components
    ref_tt2000 = cdflib.cdfepoch.compute_tt2000([
        int(year), int(month), int(day),
        int(hour), int(minute), int(second),
        int(millisecond), 0, 0
    ])
    
    # Calculate calibrated offset
    simple_result = test_epoch * 1000000.0  # Convert ms to ns
    offset_ns = ref_tt2000 - simple_result
    
    # Use JIT-compiled core function for maximum performance
    return _numba_convert_core(cdf_epoch_array, offset_ns)

# Import numba and define JIT functions at module level for optimal performance
try:
    import numba
    from numba import njit
    
    @njit(parallel=True, fastmath=True)
    def _numba_convert_core(cdf_epoch_array, offset_ns):
        """
        Numba JIT-compiled core conversion function.
        
        Provides C-speed performance with parallel execution.
        """
        n = len(cdf_epoch_array)
        result = np.empty(n, dtype=np.int64)
        ns_per_ms = 1000000.0
        
        for i in numba.prange(n):
            result[i] = int(cdf_epoch_array[i] * ns_per_ms + offset_ns)
        
        return result
    
    NUMBA_AVAILABLE = True
    
except ImportError:
    NUMBA_AVAILABLE = False
    print_manager.debug("Numba not available - time conversion will use fallback method")

def _convert_cdf_epoch_to_tt2000_fallback(cdf_epoch_array):
    """
    Fallback conversion method when Numba is not available.
    
    Uses the original vectorized cdflib approach for compatibility.
    """
    print_manager.debug(f"  Using fallback vectorized method for {len(cdf_epoch_array)} values")
    
    # Use cdflib's vectorized breakdown_epoch to convert to datetime components
    datetime_components = cdflib.cdfepoch.breakdown_epoch(cdf_epoch_array)
    
    # Convert to TT2000 using vectorized compute_tt2000
    if datetime_components.ndim == 1:
        # Single value case
        components_with_sub_ms = np.append(datetime_components, [0, 0])  # Add microsecond, nanosecond
        tt2000_array = cdflib.cdfepoch.compute_tt2000(components_with_sub_ms)
    else:
        # Array case - add microsecond and nanosecond columns
        n_points = datetime_components.shape[0]
        microseconds = np.zeros((n_points, 1))
        nanoseconds = np.zeros((n_points, 1))
        components_with_sub_ms = np.hstack([datetime_components, microseconds, nanoseconds])
        tt2000_array = cdflib.cdfepoch.compute_tt2000(components_with_sub_ms)
    
    return tt2000_array

# Constant for Unix to TT2000 conversion offset
UNIX_TO_TT2000_OFFSET = -946728000000000000  # As determined by cdflib.cdfepoch.unixtime_to_tt2000(0)

if NUMBA_AVAILABLE:
    @njit(parallel=True, fastmath=True)
    def _numba_convert_unix_to_tt2000_core(unix_epoch_array):
        """
        Numba JIT-compiled core conversion function for Unix time to TT2000.
        """
        n = len(unix_epoch_array)
        result = np.empty(n, dtype=np.int64)
        ns_per_s = 1000000000.0
        
        for i in numba.prange(n):
            result[i] = int(unix_epoch_array[i] * ns_per_s) + UNIX_TO_TT2000_OFFSET
            
        return result

def convert_unix_to_tt2000_vectorized(unix_epoch_array):
    """
    Ultra-fast conversion of Unix epoch values (seconds) to TT2000 using Numba.
    """
    import time
    start_time = timer.time()
    
    print_manager.debug(f"  Converting {len(unix_epoch_array)} Unix epoch values to TT2000 using optimized Numba method")
    
    if not NUMBA_AVAILABLE:
        print_manager.warning("Numba not available, falling back to cdflib.unixtime_to_tt2000")
        return cdflib.cdfepoch.unixtime_to_tt2000(unix_epoch_array)
        
    tt2000_array = _numba_convert_unix_to_tt2000_core(unix_epoch_array)
    
    end_time = timer.time()
    conversion_time = end_time - start_time
    
    print_manager.debug(f"  Numba Unix conversion completed: {len(tt2000_array)} values in {conversion_time:.3f} seconds")
    if len(unix_epoch_array) > 1000 and conversion_time > 0:
        rate = len(unix_epoch_array) / conversion_time
        print_manager.debug(f"  Conversion rate: {rate:.0f} values/second")
    
    return tt2000_array

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

@timer_decorator("TIMER_IMPORT_DATA_FUNCTION")
def import_data_function(trange, data_type):
    """Import data function that reads CDF or calculates FITS CSV data within the specified time range."""
    
    # Step: Initialize import_data_function
    from .get_data import next_step, end_step
    step_key, step_start = next_step("Initialize import_data_function", data_type)
    
    data_type_requested_at_start = data_type # Capture for final debug print
    data_obj_to_return = None # Initialize a variable to hold the object to be returned
    
    print_manager.debug('Import data function called')
    
    # Format trange for printing (remove .000000)
    trange_str = str(trange)
    if '.000000' in trange_str:
        trange_str = trange_str.replace('.000000', '')
    print_manager.debug(f"Input trange: {trange_str}")
    print_manager.variable_testing(f"import_data_function called for data_type: {data_type}")
    
    # Add time tracking for function entry
    print_manager.time_input("import_data_function", trange)
    
    end_step(step_key, step_start, {"data_type": data_type, "trange": trange_str})
    
    # Step: Determine data source type
    step_key, step_start = next_step("Determine data source type", data_type)
    
    # Determine if this is a request for calculated FITS data
    # We'll use a placeholder data_type like 'fits_calculated' for now
    # OR check if requested data_type requires sf00/sf01 calculation
    # For simplicity, let's assume a specific trigger type for now.
    # We need a clear way to know when to perform the FITS calculation.
    # Maybe check if data_type is NOT in data_types but is a known calculated product?
    # Let's refine this trigger logic. How should plotbot request this calculation?
    #
    # --> TEMPORARY APPROACH: Define a specific data_type trigger
    FITS_CALCULATED_TRIGGER = 'fits_calculated'

    is_fits_calculation = (data_type == FITS_CALCULATED_TRIGGER)
    
    # Check if this is a CDF data type (from custom_classes)
    is_cdf_data_type = False
    if not is_fits_calculation and data_type in data_types:
        config = data_types[data_type]
        is_cdf_data_type = config.get('data_sources', [None])[0] == 'local_cdf'

    if not is_fits_calculation and not is_cdf_data_type and data_type not in data_types:
        print_manager.variable_testing(f"Error: {data_type} not found in data_types and is not the FITS calculation trigger.")
        print_manager.time_output("import_data_function", "error: invalid data_type")
        end_step(step_key, step_start, {"error": "invalid data_type"})
        return None
    
    # Get config - if it's a standard type, get its config.
    # If it's the FITS calculation, we'll fetch sf00/sf01 configs later.
    if not is_fits_calculation:
        print_manager.variable_testing(f"Getting configuration for {'CDF' if is_cdf_data_type else 'standard'} data type: {data_type}")
        config = data_types[data_type]
    else:
        # config = None # Explicitly set config to None or handle later
        print_manager.variable_testing(f"Recognized request for calculated FITS data.")
    
    end_step(step_key, step_start, {"is_fits_calculation": is_fits_calculation, "config_found": not is_fits_calculation})
    
    # Step: Parse time range
    step_key, step_start = next_step("Parse time range")
    
    # Parse times using flexible parser and ensure UTC timezone
    try:
        from dateutil.parser import parse
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc) # Ensure UTC
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)   # Ensure UTC
        print_manager.time_tracking(f"Parsed time range: {format_datetime_for_log(start_time)} to {format_datetime_for_log(end_time)}")
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        print_manager.time_output("import_data_function", "error: time parsing failed")
        end_step(step_key, step_start, {"error": "time parsing failed"})
        return None
    
    # Format the original trange list using the helper for the next print statement
    formatted_trange_list = [format_datetime_for_log(t) for t in trange]
    print_manager.debug(f"\nImporting data for UTC time range: {formatted_trange_list}")
    
    end_step(step_key, step_start, {"start_time": format_datetime_for_log(start_time), "end_time": format_datetime_for_log(end_time)})

    #====================================================================
    # CHECK DATA SOURCE TYPE (FITS Calculation vs CDF vs Other Local CSV)
    #====================================================================

    if is_fits_calculation:
        # --- FITS Data Loading Logic (Modified) ---
        
        # Step: Load FITS raw data
        step_key, step_start = next_step("Load FITS raw data", data_type)
        
        print_manager.debug(f"\n=== Starting FITS Raw Data Import for {trange} ===")

        # Get config for the required input type (sf00 only needed now)
        try:
            sf00_config = data_types['sf00_fits']
        except KeyError as e:
            print_manager.error(f"Configuration error: Missing 'sf00_fits' data type definition in data_types.py")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
            return None

        if not sf00_config:
            print_manager.error(f"Configuration error: Could not load config for sf00_fits.")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
            return None

        sf00_base_path = sf00_config.get('local_path')
        sf00_patterns = sf00_config.get('file_pattern_import')

        if not sf00_base_path or not sf00_patterns:
            print_manager.error(f"Configuration error: Missing 'local_path' or 'file_pattern_import' for sf00.")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
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
            end_step(step_key, step_start, {"error": "no raw data loaded"})
            return None

        # Consolidate raw data
        print_manager.debug("Consolidating raw FITS data...")
        try:
            final_raw_df = pd.concat(all_raw_data_list, ignore_index=True)
        except Exception as concat_e:
            print_manager.error(f"Error concatenating raw FITS DataFrames: {concat_e}")
            end_step(step_key, step_start, {"error": "concatenation error"})
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
            end_step(step_key, step_start, {"error": "time conversion error"})
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
            end_step(step_key, step_start, {"error": "sorting error"})
            return None

        print_manager.debug(f"Sorted all raw FITS data based on time.")

        # Create and return DataObject containing RAW data
        data_object = DataObject(times=times_sorted, data=data_sorted)
        global_tracker.update_imported_range(trange, data_type) # Track successful import
        print_manager.status(f"✅ - FITS raw data import complete for range {trange}.\n")
        # Calculate output range based on sorted times
        output_range_dt = cdflib.epochs.CDFepoch.to_datetime(times_sorted[[0, -1]])
        print_manager.time_output("import_data_function", output_range_dt.tolist())

        # === DIAGNOSTIC PRINT BEFORE RETURN ===
        print_manager.debug(f"*** IMPORT_DATA_DEBUG (FITS Path) for data_type '{data_type}' (originally requested: '{data_type_requested_at_start}') ***")
        if data_object is not None:
            if hasattr(data_object, 'times') and data_object.times is not None:
                print_manager.debug(f"    DataObject.times length: {len(data_object.times)}, dtype: {data_object.times.dtype if hasattr(data_object.times, 'dtype') else type(data_object.times)}")
            else:
                print_manager.debug(f"    DataObject.times is None or missing.")
            
            if hasattr(data_object, 'data') and isinstance(data_object.data, dict):
                print_manager.debug(f"    DataObject.data keys: {list(data_object.data.keys())}")
                # Specific check for mag_RTN if it was the initially requested type
                if data_type_requested_at_start == 'mag_RTN': 
                    expected_key = 'psp_fld_l2_mag_RTN'
                    if expected_key in data_object.data:
                        val = data_object.data[expected_key]
                        val_type = type(val)
                        val_shape = val.shape if hasattr(val, 'shape') else 'N/A'
                        val_len = len(val) if hasattr(val, '__len__') else 'N/A' # Check for __len__ before calling len()
                        print_manager.debug(f"        '{expected_key}' is PRESENT. Type: {val_type}, Shape: {val_shape}, Len: {val_len}")
                    else:
                        print_manager.debug(f"        '{expected_key}' is MISSING from data_object.data for mag_RTN request.")
            else:
                print_manager.debug(f"    DataObject.data is None or not a dict.")
        else:
            print_manager.debug(f"    data_object is None at final diagnostic print (FITS Path).")
        # === END DIAGNOSTIC PRINT ===

        data_obj_to_return = data_object # data_object is used in FITS path
        end_step(step_key, step_start, {"data_object": data_object})
        return data_obj_to_return

    # --- Handle Local Support Data (various file types: NPZ, CSV, JSON, HDF5, etc.) ---
    elif config and 'local_support_data' in config.get('data_sources', []):
        
        # Step: Load local support data
        step_key, step_start = next_step("Load local support data", data_type)
        
        print_manager.debug(f"\n=== Starting Local Support Data Import for {trange} ===")
        
        support_base_path = config.get('local_path')
        file_pattern = config.get('file_pattern_import')
        
        if not support_base_path or not file_pattern:
            print_manager.error(f"Configuration error: Missing 'local_path' or 'file_pattern_import' for {data_type}.")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
            return None
        
        # Resolve support_base_path relative to project root for robust path resolution
        if not os.path.isabs(support_base_path):
            project_root = get_project_root()
            support_base_path = os.path.join(project_root, support_base_path)
            print_manager.debug(f"Resolved support_base_path to: {support_base_path}")
        
        # Search for the file in support_data and subfolders
        support_file_path = None
        for root, dirs, files in os.walk(support_base_path):
            for filename in files:
                if filename == file_pattern:  # Exact match for support files
                    support_file_path = os.path.join(root, filename)
                    break
            if support_file_path:
                break
        
        if not support_file_path:
            print_manager.error(f"Could not find {file_pattern} in {support_base_path} or its subfolders.")
            print_manager.time_output("import_data_function", "error: file not found")
            end_step(step_key, step_start, {"error": "file not found"})
            return None
        
        print_manager.debug(f"Found support data file: {support_file_path}")
        
        try:
            # Determine file type and load accordingly
            file_extension = os.path.splitext(support_file_path)[1].lower()
            
            if file_extension == '.npz':
                # Handle NPZ files (e.g., Parker positional data)
                print_manager.debug(f"Loading NPZ file: {os.path.basename(support_file_path)}")
                loaded_data = np.load(support_file_path)
                print_manager.debug(f"NPZ file loaded successfully. Contains: {list(loaded_data.files)}")
                
                # Create a DataObject with the NPZ data structure
                # This ensures compatibility with the caching system while preserving the NPZ interface
                data_object = DataObject(times=loaded_data.get('times', []), data=loaded_data)
                
            elif file_extension == '.csv':
                # Handle CSV files
                print_manager.debug(f"Loading CSV file: {os.path.basename(support_file_path)}")
                loaded_data = pd.read_csv(support_file_path)
                print_manager.debug(f"CSV file loaded successfully. Shape: {loaded_data.shape}")
                data_object = loaded_data  # Return DataFrame
                
            elif file_extension == '.json':
                # Handle JSON files
                import json
                print_manager.debug(f"Loading JSON file: {os.path.basename(support_file_path)}")
                with open(support_file_path, 'r') as f:
                    loaded_data = json.load(f)
                print_manager.debug(f"JSON file loaded successfully.")
                data_object = loaded_data  # Return dict/list
                
            elif file_extension in ['.h5', '.hdf5']:
                # Handle HDF5 files
                import h5py
                print_manager.debug(f"Loading HDF5 file: {os.path.basename(support_file_path)}")
                loaded_data = h5py.File(support_file_path, 'r')
                print_manager.debug(f"HDF5 file opened successfully.")
                data_object = loaded_data  # Return h5py file object
                
            else:
                print_manager.error(f"Unsupported file type: {file_extension} for {support_file_path}")
                print_manager.time_output("import_data_function", "error: unsupported file type")
                end_step(step_key, step_start, {"error": "unsupported file type"})
                return None
            
            # For support data, we typically don't need time filtering since they often contain 
            # full mission datasets. The respective data classes handle time clipping internally.
            global_tracker.update_imported_range(trange, data_type)
            print_manager.status(f"✅ - Local support data import complete for {data_type}.\n")
            
            print_manager.time_output("import_data_function", f"success - loaded {file_pattern}")
            
            # === DIAGNOSTIC PRINT BEFORE RETURN ===
            print_manager.debug(f"*** IMPORT_DATA_DEBUG (Local Support Data Path) for data_type '{data_type}' ***")
            print_manager.debug(f"    File type: {file_extension}, File: {os.path.basename(support_file_path)}")
            if file_extension == '.npz':
                print_manager.debug(f"    NPZ contents: {list(loaded_data.files)}")
            elif file_extension == '.csv':
                print_manager.debug(f"    CSV shape: {loaded_data.shape}, columns: {list(loaded_data.columns)}")
            
            data_obj_to_return = data_object
            end_step(step_key, step_start, {"data_object": data_object})
            return data_obj_to_return
            
        except Exception as e:
            print_manager.error(f"Error loading support data file {support_file_path}: {e}")
            import traceback
            print_manager.debug(traceback.format_exc())
            print_manager.time_output("import_data_function", f"error: {file_extension} loading failed")
            end_step(step_key, step_start, {"error": f"{file_extension} loading failed"})
            return None
    
    # --- Handle Hammerhead (ham) CSV Loading ---
    elif data_type == 'ham':
        
        # Step: Load HAM CSV data
        step_key, step_start = next_step("Load HAM CSV data", data_type)
        
        print_manager.debug(f"\n=== Starting Hammerhead CSV Data Import for {trange} ===")

        # Get config for the ham data type
        config = data_types['ham']
        if not config:
            print_manager.error(f"Configuration error: Missing 'ham' data type definition in data_types.py")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
            return None

        # CRITICAL FIX: Use get_local_path to get absolute path that works from subdirectories
        # get_local_path is already imported at the top of this file  
        ham_base_path = get_local_path('ham')
        ham_patterns = config.get('file_pattern_import', ['*.csv'])  # Default to all CSVs if not specified
        datetime_column = config.get('datetime_column', 'datetime')  # Get datetime column name

        if not ham_base_path:
            print_manager.error(f"Configuration error: Missing 'local_path' for ham.")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
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
                                datetime_series_naive = datetime_series.dt.tz_localize(None) # Convert to timezone-naive UTC
                                datetime_objs_naive = datetime_series_naive.to_numpy() # numpy array of timezone-naive datetime64[ns]

                                # Convert numpy datetime64 to components list for TT2000
                                # Need to handle potential NaT values if any times failed parsing
                                datetime_components_list = []
                                valid_time_mask = pd.notna(datetime_objs_naive) # Mask for valid times using naive array
                                # Use the naive array directly, conversion to datetime64[us] is safer now
                                temp_dt_objs = datetime_objs_naive[valid_time_mask].astype('datetime64[us]').tolist()

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
             end_step(step_key, step_start, {"error": "no ham data found"})
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

        # === DIAGNOSTIC PRINT BEFORE RETURN ===
        print_manager.debug(f"*** IMPORT_DATA_DEBUG (HAM Path) for data_type '{data_type}' (originally requested: '{data_type_requested_at_start}') ***")
        if data_obj is not None: 
            if hasattr(data_obj, 'times') and data_obj.times is not None:
                print_manager.time_output("import_data_function", f"    DataObject.times length: {len(data_obj.times)}, dtype: {data_obj.times.dtype if hasattr(data_obj.times, 'dtype') else type(data_obj.times)}")
            else:
                print_manager.time_output("import_data_function", f"    DataObject.times is None or missing.")
            if hasattr(data_obj, 'data') and isinstance(data_obj.data, dict):
                print_manager.time_output("import_data_function", f"    DataObject.data keys: {list(data_obj.data.keys())}")
            else:
                print_manager.time_output("import_data_function", f"    DataObject.data is None or not a dict.")
        else:
            print_manager.debug(f"    data_obj is None at final diagnostic print (HAM Path).")
        # === END DIAGNOSTIC PRINT ===

        data_obj_to_return = data_obj # data_obj is used in HAM path
        end_step(step_key, step_start, {"data_object": data_obj})
        return data_obj_to_return
        
    # --- Handle Custom CDF Data Types (auto-generated classes) ---
    elif is_cdf_data_type:
        
        # Step: Load custom CDF data
        step_key, step_start = next_step("Load custom CDF data", data_type)
        
        print_manager.debug(f"\n=== Starting Custom CDF Data Import for {data_type} ===")
        
        # Get the CDF file path from configuration
        cdf_base_path = config.get('local_path')
        file_pattern = config.get('file_pattern_import', '*.cdf')
        
        # Check if we should get the path from class metadata
        original_cdf_file = None
        if cdf_base_path == 'FROM_CLASS_METADATA':
            print_manager.debug("Getting CDF file path from class metadata...")
            
            # Get the class instance from data_cubby to read metadata
            from .data_cubby import data_cubby
            class_name = config.get('cdf_class_name', data_type)
            class_instance = data_cubby.grab(class_name)
            
            if class_instance and hasattr(class_instance, '_original_cdf_file_path'):
                original_cdf_file = class_instance._original_cdf_file_path
                cdf_base_path = os.path.dirname(original_cdf_file)
                print_manager.debug(f"Using CDF file path from metadata: {original_cdf_file}")
                print_manager.debug(f"CDF directory: {cdf_base_path}")
            else:
                # Fallback to default path if metadata is not available
                fallback_path = config.get('default_cdf_path')
                if fallback_path and os.path.exists(fallback_path):
                    cdf_base_path = fallback_path
                    print_manager.debug(f"Metadata not available, using fallback path: {fallback_path}")
                else:
                    print_manager.error(f"Could not get CDF file path from class metadata for {data_type} and no valid fallback path")
                    end_step(step_key, step_start, {"error": "no metadata path"})
                    return None
        
        if not cdf_base_path:
            print_manager.error(f"Configuration error: Missing 'local_path' for CDF data type {data_type}.")
            print_manager.time_output("import_data_function", "error: config error")
            end_step(step_key, step_start, {"error": "config error"})
            return None
        
        # Resolve CDF base path
        if not os.path.isabs(cdf_base_path):
            project_root = get_project_root()
            cdf_base_path = os.path.join(project_root, cdf_base_path)
            print_manager.debug(f"Resolved CDF base path to: {cdf_base_path}")
        
        # Find CDF files using smart pattern discovery
        cdf_files = []
        
        # SMART SCAN: Try pattern-based discovery first
        if class_instance and hasattr(class_instance, '_cdf_file_pattern') and cdf_base_path and os.path.exists(cdf_base_path):
            import glob
            pattern = class_instance._cdf_file_pattern
            pattern_path = os.path.join(cdf_base_path, pattern)
            matching_files = glob.glob(pattern_path)
            
            if matching_files:
                cdf_files = matching_files
                print_manager.debug(f"🎯 Smart scan found {len(cdf_files)} files using pattern: {pattern}")
                for f in cdf_files:
                    print_manager.debug(f"   📄 {os.path.basename(f)}")
                
                # Apply time filtering if trange is available and we have multiple files
                if len(cdf_files) > 1 and 'trange' in locals():
                    try:
                        from dateutil.parser import parse
                        from .data_import_cdf import filter_cdf_files_by_time
                        start_time = parse(trange[0])
                        end_time = parse(trange[1])
                        filtered_files = filter_cdf_files_by_time(cdf_files, start_time, end_time)
                        if filtered_files:
                            cdf_files = filtered_files
                            print_manager.debug(f"⚡ Time filter reduced to {len(cdf_files)} relevant files")
                    except Exception as e:
                        print_manager.debug(f"Time filtering failed, using all pattern matches: {e}")
        
        # Fallback 1: Use exact file from metadata
        if not cdf_files and original_cdf_file and os.path.exists(original_cdf_file):
            cdf_files = [original_cdf_file]
            print_manager.debug(f"📌 Fallback to exact file from metadata: {os.path.basename(original_cdf_file)}")
        
        # Fallback 2: Search for all CDF files in directory
        if not cdf_files and cdf_base_path and os.path.exists(cdf_base_path):
            for file in os.listdir(cdf_base_path):
                if file.endswith('.cdf'):
                    cdf_files.append(os.path.join(cdf_base_path, file))
            print_manager.debug(f"🔍 Final fallback found {len(cdf_files)} CDF files in directory: {cdf_base_path}")
        
        if not cdf_files:
            print_manager.error(f"No CDF files found for {data_type}")
            print_manager.time_output("import_data_function", "error: no cdf files")
            end_step(step_key, step_start, {"error": "no cdf files"})
            return None
        
        # Use the first file found (or merge multiple files later)
        cdf_file_path = cdf_files[0]
        print_manager.debug(f"Using CDF file: {os.path.basename(cdf_file_path)}")
        
        try:
            # Load CDF data using cdflib
            with cdflib.CDF(cdf_file_path) as cdf_file:
                print_manager.debug(f"Successfully opened CDF file: {os.path.basename(cdf_file_path)}")
                
                # Get list of all variables
                cdf_info = cdf_file.cdf_info()
                all_variables = cdf_info.zVariables + cdf_info.rVariables
                
                # Find time variable
                time_var = None
                for var_name in all_variables:
                    if any(keyword in var_name.lower() for keyword in ['epoch', 'time', 'fft_time']):
                        time_var = var_name
                        break
                
                if not time_var:
                    print_manager.error(f"No time variable found in CDF file")
                    end_step(step_key, step_start, {"error": "no time variable"})
                    return None
                
                print_manager.debug(f"Using time variable: {time_var}")
                
                # Load time data
                times = cdf_file.varget(time_var)
                print_manager.debug(f"Loaded {len(times)} time points")
                
                # CRITICAL FIX: Add time range filtering (like Standard CDF Processing)
                # Convert requested time range to same format as CDF times
                try:
                    # Convert trange to TT2000 for comparison
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
                    
                    # Check epoch type and convert CDF times if needed
                    epoch_var_info = cdf_file.varinq(time_var)
                    epoch_type = epoch_var_info.Data_Type_Description
                    print_manager.debug(f"CDF time variable type: {epoch_type}")
                    
                    # Convert CDF times to TT2000 if needed (for comparison)
                    if 'TT2000' in epoch_type:
                        times_tt2000 = times
                    elif 'CDF_EPOCH' in epoch_type:
                        print_manager.debug("Converting CDF_EPOCH to TT2000 for filtering")
                        times_tt2000 = np.array([cdflib.cdfepoch.to_datetime(t) for t in times])
                        times_tt2000 = np.array([cdflib.cdfepoch.compute_tt2000(
                            [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond//1000]
                        ) for dt in times_tt2000])
                    else:
                        # Assume already compatible format
                        times_tt2000 = times
                    
                    # Find time range indices
                    start_idx = np.searchsorted(times_tt2000, start_tt2000, side='left')
                    end_idx = np.searchsorted(times_tt2000, end_tt2000, side='right')
                    
                    print_manager.debug(f"Time range filtering: indices {start_idx} to {end_idx} out of {len(times)}")
                    
                    if start_idx >= end_idx or start_idx >= len(times):
                        print_manager.warning(f"No data in requested time range for {data_type}")
                        end_step(step_key, step_start, {"error": "no data in range"})
                        return None
                    
                    # Filter times to requested range
                    times_filtered = times[start_idx:end_idx]
                    print_manager.debug(f"Filtered to {len(times_filtered)} time points in requested range")
                    
                except Exception as e:
                    print_manager.warning(f"Time filtering failed, loading all data: {e}")
                    start_idx = 0
                    end_idx = len(times)
                    times_filtered = times
                
                # Load all other variables with time filtering
                data_dict = {time_var: times_filtered}
                for var_name in all_variables:
                    if var_name != time_var:
                        try:
                            # Check if this is a frequency/metadata variable (1D, doesn't change with time)
                            var_info = cdf_file.varinq(var_name)
                            var_shape = var_info.Dim_Sizes
                            
                            # If variable is 1D (like frequencies), load without time filtering
                            if len(var_shape) == 0 or (len(var_shape) == 1 and var_shape[0] <= 1000):
                                print_manager.debug(f"Loading {var_name} as metadata variable (no time filtering)")
                                var_data = cdf_file.varget(var_name)
                            else:
                                # FIXED: Use time range filtering for time-dependent variables
                                if start_idx < end_idx and end_idx <= len(times):
                                    var_data = cdf_file.varget(var_name, startrec=start_idx, endrec=end_idx-1)
                                    print_manager.debug(f"Loaded {var_name} with time filtering: shape {var_data.shape}")
                                else:
                                    var_data = cdf_file.varget(var_name)
                                    print_manager.debug(f"Loaded {var_name} without filtering (fallback): shape {var_data.shape}")
                            
                            data_dict[var_name] = var_data
                            
                        except Exception as e:
                            print_manager.warning(f"Failed to load variable {var_name}: {e}")
                            # Add placeholder for missing variables to prevent KeyError
                            data_dict[var_name] = None
                
                # Create DataObject
                data_object = DataObject(times=times_filtered, data=data_dict)
                
                # Update tracker
                global_tracker.update_imported_range(trange, data_type)
                print_manager.status(f"✅ Custom CDF data import complete for {data_type}")
                
                # Debug output
                print_manager.debug(f"*** IMPORT_DATA_DEBUG (Custom CDF Path) for data_type '{data_type}' ***")
                print_manager.debug(f"    Loaded {len(data_dict)} variables from {os.path.basename(cdf_file_path)}")
                print_manager.debug(f"    Time range: {len(times_filtered)} points")
                
                data_obj_to_return = data_object
                end_step(step_key, step_start, {"data_object": data_object})
                return data_obj_to_return
                
        except Exception as e:
            print_manager.error(f"Failed to load CDF file {cdf_file_path}: {e}")
            import traceback
            traceback.print_exc()
            end_step(step_key, step_start, {"error": "cdf load failed"})
            return None
        
    else:
        # --- Existing CDF Processing Logic ---
        print_manager.time_output("import_data_function", f"*** IDF_DEBUG: Entered Standard CDF Processing for {data_type} ***")
        print_manager.time_output("import_data_function", f"\n=== Starting import for {data_type} (CDF) ===")

        # Format dates for TT2000 conversion (needed for CDF processing)
        try:
            print_manager.time_output("import_data_function", f"*** IDF_DEBUG: About to compute start_tt2000 for start_time: {start_time} ***")
            start_tt2000 = cdflib.cdfepoch.compute_tt2000(
                [start_time.year, start_time.month, start_time.day,
                 start_time.hour, start_time.minute, start_time.second,
                 int(start_time.microsecond/1000)]
            )
            print_manager.time_output("import_data_function", f"*** IDF_DEBUG: Computed start_tt2000: {start_tt2000}. About to compute end_tt2000 for end_time: {end_time} ***")
            end_tt2000 = cdflib.cdfepoch.compute_tt2000(
                [end_time.year, end_time.month, end_time.day,
                 end_time.hour, end_time.minute, end_time.second,
                 int(end_time.microsecond/1000)]
            )
            print_manager.time_output("import_data_function", f"*** IDF_DEBUG: Computed end_tt2000: {end_tt2000} ***")
        except Exception as e_tt2000_conv:
            print_manager.time_output("import_data_function", f"*** IDF_DEBUG: ERROR during start/end TT2000 conversion for req range: {e_tt2000_conv} ***")
            end_step(step_key, step_start, {"error": "TT2000 conversion error"})
            return None 

        try:
            # to_datetime returns a numpy array of datetime64 if input is scalar TT2000
            start_tt2000_dt_val = cdflib.cdfepoch.to_datetime(start_tt2000)[0] 
            end_tt2000_dt_val = cdflib.cdfepoch.to_datetime(end_tt2000)[0]
            print_manager.debug(f"  Requested datetime range (from TT2000 conversion): {start_tt2000_dt_val} to {end_tt2000_dt_val}")
        except Exception as e_to_datetime_conv:
            print_manager.time_output("import_data_function", f"*** IDF_DEBUG: ERROR converting TT2000 req range to datetime: {e_to_datetime_conv} ***")
            print_manager.time_output("import_data_function", f"      start_tt2000 was: {start_tt2000}, end_tt2000 was: {end_tt2000}")
            end_step(step_key, step_start, {"error": "datetime conversion error"})
            return None

        variables = config.get('data_vars', [])     # Get list of variables to extract

        # FILE SEARCH AND COLLECTION (CDF specific)
        found_files = []
        for single_date in daterange(start_time, end_time):
            year = single_date.year
            date_str = single_date.strftime('%Y%m%d')
            local_dir = os.path.join(get_local_path(data_type).format(data_level=config['data_level']), str(year))

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
                file_pattern_template = config['file_pattern_import']
                file_pattern = file_pattern_template.format(
                    data_level=config['data_level'],
                    date_str=date_str
                )
                print_manager.debug(f"    Searching for DAILY pattern: '{file_pattern}' in dir: '{local_dir}'")
                if os.path.exists(local_dir):
                    # list_dir_files = os.listdir(local_dir) # Keep for debug if needed
                    # print_manager.debug(f"      Files in dir: {list_dir_files[:10]} ... (total {len(list_dir_files)})") # ADDED - potentially long
                    pattern_for_re = file_pattern.replace('*', '.*') # Glob to regex
                    regex = re.compile(pattern_for_re, re.IGNORECASE)
                    current_dir_matches = []
                    for f_name in os.listdir(local_dir):
                        if regex.match(f_name):
                            current_dir_matches.append(os.path.join(local_dir, f_name))
                            print_manager.debug(f"      MATCHED file: {f_name} with pattern {pattern_for_re}") # ADDED
                    found_files.extend(current_dir_matches)
                else:
                    print_manager.debug(f"    Local directory does not exist: {local_dir}") # ADDED

        if not found_files:
            print_manager.warning(f"No CDF data files found for {data_type} in the specified time range using root path {config.get('local_path')}. Searched for patterns like '{file_pattern if 'file_pattern' in locals() else 'N/A'}'.") # Enhanced warning
            print_manager.time_output("import_data_function", "no files found")
            end_step(step_key, step_start, {"error": "no files found"})
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
                    # Check for time variables in both zVariables and rVariables (WIND compatibility)
                    all_vars = cdf_file.cdf_info().zVariables + cdf_file.cdf_info().rVariables
                    time_vars = [var for var in all_vars if 'epoch' in var.lower() or var.upper() == 'TIME']
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
                    first_time_data_raw = cdf_file.varget(time_var, startrec=0, endrec=0)      
                    last_time_data_raw = cdf_file.varget(time_var, startrec=n_records-1, endrec=n_records-1)
                    
                    if first_time_data_raw is None or last_time_data_raw is None:
                        print_manager.warning(f"Could not read time boundaries for {os.path.basename(file_path)} - skipping")
                        continue
                    
                    # Ensure these are single values if varget returns array for single rec
                    file_first_raw = first_time_data_raw[0] if hasattr(first_time_data_raw, '__getitem__') and len(first_time_data_raw) > 0 else first_time_data_raw
                    file_last_raw = last_time_data_raw[0] if hasattr(last_time_data_raw, '__getitem__') and len(last_time_data_raw) > 0 else last_time_data_raw

                    # Check epoch type and convert to TT2000 if needed (WIND compatibility)
                    epoch_var_info = cdf_file.varinq(time_var)
                    epoch_type = epoch_var_info.Data_Type_Description
                    print_manager.debug(f"  Epoch type: {epoch_type}")
                    
                    if 'CDF_DOUBLE' in epoch_type or 'CDF_REAL8' in epoch_type:
                        # Handle Unix timestamp in seconds (double)
                        print_manager.debug("  Converting CDF_DOUBLE (Unix time) to TT2000 for boundary check")
                        boundary_unix_epochs = np.array([file_first_raw, file_last_raw])
                        boundary_tt2000 = convert_unix_to_tt2000_vectorized(boundary_unix_epochs)
                        file_first_tt_val = boundary_tt2000[0]
                        file_last_tt_val = boundary_tt2000[1]
                    elif 'CDF_EPOCH' in epoch_type and 'TT2000' not in epoch_type:
                        # WIND uses CDF_EPOCH format - convert to TT2000 using vectorized method
                        print_manager.debug("  Converting CDF_EPOCH to TT2000 for WIND compatibility (boundary check)")
                        # Convert boundary values using vectorized function
                        boundary_epochs = np.array([file_first_raw, file_last_raw])
                        boundary_tt2000 = convert_cdf_epoch_to_tt2000_vectorized(boundary_epochs)
                        file_first_tt_val = boundary_tt2000[0]
                        file_last_tt_val = boundary_tt2000[1]
                    else:
                        # Already TT2000 format (PSP case)
                        file_first_tt_val = file_first_raw
                        file_last_tt_val = file_last_raw

                    # Convert to datetime for display
                    try:
                        file_actual_start_dt_val = cdflib.cdfepoch.to_datetime(file_first_tt_val)[0] 
                        file_actual_end_dt_val = cdflib.cdfepoch.to_datetime(file_last_tt_val)[0]
                        print_manager.debug(f"  File actual TT2000 range: {file_first_tt_val} ({file_actual_start_dt_val}) to {file_last_tt_val} ({file_actual_end_dt_val})")
                    except Exception as e_conv_dt:
                        print_manager.warning(f"Could not convert file boundary TT2000 values to datetime for logging: {e_conv_dt}")
                        print_manager.debug(f"  Raw TT2000 vals were: {file_first_tt_val}, {file_last_tt_val}")


                    # Compare TT2000 times directly
                    file_ends_before_req_starts = file_last_tt_val < start_tt2000
                    file_starts_after_req_ends = file_first_tt_val > end_tt2000
                    print_manager.debug(f"    Comparison: File ends before request starts? {file_ends_before_req_starts} (FileEnd: {file_last_tt_val} < ReqStart: {start_tt2000})")
                    print_manager.debug(f"    Comparison: File starts after request ends? {file_starts_after_req_ends} (FileStart: {file_first_tt_val} > ReqEnd: {end_tt2000})")

                    if file_ends_before_req_starts or file_starts_after_req_ends:
                        print_manager.debug("File outside requested time range - skipping")
                        continue

                    # Read full time data ONLY if file potentially overlaps
                    print_manager.debug("Reading full time data array...")
                    time_data_raw = cdf_file.varget(time_var) # Get raw values, not epoch=True
                    if time_data_raw is None or len(time_data_raw) == 0:
                        print_manager.warning(f"Time data is empty in {os.path.basename(file_path)} - skipping")
                        continue
                    print_manager.debug(f"Read {len(time_data_raw)} time points")

                    # Convert time data to TT2000 if needed (WIND compatibility)
                    if 'CDF_DOUBLE' in epoch_type or 'CDF_REAL8' in epoch_type:
                        print_manager.debug("  Converting full CDF_DOUBLE (Unix time) array to TT2000")
                        time_data = convert_unix_to_tt2000_vectorized(time_data_raw)
                        print_manager.debug(f"  Unix time conversion completed: {len(time_data)} time points converted to TT2000")
                    elif 'CDF_EPOCH' in epoch_type and 'TT2000' not in epoch_type:
                        print_manager.debug("  Converting full time array from CDF_EPOCH to TT2000 using vectorized method")
                        # Convert CDF_EPOCH array to TT2000 using optimized vectorized function
                        time_data = convert_cdf_epoch_to_tt2000_vectorized(time_data_raw)
                        print_manager.debug(f"  Vectorized conversion completed: {len(time_data)} time points converted to TT2000")
                    else:
                        # Already TT2000 format
                        time_data = time_data_raw

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
            end_step(step_key, step_start, {"error": "no data found"})
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
        
        # Format the original trange again for the completion message
        formatted_trange_list_end = [format_datetime_for_log(t) for t in trange] 
        print_manager.status(f"☑️ - CDF Data import complete for {data_type} range {formatted_trange_list_end}.\n")
        
        output_range = [cdflib.epochs.CDFepoch.to_datetime(times_sorted[0]),
                        cdflib.epochs.CDFepoch.to_datetime(times_sorted[-1])]
        # Format output range for time_output log
        formatted_output_range = [format_datetime_for_log(t) for t in output_range]
        print_manager.time_output("import_data_function", formatted_output_range)

        # === DIAGNOSTIC PRINT BEFORE RETURN ===
        print_manager.debug(f"*** IMPORT_DATA_DEBUG (CDF Path) for data_type '{data_type}' (originally requested: '{data_type_requested_at_start}') ***")
        if data_object is not None:
            print_manager.datacubby(f"    data_object ID: {id(data_object)}")
            if hasattr(data_object, 'times') and data_object.times is not None:
                print_manager.datacubby(f"    DataObject.times length: {len(data_object.times)}, dtype: {data_object.times.dtype if hasattr(data_object.times, 'dtype') else type(data_object.times)}")
            else:
                print_manager.datacubby(f"    DataObject.times is None or missing.")
            
            if hasattr(data_object, 'data') and isinstance(data_object.data, dict):
                print_manager.datacubby(f"    data_object.data ID: {id(data_object.data)}")
                print_manager.datacubby(f"    DataObject.data keys: {list(data_object.data.keys())}")
                if data_type_requested_at_start == 'mag_RTN_4sa': # Adjusted for current test
                    expected_key = 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc'
                    if expected_key in data_object.data:
                        val = data_object.data[expected_key]
                        val_type = type(val)
                        val_shape = val.shape if hasattr(val, 'shape') else 'N/A'
                        val_len = len(val) if hasattr(val, '__len__') else 'N/A'
                        print_manager.datacubby(f"        '{expected_key}' is PRESENT. Type: {val_type}, Shape: {val_shape}, Len: {val_len}")
                    else:
                        print_manager.datacubby(f"        '{expected_key}' is MISSING from data_object.data for {data_type_requested_at_start} request.") # Adjusted
            else:
                print_manager.datacubby(f"    DataObject.data is None or not a dict.")
        else:
            print_manager.datacubby(f"    data_object is None at final diagnostic print (CDF Path).")
        # === END DIAGNOSTIC PRINT ===

        data_obj_to_return = data_object # data_object is used in CDF path
        end_step(step_key, step_start, {"data_object": data_obj_to_return})
        return data_obj_to_return

    # Fallback for any paths that might have been missed, or error returns
    # Ensure data_obj_to_return is what's being returned if it's not already handled above
    if data_obj_to_return is None and 'data_object' in locals(): # if data_object was the intended return but not assigned to data_obj_to_return
        data_obj_to_return = data_object
    elif data_obj_to_return is None and 'data_obj' in locals(): # if data_obj was the intended return
        data_obj_to_return = data_obj

    # One final diagnostic print if not already handled by specific paths
    # This is a safeguard, ideally the prints are closer to the actual return statements of each path.
    # However, given the complexity, this ensures we see something.
    # This specific print block might be redundant if all return paths are covered above.

    # If data_obj_to_return is still None here, it means an error path was taken that didn't assign to it.
    # The function would return None in those cases based on existing logic (e.g., error in time parsing, no files found etc.)
    end_step(step_key, step_start, {"data_obj_to_return": data_obj_to_return})
    return data_obj_to_return # This will be None if an error path already returned None