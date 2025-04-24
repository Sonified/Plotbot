"""Module for downloading PSP data using pyspedas from SPDF.

This module will contain the logic to interact with pyspedas for downloading
files based on Plotbot data type keys and time ranges, utilizing the 
no_update=[True, False] strategy for offline reliability.
"""

import pyspedas
import os

from .print_manager import print_manager
from .data_classes.psp_data_types import data_types # To get pyspedas datatype mapping
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

def download_spdf_data(trange, plotbot_key):
    """Attempts to download data using pyspedas from SPDF.
    
    Uses the no_update=[True, False] strategy for offline reliability.
    Checks local files first, then attempts download if not found.

    Args:
        trange (list): Time range ['.start', 'end']
        plotbot_key (str): The Plotbot data type key (e.g., 'mag_SC_4sa').

    Returns:
        str or None: The relative path to the downloaded/found file if successful,
                     None otherwise.
    """
    print_manager.debug(f"Attempting SPDF download for {plotbot_key} in range {trange}")

    if plotbot_key not in PYSPEDAS_MAP:
        print_manager.warning(f"Pyspedas mapping not defined for {plotbot_key}. Cannot download from SPDF.")
        return None
        
    map_config = PYSPEDAS_MAP[plotbot_key]
    pyspedas_func = map_config['pyspedas_func']
    pyspedas_datatype = map_config['pyspedas_datatype']
    kwargs = map_config['kwargs']
    
    file_path = None
    returned_data = None
    
    try:
        # 1. Check locally ONLY (reliable offline)
        print_manager.debug(f"Checking SPDF locally (no_update=True) for {pyspedas_datatype}...")
        returned_data = pyspedas_func(
            trange=trange,
            datatype=pyspedas_datatype,
            no_update=True,
            downloadonly=True,
            notplot=True,
            time_clip=True, # Consistent with tests
            **kwargs
        )
        if returned_data and isinstance(returned_data, list) and len(returned_data) > 0:
            file_path = returned_data[0]
            print_manager.status(f"✓ Found {plotbot_key} locally via SPDF check: {file_path}")

        # 2. If not found locally, attempt download (only if online)
        if not file_path:
            print_manager.debug(f"Attempting SPDF download (no_update=False) for {pyspedas_datatype}...")
            returned_data = pyspedas_func(
                trange=trange,
                datatype=pyspedas_datatype,
                no_update=False,
                downloadonly=True,
                notplot=True,
                time_clip=True,
                **kwargs
            )
            if returned_data and isinstance(returned_data, list) and len(returned_data) > 0:
                file_path = returned_data[0]
                print_manager.status(f"✓ Downloaded {plotbot_key} via SPDF: {file_path}")
                # TODO: Add this file path to a cleanup list?
            else:
                print_manager.warning(f"SPDF download attempt for {plotbot_key} did not return a file path.")

    except Exception as e:
        print_manager.error(f"Error during pyspedas check/download for {plotbot_key}: {e}")
        # Optionally, log the full traceback for debugging
        # import traceback
        # print_manager.error(traceback.format_exc())
        return None # Return None on error

    if file_path:
        # TODO: Perform any necessary validation on the file_path?
        # For now, just return the relative path string.
        return file_path
    else:
        print_manager.warning(f"Could not find or download {plotbot_key} from SPDF.")
        return None 