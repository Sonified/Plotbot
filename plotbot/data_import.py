import cdflib
import numpy as np
import os
import re
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from .print_manager import print_manager
from .time_utils import daterange
from .data_tracker import global_tracker
from .psp_data_types import data_types


def import_data_function(trange, data_type):
    """Import data function that reads only data within the specified time range."""
    
    print_manager.debug('Import data function called')
    print_manager.debug(f"Input trange: {trange}")
    print_manager.variable_testing(f"import_data_function called for data_type: {data_type}")
    
    # Validate data type
    if data_type not in data_types:
        print_manager.variable_testing(f"Error: {data_type} not found in psp_data_types")
        return None
    
    print_manager.variable_testing(f"Getting configuration for {data_type}")
    config = data_types[data_type]
    
    # Parse times using flexible parser and ensure UTC timezone
    try:
        start_time = parse(trange[0])
        end_time = parse(trange[1])
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        return None
    
    # Format dates for TT2000 conversion
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
    
    print_manager.debug(f"\nImporting data for UTC time range: {trange}")

    #====================================================================
    # INITIALIZATION AND CONFIGURATION 
    #====================================================================
    print_manager.debug(f"\n=== Starting import for {data_type} ===")
    variables = config.get('data_vars', [])     # Get list of variables to extract, empty list if none specified

    #====================================================================
    # FILE SEARCH AND COLLECTION
    #====================================================================
    found_files = []       # Initialize empty list to store found data files
    
    for single_date in daterange(start_time, end_time):  # Iterate through each date in the range
        year = single_date.year   # Extract year from current date
        date_str = single_date.strftime('%Y%m%d')  # Format date as YYYYMMDD string
        
        local_dir = os.path.join(config['local_path'].format(data_level=config['data_level']), str(year))  # Construct path to year directory
        
        # Handle different file timing formats (6-hour vs daily)
        if config['file_time_format'] == '6-hour':          # Check if files are in 6-hour format
            for hour in range(0, 24, 6):                    # Loop through hours in 6-hour increments
                hour_str = f"{hour:02d}"                    # Format hour as 2-digit string (e.g. '00', '06')
                date_hour_str = date_str + hour_str         # Combine date and hour strings
                file_pattern = config['file_pattern_import'].format(  # Create file pattern using config template
                    data_level=config['data_level'],
                    date_str=date_str,
                    date_hour_str=date_hour_str
                )

                if os.path.exists(local_dir): # Case insensitive file search
                    pattern = file_pattern.replace('*', '.*')  # Convert glob pattern to regex pattern
                    regex = re.compile(pattern, re.IGNORECASE)
                    matching_files = [os.path.join(local_dir, f) for f in os.listdir(local_dir) 
                                    if regex.match(f)]
                    if matching_files:                          # If matching files found
                        found_files.extend(matching_files)      # Add them to list of found files
                else:
                    print("Directory does not exist!")
        # Daily files
        elif config['file_time_format'] == 'daily':         # Check if files are in daily format
            file_pattern = config['file_pattern_import'].format(  # Create file pattern using config template
                data_level=config['data_level'],
                date_str=date_str
            )

            if os.path.exists(local_dir): # Case insensitive file search
                pattern = file_pattern.replace('*', '.*')  # Convert glob pattern to regex pattern
                regex = re.compile(pattern, re.IGNORECASE)
                matching_files = [os.path.join(local_dir, f) for f in os.listdir(local_dir) 
                                if regex.match(f)]
                if matching_files:                             # If matching files found
                    found_files.extend(matching_files)         # Add them to list of found files
            else:
                print("Directory does not exist!")
    
    if not found_files:
        print("No data files found in the specified time range.")
        return None
    #====================================================================
    # DATA EXTRACTION AND PROCESSING
    #====================================================================
    times_list = []                              # List to store time arrays from each file
    data_dict = {var: [] for var in variables}   # Dictionary to store data arrays for each variable
    epoch_cache = {}                             # Cache to store time data to avoid re-reading
    
    for file_path in sorted(found_files):        # Process each file in chronological order
        print_manager.debug(f"\nProcessing file: {file_path}")
        try:  # Attempt to open and process the CDF file
            with cdflib.CDF(file_path) as cdf_file:  # Open CDF file with context manager
                print_manager.debug("Successfully opened CDF file")
                
                # Locate and verify time variable
                time_vars = [var for var in cdf_file.cdf_info().zVariables if 'epoch' in var.lower()]  # Find time variable name
                if not time_vars:        # Skip file if no time variable found
                    print_manager.debug("No time variable found in file - skipping")
                    continue
                time_var = time_vars[0]  # Use first found time variable
                print_manager.debug(f"Using time variable: {time_var}")
                
                # Get file metadata
                var_info = cdf_file.varinq(time_var)   # Get variable info
                n_records = var_info.Last_Rec + 1      # Calculate number of records
                print_manager.debug(f"File contains {n_records} records")
                
                # Check file time boundaries
                first_time_data = cdf_file.varget(time_var, startrec=0, endrec=0)           # Get first time point
                last_time_data = cdf_file.varget(time_var, startrec=n_records-1, endrec=n_records-1)  # Get last time point
                print_manager.debug(f"File time range: {cdflib.epochs.CDFepoch.to_datetime(first_time_data[0])} to {cdflib.epochs.CDFepoch.to_datetime(last_time_data[0])}")
                print_manager.debug(f"Requested time range: {cdflib.epochs.CDFepoch.to_datetime(start_tt2000)} to {cdflib.epochs.CDFepoch.to_datetime(end_tt2000)}")
                
                # Compare TT2000 times directly, using array indexing to get scalar values
                if last_time_data[0] < start_tt2000 or first_time_data[0] > end_tt2000:
                    print_manager.debug(f"File outside requested time range:")
                    print_manager.debug(f"File start vs requested start: {first_time_data[0]} vs {start_tt2000}")
                    print_manager.debug(f"File end vs requested end: {last_time_data[0]} vs {end_tt2000}")
                    print_manager.debug("Skipping this file")
                    continue

                # Read time data
                print_manager.debug("Reading full time data array...")
                time_data = cdf_file.varget(time_var, epoch=True)
                print_manager.debug(f"Read {len(time_data)} time points")
                print_manager.debug(f"Time range in file: {cdflib.epochs.CDFepoch.to_datetime(time_data[0])} to {cdflib.epochs.CDFepoch.to_datetime(time_data[-1])}")

                # Find relevant data indices
                start_idx = np.searchsorted(time_data, start_tt2000, side='left')
                end_idx = np.searchsorted(time_data, end_tt2000, side='right')
                print_manager.debug(f"Time range requested: {start_time} to {end_time}")
                print_manager.debug(f"Time indices: {start_idx} to {end_idx}")
                if start_idx < len(time_data):
                    print_manager.debug(f"Start time selected: {cdflib.epochs.CDFepoch.to_datetime(time_data[start_idx])}")
                if end_idx > 0 and end_idx <= len(time_data):
                    print_manager.debug(f"End time selected: {cdflib.epochs.CDFepoch.to_datetime(time_data[end_idx-1])}")
                else:
                    print_manager.debug(f"End index {end_idx} out of bounds for array length {len(time_data)}")

                if start_idx >= end_idx:
                    print_manager.debug(f"Invalid index range: start_idx={start_idx}, end_idx={end_idx}")
                    print_manager.status("No data in time range for this file after indexing")
                    continue

                # Extract time slice we need - keep as TT2000
                time_slice = time_data[start_idx:end_idx]
                print_manager.debug(f"Extracted time slice range: {cdflib.epochs.CDFepoch.to_datetime(time_slice[0])} to {cdflib.epochs.CDFepoch.to_datetime(time_slice[-1])}")
                times_list.append(time_slice)
                print_manager.debug(f"Extracted {len(time_slice)} time points within requested range")
                for var_name in variables:                        # Process each requested variable
                    try:
                        print_manager.debug(f"\nReading variable: {var_name}")
                        var_data = cdf_file.varget(var_name, startrec=start_idx, endrec=end_idx-1)
                        print_manager.debug(f"Raw data shape: {var_data.shape}")
                        print_manager.debug(f"Raw data type: {var_data.dtype}")
                        print_manager.debug(f"Sample of raw data: {var_data[0] if len(var_data) > 0 else 'Empty'}")
                        
                        # Debug fill values
                        var_atts = cdf_file.varattsget(var_name)
                        print_manager.debug(f"Variable attributes: {var_atts}")
                        if "FILLVAL" in var_atts:
                            fill_val = var_atts["FILLVAL"]
                            print_manager.debug(f"Fill value: {fill_val}")
                            fill_count = np.sum(var_data == fill_val)
                            print_manager.debug(f"Number of fill values: {fill_count}")
                            
                            # Before fill value replacement
                            print_manager.debug("Data statistics before fill value replacement:")
                            print_manager.debug(f"Min: {np.min(var_data)}")
                            print_manager.debug(f"Max: {np.max(var_data)}")
                            print_manager.debug(f"Unique values: {np.unique(var_data)[:10]}...")
                            
                            # Replace fill values
                            var_data = np.where(var_data == fill_val, np.nan, var_data)
                            
                            # After fill value replacement
                            print_manager.debug("\nData statistics after fill value replacement:")
                            if not np.all(np.isnan(var_data)):
                                print_manager.debug(f"Min: {np.nanmin(var_data)}")
                                print_manager.debug(f"Max: {np.nanmax(var_data)}")
                                print_manager.debug(f"Unique values: {np.unique(var_data)[:10]}...")
                            else:
                                print_manager.debug("All values are NaN - skipping min/max calculations")
                            
                        data_dict[var_name].append(var_data)
                        print_manager.debug(f"Successfully stored data for {var_name}")
                        
                    except Exception as e:
                        print_manager.debug(f"Error processing {var_name}: {str(e)}")
                        print_manager.debug(f"Exception type: {type(e)}")
                        import traceback
                        print_manager.debug(traceback.format_exc())
                        
        except Exception as e:                                   # Handle file-level errors
            print(f"Error processing {file_path}: {e}")  # Print error message for failed file
            continue
    
    #====================================================================
    # DATA CONSOLIDATION AND CLEANUP
    #====================================================================
    if not times_list:  # Check if any data was collected
        print("No data found in the specified time range after processing files.")
        return None
        
    times = np.concatenate(times_list)
    concatenated_data = {}
    
    print_manager.debug("\nPost-concatenation debugging:")
    for var_name in variables:
        data_list = data_dict[var_name]
        if data_list:
            concatenated_data[var_name] = np.concatenate(data_list)
            data = concatenated_data[var_name]
            print_manager.debug(f"\nVariable: {var_name}")
            print_manager.debug("Shape: {data.shape}")
            print_manager.debug(f"NaN count: {np.isnan(data).sum()}")
            print_manager.debug(f"Non-NaN value range: [{np.nanmin(data)}, {np.nanmax(data)}]")
        else:
            concatenated_data[var_name] = None  # Store None if no data
    
    print_manager.debug(f"\nTotal data points after concatenation: {len(times)}")
    
    sort_indices = np.argsort(times)    # Get indices for chronological sorting
    times = times[sort_indices]         # Sort times array
    for var_name in variables:          # Sort each variable's data
        if concatenated_data[var_name] is not None:  # Check if data exists for this variable before sorting
            concatenated_data[var_name] = concatenated_data[var_name][sort_indices]  # Sort data array using same indices as time array
    
    DataObject = namedtuple('DataObject', ['times', 'data'])  # Create return object structure
    
    # After successful import
    global_tracker.update_imported_range(trange, data_type)
    # trange = np.around(trange, decimals=0)  # Truncate the seconds to integer values
    print_manager.status(f"✅ - Data import complete for range {trange}.")
    
    return DataObject(times=times, data=concatenated_data)  # Return packaged data