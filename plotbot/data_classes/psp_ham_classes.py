"""
Auto-generated plotbot class for hamstring_2021-04-29_v02.cdf
Generated on: 2025-12-02T15:55:23.519138
Source: data/cdf_files/Hamstrings/hamstring_2021-04-29_v02.cdf

This class contains 25 variables from the CDF file.
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
from ._utils import _format_setattr_debug

class ham_class:
    """
    CDF data class for hamstring_2021-04-29_v02.cdf
    
    Variables:
    - n_core: Density of core proton population
    - n_neck: Density of neck proton population
    - n_ham: Density of hammerhead proton population
    - vx_inst_core: X-component velocity of core proton population in instrument coordinates
    - vy_inst_core: Y-component velocity of core proton population in instrument coordinates
    - vz_inst_core: Z-component velocity of core proton population in instrument coordinates
    - vx_inst_neck: X-component velocity of neck proton population in instrument coordinates
    - vy_inst_neck: Y-component velocity of neck proton population in instrument coordinates
    - vz_inst_neck: Z-component velocity of neck proton population in instrument coordinates
    - vx_inst_ham: X-component velocity of hammerhead proton population in instrument coordinates
    - vy_inst_ham: Y-component velocity of hammerhead proton population in instrument coordinates
    - vz_inst_ham: Z-component velocity of hammerhead proton population in instrument coordinates
    - temp_core: Temperature of core proton population
    - temp_neck: Temperature of neck proton population
    - temp_ham: Temperature of hammerhead proton population
    - Tperp_core: Temperature perpendicular to magnetic field of core proton population
    - Tpar_core: Temperature parallel to magnetic field of core proton population
    - Tperp_neck: Temperature perpendicular to magnetic field of neck proton population
    - Tpar_neck: Temperature parallel to magnetic field of neck proton population
    - Tperp_ham: Temperature perpendicular to magnetic field of hammerhead proton population
    - Tpar_ham: Temperature parallel to magnetic field of hammerhead proton population
    - Bx_inst: X-component of magnetic field in instrument coordinates
    - By_inst: Y-component of magnetic field in instrument coordinates
    - Bz_inst: Z-component of magnetic field in instrument coordinates
    - sun_dist_rsun: Distance from Sun in solar radii
    """
    
    def __init__(self, imported_data):
        # Initialize basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'ham')
        object.__setattr__(self, 'data_type', 'ham')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
        'n_core': None,
        'n_neck': None,
        'n_ham': None,
        'vx_inst_core': None,
        'vy_inst_core': None,
        'vz_inst_core': None,
        'vx_inst_neck': None,
        'vy_inst_neck': None,
        'vz_inst_neck': None,
        'vx_inst_ham': None,
        'vy_inst_ham': None,
        'vz_inst_ham': None,
        'temp_core': None,
        'temp_neck': None,
        'temp_ham': None,
        'Tperp_core': None,
        'Tpar_core': None,
        'Tperp_neck': None,
        'Tpar_neck': None,
        'Tperp_ham': None,
        'Tpar_ham': None,
        'Bx_inst': None,
        'By_inst': None,
        'Bz_inst': None,
        'sun_dist_rsun': None
    })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'time', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', 'data/cdf_files/Hamstrings/hamstring_2021-04-29_v02.cdf')
        object.__setattr__(self, '_cdf_file_pattern', 'hamstring_*_v*.cdf')

        if imported_data is None:
            self.set_plot_config()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management(f"Calculating ham variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status(f"Successfully calculated ham variables.")
        
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
        standard_components = ['n_core', 'n_neck', 'n_ham', 'vx_inst_core', 'vy_inst_core', 'vz_inst_core', 'vx_inst_neck', 'vy_inst_neck', 'vz_inst_neck', 'vx_inst_ham', 'vy_inst_ham', 'vz_inst_ham', 'temp_core', 'temp_neck', 'temp_ham', 'Tperp_core', 'Tpar_core', 'Tperp_neck', 'Tpar_neck', 'Tperp_ham', 'Tpar_ham', 'Bx_inst', 'By_inst', 'Bz_inst', 'sun_dist_rsun']
        
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
        print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[HAM_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[HAM_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
        
        print_manager.dependency_management(f'ham getattr helper!')
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
            print_manager.dependency_management(f'ham setattr helper!')
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
        

        # Process n_core (Density of core proton population)
        n_core_data = imported_data.data['n_core']
        
        # Handle fill values for n_core
        fill_val = imported_data.data.get('n_core_FILLVAL', -1e+38)
        n_core_data = np.where(n_core_data == fill_val, np.nan, n_core_data)
        
        self.raw_data['n_core'] = n_core_data

        # Process n_neck (Density of neck proton population)
        n_neck_data = imported_data.data['n_neck']
        
        # Handle fill values for n_neck
        fill_val = imported_data.data.get('n_neck_FILLVAL', -1e+38)
        n_neck_data = np.where(n_neck_data == fill_val, np.nan, n_neck_data)
        
        self.raw_data['n_neck'] = n_neck_data

        # Process n_ham (Density of hammerhead proton population)
        n_ham_data = imported_data.data['n_ham']
        
        # Handle fill values for n_ham
        fill_val = imported_data.data.get('n_ham_FILLVAL', -1e+38)
        n_ham_data = np.where(n_ham_data == fill_val, np.nan, n_ham_data)
        
        self.raw_data['n_ham'] = n_ham_data

        # Process vx_inst_core (X-component velocity of core proton population in instrument coordinates)
        vx_inst_core_data = imported_data.data['vx_inst_core']
        
        # Handle fill values for vx_inst_core
        fill_val = imported_data.data.get('vx_inst_core_FILLVAL', -1e+38)
        vx_inst_core_data = np.where(vx_inst_core_data == fill_val, np.nan, vx_inst_core_data)
        
        self.raw_data['vx_inst_core'] = vx_inst_core_data

        # Process vy_inst_core (Y-component velocity of core proton population in instrument coordinates)
        vy_inst_core_data = imported_data.data['vy_inst_core']
        
        # Handle fill values for vy_inst_core
        fill_val = imported_data.data.get('vy_inst_core_FILLVAL', -1e+38)
        vy_inst_core_data = np.where(vy_inst_core_data == fill_val, np.nan, vy_inst_core_data)
        
        self.raw_data['vy_inst_core'] = vy_inst_core_data

        # Process vz_inst_core (Z-component velocity of core proton population in instrument coordinates)
        vz_inst_core_data = imported_data.data['vz_inst_core']
        
        # Handle fill values for vz_inst_core
        fill_val = imported_data.data.get('vz_inst_core_FILLVAL', -1e+38)
        vz_inst_core_data = np.where(vz_inst_core_data == fill_val, np.nan, vz_inst_core_data)
        
        self.raw_data['vz_inst_core'] = vz_inst_core_data

        # Process vx_inst_neck (X-component velocity of neck proton population in instrument coordinates)
        vx_inst_neck_data = imported_data.data['vx_inst_neck']
        
        # Handle fill values for vx_inst_neck
        fill_val = imported_data.data.get('vx_inst_neck_FILLVAL', -1e+38)
        vx_inst_neck_data = np.where(vx_inst_neck_data == fill_val, np.nan, vx_inst_neck_data)
        
        self.raw_data['vx_inst_neck'] = vx_inst_neck_data

        # Process vy_inst_neck (Y-component velocity of neck proton population in instrument coordinates)
        vy_inst_neck_data = imported_data.data['vy_inst_neck']
        
        # Handle fill values for vy_inst_neck
        fill_val = imported_data.data.get('vy_inst_neck_FILLVAL', -1e+38)
        vy_inst_neck_data = np.where(vy_inst_neck_data == fill_val, np.nan, vy_inst_neck_data)
        
        self.raw_data['vy_inst_neck'] = vy_inst_neck_data

        # Process vz_inst_neck (Z-component velocity of neck proton population in instrument coordinates)
        vz_inst_neck_data = imported_data.data['vz_inst_neck']
        
        # Handle fill values for vz_inst_neck
        fill_val = imported_data.data.get('vz_inst_neck_FILLVAL', -1e+38)
        vz_inst_neck_data = np.where(vz_inst_neck_data == fill_val, np.nan, vz_inst_neck_data)
        
        self.raw_data['vz_inst_neck'] = vz_inst_neck_data

        # Process vx_inst_ham (X-component velocity of hammerhead proton population in instrument coordinates)
        vx_inst_ham_data = imported_data.data['vx_inst_ham']
        
        # Handle fill values for vx_inst_ham
        fill_val = imported_data.data.get('vx_inst_ham_FILLVAL', -1e+38)
        vx_inst_ham_data = np.where(vx_inst_ham_data == fill_val, np.nan, vx_inst_ham_data)
        
        self.raw_data['vx_inst_ham'] = vx_inst_ham_data

        # Process vy_inst_ham (Y-component velocity of hammerhead proton population in instrument coordinates)
        vy_inst_ham_data = imported_data.data['vy_inst_ham']
        
        # Handle fill values for vy_inst_ham
        fill_val = imported_data.data.get('vy_inst_ham_FILLVAL', -1e+38)
        vy_inst_ham_data = np.where(vy_inst_ham_data == fill_val, np.nan, vy_inst_ham_data)
        
        self.raw_data['vy_inst_ham'] = vy_inst_ham_data

        # Process vz_inst_ham (Z-component velocity of hammerhead proton population in instrument coordinates)
        vz_inst_ham_data = imported_data.data['vz_inst_ham']
        
        # Handle fill values for vz_inst_ham
        fill_val = imported_data.data.get('vz_inst_ham_FILLVAL', -1e+38)
        vz_inst_ham_data = np.where(vz_inst_ham_data == fill_val, np.nan, vz_inst_ham_data)
        
        self.raw_data['vz_inst_ham'] = vz_inst_ham_data

        # Process temp_core (Temperature of core proton population)
        temp_core_data = imported_data.data['temp_core']
        
        # Handle fill values for temp_core
        fill_val = imported_data.data.get('temp_core_FILLVAL', -1e+38)
        temp_core_data = np.where(temp_core_data == fill_val, np.nan, temp_core_data)
        
        self.raw_data['temp_core'] = temp_core_data

        # Process temp_neck (Temperature of neck proton population)
        temp_neck_data = imported_data.data['temp_neck']
        
        # Handle fill values for temp_neck
        fill_val = imported_data.data.get('temp_neck_FILLVAL', -1e+38)
        temp_neck_data = np.where(temp_neck_data == fill_val, np.nan, temp_neck_data)
        
        self.raw_data['temp_neck'] = temp_neck_data

        # Process temp_ham (Temperature of hammerhead proton population)
        temp_ham_data = imported_data.data['temp_ham']
        
        # Handle fill values for temp_ham
        fill_val = imported_data.data.get('temp_ham_FILLVAL', -1e+38)
        temp_ham_data = np.where(temp_ham_data == fill_val, np.nan, temp_ham_data)
        
        self.raw_data['temp_ham'] = temp_ham_data

        # Process Tperp_core (Temperature perpendicular to magnetic field of core proton population)
        Tperp_core_data = imported_data.data['Tperp_core']
        
        # Handle fill values for Tperp_core
        fill_val = imported_data.data.get('Tperp_core_FILLVAL', -1e+38)
        Tperp_core_data = np.where(Tperp_core_data == fill_val, np.nan, Tperp_core_data)
        
        self.raw_data['Tperp_core'] = Tperp_core_data

        # Process Tpar_core (Temperature parallel to magnetic field of core proton population)
        Tpar_core_data = imported_data.data['Tpar_core']
        
        # Handle fill values for Tpar_core
        fill_val = imported_data.data.get('Tpar_core_FILLVAL', -1e+38)
        Tpar_core_data = np.where(Tpar_core_data == fill_val, np.nan, Tpar_core_data)
        
        self.raw_data['Tpar_core'] = Tpar_core_data

        # Process Tperp_neck (Temperature perpendicular to magnetic field of neck proton population)
        Tperp_neck_data = imported_data.data['Tperp_neck']
        
        # Handle fill values for Tperp_neck
        fill_val = imported_data.data.get('Tperp_neck_FILLVAL', -1e+38)
        Tperp_neck_data = np.where(Tperp_neck_data == fill_val, np.nan, Tperp_neck_data)
        
        self.raw_data['Tperp_neck'] = Tperp_neck_data

        # Process Tpar_neck (Temperature parallel to magnetic field of neck proton population)
        Tpar_neck_data = imported_data.data['Tpar_neck']
        
        # Handle fill values for Tpar_neck
        fill_val = imported_data.data.get('Tpar_neck_FILLVAL', -1e+38)
        Tpar_neck_data = np.where(Tpar_neck_data == fill_val, np.nan, Tpar_neck_data)
        
        self.raw_data['Tpar_neck'] = Tpar_neck_data

        # Process Tperp_ham (Temperature perpendicular to magnetic field of hammerhead proton population)
        Tperp_ham_data = imported_data.data['Tperp_ham']
        
        # Handle fill values for Tperp_ham
        fill_val = imported_data.data.get('Tperp_ham_FILLVAL', -1e+38)
        Tperp_ham_data = np.where(Tperp_ham_data == fill_val, np.nan, Tperp_ham_data)
        
        self.raw_data['Tperp_ham'] = Tperp_ham_data

        # Process Tpar_ham (Temperature parallel to magnetic field of hammerhead proton population)
        Tpar_ham_data = imported_data.data['Tpar_ham']
        
        # Handle fill values for Tpar_ham
        fill_val = imported_data.data.get('Tpar_ham_FILLVAL', -1e+38)
        Tpar_ham_data = np.where(Tpar_ham_data == fill_val, np.nan, Tpar_ham_data)
        
        self.raw_data['Tpar_ham'] = Tpar_ham_data

        # Process Bx_inst (X-component of magnetic field in instrument coordinates)
        Bx_inst_data = imported_data.data['Bx_inst']
        
        # Handle fill values for Bx_inst
        fill_val = imported_data.data.get('Bx_inst_FILLVAL', -1e+38)
        Bx_inst_data = np.where(Bx_inst_data == fill_val, np.nan, Bx_inst_data)
        
        self.raw_data['Bx_inst'] = Bx_inst_data

        # Process By_inst (Y-component of magnetic field in instrument coordinates)
        By_inst_data = imported_data.data['By_inst']
        
        # Handle fill values for By_inst
        fill_val = imported_data.data.get('By_inst_FILLVAL', -1e+38)
        By_inst_data = np.where(By_inst_data == fill_val, np.nan, By_inst_data)
        
        self.raw_data['By_inst'] = By_inst_data

        # Process Bz_inst (Z-component of magnetic field in instrument coordinates)
        Bz_inst_data = imported_data.data['Bz_inst']
        
        # Handle fill values for Bz_inst
        fill_val = imported_data.data.get('Bz_inst_FILLVAL', -1e+38)
        Bz_inst_data = np.where(Bz_inst_data == fill_val, np.nan, Bz_inst_data)
        
        self.raw_data['Bz_inst'] = Bz_inst_data

        # Process sun_dist_rsun (Distance from Sun in solar radii)
        sun_dist_rsun_data = imported_data.data['sun_dist_rsun']
        
        # Handle fill values for sun_dist_rsun
        fill_val = imported_data.data.get('sun_dist_rsun_FILLVAL', -1e+38)
        sun_dist_rsun_data = np.where(sun_dist_rsun_data == fill_val, np.nan, sun_dist_rsun_data)
        
        self.raw_data['sun_dist_rsun'] = sun_dist_rsun_data
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

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
        print_manager.dependency_management("Setting up plot options for ham variables")
        
        self.n_core = plot_manager(
            self.raw_data['n_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='n_core',
                class_name='ham',
                subclass_name='n_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='n_core (cm^-3)',
                legend_label='Density of core proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.n_neck = plot_manager(
            self.raw_data['n_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='n_neck',
                class_name='ham',
                subclass_name='n_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='n_neck (cm^-3)',
                legend_label='Density of neck proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.n_ham = plot_manager(
            self.raw_data['n_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='n_ham',
                class_name='ham',
                subclass_name='n_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='n_ham (cm^-3)',
                legend_label='Density of hammerhead proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vx_inst_core = plot_manager(
            self.raw_data['vx_inst_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vx_inst_core',
                class_name='ham',
                subclass_name='vx_inst_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vx_inst_core (km/s)',
                legend_label='X-component velocity of core proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vy_inst_core = plot_manager(
            self.raw_data['vy_inst_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vy_inst_core',
                class_name='ham',
                subclass_name='vy_inst_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vy_inst_core (km/s)',
                legend_label='Y-component velocity of core proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vz_inst_core = plot_manager(
            self.raw_data['vz_inst_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vz_inst_core',
                class_name='ham',
                subclass_name='vz_inst_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vz_inst_core (km/s)',
                legend_label='Z-component velocity of core proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vx_inst_neck = plot_manager(
            self.raw_data['vx_inst_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vx_inst_neck',
                class_name='ham',
                subclass_name='vx_inst_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vx_inst_neck (km/s)',
                legend_label='X-component velocity of neck proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vy_inst_neck = plot_manager(
            self.raw_data['vy_inst_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vy_inst_neck',
                class_name='ham',
                subclass_name='vy_inst_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vy_inst_neck (km/s)',
                legend_label='Y-component velocity of neck proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vz_inst_neck = plot_manager(
            self.raw_data['vz_inst_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vz_inst_neck',
                class_name='ham',
                subclass_name='vz_inst_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vz_inst_neck (km/s)',
                legend_label='Z-component velocity of neck proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vx_inst_ham = plot_manager(
            self.raw_data['vx_inst_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vx_inst_ham',
                class_name='ham',
                subclass_name='vx_inst_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vx_inst_ham (km/s)',
                legend_label='X-component velocity of hammerhead proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vy_inst_ham = plot_manager(
            self.raw_data['vy_inst_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vy_inst_ham',
                class_name='ham',
                subclass_name='vy_inst_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vy_inst_ham (km/s)',
                legend_label='Y-component velocity of hammerhead proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.vz_inst_ham = plot_manager(
            self.raw_data['vz_inst_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='vz_inst_ham',
                class_name='ham',
                subclass_name='vz_inst_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='vz_inst_ham (km/s)',
                legend_label='Z-component velocity of hammerhead proton population in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.temp_core = plot_manager(
            self.raw_data['temp_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='temp_core',
                class_name='ham',
                subclass_name='temp_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='temp_core (eV)',
                legend_label='Temperature of core proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.temp_neck = plot_manager(
            self.raw_data['temp_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='temp_neck',
                class_name='ham',
                subclass_name='temp_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='temp_neck (eV)',
                legend_label='Temperature of neck proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.temp_ham = plot_manager(
            self.raw_data['temp_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='temp_ham',
                class_name='ham',
                subclass_name='temp_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='temp_ham (eV)',
                legend_label='Temperature of hammerhead proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tperp_core = plot_manager(
            self.raw_data['Tperp_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tperp_core',
                class_name='ham',
                subclass_name='Tperp_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tperp_core (eV)',
                legend_label='Temperature perpendicular to magnetic field of core proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tpar_core = plot_manager(
            self.raw_data['Tpar_core'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tpar_core',
                class_name='ham',
                subclass_name='Tpar_core',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tpar_core (eV)',
                legend_label='Temperature parallel to magnetic field of core proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tperp_neck = plot_manager(
            self.raw_data['Tperp_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tperp_neck',
                class_name='ham',
                subclass_name='Tperp_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tperp_neck (eV)',
                legend_label='Temperature perpendicular to magnetic field of neck proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tpar_neck = plot_manager(
            self.raw_data['Tpar_neck'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tpar_neck',
                class_name='ham',
                subclass_name='Tpar_neck',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tpar_neck (eV)',
                legend_label='Temperature parallel to magnetic field of neck proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tperp_ham = plot_manager(
            self.raw_data['Tperp_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tperp_ham',
                class_name='ham',
                subclass_name='Tperp_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tperp_ham (eV)',
                legend_label='Temperature perpendicular to magnetic field of hammerhead proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Tpar_ham = plot_manager(
            self.raw_data['Tpar_ham'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Tpar_ham',
                class_name='ham',
                subclass_name='Tpar_ham',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Tpar_ham (eV)',
                legend_label='Temperature parallel to magnetic field of hammerhead proton population',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bx_inst = plot_manager(
            self.raw_data['Bx_inst'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Bx_inst',
                class_name='ham',
                subclass_name='Bx_inst',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Bx_inst (nT)',
                legend_label='X-component of magnetic field in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.By_inst = plot_manager(
            self.raw_data['By_inst'],
            plot_config=plot_config(
                data_type='ham',
                var_name='By_inst',
                class_name='ham',
                subclass_name='By_inst',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='By_inst (nT)',
                legend_label='Y-component of magnetic field in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bz_inst = plot_manager(
            self.raw_data['Bz_inst'],
            plot_config=plot_config(
                data_type='ham',
                var_name='Bz_inst',
                class_name='ham',
                subclass_name='Bz_inst',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='Bz_inst (nT)',
                legend_label='Z-component of magnetic field in instrument coordinates',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.sun_dist_rsun = plot_manager(
            self.raw_data['sun_dist_rsun'],
            plot_config=plot_config(
                data_type='ham',
                var_name='sun_dist_rsun',
                class_name='ham',
                subclass_name='sun_dist_rsun',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='sun_dist_rsun (R_sun)',
                legend_label='Distance from Sun in solar radii',
                color=None,
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
ham = ham_class(None)
print_manager.dependency_management(f'initialized ham class')
