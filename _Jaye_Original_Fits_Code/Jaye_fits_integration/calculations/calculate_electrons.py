import numpy as np
from datetime import datetime, timezone

# Assuming get_data, time_datetime, time_double are available
try:
    from ..functions import get_data, time_datetime, time_double
except ImportError:
    print("Warning: Could not import functions from ..functions for electron calcs.")
    def get_data(var): return None
    def time_datetime(t): return []
    def time_double(t): return 0 # Or appropriate default

def calculate_electron_pad_vars(trange):
    """Calculates variables for Electron PAD data."""
    results = {}
    #Access electron strahl pitch-angle distribution (PAD)
    epad_data = get_data('psp_spe_EFLUX_VS_PA_E')
    epad_PA = get_data('psp_spe_PITCHANGLE')

    if epad_data is None or epad_PA is None:
        print("Warning: Electron PAD data (EFLUX or PITCHANGLE) not found.")
        return results

    epad_times = epad_data.times
    epad_vals = epad_data.y
    epad_PA_vals = epad_PA.y

    results['epad_times'] = epad_times
    results['epad_vals'] = epad_vals
    results['epad_PA_vals'] = epad_PA_vals

    # Determine energy index based on time range
    # Note: trange needs to be passed into this function
    if (time_double(trange[0]) < time_double('2021-11-15')):
        strahl_energy_index = 8
    else:
        strahl_energy_index = 10
    
    energy_index = strahl_energy_index
    results['strahl_energy_index'] = strahl_energy_index

    if energy_index >= epad_vals.shape[2]:
         print(f"Warning: energy_index {energy_index} is out of bounds for epad_vals shape {epad_vals.shape}")
         return results # Avoid index error

    epad_strahl = epad_vals[:,:,energy_index]
    results['epad_strahl'] = epad_strahl

    # Convert Unix timestamps to timezone-aware datetime objects in UTC
    datetime_spe = np.array([dt.replace(tzinfo=timezone.utc) for dt in time_datetime(epad_times)])
    results['datetime_spe'] = datetime_spe

    # Prepare the time array for pcolormesh
    times_spe_repeat = np.repeat(
        np.expand_dims(datetime_spe, 1),
        epad_strahl.shape[1], 
        axis = 1
    )
    results['times_spe_repeat'] = times_spe_repeat

    # Apply logarithmic transformation
    # Use np.errstate to handle potential log10 of zero or negative numbers
    with np.errstate(divide='ignore'):
        log_epad_strahl = np.log10(epad_strahl)
    log_epad_strahl[np.isinf(log_epad_strahl)] = np.nan # Replace inf with nan
    results['log_epad_strahl'] = log_epad_strahl

    # Compute centroids
    # Use masked array average to handle potential NaNs introduced by log10
    weights_ma = np.ma.masked_invalid(epad_strahl)
    if not np.all(weights_ma.mask): # Ensure there are valid weights
        centroids_epad = np.ma.average(epad_PA_vals, 
                            weights=weights_ma, 
                            axis=1)
        results['centroids_epad'] = centroids_epad
    else:
        print("Warning: All weights invalid for epad centroid calculation.")
        results['centroids_epad'] = np.full(epad_PA_vals.shape[0], np.nan)

    return results
