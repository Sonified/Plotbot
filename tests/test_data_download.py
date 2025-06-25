#tests/test_data_download.py
# To run ALL tests in this file from the project root directory and see verbose print output:
# conda run -n plotbot_env python -m pytest tests/test_data_download.py -vv -s
#
# To run tests for a SPECIFIC DATA TYPE (parameterization) and see verbose print output:
# Use the '-k' flag followed by the unique 'test_id_suffix' from the @pytest.mark.parametrize decorator.
# For example, to test only 'mag_RTN_4sa' (using its corrected id 'mag_RTN_4sa_br'):
# conda run -n plotbot_env python -m pytest tests/test_data_download.py -k "mag_RTN_4sa_br" -vv -s
#
# Other examples of test_id_suffix values:
#   "mag_SC_4sa_bx"
#   "epad_strahl"
#   "proton_anisotropy"
#
# The '-s' flag ensures that print statements from the tests are shown in the console.
# The '-vv' flag provides very verbose output.

"""
Tests for data download functionality.

To run all tests in this file and see print output:
  (Activate conda environment: conda activate plotbot_env)
  python -m pytest -s tests/test_data_download.py -v

To run a specific parameterized test (e.g., mag_RTN_br) and see print output:
  python -m pytest -s tests/test_data_download.py -k "mag_RTN_br" -v
"""
import pytest
import os
import shutil
import glob
from datetime import datetime, timezone, timedelta # Added for new function
from dateutil.parser import parse # Added for new function

# Add the parent directory to sys.path to allow imports from plotbot
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import mag_rtn_4sa, config, mag_sc_4sa, epad, proton # Updated imports
from plotbot.plotbot_main import plotbot
from plotbot.print_manager import print_manager
from plotbot.data_classes.data_types import data_types as psp_data_types_config # Added for new function
from plotbot.time_utils import daterange # Added for new function
from plotbot.data_download_helpers import case_insensitive_file_search
from plotbot.data_import import find_local_csvs # For local_csv deletion

# Define the base path for mag_rtn_4sa data - This will be superseded by the new function
# MAG_RTN_4SA_DATA_PATH = os.path.join('psp_data', 'fields', 'l2', 'mag_rtn_4_per_cycle')
# MAG_RTN_4SA_ABSOLUTE_PATH = os.path.abspath(MAG_RTN_4SA_DATA_PATH)

