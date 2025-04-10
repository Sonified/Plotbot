import numpy as np
import pandas as pd

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


def calculate_proton_fits_vars(df_sf00, vmag_spi=None, datetime_spi=None):
    """
    Calculates derived variables from the SF00 FITS dataframe.

    This function takes the raw FITS parameters from an SF00 CSV file,
    applies filtering, calculates numerous derived plasma parameters 
    (temperatures, velocities, betas, Alfven speed, Mach numbers, heat flux, etc.),
    and returns both the processed DataFrame and a dictionary containing
    the calculated variables as NumPy arrays, typically with a '_pfits' suffix.

    Args:
        df_sf00 (pd.DataFrame): DataFrame containing the raw data from an SF00 file.
                                Must include columns like 'np1', 'np2', 'Tperp1', 'Trat1',
                                'vdrift', 'B_inst_x', 'time', etc.
        vmag_spi (np.ndarray, optional): Array of solar wind speed magnitudes from
                                         SPI moments, used for Mach number calculation.
                                         Must match the length of df_sf00 after filtering/upsampling.
                                         Defaults to None.
        datetime_spi (np.ndarray, optional): Array of datetime objects corresponding to
                                             vmag_spi, used for potential upsampling.
                                             Defaults to None.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: The input DataFrame with added columns for calculated variables.
            - dict: A dictionary where keys are variable names (often ending in '_pfits')
                    and values are the corresponding NumPy arrays of calculated data.
                    Includes 'datetime_array_sf00' with the final datetime objects.
    """
    if df_sf00 is None or df_sf00.empty:
        print("Warning: SF00 FITS DataFrame is empty or None.")
        return pd.DataFrame(), {} # Return empty DataFrame and dict
    
    results_np = {}
    df = df_sf00.copy() # Work on a copy

    # Filtering (consider making thresholds arguments)
    # Define filters based on reasonable physical expectations or known issues
    filter_conditions = (
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
    )
    
    # Apply the filter: Find indices where conditions are true
    filtered_val_index_sf00 = np.where(filter_conditions)[0]
    
    # Create a boolean mask for easy application
    mask_sf00 = df.index.isin(filtered_val_index_sf00)
    
    # Apply NaN mask to all columns except 'time' where the mask is False
    columns_to_mask_sf00 = df.columns.difference(['time'])
    df.loc[~mask_sf00, columns_to_mask_sf00] = np.nan

    # Datetime conversion
    # Convert epoch time (assuming seconds since epoch) to datetime objects
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    # Store python datetime objects for potential use elsewhere
    datetime_array = df['datetime'].dt.to_pydatetime()
    results_np['datetime_array_sf00'] = datetime_array 

    # Upsampling (Optional - If SPI moment data has higher cadence)
    # This section is currently commented out as upsampling functions are not fully integrated/tested here
    # if datetime_spi is not None and len(datetime_array) < len(datetime_spi):
    #     print("Upsampling SF00 FITS data...")
    #     try:
    #         from ..functions import upsample_to_match # Assumes this function exists and works
    #         df = upsample_to_match(df, datetime_array, datetime_spi)
    #         # Recalculate datetime_array after upsampling
    #         datetime_array = df['datetime'].dt.to_pydatetime()
    #         results_np['datetime_array_sf00'] = datetime_array
    #         print(f"SF00 FITS data upsampled to {len(df)} points.")
    #     except ImportError:
    #         print("Warning: Upsampling function not available. Skipping upsampling.")
    #     except Exception as e:
    #         print(f"Error during upsampling: {e}. Skipping upsampling.")

    # Add moment velocity if available
    if vmag_spi is not None:
        if len(vmag_spi) == len(df):
             df['vsw_mom'] = vmag_spi
        else:
             # If lengths don't match, likely due to filtering/sampling differences
             print(f"Warning: Length mismatch between vmag_spi ({len(vmag_spi)}) and df_sf00 ({len(df)}). Cannot assign vsw_mom.")
             df['vsw_mom'] = np.nan # Assign NaN if lengths mismatch
    else:
        df['vsw_mom'] = np.nan # Assign NaN if vmag_spi not provided

    # --- Derived Parameter Calculations ---

    # Calculate magnitudes and unit vectors
    df['vp1_mag'] = np.sqrt(df['vp1_x']**2 + df['vp1_y']**2 + df['vp1_z']**2) 
    # Ensure B_mag calculation handles potential NaNs gracefully
    with np.errstate(invalid='ignore'): # Ignore warnings for sqrt(NaN)
        df['B_mag'] = np.sqrt(df['B_inst_x']**2 + df['B_inst_y']**2 + df['B_inst_z']**2)
    
    # Calculate magnetic field unit vector components (handle potential division by zero/NaN)
    with np.errstate(divide='ignore', invalid='ignore'):
        b_mag_safe = np.where(df['B_mag'] != 0, df['B_mag'], np.nan) # Avoid division by zero
        df['bhat_x'] = df['B_inst_x'] / b_mag_safe
        df['bhat_y'] = df['B_inst_y'] / b_mag_safe
        df['bhat_z'] = df['B_inst_z'] / b_mag_safe
    
    # Total density and temperatures
    df['n_tot'] = df['np1'] + df['np2']
    with np.errstate(divide='ignore', invalid='ignore'):
        n_tot_safe = np.where(df['n_tot'] != 0, df['n_tot'], np.nan)
        df['Tperp_tot'] = (df['np1'] * df['Tperp1'] + df['np2'] * df['Tperp2']) / n_tot_safe
        
        # Calculate parallel temperatures from ratios (handle division by zero/NaN)
        Trat1_safe = np.where(df['Trat1'] != 0, df['Trat1'], np.nan)
        Trat2_safe = np.where(df['Trat2'] != 0, df['Trat2'], np.nan)
        df['Tpar1'] = df['Tperp1'] / Trat1_safe
        df['Tpar2'] = df['Tperp2'] / Trat2_safe
        
        # Calculate total parallel temperature (includes drift term)
        drift_term = (df['np1'] * df['np2'] / n_tot_safe) * m * (df['vdrift']**2)
        df['Tpar_tot'] = (df['np1'] * df['Tpar1'] + df['np2'] * df['Tpar2'] + drift_term) / n_tot_safe
        
        # Calculate total temperature ratio and average temperature
        Tpar_tot_safe = np.where(df['Tpar_tot'] != 0, df['Tpar_tot'], np.nan)
        df['Trat_tot'] = df['Tperp_tot'] / Tpar_tot_safe
        df['Temp_tot'] = (2 * df['Tperp_tot'] + df['Tpar_tot']) / 3
    
    # Center-of-mass velocity
    with np.errstate(divide='ignore', invalid='ignore'):
        n_tot_safe = np.where(df['n_tot'] != 0, df['n_tot'], np.nan)
        frac_p2 = df['np2'] / n_tot_safe
        df['vcm_x'] = df['vp1_x'] + frac_p2 * df['vdrift'] * df['bhat_x']
        df['vcm_y'] = df['vp1_y'] + frac_p2 * df['vdrift'] * df['bhat_y']
        df['vcm_z'] = df['vp1_z'] + frac_p2 * df['vdrift'] * df['bhat_z']
    df['vcm_mag'] = np.sqrt(df['vcm_x']**2 + df['vcm_y']**2 + df['vcm_z']**2)

    # Beam velocity (vp2)
    df['vp2_x'] = df['vp1_x'] + df['vdrift'] * df['bhat_x']
    df['vp2_y'] = df['vp1_y'] + df['vdrift'] * df['bhat_y']
    df['vp2_z'] = df['vp1_z'] + df['vdrift'] * df['bhat_z']
    df['vp2_mag'] = np.sqrt(df['vp2_x']**2 + df['vp2_y']**2 + df['vp2_z']**2)

    # Heat flux calculation (handle potential NaNs)
    with np.errstate(divide='ignore', invalid='ignore'):
        vt1perp2 = 2 * df['Tperp1'] / m 
        vt2perp2 = 2 * df['Tperp2'] / m 
        vt1par2 = 2 * df['Tpar1'] / m 
        vt2par2 = 2 * df['Tpar2'] / m 
        fac = 1.602E-10 # Conversion factor to W/m^2
        n_tot_safe = np.where(df['n_tot'] != 0, df['n_tot'], np.nan)
        density_term = (df['np1'] * df['np2']) / n_tot_safe
        temp_diff_term = 1.5 * (vt2par2 - vt1par2)
        drift_squared_term = df['vdrift']**2 * (df['np1']**2 - df['np2']**2) / (n_tot_safe**2)
        perp_temp_diff = (vt2perp2 - vt1perp2)
        
        df['qz_p'] = fac * 0.5 * m * density_term * df['vdrift'] * (temp_diff_term + drift_squared_term + perp_temp_diff)
        df['|qz_p|'] = np.abs(df['qz_p'])

    # Normalized heat flux (handle potential division by zero/NaN)
    with np.errstate(divide='ignore', invalid='ignore'):
        n_tot_safe = np.where(df['n_tot'] > 0, df['n_tot'], np.nan)
        vt_perp_tot_sq = 2 * (df['np1'] * df['Tperp1'] + df['np2'] * df['Tperp2']) / (m * n_tot_safe)
        vt_par_tot_sq = 2 * (df['np1'] * df['Tpar1']+ df['np2'] * df['Tpar2'] + m * df['vdrift']**2 * (df['np1'] * df['np2'])/n_tot_safe) / (m * n_tot_safe)
        
        vt_perp_tot = np.sqrt(vt_perp_tot_sq)
        vt_par_tot = np.sqrt(vt_par_tot_sq)
        
        denom_perp = m * n_tot_safe * vt_perp_tot**3
        denom_par = m * n_tot_safe * vt_par_tot**3
        
        denom_perp_safe = np.where(denom_perp != 0, denom_perp, np.nan)
        denom_par_safe = np.where(denom_par != 0, denom_par, np.nan)

        df['qz_p_perp'] = df['qz_p'] / denom_perp_safe
        df['qz_p_par'] = df['qz_p'] / denom_par_safe

    # Alfven speed, Mach numbers, Beta (handle potential division by zero/NaN)
    with np.errstate(divide='ignore', invalid='ignore'):
        n_tot_safe = np.where(df['n_tot'] > 0, df['n_tot'], np.nan)
        df['valfven'] = 21.8 * df['B_mag'] / np.sqrt(n_tot_safe) # Note: Renamed to remove _pfits suffix internally
        
        valfven_safe = np.where(df['valfven'] != 0, df['valfven'], np.nan)
        df['vdrift_va'] = df['vdrift'] / valfven_safe
        df['Vcm_mach'] = df['vcm_mag'] / valfven_safe
        df['Vp1_mach'] = df['vp1_mag'] / valfven_safe
        df['vsw_mach'] = df['vsw_mom'] / valfven_safe # Based on SPI moment speed if available

        # Plasma Beta calculations
        beta_denom = (1e-5 * df['B_mag'])**2
        beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)
        df['beta_ppar'] = (4.03E-11 * n_tot_safe * df['Tpar_tot']) / beta_denom_safe
        df['beta_pperp'] = (4.03E-11 * n_tot_safe * df['Tperp_tot']) / beta_denom_safe
        # Individual component betas (might not be needed in final output but calculated here)
        df['beta_par_p1'] = (4.03E-11 * df['np1'] * df['Tpar1']) / beta_denom_safe
        df['beta_par_p2'] = (4.03E-11 * df['np2'] * df['Tpar2']) / beta_denom_safe
        df['beta_perp_p1'] = (4.03E-11 * df['np1'] * df['Tperp1']) / beta_denom_safe
        df['beta_perp_p2'] = (4.03E-11 * df['np2'] * df['Tperp2']) / beta_denom_safe
        df['beta_p_tot'] = np.sqrt(df['beta_ppar']**2 + df['beta_pperp']**2) # Total proton beta magnitude

    # Hammerhead diagnostic
    with np.errstate(divide='ignore', invalid='ignore'):
        Trat_tot_safe = np.where(df['Trat_tot'] != 0, df['Trat_tot'], np.nan)
        Tperp1_safe = np.where(df['Tperp1'] != 0, df['Tperp1'], np.nan)
        df['ham_param'] = (df['Tperp2'] / Tperp1_safe) / Trat_tot_safe
    
    #-------------------- Prepare Output Dictionary --------------------
    # Define the final columns needed for the output dictionary
    # Use the internal names calculated above (without _pfits suffix yet)
    cols_to_output = [
        'valfven', 'beta_ppar', 'beta_pperp', 'np1', 'np2', 'vp1_x', 'vp1_y', 
        'vp1_z', 'vp1_mag', 'vdrift', 'Tperp1', 'Tperp2', 'Trat1', 'Trat2', 
        'qz_p', 'ham_param',
        # Add other derived variables if needed by the proton_fits_class
        'n_tot', 'vcm_x', 'vcm_y', 'vcm_z', 'vcm_mag', 'Tperp_tot', 
        'Tpar1', 'Tpar2', 'Tpar_tot', 'Trat_tot', 'Temp_tot', '|qz_p|',
        'vdrift_va', 'Vcm_mach', 'Vp1_mach', 'vsw_mach', 'beta_p_tot',
        # Include dpar columns if they exist and are needed (check if they are calculated/present)
        # 'np1_dpar', 'np2_dpar', 'vp1_x_dpar', 'vp1_y_dpar', 'vp1_z_dpar', 
        # 'vdrift_dpar', 'Trat1_dpar', 'Trat2_dpar', 'Tperp1_dpar', 'Tperp2_dpar'
        # Removed 'chi_p' as it's handled internally by the class now
    ]
    
    # Add dpar columns to output if they exist in the DataFrame
    dpar_cols = [col for col in df.columns if '_dpar' in col]
    cols_to_output.extend(dpar_cols)
    
    # Create the NumPy results dictionary, adding '_pfits' suffix
    for col in cols_to_output:
        if col in df.columns:
            # Add suffix, except for datetime array which is handled separately
            if col != 'datetime_array_sf00':
                results_np[f"{col}_pfits"] = df[col].to_numpy()
        else:
            print(f"Warning: Column '{col}' defined in cols_to_output but not found in DataFrame.")
    
    # Ensure datetime_array is added if not already present
    if 'datetime_array_sf00' not in results_np and 'datetime_array_sf00' in locals():
         results_np['datetime_array_sf00'] = datetime_array
    elif 'datetime_array_sf00' not in results_np:
         print("Warning: datetime_array_sf00 could not be added to results_np.")

    # Return both the processed DataFrame and the NumPy dictionary
    return df, results_np

def calculate_sf01_fits_vars(df_sf01, df_sf00_processed, datetime_spi_sf0a=None):
    """
    Calculates derived variables from the SF01 (alpha particle) FITS dataframe,
    // ... existing code ...
    """
    # ... existing code ...

    # ... rest of the function ...

    # ... return the processed DataFrame and the NumPy dictionary ...

    return df_sf01, results_np 