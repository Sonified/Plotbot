"""Module for downloading PSP data using pyspedas from SPDF.

This module will contain the logic to interact with pyspedas for downloading
files based on Plotbot data type keys and time ranges, utilizing the 
no_update=[True, False] strategy for offline reliability.
"""

import os
import glob # Added
import plotbot # Added for config access
from datetime import datetime, timedelta # Added for date iteration
import cdflib
import numpy as np
from dateutil.parser import parse

from .print_manager import print_manager
from .data_classes.data_types import data_types, get_local_path # To get pyspedas datatype mapping
from .time_utils import daterange
from pathlib import Path
from datetime import timedelta
# Add other necessary imports (time, etc.) as needed

# Import the precise download function for efficiency - moved to function level

def smart_check_local_pyspedas_files(plotbot_key, trange):
    """Smart local file checking for pyspedas data types.
    
    Constructs expected file paths using data_types.py configuration and checks
    if files exist locally before calling pyspedas.
    
    Args:
        plotbot_key (str): The Plotbot data type key (e.g., 'mag_RTN_4sa')
        trange (list): Time range [start, end]
        
    Returns:
        list: List of existing local file paths, or None if files not found
    """
    from .config import config
    
    # Check if we have configuration for this data type
    if plotbot_key not in data_types:
        print_manager.debug(f"No data_types configuration for {plotbot_key}, skipping smart check")
        return None
    
    data_config = data_types[plotbot_key]
    
    # Only do smart checking for data types with clear file patterns
    # Check for 'file_pattern' or 'file_pattern_import' (WIND uses the latter)
    if 'local_path' not in data_config:
        print_manager.debug(f"Missing local_path configuration for {plotbot_key}, skipping smart check")
        return None
    
    if 'file_pattern' not in data_config and 'file_pattern_import' not in data_config:
        print_manager.debug(f"Missing file pattern configuration for {plotbot_key}, skipping smart check")
        return None
    
    try:
        # Parse date range
        start_dt = parse(trange[0].replace('/', ' '))
        end_dt = parse(trange[1].replace('/', ' '))
        
        # Build expected file paths based on data type configuration
        # Priority: spdf_file_pattern > file_pattern > file_pattern_import
        file_pattern = data_config.get('spdf_file_pattern', 
                                      data_config.get('file_pattern', 
                                                     data_config.get('file_pattern_import')))
        data_level = data_config['data_level']
        file_time_format = data_config['file_time_format']
        
        # Use get_local_path() to properly handle config.data_dir (it strips 'data' prefix automatically)
        local_path_template = get_local_path(plotbot_key)
        if not local_path_template:
            print_manager.debug(f"Could not get local path for {plotbot_key}")
            return None
        
        # Construct local path by replacing placeholders
        local_path = local_path_template.format(data_level=data_level)
        base_path = Path(local_path)
        
        expected_files = []
        
        if file_time_format == 'daily':
            # Daily files - one file per day
            current_date = start_dt.date()
            end_date = end_dt.date()
            
            while current_date <= end_date:
                year_str = str(current_date.year)
                date_str = current_date.strftime('%Y%m%d')
                
                # Construct filename pattern (may contain wildcards like v*.cdf)
                filename_pattern = file_pattern.format(data_level=data_level, date_str=date_str)
                
                # Full glob pattern
                glob_pattern = str(base_path / year_str / filename_pattern)
                
                # Use glob to find matching files (handles wildcards like v*)
                import glob as glob_module
                matching_files = glob_module.glob(glob_pattern)
                
                # Add all matching files to expected_files
                expected_files.extend(matching_files)
                
                current_date += timedelta(days=1)
                
        elif file_time_format == '6-hour':
            # 6-hour files - multiple files per day
            from .time_utils import get_needed_6hour_blocks
            needed_blocks = get_needed_6hour_blocks(trange)
            
            import glob as glob_module
            for date_str, hour_str in needed_blocks:
                year_str = date_str[:4]
                date_hour_str = f"{date_str}{hour_str}"
                
                # Construct filename pattern (may contain wildcards)
                filename_pattern = file_pattern.format(data_level=data_level, date_hour_str=date_hour_str)
                
                # Full glob pattern
                glob_pattern = str(base_path / year_str / filename_pattern)
                
                # Use glob to find matching files
                matching_files = glob_module.glob(glob_pattern)
                expected_files.extend(matching_files)
        
        # Check which files actually exist
        existing_files = [f for f in expected_files if Path(f).exists()]
        
        if existing_files:
            print_manager.status(f"✅ Smart check found {len(existing_files)} local {plotbot_key} file(s):")
            for f in existing_files:
                print_manager.status(f"   📁 {f}")
            return existing_files
        else:
            print_manager.status(f"📡 Smart check: {plotbot_key} files not found locally, will download")
            return None
            
    except Exception as e:
        print_manager.debug(f"Smart file check failed for {plotbot_key}: {e}, falling back to pyspedas")
        return None