def clear_downloaded_data(trange_str_list, data_type_key):
    """
    Clears downloaded data files for a given data_type and time range.
    Uses psp_data_types.py for configuration.
    """
    print_manager.test(f"Attempting to clear downloaded data for type '{data_type_key}' in range {trange_str_list}")

    if data_type_key not in psp_data_types_config:
        print_manager.warning(f"Data type '{data_type_key}' not found in psp_data_types_config. Cannot clear.")
        return

    config_entry = psp_data_types_config[data_type_key]
    local_path_template = config_entry.get('local_path')
    data_level = config_entry.get('data_level')
    file_time_format = config_entry.get('file_time_format')
    file_pattern_import = config_entry.get('file_pattern_import')
    data_sources = config_entry.get('data_sources', []) # For all source types

    if not local_path_template:
        print_manager.warning(f"No 'local_path' defined for data type '{data_type_key}'. Cannot clear.")
        return

    try:
        start_dt = parse(trange_str_list[0]).replace(tzinfo=timezone.utc)
        end_dt = parse(trange_str_list[1]).replace(tzinfo=timezone.utc)
    except Exception as e:
        print_manager.error(f"Error parsing time range {trange_str_list} for cleanup: {e}")
        return

    files_to_delete = []
    dirs_to_check_for_emptiness = set() # To potentially remove empty year dirs

    base_data_dir = local_path_template.format(data_level=data_level) if data_level and "{data_level}" in local_path_template else local_path_template
    absolute_base_data_dir = os.path.abspath(base_data_dir)

    if 'local_csv' in data_sources:
        print_manager.test(f"Clearing local_csv type: {data_type_key} from base path: {absolute_base_data_dir}")
        # For local_csv, patterns might be a list or string
        patterns = file_pattern_import if isinstance(file_pattern_import, list) else [file_pattern_import]
        for single_date in daterange(start_dt, end_dt):
            date_str = single_date.strftime('%Y%m%d') # find_local_csvs uses YYYYMMDD
            # find_local_csvs searches recursively from base_path
            found_csvs = find_local_csvs(absolute_base_data_dir, patterns, date_str)
            files_to_delete.extend(found_csvs)
            # For CSVs, the year directory structure is less fixed, so we don't typically add to dirs_to_check_for_emptiness
            # unless find_local_csvs was modified to return the containing directory of each file.
            # For now, we assume local_csv files might be in various subdirs of the base_path.
    else: # Assuming CDF files downloaded from a server
        print_manager.test(f"Clearing CDF type: {data_type_key} from base path: {absolute_base_data_dir}")
        for single_date in daterange(start_dt, end_dt):
            year_str = str(single_date.year)
            date_str_yyyymmdd = single_date.strftime('%Y%m%d')
            
            year_specific_dir = os.path.join(absolute_base_data_dir, year_str)
            dirs_to_check_for_emptiness.add(year_specific_dir)

            if not os.path.isdir(year_specific_dir):
                # print_manager.debug(f"Directory does not exist, nothing to delete for {date_str_yyyymmdd}: {year_specific_dir}")
                continue

            if file_time_format == 'daily':
                # Ensure file_pattern_import is a string before .format
                if not isinstance(file_pattern_import, str):
                    print_manager.warning(f"file_pattern_import for {data_type_key} is not a string. Skipping daily cleanup for {date_str_yyyymmdd}.")
                    continue
                pattern = file_pattern_import.format(data_level=data_level, date_str=date_str_yyyymmdd)
                # Use case_insensitive_file_search which handles partial pattern matching (e.g. _v*.cdf)
                found_for_day = case_insensitive_file_search(year_specific_dir, pattern)
                files_to_delete.extend(found_for_day)
            elif file_time_format == '6-hour':
                # Ensure file_pattern_import is a string before .format
                if not isinstance(file_pattern_import, str):
                    print_manager.warning(f"file_pattern_import for {data_type_key} is not a string. Skipping 6-hour cleanup for {date_str_yyyymmdd}.")
                    continue
                for hour_block in range(4):
                    hour_str = f"{hour_block * 6:02d}"
                    date_hour_str = f"{date_str_yyyymmdd}{hour_str}"
                    pattern = file_pattern_import.format(data_level=data_level, date_hour_str=date_hour_str)
                    found_for_block = case_insensitive_file_search(year_specific_dir, pattern)
                    files_to_delete.extend(found_for_block)
            else:
                print_manager.warning(f"Unknown file_time_format '{file_time_format}' for {data_type_key}")

    if not files_to_delete:
        print_manager.test("No files found to delete for the given criteria.")
    else:
        print_manager.test(f"Found {len(files_to_delete)} file(s) to delete:")
        for f_path in files_to_delete:
            try:
                os.remove(f_path)
                print_manager.test(f"  Deleted: {f_path}")
            except OSError as e:
                print_manager.warning(f"  Error deleting file {f_path}: {e}")

    # Attempt to remove empty year directories (only for CDF types currently)
    if 'local_csv' not in data_sources:
        for dir_path in sorted(list(dirs_to_check_for_emptiness), reverse=True): # Process deeper dirs first
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path) # shutil.rmtree is for non-empty, os.rmdir for empty
                    print_manager.test(f"Removed empty directory: {dir_path}")
                except OSError as e:
                    print_manager.warning(f"Error removing empty directory {dir_path}: {e}")
            elif os.path.exists(dir_path):
                print_manager.debug(f"Directory not empty, not removing: {dir_path}")

