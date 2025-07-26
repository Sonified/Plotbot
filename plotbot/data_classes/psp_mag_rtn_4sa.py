# psp_mag_rtn_4sa.py - Calculates and stores mag_rtn_4sa variables

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
import sys
from typing import Optional, List # Added for type hinting

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from ._utils import _format_setattr_debug
# import matplotlib.dates as mdates # Will be moved
# import scipy.interpolate as interpolate # Will be moved

# 🎉 Define the main class to calculate and store mag_rtn_4sa variables 🎉
class mag_rtn_4sa_class:
    def __init__(self, imported_data):
        # Initialize attributes
        # These are fundamental identifiers for Plotbot
        object.__setattr__(self, 'class_name', 'mag_rtn_4sa') 
        object.__setattr__(self, 'data_type', 'mag_RTN_4sa') # Changed to uppercase RTN to match psp_data_types.py
        # subclass_name is typically for components like .br, .bt, not the main class instance itself initially
        object.__setattr__(self, 'subclass_name', None) 
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'br': None,
            'bt': None,
            'bn': None,
            'bmag': None,
            'pmag': None,
            'br_norm': None  # Add br_norm to raw_data initialization
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None) # For dependency tracking (all available data)
        object.__setattr__(self, '_original_requested_trange', None) # For .data property clipping (user's last request)

        print_manager.dependency_management(f"*** MAG_CLASS_INIT (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")
        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating mag rtn 4sa variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag rtn 4sa variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        # Store the passed trange for both dependency tracking and data clipping
        print_manager.status(f"🔍 [MAG_DEBUG] Received original_requested_trange: {original_requested_trange}")
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        object.__setattr__(self, '_original_requested_trange', original_requested_trange)
        print_manager.processing(f"PSP_MAG_RTN_4SA_CLASS UPDATE: self._current_operation_trange SET TO: {self._current_operation_trange} (original_requested_trange was: {original_requested_trange})") # ADDED FOR DEBUG
        print_manager.processing(f"PSP_MAG_RTN_4SA_CLASS UPDATE: self._original_requested_trange SET TO: {self._original_requested_trange}")
        if original_requested_trange:
            print_manager.dependency_management(f"[MAG_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
            print_manager.dependency_management(f"[MAG_CLASS_UPDATE] Stored _original_requested_trange: {self._original_requested_trange}")
        else:
            print_manager.dependency_management(f"[MAG_CLASS_UPDATE] original_requested_trange not provided or None.")

        print_manager.dependency_management(f"*** MAG_CLASS_UPDATE (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['all', 'br', 'bt', 'bn', 'bmag', 'pmag']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_ploption_snapshot(current_plot_states[comp_name])}")

        # Special handling for br_norm: save state only if it's been fully initialized
        if hasattr(self, '_br_norm_manager') and \
           isinstance(self._br_norm_manager, plot_manager) and \
           self.raw_data.get('br_norm') is not None and \
           hasattr(self._br_norm_manager, '_plot_state'):
            current_plot_states['br_norm'] = dict(self._br_norm_manager._plot_state)
            print_manager.datacubby(f"Stored br_norm (from _br_norm_manager) state: {retrieve_ploption_snapshot(current_plot_states['br_norm'])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_ploptions()                                                  # Recreate plot managers for standard components
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        print_manager.processing(f"[MAG_UPDATE_DEBUG] Entering loop to restore plot states. current_plot_states keys: {list(current_plot_states.keys())}")
        for comp_name, state in current_plot_states.items():
            print_manager.processing(f"[MAG_UPDATE_DEBUG] Processing comp_name: '{comp_name}'")
            target_manager = None
            if comp_name == 'br_norm':
                # If br_norm state was saved, it means it was active.
                # Accessing self.br_norm will trigger the property, which should
                # re-calculate if necessary and update/create self._br_norm_manager.
                _ = self.br_norm # Ensure property runs and _br_norm_manager is current
                if hasattr(self, '_br_norm_manager') and isinstance(self._br_norm_manager, plot_manager):
                    target_manager = self._br_norm_manager
            elif hasattr(self, comp_name): # For standard components
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    target_manager = manager
            
            print_manager.processing(f"[MAG_UPDATE_DEBUG] For comp_name '{comp_name}', target_manager is: {type(target_manager)}, Value: {target_manager}")
            print_manager.processing(f"[MAG_UPDATE_DEBUG] ---> IMMEDIATELY BEFORE 'if target_manager:' for comp_name '{comp_name}'")
            if target_manager:
                target_manager._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(target_manager.plot_options, attr):
                        setattr(target_manager.plot_options, attr, value)
                print_manager.datacubby(f"Restored {comp_name} state to {'_br_norm_manager' if comp_name == 'br_norm' else comp_name}: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

        # First, check if it's a direct attribute/property of the instance
        if hasattr(self, subclass_name):
            # Verify it's not a private or dunder attribute unless explicitly intended (though typically not requested via get_subclass)
            if not subclass_name.startswith('_'): 
                retrieved_attr = getattr(self, subclass_name)
                print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        # This part might be redundant if set_ploptions correctly creates plot_manager instances as attributes.
        # However, keeping it ensures that if raw_data keys are somehow requested directly, they can be accessed if they aren't also properties.
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            # This path should ideally be less common if plot_managers are set up for all raw_data items
            # and those plot_managers are accessed directly as attributes (handled by the hasattr check above).
            # This could return the raw numpy array if the plot_manager wasn't set up as an attribute.
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component # Could be a plot_manager if set_ploptions assigned it here, or raw data.

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[MAG_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
        return None

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                # Re-raise AttributeError if the internal/dunder method truly doesn't exist
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        print_manager.dependency_management(f"[GETATTR DEBUG] Trying to access '{name}'")

        # Default handling for other attributes
        if 'raw_data' not in self.__dict__:
            print_manager.dependency_management(f"[GETATTR DEBUG] raw_data not in __dict__")
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        
        print_manager.dependency_management(f"[GETATTR DEBUG] Entering general fallback path")
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"[mag_rtn_4sa getattr] '{name}' is not a recognized attribute, friend!")                
        print(f"[mag_rtn_4sa getattr] Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use

    @property
    def br_norm(self):
        """Property for br_norm component that handles lazy loading."""
        print_manager.dependency_management(f"[BR_NORM_PROPERTY ENTRY] Accessing br_norm for instance ID: {id(self)}")
        dt_array_status = "exists and is populated" if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0 else "MISSING or EMPTY"
        print_manager.dependency_management(f"[BR_NORM_PROPERTY ENTRY] Parent self.datetime_array status: {dt_array_status}")
        if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
            print_manager.dependency_management(f"[BR_NORM_PROPERTY ENTRY] Parent self.datetime_array[0]: {self.datetime_array[0]}, [-1]: {self.datetime_array[-1]}")

        # Store the plot_manager in a private attribute
        if not hasattr(self, '_br_norm_manager'):
            print_manager.dependency_management("[BR_NORM_PROPERTY] Creating initial placeholder manager")
            # Create an empty placeholder initially
            self._br_norm_manager = plot_manager(
                np.array([]),
                plot_options=ploptions(
                    data_type='mag_RTN_4sa',
                    var_name='br_norm_rtn_4sa',
                    class_name='mag_rtn_4sa',
                    subclass_name='br_norm',
                    plot_type='time_series',
                    datetime_array=self.datetime_array,
                    y_label='Br·R² [nT·AU²]',
                    legend_label=r'$B_R \cdot R^2$',
                    color='darkorange',
                    y_scale='linear',
                    line_width=1,
                    line_style='-'
                )
            )
            print_manager.dependency_management(f"[BR_NORM_PROPERTY] Initial _br_norm_manager.plot_options.datetime_array len: {len(self._br_norm_manager.plot_options.datetime_array) if self._br_norm_manager.plot_options.datetime_array is not None else 'None'}")

        # If data is available, try to calculate
        br_exists_and_populated = hasattr(self, 'raw_data') and 'br' in self.raw_data and self.raw_data['br'] is not None and len(self.raw_data['br']) > 0
        print_manager.dependency_management(f"[BR_NORM_PROPERTY] Check for calculation: hasattr(self, 'raw_data'): {hasattr(self, 'raw_data')}, 'br' in raw_data: {'br' in self.raw_data if hasattr(self, 'raw_data') else 'N/A'}, raw_data['br'] is not None: {self.raw_data.get('br') is not None if hasattr(self, 'raw_data') else 'N/A'}, len(raw_data['br']) > 0: {len(self.raw_data.get('br')) > 0 if hasattr(self, 'raw_data') and self.raw_data.get('br') is not None else 'N/A'}")

        if hasattr(self, 'raw_data') and self.raw_data.get('br') is not None and len(self.raw_data['br']) > 0 : # Check if 'br' data exists and is populated
            print_manager.dependency_management("[BR_NORM_PROPERTY] Parent raw_data['br'] exists and is populated. Attempting calculation.")
            success = self._calculate_br_norm()
            if success and self.raw_data.get('br_norm') is not None:
                print_manager.dependency_management("[BR_NORM_PROPERTY] _calculate_br_norm successful, updating _br_norm_manager.")
                options = self._br_norm_manager.plot_options
                print_manager.dependency_management(f"[BR_NORM_PROPERTY] _br_norm_manager is being updated. Current options.datetime_array len: {len(options.datetime_array) if options.datetime_array is not None else 'None'}")
                # if options.datetime_array is not None and len(options.datetime_array) > 0:
                #     print_manager.dependency_management(f"[BR_NORM_PROPERTY] options.datetime_array[0]: {options.datetime_array[0]}, [-1]: {options.datetime_array[-1]}")
                
                # Ensure the plot_options for the new manager uses the PARENT's datetime_array
                if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                    print_manager.dependency_management(f"[BR_NORM_PROPERTY] Parent self.datetime_array IS valid and populated. Setting options.datetime_array. Parent len: {len(self.datetime_array)}")
                    options.datetime_array = self.datetime_array
                elif options.datetime_array is None: # Parent dt_array is None/empty, and current options.dt_array is also None
                    print_manager.dependency_management(f"[BR_NORM_PROPERTY] Parent self.datetime_array is NOT valid (or empty), and options.datetime_array is None. Setting to empty np.array([]) to be safe.")
                    options.datetime_array = np.array([]) # Default to empty array
                else: # Parent dt_array is None/empty, but options.datetime_array was something (e.g. from placeholder or already empty)
                    print_manager.dependency_management(f"[BR_NORM_PROPERTY] Parent self.datetime_array is NOT valid (or empty). Current options.datetime_array len: {len(options.datetime_array) if options.datetime_array is not None else 'None'}. Will retain existing options.datetime_array or ensure it's an empty array if it was None.")
                    options.datetime_array = options.datetime_array if options.datetime_array is not None else np.array([])

                self._br_norm_manager = plot_manager(
                    self.raw_data['br_norm'],
                    plot_options=options 
                )
                print_manager.dependency_management(f"[BR_NORM_PROPERTY] Updated _br_norm_manager with data shape: {self.raw_data['br_norm'].shape if self.raw_data['br_norm'] is not None else 'None'}")
                print_manager.dependency_management(f"[BR_NORM_PROPERTY] New _br_norm_manager.plot_options.datetime_array len: {len(self._br_norm_manager.plot_options.datetime_array) if self._br_norm_manager.plot_options.datetime_array is not None else 'None'}")
                if self._br_norm_manager.plot_options.datetime_array is not None and len(self._br_norm_manager.plot_options.datetime_array) > 0:
                    print_manager.dependency_management(f"[BR_NORM_PROPERTY] New _br_norm_manager.plot_options.datetime_array[0]: {self._br_norm_manager.plot_options.datetime_array[0]}, [-1]: {self._br_norm_manager.plot_options.datetime_array[-1]}")

            else:
                print_manager.dependency_management(f"[BR_NORM_PROPERTY] _calculate_br_norm did not succeed or br_norm data is None. Success: {success}, br_norm data is None: {self.raw_data.get('br_norm') is None}")
        else:
            print_manager.dependency_management("[BR_NORM_PROPERTY] Parent raw_data['br'] MISSING or EMPTY. Not attempting _calculate_br_norm.")
        
        print_manager.dependency_management(f"[BR_NORM_PROPERTY EXIT] Returning _br_norm_manager (ID: {id(self._br_norm_manager)}). Datetime array len: {len(self._br_norm_manager.datetime_array) if self._br_norm_manager.datetime_array is not None else 'None'})")
        if self._br_norm_manager.datetime_array is not None and len(self._br_norm_manager.datetime_array) > 0:
             print_manager.dependency_management(f"[BR_NORM_PROPERTY EXIT] _br_norm_manager.datetime_array[0]: {self._br_norm_manager.datetime_array[0]}, [-1]: {self._br_norm_manager.datetime_array[-1]}")
        return self._br_norm_manager

    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.dependency_management(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('mag_rtn_4sa setattr helper!')
            print(f"[mag_rtn_4sa setattr] '{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"[mag_rtn_4sa setattr] Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
           
            # Do not set the attrib
    def calculate_variables(self, imported_data):
        # STRATEGIC PRINT I
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG I] calculate_variables called for instance ID: {id(self)}")

        print_manager.dependency_management(f"*** MAG_CLASS_CALCVARS (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
        if hasattr(imported_data, 'data') and isinstance(imported_data.data, dict):
            print_manager.dependency_management(f"    Available keys in imported_data.data for CALCVARS: {list(imported_data.data.keys())}")
        else:
            print_manager.dependency_management(f"    CALCVARS: imported_data.data is missing or not a dict.")
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))        
        
        # STRATEGIC PRINT J
        dt_len_in_calc_vars = len(self.datetime_array) if self.datetime_array is not None else "None"
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG J] Instance ID: {id(self)} AFTER self.datetime_array assignment in calculate_variables. Length: {dt_len_in_calc_vars}")
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG J] First datetime: {self.datetime_array[0] if len(self.datetime_array) > 0 else 'EMPTY'}")
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG J] Last datetime: {self.datetime_array[-1] if len(self.datetime_array) > 0 else 'EMPTY'}")
        print_manager.dependency_management("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.dependency_management("First element type: {type(self.datetime_array[0])}")
        
        # Get field data as numpy array
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'])
        
        # Extract components and calculate derived quantities efficiently
        br = self.field[:, 0]
        bt = self.field[:, 1]
        bn = self.field[:, 2]
        
        # Calculate magnitude using numpy operations
        bmag = np.sqrt(br**2 + bt**2 + bn**2)
        
        # Calculate magnetic pressure
        mu_0 = 4 * np.pi * 1e-7  # Permeability of free space
        pmag = (bmag**2) / (2 * mu_0) * 1e-9  # Convert to nPa
        
        # Store all data in raw_data dictionary
        self.raw_data = {
            'all': [br, bt, bn],
            'br': br,
            'bt': bt,
            'bn': bn,
            'bmag': bmag,
            'pmag': pmag,
            'br_norm': None  # br_norm is calculated only when requested (lazy loading)
        }

        # # Convert TT2000 timestamps to datetime objects using cdflib
        # self.datetime = cdflib.cdfepoch.to_datetime(self.time)

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        print_manager.dependency_management(f"Field data shape: {self.field.shape}")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")
    
    def _calculate_br_norm(self):
        """Calculate Br normalized by R^2."""
        from plotbot.get_data import get_data # Local import
        from plotbot import proton # Local import for proton data
        import matplotlib.dates as mdates # Moved here
        import scipy.interpolate as interpolate # Moved here

        # Log entry with instance ID
        print_manager.dependency_management(f"[BR_NORM_CALC ENTRY] _calculate_br_norm called for instance ID: {id(self)}")

        # Determine the trange to use for fetching dependencies
        trange_for_dependencies = None
        if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:
            trange_for_dependencies = self._current_operation_trange
            print_manager.dependency_management(f"[BR_NORM_CALC] Using specific _current_operation_trange for dependencies: {trange_for_dependencies}")
        else:
            print_manager.error("[BR_NORM_CALC] Cannot determine time range for dependencies: _current_operation_trange is None or not set.")
            print_manager.warning("[BR_NORM_CALC] The br_norm calculation now STRICTLY requires _current_operation_trange. The fallback to self.datetime_array for dependency trange has been removed.")
            self.raw_data['br_norm'] = None # Ensure it's None if calculation fails
            return False

        # Ensure proton.sun_dist_rsun data is loaded for the correct time range BEFORE accessing its .data attribute
        print_manager.dependency_management(f"[BR_NORM_CALC] Calling get_data for proton.sun_dist_rsun with trange: {trange_for_dependencies}")
        get_data(trange_for_dependencies, proton.sun_dist_rsun)
        print_manager.dependency_management(f"[BR_NORM_CALC] Returned from get_data for proton.sun_dist_rsun.")
        
        # Check 2: Ensure proton data is available AFTER attempting to load it
        if not hasattr(proton, 'sun_dist_rsun') or not hasattr(proton.sun_dist_rsun, 'data'):
            print_manager.error("[BR_NORM_CALC ERROR] proton.sun_dist_rsun or its .data attribute is not available even after get_data call.")
            self.raw_data['br_norm'] = None # Ensure it's None if calculation fails
            return False
        
        if proton.sun_dist_rsun.data is None or len(proton.sun_dist_rsun.data) == 0: # This was the line causing the error
            print_manager.error(f"[BR_NORM_CALC ERROR] proton.sun_dist_rsun.data is None or empty after get_data call for trange {trange_for_dependencies}. Cannot calculate br_norm.")
            print_manager.dependency_management(f"[BR_NORM_CALC DEBUG] proton.sun_dist_rsun type: {type(proton.sun_dist_rsun)}, .data type: {type(proton.sun_dist_rsun.data) if hasattr(proton.sun_dist_rsun, 'data') else 'N/A'}")
            self.raw_data['br_norm'] = None # Ensure it's None if calculation fails
            return False
        
        # Check 3: Ensure trange_for_dependencies is valid (repeated check, but good for safety after get_data)
        if trange_for_dependencies is None or not isinstance(trange_for_dependencies, list) or len(trange_for_dependencies) != 2:
            print_manager.dependency_management("[BR_NORM_DEBUG] trange_for_dependencies is None or invalid (post get_data check)")
            return False
        
        # Use existing data
        print_manager.dependency_management("[BR_NORM_DEBUG] All checks passed, proceeding with br_norm calculation")
        br_data = self.raw_data['br']
        print_manager.dependency_management(f"[BR_NORM_DEBUG] br_data type: {type(br_data)}, shape: {getattr(br_data, 'shape', 'NO SHAPE')}")
        
        # Get time range from datetime_array - no checks, just use it
        print_manager.dependency_management(f"[BR_NORM_DEBUG] datetime_array length: {len(self.datetime_array)}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] First datetime: {self.datetime_array[0] if len(self.datetime_array) > 0 else 'EMPTY'}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Last datetime: {self.datetime_array[-1] if len(self.datetime_array) > 0 else 'EMPTY'}")
        
        # Fix: Use YYYY-MM-DD/HH:MM:SS.fff format with slash separator
        start_time = pd.Timestamp(self.datetime_array[0]).strftime('%Y-%m-%d/%H:%M:%S.%f')
        end_time = pd.Timestamp(self.datetime_array[-1]).strftime('%Y-%m-%d/%H:%M:%S.%f')
        trange = [start_time, end_time]
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Created trange: {trange}")
        
        # Get proton sun_dist_rsun data
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Getting sun_dist_rsun data for br_norm calculation (using trange: {trange_for_dependencies})")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Before get_data: proton ID={id(proton)}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Before get_data: proton.sun_dist_rsun.data = {getattr(proton.sun_dist_rsun, 'data', 'NO DATA ATTR')}")
        get_data(trange_for_dependencies, proton.sun_dist_rsun)
        print_manager.dependency_management(f"[BR_NORM_DEBUG] After get_data: proton.sun_dist_rsun.data = {getattr(proton.sun_dist_rsun, 'data', 'NO DATA ATTR')}")

        # Add explicit check that data was loaded
        if not hasattr(proton.sun_dist_rsun, 'data') or proton.sun_dist_rsun.data is None:
            print_manager.dependency_management(f"[BR_NORM_DEBUG] ERROR: proton.sun_dist_rsun.data is None after get_data call")
            return False
            
        if len(proton.sun_dist_rsun.data) == 0:
            print_manager.dependency_management(f"[BR_NORM_DEBUG] ERROR: proton.sun_dist_rsun.data is empty (length 0) after get_data call")
            return False
        
        print_manager.dependency_management(f"[BR_NORM_DEBUG] SUCCESS: proton.sun_dist_rsun.data loaded with shape {proton.sun_dist_rsun.data.shape}")
        
        # Get the proton data directly - let any errors raise naturally
        mag_datetime = self.datetime_array
        proton_datetime = proton.datetime_array
        sun_dist_rsun = proton.sun_dist_rsun.data
        
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Using proton_datetime with length {len(proton_datetime)}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Using sun_dist_rsun with shape {sun_dist_rsun.shape}")
        
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Proton data state:")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] proton_datetime type: {type(proton_datetime)}, shape: {getattr(proton_datetime, 'shape', 'NO SHAPE')}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] sun_dist_rsun type: {type(sun_dist_rsun)}, shape: {getattr(sun_dist_rsun, 'shape', 'NO SHAPE')}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] First proton datetime: {proton_datetime[0] if len(proton_datetime) > 0 else 'EMPTY'}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Last proton datetime: {proton_datetime[-1] if len(proton_datetime) > 0 else 'EMPTY'}")
        
        # Convert datetime arrays to numeric for interpolation
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Converting datetime arrays to numeric with mdates.date2num")
        proton_time_numeric = mdates.date2num(proton_datetime)
        mag_time_numeric = mdates.date2num(mag_datetime)
        print_manager.dependency_management(f"[BR_NORM_DEBUG] proton_time_numeric shape: {proton_time_numeric.shape}")
        print_manager.dependency_management(f"[BR_NORM_DEBUG] mag_time_numeric shape: {mag_time_numeric.shape}")
        
        # Create interpolation function
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Creating interpolation function")
        interp_func = interpolate.interp1d(
            proton_time_numeric, 
            sun_dist_rsun,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        # Apply interpolation to get sun distance at mag timestamps
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Applying interpolation")
        sun_dist_interp = interp_func(mag_time_numeric)
        print_manager.dependency_management(f"[BR_NORM_DEBUG] sun_dist_interp shape: {sun_dist_interp.shape}")
        
        # Calculate br_norm using the precise conversion factor
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Calculating br_norm with conversion factor")
        rsun_to_au_conversion_factor = 215.032867644  # Solar radii per AU
        br_norm = br_data * ((sun_dist_interp / rsun_to_au_conversion_factor) ** 2)
        print_manager.dependency_management(f"[BR_NORM_DEBUG] br_norm shape: {br_norm.shape}")
        
        # Store the result
        self.raw_data['br_norm'] = br_norm
        print_manager.dependency_management(f"[BR_NORM_DEBUG] Successfully calculated br_norm (shape: {br_norm.shape})")
        print_manager.dependency_management(f"[_CALCULATE_BR_NORM EXIT] Successfully calculated and stored br_norm.")
        return True
    
    def _setup_br_norm_plot_manager(self):
        """Create plot manager for br_norm with appropriate options"""
        if self.raw_data['br_norm'] is not None and hasattr(self, 'datetime_array') and self.datetime_array is not None:
            self.br_norm = plot_manager(
                self.raw_data['br_norm'],
                plot_options=ploptions(
                    data_type='mag_RTN_4sa',    # Actual data product name
                    var_name='br_norm_rtn_4sa',  # Variable name
                    class_name='mag_rtn_4sa',   # Class handling this data
                    subclass_name='br_norm',    # Specific component
                    plot_type='time_series',    # Type of plot
                    datetime_array=self.datetime_array,  # Time data
                    y_label='Br·R² [nT·AU²]',   # Y-axis label
                    legend_label=r'$B_R \cdot R^2$',  # Legend text - Changed to raw string
                    color='darkorange',         # Plot color (different from br's forestgreen)
                    y_scale='linear',           # Scale type
                    y_limit=None,               # Y-axis limits
                    line_width=1,               # Line width
                    line_style='-'              # Line style
                )
            )
            print_manager.dependency_management(f"Created plot manager for br_norm")
            return True
        else:
            print_manager.dependency_management(f"Cannot create plot manager for br_norm: missing data or datetime_array")
            return False

    def set_ploptions(self):
        """Create plot managers for each component with default options"""
        # STRATEGIC PRINT K
        dt_len_in_set_ploptions = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else "None_or_NoAttr"
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG K] set_ploptions called for instance ID: {id(self)}. self.datetime_array len: {dt_len_in_set_ploptions}")

        print_manager.dependency_management(f"Setting up plot options for mag_rtn_4sa variables")
        
        self.all = plot_manager(
            [self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name=['br_rtn_4sa', 'bt_rtn_4sa', 'bn_rtn_4sa'],  # Variable names
                class_name='mag_rtn_4sa',   # Class handling this data
                subclass_name='all',        # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label=['$B_R$', '$B_T$', '$B_N$'],  # Legend text
                color=['forestgreen', 'orange', 'dodgerblue'],  # Plot colors
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=[1, 1, 1],      # Line widths
                line_style=['-', '-', '-'] # Line styles
            )
        )
        print_manager.dependency_management(f"FYI: Example mag data: Created mag_rtn_4sa.all variable with {3 if self.raw_data['br'] is not None else 0} components")
        
        self.br = plot_manager(
            self.raw_data['br'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='br_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='br',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_R$',      # Legend text
                color='forestgreen',        # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bt = plot_manager(
            self.raw_data['bt'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bt_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bt',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_T$',      # Legend text
                color='orange',            # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bn = plot_manager(
            self.raw_data['bn'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bn_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bn',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_N$',      # Legend text
                color='dodgerblue',        # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )
        
        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bmag_rtn_4sa',     # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='|B| (nT)',        # Y-axis label
                legend_label='$|B|$',      # Legend text
                color='black',             # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.pmag = plot_manager(
            self.raw_data['pmag'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='pmag_rtn_4sa',     # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='pmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Pmag (nPa)',      # Y-axis label
                legend_label='$P_{mag}$',  # Legend text
                color='purple',            # Plot color
                y_scale='log',             # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
            
        )

        # br_norm plot manager is only created when it's data is available (lazy loading)
        # We don't create it here initially to avoid unnecessary proton data loading

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print_manager.dependency_management(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print_manager.dependency_management(f"    PRE-CHECK - time len: {original_time_len}")
        print_manager.dependency_management(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
                changed_time = True

            expected_len = len(self.datetime_array)
            if ('br' in self.raw_data and self.raw_data['br'] is not None and
                'bt' in self.raw_data and self.raw_data['bt'] is not None and
                'bn' in self.raw_data and self.raw_data['bn'] is not None and
                len(self.raw_data['br']) == expected_len and
                len(self.raw_data['bt']) == expected_len and
                len(self.raw_data['bn']) == expected_len):
                new_field = np.column_stack((self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']))
                if not hasattr(self, 'field') or self.field is None or not np.array_equal(self.field, new_field):
                    self.field = new_field
                    print_manager.dependency_management(f"    Updated self.field from RTN components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print_manager.dependency_management(f"    Nullifying self.field. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print_manager.dependency_management(f"    Setting self.field to None. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print_manager.dependency_management(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print_manager.dependency_management(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print_manager.dependency_management(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print_manager.dependency_management(f"    POST-FIX - time len: {final_time_len}")
            print_manager.dependency_management(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

mag_rtn_4sa = mag_rtn_4sa_class(None) #Initialize the class with no data
print_manager.dependency_management('initialized mag_rtn_4sa class') 