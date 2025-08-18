#plotbot/data_classes/psp_electron_classes.py

import numpy as np
import pandas as pd 
import cdflib 
from datetime import datetime, timedelta, timezone
from typing import Optional, List # Added for type hinting

# Import our custom managers (UPDATED PATHS)
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from plotbot.utils import get_encounter_number
from ._utils import _format_setattr_debug
# from plotbot.data_cubby import data_cubby # REMOVED Circular Import

class epad_strahl_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'strahl': None,
            'centroids': None,
            'pitch_angle_y_values': None # Added for merging pitch angle
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'data_type', 'spe_sf0_pad') # Explicitly set data_type
        object.__setattr__(self, '_current_operation_trange', None) # Initialize new attribute

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating EPAD strahl variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated EPAD strahl variables.")

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        # data_cubby.stash(self, class_name='epad')


    #strahl_update
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")
        
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_state = {}
        for subclass_name in self.raw_data.keys():                             # Use keys()
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

    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component"""
        print_manager.dependency_management(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.dependency_management(f"Returning {subclass_name} component")  # Log successful component find
            
            # 🚀 PERFORMANCE FIX: Only set requested_trange on the SPECIFIC subclass being requested
            current_trange = TimeRangeTracker.get_current_trange()
            if current_trange:
                try:
                    attr_value = getattr(self, subclass_name)
                    if isinstance(attr_value, plot_manager):
                        attr_value.requested_trange = current_trange
                except Exception:
                    pass
            
            return getattr(self, subclass_name)  # Return the plot_manager instance
        else:
            print(f"'{subclass_name}' is not a recognized subclass, friend!")  # Friendly error message
            print(f"Try one of these: {', '.join(self.raw_data.keys())}")  # Show available components
            return None  # Return None if not found

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print('epad_strahl getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
        # raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(f"Setting attribute: {name} with value: {value}")
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'times_mesh', 'energy_index', 'data_type'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('epad_strahl setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attrib
    
    def calculate_variables(self, imported_data):
        """Calculate and store EPAD strahl variables"""
        print_manager.processing(f"[EPAD_CALC_VARS ENTRY] id(self): {id(self)}")
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        print_manager.processing(f"[EPAD_CALC_VARS] self.datetime_array (id: {id(self.datetime_array)}) len: {len(self.datetime_array) if self.datetime_array is not None else 'None'}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}" if self.datetime_array is not None and len(self.datetime_array) > 0 else "[EPAD_CALC_VARS] self.datetime_array is empty/None")
        
        # Extract data
        eflux = imported_data.data['EFLUX_VS_PA_E']
        self.raw_data['pitch_angle_y_values'] = imported_data.data['PITCHANGLE'] # Now in raw_data

        # Debug the time values
        print_manager.debug(f"Time values type: {type(self.time)}")
        print_manager.debug(f"Time values range: {self.time[0]} to {self.time[-1]}")

        # Set energy index based on encounter number
        # Convert numpy.datetime64 to datetime before using strftime
        date_str = pd.Timestamp(self.datetime_array[0]).strftime('%Y-%m-%d')
        encounter_number = get_encounter_number(date_str)
        if encounter_number in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9']:
            self.energy_index = 8
        else:
            self.energy_index = 12

        print_manager.debug(f"Encounter number: {encounter_number}")
        print_manager.debug(f"Energy index: {self.energy_index}")

        # Extract strahl flux for specific energy
        strahl = eflux[:, :, self.energy_index]
        
        # Replace zeros and calculate log version
        strahl = np.where(strahl == 0, 1e-10, strahl)  # Replace zeros
        log_strahl = np.log10(strahl)
        strahl = log_strahl

        # Create time mesh to match strahl data dimensions
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(strahl.shape[1]),
            indexing='ij'
        )[0]
        print_manager.processing(f"[EPAD_CALC_VARS] self.times_mesh (id: {id(self.times_mesh)}) shape: {self.times_mesh.shape if self.times_mesh is not None else 'None'}. Time range (mesh[0,:]): {self.times_mesh[0,0]} to {self.times_mesh[0,-1]}" if self.times_mesh is not None and self.times_mesh.size > 0 and self.times_mesh.shape[1] > 0 else "[EPAD_CALC_VARS] self.times_mesh is empty/None or not 2D as expected")

        # Calculate centroids
        centroids = np.ma.average(self.raw_data['pitch_angle_y_values'], # Use from raw_data
                                weights=strahl, 
                                axis=1)

        strahl_centroids = centroids
        # Store raw data
        self.raw_data['strahl'] = strahl # Already part of self.raw_data initialization
        self.raw_data['centroids'] = centroids # Already part of self.raw_data initialization
        # 'pitch_angle_y_values' is already set above

    def set_ploptions(self):
        """Set up the plotting options for strahl data"""
        print_manager.processing(f"[EPAD_SET_PLOPT ENTRY] id(self): {id(self)}")
        print_manager.processing(f"[EPAD_SET_PLOPT] self.datetime_array (id: {id(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'N/A'}) len: {len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None'}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}" if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0 else "[EPAD_SET_PLOPT] self.datetime_array is empty/None or N/A")
        
        # Corrected print for self.times_mesh
        times_mesh_exists = hasattr(self, 'times_mesh') and self.times_mesh is not None
        raw_data_strahl_exists = hasattr(self, 'raw_data') and 'strahl' in self.raw_data and self.raw_data['strahl'] is not None
        datetime_array_exists = hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0

        if times_mesh_exists and isinstance(self.times_mesh, np.ndarray) and raw_data_strahl_exists and datetime_array_exists:
            # Check if times_mesh needs regeneration
            needs_regeneration = False
            if self.times_mesh.ndim != 2: # Ensure times_mesh is 2D
                needs_regeneration = True
                print_manager.processing(f"[EPAD_SET_PLOPT] times_mesh is not 2D (shape: {self.times_mesh.shape}). Regenerating.")
            elif self.times_mesh.shape[0] != len(self.datetime_array):
                needs_regeneration = True
                print_manager.processing(f"[EPAD_SET_PLOPT] times_mesh.shape[0] ({self.times_mesh.shape[0]}) != len(datetime_array) ({len(self.datetime_array)}). Regenerating.")
            elif self.raw_data['strahl'].ndim == 2 and self.times_mesh.shape[1] != self.raw_data['strahl'].shape[1]: # Check second dimension if strahl data is 2D
                needs_regeneration = True
                print_manager.processing(f"[EPAD_SET_PLOPT] times_mesh.shape[1] ({self.times_mesh.shape[1]}) != raw_data['strahl'].shape[1] ({self.raw_data['strahl'].shape[1]}). Regenerating.")
            elif self.raw_data['strahl'].ndim == 1 and self.times_mesh.shape[1] != 1: # Handle 1D strahl data case (e.g. centroids) - times_mesh should have 1 column
                 # This case might need specific handling if strahl can be 1D and times_mesh needs to reflect that.
                 # For now, assuming strahl (for pcolormesh) is typically 2D in data, so times_mesh matching its second dim is correct.
                 # If 'strahl' component data itself can be 1D and used for pcolormesh, this check might need refinement.
                 # The current check for raw_data['strahl'].ndim == 2 above handles the primary case.
                 pass


            if needs_regeneration:
                print_manager.processing(f"[EPAD_SET_PLOPT] Regenerating times_mesh. Old shape: {self.times_mesh.shape if isinstance(self.times_mesh, np.ndarray) else 'N/A'}")
                self.times_mesh = np.meshgrid(
                    self.datetime_array,
                    np.arange(self.raw_data['strahl'].shape[1] if self.raw_data['strahl'].ndim == 2 else 1), # Use 1 if strahl is 1D
                    indexing='ij'
                )[0]
                print_manager.processing(f"[EPAD_SET_PLOPT] Regenerated times_mesh. New shape: {self.times_mesh.shape}")

        if times_mesh_exists and isinstance(self.times_mesh, np.ndarray):
            print_manager.processing(f"[EPAD_SET_PLOPT] self.times_mesh (id: {id(self.times_mesh)}) is ndarray. Shape: {self.times_mesh.shape}. Time range (mesh[0,:]): {self.times_mesh[0,0]} to {self.times_mesh[0,-1]}" if self.times_mesh.size > 0 and self.times_mesh.ndim == 2 and self.times_mesh.shape[1] > 0 else f"[EPAD_SET_PLOPT] self.times_mesh is ndarray but empty, not 2D, or second dim is 0. Shape: {self.times_mesh.shape}")
        elif times_mesh_exists: # It exists but is not an ndarray (e.g., a list)
            print_manager.processing(f"[EPAD_SET_PLOPT] self.times_mesh (id: {id(self.times_mesh)}) is {type(self.times_mesh)}. Len: {len(self.times_mesh) if hasattr(self.times_mesh, '__len__') else 'N/A'}. Value: {self.times_mesh}")
        else: # Does not exist or is None
            print_manager.processing(f"[EPAD_SET_PLOPT] self.times_mesh does not exist or is None.")

        # The datetime_array passed to plot_manager for strahl IS self.times_mesh
        pm_arg_times_mesh = self.times_mesh if hasattr(self, 'times_mesh') else None # Ensure it exists for print
        # Corrected print for pm_arg_times_mesh (which is self.times_mesh)
        if pm_arg_times_mesh is not None and isinstance(pm_arg_times_mesh, np.ndarray):
            print_manager.processing(f"[EPAD_SET_PLOPT] plot_manager for strahl gets datetime_array (is self.times_mesh, id: {id(pm_arg_times_mesh)}) is ndarray. Shape: {pm_arg_times_mesh.shape}. Time range (mesh[0,:]): {pm_arg_times_mesh[0,0]} to {pm_arg_times_mesh[0,-1]}" if pm_arg_times_mesh.size > 0 and pm_arg_times_mesh.ndim == 2 and pm_arg_times_mesh.shape[1] > 0 else f"[EPAD_SET_PLOPT] plot_manager for strahl gets datetime_array (self.times_mesh) is ndarray but empty, not 2D, or second dim is 0. Shape: {pm_arg_times_mesh.shape}")
        elif pm_arg_times_mesh is not None: # It exists but is not an ndarray (e.g., a list)
            print_manager.processing(f"[EPAD_SET_PLOPT] plot_manager for strahl gets datetime_array (is self.times_mesh, id: {id(pm_arg_times_mesh)}) is {type(pm_arg_times_mesh)}. Len: {len(pm_arg_times_mesh) if hasattr(pm_arg_times_mesh, '__len__') else 'N/A'}. Value: {pm_arg_times_mesh}")
        else: # Does not exist or is None
            print_manager.processing(f"[EPAD_SET_PLOPT] plot_manager for strahl gets datetime_array (self.times_mesh) that does not exist or is None.")

        self.strahl = plot_manager(
            self.raw_data['strahl'],
            plot_options=ploptions(
                data_type='spe_sf0_pad',
                var_name='log_strahl',
                class_name='epad',
                subclass_name='strahl',
                plot_type='spectral',
                datetime_array=self.times_mesh,  # Use the mesh for time array
                y_label='Pitch Angle\n(degrees)',
                legend_label='Electron PAD',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['pitch_angle_y_values'], # Use from raw_data
                colormap='jet',
                colorbar_scale='log',
                colorbar_limits=None
                # colorbar_limits=[9.4, 10.5]
            )
        )

        # Initialize centroids with plot_manager
        # The datetime_array passed to plot_manager for centroids IS self.datetime_array
        pm_arg_datetime_array = self.datetime_array if hasattr(self, 'datetime_array') else None # Ensure it exists for print
        print_manager.processing(f"[EPAD_SET_PLOPT] plot_manager for centroids gets datetime_array (is self.datetime_array, id: {id(pm_arg_datetime_array) if pm_arg_datetime_array is not None else 'N/A'}) len: {len(pm_arg_datetime_array) if pm_arg_datetime_array is not None else 'None'}. Range: {pm_arg_datetime_array[0]} to {pm_arg_datetime_array[-1]}" if pm_arg_datetime_array is not None and len(pm_arg_datetime_array) > 0 else "[EPAD_SET_PLOPT] plot_manager for centroids gets datetime_array (self.datetime_array) that is empty/None or N/A")

        self.centroids = plot_manager(
            self.raw_data['centroids'],
            plot_options=ploptions(
                data_type='spe_sf0_pad',
                var_name='strahl_centroids',
                class_name='epad',
                subclass_name='centroids',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pitch Angle \n (degrees)',
                legend_label='Strahl Centroids',
                color='crimson',
                y_scale='linear',
                y_limit=[0, 180],
                line_width=1,
                line_style='-'
            )
        )

    @property
    def pitch_angle_y_values(self):
        if hasattr(self, 'raw_data') and 'pitch_angle_y_values' in self.raw_data:
            return self.raw_data['pitch_angle_y_values']
        print_manager.warning(f"Property 'pitch_angle_y_values' accessed but not found in raw_data for {self.__class__.__name__}")
        return None

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

epad = epad_strahl_class(None) #Initialize the class with no data
print('initialized epad class')

class epad_strahl_high_res_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'strahl': None,
            'centroids': None,
            'pitch_angle_y_values': None # Added for merging pitch angle
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'data_type', 'spe_hires_pad') # Explicitly set data_type for high-res
        object.__setattr__(self, '_current_operation_trange', None) # Initialize new attribute

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating high-resolution EPAD strahl variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated high-resolution EPAD strahl variables.")

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        # data_cubby.stash(self, class_name='epad_hr')

    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")
        
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_state = {}
        for subclass_name in self.raw_data.keys():                             # Use keys()
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

    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

        # First, check if it's a direct attribute/property of the instance
        if hasattr(self, subclass_name):
            # 🚀 PERFORMANCE FIX: Only set requested_trange on the SPECIFIC subclass being requested
            current_trange = TimeRangeTracker.get_current_trange()
            if current_trange:
                try:
                    attr_value = getattr(self, subclass_name)
                    if isinstance(attr_value, plot_manager):
                        attr_value.requested_trange = current_trange
                except Exception:
                    pass
            # Verify it's not a private or dunder attribute unless explicitly intended
            if not subclass_name.startswith('_'): 
                retrieved_attr = getattr(self, subclass_name)
                print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[ELECTRON_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[ELECTRON_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
        return None
    
    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.debug('epad_strahl_hr getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
        # raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(f"Setting attribute: {name} with value: {value}")
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'times_mesh', 'energy_index', 'data_type'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('epad_strahl_hr setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attrib
    
    def calculate_variables(self, imported_data):
        """Calculate and store high-resolution EPAD strahl variables"""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        # Extract data
        eflux = imported_data.data['EFLUX_VS_PA_E']
        self.raw_data['pitch_angle_y_values'] = imported_data.data['PITCHANGLE'] # Now in raw_data

        # Debug the time values
        print_manager.debug(f"Time values type: {type(self.time)}")
        print_manager.debug(f"Time values range: {self.time[0]} to {self.time[-1]}")

        # Set energy index based on encounter number
        # Convert numpy.datetime64 to datetime before using strftime
        date_str = pd.Timestamp(self.datetime_array[0]).strftime('%Y-%m-%d')
        encounter_number = get_encounter_number(date_str)
        if encounter_number in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9']:
            self.energy_index = 8
        else:
            self.energy_index = 12

        print_manager.debug(f"Encounter number: {encounter_number}")
        print_manager.debug(f"Energy index: {self.energy_index}")
        
        # Extract strahl flux for specific energy
        strahl = eflux[:, :, self.energy_index]
        
        # Calculate log version
        log_strahl = np.log10(strahl)
        strahl = log_strahl

        # Create time mesh to match strahl data dimensions
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(strahl.shape[1]),
            indexing='ij'
        )[0]

        # Calculate centroids
        centroids = np.ma.average(self.raw_data['pitch_angle_y_values'], # Use from raw_data
                                weights=strahl, 
                                axis=1)

        strahl_centroids = centroids
        # Store raw data
        self.raw_data['strahl'] = strahl # Already part of self.raw_data initialization
        self.raw_data['centroids'] = centroids # Already part of self.raw_data initialization
        # 'pitch_angle_y_values' is already set above
    
    def set_ploptions(self):
        """Set up the plotting options for high-resolution strahl data"""
        # Add the times_mesh regeneration logic for epad_strahl_high_res_class as well
        times_mesh_exists_hr = hasattr(self, 'times_mesh') and self.times_mesh is not None
        raw_data_strahl_exists_hr = hasattr(self, 'raw_data') and 'strahl' in self.raw_data and self.raw_data['strahl'] is not None
        datetime_array_exists_hr = hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0

        if times_mesh_exists_hr and isinstance(self.times_mesh, np.ndarray) and raw_data_strahl_exists_hr and datetime_array_exists_hr:
            needs_regeneration_hr = False
            if self.times_mesh.ndim != 2:
                needs_regeneration_hr = True
                print_manager.processing(f"[EPAD_HR_SET_PLOPT] times_mesh is not 2D (shape: {self.times_mesh.shape}). Regenerating.")
            elif self.times_mesh.shape[0] != len(self.datetime_array):
                needs_regeneration_hr = True
                print_manager.processing(f"[EPAD_HR_SET_PLOPT] times_mesh.shape[0] ({self.times_mesh.shape[0]}) != len(datetime_array) ({len(self.datetime_array)}). Regenerating.")
            elif self.raw_data['strahl'].ndim == 2 and self.times_mesh.shape[1] != self.raw_data['strahl'].shape[1]:
                needs_regeneration_hr = True
                print_manager.processing(f"[EPAD_HR_SET_PLOPT] times_mesh.shape[1] ({self.times_mesh.shape[1]}) != raw_data['strahl'].shape[1] ({self.raw_data['strahl'].shape[1]}). Regenerating.")
            elif self.raw_data['strahl'].ndim == 1 and self.times_mesh.shape[1] != 1:
                 pass # As per previous logic for 1D strahl data

            if needs_regeneration_hr:
                print_manager.processing(f"[EPAD_HR_SET_PLOPT] Regenerating times_mesh. Old shape: {self.times_mesh.shape if isinstance(self.times_mesh, np.ndarray) else 'N/A'}")
                self.times_mesh = np.meshgrid(
                    self.datetime_array,
                    np.arange(self.raw_data['strahl'].shape[1] if self.raw_data['strahl'].ndim == 2 else 1),
                    indexing='ij'
                )[0]
                print_manager.processing(f"[EPAD_HR_SET_PLOPT] Regenerated times_mesh. New shape: {self.times_mesh.shape}")

        self.strahl = plot_manager(
            self.raw_data['strahl'],
            plot_options=ploptions(
                data_type='spe_af0_pad',
                var_name='log_strahl_hr',
                class_name='epad_hr',
                subclass_name='strahl',
                plot_type='spectral',
                datetime_array=self.times_mesh,  # Use the mesh for time array
                y_label='Pitch Angle\n(degrees)',
                legend_label='Electron PAD (High Res)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['pitch_angle_y_values'], # Use from raw_data
                colormap='jet',
                colorbar_scale='log',
                colorbar_limits=None
            )
        )

        # Initialize centroids with plot_manager
        self.centroids = plot_manager(
            self.raw_data['centroids'],
            plot_options=ploptions(
                data_type='spe_af0_pad',
                var_name='strahl_centroids',
                class_name='epad_hr',
                subclass_name='centroids',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pitch Angle \n (degrees)',
                legend_label='Strahl Centroids',
                color='crimson',
                y_scale='linear',
                y_limit=[0, 180],
                line_width=0.5,
                line_style='-'
            )
        )

    @property
    def pitch_angle_y_values(self):
        if hasattr(self, 'raw_data') and 'pitch_angle_y_values' in self.raw_data:
            return self.raw_data['pitch_angle_y_values']
        print_manager.warning(f"Property 'pitch_angle_y_values' accessed but not found in raw_data for {self.__class__.__name__}")
        return None

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

epad_hr = epad_strahl_high_res_class(None) #Initialize the class with no data
print('initialized epad_hr class')