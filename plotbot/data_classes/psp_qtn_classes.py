# plotbot/data_classes/psp_qtn_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store QTN variables 🎉
class psp_qtn_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'psp_qtn')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'sqtn_rfs_v1v2')      # Key for data_types.data_types
        object.__setattr__(self, 'subclass_name', None)         # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'density': None,      # Electron density from QTN
            'temperature': None   # Electron core temperature from QTN
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None) # For dependency tracking

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating QTN variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated QTN variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[PSP_QTN_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[PSP_QTN_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['density', 'temperature']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_ploption_snapshot(current_plot_states[comp_name])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_ploptions()                                                  # Recreate plot managers for standard components
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for comp_name, state in current_plot_states.items():                    # Restore saved states
            if hasattr(self, comp_name): # For standard components
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_options, attr):
                            setattr(manager.plot_options, attr, value)
                    print_manager.datacubby(f"Restored {comp_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[QTN_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[QTN_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
        print_manager.dependency_management('psp_qtn getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
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
            print_manager.dependency_management('psp_qtn setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate the QTN-derived electron density and temperature."""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        print_manager.dependency_management("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.dependency_management("First element type: {type(self.datetime_array[0])}")
        
        # Extract QTN data - these variable names will need to be verified from actual CDF files
        # Common QTN variable names include 'electron_density', 'n_elec', 'DENS_ELEC', etc.
        density_var_names = ['electron_density', 'n_elec', 'DENS_ELEC', 'ne_qtn']
        temp_var_names = ['electron_core_temperature', 'T_elec', 'TEMP_ELEC', 'Te_core']
        
        # Try to find density variable
        density_data = None
        density_var_found = None
        for var_name in density_var_names:
            if var_name in imported_data.data:
                density_data = np.asarray(imported_data.data[var_name])
                density_var_found = var_name
                print_manager.dependency_management(f"Found density variable: {var_name}")
                break
        
        if density_data is None:
            print_manager.warning("No density variable found in QTN data. Available variables:")
            print_manager.warning(f"{list(imported_data.data.keys())}")
            density_data = np.array([])  # Empty array as fallback
        
        # Try to find temperature variable
        temperature_data = None
        temp_var_found = None
        for var_name in temp_var_names:
            if var_name in imported_data.data:
                temperature_data = np.asarray(imported_data.data[var_name])
                temp_var_found = var_name
                print_manager.dependency_management(f"Found temperature variable: {var_name}")
                break
        
        if temperature_data is None:
            print_manager.warning("No temperature variable found in QTN data. Available variables:")
            print_manager.warning(f"{list(imported_data.data.keys())}")
            temperature_data = np.array([])  # Empty array as fallback

        # Store all data in raw_data dictionary
        self.raw_data = {
            'density': density_data,
            'temperature': temperature_data
        }

        print_manager.dependency_management(f"\nDebug - QTN Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        print_manager.dependency_management(f"Density data shape: {density_data.shape if density_data is not None else 'None'}")
        print_manager.dependency_management(f"Temperature data shape: {temperature_data.shape if temperature_data is not None else 'None'}")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")
    
    def set_ploptions(self):
        """Set up the plotting options for QTN density and temperature"""
        # Electron density with sky blue color (as requested)
        self.density = plot_manager(
            self.raw_data['density'],
            plot_options=ploptions(
                data_type='sqtn_rfs_v1v2',       # Actual data product name
                var_name='electron_density',     # Variable name
                class_name='psp_qtn',           # Class handling this data
                subclass_name='density',        # Specific component
                plot_type='time_series',        # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='n$_e$ (cm$^{-3}$)',   # Y-axis label
                legend_label='n$_e$ (QTN)',     # Legend text
                color='skyblue',               # Sky blue color as requested
                y_scale='linear',              # Scale type
                y_limit=None,                  # Y-axis limits
                line_width=1,                  # Line width
                line_style='-'                 # Line style
            )
        )

        # Electron core temperature
        self.temperature = plot_manager(
            self.raw_data['temperature'],
            plot_options=ploptions(
                data_type='sqtn_rfs_v1v2',       # Actual data product name
                var_name='electron_temperature', # Variable name
                class_name='psp_qtn',           # Class handling this data
                subclass_name='temperature',    # Specific component
                plot_type='time_series',        # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='T$_e$ (eV)',          # Y-axis label
                legend_label='T$_e$ (QTN)',     # Legend text
                color='darkorange',            # Temperature color
                y_scale='linear',              # Scale type
                y_limit=None,                  # Y-axis limits
                line_width=1,                  # Line width
                line_style='-'                 # Line style
            )
        )

    def ensure_internal_consistency(self):
        """Ensures .time and .datetime_array are consistent with .raw_data."""
        print_manager.dependency_management(f"*** QTN ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        
        print_manager.dependency_management(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print_manager.dependency_management(f"    PRE-CHECK - time len: {original_time_len}")
        
        changed_time = False

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
            
            if changed_time and hasattr(self, 'set_ploptions'):
                print_manager.dependency_management(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}).")
                self.set_ploptions()
        else:
            print_manager.dependency_management(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'

        if changed_time:
            print_manager.dependency_management(f"*** QTN ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print_manager.dependency_management(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print_manager.dependency_management(f"    POST-FIX - time len: {final_time_len}")
        else:
            print_manager.dependency_management(f"*** QTN ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}")
        print_manager.dependency_management(f"*** QTN ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

psp_qtn = psp_qtn_class(None) #Initialize the class with no data
print('initialized psp_qtn class') 