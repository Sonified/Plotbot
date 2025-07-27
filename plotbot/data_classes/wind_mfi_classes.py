# wind_mfi_classes.py - Calculates and stores WIND MFI magnetic field variables

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

# 🎉 Define the main class to calculate and store WIND MFI variables 🎉
class wind_mfi_h2_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'wind_mfi_h2')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'wind_mfi_h2')      # Key for data_types
        object.__setattr__(self, 'subclass_name', None)           # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'bx': None,      # X component (GSE)
            'by': None,      # Y component (GSE)  
            'bz': None,      # Z component (GSE)
            'bmag': None,    # |B| magnitude
            'bgse': None,    # Full vector [N,3]
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)

        print_manager.dependency_management(f"*** WIND_MFI_CLASS_INIT (wind_mfi_h2_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating WIND MFI variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated WIND MFI variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[WIND_MFI_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[WIND_MFI_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['all', 'bx', 'by', 'bz', 'bmag', 'bgse']
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
        print_manager.dependency_management('wind_mfi_h2 getattr helper!')
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
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('wind_mfi_h2 setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate WIND MFI magnetic field variables from imported CDF data."""
        print_manager.processing("WIND MFI: Starting calculate_variables...")

        if imported_data is None or not hasattr(imported_data, 'data') or imported_data.data is None:
            print_manager.warning("WIND MFI: No data available for calculation")
            return

        data = imported_data.data
        print_manager.processing(f"WIND MFI: Processing data with keys: {list(data.keys())}")

        # Store only TT2000 times as numpy array (following PSP pattern)
        if hasattr(imported_data, 'times') and imported_data.times is not None:
            self.time = np.asarray(imported_data.times)
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"self.datetime_array type after conversion: {type(self.datetime_array)}")
            print_manager.dependency_management(f"First element type: {type(self.datetime_array[0])}")
            print_manager.processing(f"WIND MFI: Processed {len(self.datetime_array)} time points")
        else:
            print_manager.warning("WIND MFI: No times data found in imported_data")
            return

        # Extract magnetic field data
        if 'BGSE' in data and 'BF1' in data:
            bgse_data = data['BGSE']  # [N, 3] array
            bf1_data = data['BF1']    # [N] magnitude array

            print_manager.processing(f"WIND MFI: BGSE shape: {bgse_data.shape}, BF1 shape: {bf1_data.shape}")

            # Get field data as numpy array (following PSP pattern)
            self.field = np.asarray(bgse_data)

            # Extract components
            bx = bgse_data[:, 0]  # X-component in GSE
            by = bgse_data[:, 1]  # Y-component in GSE
            bz = bgse_data[:, 2]  # Z-component in GSE
            bmag = bf1_data       # Magnitude from CDF

            # Store all data in raw_data dictionary
            self.raw_data = {
                'all': [bx, by, bz],
                'bx': bx,
                'by': by,
                'bz': bz,
                'bmag': bmag,
                'bgse': bgse_data,
            }

            print_manager.processing("WIND MFI: Successfully calculated magnetic field components")
            print_manager.processing(f"WIND MFI: Bx range: [{np.min(bx):.2f}, {np.max(bx):.2f}] nT")
            print_manager.processing(f"WIND MFI: By range: [{np.min(by):.2f}, {np.max(by):.2f}] nT")
            print_manager.processing(f"WIND MFI: Bz range: [{np.min(bz):.2f}, {np.max(bz):.2f}] nT")
            print_manager.processing(f"WIND MFI: |B| range: [{np.min(bmag):.2f}, {np.max(bmag):.2f}] nT")

            print_manager.dependency_management(f"\nDebug - Data Arrays:")
            print_manager.dependency_management(f"Time array shape: {self.time.shape}")
            print_manager.dependency_management(f"Field data shape: {self.field.shape}")
            print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")

        else:
            print_manager.warning("WIND MFI: Missing required magnetic field data (BGSE and/or BF1)")

    def set_ploptions(self):
        """Set up the plotting options for all magnetic field components"""
        # Initialize each component with plot_manager
        self.all = plot_manager(
            [self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name=['bx_gse', 'by_gse', 'bz_gse'],
                class_name='wind_mfi_h2',
                subclass_name='all',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label=['$B_X$ (GSE)', '$B_Y$ (GSE)', '$B_Z$ (GSE)'],
                color=['red', 'green', 'blue'],
                y_scale='linear',
                y_limit=None,
                line_width=[1, 1, 1],
                line_style=['-', '-', '-']
            )
        )

        self.bx = plot_manager(
            self.raw_data['bx'],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name='bx_gse',
                class_name='wind_mfi_h2',
                subclass_name='bx',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label='$B_X$ (GSE)',
                color='red',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.by = plot_manager(
            self.raw_data['by'],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name='by_gse',
                class_name='wind_mfi_h2',
                subclass_name='by',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label='$B_Y$ (GSE)',
                color='green',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.bz = plot_manager(
            self.raw_data['bz'],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name='bz_gse',
                class_name='wind_mfi_h2',
                subclass_name='bz',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label='$B_Z$ (GSE)',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name='bmag_gse',
                class_name='wind_mfi_h2',
                subclass_name='bmag',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label='$|B|$',
                color='black',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.bgse = plot_manager(
            self.raw_data['bgse'],
            plot_options=ploptions(
                data_type='wind_mfi_h2',
                var_name='bgse_vector',
                class_name='wind_mfi_h2',
                subclass_name='bgse',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='B (nT)',
                legend_label='B GSE Vector',
                color='purple',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** WIND ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
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
            if ('bx' in self.raw_data and self.raw_data['bx'] is not None and
                'by' in self.raw_data and self.raw_data['by'] is not None and
                'bz' in self.raw_data and self.raw_data['bz'] is not None and
                len(self.raw_data['bx']) == expected_len and
                len(self.raw_data['by']) == expected_len and
                len(self.raw_data['bz']) == expected_len):
                new_field = np.column_stack((self.raw_data['bx'], self.raw_data['by'], self.raw_data['bz']))
                if not hasattr(self, 'field') or self.field is None or not np.array_equal(self.field, new_field):
                    self.field = new_field
                    print_manager.dependency_management(f"    Updated self.field from GSE components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print_manager.dependency_management(f"    Nullifying self.field. Reason: GSE components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print_manager.dependency_management(f"    Setting self.field to None. Reason: GSE components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
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
            print_manager.dependency_management(f"*** WIND ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print_manager.dependency_management(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print_manager.dependency_management(f"    POST-FIX - time len: {final_time_len}")
            print_manager.dependency_management(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print_manager.dependency_management(f"*** WIND ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print_manager.dependency_management(f"*** WIND ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

wind_mfi_h2 = wind_mfi_h2_class(None)  # Initialize the class with no data
print_manager.dependency_management('initialized wind_mfi_h2 class') 