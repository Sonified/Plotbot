import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone

# Assuming get_data, time_datetime, downsample_to_min_ind, 
# find_Tanisotropy, lista_hista, upsample_to_match are available
try:
    from ..functions import (
        get_data, time_datetime, downsample_to_min_ind, 
        find_Tanisotropy, lista_hista, upsample_to_match
    )
except ImportError:
    print("Warning: Could not import functions from ..functions for hammerhead calcs.")
    # Define dummy functions
    def get_data(var): return None
    def time_datetime(t): return []
    def downsample_to_min_ind(t1, d1, t2): return None
    def find_Tanisotropy(t1,t2,t3,t4,t5,t6): return None, None, None
    def lista_hista(t, tau): return None, None
    def upsample_to_match(d, t1, t2): return d

def calculate_hammerhead_vars(datham, datetime_spi=None, B_mag_XYZ_spi=None, dens_spi_y=None):
    """Calculates variables related to Hammerhead (HAM) data."""
    results = {}
    if datham is None or not datham:
        print("Warning: Hammerhead data (datham) is empty or None.")
        return results
        
    # Extract data from the datham dictionary
    hardham_list = []
    core_dens_list, neck_dens_list, ham_dens_list = [], [], []
    core_ux_list, core_uy_list, core_uz_list = [], [], []
    neck_ux_list, neck_uy_list, neck_uz_list = [], [], []
    ham_ux_list, ham_uy_list, ham_uz_list = [], [], []
    core_T_list = { 'Txx': [], 'Txy': [], 'Txz': [], 'Tyy': [], 'Tyz': [], 'Tzz': [] }
    neck_T_list = { 'Txx': [], 'Txy': [], 'Txz': [], 'Tyy': [], 'Tyz': [], 'Tzz': [] }
    ham_T_list = { 'Txx': [], 'Txy': [], 'Txz': [], 'Tyy': [], 'Tyz': [], 'Tzz': [] }
    ogflag_list = []

    for key in datham.keys():
        try:
            # Densities
            core_dens_list.append(datham[key]['core_moments']['n'])
            neck_dens_list.append(datham[key]['neck_moments']['n'])
            ham_dens_list.append(datham[key]['hammer_moments']['n'])

            # Velocities
            core_ux_list.append(datham[key]['core_moments']['Ux'])
            core_uy_list.append(datham[key]['core_moments']['Uy'])
            core_uz_list.append(datham[key]['core_moments']['Uz'])
            neck_ux_list.append(datham[key]['neck_moments']['Ux'])
            neck_uy_list.append(datham[key]['neck_moments']['Uy'])
            neck_uz_list.append(datham[key]['neck_moments']['Uz'])
            ham_ux_list.append(datham[key]['hammer_moments']['Ux'])
            ham_uy_list.append(datham[key]['hammer_moments']['Uy'])
            ham_uz_list.append(datham[key]['hammer_moments']['Uz'])

            # Temperatures
            for T_comp in core_T_list.keys():
                 core_T_list[T_comp].append(datham[key]['core_moments'][T_comp])
                 neck_T_list[T_comp].append(datham[key]['neck_moments'][T_comp])
                 ham_T_list[T_comp].append(datham[key]['hammer_moments'][T_comp])

            try: ogflag_list.append(datham[key]['og_flag'])
            except KeyError: ogflag_list.append(False) # Handle missing flag
            
            hardham_list.append(key) # Store the time key

        except KeyError as e:
             print(f"KeyError accessing hammerhead data for key {key}: {e}. Skipping this entry.")
             continue # Skip to next key if data is incomplete

    if not hardham_list: # Check if any valid data was processed
        print("Warning: No valid hammerhead data found after processing keys.")
        return results

    # Convert lists to numpy arrays
    ogflag_list = np.asarray(ogflag_list)
    hardham_list = np.asarray(hardham_list) # These are time keys (likely CDF epoch)
    results['ogflag_list'] = ogflag_list
    results['hardham_times_epoch'] = hardham_list

    # Convert time keys to datetime objects
    hardham_datetime_cdflib = cdflib.cdfepoch.to_datetime(hardham_list)
    hardham_datetime = [pd.Timestamp(t) for t in hardham_datetime_cdflib]
    hardham_datetime_utc = np.array([dt.replace(tzinfo=timezone.utc) for dt in hardham_datetime])
    results['hardham_datetime_utc'] = hardham_datetime_utc

    # Calculate time differences
    dt_hardham_datetime_utc = np.diff(hardham_datetime_utc)
    hardham_datetime_utc_plus_dt = hardham_datetime_utc[:-1] + dt_hardham_datetime_utc
    results['dt_hardham_datetime_utc'] = dt_hardham_datetime_utc
    results['hardham_datetime_utc_plus_dt'] = hardham_datetime_utc_plus_dt

    # Process densities
    core_dens = np.asarray(core_dens_list)
    neck_dens = np.asarray(neck_dens_list)
    ham_dens = np.asarray(ham_dens_list)
    results['core_dens_ham'] = core_dens
    results['neck_dens_ham'] = neck_dens
    results['ham_dens_ham'] = ham_dens
    Ntot_ham = core_dens + neck_dens + ham_dens
    results['Ntot_ham'] = Ntot_ham
    Ntot_ham_safe = np.where(Ntot_ham > 0, Ntot_ham, np.nan)
    core_dens_safe = np.where(core_dens > 0, core_dens, np.nan)
    results['Nham_div_Ntot'] = ham_dens / Ntot_ham_safe
    results['Nham_div_Ncore'] = ham_dens / core_dens_safe
    results['Nneck_div_Ncore'] = neck_dens / core_dens_safe

    # Process velocities
    core_ux = np.asarray(core_ux_list)
    core_uy = np.asarray(core_uy_list)
    core_uz = np.asarray(core_uz_list)
    core_umag = np.sqrt(core_ux**2 + core_uy**2 + core_uz**2)
    results['core_umag_ham'] = core_umag

    neck_ux = np.asarray(neck_ux_list)
    neck_uy = np.asarray(neck_uy_list)
    neck_uz = np.asarray(neck_uz_list)
    neck_umag = np.sqrt(neck_ux**2 + neck_uy**2 + neck_uz**2)
    neck_core_drift = abs(neck_umag - core_umag)
    results['neck_core_drift_ham'] = neck_core_drift

    ham_ux = np.asarray(ham_ux_list)
    ham_uy = np.asarray(ham_uy_list)
    ham_uz = np.asarray(ham_uz_list)
    ham_umag = np.sqrt(ham_ux**2 + ham_uy**2 + ham_uz**2)
    ham_core_drift = np.abs(ham_umag - core_umag)
    results['ham_core_drift_ham'] = ham_core_drift

    # Downsample B and density from SPI if provided
    if datetime_spi is not None and B_mag_XYZ_spi is not None and dens_spi_y is not None:
        print("Downsampling SPI B and density for HAM calculations...")
        b_ds = downsample_to_min_ind(datetime_spi, B_mag_XYZ_spi, hardham_datetime_utc)
        d_ds = downsample_to_min_ind(datetime_spi, dens_spi_y, hardham_datetime_utc)
        d_ds_safe = np.where(d_ds > 0, d_ds, np.nan)
        v_alfven_spi_ham = 21.8 * b_ds / np.sqrt(d_ds_safe)
        v_alfven_spi_ham_safe = np.where(v_alfven_spi_ham != 0, v_alfven_spi_ham, np.nan)
        results['ham_core_drift_va'] = ham_core_drift / v_alfven_spi_ham_safe
        results['neck_core_drift_va'] = neck_core_drift / v_alfven_spi_ham_safe
    else:
        print("Warning: SPI data not provided for HAM Alfven speed calculation.")
        results['ham_core_drift_va'] = np.full_like(ham_core_drift, np.nan)
        results['neck_core_drift_va'] = np.full_like(neck_core_drift, np.nan)

    # Process temperatures
    conv_fac = 1e6 / 11600 # MK to eV
    conv_fac = 1 / conv_fac # Factor to convert from MK? to eV (based on usage)

    core_T = {k: np.asarray(v) / conv_fac for k, v in core_T_list.items()}
    neck_T = {k: np.asarray(v) / conv_fac for k, v in neck_T_list.items()}
    ham_T = {k: np.asarray(v) / conv_fac for k, v in ham_T_list.items()}

    results['core_temp_ham'] = (core_T['Txx'] + core_T['Tyy'] + core_T['Tzz']) / 3 # Note: Original used Tyy twice?
    results['neck_temp_ham'] = (neck_T['Txx'] + neck_T['Tyy'] + neck_T['Tzz']) / 3
    results['ham_temp_ham'] = (ham_T['Txx'] + ham_T['Tyy'] + ham_T['Tzz']) / 3

    # Anisotropy calculations
    T_perp_core, T_parallel_core, Anisotropy_core = find_Tanisotropy(core_T['Txx'],core_T['Tyy'],core_T['Tzz'],core_T['Txy'],core_T['Txz'],core_T['Tyz'])
    T_perp_neck, T_parallel_neck, Anisotropy_neck = find_Tanisotropy(neck_T['Txx'],neck_T['Tyy'],neck_T['Tzz'],neck_T['Txy'],neck_T['Txz'],neck_T['Tyz'])
    T_perp_ham, T_parallel_ham, Anisotropy_ham = find_Tanisotropy(ham_T['Txx'],ham_T['Tyy'],ham_T['Tzz'],ham_T['Txy'],ham_T['Txz'],ham_T['Tyz'])

    results['T_perp_core_ham'] = T_perp_core
    results['T_parallel_core_ham'] = T_parallel_core
    results['Anisotropy_core_ham'] = Anisotropy_core
    results['T_perp_neck_ham'] = T_perp_neck
    results['T_parallel_neck_ham'] = T_parallel_neck
    results['Anisotropy_neck_ham'] = Anisotropy_neck
    results['T_perp_ham_ham'] = T_perp_ham # Renamed to avoid clash
    results['T_parallel_ham_ham'] = T_parallel_ham
    results['Anisotropy_ham_ham'] = Anisotropy_ham

    T_perp_core_safe = np.where(T_perp_core > 0, T_perp_core, np.nan)
    results['Tperp_ham_div_core'] = T_perp_ham / T_perp_core_safe
    results['Tperprat_driftva_hc'] = results['Tperp_ham_div_core'] * results.get('ham_core_drift_va', np.nan) # Use .get for safety

    # Hammerhead histograms
    ham_hist_results = {}
    hardham_datetime_og = np.asarray(hardham_datetime)[ogflag_list]

    for tau_label, tau_sec in [('30s', 30), ('1m', 60), ('2m', 120), ('20m', 1200), ('90m', 5400), ('4h', 14400), ('12h', 43200)]:
        ham_hist_results[tau_label] = {}
        c, bin_t = lista_hista(hardham_datetime, tau_sec)
        c_og, bin_t_og = lista_hista(hardham_datetime_og, tau_sec)
        ham_hist_results[tau_label]['counts'] = c
        ham_hist_results[tau_label]['bin_centers_time'] = bin_t
        ham_hist_results[tau_label]['counts_og'] = c_og
        ham_hist_results[tau_label]['bin_centers_time_og'] = bin_t_og

        # Upsample counts if datetime_spi is available
        if datetime_spi is not None:
             if c is not None and bin_t is not None:
                 ham_hist_results[tau_label]['counts_up'] = upsample_to_match(bin_t, c, datetime_spi)
             if c_og is not None and bin_t_og is not None:
                 ham_hist_results[tau_label]['counts_og_up'] = upsample_to_match(bin_t_og, c_og, datetime_spi)
        
    results['ham_histograms'] = ham_hist_results

    # Upsample other HAM variables to SPI time grid if possible
    if datetime_spi is not None:
        print("Upsampling HAM variables to SPI time grid...")
        results['Anisotropy_ham_up'] = upsample_to_match(hardham_datetime_utc, Anisotropy_ham, datetime_spi)
        results['ham_core_drift_up'] = upsample_to_match(hardham_datetime_utc, ham_core_drift, datetime_spi)
        results['ham_core_drift_va_up'] = upsample_to_match(hardham_datetime_utc, results.get('ham_core_drift_va', np.nan), datetime_spi)
        results['Nham_div_Ncore_up'] = upsample_to_match(hardham_datetime_utc, results['Nham_div_Ncore'], datetime_spi)
        results['Nham_div_Ntot_up'] = upsample_to_match(hardham_datetime_utc, results['Nham_div_Ntot'], datetime_spi)
        results['Tperp_ham_div_core_up'] = upsample_to_match(hardham_datetime_utc, results['Tperp_ham_div_core'], datetime_spi)
        results['Tperprat_driftva_hc_up'] = upsample_to_match(hardham_datetime_utc, results.get('Tperprat_driftva_hc', np.nan), datetime_spi)

    return results
