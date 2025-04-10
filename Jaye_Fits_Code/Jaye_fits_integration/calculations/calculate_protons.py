import numpy as np
from scipy import constants

# Assuming get_data, split_vec, time_datetime, store_data, tinterpol, divide are available
try:
    from ..functions import (
        get_data, split_vec, time_datetime, store_data, tinterpol, divide
    )
except ImportError:
    print("Warning: Could not import functions from ..functions for proton calcs.")
    # Define dummy functions or raise error if essential
    def get_data(var): return None
    def split_vec(var): pass
    def time_datetime(t): return []
    def store_data(n, data): pass
    def tinterpol(v1, v2, newname): pass
    def divide(v1, v2, newname): pass

def calculate_spi_sf00_mom_vars():
    """Calculates variables for SPI SF00 Moment data."""
    results = {}

    # Proton temperature anisotropy from Temperature Tensor
    T_Tens = get_data('psp_spi_sf00_T_TENSOR_INST')
    B_spi = get_data('psp_spi_sf00_MAGF_INST')
    dens_spi = get_data('psp_spi_sf00_DENS')
    temp_spi = get_data('psp_spi_sf00_TEMP')
    sun_dist_ = get_data('psp_spi_sf00_SUN_DIST')

    if T_Tens is None or B_spi is None or dens_spi is None or temp_spi is None or sun_dist_ is None:
        print("Warning: Missing required SPI SF00 moment data (T_TENSOR, MAGF, DENS, TEMP, SUN_DIST).")
        return results

    T_XX = T_Tens.y[:,0]
    T_YY = T_Tens.y[:,1]
    T_ZZ = T_Tens.y[:,2]
    T_XY = T_Tens.y[:,3]
    T_XZ = T_Tens.y[:,4]
    T_YZ = T_Tens.y[:,5]
    T_YX = T_XY
    T_ZX = T_XZ
    T_ZY = T_YZ

    B_X = B_spi.y[:,0]
    B_Y = B_spi.y[:,1]
    B_Z = B_spi.y[:,2]
    B_mag_XYZ = np.sqrt(B_X**2 + B_Y**2 + B_Z**2)
    results['B_mag_XYZ_spi'] = B_mag_XYZ # Store Bmag from SPI cadence

    T_parallel=[]
    T_perpendicular=[]
    Anisotropy=[]
    for i in range(len(B_X)):
        Sum_1=B_X[i]*B_X[i]*T_XX[i]
        Sum_2=B_X[i]*B_Y[i]*T_XY[i]
        Sum_3=B_X[i]*B_Z[i]*T_XZ[i]
        Sum_4=B_Y[i]*B_X[i]*T_YX[i]
        Sum_5=B_Y[i]*B_Y[i]*T_YY[i]
        Sum_6=B_Y[i]*B_Z[i]*T_YZ[i]
        Sum_7=B_Z[i]*B_X[i]*T_ZX[i]
        Sum_8=B_Z[i]*B_Y[i]*T_ZY[i]
        Sum_9=B_Z[i]*B_Z[i]*T_ZZ[i]
        # Avoid division by zero if B_mag_XYZ is zero
        b_mag_sq = B_mag_XYZ[i]**2
        if b_mag_sq == 0:
            T_para = np.nan
            T_perp = np.nan
            aniso = np.nan
        else:
            T_para=((Sum_1+Sum_2+Sum_3+Sum_4+Sum_5+Sum_6+Sum_7+Sum_8+Sum_9)/b_mag_sq)
            Trace_Temp=(T_XX[i]+T_YY[i]+T_ZZ[i])
            T_perp=(Trace_Temp-T_para)/2.0
            aniso = T_perp / T_para if T_para != 0 else np.nan
        
        T_parallel.append(T_para)
        T_perpendicular.append(T_perp)
        Anisotropy.append(aniso)

    results['T_parallel_spi'] = np.array(T_parallel)
    results['T_perpendicular_spi'] = np.array(T_perpendicular)
    results['Anisotropy_spi'] = np.array(Anisotropy)

    # Velocity calculations
    split_vec('psp_spi_sf00_VEL_RTN_SUN')
    vr_ = get_data('psp_spi_sf00_VEL_RTN_SUN_x')
    vt_ = get_data('psp_spi_sf00_VEL_RTN_SUN_y')
    vn_ = get_data('psp_spi_sf00_VEL_RTN_SUN_z')

    if vr_ is None or vt_ is None or vn_ is None:
        print("Warning: Missing SPI SF00 velocity components.")
        # Can still calculate other things, but store Nones for velocity dependent vars
        vr, vt, vn, vmag = np.nan, np.nan, np.nan, np.nan
    else:
        vr = vr_.y
        vt = vt_.y
        vn = vn_.y
        vmag = np.sqrt(vr**2 + vt **2 + vn**2)
    
    results['vr_spi'] = vr
    results['vt_spi'] = vt
    results['vn_spi'] = vn
    results['vmag_spi'] = vmag
    results['vr_spi_times'] = vr_.times if vr_ else None # Store time axis too

    # Energy flux calculations
    spi_eflux_v_energy = get_data('psp_spi_sf00_EFLUX_VS_ENERGY')
    spi_eflux_v_theta = get_data('psp_spi_sf00_EFLUX_VS_THETA')
    spi_eflux_v_phi = get_data('psp_spi_sf00_EFLUX_VS_PHI')

    if spi_eflux_v_energy is None or spi_eflux_v_theta is None or spi_eflux_v_phi is None:
        print("Warning: Missing SPI SF00 EFLUX data.")
        # Handle missing flux data gracefully
    else:
        spi_times = spi_eflux_v_energy.times
        results['spi_times'] = spi_times
        datetime_spi = time_datetime(spi_times)
        results['datetime_spi'] = datetime_spi
        
        # Energy vs Energy
        spi_nrg_flux = spi_eflux_v_energy.y
        spi_nrg_vals = spi_eflux_v_energy.v
        results['spi_nrg_flux'] = spi_nrg_flux
        results['spi_nrg_vals'] = spi_nrg_vals
        with np.errstate(divide='ignore'):
            log_spi_nrg_flux = np.log10(spi_nrg_flux)
        log_spi_nrg_flux[np.isinf(log_spi_nrg_flux)] = np.nan
        results['log_spi_nrg_flux'] = log_spi_nrg_flux
        
        times_spi_repeat = np.repeat(np.expand_dims(datetime_spi,1),32,1)
        results['times_spi_repeat'] = times_spi_repeat

        weights_nrg = np.ma.masked_invalid(spi_nrg_flux)
        if not np.all(weights_nrg.mask):
             results['centroids_spi_nrg'] = np.ma.average(spi_nrg_vals, weights=weights_nrg, axis=1)
        else:
            results['centroids_spi_nrg'] = np.full(spi_nrg_vals.shape[0], np.nan)

        # Energy vs Theta
        spi_nrg_flux_theta = spi_eflux_v_theta.y
        spi_nrg_vals_theta = spi_eflux_v_theta.v
        results['spi_nrg_flux_theta'] = spi_nrg_flux_theta
        results['spi_nrg_vals_theta'] = spi_nrg_vals_theta
        with np.errstate(divide='ignore'):
             log_spi_nrg_flux_theta = np.log10(spi_nrg_flux_theta)
        log_spi_nrg_flux_theta[np.isinf(log_spi_nrg_flux_theta)] = np.nan
        results['log_spi_nrg_flux_theta'] = log_spi_nrg_flux_theta

        times_spi_repeat_angle = np.repeat(np.expand_dims(datetime_spi,1),8,1) 
        results['times_spi_repeat_angle'] = times_spi_repeat_angle

        weights_theta = np.ma.masked_invalid(spi_nrg_flux_theta)
        if not np.all(weights_theta.mask):
            results['centroids_spi_theta'] = np.ma.average(spi_nrg_vals_theta, weights=weights_theta, axis=1)
        else:
            results['centroids_spi_theta'] = np.full(spi_nrg_vals_theta.shape[0], np.nan)

        # Energy vs Phi
        spi_nrg_flux_phi = spi_eflux_v_phi.y
        spi_nrg_vals_phi = spi_eflux_v_phi.v
        results['spi_nrg_flux_phi'] = spi_nrg_flux_phi
        results['spi_nrg_vals_phi'] = spi_nrg_vals_phi
        with np.errstate(divide='ignore'):
             log_spi_nrg_flux_phi = np.log10(spi_nrg_flux_phi)
        log_spi_nrg_flux_phi[np.isinf(log_spi_nrg_flux_phi)] = np.nan
        results['log_spi_nrg_flux_phi'] = log_spi_nrg_flux_phi

        weights_phi = np.ma.masked_invalid(spi_nrg_flux_phi)
        if not np.all(weights_phi.mask):
             results['centroids_spi_phi'] = np.ma.average(spi_nrg_vals_phi, weights=weights_phi, axis=1)
        else:
             results['centroids_spi_phi'] = np.full(spi_nrg_vals_phi.shape[0], np.nan)

    # Plasma Parameters
    dens_spi_y = dens_spi.y
    temp_spi_y = temp_spi.y
    b_mag_spi = B_mag_XYZ # Use the Bmag calculated earlier at SPI cadence
    results['dens_spi'] = dens_spi_y
    results['temp_spi'] = temp_spi_y

    # The alfven speed (avoid division by zero or sqrt of negative)
    dens_spi_y_safe = np.where(dens_spi_y > 0, dens_spi_y, np.nan)
    v_alfven_spi = 21.8 * b_mag_spi / np.sqrt(dens_spi_y_safe)
    results['v_alfven_spi'] = v_alfven_spi

    # Alfven Mach number
    v_sw_spi = vmag # Use vmag calculated earlier
    M_alfven_spi = v_sw_spi / v_alfven_spi
    results['M_alfven_spi'] = M_alfven_spi

    # Beta calculations (handle potential division by zero in Bmag)
    b_mag_spi_sq = b_mag_spi**2
    beta_denom = (1e-5 * b_mag_spi)**2
    beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)

    beta_ppar_spi = (4.03E-11 * dens_spi_y * results['T_parallel_spi']) / beta_denom_safe
    beta_pperp_spi = (4.03E-11 * dens_spi_y * results['T_perpendicular_spi']) / beta_denom_safe
    beta_p_spi = (4.03E-11 * dens_spi_y * temp_spi_y) / beta_denom_safe
    results['beta_ppar_spi'] = beta_ppar_spi
    results['beta_pperp_spi'] = beta_pperp_spi
    results['beta_p_spi'] = beta_p_spi

    # Pressure calculations
    pressure_ppar_spi = 1.602E-4 * dens_spi_y * results['T_parallel_spi']
    pressure_pperp_spi = 1.602E-4 * dens_spi_y * results['T_perpendicular_spi']
    pressure_p_spi = 1.602E-4 * temp_spi_y * dens_spi_y
    results['pressure_ppar_spi'] = pressure_ppar_spi
    results['pressure_pperp_spi'] = pressure_pperp_spi
    results['pressure_p_spi'] = pressure_p_spi

    # Magnetic pressure
    mu_0 = constants.mu_0
    pmag_spi = (b_mag_spi_sq) / (2 * mu_0)
    pmag_spi = pmag_spi * 1e9 # Convert to nPa
    results['pmag_spi'] = pmag_spi

    # Total pressure
    pressure_tot_mag_p = pressure_p_spi + pmag_spi
    results['pressure_tot_mag_p_spi'] = pressure_tot_mag_p

    # Distance from sun
    sun_dist_km = sun_dist_.y
    sun_dist_rsun = sun_dist_km / 695700.0
    results['sun_dist_km'] = sun_dist_km
    results['sun_dist_rsun'] = sun_dist_rsun
    
    return results

