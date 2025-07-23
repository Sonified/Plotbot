"""
Auto-generated plotbot class for PSP_wavePower_2021-04-29_v1.3.cdf
Generated on: 2025-07-23T12:36:55.178687
Source: /Users/robertalexander/GitHub/Plotbot/docs/implementation_plans/CDF_Integration/KP_wavefiles/PSP_wavePower_2021-04-29_v1.3.cdf

This class contains 2 variables from the CDF file.
"""

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from .._utils import _format_setattr_debug

class psp_waves_timeseries_class:
    """
    CDF data class for PSP_wavePower_2021-04-29_v1.3.cdf
    
    Variables:
    - wavePower_LH: EMIC Wave Power observed by PSP with Ellipticity below -0.8 (Left-handed), coherency above 0.8, and wave normal angle below 25 degrees.
    - wavePower_RH: EMIC Wave Power observed by PSP with Ellipticity above 0.8 (Right-handed), coherency above 0.8, and wave normal angle below 25 degrees.
    """
    
    def __init__(self, imported_data):
        # Initialize basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'psp_waves_timeseries')
        object.__setattr__(self, 'data_type', 'psp_waves_timeseries')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
        'wavePower_LH': None,
        'wavePower_RH': None
    })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', '/Users/robertalexander/GitHub/Plotbot/docs/implementation_plans/CDF_Integration/KP_wavefiles/PSP_wavePower_2021-04-29_v1.3.cdf')
        object.__setattr__(self, '_cdf_file_pattern', 'PSP_wavePower_2021-04-29_v1.3.cdf')

        if imported_data is None:
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management("Calculating psp_waves_timeseries variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated psp_waves_timeseries variables.")
        
        # Auto-register with data_cubby (following plotbot pattern)
        from plotbot.data_cubby import data_cubby
        data_cubby.stash(self, class_name='psp_waves_timeseries')
        print_manager.dependency_management("Registered psp_waves_timeseries with data_cubby")
    
    def update(self, imported_data, original_requested_trange=None):
        """Method to update class with new data."""
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update
        current_state = {}
        for subclass_name in self.raw_data.keys():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_ploptions()
        
        # Restore state
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
    def get_subclass(self, subclass_name):
        """Retrieve a specific component"""
        print_manager.dependency_management(f"Getting subclass: {subclass_name}")
        if subclass_name in self.raw_data.keys():
            print_manager.dependency_management(f"Returning {subclass_name} component")
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
        
        print_manager.dependency_management('psp_waves_timeseries getattr helper!')
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
        allowed_attrs = ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'variable_meshes', 'data_type']
        if name in allowed_attrs or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            print_manager.dependency_management('psp_waves_timeseries setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate and store CDF variables"""
        # Dynamically find time variable from any CDF data
        time_var = None
        for var_name in imported_data.data.keys():
            if any(keyword in var_name.lower() for keyword in ['epoch', 'time', 'fft_time']):
                time_var = var_name
                break
        
        # Store time data
        if time_var and time_var in imported_data.data:
            self.time = np.asarray(imported_data.data[time_var])
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"Using time variable: {time_var}")
        else:
            # Fallback to imported_data.times if available
            self.time = np.asarray(imported_data.times) if hasattr(imported_data, 'times') else np.array([])
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time)) if len(self.time) > 0 else np.array([])
            print_manager.dependency_management("Using fallback times from imported_data.times")
        
        print_manager.dependency_management(f"self.datetime_array type: {type(self.datetime_array)}")
        print_manager.dependency_management(f"Datetime range: {self.datetime_array[0] if len(self.datetime_array) > 0 else 'Empty'} to {self.datetime_array[-1] if len(self.datetime_array) > 0 else 'Empty'}")
        

        # Process wavePower_LH (EMIC Wave Power observed by PSP with Ellipticity below -0.8 (Left-handed), coherency above 0.8, and wave normal angle below 25 degrees.)
        wavePower_LH_data = imported_data.data['wavePower_LH']
        
        # Handle fill values for wavePower_LH
        fill_val = imported_data.data.get('wavePower_LH_FILLVAL', -1e+38)
        wavePower_LH_data = np.where(wavePower_LH_data == fill_val, np.nan, wavePower_LH_data)
        
        self.raw_data['wavePower_LH'] = wavePower_LH_data

        # Process wavePower_RH (EMIC Wave Power observed by PSP with Ellipticity above 0.8 (Right-handed), coherency above 0.8, and wave normal angle below 25 degrees.)
        wavePower_RH_data = imported_data.data['wavePower_RH']
        
        # Handle fill values for wavePower_RH
        fill_val = imported_data.data.get('wavePower_RH_FILLVAL', -1e+38)
        wavePower_RH_data = np.where(wavePower_RH_data == fill_val, np.nan, wavePower_RH_data)
        
        self.raw_data['wavePower_RH'] = wavePower_RH_data
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        # Keep frequency arrays as 1D - individual meshes handle the 2D time dimension
        # Each spectral variable gets its own mesh in variable_meshes dictionary

        print_manager.dependency_management(f"Processed {len([v for v in self.raw_data.values() if v is not None])} variables successfully")
    
    def _find_frequency_data(self):
        """Dynamically find frequency data that matches spectral variables."""
        # Look for frequency variables that actually have data
        for var_name, var_data in self.raw_data.items():
            if ('freq' in var_name.lower() and 
                var_data is not None and 
                hasattr(var_data, '__len__') and 
                len(var_data) > 1):
                
                # Create frequency array that matches time dimension for pcolormesh
                # plotbot expects additional_data to be indexable by time
                if hasattr(self, 'datetime_array') and self.datetime_array is not None:
                    n_times = len(self.datetime_array)
                    n_freqs = len(var_data)
                    # Create 2D frequency array: each row is the same frequency values
                    freq_2d = np.tile(var_data, (n_times, 1))
                    return freq_2d
                else:
                    return var_data
        
        # Fallback - create a simple frequency array if nothing found
        # Assume 100 frequency bins from 10 Hz to 1 kHz
        freq_array = np.logspace(1, 3, 100)
        if hasattr(self, 'datetime_array') and self.datetime_array is not None:
            n_times = len(self.datetime_array)
            freq_2d = np.tile(freq_array, (n_times, 1))
            return freq_2d
        return freq_array
    
    def set_ploptions(self):
        """Set up plotting options for all variables"""
        print_manager.dependency_management("Setting up plot options for psp_waves_timeseries variables")
        

        self.wavePower_LH = plot_manager(
            self.raw_data['wavePower_LH'],
            plot_options=ploptions(
                data_type='psp_waves_timeseries',
                var_name='wavePower_LH',
                class_name='psp_waves_timeseries',
                subclass_name='wavePower_LH',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='wavePower_LH (nt$^2$)',
                legend_label='EMIC Wave Power observed by PSP with Ellipticity below -0.8 (Left-handed), coherency above 0.8, and wave normal angle below 25 degrees.',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.wavePower_RH = plot_manager(
            self.raw_data['wavePower_RH'],
            plot_options=ploptions(
                data_type='psp_waves_timeseries',
                var_name='wavePower_RH',
                class_name='psp_waves_timeseries',
                subclass_name='wavePower_RH',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='wavePower_RH (nt$^2$)',
                legend_label='EMIC Wave Power observed by PSP with Ellipticity above 0.8 (Right-handed), coherency above 0.8, and wave normal angle below 25 degrees.',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

# Initialize the class with no data
psp_waves_timeseries = psp_waves_timeseries_class(None)
print_manager.dependency_management('initialized psp_waves_timeseries class')
