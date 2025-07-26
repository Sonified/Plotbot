#plotbot/data_classes/psp_proton_fits_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging

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
# from plotbot.data_cubby import data_cubby # REMOVED
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
# Import get_data and proton instance for dependency loading (within method if needed)
# from ..get_data import get_data 
# from .psp_proton_classes import proton

class proton_fits_class:
    def __init__(self, imported_data):
        # Initialize raw_data with keys for BOTH raw inputs and calculated outputs
        object.__setattr__(self, 'raw_data', {
            # Raw inputs from data_import
            'np1': None,
            'np2': None,
            'Tperp1': None,
            'Tperp2': None,
            'Trat1': None,
            'Trat2': None,
            'vdrift': None,
            'B_inst_x': None,
            'B_inst_y': None,
            'B_inst_z': None,
            'vp1_x': None,
            'vp1_y': None,
            'vp1_z': None,
            'chi': None, # Source data key
            # Calculated outputs
            'qz_p': None,
            'vsw_mach': None, # Placeholder
            'beta_ppar': None,
            'beta_pperp': None,
            'ham_param': None,
            'n_tot': None,
            'np2_np1_ratio': None, # ADDED
            'vp1_mag': None,
            'vcm_x': None,
            'vcm_y': None,
            'vcm_z': None,
            'vcm_mag': None,
            'vdrift_abs': None, # ADDED
            'vdrift_va': None,
            'Trat_tot': None,
            'Tpar1': None,
            'Tpar2': None,
            'Tpar_tot': None,
            'Tperp_tot': None,
            'Temp_tot': None,
            '|qz_p|': None,
            'chi_p_norm': None, # ADDED
            'valfven': None,
            'B_mag': None,
            'bhat_x': None,
            'bhat_y': None,
            'bhat_z': None,
            'vp2_x': None,
            'vp2_y': None,
            'vp2_z': None,
            'vp2_mag': None,
            'qz_p_perp': None,
            'qz_p_par': None,
            'Vcm_mach': None,
            'Vp1_mach': None,
            'beta_p_tot': None,
            # Use 'chi_p' as the key for the processed/stored chi value
            'chi_p': None, 
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'data_type', 'psp_fld_l3_sf0_fit') # Explicitly set data_type
        object.__setattr__(self, '_current_operation_trange', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.debug("Calculating proton fits variables internally...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated proton fits variables.")

    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data.
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if original_requested_trange is not None:
            object.__setattr__(self, '_current_operation_trange', original_requested_trange)
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return

        # Check with DataTracker before recalculating
        from plotbot.data_tracker import global_tracker
        trange = None
        if hasattr(imported_data, 'times') and imported_data.times is not None and len(imported_data.times) > 1:
            import cdflib
            dt_array = cdflib.cdfepoch.to_datetime(imported_data.times)
            start = dt_array[0]
            end = dt_array[-1]
            # Format as string for DataTracker
            if hasattr(start, 'strftime'):
                start = start.strftime('%Y-%m-%d/%H:%M:%S.%f')
            else:
                start = str(start)  # Add this line to handle datetime64 objects
            if hasattr(end, 'strftime'):
                end = end.strftime('%Y-%m-%d/%H:%M:%S.%f')
            else:
                end = str(end)  # Add this line to handle datetime64 objects
            trange = [start, end]
        data_type = getattr(self, 'data_type', self.__class__.__name__)
        if trange and not global_tracker.is_calculation_needed(trange, data_type):
            print_manager.status(f"{data_type} already calculated for the time range: {trange}")
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
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                # Re-raise AttributeError if the internal/dunder method truly doesn't exist
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.debug(f'proton_fits __getattr__ triggered for: {name}')
        available_attrs = [attr for attr in dir(self) 
                           if isinstance(getattr(self, attr, None), plot_manager) 
                           and not attr.startswith('_')]
        error_message = f"'{name}' is not a recognized attribute, friend!"
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
        """Calculates derived FITS variables internally, fetching dependencies as needed."""
        # --- Import needed functions/instances within method to avoid top-level circular imports --- 
        # from ..get_data import get_data # NO LONGER NEEDED
        from ..data_import import import_data_function # Import directly
        from .psp_proton import proton # MODIFIED - Still need the proton class instance for attribute access
        from dateutil.parser import parse

        try:
            # imported_data is expected to be a DataObject instance
            if not hasattr(imported_data, 'data') or not hasattr(imported_data, 'times'):
                logging.error("Error in calculate_variables: imported_data is not a valid DataObject.")
                return # Abort if data object is invalid

            data_dict = imported_data.data # Access the dictionary within the DataObject
            self.time = np.asarray(imported_data.times) # TT2000 array

            if self.time is None or self.time.size == 0:
                 logging.error("Imported DataObject has empty or None 'times' attribute.")
                 self.datetime_array = None
                 return

            # Convert TT2000 back to datetime objects
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))

            # --- Determine Time Range Needed --- 
            fits_start_dt_np = self.datetime_array.min()
            fits_end_dt_np = self.datetime_array.max()
            fits_start_dt = pd.Timestamp(fits_start_dt_np)
            fits_end_dt = pd.Timestamp(fits_end_dt_np)
            trange_for_deps_str = [
                fits_start_dt.strftime('%Y-%m-%d/%H:%M:%S.%f'), 
                fits_end_dt.strftime('%Y-%m-%d/%H:%M:%S.%f')
            ]
            print_manager.debug(f"FITS Calculation: Determined dependency trange: {trange_for_deps_str}")

            # --- Fetch Dependency: Proton Moments (spi_sf00_l3_mom) --- 
            print_manager.debug("FITS Calculation: Importing proton moment data directly...")
            proton_data_available = False # Default
            vsw_mom_data = None
            proton_times = None
            try:
                # Directly import the required data type
                proton_data_obj = import_data_function(trange_for_deps_str, 'spi_sf00_l3_mom') 
                
                # --- ADDED DEBUGGING --- 
                if proton_data_obj and hasattr(proton_data_obj, 'times') and hasattr(proton_data_obj, 'data'):
                    print_manager.debug(" Checking proton data availability post import_data_function call:")
                    proton_times = proton_data_obj.times # TT2000 times
                    proton_data_dict = proton_data_obj.data
                    
                    if proton_times is not None:
                        print_manager.debug(f"  proton_times length: {len(proton_times)}")
                        if len(proton_times) > 0:
                             proton_dt_array = np.array(cdflib.cdfepoch.to_datetime(proton_times))
                             print_manager.debug(f"  proton time range: {proton_dt_array.min()} to {proton_dt_array.max()}")
                    else:
                        print_manager.debug("  proton_times is None.")
                    
                    # Need to access v_sw data (check exact key in data_types? likely VEL_RTN_SUN -> v_sw)
                    # Let's assume the calculation within proton class stores it as 'v_sw'
                    # We might need to calculate it here if import_data doesn't
                    # For now, let's try getting 'VEL_RTN_SUN' and calculating magnitude
                    vel_rtn_sun = proton_data_dict.get('VEL_RTN_SUN')
                    if vel_rtn_sun is not None and vel_rtn_sun.shape[1] == 3:
                         vsw_mom_data = np.sqrt(vel_rtn_sun[:, 0]**2 + vel_rtn_sun[:, 1]**2 + vel_rtn_sun[:, 2]**2)
                         print_manager.debug(f"  Calculated vsw_mom_data length: {len(vsw_mom_data)}")
                         valid_vsw = ~np.isnan(vsw_mom_data)
                         print_manager.debug(f"  vsw_mom_data valid points: {np.sum(valid_vsw)}")
                         proton_data_available = (proton_times is not None and len(proton_times) > 0 and 
                                                  vsw_mom_data is not None and len(vsw_mom_data) > 0)
                    else:
                         print_manager.debug("  VEL_RTN_SUN data not found or has wrong shape in proton_data_obj.")
                else:
                    print_manager.debug("  import_data_function returned None for proton data.")
                # --- END DEBUGGING ---

            except Exception as import_e:
                logging.error(f"Error calling import_data_function for proton dependency: {import_e}")
                # proton_data_available remains False
            
            vsw_mom_aligned = None # Initialize
            if proton_data_available:
                print_manager.debug("FITS Calculation: Proton data found. Aligning v_sw...")
                try:
                    # --- Align vsw_mom data to FITS time grid --- 
                    # Convert FITS TT2000 times to Unix timestamps
                    fits_times_unix = np.array([cdflib.cdfepoch.unixtime(t) for t in self.time])
                    # Convert Proton TT2000 times to Unix timestamps
                    proton_times_unix = np.array([cdflib.cdfepoch.unixtime(t) for t in proton_times])
                    
                    # Handle potential NaNs in proton data before interpolation
                    valid_proton_mask = ~np.isnan(proton_times_unix) & ~np.isnan(vsw_mom_data)
                    if np.sum(valid_proton_mask) > 1: # Need at least 2 points to interpolate
                        vsw_mom_aligned = np.interp(
                            fits_times_unix, 
                            proton_times_unix[valid_proton_mask],
                            vsw_mom_data[valid_proton_mask],
                            left=np.nan, 
                            right=np.nan
                        )
                        print_manager.debug(f"Alignment successful. Shape: {vsw_mom_aligned.shape}")
                    else:
                        print_manager.warning("Not enough valid proton data points to perform interpolation.")
                        vsw_mom_aligned = np.full_like(self.datetime_array, np.nan, dtype=float)

                except Exception as interp_e:
                    logging.error(f"Error during vsw_mom alignment/interpolation: {interp_e}")
                    vsw_mom_aligned = np.full_like(self.datetime_array, np.nan, dtype=float)
            else:
                print_manager.warning("FITS Calculation: Proton moment data (v_sw) not available or empty. vsw_mach will be NaN.")
                vsw_mom_aligned = np.full_like(self.datetime_array, np.nan, dtype=float)

            # --- Extract raw FITS data (as before) ---
            np1 = data_dict.get('np1')
            np2 = data_dict.get('np2')
            Tperp1 = data_dict.get('Tperp1')
            Tperp2 = data_dict.get('Tperp2')
            Trat1 = data_dict.get('Trat1')
            Trat2 = data_dict.get('Trat2')
            vdrift = data_dict.get('vdrift')
            B_inst_x = data_dict.get('B_inst_x')
            B_inst_y = data_dict.get('B_inst_y')
            B_inst_z = data_dict.get('B_inst_z')
            vp1_x = data_dict.get('vp1_x')
            vp1_y = data_dict.get('vp1_y')
            vp1_z = data_dict.get('vp1_z')

            # Check if any essential raw data is missing
            essential_raw = [np1, np2, Tperp1, Tperp2, Trat1, Trat2, vdrift,
                            B_inst_x, B_inst_y, B_inst_z, vp1_x, vp1_y, vp1_z]
            if any(v is None for v in essential_raw):
                missing_keys = [k for k, v in data_dict.items() if v is None and k in [
                    'np1', 'np2', 'Tperp1', 'Tperp2', 'Trat1', 'Trat2', 'vdrift',
                    'B_inst_x', 'B_inst_y', 'B_inst_z', 'vp1_x', 'vp1_y', 'vp1_z'
                ]]
                logging.error(f"Essential raw data missing from imported_data: {missing_keys}. Cannot perform calculations.")
                # Clear potentially calculated fields from previous runs
                for key in self.raw_data:
                    if key not in data_dict: # Don't clear raw inputs
                        self.raw_data[key] = None
                return

            # --- Filtering (Apply filtering similar to the original function) ---
            filter_conditions = (
                (np1 > 10) &
                (np2 > 10) &
                (Tperp1 > .03) &
                (Tperp2 > .03) &
                (Trat1 > .01) &
                (Trat2 > .01) &
                (Trat1 != 30) &
                (Trat2 != 30) &
                (Trat1 != 2.0) &
                (Trat2 != 2.0) &
                (Trat1 != 1.0) &
                (Trat2 != 1.0) &
                (vdrift != 10000) &
                (vdrift != -10000)
            )
            mask = filter_conditions

            # Apply NaN mask to all input arrays where the mask is False
            # Important: Create copies or ensure subsequent calculations use masked arrays
            raw_arrays_to_mask = {
                'np1': np1, 'np2': np2, 'Tperp1': Tperp1, 'Tperp2': Tperp2,
                'Trat1': Trat1, 'Trat2': Trat2, 'vdrift': vdrift, 'B_inst_x': B_inst_x,
                'B_inst_y': B_inst_y, 'B_inst_z': B_inst_z, 'vp1_x': vp1_x,
                'vp1_y': vp1_y, 'vp1_z': vp1_z
            }
            masked_data = {}
            for key, arr in raw_arrays_to_mask.items():
                # Ensure array is float before assigning NaN
                if not np.issubdtype(arr.dtype, np.floating):
                     masked_data[key] = arr.astype(float)
                else:
                     masked_data[key] = arr.copy()
                masked_data[key][~mask] = np.nan

            # Use masked data for subsequent calculations
            np1 = masked_data['np1']
            np2 = masked_data['np2']
            Tperp1 = masked_data['Tperp1']
            Tperp2 = masked_data['Tperp2']
            Trat1 = masked_data['Trat1']
            Trat2 = masked_data['Trat2']
            vdrift = masked_data['vdrift']
            B_inst_x = masked_data['B_inst_x']
            B_inst_y = masked_data['B_inst_y']
            B_inst_z = masked_data['B_inst_z']
            vp1_x = masked_data['vp1_x']
            vp1_y = masked_data['vp1_y']
            vp1_z = masked_data['vp1_z']

            # --- Perform Derived Parameter Calculations (transplanted logic) ---

            # Calculate magnitudes and unit vectors
            vp1_mag = np.sqrt(vp1_x**2 + vp1_y**2 + vp1_z**2)
            with np.errstate(invalid='ignore'): # Ignore warnings for sqrt(NaN)
                B_mag = np.sqrt(B_inst_x**2 + B_inst_y**2 + B_inst_z**2)

            # Calculate magnetic field unit vector components (handle potential division by zero/NaN)
            with np.errstate(divide='ignore', invalid='ignore'):
                b_mag_safe = np.where(B_mag != 0, B_mag, np.nan)
                bhat_x = B_inst_x / b_mag_safe
                bhat_y = B_inst_y / b_mag_safe
                bhat_z = B_inst_z / b_mag_safe

            # Total density and temperatures
            n_tot = np1 + np2
            with np.errstate(divide='ignore', invalid='ignore'):
                n_tot_safe = np.where(n_tot != 0, n_tot, np.nan)
                Tperp_tot = (np1 * Tperp1 + np2 * Tperp2) / n_tot_safe

                # Calculate parallel temperatures from ratios (handle division by zero/NaN)
                Trat1_safe = np.where(Trat1 != 0, Trat1, np.nan)
                Trat2_safe = np.where(Trat2 != 0, Trat2, np.nan)
                Tpar1 = Tperp1 / Trat1_safe
                Tpar2 = Tperp2 / Trat2_safe

                # Calculate total parallel temperature (includes drift term)
                drift_term = (np1 * np2 / n_tot_safe) * m * (vdrift**2)
                Tpar_tot = (np1 * Tpar1 + np2 * Tpar2 + drift_term) / n_tot_safe

                # Calculate total temperature ratio and average temperature
                Tpar_tot_safe = np.where(Tpar_tot != 0, Tpar_tot, np.nan)
                Trat_tot = Tperp_tot / Tpar_tot_safe
                Temp_tot = (2 * Tperp_tot + Tpar_tot) / 3

            # Center-of-mass velocity
            with np.errstate(divide='ignore', invalid='ignore'):
                n_tot_safe = np.where(n_tot != 0, n_tot, np.nan)
                frac_p2 = np2 / n_tot_safe
                vcm_x = vp1_x + frac_p2 * vdrift * bhat_x
                vcm_y = vp1_y + frac_p2 * vdrift * bhat_y
                vcm_z = vp1_z + frac_p2 * vdrift * bhat_z
            vcm_mag = np.sqrt(vcm_x**2 + vcm_y**2 + vcm_z**2)

            # Beam velocity (vp2)
            vp2_x = vp1_x + vdrift * bhat_x
            vp2_y = vp1_y + vdrift * bhat_y
            vp2_z = vp1_z + vdrift * bhat_z
            vp2_mag = np.sqrt(vp2_x**2 + vp2_y**2 + vp2_z**2)

            # Heat flux calculation (handle potential NaNs)
            with np.errstate(divide='ignore', invalid='ignore'):
                vt1perp2 = 2 * Tperp1 / m
                vt2perp2 = 2 * Tperp2 / m
                vt1par2 = 2 * Tpar1 / m
                vt2par2 = 2 * Tpar2 / m
                fac = 1.602E-10 # Conversion factor to W/m^2
                n_tot_safe = np.where(n_tot != 0, n_tot, np.nan)
                density_term = (np1 * np2) / n_tot_safe
                temp_diff_term = 1.5 * (vt2par2 - vt1par2)
                drift_squared_term = vdrift**2 * (np1**2 - np2**2) / (n_tot_safe**2)
                perp_temp_diff = (vt2perp2 - vt1perp2)

                qz_p = fac * 0.5 * m * density_term * vdrift * (temp_diff_term + drift_squared_term + perp_temp_diff)
                qz_p_abs = np.abs(qz_p)

            # Normalized heat flux (handle potential division by zero/NaN)
            with np.errstate(divide='ignore', invalid='ignore'):
                n_tot_safe = np.where(n_tot > 0, n_tot, np.nan)
                vt_perp_tot_sq = 2 * (np1 * Tperp1 + np2 * Tperp2) / (m * n_tot_safe)
                vt_par_tot_sq = 2 * (np1 * Tpar1+ np2 * Tpar2 + m * vdrift**2 * (np1 * np2)/n_tot_safe) / (m * n_tot_safe)

                vt_perp_tot = np.sqrt(vt_perp_tot_sq)
                vt_par_tot = np.sqrt(vt_par_tot_sq)

                denom_perp = m * n_tot_safe * vt_perp_tot**3
                denom_par = m * n_tot_safe * vt_par_tot**3

                denom_perp_safe = np.where(denom_perp != 0, denom_perp, np.nan)
                denom_par_safe = np.where(denom_par != 0, denom_par, np.nan)

                qz_p_perp = qz_p / denom_perp_safe
                qz_p_par = qz_p / denom_par_safe

            # Alfven speed, Mach numbers, Beta (MODIFIED SECTION) 
            with np.errstate(divide='ignore', invalid='ignore'):
                n_tot_safe = np.where(n_tot > 0, n_tot, np.nan)
                valfven = 21.8 * B_mag / np.sqrt(n_tot_safe)

                valfven_safe = np.where(valfven != 0, valfven, np.nan)
                vdrift_va = vdrift / valfven_safe
                Vcm_mach = vcm_mag / valfven_safe
                Vp1_mach = vp1_mag / valfven_safe
                
                # --- USE ALIGNED vsw_mom_aligned --- 
                if vsw_mom_aligned is not None:
                    vsw_mach = vsw_mom_aligned / valfven_safe # Calculate using aligned SPI speed
                else:
                    # Fallback if alignment failed or data wasn't available
                    vsw_mach = np.full_like(valfven, np.nan) 
                # -------------------------------------

                # Plasma Beta calculations
                beta_denom = (1e-5 * B_mag)**2
                beta_denom_safe = np.where(beta_denom > 0, beta_denom, np.nan)
                beta_ppar = (4.03E-11 * n_tot_safe * Tpar_tot) / beta_denom_safe
                beta_pperp = (4.03E-11 * n_tot_safe * Tperp_tot) / beta_denom_safe
                beta_p_tot = np.sqrt(beta_ppar**2 + beta_pperp**2)

            # Hammerhead diagnostic
            with np.errstate(divide='ignore', invalid='ignore'):
                Trat_tot_safe = np.where(Trat_tot != 0, Trat_tot, np.nan)
                Tperp1_safe = np.where(Tperp1 != 0, Tperp1, np.nan)
                ham_param = (Tperp2 / Tperp1_safe) / Trat_tot_safe

            # --- Extract chi if available ---
            chi_p = data_dict.get('chi') # Get source data using key 'chi', store locally as chi_p

            # --- Calculate Additional Ratios/Values ---
            with np.errstate(divide='ignore', invalid='ignore'):
                np1_safe = np.where(np1 != 0, np1, np.nan) # Avoid division by zero
                np2_np1_ratio = np2 / np1_safe

            vdrift_abs = np.abs(vdrift)

            # chi_p_norm (use local variable chi_p which holds masked 'chi' data)
            with np.errstate(divide='ignore', invalid='ignore'):
                 # Ensure chi_p (the masked data from 'chi' column) exists before dividing
                 if chi_p is not None:
                      chi_p_norm = chi_p / 2038.0 # Ensure float division
                 else:
                      # If source 'chi' column was missing, norm is also undefined
                      chi_p_norm = np.full_like(np1, np.nan) if np1 is not None else None

            # --- Store calculated results in self.raw_data ---
            # Store raw inputs as well for completeness/debugging
            self.raw_data['np1'] = np1
            self.raw_data['np2'] = np2
            self.raw_data['Tperp1'] = Tperp1
            self.raw_data['Tperp2'] = Tperp2
            self.raw_data['Trat1'] = Trat1
            self.raw_data['Trat2'] = Trat2
            self.raw_data['vdrift'] = vdrift
            self.raw_data['B_inst_x'] = B_inst_x
            self.raw_data['B_inst_y'] = B_inst_y
            self.raw_data['B_inst_z'] = B_inst_z
            self.raw_data['vp1_x'] = vp1_x
            self.raw_data['vp1_y'] = vp1_y
            self.raw_data['vp1_z'] = vp1_z
            # Store chi if it was found
            if chi_p is not None: # Use local chi_p
                # Apply the same NaN mask based on filter conditions using local chi_p
                if not np.issubdtype(chi_p.dtype, np.floating):
                    chi_p_masked = chi_p.astype(float)
                else:
                    chi_p_masked = chi_p.copy()
                chi_p_masked[~mask] = np.nan
                # STORE under key 'chi_p' using data from chi_p_masked
                self.raw_data['chi_p'] = chi_p_masked # STORE USING KEY 'chi_p'
            else:
                # Ensure the key exists even if data wasn't found in source
                self.raw_data['chi_p'] = None # Store None under key 'chi_p'
                # Warning still refers to the source column name
                logging.warning("Column 'chi' not found in imported FITS data.") 

            # Store calculated values
            self.raw_data['beta_ppar'] = beta_ppar
            self.raw_data['beta_pperp'] = beta_pperp
            self.raw_data['valfven'] = valfven
            self.raw_data['qz_p'] = qz_p
            self.raw_data['ham_param'] = ham_param
            self.raw_data['vp1_mag'] = vp1_mag
            self.raw_data['vsw_mach'] = vsw_mach # Store the calculated or NaN value
            self.raw_data['B_mag'] = B_mag
            self.raw_data['bhat_x'] = bhat_x
            self.raw_data['bhat_y'] = bhat_y
            self.raw_data['bhat_z'] = bhat_z
            self.raw_data['n_tot'] = n_tot
            self.raw_data['Tperp_tot'] = Tperp_tot
            self.raw_data['Tpar1'] = Tpar1
            self.raw_data['Tpar2'] = Tpar2
            self.raw_data['Tpar_tot'] = Tpar_tot
            self.raw_data['Trat_tot'] = Trat_tot
            self.raw_data['Temp_tot'] = Temp_tot
            self.raw_data['vcm_x'] = vcm_x
            self.raw_data['vcm_y'] = vcm_y
            self.raw_data['vcm_z'] = vcm_z
            self.raw_data['vcm_mag'] = vcm_mag
            self.raw_data['vp2_x'] = vp2_x
            self.raw_data['vp2_y'] = vp2_y
            self.raw_data['vp2_z'] = vp2_z
            self.raw_data['vp2_mag'] = vp2_mag
            self.raw_data['abs_qz_p'] = qz_p_abs
            self.raw_data['qz_p_perp'] = qz_p_perp
            self.raw_data['qz_p_par'] = qz_p_par
            self.raw_data['vdrift_va'] = vdrift_va
            self.raw_data['Vcm_mach'] = Vcm_mach
            self.raw_data['Vp1_mach'] = Vp1_mach
            self.raw_data['beta_p_tot'] = beta_p_tot
            self.raw_data['np2_np1_ratio'] = np2_np1_ratio
            self.raw_data['vdrift_abs'] = vdrift_abs
            self.raw_data['chi_p_norm'] = chi_p_norm

            # --- Store RAW input 'chi' data separately --- 
            # (This assumes chi_p is the masked version from earlier)
            raw_chi = data_dict.get('chi') # Get original raw chi again
            self.raw_data['chi'] = raw_chi if raw_chi is not None else None

        except Exception as e:
            # --- ADDED DEBUG PRINT FOR HIDDEN ERRORS --- 
            print_manager.error(f"!!! CAUGHT UNEXPECTED ERROR IN calculate_variables: {e}")
            # --- END DEBUG PRINT --- 
            logging.error(f"Error during internal FITS calculation in proton_fits_class.calculate_variables: {e}")
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

    def _create_fits_scatter_ploptions(self, var_name, subclass_name, y_label, legend_label, color):
        """Helper method to create ploptions for standard FITS scatter plots."""
        return ploptions(
            var_name=var_name,
            data_type='proton_fits',
            class_name='proton_fits',
            subclass_name=subclass_name,
            plot_type='scatter',         # Default
            datetime_array=self.datetime_array, # Default
            y_label=y_label,
            legend_label=legend_label,
            color=color,
            y_scale='linear',          # Default
            marker_style='*',           # Default (star marker)
            marker_size=5,             # Default
            alpha=0.7,                 # Default
            y_limit=None               # Default
        )

    def set_ploptions(self):
        """Initialize or update plot_manager instances with data and plot options."""
        
        # Initialize plot managers in the order specified by user (1-34)

        # 1. qz_p (Scatter, Size 20)
        self.qz_p = plot_manager( # Heat flux of the proton beam
            self.raw_data.get('qz_p'),
            plot_options=ploptions(
                var_name='qz_p',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='qz_p', # User list #1
                plot_type='scatter',
                datetime_array=self.datetime_array,
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
            plot_options=ploptions(
                var_name='vsw_mach', 
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vsw_mach_pfits', # User list #2
                plot_type='scatter',
                datetime_array=self.datetime_array,
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
            plot_options=ploptions(
                var_name='beta_ppar',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='beta_ppar_pfits', # User list #3 (Updated)
                plot_type='scatter', 
                datetime_array=self.datetime_array,
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
            plot_options=ploptions(
                var_name='beta_pperp', 
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='beta_pperp_pfits', # User list #4 (Updated)
                plot_type='scatter',
                datetime_array=self.datetime_array,
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
            plot_options=ploptions(
                var_name='ham_param',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='ham_param', # User list #5
                plot_type='scatter',
                datetime_array=self.datetime_array,
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
            plot_options=ploptions(
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

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)


# Initialize with no data - this creates the global singleton instance
proton_fits = proton_fits_class(None)
print('initialized proton_fits class')