def calculate_spi_sf0a_mom_vars():
    """Calculates variables for SPI SF0A Moment data (Alphas)."""
    results = {}

    # Temperature Tensor and Magnetic Field
    T_Tens_sf0a = get_data('psp_spi_sf0a_T_TENSOR_INST')
    B_spi_sf0a = get_data('psp_spi_sf0a_MAGF_INST')
    dens_spi_sf0a = get_data('psp_spi_sf0a_DENS')
    temp_spi_sf0a = get_data('psp_spi_sf0a_TEMP')
    sun_dist_sf0a_ = get_data('psp_spi_sf0a_SUN_DIST')

    if T_Tens_sf0a is None or B_spi_sf0a is None or dens_spi_sf0a is None or temp_spi_sf0a is None or sun_dist_sf0a_ is None:
        print("Warning: Missing required SPI SF0A moment data.")
        return results

    T_XX_sf0a = T_Tens_sf0a.y[:,0]
    T_YY_sf0a = T_Tens_sf0a.y[:,1]
    T_ZZ_sf0a = T_Tens_sf0a.y[:,2]
    T_XY_sf0a = T_Tens_sf0a.y[:,3]
    T_XZ_sf0a = T_Tens_sf0a.y[:,4]
    T_YZ_sf0a = T_Tens_sf0a.y[:,5]
    T_YX_sf0a = T_XY_sf0a
    T_ZX_sf0a = T_XZ_sf0a
    T_ZY_sf0a = T_YZ_sf0a

    B_X_sf0a = B_spi_sf0a.y[:,0]
    B_Y_sf0a = B_spi_sf0a.y[:,1]
    B_Z_sf0a = B_spi_sf0a.y[:,2]
    B_mag_XYZ_sf0a = np.sqrt(B_X_sf0a**2 + B_Y_sf0a**2 + B_Z_sf0a**2)
    results['B_mag_XYZ_sf0a'] = B_mag_XYZ_sf0a

    # Anisotropy
    T_parallel_sf0a=[]
    T_perpendicular_sf0a=[]
    Anisotropy_sf0a=[]
    for i in range(len(B_X_sf0a)):
        Sum_1_sf0a=B_X_sf0a[i]*B_X_sf0a[i]*T_XX_sf0a[i]
        Sum_2_sf0a=B_X_sf0a[i]*B_Y_sf0a[i]*T_XY_sf0a[i]
        Sum_3_sf0a=B_X_sf0a[i]*B_Z_sf0a[i]*T_XZ_sf0a[i]
        Sum_4_sf0a=B_Y_sf0a[i]*B_X_sf0a[i]*T_YX_sf0a[i]
        Sum_5_sf0a=B_Y_sf0a[i]*B_Y_sf0a[i]*T_YY_sf0a[i]
        Sum_6_sf0a=B_Y_sf0a[i]*B_Z_sf0a[i]*T_YZ_sf0a[i]
        Sum_7_sf0a=B_Z_sf0a[i]*B_X_sf0a[i]*T_ZX_sf0a[i]
        Sum_8_sf0a=B_Z_sf0a[i]*B_Y_sf0a[i]*T_ZY_sf0a[i]
        Sum_9_sf0a=B_Z_sf0a[i]*B_Z_sf0a[i]*T_ZZ_sf0a[i]
        b_mag_sq = B_mag_XYZ_sf0a[i]**2
        if b_mag_sq == 0:
            T_para_sf0a = np.nan
            T_perp_sf0a = np.nan
            aniso_sf0a = np.nan
        else:
            T_para_sf0a=((Sum_1_sf0a+Sum_2_sf0a+Sum_3_sf0a+Sum_4_sf0a+Sum_5_sf0a+Sum_6_sf0a+Sum_7_sf0a+Sum_8_sf0a+Sum_9_sf0a)/b_mag_sq)
            Trace_Temp_sf0a=(T_XX_sf0a[i]+T_YY_sf0a[i]+T_ZZ_sf0a[i])
            T_perp_sf0a=(Trace_Temp_sf0a-T_para_sf0a)/2.0
            aniso_sf0a = T_perp_sf0a / T_para_sf0a if T_para_sf0a != 0 else np.nan

        T_parallel_sf0a.append(T_para_sf0a)
        T_perpendicular_sf0a.append(T_perp_sf0a)
        Anisotropy_sf0a.append(aniso_sf0a)

    results['T_parallel_sf0a'] = np.array(T_parallel_sf0a)
    results['T_perpendicular_sf0a'] = np.array(T_perpendicular_sf0a)
    results['Anisotropy_sf0a'] = np.array(Anisotropy_sf0a)

    # Velocity
    split_vec('psp_spi_sf0a_VEL_RTN_SUN')
    vr_sf0a_ = get_data('psp_spi_sf0a_VEL_RTN_SUN_x')
    vt_sf0a_ = get_data('psp_spi_sf0a_VEL_RTN_SUN_y')
    vn_sf0a_ = get_data('psp_spi_sf0a_VEL_RTN_SUN_z')

    if vr_sf0a_ is None or vt_sf0a_ is None or vn_sf0a_ is None:
        print("Warning: Missing SPI SF0A velocity components.")
        vr_sf0a, vt_sf0a, vn_sf0a, vmag_sf0a = np.nan, np.nan, np.nan, np.nan
    else:
        vr_sf0a = vr_sf0a_.y
        vt_sf0a = vt_sf0a_.y
        vn_sf0a = vn_sf0a_.y
        vmag_sf0a = np.sqrt(vr_sf0a**2 + vt_sf0a **2 + vn_sf0a**2)
    
    results['vr_sf0a'] = vr_sf0a
    results['vt_sf0a'] = vt_sf0a
    results['vn_sf0a'] = vn_sf0a
    results['vmag_sf0a'] = vmag_sf0a
    results['vr_sf0a_times'] = vr_sf0a_.times if vr_sf0a_ else None

    # Energy Flux
    spi_sf0a_eflux_v_energy = get_data('psp_spi_sf0a_EFLUX_VS_ENERGY')
    spi_sf0a_eflux_v_theta = get_data('psp_spi_sf0a_EFLUX_VS_THETA')
    spi_sf0a_eflux_v_phi = get_data('psp_spi_sf0a_EFLUX_VS_PHI')

    if spi_sf0a_eflux_v_energy is None or spi_sf0a_eflux_v_theta is None or spi_sf0a_eflux_v_phi is None:
         print("Warning: Missing SPI SF0A EFLUX data.")
    else:
        spi_sf0a_times = spi_sf0a_eflux_v_energy.times
        results['spi_sf0a_times'] = spi_sf0a_times
        datetime_spi_sf0a = time_datetime(spi_sf0a_times)
        results['datetime_spi_sf0a'] = datetime_spi_sf0a
        
        spi_sf0a_nrg_flux = spi_sf0a_eflux_v_energy.y
        spi_sf0a_nrg_vals = spi_sf0a_eflux_v_energy.v
        results['spi_sf0a_nrg_flux'] = spi_sf0a_nrg_flux
        results['spi_sf0a_nrg_vals'] = spi_sf0a_nrg_vals
        with np.errstate(divide='ignore'):
            log_spi_sf0a_nrg_flux = np.log10(spi_sf0a_nrg_flux)
        log_spi_sf0a_nrg_flux[np.isinf(log_spi_sf0a_nrg_flux)] = np.nan
        results['log_spi_sf0a_nrg_flux'] = log_spi_sf0a_nrg_flux
        
        times_spi_sf0a_repeat = np.repeat(np.expand_dims(datetime_spi_sf0a,1),32,1)
        results['times_spi_sf0a_repeat'] = times_spi_sf0a_repeat

        weights_nrg_a = np.ma.masked_invalid(spi_sf0a_nrg_flux)
        if not np.all(weights_nrg_a.mask):
            results['centroids_spi_sf0a_nrg'] = np.ma.average(spi_sf0a_nrg_vals, weights=weights_nrg_a, axis=1)
        else:
            results['centroids_spi_sf0a_nrg'] = np.full(spi_sf0a_nrg_vals.shape[0], np.nan)

        spi_sf0a_nrg_flux_theta = spi_sf0a_eflux_v_theta.y
        spi_sf0a_nrg_vals_theta = spi_sf0a_eflux_v_theta.v
        results['spi_sf0a_nrg_flux_theta'] = spi_sf0a_nrg_flux_theta
        results['spi_sf0a_nrg_vals_theta'] = spi_sf0a_nrg_vals_theta
        with np.errstate(divide='ignore'):
            log_spi_sf0a_nrg_flux_theta = np.log10(spi_sf0a_nrg_flux_theta)
        log_spi_sf0a_nrg_flux_theta[np.isinf(log_spi_sf0a_nrg_flux_theta)] = np.nan
        results['log_spi_sf0a_nrg_flux_theta'] = log_spi_sf0a_nrg_flux_theta

        times_spi_sf0a_repeat_angle = np.repeat(np.expand_dims(datetime_spi_sf0a,1),8,1)
        results['times_spi_sf0a_repeat_angle'] = times_spi_sf0a_repeat_angle

        weights_theta_a = np.ma.masked_invalid(spi_sf0a_nrg_flux_theta)
        if not np.all(weights_theta_a.mask):
             results['centroids_spi_sf0a_theta'] = np.ma.average(spi_sf0a_nrg_vals_theta, weights=weights_theta_a, axis=1)
        else:
             results['centroids_spi_sf0a_theta'] = np.full(spi_sf0a_nrg_vals_theta.shape[0], np.nan)

        spi_sf0a_nrg_flux_phi = spi_sf0a_eflux_v_phi.y
        spi_sf0a_nrg_vals_phi = spi_sf0a_eflux_v_phi.v
        results['spi_sf0a_nrg_flux_phi'] = spi_sf0a_nrg_flux_phi
        results['spi_sf0a_nrg_vals_phi'] = spi_sf0a_nrg_vals_phi
        with np.errstate(divide='ignore'):
            log_spi_sf0a_nrg_flux_phi = np.log10(spi_sf0a_nrg_flux_phi)
        log_spi_sf0a_nrg_flux_phi[np.isinf(log_spi_sf0a_nrg_flux_phi)] = np.nan
        results['log_spi_sf0a_nrg_flux_phi'] = log_spi_sf0a_nrg_flux_phi

        weights_phi_a = np.ma.masked_invalid(spi_sf0a_nrg_flux_phi)
        if not np.all(weights_phi_a.mask):
            results['centroids_spi_sf0a_phi'] = np.ma.average(spi_sf0a_nrg_vals_phi, weights=weights_phi_a, axis=1)
        else:
             results['centroids_spi_sf0a_phi'] = np.full(spi_sf0a_nrg_vals_phi.shape[0], np.nan)

    # Plasma Parameters
    dens_spi_sf0a_y = dens_spi_sf0a.y
    temp_spi_sf0a_y = temp_spi_sf0a.y
    b_mag_spi_sf0a = B_mag_XYZ_sf0a
    results['dens_spi_sf0a'] = dens_spi_sf0a_y
    results['temp_spi_sf0a'] = temp_spi_sf0a_y

    dens_spi_sf0a_y_safe = np.where(dens_spi_sf0a_y > 0, dens_spi_sf0a_y, np.nan)
    v_alfven_spi_sf0a = 21.8 * b_mag_spi_sf0a / np.sqrt(dens_spi_sf0a_y_safe)
    results['v_alfven_spi_sf0a'] = v_alfven_spi_sf0a

    M_alfven_spi_sf0a = vmag_sf0a / v_alfven_spi_sf0a
    results['M_alfven_spi_sf0a'] = M_alfven_spi_sf0a

    b_mag_spi_sf0a_sq = b_mag_spi_sf0a**2
    beta_denom_sf0a = (1e-5 * b_mag_spi_sf0a)**2
    beta_denom_sf0a_safe = np.where(beta_denom_sf0a > 0, beta_denom_sf0a, np.nan)

    beta_ppar_spi_sf0a = (4.03E-11 * dens_spi_sf0a_y * results['T_parallel_sf0a']) / beta_denom_sf0a_safe
    beta_pperp_spi_sf0a = (4.03E-11 * dens_spi_sf0a_y * results['T_perpendicular_sf0a']) / beta_denom_sf0a_safe
    beta_p_spi_sf0a = (4.03E-11 * dens_spi_sf0a_y * temp_spi_sf0a_y) / beta_denom_sf0a_safe
    results['beta_ppar_spi_sf0a'] = beta_ppar_spi_sf0a
    results['beta_pperp_spi_sf0a'] = beta_pperp_spi_sf0a
    results['beta_p_spi_sf0a'] = beta_p_spi_sf0a

    pressure_ppar_spi_sf0a = 1.602E-4 * dens_spi_sf0a_y * results['T_parallel_sf0a']
    pressure_pperp_spi_sf0a = 1.602E-4 * dens_spi_sf0a_y * results['T_perpendicular_sf0a']
    pressure_p_spi_sf0a = 1.602E-4 * temp_spi_sf0a_y * dens_spi_sf0a_y
    results['pressure_ppar_spi_sf0a'] = pressure_ppar_spi_sf0a
    results['pressure_pperp_spi_sf0a'] = pressure_pperp_spi_sf0a
    results['pressure_p_spi_sf0a'] = pressure_p_spi_sf0a

    mu_0 = constants.mu_0
    pmag_spi_sf0a = (b_mag_spi_sf0a_sq) / (2 * mu_0)
    pmag_spi_sf0a = pmag_spi_sf0a * 1e9 # nPa
    results['pmag_spi_sf0a'] = pmag_spi_sf0a

    pressure_tot_mag_p_sf0a = pressure_p_spi_sf0a + pmag_spi_sf0a
    results['pressure_tot_mag_p_sf0a'] = pressure_tot_mag_p_sf0a

    sun_dist_sf0a_km = sun_dist_sf0a_.y
    sun_dist_sf0a_rsun = sun_dist_sf0a_km / 695700.0
    results['sun_dist_sf0a_km'] = sun_dist_sf0a_km
    results['sun_dist_sf0a_rsun'] = sun_dist_sf0a_rsun

    return results