# Define the mapping from Plotbot keys to pyspedas specifics
# (Borrowed from tests/test_pyspedas_download.py - may need refinement)
# TODO: Formalize this mapping, potentially move to psp_data_types.py?
def _get_pyspedas_map():
    """
    Get the PySpedas mapping dictionary. This function imports pyspedas
    to ensure it reads the environment variables after config is set.
    """
    import pyspedas
    print_manager.debug(f"DEBUG: pyspedas module attributes: {[attr for attr in dir(pyspedas) if not attr.startswith('_')]}")

    
    return {
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
    'spi_sf00_8dx32ex8a': {  # PSP SPAN-I L2 VDF data
        'pyspedas_datatype': 'spi_sf00_8dx32ex8a',
        'pyspedas_func': pyspedas.psp.spi,
        'kwargs': {'level': 'l2', 'get_support_data': True}
    },
    'psp_span_vdf': {  # PSP SPAN-I VDF data (plotbot interface)
        'pyspedas_datatype': 'spi_sf00_8dx32ex8a',  # Uses same underlying data
        'pyspedas_func': pyspedas.psp.spi,
        'kwargs': {'level': 'l2', 'get_support_data': True}
    },
    'spe_sf0_pad': {
        'pyspedas_datatype': 'spe_sf0_pad',
        'pyspedas_func': pyspedas.psp.spe,
        'kwargs': {'level': 'l3', 'get_support_data': True}
    },
    'spi_sf0a_l3_mom': {
        'pyspedas_datatype': 'spi_sf0a_l3_mom',
        'pyspedas_func': pyspedas.psp.spi,
        'kwargs': {'level': 'l3'}
    },
    'sqtn_rfs_v1v2': {
        'pyspedas_datatype': 'sqtn_rfs_V1V2',  # Pyspedas still expects uppercase datatype
        'pyspedas_func': pyspedas.psp.fields,
        'kwargs': {'level': 'l3', 'get_support_data': True}
    },
    'dfb_ac_spec_dv12hg': {  # PSP FIELDS AC spectrum dv12 - PRECISE DOWNLOAD WITH FALLBACK
        'pyspedas_datatype': 'dfb_ac_spec',        # Regular PySpedas fallback
        'pyspedas_func': pyspedas.psp.fields,      # Regular PySpedas fallback
        'kwargs': {'level': 'l2', 'time_clip': True}, # Regular PySpedas fallback
        'download_method': 'precise',              # NEW: Use precise method first
        'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_ac_spec/dv12hg/',
        'local_path': 'data/psp/fields/l2/dfb_ac_spec/dv12hg/',
        'expected_var': 'psp_fld_l2_dfb_ac_spec_dV12hg'
    },
    'dfb_ac_spec_dv34hg': {  # PSP FIELDS AC spectrum dv34 - PRECISE DOWNLOAD WITH FALLBACK
        'pyspedas_datatype': 'dfb_ac_spec',        # Regular PySpedas fallback (same as dv12hg)
        'pyspedas_func': pyspedas.psp.fields,      # Regular PySpedas fallback
        'kwargs': {'level': 'l2', 'time_clip': True}, # Regular PySpedas fallback
        'download_method': 'precise',              # NEW: Use precise method first
        'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_ac_spec/dv34hg/',
        'local_path': 'data/psp/fields/l2/dfb_ac_spec/dv34hg/',
        'expected_var': 'psp_fld_l2_dfb_ac_spec_dV34hg'
    },
    'dfb_dc_spec_dv12hg': {  # PSP FIELDS DC spectrum dv12 - PRECISE DOWNLOAD WITH FALLBACK
        'pyspedas_datatype': 'dfb_dc_spec',        # Regular PySpedas fallback
        'pyspedas_func': pyspedas.psp.fields,      # Regular PySpedas fallback
        'kwargs': {'level': 'l2', 'time_clip': True}, # Regular PySpedas fallback
        'download_method': 'precise',              # NEW: Use precise method first
        'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_dc_spec/dv12hg/',
        'local_path': 'data/psp/fields/l2/dfb_dc_spec/dv12hg/',
        'expected_var': 'psp_fld_l2_dfb_dc_spec_dV12hg'
    },
    # Add mappings for other data types as needed (e.g., high-res versions)
    
    # === WIND SATELLITE DATA TYPES ===
    # Magnetic Field Investigation (MFI) - 11 samples/sec
    'wind_mfi_h2': {
        'pyspedas_datatype': 'h2',
        'pyspedas_func': pyspedas.wind.mfi,
        'kwargs': {}  # No level parameter needed
    },
    # Solar Wind Experiment (SWE) - proton/alpha moments, 92-sec
    'wind_swe_h1': {
        'pyspedas_datatype': 'h1',
        'pyspedas_func': pyspedas.wind.swe,
        'kwargs': {}  # No level parameter needed
    },
    # Solar Wind Experiment (SWE) - electron temperature
    'wind_swe_h5': {
        'pyspedas_datatype': 'h5',
        'pyspedas_func': pyspedas.wind.swe,
        'kwargs': {}  # No level parameter needed
    },
    # 3D Plasma Analyzer (3DP) - ion parameters, 3-sec high resolution
    'wind_3dp_pm': {
        'pyspedas_datatype': '3dp_pm',
        'pyspedas_func': pyspedas.wind.threedp,
        'kwargs': {}  # No level parameter needed
    },
    # 3D Plasma Analyzer (3DP) - electron pitch-angle distributions, 24-sec
    'wind_3dp_elpd': {
        'pyspedas_datatype': '3dp_elpd',
        'pyspedas_func': pyspedas.wind.threedp,
        'kwargs': {}  # No level parameter needed
    }
    }

