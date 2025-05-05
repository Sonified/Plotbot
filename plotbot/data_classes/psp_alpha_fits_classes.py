#plotbot/data_classes/psp_alpha_fits_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

# Define constants if needed (e.g., mass, physical constants for future calculations)
# from scipy.constants import physical_constants # Example

# Import our custom managers (CHECK PATHS)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
# Import dependencies if needed later for calculations
# from ..get_data import get_data 
from .psp_proton_fits_classes import proton_fits # Import proton_fits instance

# Define constants (moved from calculation file)
try:
    from scipy.constants import physical_constants, k as k_B_scipy, proton_mass as proton_mass_kg_scipy
    # Alpha mass is approx 4 * proton mass
    m_alpha_kg = 4.0 * proton_mass_kg_scipy 
except ImportError:
    print("Warning: scipy.constants not found, using approximate constants.")
    k_B_scipy = 1.380649e-23 # Boltzmann constant J/K
    proton_mass_kg_scipy = 1.67262192e-27 # kg Fallback
    m_alpha_kg = 4.0 * proton_mass_kg_scipy

# Constants for calculations (SI units where applicable)
m_alpha = m_alpha_kg # Mass of alpha particle in kg
k_B = k_B_scipy     # Boltzmann constant in J/K
# Conversion factor from eV (common in plasma physics) to Kelvin
# T_Kelvin = T_eV * e / k_B 
# We assume input temperatures (Tperpa, Tpara) are already in eV or similar energy units
# Thermal speed: v_th = sqrt(2 * k_B * T_Kelvin / m) = sqrt(2 * T_eV * e / m)
# Let's assume T inputs (Tperpa, Tpara) are in eV for thermal speed calculation
electron_volt = 1.602176634e-19 # Joules per eV

