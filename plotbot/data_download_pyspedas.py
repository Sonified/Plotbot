"""Module for downloading PSP data using pyspedas from SPDF.

This module will contain the logic to interact with pyspedas for downloading
files based on Plotbot data type keys and time ranges, utilizing the 
no_update=[True, False] strategy for offline reliability.
"""

import pyspedas
import os
import glob # Added
import plotbot # Added for config access
from datetime import datetime, timedelta # Added for date iteration
import cdflib
import numpy as np
from dateutil.parser import parse

from .print_manager import print_manager
from .data_classes.psp_data_types import data_types # To get pyspedas datatype mapping
from .time_utils import daterange
# Add other necessary imports (time, etc.) as needed

# Define the mapping from Plotbot keys to pyspedas specifics
# (Borrowed from tests/test_pyspedas_download.py - may need refinement)
# TODO: Formalize this mapping, potentially move to psp_data_types.py?
PYSPEDAS_MAP = {
    'mag_RTN_4sa': {
        'pyspedas_datatype': 'mag_rtn_4_sa_per_cyc',
        'pyspedas_func': pyspedas.psp.fields,
        'kwargs': {'level': 'l2', 'get_support_data': True}
    },
    'mag_SC_4sa': {
        'pyspedas_datatype': 'mag_sc_4_sa_per_cyc',
        'pyspedas_func': pyspedas.psp.fields,
        'kwargs': {'level': 'l2', 'get_support_data': True}
    },
    'spi_sf00_l3_mom': {
        'pyspedas_datatype': 'spi_sf00_l3_mom',
        'pyspedas_func': pyspedas.psp.spi,
        'kwargs': {'level': 'l3'}
    },
    'spe_sf0_pad': {
        'pyspedas_datatype': 'spe_sf0_pad',
        'pyspedas_func': pyspedas.psp.spe,
        'kwargs': {'level': 'l3', 'get_support_data': True}
    },
    # Add mappings for other data types as needed (e.g., high-res versions)
}

def _get_dates_in_range(start_str, end_str):
    """Helper to get list of YYYYMMDD strings for a date range."""
    dates = []
    try:
        # Attempt to parse common date formats
        start_date = None
        end_date = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                if start_date is None:
                    start_date = datetime.strptime(start_str.split(' ')[0], fmt.split(' ')[0])
                if end_date is None:
                    end_date = datetime.strptime(end_str.split(' ')[0], fmt.split(' ')[0])
                if start_date and end_date: # Stop if both parsed
                    break 
            except ValueError:
                continue # Try next format
        
        if start_date is None or end_date is None:
            raise ValueError("Could not parse start or end date string")

        delta = timedelta(days=1)
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y%m%d'))
            current_date += delta
    except Exception as e:
        print_manager.warning(f"Could not parse dates from trange for rename check: {start_str}, {end_str}. Error: {e}")
    return dates