def calculate_proton_alpha_combined_vars(sf00_results, sf0a_results):
    """Calculates combined proton-alpha variables."""
    results = {}
    # Check if essential inputs are present
    if not all(k in sf00_results for k in ['vr_spi_times', 'vmag_spi', 'v_alfven_spi']) or \
       not all(k in sf0a_results for k in ['vr_sf0a_times', 'vmag_sf0a']): 
        print("Warning: Missing data required for combined proton-alpha calcs.")
        return results

    # Density ratio
    # Need to ensure data exists before calling divide
    if get_data('psp_spi_sf0a_DENS') is not None and get_data('psp_spi_sf00_DENS') is not None:
        divide('psp_spi_sf0a_DENS','psp_spi_sf00_DENS','Na/Np')
        na_div_np_ = get_data('Na/Np')
        if na_div_np_:
            results['na_div_np'] = na_div_np_.y
    
    # Alpha-proton drift speed
    store_data('|Vsw|', data={'x': sf00_results['vr_spi_times'], 'y': sf00_results['vmag_spi']})
    store_data('|Valpha|', data={'x': sf0a_results['vr_sf0a_times'], 'y': sf0a_results['vmag_sf0a']})
    
    tinterpol('|Vsw|', '|Valpha|', newname='va-vp')
    vdrift_ap_ = get_data('va-vp')
    if vdrift_ap_:
        results['vdrift_ap'] = vdrift_ap_.y

        # Normalize by Alfven speed
        store_data('valfven_spi', data={'x': sf00_results['vr_spi_times'], 'y': sf00_results['v_alfven_spi']})
        divide('va-vp','valfven_spi','va-vp/vA')
        vdrift_ap_va_ = get_data('va-vp/vA')
        if vdrift_ap_va_:
            results['vdrift_ap_va'] = vdrift_ap_va_.y

    # Temperature ratio
    if get_data('psp_spi_sf0a_TEMP') is not None and get_data('psp_spi_sf00_TEMP') is not None:
        divide('psp_spi_sf0a_TEMP','psp_spi_sf00_TEMP','Ta/Tp')
        ta_div_tp_ = get_data('Ta/Tp')
        if ta_div_tp_:
            results['ta_div_tp'] = ta_div_tp_.y
            
    return results
