import numpy as np

# Assuming get_data, time_datetime, downsample_time_based, lista_hista2d are available
try:
    from ..functions import (
        get_data, time_datetime, downsample_time_based, lista_hista2d, lista_hista
    )
except ImportError:
    print("Warning: Could not import functions from ..functions for wave power calcs.")
    # Define dummy functions
    def get_data(var): return None
    def time_datetime(t): return []
    def downsample_time_based(t1, d1, t2): return None
    def lista_hista2d(t, d, **kwargs): return None, None, None
    def lista_hista(t, tau): return None, None

def calculate_wave_power_vars(datetime_spi):
    """Calculates variables related to Wave Power data."""
    results = {}
    wvpow_LH_dat = get_data('wavePower_LH')
    wvpow_RH_dat = get_data('wavePower_RH')

    if wvpow_LH_dat is None or wvpow_RH_dat is None:
        print("Warning: Wave power data (LH or RH) not found.")
        return results

    wvpow_times = wvpow_LH_dat.times
    results['wvpow_times'] = wvpow_times
    datetime_wvpow = time_datetime(wvpow_times)
    results['datetime_wvpow'] = datetime_wvpow
    wvpow_LH = wvpow_LH_dat.y
    wvpow_RH = wvpow_RH_dat.y
    results['wvpow_LH'] = wvpow_LH
    results['wvpow_RH'] = wvpow_RH

    if datetime_spi is not None: # Ensure datetime_spi was calculated
        wvpow_LH_spi = downsample_time_based(datetime_wvpow, wvpow_LH, datetime_spi)
        wvpow_RH_spi = downsample_time_based(datetime_wvpow, wvpow_RH, datetime_spi)
        results['wvpow_LH_spi'] = wvpow_LH_spi
        results['wvpow_RH_spi'] = wvpow_RH_spi
    else:
        print("Warning: datetime_spi not provided for wave power downsampling.")

    # Histograms (multiple time scales)
    hist_results = {}
    log_wvpow_RH = np.log10(wvpow_RH)
    log_wvpow_LH = np.log10(wvpow_LH)
    hist_range = [[wvpow_times[0], wvpow_times[-1]], [-3, 3]]
    
    for tau_label, tau_sec in [('30s', 30), ('2m', 120), ('20m', 1200), ('90m', 5400), ('4h', 14400), ('12h', 43200)]:
        hist_results[tau_label] = {}
        # RH
        h_RH, bin_t_RH, bin_v_RH = lista_hista2d(datetime_wvpow, log_wvpow_RH, density=True, cmax=1e-3, tau=tau_sec, range=hist_range, cmap='Reds')
        hist_results[tau_label]['h_RH'] = h_RH
        hist_results[tau_label]['bin_t_RH'] = bin_t_RH
        hist_results[tau_label]['bin_v_RH'] = bin_v_RH
        
        # LH
        h_LH, bin_t_LH, bin_v_LH = lista_hista2d(datetime_wvpow, log_wvpow_LH, density=True, cmax=1e-3, tau=tau_sec, range=hist_range, cmap='Blues')
        hist_results[tau_label]['h_LH'] = h_LH
        hist_results[tau_label]['bin_t_LH'] = bin_t_LH
        hist_results[tau_label]['bin_v_LH'] = bin_v_LH

        # Repeat times and values for plotting (if histograms were generated)
        if h_RH is not None and bin_t_RH is not None and bin_v_RH is not None:
            times_RH_repeat = np.repeat(np.expand_dims(bin_t_RH, 1), h_RH.shape[1], axis=1)
            ydat_RH = np.power(10, bin_v_RH)
            ydat_RH_repeat = np.repeat(np.expand_dims(ydat_RH, 0), h_RH.shape[0], axis=0) # Corrected axis
            hist_results[tau_label]['times_RH_repeat'] = times_RH_repeat
            hist_results[tau_label]['ydat_RH_repeat'] = ydat_RH_repeat
            
            # Centroids RH
            weights_RH = np.ma.masked_invalid(h_RH.T)
            if not np.all(weights_RH.mask):
                 hist_results[tau_label]['centroids_RH'] = np.ma.average(ydat_RH_repeat.T, axis=1, weights=weights_RH) # Average along correct axis
            else:
                 hist_results[tau_label]['centroids_RH'] = np.full(h_RH.shape[0], np.nan)

        if h_LH is not None and bin_t_LH is not None and bin_v_LH is not None:
            times_LH_repeat = np.repeat(np.expand_dims(bin_t_LH, 1), h_LH.shape[1], axis=1)
            ydat_LH = np.power(10, bin_v_LH)
            ydat_LH_repeat = np.repeat(np.expand_dims(ydat_LH, 0), h_LH.shape[0], axis=0) # Corrected axis
            hist_results[tau_label]['times_LH_repeat'] = times_LH_repeat
            hist_results[tau_label]['ydat_LH_repeat'] = ydat_LH_repeat
            
            # Centroids LH
            weights_LH = np.ma.masked_invalid(h_LH.T)
            if not np.all(weights_LH.mask):
                 hist_results[tau_label]['centroids_LH'] = np.ma.average(ydat_LH_repeat.T, axis=1, weights=weights_LH)
            else:
                 hist_results[tau_label]['centroids_LH'] = np.full(h_LH.shape[0], np.nan)

    results['histograms'] = hist_results
    return results
