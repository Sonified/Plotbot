#plotbot/data_classes/psp_mag_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

# from ..plot_manager import plot_manager # Import moved into function to avoid circular import

# Import our custom managers (UPDATED PATHS)
from plotbot.print_manager import print_manager
# from plotbot.data_cubby import data_cubby # REMOVED to break circular import
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

def _format_setattr_debug(name, value):
    """Helper function to create a concise debug string for __setattr__."""
    MAX_LEN = 100 # Max length for string representation
    msg = f"Setting attribute: {name}"
    if isinstance(value, (np.ndarray, pd.Series, pd.DataFrame)):
        dtype_str = f"dtype={getattr(value, 'dtype', 'N/A')}"
        shape_str = f"shape={getattr(value, 'shape', 'N/A')}"
        return f"{msg} (type={type(value).__name__}, {shape_str}, {dtype_str})"
    else:
        val_str = repr(value)
        if len(val_str) > MAX_LEN:
            val_str = val_str[:MAX_LEN] + '...'
        return f"{msg} with value: {val_str}"

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
            'pmag': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

        print(f"*** MAG_CLASS_INIT (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")
        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating mag rtn 4sa variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag rtn 4sa variables.")
    
    def update(self, imported_data):
        print(f"*** MAG_CLASS_UPDATE (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'}. Keys: {list(imported_data.data.keys()) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
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
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        print_manager.variable_testing(f"Accessing subclass: mag_rtn_4sa.{subclass_name}")
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
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
                # Re-raise AttributeError if the internal/dunder method truly doesn't exist
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.debug('mag_rtn_4sa getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_rtn_4sa setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.variable_testing(f"Attempted to set unknown attribute: {name}")
           
            # Do not set the attrib
    def calculate_variables(self, imported_data):
        print(f"*** MAG_CLASS_CALCVARS (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
        if hasattr(imported_data, 'data') and isinstance(imported_data.data, dict):
            print(f"    Available keys in imported_data.data for CALCVARS: {list(imported_data.data.keys())}")
        else:
            print(f"    CALCVARS: imported_data.data is missing or not a dict.")
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))        
        
        print_manager.debug("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.debug("First element type: {type(self.datetime_array[0])}")
        
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
            'pmag': pmag
        }

        # # Convert TT2000 timestamps to datetime objects using cdflib
        # self.datetime = cdflib.cdfepoch.to_datetime(self.time)

        print_manager.debug("\nDebug - Data Arrays:")
        print_manager.debug("Time array shape: {self.time.shape}")
        print_manager.debug(f"Field data shape: {self.field.shape}")
        print_manager.debug(f"First TT2000 time: {self.time[0]}")
    
    def set_ploptions(self):
        """Create plot managers for each component with default options"""
        print_manager.variable_testing(f"Setting up plot options for mag_rtn_4sa variables")
        
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
        print_manager.variable_testing(f"FYI: Example mag data: Created mag_rtn_4sa.all variable with {3 if self.raw_data['br'] is not None else 0} components")
        
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
                var_name='bmag_rtn_4sa',    # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='|B|',        # Legend text
                color='k',                 # Plot color
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
                var_name='pmag_rtn_4sa',    # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='pmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Magnetic\nPressure\n(nPa)', # Y-axis label
                legend_label='$P_{mag}$',   # Legend text
                color='darkblue',          # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
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

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print(f"    PRE-CHECK - time len: {original_time_len}")
        print(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
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
                    print(f"    Updated self.field from RTN components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print(f"    Nullifying self.field. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print(f"    Setting self.field to None. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print(f"    POST-FIX - time len: {final_time_len}")
            print(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

mag_rtn_4sa = mag_rtn_4sa_class(None) #Initialize the class with no data
print('initialized mag_rtn_4sa class')


# 🎉 Define the main class to calculate and store mag_rtn variables 🎉
class mag_rtn_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'mag_rtn')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'mag_RTN')      # Key for psp_data_types.data_types
        object.__setattr__(self, 'subclass_name', None)         # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'br': None,
            'bt': None,
            'bn': None,
            'bmag': None,
            'pmag': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating mag rtn variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag rtn variables.")
    
    def update(self, imported_data): #This is function is the exact same across all classes :)
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
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
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
        print_manager.debug('mag_rtn getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_rtn setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.variable_testing(f"Attempted to set unknown attribute: {name}")
           
            # Do not set the attrib

    def calculate_variables(self, imported_data):
        """Calculate the magnetic field components and derived quantities."""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        print_manager.debug("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.debug("First element type: {type(self.datetime_array[0])}")
        
        # Get field data as numpy array
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_RTN'])
        
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
            'pmag': pmag
        }

        print_manager.debug("\nDebug - Data Arrays:")
        print_manager.debug("Time array shape: {self.time.shape}")
        print_manager.debug(f"Field data shape: {self.field.shape}")
        print_manager.debug(f"First TT2000 time: {self.time[0]}")
    
    def set_ploptions(self):
        """Set up the plotting options for all magnetic field components"""
        # Initialize each component with plot_manager
        self.all = plot_manager(
            [self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']],
            plot_options=ploptions(
                data_type='mag_RTN',       # Actual data product name
                var_name=['br_rtn', 'bt_rtn', 'bn_rtn'],  # Variable names
                class_name='mag_rtn',      # Class handling this data
                subclass_name='all',       # Specific component
                plot_type='time_series',   # Type of plot
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

        self.br = plot_manager(
            self.raw_data['br'],
            plot_options=ploptions(
                data_type='mag_RTN',       # Actual data product name
                var_name='br_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='br',        # Specific component
                plot_type='time_series',   # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_R$',      # Legend text
                color='forestgreen',       # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bt = plot_manager(
            self.raw_data['bt'],
            plot_options=ploptions(
                data_type='mag_RTN',       # Actual data product name
                var_name='bt_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bt',        # Specific component
                plot_type='time_series',   # Type of plot
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
                data_type='mag_RTN',       # Actual data product name
                var_name='bn_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bn',        # Specific component
                plot_type='time_series',   # Type of plot
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
                data_type='mag_RTN',       # Actual data product name
                var_name='bmag_rtn',       # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bmag',      # Specific component
                plot_type='time_series',   # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='|B|',        # Legend text
                color='k',                 # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.pmag = plot_manager(
            self.raw_data['pmag'],
            plot_options=ploptions(
                data_type='mag_RTN',       # Actual data product name
                var_name='pmag_rtn',       # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='pmag',      # Specific component
                plot_type='time_series',   # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Magnetic\nPressure\n(nPa)', # Y-axis label
                legend_label='$P_{mag}$',   # Legend text
                color='darkblue',          # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print(f"    PRE-CHECK - time len: {original_time_len}")
        print(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
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
                    print(f"    Updated self.field from RTN components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print(f"    Nullifying self.field. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print(f"    Setting self.field to None. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print(f"    POST-FIX - time len: {final_time_len}")
            print(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

mag_rtn = mag_rtn_class(None) #Initialize the class with no data
print('initialized mag_rtn class')

# 🎉 Define the main class to calculate and store mag_sc_4sa variables 🎉
class mag_sc_4sa_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'bx': None,
            'by': None,
            'bz': None,
            'bmag': None,
            'pmag': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating mag sc 4sa variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag sc 4sa variables.")
    
    def update(self, imported_data): #This is function is the exact same across all classes :)
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
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
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
        print_manager.debug('mag_sc_4sa getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_sc_4sa setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.variable_testing(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate and store MAG SC 4sa variables"""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        print_manager.debug("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.debug("First element type: {type(self.datetime_array[0])}")
        
        # Get field data as numpy array
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_SC_4_Sa_per_Cyc'])
        
        # Extract components and calculate derived quantities efficiently
        bx = self.field[:, 0]
        by = self.field[:, 1]
        bz = self.field[:, 2]
        
        # Calculate magnitude using numpy operations
        bmag = np.sqrt(bx**2 + by**2 + bz**2)
        
        # Calculate magnetic pressure
        mu_0 = 4 * np.pi * 1e-7  # Permeability of free space
        pmag = (bmag**2) / (2 * mu_0) * 1e-9  # Convert to nPa
        
        # Store all data in raw_data dictionary
        self.raw_data = {
            'all': [bx, by, bz],
            'bx': bx,
            'by': by,
            'bz': bz,
            'bmag': bmag,
            'pmag': pmag
        }

        print_manager.debug("\nDebug - Data Arrays:")
        print_manager.debug("Time array shape: {self.time.shape}")
        print_manager.debug(f"Field data shape: {self.field.shape}")
        print_manager.debug(f"First TT2000 time: {self.time[0]}")
    
    def set_ploptions(self):
        """Set up the plotting options for all magnetic field components."""
        self.all = plot_manager(
            [self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']],
            plot_options=ploptions(
                data_type='mag_SC_4sa',     # Actual data product name
                var_name=['bx_sc_4sa', 'by_sc_4sa', 'bz_sc_4sa'],  # Variable names
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='all',        # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label=['$B_X$', '$B_Y$', '$B_Z$'],  # Legend text
                color=['red', 'blue', 'purple'],  # Plot colors
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=[1, 1, 1],      # Line widths
                line_style=['-', '-', '-'] # Line styles
            )
        )

        self.bx = plot_manager(
            self.raw_data['bx'],
            plot_options=ploptions(
                data_type='mag_SC_4sa',     # Actual data product name
                var_name='bx_sc_4sa',       # Variable name
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='bx',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_X$',      # Legend text
                color='red',               # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.by = plot_manager(
            self.raw_data['by'],
            plot_options=ploptions(
                data_type='mag_SC_4sa',     # Actual data product name
                var_name='by_sc_4sa',       # Variable name
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='by',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_Y$',      # Legend text
                color='blue',              # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bz = plot_manager(
            self.raw_data['bz'],
            plot_options=ploptions(
                data_type='mag_SC_4sa',     # Actual data product name
                var_name='bz_sc_4sa',       # Variable name
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='bz',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_Z$',      # Legend text
                color='purple',            # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='mag_SC_4sa',     # Actual data product name
                var_name='bmag_sc_4sa',     # Variable name
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='bmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='|B|',        # Legend text
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
                data_type='mag_SC_4sa',     # Actual data product name
                var_name='pmag_sc_4sa',     # Variable name
                class_name='mag_sc_4sa',    # Class handling this data
                subclass_name='pmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Magnetic\nPressure\n(nPa)', # Y-axis label
                legend_label='$P_{mag}$',   # Legend text
                color='navy',              # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
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

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print(f"    PRE-CHECK - time len: {original_time_len}")
        print(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
                changed_time = True

            expected_len = len(self.datetime_array)
            if ('bx' in self.raw_data and self.raw_data['bx'] is not None and
                'by' in self.raw_data and self.raw_data['by'] is not None and
                'bz' in self.raw_data and self.raw_data['bz'] is not None and
                len(self.raw_data['bx']) == expected_len and
                len(self.raw_data['by']) == expected_len and
                len(self.raw_data['bz']) == expected_len):
                new_field = np.column_stack((self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']))
                if not hasattr(self, 'field') or self.field is None or not np.array_equal(self.field, new_field):
                    self.field = new_field
                    print(f"    Updated self.field from SC components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print(f"    Nullifying self.field. Reason: SC components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print(f"    Setting self.field to None. Reason: SC components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print(f"    POST-FIX - time len: {final_time_len}")
            print(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

mag_sc_4sa = mag_sc_4sa_class(None) #Initialize the class with no data
print('initialized mag_sc_4sa class')

# 🎉 Define the main class to calculate and store mag_sc variables 🎉
class mag_sc_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'bx': None,
            'by': None,
            'bz': None,
            'bmag': None,
            'pmag': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating mag sc variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag sc variables.")
    
    #mag_sc_location
    def update(self, imported_data): #This is function is the exact same across all classes :)
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
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
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
        print_manager.debug('mag_sc getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_sc setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.variable_testing(f"Attempted to set unknown attribute: {name}")
           
            # Do not set the attrib
    
    def calculate_variables(self, imported_data):
        """Calculate and store MAG SC variables"""
        print_manager.debug(f"[mag_sc.calculate_variables ID:{id(self)}] Entered.")
        print_manager.debug(f"  imported_data.times len: {len(imported_data.times) if hasattr(imported_data, 'times') else 'N/A'}")
        print_manager.debug(f"  imported_data.data keys: {list(imported_data.data.keys()) if hasattr(imported_data, 'data') else 'N/A'}")

        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        print_manager.debug(f"  Assigned self.time, len: {len(self.time)}")
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        print_manager.debug(f"  Assigned self.datetime_array, len: {len(self.datetime_array)}")
        
        # Get field data as numpy array
        print_manager.debug(f"--- [mag_sc.calculate_variables] Accessing field data 'psp_fld_l2_mag_SC' ---") # ADDED
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_SC'])
        print_manager.debug(f"--- [mag_sc.calculate_variables] Field data shape: {self.field.shape if self.field is not None else 'None'} ---") # ADDED
        
        # Extract components and calculate derived quantities efficiently
        print_manager.debug(f"--- [mag_sc.calculate_variables] Extracting components bx, by, bz ---") # ADDED
        bx = self.field[:, 0]
        by = self.field[:, 1]
        bz = self.field[:, 2]
        
        # Calculate magnitude using numpy operations
        print_manager.debug(f"--- [mag_sc.calculate_variables] Calculating bmag ---")
        bmag = np.sqrt(bx**2 + by**2 + bz**2)
        
        # Calculate magnetic pressure
        print_manager.debug(f"--- [mag_sc.calculate_variables] Calculating pmag ---")
        mu_0 = 4 * np.pi * 1e-7  # Permeability of free space
        pmag = (bmag**2) / (2 * mu_0) * 1e-9  # Convert to nPa
        
        # Store all data in raw_data dictionary
        print_manager.debug(f"--- [mag_sc.calculate_variables] Storing data in raw_data ---")
        self.raw_data = {
            'all': [bx, by, bz],
            'bx': bx,
            'by': by,
            'bz': bz,
            'bmag': bmag,
            'pmag': pmag
        }

        print_manager.debug(f"--- [mag_sc.calculate_variables] END ---") # ADDED
        # print_manager.debug("\nDebug - Data Arrays:") # Original debug
        # print_manager.debug("Time array shape: {self.time.shape}") # Original debug
        # print_manager.debug(f"Field data shape: {self.field.shape}") # Original debug
        # print_manager.debug(f"First TT2000 time: {self.time[0]}") # Original debug
    
    def set_ploptions(self):
        """Set up the plotting options for all magnetic field components."""
        print_manager.debug(f"[mag_sc.set_ploptions ID:{id(self)}] Entered. self.datetime_array len: {len(self.datetime_array) if self.datetime_array is not None else 'None'}")
        if self.raw_data and self.raw_data.get('br') is not None:
             print_manager.debug(f"  self.raw_data['br'] len: {len(self.raw_data['br'])}")
        else:
             print_manager.debug(f"  self.raw_data['br'] is None or self.raw_data is None for set_ploptions")
        # Initialize each component with plot_manager (Copied from previous state)
        self.all = plot_manager(
            [self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']],
            plot_options=ploptions(
                data_type='mag_SC',         # Actual data product name
                var_name=['bx_sc', 'by_sc', 'bz_sc'],  # Variable names
                class_name='mag_sc',        # Class handling this data
                subclass_name='all',        # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label=['$B_X$', '$B_Y$', '$B_Z$'],  # Legend text
                color=['crimson', 'darkcyan', 'purple'],  # Plot colors
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=[1, 1, 1],      # Line widths
                line_style=['-', '-', '-'] # Line styles
            )
        )

        self.bx = plot_manager(
            self.raw_data['bx'],
            plot_options=ploptions(
                data_type='mag_SC',         # Actual data product name
                var_name='bx_sc',           # Variable name
                class_name='mag_sc',        # Class handling this data
                subclass_name='bx',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_X$',      # Legend text
                color='crimson',           # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.by = plot_manager(
            self.raw_data['by'],
            plot_options=ploptions(
                data_type='mag_SC',         # Actual data product name
                var_name='by_sc',           # Variable name
                class_name='mag_sc',        # Class handling this data
                subclass_name='by',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_Y$',      # Legend text
                color='darkcyan',          # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bz = plot_manager(
            self.raw_data['bz'],
            plot_options=ploptions(
                data_type='mag_SC',         # Actual data product name
                var_name='bz_sc',           # Variable name
                class_name='mag_sc',        # Class handling this data
                subclass_name='bz',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_Z$',      # Legend text
                color='purple',            # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='mag_SC',         # Actual data product name
                var_name='bmag_sc',         # Variable name
                class_name='mag_sc',        # Class handling this data
                subclass_name='bmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='|B|',        # Legend text
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
                data_type='mag_SC',         # Actual data product name
                var_name='pmag_sc',         # Variable name
                class_name='mag_sc',        # Class handling this data
                subclass_name='pmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Magnetic\nPressure\n(nPa)', # Y-axis label
                legend_label='$P_{mag}$',   # Legend text
                color='navy',              # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
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

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print(f"    PRE-CHECK - time len: {original_time_len}")
        print(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
                changed_time = True

            expected_len = len(self.datetime_array)
            if ('bx' in self.raw_data and self.raw_data['bx'] is not None and
                'by' in self.raw_data and self.raw_data['by'] is not None and
                'bz' in self.raw_data and self.raw_data['bz'] is not None and
                len(self.raw_data['bx']) == expected_len and
                len(self.raw_data['by']) == expected_len and
                len(self.raw_data['bz']) == expected_len):
                new_field = np.column_stack((self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']))
                if not hasattr(self, 'field') or self.field is None or not np.array_equal(self.field, new_field):
                    self.field = new_field
                    print(f"    Updated self.field from SC components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print(f"    Nullifying self.field. Reason: SC components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print(f"    Setting self.field to None. Reason: SC components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print(f"    POST-FIX - time len: {final_time_len}")
            print(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

mag_sc = mag_sc_class(None) #Initialize the class with no data
print('initialized mag_sc class')