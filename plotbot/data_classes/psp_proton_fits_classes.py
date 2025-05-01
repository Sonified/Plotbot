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
            # 'vdrift_va_p2p1_apfits': None, # Placeholder for property access
            # 'abs_vdrift_va_p2p1_apfits': None, # Placeholder for property access
        })
        # Initialize time attributes
        object.__setattr__(self, 'time', None) # Will hold TT2000 epoch
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

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
        # FIXED: Store state for ALL raw_data keys, not just non-None ones
        for subclass_name in self.raw_data.keys():  # Use all keys, just like mag classes
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")
                    # <<< ADDED >>> Debug print for n_tot state being stored
                    if subclass_name == 'n_tot':
                        stored_dt_array = current_state[subclass_name].get('datetime_array', 'MISSING')
                        print(f"DEBUG update STORE STATE n_tot: Storing datetime_array (type={type(stored_dt_array)}, is None={stored_dt_array is None or stored_dt_array == 'MISSING'})")
                        if stored_dt_array is not None and stored_dt_array != 'MISSING': print(f"DEBUG update STORE STATE n_tot: Stored datetime_array len: {len(stored_dt_array)}")

        # <<< ADDED >>> Check state BEFORE calculate_variables/set_ploptions
        print(f"DEBUG update PRE-UPDATE: Entering main update section.")
        pre_update_dt_array = getattr(self, 'datetime_array', 'ATTRIBUTE_MISSING')
        pre_update_n_tot_raw = self.raw_data.get('n_tot', 'KEY_MISSING')
        print(f"DEBUG update PRE-UPDATE: self.datetime_array is None: {pre_update_dt_array is None or pre_update_dt_array == 'ATTRIBUTE_MISSING'}")
        if pre_update_dt_array is not None and pre_update_dt_array != 'ATTRIBUTE_MISSING': print(f"DEBUG update PRE-UPDATE: datetime_array len: {len(pre_update_dt_array)}")
        print(f"DEBUG update PRE-UPDATE: self.raw_data['n_tot'] is None: {pre_update_n_tot_raw is None or pre_update_n_tot_raw == 'KEY_MISSING'}")
        if pre_update_n_tot_raw is not None and pre_update_n_tot_raw != 'KEY_MISSING': print(f"DEBUG update PRE-UPDATE: n_tot_raw shape: {pre_update_n_tot_raw.shape if hasattr(pre_update_n_tot_raw, 'shape') else 'N/A'}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_ploptions()                                                  # Recreate plot managers
        
        # <<< ADDED >>> Check state AFTER calculate_variables/set_ploptions
        print(f"DEBUG update POST-UPDATE: Finished calculate_variables/set_ploptions.")
        post_update_dt_array = getattr(self, 'datetime_array', 'ATTRIBUTE_MISSING')
        post_update_n_tot_pm = getattr(self, 'n_tot', None)
        post_update_n_tot_raw = self.raw_data.get('n_tot', 'KEY_MISSING')
        print(f"DEBUG update POST-UPDATE: self.datetime_array is None: {post_update_dt_array is None or post_update_dt_array == 'ATTRIBUTE_MISSING'}")
        if post_update_dt_array is not None and post_update_dt_array != 'ATTRIBUTE_MISSING': print(f"DEBUG update POST-UPDATE: datetime_array len: {len(post_update_dt_array)}")
        print(f"DEBUG update POST-UPDATE: self.raw_data['n_tot'] is None: {post_update_n_tot_raw is None or post_update_n_tot_raw == 'KEY_MISSING'}")
        if post_update_n_tot_raw is not None and post_update_n_tot_raw != 'KEY_MISSING': print(f"DEBUG update POST-UPDATE: n_tot_raw shape: {post_update_n_tot_raw.shape if hasattr(post_update_n_tot_raw, 'shape') else 'N/A'}")
        print(f"DEBUG update POST-UPDATE: self.n_tot (plot manager) is None: {post_update_n_tot_pm is None}")
        if post_update_n_tot_pm:
            pm_dt_array = getattr(post_update_n_tot_pm.plot_options, 'datetime_array', 'ATTRIBUTE_MISSING')
            pm_data = getattr(post_update_n_tot_pm, 'data', 'ATTRIBUTE_MISSING')
            print(f"DEBUG update POST-UPDATE: self.n_tot.plot_options.datetime_array is None: {pm_dt_array is None or pm_dt_array == 'ATTRIBUTE_MISSING'}")
            if pm_dt_array is not None and pm_dt_array != 'ATTRIBUTE_MISSING': print(f"DEBUG update POST-UPDATE: self.n_tot.plot_options.datetime_array len: {len(pm_dt_array)}")
            print(f"DEBUG update POST-UPDATE: self.n_tot.data is None: {pm_data is None or pm_data == 'ATTRIBUTE_MISSING'}")
            if pm_data is not None and pm_data != 'ATTRIBUTE_MISSING': print(f"DEBUG update POST-UPDATE: self.n_tot.data shape: {pm_data.shape if hasattr(pm_data, 'shape') else 'N/A'}")

        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():                    # Restore saved states
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                
                # <<< ADDED >>> Debug for n_tot before restoring state
                if subclass_name == 'n_tot':
                    print(f"DEBUG update RESTORE n_tot: Entering state restore for n_tot.")
                    state_dt_array = state.get('datetime_array', 'MISSING_KEY')
                    var_dt_array_before = getattr(var.plot_options, 'datetime_array', 'ATTRIBUTE_MISSING') if hasattr(var, 'plot_options') else 'NoPlotOptions'
                    print(f"DEBUG update RESTORE n_tot: State dict contains datetime_array: {'datetime_array' in state}")
                    if 'datetime_array' in state: print(f"DEBUG update RESTORE n_tot: state['datetime_array'] is None: {state_dt_array is None}")
                    print(f"DEBUG update RESTORE n_tot: var.plot_options.datetime_array BEFORE restore is None: {var_dt_array_before is None or var_dt_array_before == 'ATTRIBUTE_MISSING' or var_dt_array_before == 'NoPlotOptions'}")
                    if var_dt_array_before is not None and var_dt_array_before not in ['ATTRIBUTE_MISSING', 'NoPlotOptions']: print(f"DEBUG update RESTORE n_tot: var.plot_options.datetime_array BEFORE restore len: {len(var_dt_array_before)}")
                
                # Restore individual plot_options attributes, SKIPPING datetime_array AND y_limit
                for attr, value in state.items():
                    # Skip datetime_array and y_limit explicitly
                    if attr == 'datetime_array' or attr == 'y_limit':
                        if subclass_name == 'n_tot': print(f"DEBUG update RESTORE n_tot: Explicitly skipping setattr for {attr}")
                        continue 
                    
                    if hasattr(var.plot_options, attr):
                        if subclass_name == 'n_tot': print(f"DEBUG update RESTORE n_tot: Setting var.plot_options.{attr}")
                        setattr(var.plot_options, attr, value)

                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
                
        # <<< ADDED DEBUG: Check datetime_array AFTER restoration >>>
        post_restore_dt_array = getattr(self, 'datetime_array', None)
        print_manager.debug(f"  [DEBUG] AFTER restore loop: self.datetime_array is None: {post_restore_dt_array is None}")
        if post_restore_dt_array is not None: print_manager.debug(f"  [DEBUG] AFTER restore loop: self.datetime_array length: {len(post_restore_dt_array)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
        # ADDED: Stash the updated instance back into data_cubby
        data_cubby.stash(self, class_name='proton_fits') 

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
            # <<< ADD DEBUG HERE >>>
            print(f"DEBUG calculate_variables: Raw self.time type={type(self.time)}, shape={self.time.shape if hasattr(self.time, 'shape') else 'N/A'}")
            print(f"DEBUG calculate_variables: Raw data_dict keys={list(data_dict.keys()) if data_dict else 'None'}")
            if data_dict and 'n_tot' in data_dict:
                n_tot_val = data_dict['n_tot']
                print(f"DEBUG calculate_variables: Raw data_dict['n_tot'] type={type(n_tot_val)}, shape={n_tot_val.shape if hasattr(n_tot_val, 'shape') else 'N/A'}")
                # <<< ADDED: Print first few values >>>
                print(f"DEBUG calculate_variables: Raw n_tot values (first 5): {n_tot_val[:5] if hasattr(n_tot_val, '__len__') and len(n_tot_val) > 0 else 'N/A'}")

            if self.time is None or self.time.size == 0: # Moved this check earlier
                 logging.error(f"{self.__class__.__name__}: Imported DataObject has empty or None 'times' attribute.")
                 self.datetime_array = None
                 for key in self.raw_data: self.raw_data[key] = None
                 return

            # <<< ADDED: Print first few time values >>>
            print(f"DEBUG calculate_variables: Raw self.time values (first 5): {self.time[:5] if hasattr(self.time, '__len__') and len(self.time) > 0 else 'N/A'}")

            # <<< REVERTING >>> Using default numpy typing for datetime conversion
            datetime_list = cdflib.cdfepoch.to_datetime(self.time)
            # <<< RE-APPLYING FIX >>> Explicitly set dtype for numpy datetime conversion
            self.datetime_array = np.array(datetime_list, dtype='datetime64[ns]')
            
            # <<< ADD DEBUG HERE >>>
            print(f"DEBUG calculate_variables: Converted datetime_list type={type(datetime_list)}, len={len(datetime_list) if isinstance(datetime_list, list) else 'N/A'}")
            # <<< ADDED: Print first few datetime values >>>
            if isinstance(datetime_list, list) and len(datetime_list) > 0:
                print(f"DEBUG calculate_variables: Converted datetime_list values (first 5): {datetime_list[:5]}")
                
            # <<< ADD DEBUG HERE >>>
            print(f"DEBUG calculate_variables: Final self.datetime_array type={type(self.datetime_array)}, shape={self.datetime_array.shape if hasattr(self.datetime_array, 'shape') else 'N/A'}")
            # <<< ADDED: Print first few final datetime values >>>
            if hasattr(self.datetime_array, '__len__') and len(self.datetime_array) > 0:
                print(f"DEBUG calculate_variables: Final self.datetime_array values (first 5): {self.datetime_array[:5]}")
                # <<< ADDED >>> Check dtype explicitly
                if hasattr(self.datetime_array, 'dtype'):
                    print(f"DEBUG calculate_variables: Final self.datetime_array dtype: {self.datetime_array.dtype}")
                else:
                    print("DEBUG calculate_variables: Final self.datetime_array has no dtype attribute")
            else:
                 print("DEBUG calculate_variables: Final self.datetime_array is None or empty after creation")

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
                     # <<< MODIFIED: Force float64 conversion >>>
                     extracted_data[key] = np.asarray(data_val, dtype=np.float64)
                     # Add a debug print specifically for n_tot type after conversion
                     if key == 'n_tot':
                         print(f"DEBUG calculate_variables: n_tot type AFTER float64 cast: {extracted_data[key].dtype}")
                     # print_manager.debug(f"  Extracted {key}, shape: {extracted_data[key].shape}, type: {extracted_data[key].dtype}") # Verbose
                elif key not in vars_to_calculate: # If missing and not planned for calculation
                     potential_missing_keys.append(key)
                     extracted_data[key] = None # Set to None
                else:
                     extracted_data[key] = None # Placeholder for calculation

            # --- ADDED: Extract Vector Components ---
            vector_keys = {
                'vp1': ['vp1_x', 'vp1_y', 'vp1_z'],
                'vp2': ['vp2_x', 'vp2_y', 'vp2_z'],
                'vcm': ['vcm_x', 'vcm_y', 'vcm_z'],
                'B_inst': ['B_inst_x', 'B_inst_y', 'B_inst_z'],
                'B_SC': ['B_SC_x', 'B_SC_y', 'B_SC_z'],
                'bhat_inst': ['bhat_inst_x', 'bhat_inst_y', 'bhat_inst_z']
            }

            for vec_key, comp_keys in vector_keys.items():
                vector_data = extracted_data.get(vec_key)
                # Check if vector data exists, is 2D, and has 3 columns
                if vector_data is not None and vector_data.ndim == 2 and vector_data.shape[1] == 3:
                    # Check if component keys exist in raw_data definition before assigning
                    if comp_keys[0] in self.raw_data: extracted_data[comp_keys[0]] = vector_data[:, 0]
                    if comp_keys[1] in self.raw_data: extracted_data[comp_keys[1]] = vector_data[:, 1]
                    if comp_keys[2] in self.raw_data: extracted_data[comp_keys[2]] = vector_data[:, 2]
                    print_manager.debug(f"  Extracted components for {vec_key}.")
                else:
                    # Set components to None if vector is missing/malformed, but only if keys exist
                    if comp_keys[0] in self.raw_data: extracted_data[comp_keys[0]] = None
                    if comp_keys[1] in self.raw_data: extracted_data[comp_keys[1]] = None
                    if comp_keys[2] in self.raw_data: extracted_data[comp_keys[2]] = None
                    if vec_key in extracted_data and extracted_data[vec_key] is not None: # Only warn if vector was present but malformed
                         print_manager.warning(f"Vector '{vec_key}' has unexpected shape {vector_data.shape if vector_data is not None else 'None'}, cannot extract components.")

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
                # pass # Removed pass, debug statement provides the line

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

            # --- ADDED: Calculate abs_qz_p ---
            qz_p = extracted_data.get('qz_p')
            if qz_p is not None:
                extracted_data['abs_qz_p'] = np.abs(qz_p)
                print_manager.debug("  Calculated abs_qz_p.")
            else:
                extracted_data['abs_qz_p'] = None

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

            # --- Placeholder for vsw_mach (Requires external dependency) --- 
            # TODO: Implement fetching spi_sf00_l3_mom and aligning if vsw_mach is needed
            print_manager.debug("Skipping vsw_mach calculation (requires external dependency).")
            extracted_data['vsw_mach'] = None 

            # --- 4. Store Final Data --- 
            for key, value in extracted_data.items():
                if key in self.raw_data:
                    self.raw_data[key] = value
                    # <<< ADDED >>> Debug print for n_tot specifically when stored
                    if key == 'n_tot':
                        n_tot_val_final = self.raw_data.get('n_tot')
                        print(f"DEBUG calculate_variables: Storing self.raw_data['n_tot'] type={type(n_tot_val_final)}, shape={n_tot_val_final.shape if hasattr(n_tot_val_final, 'shape') else 'N/A'}")
                        if n_tot_val_final is not None and hasattr(n_tot_val_final, '__len__') and len(n_tot_val_final) > 0:
                             print(f"DEBUG calculate_variables: Stored n_tot values (first 5): {n_tot_val_final[:5]}")
                        elif n_tot_val_final is None:
                             print("DEBUG calculate_variables: Stored n_tot is None")
                        else:
                             print("DEBUG calculate_variables: Stored n_tot is not None but empty or unsized")

            if self.datetime_array is None:
                print_manager.error(f"{self.__class__.__name__}: No valid time array after processing.")
            
            # <<< ADDED >>> Check state right before exiting calculate_variables
            print(f"DEBUG calculate_variables END: Exiting method.")
            final_dt_array = getattr(self, 'datetime_array', None)
            final_n_tot_raw = self.raw_data.get('n_tot')
            print(f"DEBUG calculate_variables END: datetime_array is None: {final_dt_array is None}")
            if final_dt_array is not None: print(f"DEBUG calculate_variables END: datetime_array len: {len(final_dt_array)}")
            print(f"DEBUG calculate_variables END: raw_data['n_tot'] is None: {final_n_tot_raw is None}")
            if final_n_tot_raw is not None: print(f"DEBUG calculate_variables END: raw_data['n_tot'] shape: {final_n_tot_raw.shape if hasattr(final_n_tot_raw, 'shape') else 'N/A'}")
            
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

    def set_ploptions(self):
        """Initialize or update plot_manager instances with data and plot options."""
        
        # <<< ADDED >>> Debugging start of set_ploptions
        print(f"DEBUG set_ploptions START: Entering method.")
        start_dt_array = getattr(self, 'datetime_array', 'ATTRIBUTE_MISSING')
        start_n_tot_raw = self.raw_data.get('n_tot', 'KEY_MISSING')
        print(f"DEBUG set_ploptions START: self.datetime_array type={type(start_dt_array)}")
        if start_dt_array is not None and start_dt_array != 'ATTRIBUTE_MISSING': print(f"DEBUG set_ploptions START: datetime_array len={len(start_dt_array)}")
        else: print(f"DEBUG set_ploptions START: datetime_array is None or missing")
        print(f"DEBUG set_ploptions START: self.raw_data['n_tot'] type={type(start_n_tot_raw)}")
        if start_n_tot_raw is not None and start_n_tot_raw != 'KEY_MISSING': print(f"DEBUG set_ploptions START: n_tot_raw shape={start_n_tot_raw.shape if hasattr(start_n_tot_raw, 'shape') else 'N/A'}")
        else: print(f"DEBUG set_ploptions START: n_tot_raw is None or missing")

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
            plot_options=ploptions(
                var_name='np1',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='np1', # User list #6
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Density (cm$^{-3}$)',
                legend_label=r'$n_{p1}$',
                color='hotpink',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 7. np2 (Scatter, Size 5)
        self.np2 = plot_manager( # Beam density
            self.raw_data.get('np2'),
            plot_options=ploptions(
                var_name='np2',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='np2', # User list #7
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Density (cm$^{-3}$)',
                legend_label=r'$n_{p2}$',
                color='deepskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 8. n_tot (Scatter, Size 5)
        # <<< ADDED >>> Debugging before n_tot plot_manager creation
        print(f"DEBUG set_ploptions n_tot: Preparing to create plot_manager.")
        dt_array_for_pm = getattr(self, 'datetime_array', None)
        n_tot_data_for_pm = self.raw_data.get('n_tot')
        # <<< ADDED >>> Detailed check of data/time before ploptions call
        print(f"DEBUG set_ploptions n_tot: --> BEFORE ploptions: datetime_array type={type(dt_array_for_pm)}, len={len(dt_array_for_pm) if dt_array_for_pm is not None else 'None'}")
        print(f"DEBUG set_ploptions n_tot: --> BEFORE ploptions: n_tot data type={type(n_tot_data_for_pm)}, dtype={n_tot_data_for_pm.dtype if hasattr(n_tot_data_for_pm, 'dtype') else 'N/A'}, shape={n_tot_data_for_pm.shape if hasattr(n_tot_data_for_pm, 'shape') else 'N/A'}")
        if n_tot_data_for_pm is not None and hasattr(n_tot_data_for_pm, '__len__') and len(n_tot_data_for_pm) > 0: print(f"DEBUG set_ploptions n_tot: --> BEFORE ploptions: n_tot data first 5: {n_tot_data_for_pm[:5]}")
        
        # Create ploptions instance first
        n_tot_ploptions = ploptions(
            var_name='n_tot',
            data_type='proton_fits',
            class_name='proton_fits',
            subclass_name='n_tot', # User list #8
            plot_type='scatter',
            datetime_array=dt_array_for_pm, # Use the variable we checked
            y_label=r'Density (cm$^{-3}$)',
            legend_label=r'$n_{ptot}$',
            color='deepskyblue',
            y_scale='linear',
            marker_style='o',
            marker_size=25,
            alpha=1.0,
            y_limit=[0, None]
        )
        
        # <<< ADDED >>> Detailed check before plot_manager call
        ploptions_dt_array = getattr(n_tot_ploptions, 'datetime_array', None)
        print(f"DEBUG set_ploptions n_tot: --> BEFORE plot_manager: n_tot_data type={type(n_tot_data_for_pm)}, dtype={n_tot_data_for_pm.dtype if hasattr(n_tot_data_for_pm, 'dtype') else 'N/A'}, shape={n_tot_data_for_pm.shape if hasattr(n_tot_data_for_pm, 'shape') else 'N/A'}")
        print(f"DEBUG set_ploptions n_tot: --> BEFORE plot_manager: n_tot_ploptions.datetime_array type={type(ploptions_dt_array)}, len={len(ploptions_dt_array) if ploptions_dt_array is not None else 'None'}")
        
        self.n_tot = plot_manager( # Total beam+core density
            n_tot_data_for_pm, # Use the variable we checked
            plot_options=n_tot_ploptions # Pass the created instance
        )
        
        # <<< ADDED >>> Debugging after n_tot plot_manager creation
        print(f"DEBUG set_ploptions n_tot: plot_manager created.")
        pm_instance = getattr(self, 'n_tot', None)
        if pm_instance:
            pm_dt_array = getattr(pm_instance.plot_options, 'datetime_array', 'ATTRIBUTE_MISSING')
            pm_data = getattr(pm_instance, 'data', 'ATTRIBUTE_MISSING')
            print(f"DEBUG set_ploptions n_tot: Instance datetime_array is None: {pm_dt_array is None or pm_dt_array == 'ATTRIBUTE_MISSING'}")
            if pm_dt_array is not None and pm_dt_array != 'ATTRIBUTE_MISSING': print(f"DEBUG set_ploptions n_tot: Instance datetime_array len: {len(pm_dt_array)}")
            print(f"DEBUG set_ploptions n_tot: Instance data is None: {pm_data is None or pm_data == 'ATTRIBUTE_MISSING'}")
            if pm_data is not None and pm_data != 'ATTRIBUTE_MISSING': print(f"DEBUG set_ploptions n_tot: Instance data shape: {pm_data.shape if hasattr(pm_data, 'shape') else 'N/A'}")
        else:
            print("DEBUG set_ploptions n_tot: Could not retrieve created plot_manager instance.")

        # 9. np2/np1 (Scatter, Size 5)
        self.np2_np1_ratio = plot_manager( # Beam to core density ratio
            self.raw_data.get('np2_np1_ratio'),
            plot_options=ploptions(
                var_name='np2_np1_ratio',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='np2_np1_ratio', # MATCH ATTRIBUTE NAME (User list #9)
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$\frac{n_{p2}}{n_{p1}}$',
                legend_label=r'$\frac{n_{p2}}{n_{p1}}$',
                color='deepskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 10. vp1_x (Scatter, Size 5)
        self.vp1_x = plot_manager( # Core velocity x
            self.raw_data.get('vp1_x'),
            plot_options=ploptions(
                var_name='vp1_x',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vp1_x', # User list #10
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vx_{p1}$',
                color='forestgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 11. vp1_y (Scatter, Size 5)
        self.vp1_y = plot_manager( # Core velocity y
            self.raw_data.get('vp1_y'),
            plot_options=ploptions(
                var_name='vp1_y',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vp1_y', # User list #11
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vy_{p1}$',
                color='orange',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 12. vp1_z (Scatter, Size 5)
        self.vp1_z = plot_manager( # Core velocity z
            self.raw_data.get('vp1_z'),
            plot_options=ploptions(
                var_name='vp1_z',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vp1_z', # User list #12
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vz_{p1}$',
                color='dodgerblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 13. vp1_mag (Scatter, Size 5)
        self.vp1_mag = plot_manager( # Core velocity magnitude
            self.raw_data.get('vp1_mag'),
            plot_options=ploptions(
                var_name='vp1_mag',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vp1_mag', # User list #13
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vmag_{p1}$',
                color='dodgerblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 14. vcm_x (Scatter, Size 5)
        self.vcm_x = plot_manager( # Center of mass velocity x
            self.raw_data.get('vcm_x'),
            plot_options=ploptions(
                var_name='vcm_x',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vcm_x', # User list #14
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vx_{cm}$',
                color='forestgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 15. vcm_y (Scatter, Size 5)
        self.vcm_y = plot_manager( # Center of mass velocity y
            self.raw_data.get('vcm_y'),
            plot_options=ploptions(
                var_name='vcm_y',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vcm_y', # User list #15
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vy_{cm}$',
                color='orange',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 16. vcm_z (Scatter, Size 5)
        self.vcm_z = plot_manager( # Center of mass velocity z
            self.raw_data.get('vcm_z'),
            plot_options=ploptions(
                var_name='vcm_z',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vcm_z', # User list #16
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vz_{cm}$',
                color='dodgerblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 17. vcm_mag (Scatter, Size 5)
        self.vcm_mag = plot_manager( # Center of mass velocity magnitude
            self.raw_data.get('vcm_mag'),
            plot_options=ploptions(
                var_name='vcm_mag',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vcm_mag', # User list #17
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'Velocity (km/s)',
                legend_label=r'$vmag_{cm}$',
                color='dodgerblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )
        
        # 18. vdrift (Scatter, Size 5)
        self.vdrift = plot_manager( # Drift speed
            self.raw_data.get('vdrift'),
            plot_options=ploptions(
                var_name='vdrift',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vdrift', # User list #18
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$V_{drift}$',
                legend_label=r'$vdrift_{p2}$',
                color='navy',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 19. |vdrift| (Scatter, Size 5)
        self.vdrift_abs = plot_manager( # Absolute drift speed
            self.raw_data.get('vdrift_abs'),
            plot_options=ploptions(
                var_name='vdrift_abs',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vdrift_abs', # MATCH ATTRIBUTE NAME (User list #19)
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$|V_{drift}|$',
                legend_label=r'$|vdrift_{p2}|$ ',
                color='navy',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 20. vdrift_va_pfits (Scatter, Size 5)
        self.vdrift_va_pfits = plot_manager( # Normalized drift speed - ATTRIBUTE NAME CHANGED
            self.raw_data.get('vdrift_va'), # Still gets raw 'vdrift_va' data
            plot_options=ploptions(
                var_name='vdrift_va',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='vdrift_va_pfits', # User list #20
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$V_{drift}/V_A$',
                legend_label=r'$vdrift_{p2}/vA$',
                color='navy',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 21. Trat1 (Scatter, Size 5)
        self.Trat1 = plot_manager( # Temperature anisotropy of the core
            self.raw_data.get('Trat1'),
            plot_options=ploptions(
                var_name='Trat1',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Trat1', # User list #21
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}/T_{\parallel}$',
                legend_label=r'$T_{\perp}/T_{\parallel,p1}$',
                color='hotpink',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 22. Trat2 (Scatter, Size 5)
        self.Trat2 = plot_manager( # Temperature anisotropy of the beam
            self.raw_data.get('Trat2'),
            plot_options=ploptions(
                var_name='Trat2',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Trat2', # User list #22
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}/T_{\parallel}$',
                legend_label=r'$T_{\perp}/T_{\parallel,p2}$',
                color='deepskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 23. Trat_tot (Scatter, Size 5)
        self.Trat_tot = plot_manager( # Total temperature anisotropy
            self.raw_data.get('Trat_tot'),
            plot_options=ploptions(
                var_name='Trat_tot',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Trat_tot', # User list #23
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_\perp/T_\parallel$',
                legend_label=r'$T_\perp/T_\parallel$',
                color='mediumspringgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 24. Tpar1 (Scatter, Size 5)
        self.Tpar1 = plot_manager( # Temperature parallel of the core
            self.raw_data.get('Tpar1'),
            plot_options=ploptions(
                var_name='Tpar1',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tpar1', # User list #24
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\parallel}$',
                legend_label=r'$T_{\parallel,p1}$',
                color='hotpink',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 25. Tpar2 (Scatter, Size 5)
        self.Tpar2 = plot_manager( # Temperature parallel of the beam
            self.raw_data.get('Tpar2'),
            plot_options=ploptions(
                var_name='Tpar2',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tpar2', # User list #25
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\parallel}$',
                legend_label=r'$T_{\parallel,p2}$',
                color='deepskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 26. Tpar_tot (Scatter, Size 5)
        self.Tpar_tot = plot_manager( # Total temperature parallel
            self.raw_data.get('Tpar_tot'),
            plot_options=ploptions(
                var_name='Tpar_tot',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tpar_tot', # User list #26
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_\parallel$',
                legend_label=r'$T_\parallel$',
                color='mediumspringgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 27. Tperp1 (Scatter, Size 5)
        self.Tperp1 = plot_manager( # Temperature perpendicular of the core
            self.raw_data.get('Tperp1'),
            plot_options=ploptions(
                var_name='Tperp1',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tperp1', # User list #27
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}$',
                legend_label=r'$T_{\perp,p1}$',
                color='hotpink',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 28. Tperp2 (Scatter, Size 5)
        self.Tperp2 = plot_manager( # Temperature perpendicular of the beam
            self.raw_data.get('Tperp2'),
            plot_options=ploptions(
                var_name='Tperp2',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tperp2', # User list #28
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}$',
                legend_label=r'$T_{\perp,p2}$',
                color='deepskyblue',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 29. Tperp_tot (Scatter, Size 5)
        self.Tperp_tot = plot_manager( # Total temperature perpendicular
            self.raw_data.get('Tperp_tot'),
            plot_options=ploptions(
                var_name='Tperp_tot',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Tperp_tot', # User list #29
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}$',
                legend_label=r'$T_{\perp}$',
                color='mediumspringgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 30. Temp_tot (Scatter, Size 5)
        self.Temp_tot = plot_manager( # Total temperature
            self.raw_data.get('Temp_tot'),
            plot_options=ploptions(
                var_name='Temp_tot',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='Temp_tot', # User list #30
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$Temp_{tot}$',
                legend_label=r'$T_{tot}$',
                color='mediumspringgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 31. |qz_p| (Scatter, Size 5)
        self.abs_qz_p = plot_manager( # Absolute heat flux - ATTRIBUTE RENAMED to abs_qz_p
            self.raw_data.get('abs_qz_p'),
            plot_options=ploptions(
                var_name='abs_qz_p',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='abs_qz_p', # MATCH ATTRIBUTE NAME (User list #31) - UPDATED
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$|Q_p| W/m^2$',
                legend_label=r'$|Q_p|$',
                color='mediumspringgreen',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 32. chi_p (Scatter, Size 5)
        self.chi_p = plot_manager( # Chi of whole proton fit
            self.raw_data.get('chi_p'),
            plot_options=ploptions(
                var_name='chi_p',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='chi_p',       # User list #32
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$\chi_p$',
                legend_label=r'$\chi_p$',
                color='rebeccapurple',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
            )
        )

        # 33. chi_p_norm (Scatter, Size 5)
        self.chi_p_norm = plot_manager( # Normalized chi of whole proton fit
            self.raw_data.get('chi_p_norm'),
            plot_options=ploptions(
                var_name='chi_p_norm',
                data_type='proton_fits',
                class_name='proton_fits',
                subclass_name='chi_p_norm', # User list #33
                plot_type='scatter',
                datetime_array=self.datetime_array,
                y_label=r'$\chi_p norm$',
                legend_label=r'$\chi_p norm$',
                color='rebeccapurple',
                y_scale='linear',
                marker_style='*',
                marker_size=5, # Default from helper
                alpha=0.7, # Default from helper
                y_limit=None
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


# Initialize with no data - this creates the global singleton instance
proton_fits = proton_fits_class(None)
print('initialized proton_fits class')