def _get_dates_for_download(start_str, end_str):
    """Helper to get list of date strings formatted for file downloads (YYYYMMDD).
    
    If end_str is exactly midnight (00:00:00), that day is excluded since
    the range is [start, end) not [start, end].
    """
    dates = []
    try:
        # Use the more robust dateutil.parser to handle various formats
        start_dt = parse(start_str)
        end_dt = parse(end_str)
        
        start_date = start_dt.date()
        end_date = end_dt.date()
        
        # Check if end time is exactly midnight - if so, exclude that day
        # because trange is [start, end) not [start, end]
        is_end_midnight = (end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0)
        
        delta = timedelta(days=1)
        current_date = start_date
        
        # Use < instead of <= to avoid including end_date when it's midnight
        while current_date < end_date or (current_date == end_date and not is_end_midnight):
            dates.append(current_date.strftime('%Y%m%d'))
            current_date += delta
    except Exception as e:
        print_manager.warning(f"Could not parse dates from trange for download: {start_str}, {end_str}. Error: {e}")
    return dates

def download_dfb_precise(trange, plotbot_key, config):
    """
    Download DFB data using precise pyspedas.download() for maximum efficiency.
    
    This approach downloads only the exact files needed, avoiding the inefficiency
    of regular pyspedas.psp.fields() which downloads many extra files.
    
    Args:
        trange (list): Time range ['start', 'end']
        plotbot_key (str): The Plotbot data type key (e.g., 'dfb_ac_spec_dv12hg')
        config (dict): Configuration with remote_path, local_path, etc.
    
    Returns:
        list: List of relative paths to downloaded files or empty list if failed
    """
    print_manager.debug(f"[DFB_PRECISE_DOWNLOAD] Starting precise download for {plotbot_key}")
    
    # Import pyspedas download function here
    try:
        from pyspedas import download as pyspedas_download
    except ImportError:
        print_manager.error("pyspedas.download not available - falling back to regular method")
        return []
    
    # Get the dates we need to download
    dates = _get_dates_for_download(trange[0], trange[1])
    if not dates:
        print_manager.error(f"Could not parse dates from trange: {trange}")
        return []
    
    downloaded_files = []
    
    for date_str in dates:
        year = date_str[:4]
        
        # Construct remote and local paths
        remote_path = config['remote_path'] + year + '/'
        # FIXED: Use get_local_path() to properly respect custom config.data_dir
        # The config['local_path'] is just a template - get_local_path() converts it to the actual path
        import os
        from plotbot.data_classes.data_types import get_local_path
        local_path_template = get_local_path(plotbot_key)
        # Format the template with the actual data level (e.g., replace {data_level} with l2)
        data_level = config.get('data_level', 'l2')
        local_path_base = local_path_template.format(data_level=data_level)
        local_path = os.path.join(local_path_base, year)
        # Ensure the directory exists before pyspedas tries to download
        os.makedirs(local_path, exist_ok=True)
        local_path = local_path + '/'  # pyspedas expects trailing slash
        
        # File pattern for this specific date
        file_pattern = f'*{date_str}*.cdf'
        
        print_manager.debug(f"Precise download: {plotbot_key} for {date_str}")
        print_manager.debug(f"  Remote: {remote_path}")
        print_manager.debug(f"  Local: {local_path}")
        print_manager.debug(f"  Pattern: {file_pattern}")
        
        try:
            files = pyspedas_download(
                remote_path=remote_path,
                remote_file=[file_pattern],
                local_path=local_path,
                last_version=True
            )
            
            if files:
                downloaded_files.extend(files)
                print_manager.debug(f"  ✅ Downloaded {len(files)} file(s) for {date_str}")
                for file in files:
                    file_size = os.path.getsize(file) / (1024*1024) if os.path.exists(file) else 0
                    print_manager.debug(f"    - {os.path.basename(file)} ({file_size:.1f} MB)")
            else:
                print_manager.debug(f"  ❌ No files found for {date_str}")
                
        except Exception as e:
            print_manager.warning(f"Precise download failed for {plotbot_key} date {date_str}: {e}")
            # Continue with other dates
    
    if downloaded_files:
        print_manager.debug(f"[DFB_PRECISE_DOWNLOAD] Successfully downloaded {len(downloaded_files)} files for {plotbot_key}")
        print_manager.debug(f"Efficiency gain: Downloaded only needed files (vs ~4-8 extra files with regular method)")
    else:
        print_manager.warning(f"[DFB_PRECISE_DOWNLOAD] No files downloaded for {plotbot_key}")
    
    return downloaded_files