def verify_downloaded_files_exist(trange_str_list, data_type_key):
    """
    Verifies if expected downloaded data files exist locally for a given data_type and time range.
    """
    print_manager.test(f"Verifying existence of downloaded data for type '{data_type_key}' in range {trange_str_list}")

    if data_type_key not in psp_data_types_config:
        print_manager.warning(f"Data type '{data_type_key}' not found in psp_data_types_config. Cannot verify files.")
        return False

    config_entry = psp_data_types_config[data_type_key]
    local_path_template = config_entry.get('local_path')
    data_level = config_entry.get('data_level')
    file_time_format = config_entry.get('file_time_format')
    file_pattern_import = config_entry.get('file_pattern_import')
    data_sources = config_entry.get('data_sources', [])

    if not local_path_template:
        print_manager.warning(f"No 'local_path' defined for data type '{data_type_key}'. Cannot verify files.")
        return False

    try:
        start_dt = parse(trange_str_list[0]).replace(tzinfo=timezone.utc)
        end_dt = parse(trange_str_list[1]).replace(tzinfo=timezone.utc)
    except Exception as e:
        print_manager.error(f"Error parsing time range {trange_str_list} for verification: {e}")
        return False

    found_any_files = False

    base_data_dir = local_path_template.format(data_level=data_level) if data_level and "{data_level}" in local_path_template else local_path_template
    absolute_base_data_dir = os.path.abspath(base_data_dir)

    if 'local_csv' in data_sources:
        print_manager.test(f"Verifying local_csv type: {data_type_key} from base path: {absolute_base_data_dir}")
        patterns = file_pattern_import if isinstance(file_pattern_import, list) else [file_pattern_import]
        for single_date in daterange(start_dt, end_dt):
            date_str = single_date.strftime('%Y%m%d')
            # find_local_csvs searches recursively
            found_csvs = find_local_csvs(absolute_base_data_dir, patterns, date_str)
            if found_csvs:
                print_manager.test(f"  Found {len(found_csvs)} CSV file(s) for {date_str}, e.g., {os.path.basename(found_csvs[0])}")
                found_any_files = True
                break 
        if not found_any_files:
             print_manager.test(f"  No CSV files found matching criteria for {data_type_key} in range {trange_str_list}.")
    else:  # Assuming CDF files
        print_manager.test(f"Verifying CDF type: {data_type_key} from base path: {absolute_base_data_dir}")
        for single_date in daterange(start_dt, end_dt):
            if found_any_files:  # Optimization: if already found a file, no need to check further dates
                break

            year_str = str(single_date.year)
            date_str_yyyymmdd = single_date.strftime('%Y%m%d')
            year_specific_dir = os.path.join(absolute_base_data_dir, year_str)

            if not os.path.isdir(year_specific_dir):
                # print_manager.debug(f"Directory does not exist for {date_str_yyyymmdd}: {year_specific_dir}")
                continue

            current_day_found_files = []
            if file_time_format == 'daily':
                if isinstance(file_pattern_import, str):
                    pattern = file_pattern_import.format(data_level=data_level, date_str=date_str_yyyymmdd)
                    current_day_found_files = case_insensitive_file_search(year_specific_dir, pattern)
            elif file_time_format == '6-hour':
                if isinstance(file_pattern_import, str):
                    for hour_block in range(4):
                        hour_str = f"{hour_block * 6:02d}"
                        date_hour_str = f"{date_str_yyyymmdd}{hour_str}"
                        pattern = file_pattern_import.format(data_level=data_level, date_hour_str=date_hour_str)
                        found_for_block = case_insensitive_file_search(year_specific_dir, pattern)
                        if found_for_block:
                            current_day_found_files.extend(found_for_block)
                            break # Found for this day, can stop checking other blocks for this day
            
            if current_day_found_files:
                print_manager.test(f"  Found {len(current_day_found_files)} file(s) for {date_str_yyyymmdd}, e.g., {os.path.basename(current_day_found_files[0])}")
                found_any_files = True
                # Break here because we only need one file in the whole trange to confirm download occurred for the type
                break 
        
        if not found_any_files: # Log after checking all dates if no CDFs were found
            print_manager.test(f"  No CDF files found matching criteria for {data_type_key} in range {trange_str_list}.")

    if found_any_files:
        print_manager.test(f"  File verification PASSED for {data_type_key}.")
    else:
        print_manager.test(f"  File verification FAILED for {data_type_key}: No files found.")
    return found_any_files

