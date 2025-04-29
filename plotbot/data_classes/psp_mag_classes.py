#plotbot/data_classes/psp_mag_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

# from ..plot_manager import plot_manager # Import moved into function to avoid circular import

# Import our custom managers (UPDATED PATHS)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

# 🎉 Define the main class to calculate and store mag_rtn_4sa variables 🎉
class mag_rtn_4sa_class:
    def __init__(self, imported_data):
        # Initialize attributes
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
        object.__setattr__(self, 'source_filenames', [])

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

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        data_cubby.stash(self, class_name='mag_rtn_4sa')
    
    def update(self, imported_data):
        """Method to update class with new data."""
        print_manager.debug(f"---> Entering update method for {self.__class__.__name__}") # DEBUG ENTRY
        # === START TEMPORARY DEBUGGING ===
        if imported_data is None:
            print_manager.debug(f"[UPDATE DEBUG] imported_data is None for {self.__class__.__name__}.")
        else:
            print_manager.debug(f"[UPDATE DEBUG] imported_data type: {type(imported_data)} for {self.__class__.__name__}")
            if hasattr(imported_data, 'source_filenames'):
                print_manager.debug(f"[UPDATE DEBUG] imported_data HAS source_filenames attr for {self.__class__.__name__}.")
                print_manager.debug(f"[UPDATE DEBUG] imported_data.source_filenames = {imported_data.source_filenames}")
            else:
                print_manager.debug(f"[UPDATE DEBUG] imported_data DOES NOT HAVE source_filenames attr for {self.__class__.__name__}.")
        # === END TEMPORARY DEBUGGING ===
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        # Store the source filenames associated with this data update
        if hasattr(imported_data, 'source_filenames'):
            self.source_filenames = imported_data.source_filenames
            print_manager.debug(f"Stored {len(self.source_filenames)} source filenames on {self.__class__.__name__} instance.")
        else:
            # Ensure the attribute exists even if data_object didn't have it
            # Keep existing ones if update doesn't provide new ones? Or clear? Let's clear for now.
            self.source_filenames = []
            print_manager.debug(f"No source_filenames found on data_object for {self.__class__.__name__}.")
        
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
        
        print_manager.debug(f"---> Exiting update method for {self.__class__.__name__} (just before return/end)") # DEBUG EXIT
        
        # NEW: Save after update if storage enabled
        if data_cubby.use_pkl_storage:
             data_cubby.save_to_disk(obj_to_save=self, identifier_to_save=self.all.plot_options.data_type)
    
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

    def __getattr__(self, name): # Prints a friendly error message if an attribute is not found
        # --- FIX: Simplify __getattr__ to correctly raise AttributeError ---
        # Remove the explicit check for __*__ methods here.
        # __getattr__ is only called if standard lookup fails.
        # if name.startswith('__') and name.endswith('__'):
        #     raise AttributeError(f"Special method {name} not handled by __getattr__")
            
        print_manager.debug(f'{self.__class__.__name__} getattr helper!') # Use class name
        print_manager.variable_testing(f"__getattr__ called for {self.__class__.__name__}.{name}")
        
        # Attempt to generate helpful message, but ensure AttributeError is raised
        try:
            available_attrs = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
            print(f"\n'{name}\' is not a recognized attribute for {self.__class__.__name__}, friend!")
            if available_attrs:
                print(f"Try one of these: {', '.join(available_attrs)}")
            else:
                print("(No raw_data available to suggest attributes)")
        except Exception as e:
            # Avoid errors within getattr itself from hiding the main issue
            print(f"Error generating suggestion in __getattr__: {e}")
            
        # CRITICAL: Always raise AttributeError as expected for __getattr__
        raise AttributeError(f"'{self.__class__.__name__}\' object has no attribute '{name}\'")
        # ------------------------------------------------------------------
    
    def __setattr__(self, name, value):
        """Handle attribute assignment with friendly error messages."""
        # Allow setting known attributes
        # Simplify debug print: try to show only first few elements/rows and limit total length
        try:
            # Check type name for plot_manager to avoid circular import if necessary
            is_plot_manager = type(value).__name__ == 'plot_manager'

            # Limit preview for lists/arrays AND plot_manager
            if is_plot_manager:
                # Concise representation for plot_manager
                pm_id = f" for {value.plot_options.data_type}.{value.plot_options.subclass_name}" if hasattr(value, 'plot_options') else ""
                preview = f"<plot_manager instance{pm_id}>"
            elif isinstance(value, (list, np.ndarray)):
                # Show first 2 elements only for other lists/arrays
                preview = repr(value[:2]) + ('...' if len(value) > 2 else '')
            elif callable(value):
                # Try to avoid printing the full callable representation
                preview = f"<callable {name}>"
            else:
                # Limit length of other representations too
                preview = repr(value)
                if len(preview) > 80:
                    preview = preview[:80] + '...'
            value_repr = preview # Use the generated preview

        except Exception as e:
            # Fallback to default representation if slicing fails or it's not applicable
            value_repr = repr(value)
            if len(value_repr) > 80: # Apply length limit even in fallback
                 value_repr = value_repr[:80] + '...'
            value_repr += f" (repr error: {e})"

        print_manager.debug(f"Setting attribute: {name} with value: {value_repr}")

        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'source_filenames'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_rtn_4sa setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.variable_testing(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate the magnetic field components and derived quantities."""
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
                line_style=['-', '-', '-'], # Line styles
                source_filenames=self.source_filenames # Pass source filenames
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
                line_style='-',             # Line style
                source_filenames=self.source_filenames # Pass source filenames
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
                line_style='-',             # Line style
                source_filenames=self.source_filenames # Pass source filenames
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
                line_style='-',             # Line style
                source_filenames=self.source_filenames # Pass source filenames
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
                legend_label='|B|',         # Legend text
                color='k',                 # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-',             # Line style
                source_filenames=self.source_filenames # Pass source filenames
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
                legend_label='$P_{mag}$',  # Legend text
                color='darkblue',          # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-',             # Line style
                source_filenames=self.source_filenames # Pass source filenames
            )
        )

mag_rtn_4sa = mag_rtn_4sa_class(None) #Initialize the class with no data
print('initialized mag_rtn_4sa class')


# 🎉 Define the main class to calculate and store mag_rtn variables 🎉
class mag_rtn_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
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
        object.__setattr__(self, 'source_filenames', [])

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

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        data_cubby.stash(self, class_name='mag_rtn')
    
    def update(self, imported_data):
        """Method to update class with new data."""
        print_manager.debug(f"---> Entering update method for {self.__class__.__name__}") # DEBUG ENTRY
        # === START TEMPORARY DEBUGGING ===
        if imported_data is None:
            print_manager.debug(f"[UPDATE DEBUG] imported_data is None for {self.__class__.__name__}.")
        else:
            print_manager.debug(f"[UPDATE DEBUG] imported_data type: {type(imported_data)} for {self.__class__.__name__}")
            if hasattr(imported_data, 'source_filenames'):
                print_manager.debug(f"[UPDATE DEBUG] imported_data HAS source_filenames attr for {self.__class__.__name__}.")
                print_manager.debug(f"[UPDATE DEBUG] imported_data.source_filenames = {imported_data.source_filenames}")
            else:
                print_manager.debug(f"[UPDATE DEBUG] imported_data DOES NOT HAVE source_filenames attr for {self.__class__.__name__}.")
        # === END TEMPORARY DEBUGGING ===
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        # Store the source filenames associated with this data update
        if hasattr(imported_data, 'source_filenames'):
            self.source_filenames = imported_data.source_filenames
            print_manager.debug(f"Stored {len(self.source_filenames)} source filenames on {self.__class__.__name__} instance.")
        else:
            self.source_filenames = []
            print_manager.debug(f"No source_filenames found on data_object for {self.__class__.__name__}.")
        
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
        
        # NEW: Save after update if storage enabled
        if data_cubby.use_pkl_storage:
             data_cubby.save_to_disk(obj_to_save=self, identifier_to_save=self.all.plot_options.data_type)
    
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

    def __getattr__(self, name): # Prints a friendly error message if an attribute is not found
        # --- FIX: Simplify __getattr__ to correctly raise AttributeError ---
        # Remove the explicit check for __*__ methods here.
        # __getattr__ is only called if standard lookup fails.
        # if name.startswith('__') and name.endswith('__'):
        #     raise AttributeError(f"Special method {name} not handled by __getattr__")
            
        print_manager.debug(f'{self.__class__.__name__} getattr helper!') # Use class name
        print_manager.variable_testing(f"__getattr__ called for {self.__class__.__name__}.{name}")
        
        # Attempt to generate helpful message, but ensure AttributeError is raised
        try:
            available_attrs = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
            print(f"\n'{name}\' is not a recognized attribute for {self.__class__.__name__}, friend!")
            if available_attrs:
                print(f"Try one of these: {', '.join(available_attrs)}")
            else:
                print("(No raw_data available to suggest attributes)")
        except Exception as e:
            # Avoid errors within getattr itself from hiding the main issue
            print(f"Error generating suggestion in __getattr__: {e}")
            
        # CRITICAL: Always raise AttributeError as expected for __getattr__
        raise AttributeError(f"'{self.__class__.__name__}\' object has no attribute '{name}\'")
        # ------------------------------------------------------------------
    
    def __setattr__(self, name, value):
        """Handle attribute assignment with friendly error messages."""
        # Allow setting known attributes
        # Simplify debug print: try to show only first few elements/rows and limit total length
        try:
            # Check type name for plot_manager to avoid circular import if necessary
            is_plot_manager = type(value).__name__ == 'plot_manager'

            # Limit preview for lists/arrays AND plot_manager
            if is_plot_manager:
                # Concise representation for plot_manager
                pm_id = f" for {value.plot_options.data_type}.{value.plot_options.subclass_name}" if hasattr(value, 'plot_options') else ""
                preview = f"<plot_manager instance{pm_id}>"
            elif isinstance(value, (list, np.ndarray)):
                # Show first 2 elements only for other lists/arrays
                preview = repr(value[:2]) + ('...' if len(value) > 2 else '')
            elif callable(value):
                # Try to avoid printing the full callable representation
                preview = f"<callable {name}>"
            else:
                # Limit length of other representations too
                preview = repr(value)
                if len(preview) > 80:
                    preview = preview[:80] + '...'
            value_repr = preview # Use the generated preview

        except Exception as e:
            # Fallback to default representation if slicing fails or it's not applicable
            value_repr = repr(value)
            if len(value_repr) > 80: # Apply length limit even in fallback
                 value_repr = value_repr[:80] + '...'
            value_repr += f" (repr error: {e})"

        print_manager.debug(f"Setting attribute: {name} with value: {value_repr}")

        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'source_filenames'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_rtn setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attribute
    
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

mag_rtn = mag_rtn_class(None) #Initialize the class with no data
print('initialized mag_rtn class')

# 🎉 Define the main class to calculate and store mag_sc_4sa variables 🎉
class mag_sc_4sa_class:
    def __init__(self, data_source, cdf_obj):
        # --- NEW: Handle initialization with None ---
        if cdf_obj is None:
            # Initialize with default empty values
            object.__setattr__(self, 'raw_data', {}) # Use object.__setattr__ to bypass our custom __setattr__
            object.__setattr__(self, 'metadata', {})
            object.__setattr__(self, 'field_components', ['B_X', 'B_Y', 'B_Z']) # Default components
            object.__setattr__(self, 'time_index', 'epoch') # Default time index
            object.__setattr__(self, 'reference_frame', 'SC') # Default frame
            object.__setattr__(self, 'time', np.array([])) # Empty numpy array for time
            object.__setattr__(self, 'datetime_array', np.array([])) # Empty numpy array for datetime
            object.__setattr__(self, 'field', np.array([])) # Empty numpy array for field
            # Initialize specific data keys to None or empty arrays
            self.raw_data = { 
                'all': [None, None, None],
                'bx': None, 
                'by': None, 
                'bz': None, 
                'bmag': None, 
                'pmag': None
            } 
            self.set_ploptions() # Call set_ploptions like other classes
            print_manager.debug(f"{self.__class__.__name__}: Initialized with no data (cdf_obj was None).")
            return # Skip the rest of __init__
        # --- END NEW ---
            
        # Existing logic when cdf_obj is provided
        self.raw_data = cdf_obj[data_source]
        self.metadata = cdf_obj[data_source].attrs
        self.field_components = ['B_X', 'B_Y', 'B_Z'] # Make sure this matches default if needed
        self.time_index = 'epoch'
        self.reference_frame = 'SC' # Make sure this matches default if needed
        self.calculate_variables(cdf_obj[data_source])
        self.set_ploptions() # Also call set_ploptions when data *is* provided
        print_manager.debug(f"{self.__class__.__name__}: Initialized with data.")

    def __setattr__(self, name, value):
        # Handle attribute initialization during __init__
        if name in ['raw_data', 'metadata', 'field_components', 'time_index', 'reference_frame']:
            super().__setattr__(name, value)
            return

        # Check if the attribute is allowed based on raw_data keys
        allowed_attrs = list(self.raw_data.keys()) if self.raw_data else []
        if name not in allowed_attrs and name not in self.__dict__:
             # Try to provide a helpful error message with available attributes
            print(f"\n--- Debug Info ---")
            print(f"Attempted to set attribute '{name}' on {self.__class__.__name__}.")
            if allowed_attrs:
                print(f"Available attributes from raw_data: {', '.join(allowed_attrs)}")
            else:
                print("No raw_data available to determine allowed attributes.")
            print(f"Current instance attributes: {', '.join(self.__dict__.keys())}")
            print(f"Value type provided: {type(value)}")
            
            # Limit preview for large data types
            value_repr = repr(value)
            if isinstance(value, (list, tuple, dict, set)) and len(value_repr) > 100:
                 value_repr = f"{value_repr[:100]}... (truncated)"
            elif hasattr(value, 'shape'): # Handle numpy arrays or similar
                 value_repr = f"Array-like object with shape {value.shape} and dtype {value.dtype} (preview truncated)"

            print(f"Value provided (preview): {value_repr}")
            print(f"--------------------")
            
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'. Cannot set this attribute.")
        
        # If the attribute is allowed or already exists, set it using the parent class's method
        try:
            super().__setattr__(name, value)
            print(f"\n--- Debug Info ---")
            print(f"Successfully set attribute '{name}' on {self.__class__.__name__}.")
            print(f"Value type: {type(value)}")
             # Limit preview for large data types
            value_repr = repr(value)
            if isinstance(value, (list, tuple, dict, set)) and len(value_repr) > 100:
                 value_repr = f"{value_repr[:100]}... (truncated)"
            elif hasattr(value, 'shape'): # Handle numpy arrays or similar
                 value_repr = f"Array-like object with shape {value.shape} and dtype {value.dtype} (preview truncated)"
            print(f"Value set (preview): {value_repr}")
            print(f"--------------------")
        except Exception as e:
            print(f"\n--- Debug Info ---")
            print(f"Error setting attribute '{name}' on {self.__class__.__name__}: {e}")
            print(f"Value type provided: {type(value)}")
             # Limit preview for large data types
            value_repr = repr(value)
            if isinstance(value, (list, tuple, dict, set)) and len(value_repr) > 100:
                 value_repr = f"{value_repr[:100]}... (truncated)"
            elif hasattr(value, 'shape'): # Handle numpy arrays or similar
                 value_repr = f"Array-like object with shape {value.shape} and dtype {value.dtype} (preview truncated)"
            print(f"Value provided (preview): {value_repr}")
            print(f"--------------------")
            raise # Re-raise the exception after logging

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
                color='darkred',           # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

mag_sc_4sa = mag_sc_4sa_class(None, None) # Initialize the class with no data
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
        object.__setattr__(self, 'source_filenames', [])

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

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        data_cubby.stash(self, class_name='mag_sc')
    
    def update(self, imported_data):
        """Method to update class with new data."""
        print_manager.debug(f"---> Entering update method for {self.__class__.__name__}") # DEBUG ENTRY
        # === START TEMPORARY DEBUGGING ===
        if imported_data is None:
            print_manager.debug(f"[UPDATE DEBUG] imported_data is None for {self.__class__.__name__}.")
        else:
            print_manager.debug(f"[UPDATE DEBUG] imported_data type: {type(imported_data)} for {self.__class__.__name__}")
            if hasattr(imported_data, 'source_filenames'):
                print_manager.debug(f"[UPDATE DEBUG] imported_data HAS source_filenames attr for {self.__class__.__name__}.")
                print_manager.debug(f"[UPDATE DEBUG] imported_data.source_filenames = {imported_data.source_filenames}")
            else:
                print_manager.debug(f"[UPDATE DEBUG] imported_data DOES NOT HAVE source_filenames attr for {self.__class__.__name__}.")
        # === END TEMPORARY DEBUGGING ===
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        # Store the source filenames associated with this data update
        if hasattr(imported_data, 'source_filenames'):
            self.source_filenames = imported_data.source_filenames
            print_manager.debug(f"Stored {len(self.source_filenames)} source filenames on {self.__class__.__name__} instance.")
        else:
            self.source_filenames = []
            print_manager.debug(f"No source_filenames found on data_object for {self.__class__.__name__}.")
        
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
        
        # NEW: Save after update if storage enabled
        if data_cubby.use_pkl_storage:
             data_cubby.save_to_disk(obj_to_save=self, identifier_to_save=self.all.plot_options.data_type)
    
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

    def __getattr__(self, name): # Prints a friendly error message if an attribute is not found
        # --- FIX: Simplify __getattr__ to correctly raise AttributeError ---
        # Remove the explicit check for __*__ methods here.
        # __getattr__ is only called if standard lookup fails.
        # if name.startswith('__') and name.endswith('__'):
        #     raise AttributeError(f"Special method {name} not handled by __getattr__")
            
        print_manager.debug(f'{self.__class__.__name__} getattr helper!') # Use class name
        print_manager.variable_testing(f"__getattr__ called for {self.__class__.__name__}.{name}")
        
        # Attempt to generate helpful message, but ensure AttributeError is raised
        try:
            available_attrs = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
            print(f"\n'{name}\' is not a recognized attribute for {self.__class__.__name__}, friend!")
            if available_attrs:
                print(f"Try one of these: {', '.join(available_attrs)}")
            else:
                print("(No raw_data available to suggest attributes)")
        except Exception as e:
            # Avoid errors within getattr itself from hiding the main issue
            print(f"Error generating suggestion in __getattr__: {e}")
            
        # CRITICAL: Always raise AttributeError as expected for __getattr__
        raise AttributeError(f"'{self.__class__.__name__}\' object has no attribute '{name}\'")
        # ------------------------------------------------------------------
    
    def __setattr__(self, name, value):
        """Handle attribute assignment with friendly error messages."""
        # Allow setting known attributes
        # Simplify debug print: try to show only first few elements/rows and limit total length
        try:
            # Check type name for plot_manager to avoid circular import if necessary
            is_plot_manager = type(value).__name__ == 'plot_manager'

            # Limit preview for lists/arrays AND plot_manager
            if is_plot_manager:
                # Concise representation for plot_manager
                pm_id = f" for {value.plot_options.data_type}.{value.plot_options.subclass_name}" if hasattr(value, 'plot_options') else ""
                preview = f"<plot_manager instance{pm_id}>"
            elif isinstance(value, (list, np.ndarray)):
                # Show first 2 elements only for other lists/arrays
                preview = repr(value[:2]) + ('...' if len(value) > 2 else '')
            elif callable(value):
                # Try to avoid printing the full callable representation
                preview = f"<callable {name}>"
            else:
                # Limit length of other representations too
                preview = repr(value)
                if len(preview) > 80:
                    preview = preview[:80] + '...'
            value_repr = preview # Use the generated preview

        except Exception as e:
            # Fallback to default representation if slicing fails or it's not applicable
            value_repr = repr(value)
            if len(value_repr) > 80: # Apply length limit even in fallback
                 value_repr = value_repr[:80] + '...'
            value_repr += f" (repr error: {e})"

        print_manager.debug(f"Setting attribute: {name} with value: {value_repr}")

        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'source_filenames'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('mag_sc setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attribute
    
    def calculate_variables(self, imported_data):
        """Calculate and store MAG SC variables"""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        print_manager.debug("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.debug("First element type: {type(self.datetime_array[0])}")
        
        # Get field data as numpy array
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_SC'])
        
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

mag_sc = mag_sc_class(None) #Initialize the class with no data
print('initialized mag_sc class')