class alpha_fits_class: # Renamed class
    def __init__(self, imported_data):
        # Initialize raw_data dictionary with keys for alpha FITS variables (sf01)
        # AND the 17 target plot variables 
        object.__setattr__(self, 'raw_data', {
            # Raw inputs from sf01 CSV (as loaded by data_import)
            'na': None,             # Alpha density
            'va_x': None,           # Alpha velocity X (RTN?)
            'va_y': None,           # Alpha velocity Y
            'va_z': None,           # Alpha velocity Z
            'Trata': None,          # Alpha Temperature Ratio (Tperp/Tpar)
            'Ta_perp': None,        # Alpha Perpendicular Temperature (eV?) -> Tperpa
            'B_inst_x': None,       # Inst. Magnetic Field X (from FITS source)
            'B_inst_y': None,       # Inst. Magnetic Field Y
            'B_inst_z': None,       # Inst. Magnetic Field Z
            'na_dpar': None,        # Uncertainty in na
            'va_x_dpar': None,      # Uncertainty in va_x
            'va_y_dpar': None,      # Uncertainty in va_y
            'va_z_dpar': None,      # Uncertainty in va_z
            'Trata_dpar': None,     # Uncertainty in Trata
            'Ta_perp_dpar': None,   # Uncertainty in Ta_perp -> Tperpa_dpar
            'chi': None,            # Raw chi-squared from FITS source -> chi_a
            
            # --- 17 Calculated Target Outputs (names match user list/plots) ---
            # 1. na (uses raw 'na' after filtering) - re-stored under same key
            # 2. Tp_alpha (Calculated Total Alpha Temp)
            'Tp_alpha': None,       
            # 3. Trat_alpha (uses raw 'Trata' after filtering)
            'Trat_alpha': None,     
            # 4. va_x (uses raw 'va_x' after filtering) - re-stored
            # 5. va_y (uses raw 'va_y' after filtering) - re-stored
            # 6. va_z (uses raw 'va_z' after filtering) - re-stored
            # 7. va_mag (Calculated Alpha Velocity Magnitude)
            'va_mag': None,         
            # 8. vsw_mach_alpha (Calculated Alpha Mach Number)
            'vsw_mach_alpha': None, 
            # 9. beta_alpha (Calculated Total Alpha Beta)
            'beta_alpha': None,     
            # 10. vth_alpha (Calculated Alpha Thermal Speed)
            'vth_alpha': None,      
            # 11. vth_par_alpha (Calculated Parallel Alpha Thermal Speed)
            'vth_par_alpha': None,  
            # 12. vth_perp_alpha (Calculated Perpendicular Alpha Thermal Speed)
            'vth_perp_alpha': None, 
            # 13. vth_drift (Calculated Drift Thermal Speed - TBD if possible)
            'vth_drift': None,      # Placeholder - Calculation unclear/complex
            # 14. beta_par_alpha (uses 'beta_par_a' calculation)
            'beta_par_alpha': None, 
            # 15. beta_perp_alpha (Calculated Perpendicular Alpha Beta)
            'beta_perp_alpha': None, 
            # 16. chi_alpha (uses raw 'chi' after filtering, stored as 'chi_a')
            'chi_alpha': None,          # Will hold masked 'chi' data
            # 17. chi_alpha_norm (Calculated Normalized Chi)
            'chi_alpha_norm': None, 

            # --- Intermediate/Supporting Calculations ---
            'Tpara': None,          # Calculated Parallel Alpha Temperature (eV?)
            'nap_tot': None,        # Total density (alpha + proton core + proton beam)
            'valfven_apfits': None, # Alfven speed using nap_tot
            'vdrift_ap1': None,     # Alpha vel mag relative to proton core vel mag
            'vdrift_va_ap1': None,  # vdrift_ap1 normalized by valfven_apfits
            'na_div_np': None,      # Ratio na / (np1+np2)
            'na_div_np1': None,     # Ratio na / np1
            'na_div_np2': None,     # Ratio na / np2
            'B_mag': None,          # Magnetic field magnitude (from aligned proton B)
            # Store uncertainties if needed for plots later
            # 'na_dpar_afits': None, # Example
        })
        # Use 'time' for TT2000 array, 'datetime_array' for datetime objects
        object.__setattr__(self, 'time', None) 
        object.__setattr__(self, 'datetime_array', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_ploptions() # Will init empty plotters
            print_manager.debug("alpha_fits_class: No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.debug("alpha_fits_class: Calculating alpha fits variables internally...")
            self.calculate_variables(imported_data)
            # Check if calculate_variables successfully produced time array
            if self.time is not None and len(self.time) > 0:
                 self.set_ploptions()
                 print_manager.status("alpha_fits_class: Successfully calculated alpha fits variables.")
            else:
                 # If calculation failed, still call set_ploptions to init empty plotters
                 self.set_ploptions() 
                 print_manager.warning("alpha_fits_class: Calculation failed or produced no time data. Plot options initialized empty.")


        # Stash the instance in data_cubby
        data_cubby.stash(self, class_name='alpha_fits') # Use unique class name

    def update(self, imported_data):
        """Method to update class with new data."""
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return

        print_manager.datacubby(f"\\n=== Starting {self.__class__.__name__} update... ===")
        
        # Store current state
        current_state = {}
        # Iterate through expected plottable attributes (keys in raw_data that get ploptions)
        plot_keys = [k for k, v in self.raw_data.items() if v is not None] # Or use predefined list based on set_ploptions
        for subclass_name in plot_keys:
             if hasattr(self, subclass_name):
                 var = getattr(self, subclass_name)
                 if hasattr(var, '_plot_state'):
                      current_state[subclass_name] = dict(var._plot_state)
                      print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_ploptions()
        
        # Restore state
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")

    def get_subclass(self, subclass_name):
        """Retrieve a specific plot_manager attribute by its name."""
        print_manager.debug(f"alpha_fits_class: Attempting to get subclass/attribute: {subclass_name}")
        if hasattr(self, subclass_name):
            attribute_value = getattr(self, subclass_name)
            if isinstance(attribute_value, plot_manager):
                print_manager.debug(f"Returning plot_manager instance for: {subclass_name}")
                return attribute_value
            else:
                print_manager.warning(f"Attribute '{subclass_name}' exists but is not a plot_manager instance (Type: {type(attribute_value)}). Returning None.")
                return None
        else:
            print(f"'{subclass_name}' is not a recognized alpha_fits subclass/attribute, friend!")
            available_attrs = [attr for attr in dir(self) if isinstance(getattr(self, attr, None), plot_manager) and not attr.startswith('_')]
            print(f"Available plot managers: {', '.join(sorted(available_attrs))}")
            return None

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        print_manager.debug(f'alpha_fits_class __getattr__ triggered for: {name}')
        available_attrs = [attr for attr in dir(self) 
                           if isinstance(getattr(self, attr, None), plot_manager) 
                           and not attr.startswith('_')]
        error_message = f"'{name}' is not a recognized alpha_fits attribute, friend!"
        if available_attrs:
            error_message += f"\nAvailable plot managers: {', '.join(sorted(available_attrs))}"
        else:
            error_message += "\nNo plot manager attributes seem to be available yet."
        raise AttributeError(error_message)

    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return
        """Allow setting attributes directly."""
        # Simplified: Allow setting any attribute directly.
        super().__setattr__(name, value)

    def calculate_variables(self, imported_data):
        """Calculates derived alpha FITS variables internally, fetching proton dependencies."""
        # --- Import needed functions/instances within method --- 
        from ..data_cubby import data_cubby # To get proton_fits instance
        # Constants are now defined outside __init__ but within class scope

        try:
            # --- 1. Initial Data Validation & Time Setup ---
            if not hasattr(imported_data, 'data') or not hasattr(imported_data, 'times'):
                logging.error("alpha_fits_class Error: imported_data is not a valid DataObject.")
                return # Abort

            data_dict = imported_data.data # Alpha FITS data dictionary
            self.time = np.asarray(imported_data.times) # TT2000 array for Alphas

            if self.time is None or self.time.size == 0:
                 logging.error("alpha_fits_class Error: Imported DataObject has empty or None 'times'.")
                 self.datetime_array = None
                 # Clear all potential data fields
                 for key in self.raw_data: self.raw_data[key] = None
                 return

            # Convert alpha TT2000 to datetime objects and store
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            # Convert alpha TT2000 to Unix timestamps for interpolation
            alpha_times_unix = np.array([cdflib.cdfepoch.unixtime(t) for t in self.time])

            # --- 2. Fetch Proton Data Dependency ---
            proton_fits_instance = data_cubby.grab('proton_fits')
            proton_data_available = False
            proton_time_unix = None
            p_np1, p_np2, p_vp1_mag, p_B_mag = (None,) * 4 # Initialize proton vars

            if proton_fits_instance is not None and hasattr(proton_fits_instance, 'time') and proton_fits_instance.time is not None and len(proton_fits_instance.time) > 0:
                print_manager.debug("Alpha Calc: Found proton_fits instance in data_cubby.")
                proton_time_tt2000 = proton_fits_instance.time
                proton_time_unix = np.array([cdflib.cdfepoch.unixtime(t) for t in proton_time_tt2000])
                
                # Extract necessary raw proton data (use .get for safety)
                p_raw = proton_fits_instance.raw_data
                p_np1 = p_raw.get('np1')
                p_np2 = p_raw.get('np2')
                p_vp1_mag = p_raw.get('vp1_mag') 
                p_B_mag = p_raw.get('B_mag') # B_mag calculated within proton_fits

                # Check if essential proton data exists
                essential_proton = [p_np1, p_np2, p_vp1_mag, p_B_mag]
                if all(v is not None and len(v) == len(proton_time_unix) for v in essential_proton):
                    proton_data_available = True
                    print_manager.debug("Alpha Calc: Essential proton data loaded.")
                else:
                    missing_p_keys = [k for k, v in {'np1':p_np1, 'np2':p_np2, 'vp1_mag':p_vp1_mag, 'B_mag':p_B_mag}.items() if v is None or len(v) != len(proton_time_unix)]
                    logging.warning(f"Alpha Calc: Missing or mismatched length in essential proton data: {missing_p_keys}. Cannot perform dependent calculations.")
            else:
                logging.warning("Alpha Calc: proton_fits instance not found or has no time data in data_cubby. Cannot perform dependent calculations.")

            # --- 3. Align Proton Data to Alpha Time Grid ---
            aligned_np1, aligned_np2, aligned_vp1_mag, aligned_B_mag = (None,) * 4 # Initialize aligned vars

            if proton_data_available:
                print_manager.debug("Alpha Calc: Aligning proton data to alpha time grid...")
                try:
                    # Handle potential NaNs in proton data before interpolation
                    valid_proton_mask = ~np.isnan(proton_time_unix) & \
                                        ~np.isnan(p_np1) & \
                                        ~np.isnan(p_np2) & \
                                        ~np.isnan(p_vp1_mag) & \
                                        ~np.isnan(p_B_mag)
                                        
                    if np.sum(valid_proton_mask) > 1: # Need at least 2 points
                        proton_time_valid = proton_time_unix[valid_proton_mask]
                        
                        aligned_np1 = np.interp(alpha_times_unix, proton_time_valid, p_np1[valid_proton_mask], left=np.nan, right=np.nan)
                        aligned_np2 = np.interp(alpha_times_unix, proton_time_valid, p_np2[valid_proton_mask], left=np.nan, right=np.nan)
                        aligned_vp1_mag = np.interp(alpha_times_unix, proton_time_valid, p_vp1_mag[valid_proton_mask], left=np.nan, right=np.nan)
                        aligned_B_mag = np.interp(alpha_times_unix, proton_time_valid, p_B_mag[valid_proton_mask], left=np.nan, right=np.nan)
                        print_manager.debug("Alpha Calc: Proton data alignment successful.")
                    else:
                        print_manager.warning("Alpha Calc: Not enough valid proton data points for interpolation.")
                        # Create NaN arrays matching alpha time length if interpolation fails
                        nan_array = np.full_like(alpha_times_unix, np.nan, dtype=float)
                        aligned_np1, aligned_np2, aligned_vp1_mag, aligned_B_mag = (nan_array,) * 4
                        proton_data_available = False # Mark as unavailable for calculations

                except Exception as interp_e:
                    logging.error(f"Alpha Calc: Error during proton data alignment/interpolation: {interp_e}")
                    # Create NaN arrays matching alpha time length if interpolation fails
                    nan_array = np.full_like(alpha_times_unix, np.nan, dtype=float)
                    aligned_np1, aligned_np2, aligned_vp1_mag, aligned_B_mag = (nan_array,) * 4
                    proton_data_available = False # Mark as unavailable
            else:
                 # If proton data wasn't available to begin with, create NaN arrays
                 nan_array = np.full_like(alpha_times_unix, np.nan, dtype=float)
                 aligned_np1, aligned_np2, aligned_vp1_mag, aligned_B_mag = (nan_array,) * 4
                 print_manager.warning("Alpha Calc: Skipping dependent calculations due to unavailable/unalignable proton data.")

            # --- 4. Extract Raw Alpha Data ---
            # Use .get() for safety, default to None if key missing
            na = data_dict.get('na')
            va_x = data_dict.get('va_x')
            va_y = data_dict.get('va_y')
            va_z = data_dict.get('va_z')
            Trata = data_dict.get('Trata')
            # Rename Ta_perp from input to Tperpa internally for consistency with Jaye's formulas maybe?
            # Let's stick to Ta_perp as the key for raw data, use Tperpa variable name locally if needed
            Tperpa = data_dict.get('Ta_perp') 
            B_inst_x = data_dict.get('B_inst_x') # Raw B from alpha file (may differ slightly from proton B)
            B_inst_y = data_dict.get('B_inst_y')
            B_inst_z = data_dict.get('B_inst_z')
            # Uncertainties
            na_dpar = data_dict.get('na_dpar')
            va_x_dpar = data_dict.get('va_x_dpar')
            va_y_dpar = data_dict.get('va_y_dpar')
            va_z_dpar = data_dict.get('va_z_dpar')
            Trata_dpar = data_dict.get('Trata_dpar')
            Tperpa_dpar = data_dict.get('Ta_perp_dpar') 
            chi_source = data_dict.get('chi') # Raw chi from sf01

            # Check essential alpha raw data
            essential_alpha = [na, va_x, va_y, va_z, Trata, Tperpa]
            if any(v is None for v in essential_alpha):
                missing_keys = [k for k, v in {'na': na, 'va_x': va_x, 'va_y': va_y, 'va_z': va_z, 'Trata': Trata, 'Ta_perp': Tperpa}.items() if v is None]
                logging.error(f"alpha_fits_class Error: Essential raw alpha data missing: {missing_keys}.")
                # Clear all potential data fields
                for key in self.raw_data: self.raw_data[key] = None
                self.time = None; self.datetime_array = None # Clear time as well
                return

            # --- 5. Filtering Alpha Data ---
            # Apply filters from Jaye's calculate_sf01_fits_vars
            # Ensure arrays are numeric before comparison
            try:
                filter_conditions = (
                    (na.astype(float) > 0) &          # Density must be positive
                    (Tperpa.astype(float) > 0.101) &   # Perpendicular Temp threshold
                    (Trata.astype(float) > 0.101) &    # Temp Ratio threshold
                    (Trata.astype(float) != 8) &       # Exclude specific ratio values
                    (Trata.astype(float) != 2.0)
                )
                mask = filter_conditions
                print_manager.debug(f"Alpha Calc: Filter applied. Valid points: {np.sum(mask)} / {len(na)}")
            except Exception as filter_e:
                 logging.error(f"Alpha Calc: Error applying filters: {filter_e}. Check data types.")
                 mask = np.ones_like(na, dtype=bool) # Default to no filtering if error occurs

            # Apply NaN mask to all relevant raw alpha arrays where mask is False
            raw_arrays_to_mask = {
                'na': na, 'va_x': va_x, 'va_y': va_y, 'va_z': va_z, 'Trata': Trata,
                'Ta_perp': Tperpa, 'B_inst_x': B_inst_x, 'B_inst_y': B_inst_y, 
                'B_inst_z': B_inst_z, 'na_dpar': na_dpar, 'va_x_dpar': va_x_dpar,
                'va_y_dpar': va_y_dpar, 'va_z_dpar': va_z_dpar, 'Trata_dpar': Trata_dpar,
                'Ta_perp_dpar': Tperpa_dpar, 'chi': chi_source
            }
            masked_data = {}
            for key, arr in raw_arrays_to_mask.items():
                if arr is None: # Skip if data was missing initially
                    masked_data[key] = None 
                    continue
                # Ensure array is float before assigning NaN, handle potential type errors
                try:
                    if not np.issubdtype(arr.dtype, np.floating):
                        masked_data[key] = arr.astype(float)
                    else:
                        masked_data[key] = arr.copy()
                    masked_data[key][~mask] = np.nan
                except TypeError as te:
                     logging.warning(f"Alpha Calc: Type error masking '{key}'. Setting to NaN array. Error: {te}")
                     masked_data[key] = np.full_like(arr, np.nan, dtype=float)
                 
            # Use masked data for subsequent calculations
            na = masked_data['na']
            va_x = masked_data['va_x']
            va_y = masked_data['va_y']
            va_z = masked_data['va_z']
            Trata = masked_data['Trata'] # This will be stored as 'Trat_alpha'
            Tperpa = masked_data['Ta_perp'] # This is the input for Tperp_alpha
            B_inst_x = masked_data['B_inst_x'] # Use local B if needed, but prefer aligned B_mag
            B_inst_y = masked_data['B_inst_y']
            B_inst_z = masked_data['B_inst_z']
            na_dpar = masked_data['na_dpar']
            va_x_dpar = masked_data['va_x_dpar']
            va_y_dpar = masked_data['va_y_dpar']
            va_z_dpar = masked_data['va_z_dpar']
            Trata_dpar = masked_data['Trata_dpar']
            Tperpa_dpar = masked_data['Ta_perp_dpar']
            chi_a = masked_data['chi'] # Store masked chi under key 'chi_alpha' later


            # --- 6. Perform Derived Alpha Parameter Calculations ---
            with np.errstate(all='ignore'): # Suppress warnings for NaN operations

                # --- Basic Alpha Variables ---
                va_mag = np.sqrt(va_x**2 + va_y**2 + va_z**2)
                Trata_safe = np.where(Trata != 0, Trata, np.nan) # Avoid division by zero
                Tpara = Tperpa / Trata_safe # Calculate Alpha Parallel Temp (assuming eV)
                Tp_alpha = (2 * Tperpa + Tpara) / 3 # Calculate Total Alpha Temp (assuming eV)

                # --- Variables Dependent on Aligned Proton Data ---
                # Use aligned_B_mag from interpolated proton data for consistency
                B_mag = aligned_B_mag # Use aligned value
                
                # Total density (Protons + Alphas)
                nap_tot = aligned_np1 + aligned_np2 + na
                
                # Alfven Speed (using total density and aligned B_mag)
                nap_tot_safe = np.where(nap_tot > 0, nap_tot, np.nan)
                valfven_apfits = 21.8 * B_mag / np.sqrt(nap_tot_safe)
                valfven_apfits_safe = np.where(valfven_apfits != 0, valfven_apfits, np.nan)

                # Alpha velocity relative to proton core velocity
                vdrift_ap1 = va_mag - aligned_vp1_mag 
                vdrift_va_ap1 = vdrift_ap1 / valfven_apfits_safe # Normalized drift

                # Density Ratios
                np_tot_aligned = aligned_np1 + aligned_np2
                np_tot_safe = np.where(np_tot_aligned > 0, np_tot_aligned, np.nan)
                np1_safe = np.where(aligned_np1 > 0, aligned_np1, np.nan)
                np2_safe = np.where(aligned_np2 > 0, aligned_np2, np.nan)
                na_div_np = na / np_tot_safe
                na_div_np1 = na / np1_safe
                na_div_np2 = na / np2_safe

                # Alpha Betas (using aligned B_mag)
                beta_denom = (1e-5 * B_mag)**2
                beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)
                # Parallel Beta Alpha (Target Variable 14)
                beta_par_alpha = (4.03E-11 * na * Tpara) / beta_denom_safe # Use calculated Tpara
                # Perpendicular Beta Alpha (Target Variable 15)
                beta_perp_alpha = (4.03E-11 * na * Tperpa) / beta_denom_safe # Use input Tperpa
                # Total Beta Alpha (Target Variable 9)
                beta_alpha = np.sqrt(beta_par_alpha**2 + beta_perp_alpha**2)

                # Alpha Mach Number (Target Variable 8)
                vsw_mach_alpha = va_mag / valfven_apfits_safe

                # --- Thermal Speeds ---
                # v_th = sqrt(2 * T_eV * e / m) ; Units: m/s
                # Convert result to km/s by dividing by 1000
                # Parallel Alpha Thermal Speed (Target Variable 11)
                vth_par_alpha = np.sqrt(2 * Tpara * electron_volt / m_alpha) / 1000.0 
                # Perpendicular Alpha Thermal Speed (Target Variable 12)
                vth_perp_alpha = np.sqrt(2 * Tperpa * electron_volt / m_alpha) / 1000.0
                # Total Alpha Thermal Speed (Target Variable 10)
                vth_alpha = np.sqrt(2 * Tp_alpha * electron_volt / m_alpha) / 1000.0 
                # Drift Thermal Speed (Target Variable 13) - Calculation unclear, leave as NaN
                vth_drift = np.full_like(na, np.nan) 

                # --- Chi Squared ---
                # Chi Alpha (Target Variable 16) - already masked in chi_a
                # Normalized Chi Alpha (Target Variable 17) - Use same normalization as proton?
                chi_alpha_norm = chi_a / 2038.0 if chi_a is not None else np.full_like(na, np.nan)

            # --- 7. Store Calculated Results in self.raw_data ---
            # Store RAW masked inputs first (overwrites initial None values)
            self.raw_data['na'] = na           # Target 1 (re-stored)
            self.raw_data['va_x'] = va_x         # Target 4 (re-stored)
            self.raw_data['va_y'] = va_y         # Target 5 (re-stored)
            self.raw_data['va_z'] = va_z         # Target 6 (re-stored)
            self.raw_data['Trat_alpha'] = Trata # Target 3 (using masked Trata)
            self.raw_data['Ta_perp'] = Tperpa      # Raw input base for Tperp_alpha
            self.raw_data['B_inst_x'] = B_inst_x
            self.raw_data['B_inst_y'] = B_inst_y
            self.raw_data['B_inst_z'] = B_inst_z
            self.raw_data['na_dpar'] = na_dpar
            self.raw_data['va_x_dpar'] = va_x_dpar
            self.raw_data['va_y_dpar'] = va_y_dpar
            self.raw_data['va_z_dpar'] = va_z_dpar
            self.raw_data['Trata_dpar'] = Trata_dpar
            self.raw_data['Ta_perp_dpar'] = Tperpa_dpar
            # Store original 'chi' (masked) under the key 'chi_alpha' (Target 16)
            self.raw_data['chi_alpha'] = chi_a 
            # Keep raw chi source name in dict too? Maybe not necessary if stored as chi_alpha
            self.raw_data['chi'] = chi_source # Store unmasked original for reference? or masked? Let's store masked.
            
            # Store CALCULATED target variables 
            self.raw_data['Tp_alpha'] = Tp_alpha             # Target 2
            self.raw_data['va_mag'] = va_mag                 # Target 7
            self.raw_data['vsw_mach_alpha'] = vsw_mach_alpha # Target 8
            self.raw_data['beta_alpha'] = beta_alpha         # Target 9
            self.raw_data['vth_alpha'] = vth_alpha           # Target 10
            self.raw_data['vth_par_alpha'] = vth_par_alpha   # Target 11
            self.raw_data['vth_perp_alpha'] = vth_perp_alpha # Target 12
            self.raw_data['vth_drift'] = vth_drift           # Target 13 (NaN)
            self.raw_data['beta_par_alpha'] = beta_par_alpha # Target 14
            self.raw_data['beta_perp_alpha'] = beta_perp_alpha # Target 15
            self.raw_data['chi_alpha_norm'] = chi_alpha_norm # Target 17

            # Store Intermediate/Supporting calculations
            self.raw_data['Tpara'] = Tpara
            self.raw_data['nap_tot'] = nap_tot
            self.raw_data['valfven_apfits'] = valfven_apfits
            self.raw_data['vdrift_ap1'] = vdrift_ap1
            self.raw_data['vdrift_va_ap1'] = vdrift_va_ap1
            self.raw_data['na_div_np'] = na_div_np
            self.raw_data['na_div_np1'] = na_div_np1
            self.raw_data['na_div_np2'] = na_div_np2
            self.raw_data['B_mag'] = B_mag # Store the aligned B_mag used

        except Exception as e:
            print_manager.error(f"!!! CAUGHT UNEXPECTED ERROR IN alpha_fits_class.calculate_variables: {e}")
            logging.error(f"Error during internal FITS calculation in alpha_fits_class.calculate_variables: {e}")
            import traceback
            logging.error(traceback.format_exc())
            # Clear potentially calculated fields if error occurs
            for key in self.raw_data:
                # Check if key exists in self.raw_data before trying to assign None
                # Also check if it wasn't part of the original input (data_dict)
                if key in self.raw_data and key not in data_dict:
                     self.raw_data[key] = None
            self.datetime_array = None # Also clear time
            self.time = None

        # Stash the updated instance in data_cubby 
        data_cubby.stash(self, class_name='alpha_fits')

    # UPDATED HELPER DEFINITION with optional keyword args and defaults
    def _create_alpha_scatter_ploptions(self, var_name, subclass_name, y_label, legend_label, color,
                                       marker_style='o', marker_size=5, alpha=0.7, y_scale='linear', y_limit=None):
        """Helper method to create ploptions for standard Alpha FITS scatter plots."""
        dt_array = self.datetime_array if hasattr(self, 'datetime_array') and self.datetime_array is not None else None
        
        return ploptions(
            var_name=var_name,
            data_type='alpha_fits', 
            class_name='alpha_fits',
            subclass_name=subclass_name,
            plot_type='scatter',
            datetime_array=dt_array,
            y_label=y_label,
            legend_label=legend_label,
            color=color,
            # Use arguments passed to helper (or their defaults)
            y_scale=y_scale,          
            marker_style=marker_style,           
            marker_size=marker_size,             
            alpha=alpha,                 
            y_limit=y_limit               
        )

    def set_ploptions(self):
        """Initialize or update plot_manager instances for the 17 target alpha FITS data variables."""
        print_manager.debug("alpha_fits_class: Setting plot options...")
        
        # Helper lambda to get data safely
        get_data = lambda key: self.raw_data.get(key) if hasattr(self, 'raw_data') else None
        # Ensure datetime_array is valid or None
        dt_array = self.datetime_array if hasattr(self, 'datetime_array') and self.datetime_array is not None else None

        # --- Create Plot Managers using the helper (overrides only when needed) ---

        # 1. na (Alpha Density) - Uses helper defaults
        self.na = plot_manager(
            get_data('na'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='na', 
                subclass_name='na', 
                y_label=r'$N_\alpha$ (cm$^{-3}$)', 
                legend_label=r'$n_{\alpha}$', 
                color='black' 
            )
        )

        # 2. Tp_alpha (Total Alpha Temperature) - Uses helper defaults
        self.Tp_alpha = plot_manager(
            get_data('Tp_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='Tp_alpha', 
                subclass_name='Tp_alpha', 
                y_label=r'$T_{\alpha}$ (eV)', 
                legend_label=r'$T_{\alpha}$', 
                color='grey'
            )
        )
        
        # 3. Trat_alpha (Alpha Temp. Anisotropy) - Uses helper defaults
        self.Trat_alpha = plot_manager(
            get_data('Trat_alpha'), # Contains masked 'Trata'
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='Trat_alpha', # Use the target key name
                subclass_name='Trat_alpha', 
                y_label=r'$T_{\perp} / T_{\parallel}$', 
                legend_label=r'$T_{\perp} / T_{\parallel, \alpha}$', 
                color='grey' 
            )
        )

        # 4. va_x (Alpha Velocity X) - Uses helper defaults
        self.va_x = plot_manager(
            get_data('va_x'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='va_x',
                subclass_name='va_x', 
                y_label=r'Velocity (km/s)',
                legend_label=r'$vx_{\alpha}$',
                color='forestgreen' 
            )
        )

        # 5. va_y (Alpha Velocity Y) - Uses helper defaults
        self.va_y = plot_manager(
            get_data('va_y'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='va_y',
                subclass_name='va_y', 
                y_label=r'Velocity (km/s)',
                legend_label=r'$vy_{\alpha}$',
                color='orange' 
            )
        )

        # 6. va_z (Alpha Velocity Z) - Uses helper defaults
        self.va_z = plot_manager(
            get_data('va_z'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='va_z',
                subclass_name='va_z', 
                y_label=r'Velocity (km/s)',
                legend_label=r'$vz_{\alpha}$',
                color='dodgerblue' 
            )
        )

        # 7. va_mag (Alpha Velocity Magnitude) - Uses helper defaults
        self.va_mag = plot_manager(
            get_data('va_mag'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='va_mag', 
                subclass_name='va_mag', 
                y_label=r'$|V_\alpha|$ (km/s)', 
                legend_label=r'$|V_\alpha|$',
                color='black' 
            )
        )

        # 8. vsw_mach_alpha (Alpha Mach Number) - Uses helper defaults
        self.vsw_mach_alpha = plot_manager(
            get_data('vsw_mach_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='vsw_mach_alpha', 
                subclass_name='vsw_mach_alpha', 
                y_label=r'$V_{\alpha}/V_A$', 
                legend_label=r'$V_{\alpha}/V_A$', 
                color='gold'
            )
        )

        # 9. beta_alpha (Total Alpha Beta) - Uses helper defaults
        self.beta_alpha = plot_manager(
            get_data('beta_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='beta_alpha', 
                subclass_name='beta_alpha', 
                y_label=r'$\beta_{\alpha}$', 
                legend_label=r'$\beta_{\alpha}$', 
                color='lightskyblue'
            )
        )

        # 10. vth_alpha (Total Alpha Thermal Speed) - Uses helper defaults
        self.vth_alpha = plot_manager(
            get_data('vth_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='vth_alpha', 
                subclass_name='vth_alpha', 
                y_label=r'$v_{th,\alpha}$ (km/s)', 
                legend_label=r'$v_{th,\alpha}$', 
                color='mediumspringgreen'
            )
        )

        # 11. vth_par_alpha (Parallel Alpha Thermal Speed) - Uses helper defaults
        self.vth_par_alpha = plot_manager(
            get_data('vth_par_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='vth_par_alpha', 
                subclass_name='vth_par_alpha', 
                y_label=r'$v_{th,\parallel \alpha}$ (km/s)', 
                legend_label=r'$v_{th,\parallel \alpha}$', 
                color='hotpink'
            )
        )
        
        # 12. vth_perp_alpha (Perpendicular Alpha Thermal Speed) - Uses helper defaults
        self.vth_perp_alpha = plot_manager(
            get_data('vth_perp_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='vth_perp_alpha', 
                subclass_name='vth_perp_alpha', 
                y_label=r'$v_{th,\perp \alpha}$ (km/s)', 
                legend_label=r'$v_{th,\perp \alpha}$', 
                color='deepskyblue'
            )
        )

        # 13. vth_drift (Drift Thermal Speed - Placeholder) - Needs overrides
        self.vth_drift = plot_manager(
            get_data('vth_drift'), # Contains NaNs
            plot_options=self._create_alpha_scatter_ploptions( # Use helper
                var_name='vth_drift',
                subclass_name='vth_drift',
                y_label=r'$v_{th,drift}$ (km/s)',
                legend_label=r'$v_{th,drift}$ (N/A)',
                color='purple',
                marker_style='x', # Override default
                alpha=0.5        # Override default
                # Other args use helper defaults
            )
        )
        
        # 14. beta_par_alpha (Parallel Alpha Beta) - Uses helper defaults
        self.beta_par_alpha = plot_manager(
            get_data('beta_par_alpha'), # Key from calculate_variables
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='beta_par_alpha', # Key from calculate_variables
                subclass_name='beta_par_alpha', 
                y_label=r'$\beta_{\parallel, \alpha}$', 
                legend_label=r'$\beta_{\parallel, \alpha}$',
                color='grey' 
            )
        )

        # 15. beta_perp_alpha (Perpendicular Alpha Beta) - Uses helper defaults
        self.beta_perp_alpha = plot_manager(
            get_data('beta_perp_alpha'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='beta_perp_alpha', 
                subclass_name='beta_perp_alpha', 
                y_label=r'$\beta_{\perp, \alpha}$', 
                legend_label=r'$\beta_{\perp, \alpha}$', 
                color='lightcoral'
            )
        )

        # 16. chi_alpha (Alpha Chi Squared) - Uses helper defaults
        self.chi_alpha = plot_manager(
            get_data('chi_alpha'), # Key used in calculate_variables
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='chi_alpha', # Key used in calculate_variables
                subclass_name='chi_alpha', 
                y_label=r'$\chi^2_{\alpha}$', 
                legend_label=r'$\chi^2_{\alpha}$',
                color='dodgerblue' 
            )
        )

        # 17. chi_alpha_norm (Normalized Alpha Chi Squared) - Uses helper defaults
        self.chi_alpha_norm = plot_manager(
            get_data('chi_alpha_norm'),
            plot_options=self._create_alpha_scatter_ploptions(
                var_name='chi_alpha_norm', 
                subclass_name='chi_alpha_norm', 
                y_label=r'$\chi^2_{\alpha} / \nu$', 
                legend_label=r'$\chi^2_{\alpha, norm}$',
                color='rebeccapurple' 
            )
        )

        print_manager.debug("alpha_fits_class: Finished setting plot options.")


# Initialize with no data - This should be moved to data_classes/__init__.py
alpha_fits = alpha_fits_class(None) 
print('initialized alpha_fits class') 