@pytest.mark.mission("Data Download Test")
@pytest.mark.parametrize(
    "test_id_suffix, data_type_key, data_object_module, variable_attr_name, plot_manager_data_attr_name",
    [
        ("mag_RTN_4sa_br", "mag_RTN_4sa", mag_rtn_4sa, "br", "data"),
        ("mag_SC_4sa_bx", "mag_SC_4sa", mag_sc_4sa, "bx", "data"),
        ("epad_strahl", "spe_sf0_pad", epad, "strahl", "data"),
        ("proton_anisotropy", "spi_sf00_l3_mom", proton, "anisotropy", "data"),
    ]
)
def test_data_download_from_berkeley(test_id_suffix, data_type_key, data_object_module, variable_attr_name, plot_manager_data_attr_name):
    """
    Tests the download functionality for various data types from the Berkeley server.
    1. Cleans up any existing local data for the specified data_type_key and trange.
    2. Sets the data server to 'berkeley'.
    3. Attempts to plot the specified variable, which should trigger a download.
    4. Asserts that data has been loaded into the plot_manager's specified data attribute.
    5. Asserts that corresponding local files were created.
    """
    
    # Set print_manager verbosity for detailed test output
    print_manager.show_status = True
    print_manager.show_debug = True
    print_manager.show_processing = True
    print_manager.show_datacubby = True
    print_manager.show_test = True # Ensure test-specific prints are shown
    
    print_manager.test(f"\n========================= TEST START: {test_id_suffix} =========================")
    print_manager.test(f"Testing data_type_key: {data_type_key}, variable: {data_object_module.__class__.__name__}.{variable_attr_name}")
    print_manager.test("Ensures data is downloaded correctly from Berkeley server.")
    print_manager.test("================================================================================\n")

    # Define a time range that is likely to have data.
    trange_strings = ['2023-09-27/00:00:00.000', '2023-09-27/23:59:59.999']
    print_manager.test(f"Using default trange for {data_type_key}: {trange_strings}")


    # Phase 1: Cleanup using the new function
    print_manager.test(f"--- Phase 1: Cleaning up existing data for {data_type_key} ---")
    clear_downloaded_data(trange_strings, data_type_key)
      
    # Phase 2: Configure and Download
    print_manager.test(f"\n--- Phase 2: Configuring server and attempting download for {data_type_key} ---")
    original_server = config.data_server
    config.data_server = 'berkeley'
    print_manager.test(f"Set config.data_server to: {config.data_server}")

    variable_to_plot = getattr(data_object_module, variable_attr_name)

    try:
        print_manager.test(f"Calling plotbot to trigger download for {data_object_module.__class__.__name__}.{variable_attr_name}...")
        plotbot(trange_strings, variable_to_plot, 1)
        print_manager.test("Plotbot call completed.")
    except Exception as e:
        print_manager.test(f"ERROR during plotbot call for {data_type_key}: {e}")
        config.data_server = original_server # Restore server setting on error
        pytest.fail(f"Test failed during plotbot call for {data_type_key} ({test_id_suffix}): {e}")
    finally:
        config.data_server = original_server # Ensure server setting is always restored
        print_manager.test(f"Restored config.data_server to: {config.data_server}")

    # Phase 3: Verification
    print_manager.test(f"\n--- Phase 3: Verifying data download for {data_type_key} ---")
    # Removed the old data_loaded_correctly and num_points logic.
    # The success of the plotbot() call in Phase 2 implies plotting was successful.
    # Now, we just need to verify that files were actually downloaded.

    files_were_downloaded = verify_downloaded_files_exist(trange_strings, data_type_key)
    assert files_were_downloaded, f"File download verification FAILED for {data_type_key}. Expected files were not found locally after plotbot call. Check logs for details."
    
    print_manager.test(f"SUCCESS: {data_type_key} data download test ({test_id_suffix}) passed. Plotbot call completed and files were found.")

# Example of how to run this test (from the Plotbot root directory):
# conda run -n plotbot_env python -m pytest tests/test_data_download.py -v -s
# To run a specific parameter set:
# conda run -n plotbot_env python -m pytest tests/test_data_download.py -k "test_id_suffix_name" -v -s
# e.g. conda run -n plotbot_env python -m pytest tests/test_data_download.py -k "mag_RTN_br" -v -s