def _get_dates_in_range(start_str, end_str):
    """Helper to get list of YYYYMMDD strings for a date range.
    
    If end_str is exactly midnight (00:00:00), that day is excluded since
    the range is [start, end) not [start, end].
    """
    dates = []
    try:
        # Attempt to parse common date formats - need full datetime now to check for midnight
        start_dt = None
        end_dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                if start_dt is None:
                    start_dt = datetime.strptime(start_str, fmt)
                if end_dt is None:
                    end_dt = datetime.strptime(end_str, fmt)
                if start_dt and end_dt: # Stop if both parsed
                    break 
            except ValueError:
                continue # Try next format
        
        if start_dt is None or end_dt is None:
            raise ValueError("Could not parse start or end date string")
        
        start_date = start_dt.date()
        end_date = end_dt.date()
        
        # Check if end time is exactly midnight - if so, exclude that day
        is_end_midnight = (end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0)

        delta = timedelta(days=1)
        current_date = start_date
        # Use < instead of <= to avoid including end_date when it's midnight
        while current_date < end_date or (current_date == end_date and not is_end_midnight):
            dates.append(current_date.strftime('%Y%m%d'))
            current_date += delta
    except Exception as e:
        print_manager.warning(f"Could not parse dates from trange for rename check: {start_str}, {end_str}. Error: {e}")
    return dates

