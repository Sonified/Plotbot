# wind_swe_h5_classes.py - Calculates and stores WIND SWE H5 electron temperature variables

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
import sys
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store WIND SWE H5 electron temperature variables 🎉
class wind_swe_h5_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'wind_swe_h5')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'wind_swe_h5')      # Key for data_types
        object.__setattr__(self, 'subclass_name', None)           # For the main class instance
        object.__setattr__(self, 'raw_data', {
            't_elec': None,      # Electron temperature from quadrature analysis
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)

        print_manager.dependency_management(f"*** WIND_SWE_H5_CLASS_INIT (wind_swe_h5_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating WIND SWE H5 variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated WIND SWE H5 variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[WIND_SWE_H5_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[WIND_SWE_H5_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['t_elec']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_ploption_snapshot(current_plot_states[comp_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_ploptions()
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for comp_name, state in current_plot_states.items():
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_options, attr):
                            setattr(manager.plot_options, attr, value)
                    print_manager.datacubby(f"Restored {comp_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
    def get_subclass(self, subclass_name):
        """
        Retrieves a specific data component (subclass) by its name.
        
        Args:
            subclass_name (str): The name of the component to retrieve.
            
        Returns:
            The requested component, or None if not found.
        """
        # Update requested_trange for all plot_manager components when accessed
        current_trange = TimeRangeTracker.get_current_trange()
        if current_trange:
            for attr_name in dir(self):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(self, attr_name)
                        if isinstance(attr_value, plot_manager):
                            attr_value.requested_trange = current_trange
                    except Exception:
                        pass
        print_manager.debug(f"Getting subclass: {subclass_name}")
        if subclass_name in self.raw_data:
            return getattr(self, subclass_name)
        else:
            print(f"'{subclass_name}' is not a recognized subclass, friend!")
            print(f"Try one of these: {', '.join(self.raw_data.keys())}")
            return None

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.dependency_management('wind_swe_h5 getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}")
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.dependency_management(_format_setattr_debug(name, value))
        if name in ['datetime', 'datetime_array', 'raw_data', 'time'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('wind_swe_h5 setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate WIND SWE H5 electron temperature variables from imported CDF data."""
        print_manager.processing("WIND SWE H5: Starting calculate_variables...")

        if imported_data is None or not hasattr(imported_data, 'data') or imported_data.data is None:
            print_manager.warning("WIND SWE H5: No data available for calculation")
            return

        data = imported_data.data
        print_manager.processing(f"WIND SWE H5: Processing data with keys: {list(data.keys())}")

        # Store only TT2000 times as numpy array (following PSP pattern)
        if hasattr(imported_data, 'times') and imported_data.times is not None:
            self.time = np.asarray(imported_data.times)
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"self.datetime_array type after conversion: {type(self.datetime_array)}")
            print_manager.dependency_management(f"First element type: {type(self.datetime_array[0])}")
            print_manager.processing(f"WIND SWE H5: Processed {len(self.datetime_array)} time points")
        else:
            print_manager.warning("WIND SWE H5: No times data found in imported_data")
            return

        # Extract electron temperature data
        if 'T_elec' in data:
            t_elec_data = data['T_elec']  # Electron temperature array

            print_manager.processing(f"WIND SWE H5: T_elec shape: {t_elec_data.shape}")
            print_manager.processing(f"WIND SWE H5: T_elec range: [{np.nanmin(t_elec_data):.2e}, {np.nanmax(t_elec_data):.2e}] K")
            
            # Debug: Check for any problematic values
            negative_count = np.sum(t_elec_data < 0)
            if negative_count > 0:
                print_manager.processing(f"WIND SWE H5: WARNING - Found {negative_count} negative temperature values!")
                print_manager.processing(f"WIND SWE H5: Negative values: {t_elec_data[t_elec_data < 0]}")
            
            # Check for fill values
            fill_val = -1e31
            fill_count = np.sum(np.abs(t_elec_data - fill_val) < 1e30)
            if fill_count > 0:
                print_manager.processing(f"WIND SWE H5: WARNING - Found {fill_count} fill values!")
                
            print_manager.processing(f"WIND SWE H5: First 10 T_elec values: {t_elec_data[:10]}")
            print_manager.processing(f"WIND SWE H5: Data type: {type(t_elec_data)}, dtype: {t_elec_data.dtype}")

            # Quality filtering: Currently disabled - preserving raw data including bad values
            # NOTE: Found negative temperature (-180,603 K) at 2022-06-02T00:49:09 - clearly unphysical
            # Valid temperature range from CDF metadata: 10,000 to 1,000,000 K  
            # TODO: Implement optional quality filtering in future
            # quality_mask = (t_elec_data >= 10000.0) & (t_elec_data <= 1000000.0)
            # bad_values_count = np.sum(~quality_mask)
            # if bad_values_count > 0:
            #     print_manager.processing(f"WIND SWE H5: Found {bad_values_count} values outside valid range - replacing with NaN")
            #     t_elec_data = np.where(quality_mask, t_elec_data, np.nan)

            # Store data in raw_data dictionary
            self.raw_data = {
                't_elec': t_elec_data,  # Electron temperature
            }

            print_manager.processing("WIND SWE H5: Successfully calculated electron temperature")

            print_manager.dependency_management(f"\nDebug - Data Arrays:")
            print_manager.dependency_management(f"Time array shape: {self.time.shape}")
            print_manager.dependency_management(f"T_elec data shape: {t_elec_data.shape}")
            print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")

        else:
            print_manager.warning("WIND SWE H5: Missing required electron temperature data (T_elec)")

    def set_ploptions(self):
        """Set up the plotting options for electron temperature"""
        # Electron temperature
        self.t_elec = plot_manager(
            self.raw_data['t_elec'],
            plot_options=ploptions(
                data_type='wind_swe_h5',
                var_name='t_elec',
                class_name='wind_swe_h5',
                subclass_name='t_elec',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Temperature (K)',
                legend_label='$T_e$ (electron)',
                color='orange',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    def ensure_internal_consistency(self):
        """Ensures .time and data are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** WIND_SWE_H5 ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        
        changed_time = False
        if hasattr(self, 'datetime_array') and self.datetime_array is not None:
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
            print_manager.dependency_management(f"    Calling self.set_ploptions() due to time consistency updates.")
            self.set_ploptions()
            
        print_manager.dependency_management(f"*** WIND_SWE_H5 ENSURE ID:{id(self)} *** Finished.")

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

# Initialize the class with no data
wind_swe_h5 = wind_swe_h5_class(None)  
print_manager.dependency_management('initialized wind_swe_h5 class') 