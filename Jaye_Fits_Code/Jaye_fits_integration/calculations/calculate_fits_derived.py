import numpy as np
import pandas as pd

# Assuming upsample_to_match, downsample_to_match are available
try:
    from ..functions import upsample_to_match, downsample_to_match
except ImportError:
    print("Warning: Could not import functions from ..functions for fits derived calcs.")
    def upsample_to_match(df, t1, t2): return df # Dummy
    def downsample_to_match(t1, d1, t2): return d1 # Dummy

# Define proton mass (use scipy constants if available, otherwise define manually)
try:
    from scipy.constants import physical_constants
    proton_mass_kg_scipy = physical_constants['proton mass'][0]
    electron_volt = physical_constants['electron volt'][0]
    speed_of_light = physical_constants['speed of light in vacuum'][0]
    # Note: The original m_proton_kg calculation in the try block seemed incorrect
except ImportError:
     print("Warning: scipy.constants not found, using approximate proton mass.")
     proton_mass_kg_scipy = 1.67262192e-27 # kg Fallback

# Define m for Tpar_tot calculation (value from original script, units unclear)
m = 1836 * 511000.0 / (299792.0**2)

# Define proton mass in kg for other potential uses (using scipy if available)
m_proton_kg = proton_mass_kg_scipy

def calculate_sf00_fits_vars(df_sf00, vmag_spi=None, datetime_spi=None):
    """Calculates derived variables from the SF00 FITS dataframe."""
    if df_sf00 is None or df_sf00.empty:
        print("Warning: SF00 FITS DataFrame is empty or None.")
        return pd.DataFrame(), {} # Return empty DataFrame and dict
    
    results_np = {}
    df = df_sf00.copy() # Work on a copy

    # Filtering (consider making thresholds arguments)
    filtered_val_index_sf00 = np.where(
        (df['np1'] > 10) &
        (df['np2'] > 10) &
        (df['Tperp1'] > .03) &
        (df['Tperp2'] > .03) &
        (df['Trat1'] > .01) &
        (df['Trat2'] > .01) &
        (df['Trat1'] != 30) &
        (df['Trat2'] != 30) &
        (df['Trat1'] != 2.0) &
        (df['Trat2'] != 2.0) &
        (df['Trat1'] != 1.0) &
        (df['Trat2'] != 1.0) &
        (df['vdrift'] != 10000) &
        (df['vdrift'] != -10000)
    )[0]
    
    mask_sf00 = df.index.isin(filtered_val_index_sf00)
    columns_to_mask_sf00 = df.columns.difference(['time'])
    df.loc[~mask_sf00, columns_to_mask_sf00] = np.nan

    # Datetime conversion
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    datetime_array = df['datetime'].dt.to_pydatetime()
    results_np['datetime_array_sf00'] = datetime_array # Store for potential use

    # Upsampling (if necessary and datetime_spi is provided)
    if datetime_spi is not None and len(datetime_array) < len(datetime_spi):
        print("Upsampling SF00 FITS data...")
        df = upsample_to_match(df, datetime_array, datetime_spi)
        # Recalculate datetime_array after upsampling
        datetime_array = df['datetime'].dt.to_pydatetime()
        results_np['datetime_array_sf00'] = datetime_array
        print(f"SF00 FITS data upsampled to {len(df)} points.")

    # Add moment velocity if available
    if vmag_spi is not None:
        if len(vmag_spi) == len(df):
             df['vsw_mom'] = vmag_spi
        else:
             print(f"Warning: Length mismatch between vmag_spi ({len(vmag_spi)}) and df_sf00 ({len(df)}). Cannot assign vsw_mom.")
             df['vsw_mom'] = np.nan
    else:
        df['vsw_mom'] = np.nan

    # Derived calculations
    df['vp1_mag'] = np.sqrt(df['vp1_x']**2 + df['vp1_y']**2 + df['vp1_z']**2) 
    df['B_mag'] = np.sqrt(df['B_inst_x']**2 + df['B_inst_y']**2 + df['B_inst_z']**2)
    df['bhat_x'] = df['B_inst_x']/df['B_mag']
    df['bhat_y'] = df['B_inst_y']/df['B_mag']
    df['bhat_z'] = df['B_inst_z']/df['B_mag']
    
    df['n_tot'] = df['np1'] + df['np2']
    df['Tperp_tot'] = (df['np1'] * df['Tperp1'] + df['np2'] * df['Tperp2'])/df['n_tot']
    df['Tpar1'] = df['Tperp1']/df['Trat1']
    df['Tpar2'] = df['Tperp2']/df['Trat2']
    # Ensure m is defined (proton mass related constant from original script)
    df['Tpar_tot'] = (df['np1'] * df['Tpar1'] + df['np2'] * df['Tpar2'] + (df['np1'] * df['np2'] / df['n_tot'])* m * (df['vdrift']**2))/df['n_tot']
    df['Trat_tot'] = df['Tperp_tot']/df['Tpar_tot']
    df['Temp_tot'] = (2*df['Tperp_tot'] + df['Tpar_tot'])/3
    
    df['vp1_mag'] = np.sqrt(df['vp1_x']**2 + df['vp1_y']**2 + df['vp1_z']**2)
    df['vcm_x'] = df['vp1_x'] + df['np2']/df['n_tot'] * df['vdrift'] * df['bhat_x'] # Corrected CoM (p2 * vdrift)
    df['vcm_y'] = df['vp1_y'] + df['np2']/df['n_tot'] * df['vdrift'] * df['bhat_y'] # Corrected CoM
    df['vcm_z'] = df['vp1_z'] + df['np2']/df['n_tot'] * df['vdrift'] * df['bhat_z'] # Corrected CoM
    df['vcm_mag'] = np.sqrt(df['vcm_x']**2 + df['vcm_y']**2 + df['vcm_z']**2)

    df['vp2_x'] = df['vp1_x'] + df['vdrift'] * df['bhat_x']
    df['vp2_y'] = df['vp1_y'] + df['vdrift'] * df['bhat_y']
    df['vp2_z'] = df['vp1_z'] + df['vdrift'] * df['bhat_z']
    df['vp2_mag'] = np.sqrt(df['vp2_x']**2 + df['vp2_y']**2 + df['vp2_z']**2)

    # Heat flux
    vt1perp2 = 2 * df['Tperp1']/m 
    vt2perp2 = 2 * df['Tperp2']/m 
    vt1par2 = 2 * df['Tpar1']/m 
    vt2par2 = 2 * df['Tpar2']/m 
    fac = 1.602E-10 # W/m2 conversion
    df['qz_p'] = fac * 0.5 * m * ((df['np1'] * df['np2']) / df['n_tot']) * df['vdrift'] * (1.5 * (vt2par2 - vt1par2) + df['vdrift']**2 * (df['np1']**2 - df['np2']**2)/df['n_tot']**2 + (vt2perp2 - vt1perp2))
    df['|qz_p|'] = np.abs(df['qz_p'])

    # Normalization factors for heat flux
    df['vt_perp_tot'] = np.sqrt(2 * (df['np1'] * df['Tperp1'] + df['np2'] * df['Tperp2']) / (m * df['n_tot']))
    df['vt_par_tot'] = np.sqrt(2 * (df['np1'] * df['Tpar1']+ df['np2'] * df['Tpar2'] + m * df['vdrift']**2 * (df['np1'] * df['np2'])/df['n_tot']) / (m * df['n_tot']))
    df['qz_p_perp']= df['qz_p'] / (m * df['n_tot'] * df['vt_perp_tot']**3)
    df['qz_p_par'] = df['qz_p'] / (m * df['n_tot'] * df['vt_par_tot']**3)

    # Alfven speed, Mach numbers, Beta
    n_tot_safe = np.where(df['n_tot'] > 0, df['n_tot'], np.nan)
    df['valfven_pfits'] = 21.8 * df['B_mag'] / np.sqrt(n_tot_safe)
    df['vdrift_va_pfits'] = df['vdrift'] / df['valfven_pfits']
    df['Vcm_mach_pfits'] = df['vcm_mag'] / df['valfven_pfits']
    df['Vp1_mach_pfits'] = df['vp1_mag'] / df['valfven_pfits']
    df['vsw_mach_pfits'] = df['vsw_mom'] / df['valfven_pfits']

    beta_denom = (1e-5 * df['B_mag'])**2
    beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)
    df['beta_ppar_pfits'] = (4.03E-11 * df['n_tot'] * df['Tpar_tot']) / beta_denom_safe
    df['beta_pperp_pfits'] = (4.03E-11 * df['n_tot'] * df['Tperp_tot']) / beta_denom_safe
    df['beta_par_p1'] = (4.03E-11 * df['np1'] * df['Tpar1']) / beta_denom_safe
    df['beta_par_p2'] = (4.03E-11 * df['np2'] * df['Tpar2']) / beta_denom_safe
    df['beta_perp_p1'] = (4.03E-11 * df['np1'] * df['Tperp1']) / beta_denom_safe
    df['beta_perp_p2'] = (4.03E-11 * df['np2'] * df['Tperp2']) / beta_denom_safe
    df['beta_p_pfits_tot'] = np.sqrt(df['beta_ppar_pfits']**2 + df['beta_pperp_pfits']**2)

    # Hammerhead diagnostic
    Trat_tot_safe = np.where(df['Trat_tot'] != 0, df['Trat_tot'], np.nan)
    df['ham_param'] = (df['Tperp2']/df['Tperp1']) / Trat_tot_safe
    
    #--------------------FITS Variables For Plotbot--------------------
    # Convert selected columns to numpy arrays for results_np dictionary
    cols_to_convert = [
        'qz_p', 'vsw_mach_pfits', 'beta_ppar_pfits', 'beta_pperp_pfits', 'ham_param',
        'np1', 'np2', 'n_tot', 'vp1_x', 'vp1_y', 'vp1_z', 'vp1_mag', 'vcm_x',
        'vcm_y', 'vcm_z', 'vcm_mag', 'vdrift', 'vdrift_va_pfits', 'Trat1', 'Trat2',
        'Trat_tot', 'Tperp1', 'Tperp2', 'Tperp_tot', 'Tpar1', 'Tpar2', 'Tpar_tot',
        'Temp_tot', '|qz_p|', 'np1_dpar', 'np2_dpar', 'vp1_x_dpar', 'vp1_y_dpar',
        'vp1_z_dpar', 'vdrift_dpar', 'Trat1_dpar', 'Trat2_dpar', 'Tperp1_dpar', 
        'Tperp2_dpar', 'chi', 'valfven_pfits'
    ]
    for col in cols_to_convert:
        if col in df:
             key = col if col.endswith('_pfits') else col + '_pfits'
             results_np[key] = df[col].to_numpy()
        else:
             print(f"Warning: Column '{col}' not found in df_sf00 during numpy conversion.")

    # Calculate vp1_mag_dpar separately
    if all(c in df for c in ['vp1_x_dpar', 'vp1_y_dpar', 'vp1_z_dpar']):
        results_np['vp1_mag_dpar_pfits'] = np.sqrt(df['vp1_x_dpar']**2 + df['vp1_y_dpar']**2 + df['vp1_z_dpar']**2)
    else:
        print("Warning: Missing columns for vp1_mag_dpar_pfits calculation.")
        
    # Store the potentially modified dataframe as well
    results_np['df_sf00_processed'] = df 

    return df, results_np # Return modified DataFrame and dict of numpy arrays

