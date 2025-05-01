#plotbot/data_classes/psp_proton_fits_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
from scipy.interpolate import interp1d # For Calculate What You Need (CWYN) interpolation
import matplotlib.dates as mdates      # For Calculate What You Need (CWYN) time conversion

# Define constants (moved from calculation file)
try:
    from scipy.constants import physical_constants
    proton_mass_kg_scipy = physical_constants['proton mass'][0]
    electron_volt = physical_constants['electron volt'][0]
    speed_of_light = physical_constants['speed of light in vacuum'][0]
except ImportError:
    print("Warning: scipy.constants not found, using approximate proton mass.")
    proton_mass_kg_scipy = 1.67262192e-27 # kg Fallback

m = 1836 * 511000.0 / (299792.0**2) # Factor for Tpar_tot calculation
m_proton_kg = proton_mass_kg_scipy

# Import our custom managers (UPDATED PATHS)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
# Import get_data and proton instance for dependency loading (within method if needed)
# from ..get_data import get_data 
# from .psp_proton_classes import proton

class proton_fits_class:
    def __init__(self, imported_data, plotbot_instance=None):
        # Initialize raw_data with keys matching the expected CDF variables
        # Includes directly provided variables and any *still* calculated ones.
        object.__setattr__(self, 'raw_data', {
            # --- Variables directly from spi_sf00_cdf --- 
            'Epoch': None,        # Time base
            'np1': None,
            'np2': None,
            'Tperp1': None,
            'Tperp2': None,
            'Trat1': None,
            'Trat2': None,
            'vdrift': None,       # Scalar drift speed?
            'vp1': None,          # Proton core velocity vector [vx, vy, vz]
            'B_inst': None,       # Magnetic field vector (Instrument frame)
            'B_SC': None,         # Magnetic field vector (Spacecraft frame)
            'chi_p': None,        # Chi-squared (using CDF name)
            # Pre-calculated thermal properties from CDF
            'Tpar1': None,
            'Tpar2': None,
            'Tpar_tot': None,
            'Tperp_tot': None,
            'Temp_tot': None,
            # Pre-calculated density/velocity properties from CDF
            'n_tot': None,
            'vp2': None,          # Proton beam velocity vector
            'vcm': None,          # Center of mass velocity vector
            'bhat_inst': None,    # Unit vector of B_inst
            'qz_p': None,         # Heat flux
            # Magnitudes from CDF (if directly available, verify)
            'vp1_mag': None,
            'vcm_mag': None,
            'vp2_mag': None,
            'B_mag': None,        # Assume calculated if B_inst/B_SC are vectors
            # Uncertainties from CDF
            'np1_dpar': None,
            'np2_dpar': None,
            'Tperp1_dpar': None,
            'Tperp2_dpar': None, 
            'Trat1_dpar': None,
            'Trat2_dpar': None,
            'vdrift_dpar': None,
            'vp1_dpar': None,       # Uncertainty for vp1 vector?
            # Other variables from CDF
            'epad_strahl_centroid': None,
            'ps_ht1': None,
            'ps_ht2': None,
            'qz_p_par': None,     # Parallel heat flux
            'qz_p_perp': None,    # Perpendicular heat flux
            
            # --- Variables potentially *still* calculated HERE ---
            # Check if these are in CDF or still need calculation
            'vsw_mach': None,      # Likely still needs calculation (depends on spi_sf00_l3_mom)
            'valfven': None,       # Alfven speed (might need calculation from B_mag, n_tot)
            'beta_ppar': None,     # Parallel Beta (might need calc from Tpar_tot, n_tot, B_mag)
            'beta_pperp': None,    # Perp Beta (might need calc from Tperp_tot, n_tot, B_mag)
            'beta_p_tot': None,    # Total Beta
            'ham_param': None,     # Hammerhead parameter
            'np2_np1_ratio': None, # Density ratio
            'vdrift_abs': None,   # Absolute drift (redundant if vdrift is scalar?)
            'vdrift_va': None,     # Drift / Alfven speed
            'chi_p_norm': None,   # Normalized chi
            'Vcm_mach': None,      # Vcm / Alfven speed
            'Vp1_mach': None,      # Vp1 / Alfven speed
            # Individual vector components (if needed for plotting/calcs and not accessed via slicing)
            # 'B_inst_x': None, 
            # 'B_inst_y': None, 
            # 'B_inst_z': None,
            # 'vp1_x': None,
            # 'vp1_y': None,
            # 'vp1_z': None,
            # etc. for B_SC, vp2, vcm, bhat_inst...
            # --- NEW: Variables calculated using CWYN properties ---
            'vdrift_va_p2p1_apfits': None, # Placeholder for property access
            'abs_vdrift_va_p2p1_apfits': None, # Placeholder for property access
        })
        # Initialize time attributes
        object.__setattr__(self, 'time', None) # Will hold TT2000 epoch
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_cwyn_cache', {}) # Initialize Calculate What You Need (CWYN) cache
        object.__setattr__(self, 'plotbot', plotbot_instance) # Store reference to PlotBot

        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_ploptions()
            print_manager.debug(f"{self.__class__.__name__} initialized empty.")
        else:
            # Process the imported CDF data
            print_manager.debug(f"Processing imported CDF data for {self.__class__.__name__}...")
            self.calculate_variables(imported_data) # This function needs major rewrite
            self.set_ploptions() # This function will need updates too
            # Add status message after processing
            if self.datetime_array is not None:
                 print_manager.status(f"Successfully processed {self.__class__.__name__} CDF data.")
            else:
                 print_manager.warning(f"Processing for {self.__class__.__name__} completed, but no valid data loaded.")

        # Stash the instance in data_cubby
        data_cubby.stash(self, class_name='proton_fits') # Keep key consistent for now?

    def update(self, imported_data):
        """Method to update class with new data.
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return

        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")

        # Store current state before update (including any modified ploptions)
        current_state = {}
        # Make sure to iterate over keys that will eventually have ploptions
        plot_keys = [k for k, v in self.raw_data.items() if v is not None] # Or use predefined list
        for subclass_name in plot_keys:
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)       # Save current plot state
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        
        self.set_ploptions()                                                  # Recreate plot managers

        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():                    # Restore saved states
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)                                 # Restore plot state
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)                # Restore individual options
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")

        print_manager.datacubby("=== End Update Debug ===\n")

    def get_subclass(self, subclass_name):
        """Retrieve a specific plot_manager attribute by its name (subclass_name)."""
        print_manager.debug(f"Attempting to get subclass/attribute: {subclass_name}")
        # Directly check if an attribute with the exact subclass_name exists on the instance.
        # This attribute should hold the plot_manager instance set by set_ploptions.
        if hasattr(self, subclass_name):
            attribute_value = getattr(self, subclass_name)
            # Optional: Check if it's actually a plot_manager instance?
            if isinstance(attribute_value, plot_manager):
                print_manager.debug(f"Returning plot_manager instance for: {subclass_name}")
                return attribute_value
            else:
                # This case shouldn't normally happen if set_ploptions worked correctly
                print_manager.warning(f"Attribute '{subclass_name}' exists but is not a plot_manager instance (Type: {type(attribute_value)}). Returning None.")
                return None
        else:
            # If the attribute doesn't exist (e.g., set_ploptions failed or name is wrong)
            print(f"'{subclass_name}' is not a recognized subclass/attribute, friend!")
            # List available plot_manager attributes
            available_attrs = [attr for attr in dir(self) if isinstance(getattr(self, attr, None), plot_manager) and not attr.startswith('_')]
            print(f"Available plot managers: {', '.join(sorted(available_attrs))}")
            return None # Return None if not found

    def __getattr__(self, name):
        """Provide a helpful error message when an attribute is not found.
        Lists the available plot_manager attributes that can be accessed.
        """
        print_manager.debug(f'proton_fits __getattr__ triggered for: {name}')
        
        # Generate the list of ACTUAL plottable attributes (plot_manager instances)
        available_attrs = [attr for attr in dir(self) 
                           if isinstance(getattr(self, attr, None), plot_manager) 
                           and not attr.startswith('_')]
        
        # Construct the error message
        error_message = f"'{name}' is not a recognized attribute, friend!"
        if available_attrs:
            error_message += f"\nAvailable plot managers: {', '.join(sorted(available_attrs))}"
        else:
            error_message += "\nNo plot manager attributes seem to be available yet." # Should not happen after init
            
        # Raise AttributeError, which is standard practice for __getattr__
        raise AttributeError(error_message)

    def __setattr__(self, name, value):
        """Allow setting attributes directly. The strict checking was preventing set_ploptions from working."""
        # Simplified: Allow setting any attribute directly.
        # The previous logic blocked setting plot_manager instances if their attribute
        # name didn't exactly match a raw_data key.
        super().__setattr__(name, value)
        # Original restrictive logic commented out:
        # print_manager.debug(f"Setting attribute: {name} with value: {value}")
        # if name in ['datetime', 'datetime_array', 'raw_data', 'time'] or (hasattr(self, 'raw_data') and name in self.raw_data):
        #     super().__setattr__(name, value)
        # else:
        #     # Print friendly error message
        #     print_manager.debug('proton_fits setattr helper!')
        #     print(f"'{name}' is not a recognized attribute, friend!")
        #     available_attrs = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        #     # Also list plot_manager attributes set by set_ploptions
        #     pm_attrs = [attr for attr in dir(self) if isinstance(getattr(self, attr, None), plot_manager) and not attr.startswith('_')]
        #     available_attrs.extend([a for a in pm_attrs if a not in available_attrs])
        #     print(f"Try one of these: {', '.join(sorted(available_attrs))}")
        #     # Do not set the attrib - This was the problem!

    def calculate_variables(self, imported_data):
        """Processes imported spi_sf00_fits (CDF) data, extracting variables and calculating a few remaining ones."""
        # --- Import needed functions/instances --- 
        from ..data_import import import_data_function # Potentially needed for vsw_mach
        # from .psp_proton_classes import proton # Potentially needed for vsw_mach dependency

        try:
            # --- 1. Validate Input --- 
            if not hasattr(imported_data, 'data') or not hasattr(imported_data, 'times'):
                logging.error(f"Error in {self.__class__.__name__}.calculate_variables: imported_data is not a valid DataObject.")
                self.datetime_array = None; self.time = None
                return

            data_dict = imported_data.data # Data dictionary from DataObject
            self.time = np.asarray(imported_data.times) # TT2000 from CDF Epoch

            if self.time is None or self.time.size == 0:
                 logging.error(f"{self.__class__.__name__}: Imported DataObject has empty or None 'times' attribute.")
                 self.datetime_array = None
                 for key in self.raw_data: self.raw_data[key] = None
                 return

            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.debug(f"{self.__class__.__name__}: Processing data for time range {self.datetime_array.min()} to {self.datetime_array.max()}")

            # --- 2. Extract Variables from CDF Data --- 
            # Get all variables defined in the __init__ raw_data structure 
            extracted_data = {}
            potential_missing_keys = []
            vars_to_calculate = [ # Define variables we INTEND to calculate here
                'B_mag', 'valfven', 'beta_ppar', 'beta_pperp', 'beta_p_tot', 
                'vsw_mach', 'ham_param', 'np2_np1_ratio', 'vdrift_abs', 
                'vdrift_va', 'chi_p_norm', 'Vcm_mach', 'Vp1_mach'
            ]
            
            for key in self.raw_data.keys():
                data_val = data_dict.get(key)
                if data_val is not None:
                     extracted_data[key] = np.asarray(data_val)
                     # print_manager.debug(f"  Extracted {key}, shape: {extracted_data[key].shape}, type: {extracted_data[key].dtype}") # Verbose
                elif key not in vars_to_calculate: # If missing and not planned for calculation
                     potential_missing_keys.append(key)
                     extracted_data[key] = None # Set to None
                else:
                     extracted_data[key] = None # Placeholder for calculation

            if potential_missing_keys:
                 print_manager.warning(f"{self.__class__.__name__}: The following expected CDF variables were missing: {potential_missing_keys}")

            # --- 3. Perform Necessary Calculations --- 
            
            # Calculate B_mag (if not directly present)
            B_mag = extracted_data.get('B_mag')
            if B_mag is None:
                 B_inst = extracted_data.get('B_inst')
                 if B_inst is not None and B_inst.ndim == 2 and B_inst.shape[1] == 3:
                      with np.errstate(invalid='ignore'):
                           B_mag = np.sqrt(B_inst[:, 0]**2 + B_inst[:, 1]**2 + B_inst[:, 2]**2)
                      extracted_data['B_mag'] = B_mag
                      print_manager.debug("  Calculated B_mag from B_inst vector.")
                 else:
                      print_manager.warning("Could not find/calculate B_mag (B_mag not in CDF, B_inst missing or wrong shape).")
            else:
                print_manager.debug("Using B_mag directly provided by CDF.")

            # Calculate np2_np1_ratio
            np1 = extracted_data.get('np1')
            np2 = extracted_data.get('np2')
            if np1 is not None and np2 is not None:
                 with np.errstate(divide='ignore', invalid='ignore'):
                      np1_safe = np.where(np1 != 0, np1, np.nan)
                      extracted_data['np2_np1_ratio'] = np2 / np1_safe
                      print_manager.debug("  Calculated np2_np1_ratio.")
            else:
                 extracted_data['np2_np1_ratio'] = None

            # Calculate valfven 
            n_tot = extracted_data.get('n_tot')
            valfven = None # Initialize
            if B_mag is not None and n_tot is not None:
                 with np.errstate(divide='ignore', invalid='ignore'):
                      n_tot_safe = np.where(n_tot > 0, n_tot, np.nan)
                      valfven = 21.8 * B_mag / np.sqrt(n_tot_safe)
                 extracted_data['valfven'] = valfven
                 print_manager.debug("  Calculated valfven.")
            else:
                 extracted_data['valfven'] = None
                 # print_manager.warning("Could not calculate valfven (missing B_mag or n_tot).") # Already warned about B_mag

            # Calculate beta_ppar, beta_pperp, beta_p_tot
            Tpar_tot = extracted_data.get('Tpar_tot')
            Tperp_tot = extracted_data.get('Tperp_tot')
            if Tpar_tot is not None and Tperp_tot is not None and n_tot is not None and B_mag is not None:
                 with np.errstate(divide='ignore', invalid='ignore'):
                      n_tot_safe = np.where(n_tot > 0, n_tot, np.nan)
                      beta_denom = (1e-5 * B_mag)**2
                      beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)
                      beta_ppar = (4.03E-11 * n_tot_safe * Tpar_tot) / beta_denom_safe
                      beta_pperp = (4.03E-11 * n_tot_safe * Tperp_tot) / beta_denom_safe
                      beta_p_tot = np.sqrt(beta_ppar**2 + beta_pperp**2) 
                 extracted_data['beta_ppar'] = beta_ppar
                 extracted_data['beta_pperp'] = beta_pperp
                 extracted_data['beta_p_tot'] = beta_p_tot
                 print_manager.debug("  Calculated beta parameters.")
            else:
                 extracted_data['beta_ppar'] = None
                 extracted_data['beta_pperp'] = None
                 extracted_data['beta_p_tot'] = None
                 # print_manager.warning("Could not calculate beta parameters (missing inputs).")

            # Calculate ham_param
            Tperp1 = extracted_data.get('Tperp1')
            Tperp2 = extracted_data.get('Tperp2')
            Trat_tot = extracted_data.get('Trat_tot')
            if Tperp1 is not None and Tperp2 is not None and Trat_tot is not None:
                 with np.errstate(divide='ignore', invalid='ignore'):
                      Trat_tot_safe = np.where(Trat_tot != 0, Trat_tot, np.nan)
                      Tperp1_safe = np.where(Tperp1 != 0, Tperp1, np.nan)
                      extracted_data['ham_param'] = (Tperp2 / Tperp1_safe) / Trat_tot_safe
                      print_manager.debug("  Calculated ham_param.")
            else:
                 extracted_data['ham_param'] = None

            # Calculate chi_p_norm
            chi_p = extracted_data.get('chi_p')
            if chi_p is not None:
                 with np.errstate(divide='ignore', invalid='ignore'):
                      extracted_data['chi_p_norm'] = chi_p / 2038.0
                      print_manager.debug("  Calculated chi_p_norm.")
            else:
                 extracted_data['chi_p_norm'] = None

            # Calculate vdrift_abs (simple)
            vdrift = extracted_data.get('vdrift')
            if vdrift is not None:
                 extracted_data['vdrift_abs'] = np.abs(vdrift)
                 print_manager.debug("  Calculated vdrift_abs.")
            else:
                 extracted_data['vdrift_abs'] = None

            # Calculate Mach numbers (V/Va)
            valfven_safe = np.where(valfven != 0, valfven, np.nan) if valfven is not None else None
            if valfven_safe is not None:
                 vdrift = extracted_data.get('vdrift')
                 vcm_mag = extracted_data.get('vcm_mag')
                 vp1_mag = extracted_data.get('vp1_mag')
                 with np.errstate(divide='ignore', invalid='ignore'):
                      if vdrift is not None: extracted_data['vdrift_va'] = vdrift / valfven_safe
                      if vcm_mag is not None: extracted_data['Vcm_mach'] = vcm_mag / valfven_safe
                      if vp1_mag is not None: extracted_data['Vp1_mach'] = vp1_mag / valfven_safe
                 print_manager.debug("  Calculated vdrift_va, Vcm_mach, Vp1_mach.")
            else:
                 extracted_data['vdrift_va'] = None
                 extracted_data['Vcm_mach'] = None
                 extracted_data['Vp1_mach'] = None
                 # print_manager.warning("Could not calculate Mach numbers (missing valfven).")
            
            # --- Placeholder for vsw_mach (Requires external dependency) --- 
            # TODO: Implement fetching spi_sf00_l3_mom and aligning if vsw_mach is needed
            print_manager.debug("Skipping vsw_mach calculation (requires external dependency).")
            extracted_data['vsw_mach'] = None 

            # --- 4. Store Final Data --- 
            for key, value in extracted_data.items():
                 if key in self.raw_data:
                      self.raw_data[key] = value
                 # else: # Don't warn if it was just an intermediate calc like B_mag maybe
                 #      print_manager.warning(f"Key '{key}' calculated/extracted but not in initial raw_data dict. Ignoring.")
                      
            if self.datetime_array is None:
                 print_manager.error(f"{self.__class__.__name__}: No valid time array after processing.")
            
        except Exception as e:
            print_manager.error(f"!!! UNEXPECTED ERROR in {self.__class__.__name__}.calculate_variables: {e}")
            import traceback
            logging.error(traceback.format_exc())
            # Clear potentially calculated fields if error occurs
            for key in self.raw_data: self.raw_data[key] = None # Clear everything on error
            self.datetime_array = None 
            self.time = None

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        # data_cubby.stash(self, class_name='proton_fits') # Stashing happens in __init__ / update

    # --- Calculate What You Need (CWYN) Properties ---
    @property
    def vsw_mach(self):
        """Calculates Solar Wind Mach number (Vsw / Va_proton) on demand.

        Fetches spi_sf00_l3_mom data, aligns Vsw to the FITS time base,
        and divides by the Alfven speed calculated using only proton density.
        Results are cached.
        """
        cache_key = 'vsw_mach'
        required_internal = ['valfven']
        cubby_key = 'spi_sf00_l3_mom'
        # V_rtn needed if vp not present, Epoch needed for alignment
        required_dependency_vars = ['Epoch', 'V_rtn', 'vp']

        # 1. Use helper to check cache and internal prerequisites
        cached_result, should_calculate = self._check_cwyn_cache_and_prereqs(cache_key, required_internal)
        if not should_calculate:
            return cached_result
        valfven_p = self.raw_data.get('valfven') # Already validated by helper

        # 2. Fetch and validate dependency
        try:
            # Note: required_dependency_vars includes 'vp' which might be None, 
            # the helper validates *presence*, not non-None status for optional vars.
            dependencies = self._fetch_and_validate_dependency(cache_key, cubby_key, required_dependency_vars)
            if dependencies is None:
                self._cwyn_cache[cache_key] = np.full(self.time.shape, np.nan)
                return self._cwyn_cache[cache_key]
            
            # Extract validated vars
            mom_time = dependencies.get('Epoch')
            mom_v_rtn = dependencies.get('V_rtn')
            mom_vp = dependencies.get('vp') # Could be None if not present

            # 3. Get Vsw (Solar Wind Speed magnitude)
            if mom_vp is not None:
                vsw = mom_vp
                print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Using 'vp' magnitude from {cubby_key}.")
            elif mom_v_rtn is not None and mom_v_rtn.ndim == 2 and mom_v_rtn.shape[1] >= 3:
                print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Calculating Vsw magnitude from 'V_rtn' vector.")
                with np.errstate(invalid='ignore'):
                    vsw = np.sqrt(mom_v_rtn[:, 0]**2 + mom_v_rtn[:, 1]**2 + mom_v_rtn[:, 2]**2)
            else:
                # This case should ideally be caught by the validation helper if both are missing/invalid
                logging.error(f"{self.__class__.__name__} ({cache_key}): Could not determine Vsw from validated dependencies.")
                self._cwyn_cache[cache_key] = np.full(self.time.shape, np.nan)
                return self._cwyn_cache[cache_key]

            # 4. Align Vsw to self.time
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Aligning Vsw to FITS time base...")
            vsw_aligned = self._interpolate_to_self_time(mom_time, vsw)
            if vsw_aligned is None:
                logging.error(f"{self.__class__.__name__} ({cache_key}): Alignment of Vsw failed.")
                self._cwyn_cache[cache_key] = np.full(self.time.shape, np.nan)
                return self._cwyn_cache[cache_key]

            # 5. Calculate Mach number
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Calculating Mach number...")
            with np.errstate(divide='ignore', invalid='ignore'):
                valfven_p_safe = np.where(valfven_p != 0, valfven_p, np.nan)
                mach_number = vsw_aligned / valfven_p_safe

            # 6. Cache and return result
            self._cwyn_cache[cache_key] = mach_number
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Successfully calculated and cached.")
            return self._cwyn_cache[cache_key]

        except Exception as e:
            logging.error(f"!!! UNEXPECTED ERROR calculating {cache_key} in {self.__class__.__name__}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            result_shape = self.time.shape if self.time is not None else (0,)
            self._cwyn_cache[cache_key] = np.full(result_shape, np.nan)
            return self._cwyn_cache[cache_key]

    @property
    def vdrift_va_p2p1_apfits(self):
        """Calculates normalized drift (Vdrift / Va_alphaproton) on demand.

        Fetches sf01_fits data for alpha density (na), calculates the
        Alfven speed using total density (n_tot + na), and divides the
        proton drift speed (vdrift) by this mixed Alfven speed.
        Assumes proton and alpha data are aligned. Results are cached.
        """
        cache_key = 'vdrift_va_p2p1_apfits'
        required_internal = ['vdrift', 'n_tot', 'B_mag']
        cubby_key = 'sf01_fits'
        required_dependency_vars = ['na', 'Epoch'] # Epoch needed for length check

        # 1. Use helper to check cache and internal prerequisites
        cached_result, should_calculate = self._check_cwyn_cache_and_prereqs(cache_key, required_internal)
        if not should_calculate:
            return cached_result
        vdrift = self.raw_data.get('vdrift')
        n_tot_p = self.raw_data.get('n_tot')
        b_mag = self.raw_data.get('B_mag')

        # 2. Fetch and validate dependency
        try:
            dependencies = self._fetch_and_validate_dependency(cache_key, cubby_key, required_dependency_vars)
            if dependencies is None:
                self._cwyn_cache[cache_key] = np.full(self.time.shape, np.nan)
                return self._cwyn_cache[cache_key]
            
            na = dependencies.get('na')
            # alpha_time = dependencies.get('Epoch') # Not needed for calculation, only length check

            # 3. Verify array lengths (assuming alignment)
            if len(na) != len(self.time) or len(n_tot_p) != len(self.time) or len(vdrift) != len(self.time) or len(b_mag) != len(self.time):
                 logging.error(f"{self.__class__.__name__} ({cache_key}): Length mismatch ({len(self.time)=}, {len(na)=}, {len(n_tot_p)=}). Cannot calculate. Data might not be aligned.")
                 self._cwyn_cache[cache_key] = np.full(self.time.shape, np.nan)
                 return self._cwyn_cache[cache_key]

            # 4. Calculate Mixed Alfven Speed (Va_ap)
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Calculating mixed Alfven speed (Va_ap)...")
            with np.errstate(divide='ignore', invalid='ignore'):
                n_total_ap = n_tot_p + na
                n_total_ap_safe = np.where(n_total_ap > 0, n_total_ap, np.nan)
                valfven_ap = 21.8 * b_mag / np.sqrt(n_total_ap_safe)

            # 5. Calculate Normalized Drift (Vdrift / Va_ap)
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Calculating normalized drift (Vdrift / Va_ap)...")
            with np.errstate(divide='ignore', invalid='ignore'):
                valfven_ap_safe = np.where(valfven_ap != 0, valfven_ap, np.nan)
                norm_drift = vdrift / valfven_ap_safe

            # 6. Cache and return result
            self._cwyn_cache[cache_key] = norm_drift
            print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Successfully calculated and cached.")
            return self._cwyn_cache[cache_key]

        except Exception as e:
            logging.error(f"!!! UNEXPECTED ERROR calculating {cache_key} in {self.__class__.__name__}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            result_shape = self.time.shape if self.time is not None else (0,)
            self._cwyn_cache[cache_key] = np.full(result_shape, np.nan)
            return self._cwyn_cache[cache_key]

    @property
    def abs_vdrift_va_p2p1_apfits(self):
        """Calculates absolute normalized drift (|Vdrift| / Va_alphaproton) on demand.

        Simply calls the vdrift_va_p2p1_apfits property and returns the absolute value.
        Relies on the caching mechanism within vdrift_va_p2p1_apfits.
        """
        print_manager.debug(f"{self.__class__.__name__}: Calculating abs_vdrift_va_p2p1_apfits...")
        
        # Get the potentially cached result from the non-absolute property
        norm_drift = self.vdrift_va_p2p1_apfits

        # Check if the result was valid before taking abs
        if norm_drift is None:
            logging.warning(f"{self.__class__.__name__}: Underlying vdrift_va_p2p1_apfits returned None.")
            return None # Propagate None if calculation failed

        # Calculate and return the absolute value
        # Use errstate to handle potential NaNs gracefully
        with np.errstate(invalid='ignore'):
            abs_norm_drift = np.abs(norm_drift)

        # No separate caching needed here
        print_manager.debug(f"{self.__class__.__name__}: Returning absolute value of vdrift_va_p2p1_apfits.")
        return abs_norm_drift

    def _interpolate_to_self_time(self, source_time, source_data):
        """Interpolates external data onto this instance's time base. Used for 

        Args:
            source_time (np.ndarray): Datetime array of the source data.
            source_data (np.ndarray): Data values corresponding to source_time.

        Returns:
            np.ndarray or None: Interpolated data array matching self.time, or None if interpolation fails.
        """
        if self.time is None or len(self.time) == 0:
            logging.error(f"{self.__class__.__name__}: Cannot interpolate, self.time is not set.")
            return None
        if source_time is None or len(source_time) < 2 or source_data is None or len(source_data) < 2:
            logging.warning(f"{self.__class__.__name__}: Insufficient source data points for interpolation.")
            # Return array of NaNs with the shape of the target time
            return np.full(self.time.shape, np.nan)
        if len(source_time) != len(source_data):
             logging.error(f"{self.__class__.__name__}: Source time and data lengths mismatch for interpolation ({len(source_time)} vs {len(source_data)}).")
             return np.full(self.time.shape, np.nan)

        try:
            # Convert times to numeric representation (TT2000/CDF Epoch should already be numeric)
            # If target time is datetime, convert it
            target_time_numeric = self.time
            if isinstance(target_time_numeric[0], datetime):
                target_time_numeric = mdates.date2num(target_time_numeric)

            # Convert source time to numeric if it's datetime
            source_time_numeric = source_time
            if isinstance(source_time_numeric[0], datetime):
                source_time_numeric = mdates.date2num(source_time_numeric)

            # Handle NaNs in source data
            valid_mask = ~np.isnan(source_data)
            if not np.all(valid_mask):
                if np.sum(valid_mask) < 2:
                    logging.warning(f"{self.__class__.__name__}: Not enough valid source data points after NaN removal for interpolation.")
                    return np.full(self.time.shape, np.nan)
                source_time_numeric = source_time_numeric[valid_mask]
                source_data_valid = source_data[valid_mask]
            else:
                source_data_valid = source_data

            # Create interpolation function
            # Use bounds_error=False and fill_value=np.nan to handle extrapolation
            interp_func = interp1d(
                source_time_numeric,
                source_data_valid,
                kind='linear',
                bounds_error=False,
                fill_value=np.nan
            )

            # Perform interpolation
            interpolated_data = interp_func(target_time_numeric)
            print_manager.debug(f"{self.__class__.__name__}: Successfully interpolated data onto self.time.")
            return interpolated_data

        except Exception as e:
            logging.error(f"!!! UNEXPECTED ERROR during interpolation in {self.__class__.__name__}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            # Return NaNs in case of any unexpected error
            return np.full(self.time.shape, np.nan)

    def _check_cwyn_cache_and_prereqs(self, cache_key, required_internal_keys=[]):
        """Checks CWYN cache and internal prerequisites for a property calculation.

        Args:
            cache_key (str): The key to check in self._cwyn_cache.
            required_internal_keys (list, optional): List of keys that must be present
                and not all NaN in self.raw_data. Defaults to [].

        Returns:
            tuple: (result, should_calculate)
                - result: The cached value if found, or an array of NaNs if prerequisites fail.
                - should_calculate (bool): True if calculation should proceed, False otherwise.
        """
        # 1. Check cache
        if cache_key in self._cwyn_cache:
            print_manager.debug(f"{self.__class__.__name__}: Returning cached {cache_key}.")
            return self._cwyn_cache[cache_key], False # Return cached value, don't calculate

        print_manager.debug(f"{self.__class__.__name__}: Calculating {cache_key} (not cached)...")

        # 2. Check core prerequisites (plotbot reference and time array)
        if self.plotbot is None or self.plotbot.data_cubby is None:
            logging.error(f"{self.__class__.__name__}: PlotBot/DataCubby reference not available. Cannot calculate {cache_key}.")
            nan_result = np.full(self.time.shape, np.nan) if self.time is not None else None
            return nan_result, False # Return NaNs, don't calculate
        if self.time is None:
            logging.error(f"{self.__class__.__name__}: Self time array is None. Cannot calculate {cache_key}.")
            return None, False # Return None, don't calculate

        # 3. Check required internal raw_data keys
        for key in required_internal_keys:
            data = self.raw_data.get(key)
            if data is None or np.all(np.isnan(data)):
                logging.warning(f"{self.__class__.__name__}: Required internal key '{key}' not available or all NaN. Cannot calculate {cache_key}.")
                nan_result = np.full(self.time.shape, np.nan)
                return nan_result, False # Return NaNs, don't calculate

        # Prerequisites met, calculation should proceed
        return None, True

    def _fetch_and_validate_dependency(self, cache_key, cubby_key, required_dependency_vars):
        """Fetches dependency from DataCubby and validates required variables.

        Args:
            cache_key (str): The cache key of the calling property (for logging).
            cubby_key (str): The key to fetch from self.plotbot.data_cubby.
            required_dependency_vars (list): List of variable names that must be extracted
                and validated from the dependency instance.

        Returns:
            dict or None: A dictionary containing the validated dependency variables
                          (e.g., {'Epoch': time_array, 'na': na_array}) if successful,
                          otherwise None.
        """
        print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Fetching dependency '{cubby_key}'...")
        dependency_instance = self.plotbot.data_cubby.grab(cubby_key)

        # 1. Check if instance was fetched
        if dependency_instance is None:
            logging.error(f"{self.__class__.__name__} ({cache_key}): Failed to retrieve '{cubby_key}' from DataCubby.")
            return None

        # 2. Try to extract required variables
        extracted_vars = {}
        dependency_raw_data = getattr(dependency_instance, 'raw_data', None)

        for var_name in required_dependency_vars:
            value = None
            # Prioritize raw_data dictionary
            if dependency_raw_data is not None and var_name in dependency_raw_data:
                value = dependency_raw_data[var_name]
            # Fallback to direct attribute access
            elif hasattr(dependency_instance, var_name):
                value = getattr(dependency_instance, var_name)

            # Basic validation: Check if None or all NaN (if array)
            if value is None:
                logging.warning(f"{self.__class__.__name__} ({cache_key}): Required variable '{var_name}' not found in '{cubby_key}' instance.")
                return None # Fail if any required var is missing
            if isinstance(value, np.ndarray) and value.size > 0 and np.all(np.isnan(value)):
                logging.warning(f"{self.__class__.__name__} ({cache_key}): Required variable '{var_name}' in '{cubby_key}' is all NaN.")
                # Decide if all NaN is acceptable or a failure - for now, let's treat it as failure
                return None
            if isinstance(value, np.ndarray) and value.size == 0:
                 logging.warning(f"{self.__class__.__name__} ({cache_key}): Required variable '{var_name}' in '{cubby_key}' is an empty array.")
                 return None # Treat empty array as failure
                 
            extracted_vars[var_name] = value

        print_manager.debug(f"{self.__class__.__name__} ({cache_key}): Successfully fetched and validated dependency '{cubby_key}'.")
        return extracted_vars

    def _create_fits_scatter_ploptions(self, var_name, subclass_name, y_label, legend_label, color,
                                       marker_style='*', marker_size=5, alpha=0.7, y_scale='linear', y_limit=None):
        """Helper method to create ploptions for standard FITS scatter plots."""
        # Ensure datetime_array is handled correctly if None
        dt_array = self.datetime_array if hasattr(self, 'datetime_array') and self.datetime_array is not None else None
        
        return ploptions(
            var_name=var_name,
            data_type='proton_fits',
            class_name='proton_fits',
            subclass_name=subclass_name,
            plot_type='scatter',         
            datetime_array=dt_array, # Use potentially None dt_array
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
        """Initialize or update plot_manager instances with data and plot options."""
        
        # Initialize plot managers in the order specified by user (1-34)

        # 1. qz_p (Scatter, Size 20)
        self.qz_p = plot_manager( # Heat flux of the proton beam
            self.raw_data.get('qz_p'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='qz_p',
                subclass_name='qz_p', # User list #1
                y_label=r'$q_{z,p}$ (W/m$^2$)',
                legend_label=r'$q_{z,p}$',
                color='blueviolet',
                y_scale='linear',
                marker_style='*', 
                marker_size=20,
                alpha=0.7,
                y_limit=None
            )
        )

        # 2. vsw_mach_pfits (Scatter, Size 20)
        self.vsw_mach_pfits = plot_manager( # Solar wind Mach number - ATTRIBUTE NAME CHANGED
            self.raw_data.get('vsw_mach'), # Still gets raw 'vsw_mach' data
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vsw_mach', 
                subclass_name='vsw_mach_pfits', # User list #2
                y_label=r'$V_{sw}/V_A$', 
                legend_label=r'$V_{sw}/V_A$', 
                color='gold', 
                y_scale='linear',
                y_limit=None,
                marker_style='*',
                marker_size=20, 
                alpha=0.7
            )
        )

        # 3. beta_ppar_pfits (Scatter, Size 20)
        self.beta_ppar_pfits = plot_manager( # Total Proton parallel beta - ATTRIBUTE NAME CHANGED
            self.raw_data.get('beta_ppar'), # Still gets raw 'beta_ppar' data
            plot_options=self._create_fits_scatter_ploptions(
                var_name='beta_ppar',
                subclass_name='beta_ppar_pfits', # User list #3 (Updated)
                y_label=r'$\beta_{\parallel,p}$', 
                legend_label=r'$\beta_{\parallel,p}$', 
                color='hotpink', 
                y_scale='linear', 
                marker_style='*', 
                marker_size=20,   
                alpha=0.7,      
                y_limit=None
            )
        )

        # 4. beta_pperp_pfits (Scatter, Size 20)
        self.beta_pperp_pfits = plot_manager( # Total Proton perpendicular beta - ATTRIBUTE NAME CHANGED
            self.raw_data.get('beta_pperp'), # Still gets raw 'beta_pperp' data
            plot_options=self._create_fits_scatter_ploptions(
                var_name='beta_pperp', 
                subclass_name='beta_pperp_pfits', # User list #4 (Updated)
                y_label=r'$\beta_{\perp,p}$',
                legend_label=r'$\beta_{\perp,p}$',
                color='lightskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=20,
                alpha=0.7,
                y_limit=None
            )
        )

        # 5. ham_param (Scatter, Size 20)
        self.ham_param = plot_manager( # Hammerhead parameter
            self.raw_data.get('ham_param'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='ham_param',
                subclass_name='ham_param', # User list #5
                y_label='Hamplitude', 
                legend_label='Hamplitude', 
                color='palevioletred',
                y_scale='linear',
                marker_style='*',
                marker_size=20,
                alpha=0.7,
                y_limit=None
            )
        )

        # 6. np1 (Scatter, Size 5)
        self.np1 = plot_manager( # Core density
            self.raw_data.get('np1'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='np1',
                subclass_name='np1', # User list #6
                y_label=r'Density (cm$^{-3}$)',
                legend_label=r'$n_{p1}$',
                color='hotpink'
            )
        )

        # 7. np2 (Scatter, Size 5)
        self.np2 = plot_manager( # Beam density
            self.raw_data.get('np2'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='np2',
                subclass_name='np2', # User list #7
                y_label=r'Density (cm$^{-3}$)', 
                legend_label=r'$n_{p2}$',
                color='deepskyblue'
            )
        )

        # 8. n_tot (Scatter, Size 5)
        self.n_tot = plot_manager( # Total beam+core density
            self.raw_data.get('n_tot'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='n_tot',
                subclass_name='n_tot', # User list #8
                y_label=r'Density (cm$^{-3}$)',
                legend_label=r'$n_{ptot}$', 
                color='deepskyblue' 
            )
        )

        # 9. np2/np1 (Scatter, Size 5)
        self.np2_np1_ratio = plot_manager( # Beam to core density ratio
            self.raw_data.get('np2_np1_ratio'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='np2_np1_ratio',
                subclass_name='np2_np1_ratio', # MATCH ATTRIBUTE NAME (User list #9)
                y_label=r'$\frac{n_{p2}}{n_{p1}}$', 
                legend_label=r'$\frac{n_{p2}}{n_{p1}}$', 
                color='deepskyblue' 
            )
        )

        # 10. vp1_x (Scatter, Size 5)
        self.vp1_x = plot_manager( # Core velocity x
            self.raw_data.get('vp1_x'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vp1_x',
                subclass_name='vp1_x', # User list #10
                y_label=r'Velocity (km/s)',
                legend_label=r'$vx_{p1}$',
                color='forestgreen'
            )
        )

        # 11. vp1_y (Scatter, Size 5)
        self.vp1_y = plot_manager( # Core velocity y
            self.raw_data.get('vp1_y'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vp1_y',
                subclass_name='vp1_y', # User list #11
                y_label=r'Velocity (km/s)',
                legend_label=r'$vy_{p1}$',
                color='orange'
            )
        )

        # 12. vp1_z (Scatter, Size 5)
        self.vp1_z = plot_manager( # Core velocity z
            self.raw_data.get('vp1_z'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vp1_z',
                subclass_name='vp1_z', # User list #12
                y_label=r'Velocity (km/s)',
                legend_label=r'$vz_{p1}$',
                color='dodgerblue'
            )
        )

        # 13. vp1_mag (Scatter, Size 5)
        self.vp1_mag = plot_manager( # Core velocity magnitude
            self.raw_data.get('vp1_mag'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vp1_mag',
                subclass_name='vp1_mag', # User list #13
                y_label=r'Velocity (km/s)',
                legend_label=r'$vmag_{p1}$',
                color='dodgerblue' 
            )
        )

        # 14. vcm_x (Scatter, Size 5)
        self.vcm_x = plot_manager( # Center of mass velocity x
            self.raw_data.get('vcm_x'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vcm_x',
                subclass_name='vcm_x', # User list #14
                y_label=r'Velocity (km/s)',
                legend_label=r'$vx_{cm}$',
                color='forestgreen' 
            )
        )

        # 15. vcm_y (Scatter, Size 5)
        self.vcm_y = plot_manager( # Center of mass velocity y
            self.raw_data.get('vcm_y'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vcm_y',
                subclass_name='vcm_y', # User list #15
                y_label=r'Velocity (km/s)',
                legend_label=r'$vy_{cm}$',
                color='orange' 
            )
        )

        # 16. vcm_z (Scatter, Size 5)
        self.vcm_z = plot_manager( # Center of mass velocity z
            self.raw_data.get('vcm_z'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vcm_z',
                subclass_name='vcm_z', # User list #16
                y_label=r'Velocity (km/s)',
                legend_label=r'$vz_{cm}$',
                color='dodgerblue' 
            )
        )

        # 17. vcm_mag (Scatter, Size 5)
        self.vcm_mag = plot_manager( # Center of mass velocity magnitude
            self.raw_data.get('vcm_mag'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vcm_mag',
                subclass_name='vcm_mag', # User list #17
                y_label=r'Velocity (km/s)',
                legend_label=r'$vmag_{cm}$',
                color='dodgerblue' 
            )
        )
        
        # 18. vdrift (Scatter, Size 5)
        self.vdrift = plot_manager( # Drift speed
            self.raw_data.get('vdrift'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vdrift',
                subclass_name='vdrift', # User list #18
                y_label=r'$V_{drift}$', 
                legend_label=r'$vdrift_{p2}$', 
                color='navy' 
            )
        )

        # 19. |vdrift| (Scatter, Size 5)
        self.vdrift_abs = plot_manager( # Absolute drift speed
            self.raw_data.get('vdrift_abs'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vdrift_abs', 
                subclass_name='vdrift_abs', # MATCH ATTRIBUTE NAME (User list #19)
                y_label=r'$|V_{drift}|$', 
                legend_label=r'$|vdrift_{p2}|$ ', 
                color='navy' 
            )
        )

        # 20. vdrift_va_pfits (Scatter, Size 5)
        self.vdrift_va_pfits = plot_manager( # Normalized drift speed - ATTRIBUTE NAME CHANGED
            self.raw_data.get('vdrift_va'), # Still gets raw 'vdrift_va' data
            plot_options=self._create_fits_scatter_ploptions(
                var_name='vdrift_va', 
                subclass_name='vdrift_va_pfits', # User list #20
                y_label=r'$V_{drift}/V_A$', 
                legend_label=r'$vdrift_{p2}/vA$', 
                color='navy' 
            )
        )

        # 21. Trat1 (Scatter, Size 5)
        self.Trat1 = plot_manager( # Temperature anisotropy of the core
            self.raw_data.get('Trat1'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Trat1',
                subclass_name='Trat1', # User list #21
                y_label=r'$T_{\perp}/T_{\parallel}$',
                legend_label=r'$T_{\perp}/T_{\parallel,p1}$',
                color='hotpink' 
            )
        )

        # 22. Trat2 (Scatter, Size 5)
        self.Trat2 = plot_manager( # Temperature anisotropy of the beam
            self.raw_data.get('Trat2'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Trat2',
                subclass_name='Trat2', # User list #22
                y_label=r'$T_{\perp}/T_{\parallel}$',
                legend_label=r'$T_{\perp}/T_{\parallel,p2}$',
                color='deepskyblue' 
            )
        )

        # 23. Trat_tot (Scatter, Size 5)
        self.Trat_tot = plot_manager( # Total temperature anisotropy
            self.raw_data.get('Trat_tot'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Trat_tot',
                subclass_name='Trat_tot', # User list #23
                y_label=r'$T_\perp/T_\parallel$',
                legend_label=r'$T_\perp/T_\parallel$',
                color='mediumspringgreen' 
            )
        )

        # 24. Tpar1 (Scatter, Size 5)
        self.Tpar1 = plot_manager( # Temperature parallel of the core
            self.raw_data.get('Tpar1'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tpar1',
                subclass_name='Tpar1', # User list #24
                y_label=r'$T_{\parallel}$',
                legend_label=r'$T_{\parallel,p1}$',
                color='hotpink' 
            )
        )

        # 25. Tpar2 (Scatter, Size 5)
        self.Tpar2 = plot_manager( # Temperature parallel of the beam
            self.raw_data.get('Tpar2'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tpar2',
                subclass_name='Tpar2', # User list #25
                y_label=r'$T_{\parallel}$',
                legend_label=r'$T_{\parallel,p2}$',
                color='deepskyblue' 
            )
        )

        # 26. Tpar_tot (Scatter, Size 5)
        self.Tpar_tot = plot_manager( # Total temperature parallel
            self.raw_data.get('Tpar_tot'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tpar_tot',
                subclass_name='Tpar_tot', # User list #26
                y_label=r'$T_\parallel$',
                legend_label=r'$T_\parallel$', 
                color='mediumspringgreen' 
            )
        )

        # 27. Tperp1 (Scatter, Size 5)
        self.Tperp1 = plot_manager( # Temperature perpendicular of the core
            self.raw_data.get('Tperp1'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tperp1',
                subclass_name='Tperp1', # User list #27
                y_label=r'$T_{\perp}$',
                legend_label=r'$T_{\perp,p1}$',
                color='hotpink' 
            )
        )

        # 28. Tperp2 (Scatter, Size 5)
        self.Tperp2 = plot_manager( # Temperature perpendicular of the beam
            self.raw_data.get('Tperp2'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tperp2',
                subclass_name='Tperp2', # User list #28
                y_label=r'$T_{\perp}$',
                legend_label=r'$T_{\perp,p2}$',
                color='deepskyblue' 
            )
        )

        # 29. Tperp_tot (Scatter, Size 5)
        self.Tperp_tot = plot_manager( # Total temperature perpendicular
            self.raw_data.get('Tperp_tot'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Tperp_tot',
                subclass_name='Tperp_tot', # User list #29
                y_label=r'$T_{\perp}$', 
                legend_label=r'$T_{\perp}$', 
                color='mediumspringgreen' 
            )
        )

        # 30. Temp_tot (Scatter, Size 5)
        self.Temp_tot = plot_manager( # Total temperature
            self.raw_data.get('Temp_tot'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='Temp_tot',
                subclass_name='Temp_tot', # User list #30
                y_label=r'$Temp_{tot}$', 
                legend_label=r'$T_{tot}$', 
                color='mediumspringgreen' 
            )
        )

        # 31. |qz_p| (Scatter, Size 5)
        self.abs_qz_p = plot_manager( # Absolute heat flux - ATTRIBUTE RENAMED to abs_qz_p
            self.raw_data.get('abs_qz_p'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='abs_qz_p',
                subclass_name='abs_qz_p', # MATCH ATTRIBUTE NAME (User list #31) - UPDATED
                y_label=r'$|Q_p| W/m^2$',
                legend_label=r'$|Q_p|$',
                color='mediumspringgreen'
            )
        )

        # 32. chi_p (Scatter, Size 5)
        self.chi_p = plot_manager( # Chi of whole proton fit
            self.raw_data.get('chi_p'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='chi_p',            
                subclass_name='chi_p',       # User list #32
                y_label=r'$\chi_p$',        
                legend_label=r'$\chi_p$',    
                color='rebeccapurple'       
            )
        )

        # 33. chi_p_norm (Scatter, Size 5)
        self.chi_p_norm = plot_manager( # Normalized chi of whole proton fit
            self.raw_data.get('chi_p_norm'),
            plot_options=self._create_fits_scatter_ploptions(
                var_name='chi_p_norm',
                subclass_name='chi_p_norm', # User list #33
                y_label=r'$\chi_p norm$', 
                legend_label=r'$\chi_p norm$', 
                color='rebeccapurple' 
            )
        )

        # 34. valfven_pfits (Time Series)
        self.valfven_pfits = plot_manager( # Alfven speed (from FITS params) - ATTRIBUTE NAME CHANGED
            self.raw_data.get('valfven'), # Still gets raw 'valfven' data
            plot_options=self._create_fits_scatter_ploptions(
                var_name='valfven',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='valfven_pfits', # User list #34 (Updated name)
                plot_type='time_series', 
                datetime_array=self.datetime_array,
                y_label=r'V$_{A}$ (km/s)', 
                legend_label=r'V$_{A}$'   
            )
        )


# Initialize with no data - this creates the global singleton instance
proton_fits = proton_fits_class(None)
print('initialized proton_fits class')
