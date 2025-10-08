"""
Auto-generated plotbot class for PSP_wavePower_2021-04-29_v1.3.cdf
Generated on: 2025-09-25T19:25:57.676752
Source: data/cdf_files/PSP_Waves/PSP_wavePower_2021-04-29_v1.3.cdf

This class contains 2 variables from the CDF file.
"""

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config, retrieve_plot_config_snapshot
from plotbot.time_utils import TimeRangeTracker
from .._utils import _format_setattr_debug

class psp_waves_test_class:
    """
    CDF data class for PSP_wavePower_2021-04-29_v1.3.cdf
    
    Variables:
    - wavePower_LH: EMIC Wave Power observed by PSP with Ellipticity below -0.8 (Left-handed), coherency above 0.8, and wave normal angle below 25 degrees.
    - wavePower_RH: EMIC Wave Power observed by PSP with Ellipticity above 0.8 (Right-handed), coherency above 0.8, and wave normal angle below 25 degrees.
    """
    
    def __init__(self, imported_data):
        # Initialize basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'psp_waves_test')
        object.__setattr__(self, 'data_type', 'psp_waves_test')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
        'wavePower_LH': None,
        'wavePower_RH': None
    })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'time', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', 'data/cdf_files/PSP_Waves/PSP_wavePower_2021-04-29_v1.3.cdf')
        object.__setattr__(self, '_cdf_file_pattern', 'PSP_wavePower_*_v*.cdf')

        if imported_data is None:
            self.set_plot_config()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management(f"Calculating psp_waves_test variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status(f"Successfully calculated psp_waves_test variables.")
        
        # NOTE: Registration with data_cubby is handled externally to avoid 
        # instance conflicts during merge operations (like mag_rtn classes)
    
    def update(self, imported_data, original_requested_trange=None):
        """Method to update class with new data."""
        # STYLE_PRESERVATION: Entry point
        print_manager.style_preservation(f"🔄 UPDATE_ENTRY for {self.__class__.__name__} (ID: {id(self)}) - operation_type: UPDATE")
        
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # STYLE_PRESERVATION: Before state preservation
        if hasattr(self, '__dict__'):
            from plotbot.plot_manager import plot_manager
            plot_managers = {k: v for k, v in self.__dict__.items() if isinstance(v, plot_manager)}
            print_manager.style_preservation(f"   📊 Existing plot_managers before preservation: {list(plot_managers.keys())}")
            for pm_name, pm_obj in plot_managers.items():
                if hasattr(pm_obj, '_plot_state'):
                    color = getattr(pm_obj._plot_state, 'color', 'Not Set')
                    legend_label = getattr(pm_obj._plot_state, 'legend_label', 'Not Set')
                    print_manager.style_preservation(f"   🎨 {pm_name}: color='{color}', legend_label='{legend_label}'")
                else:
                    print_manager.style_preservation(f"   ❌ {pm_name}: No _plot_state found")
        
        # Store current state before update (including any modified plot_config)
        current_plot_states = {}
        standard_components = ['wavePower_LH', 'wavePower_RH']
        
        # STYLE_PRESERVATION: During state save
        print_manager.style_preservation(f"💾 STATE_SAVE for {self.__class__.__name__} - capturing states for subclasses: {standard_components}")
        
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_plot_config_snapshot(current_plot_states[comp_name])}")
                    print_manager.style_preservation(f"   💾 Saved {comp_name}: color='{current_plot_states[comp_name].get('color', 'Not Set')}', legend_label='{current_plot_states[comp_name].get('legend_label', 'Not Set')}'")

        # Perform update
        # STYLE_PRESERVATION: After calculate_variables(), before set_plot_config()
        print_manager.style_preservation(f"🔄 PRE_SET_PLOT_CONFIG in {self.__class__.__name__} - about to recreate plot_managers")
        
        self.calculate_variables(imported_data)                                # Update raw data arrays
        print_manager.style_preservation(f"✅ RAW_DATA_UPDATED for {self.__class__.__name__} - calculate_variables() completed")
        
        self.set_plot_config()                                                  # Recreate plot managers for standard components
        print_manager.style_preservation(f"✅ PLOT_MANAGERS_RECREATED for {self.__class__.__name__} - set_plot_config() completed")
        
        # Ensure internal consistency after update (mirror mag_rtn pattern)
        self.ensure_internal_consistency()
        
        # Restore state (including any modified plot_config!)
        print_manager.datacubby("Restoring saved state...")
        
        # STYLE_PRESERVATION: During state restore
        print_manager.style_preservation(f"🔧 STATE_RESTORE for {self.__class__.__name__} - applying saved states to recreated plot_managers")
        
        for comp_name, state in current_plot_states.items():                    # Restore saved states
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_config, attr):
                            setattr(manager.plot_config, attr, value)
                    print_manager.datacubby(f"Restored {comp_name} state: {retrieve_plot_config_snapshot(state)}")
                    print_manager.style_preservation(f"   🔧 Restored {comp_name}: color='{state.get('color', 'Not Set')}', legend_label='{state.get('legend_label', 'Not Set')}'")
        
        # STYLE_PRESERVATION: Exit point - Final custom values confirmation
        print_manager.style_preservation(f"✅ UPDATE_EXIT for {self.__class__.__name__} - Final state verification:")
        if hasattr(self, '__dict__'):
            from plotbot.plot_manager import plot_manager
            final_plot_managers = {k: v for k, v in self.__dict__.items() if isinstance(v, plot_manager)}
            for pm_name, pm_obj in final_plot_managers.items():
                if hasattr(pm_obj, '_plot_state'):
                    color = getattr(pm_obj._plot_state, 'color', 'Not Set')
                    legend_label = getattr(pm_obj._plot_state, 'legend_label', 'Not Set')
                    print_manager.style_preservation(f"   🎨 FINAL {pm_name}: color='{color}', legend_label='{legend_label}'")
                    if color == 'Not Set' or legend_label == 'Not Set':
                        print_manager.style_preservation(f"   ⚠️  FINAL_STYLE_LOSS detected in {pm_name}!")
                else:
                    print_manager.style_preservation(f"   ❌ FINAL {pm_name}: No _plot_state found")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
    def get_subclass(self, subclass_name):
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[PSP_WAVES_TEST_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
        
        print_manager.dependency_management(f'psp_waves_test getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
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
            print_manager.dependency_management(f'psp_waves_test setattr helper!')
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
    
    def set_plot_config(self):
        """Set up plotting options for all variables"""
        dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else "None_or_NoAttr"
        print_manager.dependency_management(f"[CDF_CLASS_DEBUG] set_plot_config called for instance ID: {id(self)}. self.datetime_array len: {dt_len}")
        print_manager.dependency_management("Setting up plot options for psp_waves_test variables")
        
        self.wavePower_LH = plot_manager(
            self.raw_data['wavePower_LH'],
            plot_config=plot_config(
                data_type='psp_waves_test',
                var_name='wavePower_LH',
                class_name='psp_waves_test',
                subclass_name='wavePower_LH',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='psp_waves_test',
                var_name='wavePower_RH',
                class_name='psp_waves_test',
                subclass_name='wavePower_RH',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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

    def ensure_internal_consistency(self):
        """Ensures .time and core data attributes are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        
        # Track what changed to avoid unnecessary operations
        changed_time = False
        changed_config = False
        
        # STEP 1: Reconstruct self.time from datetime_array (critical after merges)
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
        
        # STEP 2: Sync plot manager datetime references (existing logic)
        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:
            
            for var_name in self.raw_data.keys():
                if hasattr(self, var_name):
                    var_manager = getattr(self, var_name)
                    if hasattr(var_manager, 'plot_config') and hasattr(var_manager.plot_config, 'datetime_array'):
                        if var_manager.plot_config.datetime_array is None or \
                           (hasattr(var_manager.plot_config.datetime_array, '__len__') and 
                            len(var_manager.plot_config.datetime_array) != len(self.datetime_array)):
                            var_manager.plot_config.datetime_array = self.datetime_array
                            print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Updated {var_name} plot_config.datetime_array")
                            changed_config = True
        
        # STEP 3: Only call set_plot_config if data structures actually changed
        if changed_time and hasattr(self, 'set_plot_config'):
            print_manager.dependency_management(f"    Calling self.set_plot_config() due to time reconstruction.")
            self.set_plot_config()
        
        # Log final state
        if changed_time or changed_config:
            print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{id(self)} *** CHANGES WERE MADE (time: {changed_time}, config: {changed_config}).")
        else:
            print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{id(self)} *** NO CHANGES MADE.")
        
        print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{id(self)} *** Finished.")

    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

# Initialize the class with no data
psp_waves_test = psp_waves_test_class(None)
print_manager.dependency_management(f'initialized psp_waves_test class')