def download_spdf_data(trange, plotbot_key):
    """Attempts to download data using pyspedas from SPDF.
    
    SMART APPROACH: Checks for local files first using data_types.py patterns,
    only calls pyspedas if files are missing. Preserves all server config logic.

    Args:
        trange (list): Time range ['.start', 'end']
        plotbot_key (str): The Plotbot data type key (e.g., 'mag_SC_4sa').

    Returns:
        list: List of relative paths to downloaded files or an empty list if download failed.
    """
    print_manager.debug(f"[DOWNLOAD_SPDF_ENTRY] Received trange: {trange}, data_type: {plotbot_key}")
    print_manager.debug(f"Attempting SPDF download for {plotbot_key} in range {trange}")

    # SMART CHECK: Look for local files first before calling pyspedas
    local_files = smart_check_local_pyspedas_files(plotbot_key, trange)
    if local_files:
        print_manager.status(f"✅ Using local {plotbot_key} files (skipping pyspedas)")
        return local_files

    # Import pyspedas here so it reads the environment variables AFTER config is set
    import pyspedas
    
    print_manager.status(f"📡 Local files not found, proceeding with pyspedas download for {plotbot_key}")

    PYSPEDAS_MAP = _get_pyspedas_map()
    if plotbot_key not in PYSPEDAS_MAP:
        print_manager.warning(f"Pyspedas mapping not defined for {plotbot_key}. Cannot download from SPDF.")
        return []
    
    map_config = PYSPEDAS_MAP[plotbot_key]
    
    # Check if this is a DFB data type that should use precise download
    if map_config.get('download_method') == 'precise':
        print_manager.debug(f"Attempting PRECISE download method for {plotbot_key} (efficiency optimized)")
        precise_result = download_dfb_precise(trange, plotbot_key, map_config)
        
        # If precise download succeeded, return it
        if precise_result and len(precise_result) > 0:
            print_manager.debug(f"✅ Precise download succeeded for {plotbot_key}: {len(precise_result)} files")
            return precise_result
        else:
            print_manager.warning(f"❌ Precise download failed for {plotbot_key}, falling back to regular PySpedas method")
            # Continue to regular PySpedas download below
    
    # Use regular PySpedas download method (either as primary method or as fallback)
    method_type = "FALLBACK" if map_config.get('download_method') == 'precise' else "REGULAR"
    print_manager.debug(f"Using {method_type} PySpedas download method for {plotbot_key}")
        
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
            from .data_classes.data_types import get_data_type_config
            config = get_data_type_config(plotbot_key)
            # Proceed only if we have the necessary config keys and it's a daily file format
            if config and config.get('file_time_format') == 'daily' and \
                'local_path' in config and 'file_pattern_import' in config:
                
                local_path_template = get_local_path(plotbot_key)
                berkeley_pattern_tmpl = config['file_pattern_import'] # Berkeley case pattern
                data_level = config.get('data_level', 'l2') # Default level if needed
                
                dates_to_check = _get_dates_in_range(trange[0], trange[1])

                for date_str in dates_to_check:
                    year_str = date_str[:4]
                    try:
                        # Construct full path and pattern for this date
                        # get_local_path() already returns the absolute path including config.data_dir
                        full_path = local_path_template.format(data_level=data_level)
                        expected_dir = os.path.join(full_path, year_str)

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
                            elif plotbot_key == 'spi_sf0a_l3_mom':
                                temp_name = spdf_basename.replace('L3', 'l3')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            elif plotbot_key == 'sqtn_rfs_v1v2':
                                temp_name = spdf_basename.replace('V1V2', 'v1v2')
                                if temp_name != spdf_basename: spdf_basename, rename_needed = temp_name, True
                            elif plotbot_key in ['spi_sf00_8dx32ex8a', 'psp_span_vdf']:  # VDF case handling
                                temp_name = spdf_basename.replace('8Dx32Ex8A', '8dx32ex8a').replace('L2', 'l2')
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
            # CRITICAL: no_update=False is required!
            # no_update=True ignores level/datatype parameters and returns ANY matching files
            no_update=False, # Must be False to respect level and datatype specifications!
            downloadonly=True,
            notplot=True,
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