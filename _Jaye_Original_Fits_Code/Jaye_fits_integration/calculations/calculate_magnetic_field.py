import numpy as np
from datetime import datetime, timezone
from scipy import constants
# Assuming get_data, split_vec, time_datetime are available (e.g., from ..functions import *)
# Or potentially from pyspedas import get_data, time_datetime; from pytplot import split_vec

# Placeholder for imports - adjust as needed
try:
    from ..functions import get_data, split_vec, time_datetime
except ImportError:
    # Fallback or placeholder if direct import fails
    print("Warning: Could not import functions from ..functions. Ensure dependencies are correct.")
    # Define dummy functions or raise error if essential
    def get_data(var): return None
    def split_vec(var): pass
    def time_datetime(t): return []


def calculate_mag_rtn_4sa_vars():
    """Calculates variables for MAG RTN 4 Sa/cycle data."""
    results = {}
    # Get magnetic field and time data for RTN coordinates at 4 samples per cycle
    mag_data_RTN_4sa = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc')
    if mag_data_RTN_4sa is None:
        print("Warning: psp_fld_l2_mag_RTN_4_Sa_per_Cyc data not found.")
        return results # Return empty dict if data is missing

    mag_time_RTN_4sa, mag_field_RTN_4sa = mag_data_RTN_4sa.times, mag_data_RTN_4sa.y
    results['mag_time_RTN_4sa'] = mag_time_RTN_4sa
    results['mag_field_RTN_4sa'] = mag_field_RTN_4sa

    # Access components of magnetic field in RTN coordinates at 4 samples per second
    split_vec('psp_fld_l2_mag_RTN_4_Sa_per_Cyc')
    br_RTN_4sa_data = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_x')
    bt_RTN_4sa_data = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_y')
    bn_RTN_4sa_data = get_data('psp_fld_l2_mag_RTN_4_Sa_per_Cyc_z')

    if br_RTN_4sa_data is None or bt_RTN_4sa_data is None or bn_RTN_4sa_data is None:
        print("Warning: Could not retrieve split components for mag_RTN_4sa.")
        return results # Return partial results if components missing

    br_RTN_4sa = br_RTN_4sa_data.y
    bt_RTN_4sa = bt_RTN_4sa_data.y
    bn_RTN_4sa = bn_RTN_4sa_data.y

    bmag_RTN_4sa = np.sqrt(br_RTN_4sa**2 + bt_RTN_4sa**2 + bn_RTN_4sa**2)
    results['br_RTN_4sa'] = br_RTN_4sa
    results['bt_RTN_4sa'] = bt_RTN_4sa
    results['bn_RTN_4sa'] = bn_RTN_4sa
    results['bmag_RTN_4sa'] = bmag_RTN_4sa

    # Converting the magnetic field time to a timezone-aware datetime object
    datetime_mag_RTN_4sa = np.array([dt.replace(tzinfo=timezone.utc) for dt in time_datetime(mag_time_RTN_4sa)])
    results['datetime_mag_RTN_4sa'] = datetime_mag_RTN_4sa

    # Calculate magnetic pressure
    mu_0 = constants.mu_0  # Permeability of free space
    pmag_RTN_4sa = (bmag_RTN_4sa**2) / (2 * mu_0)

    # Convert to nPa (nanoPascals) to match your other pressure units
    pmag_RTN_4sa = pmag_RTN_4sa * 1e9
    results['pmag_RTN_4sa'] = pmag_RTN_4sa

    return results

def calculate_mag_rtn_vars():
    """Calculates variables for MAG RTN full resolution data."""
    results = {}
    # Get magnetic field and time data for RTN coordinates at full resolution
    mag_data_RTN = get_data('psp_fld_l2_mag_RTN')
    if mag_data_RTN is None:
        print("Warning: psp_fld_l2_mag_RTN data not found.")
        return results
    mag_time_RTN, mag_field_RTN = mag_data_RTN.times, mag_data_RTN.y
    results['mag_time_RTN'] = mag_time_RTN
    results['mag_field_RTN'] = mag_field_RTN

    # Access components of magnetic field in RTN coordinates at full resolution
    split_vec('psp_fld_l2_mag_RTN')
    br_RTN_data = get_data('psp_fld_l2_mag_RTN_x')
    bt_RTN_data = get_data('psp_fld_l2_mag_RTN_y')
    bn_RTN_data = get_data('psp_fld_l2_mag_RTN_z')

    if br_RTN_data is None or bt_RTN_data is None or bn_RTN_data is None:
        print("Warning: Could not retrieve split components for mag_RTN.")
        return results

    br_RTN = br_RTN_data.y
    bt_RTN = bt_RTN_data.y
    bn_RTN = bn_RTN_data.y
    bmag_RTN = np.sqrt(br_RTN**2 + bt_RTN**2 + bn_RTN**2)

    results['br_RTN'] = br_RTN
    results['bt_RTN'] = bt_RTN
    results['bn_RTN'] = bn_RTN
    results['bmag_RTN'] = bmag_RTN

    # Converting the magnetic field time to a timezone-aware datetime object
    datetime_mag_RTN = np.array([dt.replace(tzinfo=timezone.utc) for dt in time_datetime(mag_time_RTN)])
    results['datetime_mag_RTN'] = datetime_mag_RTN
    
    mu_0 = constants.mu_0  # Permeability of free space
    # Calculate magnetic pressure
    pmag_RTN = (bmag_RTN**2) / (2 * mu_0)

    # Convert to nPa (nanoPascals) to match your other pressure units
    pmag_RTN = pmag_RTN * 1e9
    results['pmag_RTN'] = pmag_RTN

    return results