def download_spdf_data(trange, plotbot_key):
    """Attempts to download data using pyspedas from SPDF.
    
    Uses the no_update=[True, False] strategy for offline reliability.
    Checks local files first, then attempts download if not found.

    Args:
        trange (list): Time range ['.start', 'end']
        plotbot_key (str): The Plotbot data type key (e.g., 'mag_SC_4sa').

    Returns:
        list: List of relative paths to downloaded files or an empty list if download failed.
    """
    print_manager.debug(f"[DOWNLOAD_SPDF_ENTRY] Received trange: {trange}, data_type: {plotbot_key}")
    print_manager.debug(f"Attempting SPDF download for {plotbot_key} in range {trange}")

    if plotbot_key not in PYSPEDAS_MAP:
        print_manager.warning(f"Pyspedas mapping not defined for {plotbot_key}. Cannot download from SPDF.")
        return []
        
    # --- Pre-emptive Rename Logic for Berkeley->SPDF Case Conflict ---
    server_mode = plotbot.config.data_server
    if server_mode in ['spdf', 'dynamic']:
        # This check/rename is necessary because pyspedas's local file check 
        # (specifically when using no_update=True) appears to be case-sensitive 
        # on some systems (like macOS) and fails to find existing files downloaded 
        # from the Berkeley server, which use different casing (e.g., ..._Sa_...).
        # Renaming existing Berkeley files to the expected SPDF case allows the
        # pyspedas local check (no_update=True) to succeed. The subsequent 
        # no_update=False call correctly handles existing files regardless of case, 
        # but we want the no_update=True check to work reliably if possible to potentially
        # avoid unnecessary network index checks.
        print_manager.debug(f"Checking for Berkeley/SPDF case conflicts before SPDF download for {plotbot_key}...")
        try:
            config = data_types.get(plotbot_key)
            # Proceed only if we have the necessary config keys and it's a daily file format
            if config and config.get('file_time_format') == 'daily' and \
                'local_path' in config and 'file_pattern_import' in config:
                
                local_path_template = config['local_path']
                berkeley_pattern_tmpl = config['file_pattern_import'] # Berkeley case pattern
                data_level = config.get('data_level', 'l2') # Default level if needed
                
                dates_to_check = _get_dates_in_range(trange[0], trange[1])

                for date_str in dates_to_check:
                    year_str = date_str[:4]
                    try:
                        # Construct full path and pattern for this date
                        # Assume paths in config are relative to workspace root
                        WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Simple way to get workspace root
                        relative_dir = local_path_template.format(data_level=data_level)
                        expected_dir = os.path.join(WORKSPACE_ROOT, relative_dir, year_str)

                        if not os.path.isdir(expected_dir):
                            # print_manager.debug(f"  Directory not found for rename check: {expected_dir}")
                            continue # Skip if dir doesn't exist

                        # Create the specific glob pattern for Berkeley case for this date
                        berkeley_pattern = berkeley_pattern_tmpl.format(data_level=data_level, date_str=date_str)
                        berkeley_glob_pattern = os.path.join(expected_dir, berkeley_pattern)

                        found_berkeley_files = glob.glob(berkeley_glob_pattern)

                        for berkeley_file_path in found_berkeley_files:
                            berkeley_basename = os.path.basename(berkeley_file_path)
                            spdf_basename = berkeley_basename # Start with original
                            
                            # Apply case changes based on plotbot_key
                            rename_needed = False
                            if plotbot_key == 'mag_RTN_4sa':
                                temp_name = spdf_basename.replace('RTN', 'rtn').replace('Sa', 'sa').replace('Cyc', 'cyc')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            elif plotbot_key == 'mag_SC_4sa':
                                temp_name = spdf_basename.replace('SC', 'sc').replace('Sa', 'sa').replace('Cyc', 'cyc')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            elif plotbot_key == 'spi_sf00_l3_mom':
                                temp_name = spdf_basename.replace('L3', 'l3')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            elif plotbot_key == 'spe_sf0_pad':
                                temp_name = spdf_basename.replace('L3', 'l3')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            # Add more rules if needed for other keys

                            if rename_needed:
                                target_spdf_path = os.path.join(expected_dir, spdf_basename)
                                print_manager.debug(f"  Attempting rename for {date_str}: {berkeley_basename} -> {spdf_basename}")
                                try:
                                    os.rename(berkeley_file_path, target_spdf_path)
                                    # Verify rename by checking target existence
                                    if os.path.exists(target_spdf_path):
                                        print_manager.debug(f"  Rename successful for {date_str}.")
                                    else:
                                        print_manager.warning(f"  Rename seemed to succeed but target not found for {date_str}: {target_spdf_path}")
                                except OSError as e:
                                    print_manager.warning(f"  Rename failed for {date_str}: {e}")
                            else:
                                print_manager.debug(f"  File case already matches SPDF for {date_str}: {berkeley_basename}")
                    except KeyError as e:
                        print_manager.warning(f"  Missing placeholder formatting pattern for {plotbot_key}, date {date_str}: {e}")
                    except Exception as e_inner:
                        print_manager.warning(f"  Error processing rename for date {date_str}: {e_inner}")
            else:
                print_manager.debug(f"  Skipping rename check for {plotbot_key} (missing config or not daily format).")
        except Exception as e:
            print_manager.warning(f"Error during pre-emptive rename check: {e}")
    # --- End Pre-emptive Rename Logic ---
        
    map_config = PYSPEDAS_MAP[plotbot_key]
    pyspedas_func = map_config['pyspedas_func']
    pyspedas_datatype = map_config['pyspedas_datatype']
    kwargs = map_config['kwargs']
    
    file_path = None
    returned_data = None
    
    try:
        # 1. Check locally ONLY (reliable offline) - REMOVED
        # print_manager.debug(f"Checking SPDF locally (no_update=True) for {pyspedas_datatype}...") # Old debug message
        # returned_data = pyspedas_func(
        #     trange=trange,
        #     datatype=pyspedas_datatype,
        #     no_update=True,
        #     downloadonly=True,
        #     notplot=True,
        #     time_clip=True, # Consistent with tests
        #     **kwargs
        # )
        # if returned_data and isinstance(returned_data, list) and len(returned_data) > 0:
        #     file_path = returned_data[0]

        # 2. If not found locally, attempt download (only if online) - NOW THE ONLY STEP
        # if not file_path: # Condition removed as this is the only step now
        print_manager.debug(f"Attempting SPDF check/download (no_update=False) for {pyspedas_datatype}...")
        returned_data = pyspedas_func(
            trange=trange,
            datatype=pyspedas_datatype,
            no_update=False, # Always check online / download if needed
            downloadonly=True,
            notplot=True,
            time_clip=True,
            **kwargs
        )
        # Removed redundant assignment to file_path
        # if returned_data and isinstance(returned_data, list) and len(returned_data) > 0:
        #     file_path = returned_data[0]
        #     # TODO: Add this file path to a cleanup list?
        # else:
        #     print_manager.warning(f"SPDF download attempt for {plotbot_key} did not return a file path.")

    except Exception as e:
        print_manager.error(f"Error during pyspedas check/download for {plotbot_key}: {e}")
        # Optionally, log the full traceback for debugging
        # import traceback
        # print_manager.error(traceback.format_exc())
        return False # Return False on error

    if returned_data and isinstance(returned_data, list) and len(returned_data) > 0:
        # Pyspedas returns a list of relative paths
        # Return the list as is on success
        return returned_data 
    else:
        print_manager.warning(f"Could not find or download {plotbot_key} from SPDF.")
        # Return empty list on failure to be consistent with pyspedas downloadonly=True behavior
        return [] 