def calculate_sf01_fits_vars(df_sf01, df_sf00, datetime_spi_sf0a=None):
    """Calculates derived variables from the SF01 FITS dataframe."""
    if df_sf01 is None or df_sf01.empty:
        print("Warning: SF01 FITS DataFrame is empty or None.")
        return pd.DataFrame(), {} 
    if df_sf00 is None or df_sf00.empty:
        print("Warning: SF00 FITS DataFrame needed for SF01 calculations is empty or None.")
        return pd.DataFrame(), {}
        
    results_np = {}
    df = df_sf01.copy()
    df_sf00_copy = df_sf00.copy() # Use a copy of sf00 as well

    # Filtering
    filtered_val_index_sf01 = np.where(
        (df['na'] > 0) & 
        (df['Ta_perp'] > .101) & 
        (df['Trata'] > .101) & 
        (df['Trata'] != 8) & 
        (df['Trata'] != 2.0)
        )[0]
        
    mask_sf01 = df.index.isin(filtered_val_index_sf01)
    columns_to_mask_sf01 = df.columns.difference(['time'])
    df.loc[~mask_sf01, columns_to_mask_sf01] = np.nan
        
    # Datetime conversion
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    datetime_array_sf01 = df['datetime'].dt.to_pydatetime()
    results_np['datetime_array_sf01'] = datetime_array_sf01

    # Upsampling SF01 (if needed)
    if datetime_spi_sf0a is not None and len(datetime_array_sf01) < len(datetime_spi_sf0a):
        print("Upsampling SF01 FITS data...")
        df = upsample_to_match(df, datetime_array_sf01, datetime_spi_sf0a)
        datetime_array_sf01 = df['datetime'].dt.to_pydatetime()
        results_np['datetime_array_sf01'] = datetime_array_sf01
        print(f"SF01 FITS data upsampled to {len(df)} points.")

    # Prepare SF00 data (downsampling if needed)
    # Ensure 'datetime' column exists in sf00 df passed in
    if 'datetime' not in df_sf00_copy.columns:
         print("Error: 'datetime' column missing in input df_sf00 for SF01 calculations.")
         return df, results_np # Return partial results
         
    datetime_array_sf00 = df_sf00_copy['datetime'].dt.to_pydatetime()

    if len(datetime_array_sf01) < len(datetime_array_sf00):
        print("Downsampling SF00 variables for SF01 calculations...")
        vp1_mag_sf00 = df_sf00_copy['vp1_mag'].to_numpy()
        np1_sf00 = df_sf00_copy['np1'].to_numpy()
        np2_sf00 = df_sf00_copy['np2'].to_numpy()
        vdrift_sf00 = df_sf00_copy['vdrift'].to_numpy()

        vp1_mag_ds = downsample_to_match(datetime_array_sf00, vp1_mag_sf00, datetime_array_sf01)
        np1_ds = downsample_to_match(datetime_array_sf00, np1_sf00, datetime_array_sf01)
        np2_ds = downsample_to_match(datetime_array_sf00, np2_sf00, datetime_array_sf01)
        vdrift_ds = downsample_to_match(datetime_array_sf00, vdrift_sf00, datetime_array_sf01)
    else:
        # Ensure columns exist before trying to access
        req_cols = ['vp1_mag', 'np1', 'np2', 'vdrift']
        if not all(col in df_sf00_copy.columns for col in req_cols):
             print(f"Error: Missing required SF00 columns ({req_cols}) for SF01 calculations.")
             return df, results_np
             
        vp1_mag_ds = df_sf00_copy['vp1_mag'].to_numpy()
        np1_ds = df_sf00_copy['np1'].to_numpy()
        np2_ds = df_sf00_copy['np2'].to_numpy()
        vdrift_ds = df_sf00_copy['vdrift'].to_numpy()
        # Ensure lengths match sf01 df if no downsampling occurred
        if len(vp1_mag_ds) != len(df):
             print("Error: Length mismatch between SF01 and SF00 data after potential sampling.")
             # Attempt interpolation or return error
             # For now, return partial
             return df, results_np
             

    # Calculations using potentially downsampled sf00 data
    np_tot_ds = np1_ds + np2_ds
    df['nap_tot'] = np_tot_ds + df['na']
    df['B_mag'] = np.sqrt(df['B_inst_x']**2 + df['B_inst_y']**2 + df['B_inst_z']**2)
    nap_tot_safe = np.where(df['nap_tot'] > 0, df['nap_tot'], np.nan)
    df['valfven_apfits'] = 21.8 * df['B_mag'] / np.sqrt(nap_tot_safe)

    # Calculate vdrift_va_apfits (requires upsampling valfven_apfits back to sf00 cadence)
    valfven_apfits_sf01 = df['valfven_apfits'].to_numpy()
    if len(datetime_array_sf01) < len(datetime_array_sf00):
        valfven_apfits_us = upsample_to_match(datetime_array_sf01, valfven_apfits_sf01, datetime_array_sf00)
    else:
        valfven_apfits_us = valfven_apfits_sf01
        
    # Add to the sf00 dataframe copy (or a results dict)
    if len(valfven_apfits_us) == len(df_sf00_copy):
         # Ensure 'vdrift' exists in the sf00 copy before calculation
         if 'vdrift' in df_sf00_copy.columns:
             valfven_apfits_us_safe = np.where(valfven_apfits_us != 0, valfven_apfits_us, np.nan)
             vdrift_va_apfits = df_sf00_copy['vdrift'] / valfven_apfits_us_safe
             results_np['vdrift_va_apfits'] = vdrift_va_apfits # Store this important result
         else:
              print("Warning: 'vdrift' column missing in df_sf00_copy for vdrift_va_apfits calculation.")
              results_np['vdrift_va_apfits'] = np.full(len(df_sf00_copy), np.nan)
    else:
         print("Warning: Length mismatch when calculating vdrift_va_apfits.")
         results_np['vdrift_va_apfits'] = np.full(len(df_sf00_copy), np.nan)

    # Continue sf01 calculations
    df['va_mag'] = np.sqrt(df['va_x']**2 + df['va_y']**2 + df['va_z']**2)
    df['vdrift_ap1'] = df['va_mag'] - vp1_mag_ds # Use downsampled vp1_mag
    valfven_apfits_sf01_safe = np.where(df['valfven_apfits'] != 0, df['valfven_apfits'], np.nan)
    df['vdrift_va_ap1'] = df['vdrift_ap1'] / valfven_apfits_sf01_safe
    
    np_tot_ds_safe = np.where(np_tot_ds > 0, np_tot_ds, np.nan)
    np1_ds_safe = np.where(np1_ds > 0, np1_ds, np.nan)
    np2_ds_safe = np.where(np2_ds > 0, np2_ds, np.nan)
    df['na/np_tot'] = df['na'] / np_tot_ds_safe
    df['na/np1'] = df['na'] / np1_ds_safe
    df['na/np2'] = df['na'] / np2_ds_safe
    
    Trata_safe = np.where(df['Trata'] != 0, df['Trata'], np.nan)
    df['Tpara'] = df['Ta_perp'] / Trata_safe
    
    beta_denom_a = (1e-5 * df['B_mag'])**2
    beta_denom_a_safe = np.where(beta_denom_a > 0, beta_denom_a, np.nan)
    df['beta_par_a'] = (4.03E-11 * df['na'] * df['Tpara']) / beta_denom_a_safe

    # Convert to numpy arrays for results_np
    cols_to_convert_sf01 = [
        'na', 'na/np_tot', 'na/np1', 'na/np2', 'va_x', 'va_y', 'va_z', 'va_mag',
        'vdrift_ap1', 'vdrift_va_ap1', 'Trata', 'Ta_perp', 'Tpara', 'beta_par_a',
        'na_dpar', 'va_x_dpar', 'va_y_dpar', 'va_z_dpar', 'Trata_dpar',
        'Ta_perp_dpar', 'chi'
    ]
    for col in cols_to_convert_sf01:
        if col in df:
            results_np[col + '_afits'] = df[col].to_numpy()
        else:
            print(f"Warning: Column '{col}' not found in df_sf01 during numpy conversion.")

    if all(c in df for c in ['va_x_dpar', 'va_y_dpar', 'va_z_dpar']):
        results_np['va_mag_dpar_afits'] = np.sqrt(df['va_x_dpar']**2 + df['va_y_dpar']**2 + df['va_z_dpar']**2)
    else:
         print("Warning: Missing columns for va_mag_dpar_afits calculation.")
         
    # Store processed sf01 dataframe
    results_np['df_sf01_processed'] = df

    return df, results_np
