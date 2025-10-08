# plotbot/data_classes/psp_mag_rtn.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config, retrieve_plot_config_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

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
            'pmag': None,
            'br_norm': None  # Add br_norm for lazy loading
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'time', None)
        object.__setattr__(self, '_current_operation_trange', None) # For br_norm dependency time range

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_plot_config()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating mag rtn variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status("Successfully calculated mag rtn variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[MAG_RTN_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[MAG_RTN_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified plot_config)
        current_plot_states = {}
        standard_components = ['all', 'br', 'bt', 'bn', 'bmag', 'pmag']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_plot_config_snapshot(current_plot_states[comp_name])}")

        # Special handling for br_norm: save state only if it's been fully initialized
        if hasattr(self, '_br_norm_manager') and \
           isinstance(self._br_norm_manager, plot_manager) and \
           self.raw_data.get('br_norm') is not None and \
           hasattr(self._br_norm_manager, '_plot_state'):
            current_plot_states['br_norm'] = dict(self._br_norm_manager._plot_state)
            print_manager.datacubby(f"Stored br_norm (from _br_norm_manager) state: {retrieve_plot_config_snapshot(current_plot_states['br_norm'])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_plot_config()                                                  # Recreate plot managers for standard components
        
        # Restore state (including any modified plot_config!)
        print_manager.datacubby("Restoring saved state...")
        for comp_name, state in current_plot_states.items():                    # Restore saved states
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
            
            if target_manager:
                target_manager._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(target_manager.plot_config, attr):
                        setattr(target_manager.plot_config, attr, value)
                print_manager.datacubby(f"Restored {comp_name} state to {'_br_norm_manager' if comp_name == 'br_norm' else comp_name}: {retrieve_plot_config_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[MAG_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

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
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.dependency_management('mag_rtn getattr helper!')
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
            print_manager.dependency_management('mag_rtn setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate the magnetic field components and derived quantities."""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        print_manager.dependency_management("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.dependency_management("First element type: {type(self.datetime_array[0])}")
        
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
            'pmag': pmag,
            'br_norm': None  # br_norm is calculated only when requested (lazy loading)
        }

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        print_manager.dependency_management(f"Field data shape: {self.field.shape}")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")
    
    def set_plot_config(self):
        """Set up the plotting options for all magnetic field components"""
        # Initialize each component with plot_manager
        self.all = plot_manager(
            [self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']],
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name=['br_rtn', 'bt_rtn', 'bn_rtn'],  # Variable names
                class_name='mag_rtn',      # Class handling this data
                subclass_name='all',       # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name='br_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='br',        # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name='bt_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bt',        # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name='bn_rtn',         # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bn',        # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name='bmag_rtn',       # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='bmag',      # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='mag_RTN',       # Actual data product name
                var_name='pmag_rtn',       # Variable name
                class_name='mag_rtn',      # Class handling this data
                subclass_name='pmag',      # Specific component
                plot_type='time_series',   # Type of plot
                time=self.time if hasattr(self, 'time') else None,

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
            
            if (changed_time or changed_field) and hasattr(self, 'set_plot_config'):
                print_manager.dependency_management(f"    Calling self.set_plot_config() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_plot_config()
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

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

    @property
    def br_norm(self):
        """Property for br_norm component that handles lazy loading."""
        print_manager.dependency_management(f"[BR_NORM_PROPERTY ENTRY (mag_rtn)] Accessing br_norm for instance ID: {id(self)}")
        dt_array_status = "exists and is populated" if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0 else "MISSING or EMPTY"
        print_manager.dependency_management(f"[BR_NORM_PROPERTY ENTRY (mag_rtn)] Parent self.datetime_array status: {dt_array_status}")

        if not hasattr(self, '_br_norm_manager'):
            print_manager.dependency_management("[BR_NORM_PROPERTY (mag_rtn)] Creating initial placeholder manager")
            self._br_norm_manager = plot_manager(
                np.array([]),
                plot_config=plot_config(
                    data_type='mag_RTN',      # Adjusted for mag_rtn
                    var_name='br_norm_rtn',   # Adjusted for mag_rtn
                    class_name='mag_rtn',     # Adjusted for mag_rtn
                    subclass_name='br_norm',
                    plot_type='time_series',
                    time=self.time if hasattr(self, 'time') else None,

                    datetime_array=self.datetime_array if hasattr(self, 'datetime_array') else np.array([]),
                    y_label='Br·R² [nT·AU²]',
                    legend_label=r'$B_R \cdot R^2$', # Escaped backslash
                    color='darkorange',
                    y_scale='linear',
                    line_width=1,
                    line_style='-'
                )
            )

        if hasattr(self, 'raw_data') and self.raw_data.get('br') is not None and len(self.raw_data['br']) > 0:
            print_manager.dependency_management("[BR_NORM_PROPERTY (mag_rtn)] Parent raw_data['br'] exists. Attempting calculation.")
            success = self._calculate_br_norm()
            if success and self.raw_data.get('br_norm') is not None:
                print_manager.dependency_management("[BR_NORM_PROPERTY (mag_rtn)] _calculate_br_norm successful, updating _br_norm_manager.")
                options = self._br_norm_manager.plot_config
                
                if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                    options.datetime_array = self.datetime_array
                elif options.datetime_array is None:
                    options.datetime_array = np.array([])
                else:
                    options.datetime_array = options.datetime_array if options.datetime_array is not None else np.array([])

                self._br_norm_manager = plot_manager(
                    self.raw_data['br_norm'],
                    plot_config=options 
                )
                print_manager.dependency_management(f"[BR_NORM_PROPERTY (mag_rtn)] Updated _br_norm_manager with data shape: {self.raw_data['br_norm'].shape if self.raw_data['br_norm'] is not None else 'None'}")
        else:
            print_manager.dependency_management("[BR_NORM_PROPERTY (mag_rtn)] Parent raw_data['br'] MISSING or EMPTY. Not attempting _calculate_br_norm.")
        
        print_manager.dependency_management(f"[BR_NORM_PROPERTY EXIT (mag_rtn)] Returning _br_norm_manager (ID: {id(self._br_norm_manager)})")
        return self._br_norm_manager
    
    def _calculate_br_norm(self):
        """Calculate Br normalized by R^2."""
        from plotbot.get_data import get_data # Local import
        from plotbot import proton # Local import for proton data
        import matplotlib.dates as mdates # Moved here
        import scipy.interpolate as interpolate # Moved here

        print_manager.dependency_management(f"[BR_NORM_CALC ENTRY (mag_rtn)] _calculate_br_norm called for instance ID: {id(self)}")

        trange_for_dependencies = None
        if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:
            trange_for_dependencies = self._current_operation_trange
            print_manager.dependency_management(f"[BR_NORM_CALC (mag_rtn)] Using specific _current_operation_trange for dependencies: {trange_for_dependencies}")
        else:
            print_manager.error("[BR_NORM_CALC (mag_rtn)] Cannot determine time range for dependencies: _current_operation_trange is None or not set.")
            print_manager.warning("[BR_NORM_CALC (mag_rtn)] The br_norm calculation now STRICTLY requires _current_operation_trange. Fallback to self.datetime_array has been removed.")
            self.raw_data['br_norm'] = None
            return False

        print_manager.dependency_management(f"[BR_NORM_CALC (mag_rtn)] Calling get_data for proton.sun_dist_rsun with trange: {trange_for_dependencies}")
        get_data(trange_for_dependencies, proton.sun_dist_rsun)
        
        if not hasattr(proton, 'sun_dist_rsun') or not hasattr(proton.sun_dist_rsun, 'data') or \
           proton.sun_dist_rsun.data is None or len(proton.sun_dist_rsun.data) == 0:
            print_manager.error(f"[BR_NORM_CALC ERROR (mag_rtn)] proton.sun_dist_rsun.data is None or empty after get_data for trange {trange_for_dependencies}.")
            self.raw_data['br_norm'] = None
            return False
        
        br_data = self.raw_data['br']
        mag_datetime = self.datetime_array
        proton_datetime = proton.datetime_array
        sun_dist_rsun = np.array(proton.sun_dist_rsun)  # Use raw array, not .data property
        
        if mag_datetime is None or len(mag_datetime) == 0 or \
           proton_datetime is None or len(proton_datetime) == 0 or \
           sun_dist_rsun is None or len(sun_dist_rsun) == 0 or \
           br_data is None or len(br_data) == 0:
            print_manager.error("[BR_NORM_CALC (mag_rtn)] One or more required data arrays (mag_datetime, proton_datetime, sun_dist_rsun, br_data) are None or empty.")
            self.raw_data['br_norm'] = None
            return False

        proton_time_numeric = mdates.date2num(proton_datetime)
        mag_time_numeric = mdates.date2num(mag_datetime)
        
        interp_func = interpolate.interp1d(
            proton_time_numeric, 
            sun_dist_rsun,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        sun_dist_interp = interp_func(mag_time_numeric)
        
        rsun_to_au_conversion_factor = 215.032867644
        br_norm_calculated = br_data * ((sun_dist_interp / rsun_to_au_conversion_factor) ** 2)
        
        self.raw_data['br_norm'] = br_norm_calculated
        print_manager.dependency_management(f"[BR_NORM_CALC (mag_rtn)] Successfully calculated br_norm (shape: {br_norm_calculated.shape})")
        return True

mag_rtn = mag_rtn_class(None) #Initialize the class with no data
print_manager.dependency_management('initialized mag_rtn class') 