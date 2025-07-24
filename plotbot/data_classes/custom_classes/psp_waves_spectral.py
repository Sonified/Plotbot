"""
Auto-generated plotbot class for PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf
Generated on: 2025-07-23T17:45:54.886181
Source: data/cdf_files/PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf

This class contains 96 variables from the CDF file.
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

class psp_waves_spectral_class:
    """
    CDF data class for PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf
    
    Variables:
    - FFT_time_1: FFT_time_1
    - Frequencies: Frequencies
    - ellipticity_b: Ellipticity (Bfield)
    - FFT_time_2: FFT_time_2
    - Frequencies_1: Frequencies_1
    - wave_normal_b: Wave Normal Angle (Bfield)
    - FFT_time_3: FFT_time_3
    - Frequencies_2: Frequencies_2
    - coherency_b: Coherency (Bfield)
    - FFT_time_4: FFT_time_4
    - Frequencies_3: Frequencies_3
    - B_power_para: Bfield Power Compressional
    - FFT_time_5: FFT_time_5
    - Frequencies_4: Frequencies_4
    - B_power_perp: Bfield Power Transverse
    - FFT_time_6: FFT_time_6
    - Frequencies_5: Frequencies_5
    - Wave_Power_b: Bfield Power perpendicular to wave normal direction k
    - FFT_time_7: FFT_time_7
    - Frequencies_6: Frequencies_6
    - S_mag: Poynting Flux Magnitude
    - FFT_time_8: FFT_time_8
    - Frequencies_7: Frequencies_7
    - S_Theta: Poynting Theta (S dot B)
    - FFT_time_9: FFT_time_9
    - Frequencies_8: Frequencies_8
    - S_Phi: Poynting Phi (clock angle where 0=RTN_T and 90=RTN_N)
    - FFT_time_10: FFT_time_10
    - Frequencies_9: Frequencies_9
    - Sn: Poynting Flux Parallel (Field-oriented)
    - FFT_time_11: FFT_time_11
    - Frequencies_10: Frequencies_10
    - Sp: Poynting Flux Perpendicular (approximately in RTN_T direction)
    - FFT_time_12: FFT_time_12
    - Frequencies_11: Frequencies_11
    - Sq: Poynting Flux Perpendicular (approximately in RTN_N direction)
    - Bfield_time: Bfield_time
    - Bn: Parallel Magnetic Field Component (B!B||!N)
    - Bfield_time_1: Bfield_time_1
    - Bp: Perpendicular Magnetic Field Component in Quasi-Tangential RTN Direction (B!B&perp;T!N)
    - Bfield_time_2: Bfield_time_2
    - Bq: Perpendicular Magnetic Field Component in Quasi-Normal RTN Direction (B!B&perp;N!N)
    - FFT_time_13: FFT_time_13
    - Frequencies_12: Frequencies_12
    - Bn_fft: FFT of Compressional magnetic field
    - FFT_time_14: FFT_time_14
    - Frequencies_13: Frequencies_13
    - Bp_fft: FFT of Transverse magnetic field in RTN_T direction
    - FFT_time_15: FFT_time_15
    - Frequencies_14: Frequencies_14
    - Bq_fft: FFT of Transverse magnetic field in RTN_N direction
    - FFT_time_16: FFT_time_16
    - Frequencies_15: Frequencies_15
    - ellipticity_e: Ellipticity (Efield)
    - FFT_time_17: FFT_time_17
    - Frequencies_16: Frequencies_16
    - wave_normal_e: Wave Normal Angle (Efield)
    - FFT_time_18: FFT_time_18
    - Frequencies_17: Frequencies_17
    - coherency_e: Coherency (Efield)
    - FFT_time_19: FFT_time_19
    - Frequencies_18: Frequencies_18
    - E_power_para: Efield Power Compressional
    - FFT_time_20: FFT_time_20
    - Frequencies_19: Frequencies_19
    - E_power_perp: Efield Power Transverse
    - FFT_time_21: FFT_time_21
    - Frequencies_20: Frequencies_20
    - Wave_Power_e: Efield Power perpendicular to wave normal direction k
    - FFT_time_22: FFT_time_22
    - Frequencies_21: Frequencies_21
    - En_fft: FFT of Compressional electric field
    - FFT_time_23: FFT_time_23
    - Frequencies_22: Frequencies_22
    - Ep_fft: FFT of Transverse electric field in RTN_T direction
    - FFT_time_24: FFT_time_24
    - Frequencies_23: Frequencies_23
    - Eq_fft: FFT of Transverse electric field in RTN_N direction
    - FFT_time_25: FFT_time_25
    - Frequencies_24: Frequencies_24
    - kx_B: Wave Vector kx (Bfield)
    - FFT_time_26: FFT_time_26
    - Frequencies_25: Frequencies_25
    - ky_B: Wave Vector ky (Bfield)
    - FFT_time_27: FFT_time_27
    - Frequencies_26: Frequencies_26
    - kz_B: Wave Vector kz (Bfield)
    - FFT_time_28: FFT_time_28
    - Frequencies_27: Frequencies_27
    - kx_E: Wave Vector kx (Efield)
    - FFT_time_29: FFT_time_29
    - Frequencies_28: Frequencies_28
    - ky_E: Wave Vector ky (Efield)
    - FFT_time_30: FFT_time_30
    - Frequencies_29: Frequencies_29
    - kz_E: Wave Vector kz (Efield)
    """
    
    def __init__(self, imported_data):
        # Initialize basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'psp_waves_spectral')
        object.__setattr__(self, 'data_type', 'psp_waves_spectral')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
        'FFT_time_1': None,
        'Frequencies': None,
        'ellipticity_b': None,
        'FFT_time_2': None,
        'Frequencies_1': None,
        'wave_normal_b': None,
        'FFT_time_3': None,
        'Frequencies_2': None,
        'coherency_b': None,
        'FFT_time_4': None,
        'Frequencies_3': None,
        'B_power_para': None,
        'FFT_time_5': None,
        'Frequencies_4': None,
        'B_power_perp': None,
        'FFT_time_6': None,
        'Frequencies_5': None,
        'Wave_Power_b': None,
        'FFT_time_7': None,
        'Frequencies_6': None,
        'S_mag': None,
        'FFT_time_8': None,
        'Frequencies_7': None,
        'S_Theta': None,
        'FFT_time_9': None,
        'Frequencies_8': None,
        'S_Phi': None,
        'FFT_time_10': None,
        'Frequencies_9': None,
        'Sn': None,
        'FFT_time_11': None,
        'Frequencies_10': None,
        'Sp': None,
        'FFT_time_12': None,
        'Frequencies_11': None,
        'Sq': None,
        'Bfield_time': None,
        'Bn': None,
        'Bfield_time_1': None,
        'Bp': None,
        'Bfield_time_2': None,
        'Bq': None,
        'FFT_time_13': None,
        'Frequencies_12': None,
        'Bn_fft': None,
        'FFT_time_14': None,
        'Frequencies_13': None,
        'Bp_fft': None,
        'FFT_time_15': None,
        'Frequencies_14': None,
        'Bq_fft': None,
        'FFT_time_16': None,
        'Frequencies_15': None,
        'ellipticity_e': None,
        'FFT_time_17': None,
        'Frequencies_16': None,
        'wave_normal_e': None,
        'FFT_time_18': None,
        'Frequencies_17': None,
        'coherency_e': None,
        'FFT_time_19': None,
        'Frequencies_18': None,
        'E_power_para': None,
        'FFT_time_20': None,
        'Frequencies_19': None,
        'E_power_perp': None,
        'FFT_time_21': None,
        'Frequencies_20': None,
        'Wave_Power_e': None,
        'FFT_time_22': None,
        'Frequencies_21': None,
        'En_fft': None,
        'FFT_time_23': None,
        'Frequencies_22': None,
        'Ep_fft': None,
        'FFT_time_24': None,
        'Frequencies_23': None,
        'Eq_fft': None,
        'FFT_time_25': None,
        'Frequencies_24': None,
        'kx_B': None,
        'FFT_time_26': None,
        'Frequencies_25': None,
        'ky_B': None,
        'FFT_time_27': None,
        'Frequencies_26': None,
        'kz_B': None,
        'FFT_time_28': None,
        'Frequencies_27': None,
        'kx_E': None,
        'FFT_time_29': None,
        'Frequencies_28': None,
        'ky_E': None,
        'FFT_time_30': None,
        'Frequencies_29': None,
        'kz_E': None
    })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)
        object.__setattr__(self, 'variable_meshes', {})
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', 'data/cdf_files/PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf')
        object.__setattr__(self, '_cdf_file_pattern', 'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf')

        if imported_data is None:
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management(f"Calculating psp_waves_spectral variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status(f"Successfully calculated psp_waves_spectral variables.")
        
        # Auto-register with data_cubby (following plotbot pattern)
        from plotbot.data_cubby import data_cubby
        data_cubby.stash(self, class_name='psp_waves_spectral')
        print_manager.dependency_management(f"Registered psp_waves_spectral with data_cubby")
    
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
        
        print_manager.dependency_management(f'psp_waves_spectral getattr helper!')
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
            print_manager.dependency_management(f'psp_waves_spectral setattr helper!')
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
        

        # Process FFT_time_1 (FFT_time_1)
        FFT_time_1_data = imported_data.data['FFT_time_1']
        
        # Handle fill values for FFT_time_1
        fill_val = imported_data.data.get('FFT_time_1_FILLVAL', -1e+38)
        FFT_time_1_data = np.where(FFT_time_1_data == fill_val, np.nan, FFT_time_1_data)
        
        self.raw_data['FFT_time_1'] = FFT_time_1_data

        # Process Frequencies (Frequencies)
        Frequencies_data = imported_data.data['Frequencies']
        
        # Handle fill values for Frequencies
        fill_val = imported_data.data.get('Frequencies_FILLVAL', -1e+38)
        Frequencies_data = np.where(Frequencies_data == fill_val, np.nan, Frequencies_data)
        
        self.raw_data['Frequencies'] = Frequencies_data

        # Process ellipticity_b (Ellipticity (Bfield))
        ellipticity_b_data = imported_data.data['ellipticity_b']
        
        # Handle fill values for ellipticity_b
        fill_val = imported_data.data.get('ellipticity_b_FILLVAL', -1e+38)
        ellipticity_b_data = np.where(ellipticity_b_data == fill_val, np.nan, ellipticity_b_data)
        
        self.raw_data['ellipticity_b'] = ellipticity_b_data

        # Process FFT_time_2 (FFT_time_2)
        FFT_time_2_data = imported_data.data['FFT_time_2']
        
        # Handle fill values for FFT_time_2
        fill_val = imported_data.data.get('FFT_time_2_FILLVAL', -1e+38)
        FFT_time_2_data = np.where(FFT_time_2_data == fill_val, np.nan, FFT_time_2_data)
        
        self.raw_data['FFT_time_2'] = FFT_time_2_data

        # Process Frequencies_1 (Frequencies_1)
        Frequencies_1_data = imported_data.data['Frequencies_1']
        
        # Handle fill values for Frequencies_1
        fill_val = imported_data.data.get('Frequencies_1_FILLVAL', -1e+38)
        Frequencies_1_data = np.where(Frequencies_1_data == fill_val, np.nan, Frequencies_1_data)
        
        self.raw_data['Frequencies_1'] = Frequencies_1_data

        # Process wave_normal_b (Wave Normal Angle (Bfield))
        wave_normal_b_data = imported_data.data['wave_normal_b']
        
        # Handle fill values for wave_normal_b
        fill_val = imported_data.data.get('wave_normal_b_FILLVAL', -1e+38)
        wave_normal_b_data = np.where(wave_normal_b_data == fill_val, np.nan, wave_normal_b_data)
        
        self.raw_data['wave_normal_b'] = wave_normal_b_data

        # Process FFT_time_3 (FFT_time_3)
        FFT_time_3_data = imported_data.data['FFT_time_3']
        
        # Handle fill values for FFT_time_3
        fill_val = imported_data.data.get('FFT_time_3_FILLVAL', -1e+38)
        FFT_time_3_data = np.where(FFT_time_3_data == fill_val, np.nan, FFT_time_3_data)
        
        self.raw_data['FFT_time_3'] = FFT_time_3_data

        # Process Frequencies_2 (Frequencies_2)
        Frequencies_2_data = imported_data.data['Frequencies_2']
        
        # Handle fill values for Frequencies_2
        fill_val = imported_data.data.get('Frequencies_2_FILLVAL', -1e+38)
        Frequencies_2_data = np.where(Frequencies_2_data == fill_val, np.nan, Frequencies_2_data)
        
        self.raw_data['Frequencies_2'] = Frequencies_2_data

        # Process coherency_b (Coherency (Bfield))
        coherency_b_data = imported_data.data['coherency_b']
        
        # Handle fill values for coherency_b
        fill_val = imported_data.data.get('coherency_b_FILLVAL', -1e+38)
        coherency_b_data = np.where(coherency_b_data == fill_val, np.nan, coherency_b_data)
        
        self.raw_data['coherency_b'] = coherency_b_data

        # Process FFT_time_4 (FFT_time_4)
        FFT_time_4_data = imported_data.data['FFT_time_4']
        
        # Handle fill values for FFT_time_4
        fill_val = imported_data.data.get('FFT_time_4_FILLVAL', -1e+38)
        FFT_time_4_data = np.where(FFT_time_4_data == fill_val, np.nan, FFT_time_4_data)
        
        self.raw_data['FFT_time_4'] = FFT_time_4_data

        # Process Frequencies_3 (Frequencies_3)
        Frequencies_3_data = imported_data.data['Frequencies_3']
        
        # Handle fill values for Frequencies_3
        fill_val = imported_data.data.get('Frequencies_3_FILLVAL', -1e+38)
        Frequencies_3_data = np.where(Frequencies_3_data == fill_val, np.nan, Frequencies_3_data)
        
        self.raw_data['Frequencies_3'] = Frequencies_3_data

        # Process B_power_para (Bfield Power Compressional)
        B_power_para_data = imported_data.data['B_power_para']
        
        # Handle fill values for B_power_para
        fill_val = imported_data.data.get('B_power_para_FILLVAL', -1e+38)
        B_power_para_data = np.where(B_power_para_data == fill_val, np.nan, B_power_para_data)
        
        self.raw_data['B_power_para'] = B_power_para_data

        # Process FFT_time_5 (FFT_time_5)
        FFT_time_5_data = imported_data.data['FFT_time_5']
        
        # Handle fill values for FFT_time_5
        fill_val = imported_data.data.get('FFT_time_5_FILLVAL', -1e+38)
        FFT_time_5_data = np.where(FFT_time_5_data == fill_val, np.nan, FFT_time_5_data)
        
        self.raw_data['FFT_time_5'] = FFT_time_5_data

        # Process Frequencies_4 (Frequencies_4)
        Frequencies_4_data = imported_data.data['Frequencies_4']
        
        # Handle fill values for Frequencies_4
        fill_val = imported_data.data.get('Frequencies_4_FILLVAL', -1e+38)
        Frequencies_4_data = np.where(Frequencies_4_data == fill_val, np.nan, Frequencies_4_data)
        
        self.raw_data['Frequencies_4'] = Frequencies_4_data

        # Process B_power_perp (Bfield Power Transverse)
        B_power_perp_data = imported_data.data['B_power_perp']
        
        # Handle fill values for B_power_perp
        fill_val = imported_data.data.get('B_power_perp_FILLVAL', -1e+38)
        B_power_perp_data = np.where(B_power_perp_data == fill_val, np.nan, B_power_perp_data)
        
        self.raw_data['B_power_perp'] = B_power_perp_data

        # Process FFT_time_6 (FFT_time_6)
        FFT_time_6_data = imported_data.data['FFT_time_6']
        
        # Handle fill values for FFT_time_6
        fill_val = imported_data.data.get('FFT_time_6_FILLVAL', -1e+38)
        FFT_time_6_data = np.where(FFT_time_6_data == fill_val, np.nan, FFT_time_6_data)
        
        self.raw_data['FFT_time_6'] = FFT_time_6_data

        # Process Frequencies_5 (Frequencies_5)
        Frequencies_5_data = imported_data.data['Frequencies_5']
        
        # Handle fill values for Frequencies_5
        fill_val = imported_data.data.get('Frequencies_5_FILLVAL', -1e+38)
        Frequencies_5_data = np.where(Frequencies_5_data == fill_val, np.nan, Frequencies_5_data)
        
        self.raw_data['Frequencies_5'] = Frequencies_5_data

        # Process Wave_Power_b (Bfield Power perpendicular to wave normal direction k)
        Wave_Power_b_data = imported_data.data['Wave_Power_b']
        
        # Handle fill values for Wave_Power_b
        fill_val = imported_data.data.get('Wave_Power_b_FILLVAL', -1e+38)
        Wave_Power_b_data = np.where(Wave_Power_b_data == fill_val, np.nan, Wave_Power_b_data)
        
        self.raw_data['Wave_Power_b'] = Wave_Power_b_data

        # Process FFT_time_7 (FFT_time_7)
        FFT_time_7_data = imported_data.data['FFT_time_7']
        
        # Handle fill values for FFT_time_7
        fill_val = imported_data.data.get('FFT_time_7_FILLVAL', -1e+38)
        FFT_time_7_data = np.where(FFT_time_7_data == fill_val, np.nan, FFT_time_7_data)
        
        self.raw_data['FFT_time_7'] = FFT_time_7_data

        # Process Frequencies_6 (Frequencies_6)
        Frequencies_6_data = imported_data.data['Frequencies_6']
        
        # Handle fill values for Frequencies_6
        fill_val = imported_data.data.get('Frequencies_6_FILLVAL', -1e+38)
        Frequencies_6_data = np.where(Frequencies_6_data == fill_val, np.nan, Frequencies_6_data)
        
        self.raw_data['Frequencies_6'] = Frequencies_6_data

        # Process S_mag (Poynting Flux Magnitude)
        S_mag_data = imported_data.data['S_mag']
        
        # Handle fill values for S_mag
        fill_val = imported_data.data.get('S_mag_FILLVAL', -1e+38)
        S_mag_data = np.where(S_mag_data == fill_val, np.nan, S_mag_data)
        
        self.raw_data['S_mag'] = S_mag_data

        # Process FFT_time_8 (FFT_time_8)
        FFT_time_8_data = imported_data.data['FFT_time_8']
        
        # Handle fill values for FFT_time_8
        fill_val = imported_data.data.get('FFT_time_8_FILLVAL', -1e+38)
        FFT_time_8_data = np.where(FFT_time_8_data == fill_val, np.nan, FFT_time_8_data)
        
        self.raw_data['FFT_time_8'] = FFT_time_8_data

        # Process Frequencies_7 (Frequencies_7)
        Frequencies_7_data = imported_data.data['Frequencies_7']
        
        # Handle fill values for Frequencies_7
        fill_val = imported_data.data.get('Frequencies_7_FILLVAL', -1e+38)
        Frequencies_7_data = np.where(Frequencies_7_data == fill_val, np.nan, Frequencies_7_data)
        
        self.raw_data['Frequencies_7'] = Frequencies_7_data

        # Process S_Theta (Poynting Theta (S dot B))
        S_Theta_data = imported_data.data['S_Theta']
        
        # Handle fill values for S_Theta
        fill_val = imported_data.data.get('S_Theta_FILLVAL', -1e+38)
        S_Theta_data = np.where(S_Theta_data == fill_val, np.nan, S_Theta_data)
        
        self.raw_data['S_Theta'] = S_Theta_data

        # Process FFT_time_9 (FFT_time_9)
        FFT_time_9_data = imported_data.data['FFT_time_9']
        
        # Handle fill values for FFT_time_9
        fill_val = imported_data.data.get('FFT_time_9_FILLVAL', -1e+38)
        FFT_time_9_data = np.where(FFT_time_9_data == fill_val, np.nan, FFT_time_9_data)
        
        self.raw_data['FFT_time_9'] = FFT_time_9_data

        # Process Frequencies_8 (Frequencies_8)
        Frequencies_8_data = imported_data.data['Frequencies_8']
        
        # Handle fill values for Frequencies_8
        fill_val = imported_data.data.get('Frequencies_8_FILLVAL', -1e+38)
        Frequencies_8_data = np.where(Frequencies_8_data == fill_val, np.nan, Frequencies_8_data)
        
        self.raw_data['Frequencies_8'] = Frequencies_8_data

        # Process S_Phi (Poynting Phi (clock angle where 0=RTN_T and 90=RTN_N))
        S_Phi_data = imported_data.data['S_Phi']
        
        # Handle fill values for S_Phi
        fill_val = imported_data.data.get('S_Phi_FILLVAL', -1e+38)
        S_Phi_data = np.where(S_Phi_data == fill_val, np.nan, S_Phi_data)
        
        self.raw_data['S_Phi'] = S_Phi_data

        # Process FFT_time_10 (FFT_time_10)
        FFT_time_10_data = imported_data.data['FFT_time_10']
        
        # Handle fill values for FFT_time_10
        fill_val = imported_data.data.get('FFT_time_10_FILLVAL', -1e+38)
        FFT_time_10_data = np.where(FFT_time_10_data == fill_val, np.nan, FFT_time_10_data)
        
        self.raw_data['FFT_time_10'] = FFT_time_10_data

        # Process Frequencies_9 (Frequencies_9)
        Frequencies_9_data = imported_data.data['Frequencies_9']
        
        # Handle fill values for Frequencies_9
        fill_val = imported_data.data.get('Frequencies_9_FILLVAL', -1e+38)
        Frequencies_9_data = np.where(Frequencies_9_data == fill_val, np.nan, Frequencies_9_data)
        
        self.raw_data['Frequencies_9'] = Frequencies_9_data

        # Process Sn (Poynting Flux Parallel (Field-oriented))
        Sn_data = imported_data.data['Sn']
        
        # Handle fill values for Sn
        fill_val = imported_data.data.get('Sn_FILLVAL', -1e+38)
        Sn_data = np.where(Sn_data == fill_val, np.nan, Sn_data)
        
        self.raw_data['Sn'] = Sn_data

        # Process FFT_time_11 (FFT_time_11)
        FFT_time_11_data = imported_data.data['FFT_time_11']
        
        # Handle fill values for FFT_time_11
        fill_val = imported_data.data.get('FFT_time_11_FILLVAL', -1e+38)
        FFT_time_11_data = np.where(FFT_time_11_data == fill_val, np.nan, FFT_time_11_data)
        
        self.raw_data['FFT_time_11'] = FFT_time_11_data

        # Process Frequencies_10 (Frequencies_10)
        Frequencies_10_data = imported_data.data['Frequencies_10']
        
        # Handle fill values for Frequencies_10
        fill_val = imported_data.data.get('Frequencies_10_FILLVAL', -1e+38)
        Frequencies_10_data = np.where(Frequencies_10_data == fill_val, np.nan, Frequencies_10_data)
        
        self.raw_data['Frequencies_10'] = Frequencies_10_data

        # Process Sp (Poynting Flux Perpendicular (approximately in RTN_T direction))
        Sp_data = imported_data.data['Sp']
        
        # Handle fill values for Sp
        fill_val = imported_data.data.get('Sp_FILLVAL', -1e+38)
        Sp_data = np.where(Sp_data == fill_val, np.nan, Sp_data)
        
        self.raw_data['Sp'] = Sp_data

        # Process FFT_time_12 (FFT_time_12)
        FFT_time_12_data = imported_data.data['FFT_time_12']
        
        # Handle fill values for FFT_time_12
        fill_val = imported_data.data.get('FFT_time_12_FILLVAL', -1e+38)
        FFT_time_12_data = np.where(FFT_time_12_data == fill_val, np.nan, FFT_time_12_data)
        
        self.raw_data['FFT_time_12'] = FFT_time_12_data

        # Process Frequencies_11 (Frequencies_11)
        Frequencies_11_data = imported_data.data['Frequencies_11']
        
        # Handle fill values for Frequencies_11
        fill_val = imported_data.data.get('Frequencies_11_FILLVAL', -1e+38)
        Frequencies_11_data = np.where(Frequencies_11_data == fill_val, np.nan, Frequencies_11_data)
        
        self.raw_data['Frequencies_11'] = Frequencies_11_data

        # Process Sq (Poynting Flux Perpendicular (approximately in RTN_N direction))
        Sq_data = imported_data.data['Sq']
        
        # Handle fill values for Sq
        fill_val = imported_data.data.get('Sq_FILLVAL', -1e+38)
        Sq_data = np.where(Sq_data == fill_val, np.nan, Sq_data)
        
        self.raw_data['Sq'] = Sq_data

        # Process Bfield_time (Bfield_time)
        Bfield_time_data = imported_data.data['Bfield_time']
        
        # Handle fill values for Bfield_time
        fill_val = imported_data.data.get('Bfield_time_FILLVAL', -1e+38)
        Bfield_time_data = np.where(Bfield_time_data == fill_val, np.nan, Bfield_time_data)
        
        self.raw_data['Bfield_time'] = Bfield_time_data

        # Process Bn (Parallel Magnetic Field Component (B!B||!N))
        Bn_data = imported_data.data['Bn']
        
        # Handle fill values for Bn
        fill_val = imported_data.data.get('Bn_FILLVAL', -1e+38)
        Bn_data = np.where(Bn_data == fill_val, np.nan, Bn_data)
        
        self.raw_data['Bn'] = Bn_data

        # Process Bfield_time_1 (Bfield_time_1)
        Bfield_time_1_data = imported_data.data['Bfield_time_1']
        
        # Handle fill values for Bfield_time_1
        fill_val = imported_data.data.get('Bfield_time_1_FILLVAL', -1e+38)
        Bfield_time_1_data = np.where(Bfield_time_1_data == fill_val, np.nan, Bfield_time_1_data)
        
        self.raw_data['Bfield_time_1'] = Bfield_time_1_data

        # Process Bp (Perpendicular Magnetic Field Component in Quasi-Tangential RTN Direction (B!B&perp;T!N))
        Bp_data = imported_data.data['Bp']
        
        # Handle fill values for Bp
        fill_val = imported_data.data.get('Bp_FILLVAL', -1e+38)
        Bp_data = np.where(Bp_data == fill_val, np.nan, Bp_data)
        
        self.raw_data['Bp'] = Bp_data

        # Process Bfield_time_2 (Bfield_time_2)
        Bfield_time_2_data = imported_data.data['Bfield_time_2']
        
        # Handle fill values for Bfield_time_2
        fill_val = imported_data.data.get('Bfield_time_2_FILLVAL', -1e+38)
        Bfield_time_2_data = np.where(Bfield_time_2_data == fill_val, np.nan, Bfield_time_2_data)
        
        self.raw_data['Bfield_time_2'] = Bfield_time_2_data

        # Process Bq (Perpendicular Magnetic Field Component in Quasi-Normal RTN Direction (B!B&perp;N!N))
        Bq_data = imported_data.data['Bq']
        
        # Handle fill values for Bq
        fill_val = imported_data.data.get('Bq_FILLVAL', -1e+38)
        Bq_data = np.where(Bq_data == fill_val, np.nan, Bq_data)
        
        self.raw_data['Bq'] = Bq_data

        # Process FFT_time_13 (FFT_time_13)
        FFT_time_13_data = imported_data.data['FFT_time_13']
        
        # Handle fill values for FFT_time_13
        fill_val = imported_data.data.get('FFT_time_13_FILLVAL', -1e+38)
        FFT_time_13_data = np.where(FFT_time_13_data == fill_val, np.nan, FFT_time_13_data)
        
        self.raw_data['FFT_time_13'] = FFT_time_13_data

        # Process Frequencies_12 (Frequencies_12)
        Frequencies_12_data = imported_data.data['Frequencies_12']
        
        # Handle fill values for Frequencies_12
        fill_val = imported_data.data.get('Frequencies_12_FILLVAL', -1e+38)
        Frequencies_12_data = np.where(Frequencies_12_data == fill_val, np.nan, Frequencies_12_data)
        
        self.raw_data['Frequencies_12'] = Frequencies_12_data

        # Process Bn_fft (FFT of Compressional magnetic field)
        Bn_fft_data = imported_data.data['Bn_fft']
        
        # Handle fill values for Bn_fft
        fill_val = imported_data.data.get('Bn_fft_FILLVAL', -1e+38)
        Bn_fft_data = np.where(Bn_fft_data == fill_val, np.nan, Bn_fft_data)
        
        self.raw_data['Bn_fft'] = Bn_fft_data

        # Process FFT_time_14 (FFT_time_14)
        FFT_time_14_data = imported_data.data['FFT_time_14']
        
        # Handle fill values for FFT_time_14
        fill_val = imported_data.data.get('FFT_time_14_FILLVAL', -1e+38)
        FFT_time_14_data = np.where(FFT_time_14_data == fill_val, np.nan, FFT_time_14_data)
        
        self.raw_data['FFT_time_14'] = FFT_time_14_data

        # Process Frequencies_13 (Frequencies_13)
        Frequencies_13_data = imported_data.data['Frequencies_13']
        
        # Handle fill values for Frequencies_13
        fill_val = imported_data.data.get('Frequencies_13_FILLVAL', -1e+38)
        Frequencies_13_data = np.where(Frequencies_13_data == fill_val, np.nan, Frequencies_13_data)
        
        self.raw_data['Frequencies_13'] = Frequencies_13_data

        # Process Bp_fft (FFT of Transverse magnetic field in RTN_T direction)
        Bp_fft_data = imported_data.data['Bp_fft']
        
        # Handle fill values for Bp_fft
        fill_val = imported_data.data.get('Bp_fft_FILLVAL', -1e+38)
        Bp_fft_data = np.where(Bp_fft_data == fill_val, np.nan, Bp_fft_data)
        
        self.raw_data['Bp_fft'] = Bp_fft_data

        # Process FFT_time_15 (FFT_time_15)
        FFT_time_15_data = imported_data.data['FFT_time_15']
        
        # Handle fill values for FFT_time_15
        fill_val = imported_data.data.get('FFT_time_15_FILLVAL', -1e+38)
        FFT_time_15_data = np.where(FFT_time_15_data == fill_val, np.nan, FFT_time_15_data)
        
        self.raw_data['FFT_time_15'] = FFT_time_15_data

        # Process Frequencies_14 (Frequencies_14)
        Frequencies_14_data = imported_data.data['Frequencies_14']
        
        # Handle fill values for Frequencies_14
        fill_val = imported_data.data.get('Frequencies_14_FILLVAL', -1e+38)
        Frequencies_14_data = np.where(Frequencies_14_data == fill_val, np.nan, Frequencies_14_data)
        
        self.raw_data['Frequencies_14'] = Frequencies_14_data

        # Process Bq_fft (FFT of Transverse magnetic field in RTN_N direction)
        Bq_fft_data = imported_data.data['Bq_fft']
        
        # Handle fill values for Bq_fft
        fill_val = imported_data.data.get('Bq_fft_FILLVAL', -1e+38)
        Bq_fft_data = np.where(Bq_fft_data == fill_val, np.nan, Bq_fft_data)
        
        self.raw_data['Bq_fft'] = Bq_fft_data

        # Process FFT_time_16 (FFT_time_16)
        FFT_time_16_data = imported_data.data['FFT_time_16']
        
        # Handle fill values for FFT_time_16
        fill_val = imported_data.data.get('FFT_time_16_FILLVAL', -1e+38)
        FFT_time_16_data = np.where(FFT_time_16_data == fill_val, np.nan, FFT_time_16_data)
        
        self.raw_data['FFT_time_16'] = FFT_time_16_data

        # Process Frequencies_15 (Frequencies_15)
        Frequencies_15_data = imported_data.data['Frequencies_15']
        
        # Handle fill values for Frequencies_15
        fill_val = imported_data.data.get('Frequencies_15_FILLVAL', -1e+38)
        Frequencies_15_data = np.where(Frequencies_15_data == fill_val, np.nan, Frequencies_15_data)
        
        self.raw_data['Frequencies_15'] = Frequencies_15_data

        # Process ellipticity_e (Ellipticity (Efield))
        ellipticity_e_data = imported_data.data['ellipticity_e']
        
        # Handle fill values for ellipticity_e
        fill_val = imported_data.data.get('ellipticity_e_FILLVAL', -1e+38)
        ellipticity_e_data = np.where(ellipticity_e_data == fill_val, np.nan, ellipticity_e_data)
        
        self.raw_data['ellipticity_e'] = ellipticity_e_data

        # Process FFT_time_17 (FFT_time_17)
        FFT_time_17_data = imported_data.data['FFT_time_17']
        
        # Handle fill values for FFT_time_17
        fill_val = imported_data.data.get('FFT_time_17_FILLVAL', -1e+38)
        FFT_time_17_data = np.where(FFT_time_17_data == fill_val, np.nan, FFT_time_17_data)
        
        self.raw_data['FFT_time_17'] = FFT_time_17_data

        # Process Frequencies_16 (Frequencies_16)
        Frequencies_16_data = imported_data.data['Frequencies_16']
        
        # Handle fill values for Frequencies_16
        fill_val = imported_data.data.get('Frequencies_16_FILLVAL', -1e+38)
        Frequencies_16_data = np.where(Frequencies_16_data == fill_val, np.nan, Frequencies_16_data)
        
        self.raw_data['Frequencies_16'] = Frequencies_16_data

        # Process wave_normal_e (Wave Normal Angle (Efield))
        wave_normal_e_data = imported_data.data['wave_normal_e']
        
        # Handle fill values for wave_normal_e
        fill_val = imported_data.data.get('wave_normal_e_FILLVAL', -1e+38)
        wave_normal_e_data = np.where(wave_normal_e_data == fill_val, np.nan, wave_normal_e_data)
        
        self.raw_data['wave_normal_e'] = wave_normal_e_data

        # Process FFT_time_18 (FFT_time_18)
        FFT_time_18_data = imported_data.data['FFT_time_18']
        
        # Handle fill values for FFT_time_18
        fill_val = imported_data.data.get('FFT_time_18_FILLVAL', -1e+38)
        FFT_time_18_data = np.where(FFT_time_18_data == fill_val, np.nan, FFT_time_18_data)
        
        self.raw_data['FFT_time_18'] = FFT_time_18_data

        # Process Frequencies_17 (Frequencies_17)
        Frequencies_17_data = imported_data.data['Frequencies_17']
        
        # Handle fill values for Frequencies_17
        fill_val = imported_data.data.get('Frequencies_17_FILLVAL', -1e+38)
        Frequencies_17_data = np.where(Frequencies_17_data == fill_val, np.nan, Frequencies_17_data)
        
        self.raw_data['Frequencies_17'] = Frequencies_17_data

        # Process coherency_e (Coherency (Efield))
        coherency_e_data = imported_data.data['coherency_e']
        
        # Handle fill values for coherency_e
        fill_val = imported_data.data.get('coherency_e_FILLVAL', -1e+38)
        coherency_e_data = np.where(coherency_e_data == fill_val, np.nan, coherency_e_data)
        
        self.raw_data['coherency_e'] = coherency_e_data

        # Process FFT_time_19 (FFT_time_19)
        FFT_time_19_data = imported_data.data['FFT_time_19']
        
        # Handle fill values for FFT_time_19
        fill_val = imported_data.data.get('FFT_time_19_FILLVAL', -1e+38)
        FFT_time_19_data = np.where(FFT_time_19_data == fill_val, np.nan, FFT_time_19_data)
        
        self.raw_data['FFT_time_19'] = FFT_time_19_data

        # Process Frequencies_18 (Frequencies_18)
        Frequencies_18_data = imported_data.data['Frequencies_18']
        
        # Handle fill values for Frequencies_18
        fill_val = imported_data.data.get('Frequencies_18_FILLVAL', -1e+38)
        Frequencies_18_data = np.where(Frequencies_18_data == fill_val, np.nan, Frequencies_18_data)
        
        self.raw_data['Frequencies_18'] = Frequencies_18_data

        # Process E_power_para (Efield Power Compressional)
        E_power_para_data = imported_data.data['E_power_para']
        
        # Handle fill values for E_power_para
        fill_val = imported_data.data.get('E_power_para_FILLVAL', -1e+38)
        E_power_para_data = np.where(E_power_para_data == fill_val, np.nan, E_power_para_data)
        
        self.raw_data['E_power_para'] = E_power_para_data

        # Process FFT_time_20 (FFT_time_20)
        FFT_time_20_data = imported_data.data['FFT_time_20']
        
        # Handle fill values for FFT_time_20
        fill_val = imported_data.data.get('FFT_time_20_FILLVAL', -1e+38)
        FFT_time_20_data = np.where(FFT_time_20_data == fill_val, np.nan, FFT_time_20_data)
        
        self.raw_data['FFT_time_20'] = FFT_time_20_data

        # Process Frequencies_19 (Frequencies_19)
        Frequencies_19_data = imported_data.data['Frequencies_19']
        
        # Handle fill values for Frequencies_19
        fill_val = imported_data.data.get('Frequencies_19_FILLVAL', -1e+38)
        Frequencies_19_data = np.where(Frequencies_19_data == fill_val, np.nan, Frequencies_19_data)
        
        self.raw_data['Frequencies_19'] = Frequencies_19_data

        # Process E_power_perp (Efield Power Transverse)
        E_power_perp_data = imported_data.data['E_power_perp']
        
        # Handle fill values for E_power_perp
        fill_val = imported_data.data.get('E_power_perp_FILLVAL', -1e+38)
        E_power_perp_data = np.where(E_power_perp_data == fill_val, np.nan, E_power_perp_data)
        
        self.raw_data['E_power_perp'] = E_power_perp_data

        # Process FFT_time_21 (FFT_time_21)
        FFT_time_21_data = imported_data.data['FFT_time_21']
        
        # Handle fill values for FFT_time_21
        fill_val = imported_data.data.get('FFT_time_21_FILLVAL', -1e+38)
        FFT_time_21_data = np.where(FFT_time_21_data == fill_val, np.nan, FFT_time_21_data)
        
        self.raw_data['FFT_time_21'] = FFT_time_21_data

        # Process Frequencies_20 (Frequencies_20)
        Frequencies_20_data = imported_data.data['Frequencies_20']
        
        # Handle fill values for Frequencies_20
        fill_val = imported_data.data.get('Frequencies_20_FILLVAL', -1e+38)
        Frequencies_20_data = np.where(Frequencies_20_data == fill_val, np.nan, Frequencies_20_data)
        
        self.raw_data['Frequencies_20'] = Frequencies_20_data

        # Process Wave_Power_e (Efield Power perpendicular to wave normal direction k)
        Wave_Power_e_data = imported_data.data['Wave_Power_e']
        
        # Handle fill values for Wave_Power_e
        fill_val = imported_data.data.get('Wave_Power_e_FILLVAL', -1e+38)
        Wave_Power_e_data = np.where(Wave_Power_e_data == fill_val, np.nan, Wave_Power_e_data)
        
        self.raw_data['Wave_Power_e'] = Wave_Power_e_data

        # Process FFT_time_22 (FFT_time_22)
        FFT_time_22_data = imported_data.data['FFT_time_22']
        
        # Handle fill values for FFT_time_22
        fill_val = imported_data.data.get('FFT_time_22_FILLVAL', -1e+38)
        FFT_time_22_data = np.where(FFT_time_22_data == fill_val, np.nan, FFT_time_22_data)
        
        self.raw_data['FFT_time_22'] = FFT_time_22_data

        # Process Frequencies_21 (Frequencies_21)
        Frequencies_21_data = imported_data.data['Frequencies_21']
        
        # Handle fill values for Frequencies_21
        fill_val = imported_data.data.get('Frequencies_21_FILLVAL', -1e+38)
        Frequencies_21_data = np.where(Frequencies_21_data == fill_val, np.nan, Frequencies_21_data)
        
        self.raw_data['Frequencies_21'] = Frequencies_21_data

        # Process En_fft (FFT of Compressional electric field)
        En_fft_data = imported_data.data['En_fft']
        
        # Handle fill values for En_fft
        fill_val = imported_data.data.get('En_fft_FILLVAL', -1e+38)
        En_fft_data = np.where(En_fft_data == fill_val, np.nan, En_fft_data)
        
        self.raw_data['En_fft'] = En_fft_data

        # Process FFT_time_23 (FFT_time_23)
        FFT_time_23_data = imported_data.data['FFT_time_23']
        
        # Handle fill values for FFT_time_23
        fill_val = imported_data.data.get('FFT_time_23_FILLVAL', -1e+38)
        FFT_time_23_data = np.where(FFT_time_23_data == fill_val, np.nan, FFT_time_23_data)
        
        self.raw_data['FFT_time_23'] = FFT_time_23_data

        # Process Frequencies_22 (Frequencies_22)
        Frequencies_22_data = imported_data.data['Frequencies_22']
        
        # Handle fill values for Frequencies_22
        fill_val = imported_data.data.get('Frequencies_22_FILLVAL', -1e+38)
        Frequencies_22_data = np.where(Frequencies_22_data == fill_val, np.nan, Frequencies_22_data)
        
        self.raw_data['Frequencies_22'] = Frequencies_22_data

        # Process Ep_fft (FFT of Transverse electric field in RTN_T direction)
        Ep_fft_data = imported_data.data['Ep_fft']
        
        # Handle fill values for Ep_fft
        fill_val = imported_data.data.get('Ep_fft_FILLVAL', -1e+38)
        Ep_fft_data = np.where(Ep_fft_data == fill_val, np.nan, Ep_fft_data)
        
        self.raw_data['Ep_fft'] = Ep_fft_data

        # Process FFT_time_24 (FFT_time_24)
        FFT_time_24_data = imported_data.data['FFT_time_24']
        
        # Handle fill values for FFT_time_24
        fill_val = imported_data.data.get('FFT_time_24_FILLVAL', -1e+38)
        FFT_time_24_data = np.where(FFT_time_24_data == fill_val, np.nan, FFT_time_24_data)
        
        self.raw_data['FFT_time_24'] = FFT_time_24_data

        # Process Frequencies_23 (Frequencies_23)
        Frequencies_23_data = imported_data.data['Frequencies_23']
        
        # Handle fill values for Frequencies_23
        fill_val = imported_data.data.get('Frequencies_23_FILLVAL', -1e+38)
        Frequencies_23_data = np.where(Frequencies_23_data == fill_val, np.nan, Frequencies_23_data)
        
        self.raw_data['Frequencies_23'] = Frequencies_23_data

        # Process Eq_fft (FFT of Transverse electric field in RTN_N direction)
        Eq_fft_data = imported_data.data['Eq_fft']
        
        # Handle fill values for Eq_fft
        fill_val = imported_data.data.get('Eq_fft_FILLVAL', -1e+38)
        Eq_fft_data = np.where(Eq_fft_data == fill_val, np.nan, Eq_fft_data)
        
        self.raw_data['Eq_fft'] = Eq_fft_data

        # Process FFT_time_25 (FFT_time_25)
        FFT_time_25_data = imported_data.data['FFT_time_25']
        
        # Handle fill values for FFT_time_25
        fill_val = imported_data.data.get('FFT_time_25_FILLVAL', -1e+38)
        FFT_time_25_data = np.where(FFT_time_25_data == fill_val, np.nan, FFT_time_25_data)
        
        self.raw_data['FFT_time_25'] = FFT_time_25_data

        # Process Frequencies_24 (Frequencies_24)
        Frequencies_24_data = imported_data.data['Frequencies_24']
        
        # Handle fill values for Frequencies_24
        fill_val = imported_data.data.get('Frequencies_24_FILLVAL', -1e+38)
        Frequencies_24_data = np.where(Frequencies_24_data == fill_val, np.nan, Frequencies_24_data)
        
        self.raw_data['Frequencies_24'] = Frequencies_24_data

        # Process kx_B (Wave Vector kx (Bfield))
        kx_B_data = imported_data.data['kx_B']
        
        # Handle fill values for kx_B
        fill_val = imported_data.data.get('kx_B_FILLVAL', -1e+38)
        kx_B_data = np.where(kx_B_data == fill_val, np.nan, kx_B_data)
        
        self.raw_data['kx_B'] = kx_B_data

        # Process FFT_time_26 (FFT_time_26)
        FFT_time_26_data = imported_data.data['FFT_time_26']
        
        # Handle fill values for FFT_time_26
        fill_val = imported_data.data.get('FFT_time_26_FILLVAL', -1e+38)
        FFT_time_26_data = np.where(FFT_time_26_data == fill_val, np.nan, FFT_time_26_data)
        
        self.raw_data['FFT_time_26'] = FFT_time_26_data

        # Process Frequencies_25 (Frequencies_25)
        Frequencies_25_data = imported_data.data['Frequencies_25']
        
        # Handle fill values for Frequencies_25
        fill_val = imported_data.data.get('Frequencies_25_FILLVAL', -1e+38)
        Frequencies_25_data = np.where(Frequencies_25_data == fill_val, np.nan, Frequencies_25_data)
        
        self.raw_data['Frequencies_25'] = Frequencies_25_data

        # Process ky_B (Wave Vector ky (Bfield))
        ky_B_data = imported_data.data['ky_B']
        
        # Handle fill values for ky_B
        fill_val = imported_data.data.get('ky_B_FILLVAL', -1e+38)
        ky_B_data = np.where(ky_B_data == fill_val, np.nan, ky_B_data)
        
        self.raw_data['ky_B'] = ky_B_data

        # Process FFT_time_27 (FFT_time_27)
        FFT_time_27_data = imported_data.data['FFT_time_27']
        
        # Handle fill values for FFT_time_27
        fill_val = imported_data.data.get('FFT_time_27_FILLVAL', -1e+38)
        FFT_time_27_data = np.where(FFT_time_27_data == fill_val, np.nan, FFT_time_27_data)
        
        self.raw_data['FFT_time_27'] = FFT_time_27_data

        # Process Frequencies_26 (Frequencies_26)
        Frequencies_26_data = imported_data.data['Frequencies_26']
        
        # Handle fill values for Frequencies_26
        fill_val = imported_data.data.get('Frequencies_26_FILLVAL', -1e+38)
        Frequencies_26_data = np.where(Frequencies_26_data == fill_val, np.nan, Frequencies_26_data)
        
        self.raw_data['Frequencies_26'] = Frequencies_26_data

        # Process kz_B (Wave Vector kz (Bfield))
        kz_B_data = imported_data.data['kz_B']
        
        # Handle fill values for kz_B
        fill_val = imported_data.data.get('kz_B_FILLVAL', -1e+38)
        kz_B_data = np.where(kz_B_data == fill_val, np.nan, kz_B_data)
        
        self.raw_data['kz_B'] = kz_B_data

        # Process FFT_time_28 (FFT_time_28)
        FFT_time_28_data = imported_data.data['FFT_time_28']
        
        # Handle fill values for FFT_time_28
        fill_val = imported_data.data.get('FFT_time_28_FILLVAL', -1e+38)
        FFT_time_28_data = np.where(FFT_time_28_data == fill_val, np.nan, FFT_time_28_data)
        
        self.raw_data['FFT_time_28'] = FFT_time_28_data

        # Process Frequencies_27 (Frequencies_27)
        Frequencies_27_data = imported_data.data['Frequencies_27']
        
        # Handle fill values for Frequencies_27
        fill_val = imported_data.data.get('Frequencies_27_FILLVAL', -1e+38)
        Frequencies_27_data = np.where(Frequencies_27_data == fill_val, np.nan, Frequencies_27_data)
        
        self.raw_data['Frequencies_27'] = Frequencies_27_data

        # Process kx_E (Wave Vector kx (Efield))
        kx_E_data = imported_data.data['kx_E']
        
        # Handle fill values for kx_E
        fill_val = imported_data.data.get('kx_E_FILLVAL', -1e+38)
        kx_E_data = np.where(kx_E_data == fill_val, np.nan, kx_E_data)
        
        self.raw_data['kx_E'] = kx_E_data

        # Process FFT_time_29 (FFT_time_29)
        FFT_time_29_data = imported_data.data['FFT_time_29']
        
        # Handle fill values for FFT_time_29
        fill_val = imported_data.data.get('FFT_time_29_FILLVAL', -1e+38)
        FFT_time_29_data = np.where(FFT_time_29_data == fill_val, np.nan, FFT_time_29_data)
        
        self.raw_data['FFT_time_29'] = FFT_time_29_data

        # Process Frequencies_28 (Frequencies_28)
        Frequencies_28_data = imported_data.data['Frequencies_28']
        
        # Handle fill values for Frequencies_28
        fill_val = imported_data.data.get('Frequencies_28_FILLVAL', -1e+38)
        Frequencies_28_data = np.where(Frequencies_28_data == fill_val, np.nan, Frequencies_28_data)
        
        self.raw_data['Frequencies_28'] = Frequencies_28_data

        # Process ky_E (Wave Vector ky (Efield))
        ky_E_data = imported_data.data['ky_E']
        
        # Handle fill values for ky_E
        fill_val = imported_data.data.get('ky_E_FILLVAL', -1e+38)
        ky_E_data = np.where(ky_E_data == fill_val, np.nan, ky_E_data)
        
        self.raw_data['ky_E'] = ky_E_data

        # Process FFT_time_30 (FFT_time_30)
        FFT_time_30_data = imported_data.data['FFT_time_30']
        
        # Handle fill values for FFT_time_30
        fill_val = imported_data.data.get('FFT_time_30_FILLVAL', -1e+38)
        FFT_time_30_data = np.where(FFT_time_30_data == fill_val, np.nan, FFT_time_30_data)
        
        self.raw_data['FFT_time_30'] = FFT_time_30_data

        # Process Frequencies_29 (Frequencies_29)
        Frequencies_29_data = imported_data.data['Frequencies_29']
        
        # Handle fill values for Frequencies_29
        fill_val = imported_data.data.get('Frequencies_29_FILLVAL', -1e+38)
        Frequencies_29_data = np.where(Frequencies_29_data == fill_val, np.nan, Frequencies_29_data)
        
        self.raw_data['Frequencies_29'] = Frequencies_29_data

        # Process kz_E (Wave Vector kz (Efield))
        kz_E_data = imported_data.data['kz_E']
        
        # Handle fill values for kz_E
        fill_val = imported_data.data.get('kz_E_FILLVAL', -1e+38)
        kz_E_data = np.where(kz_E_data == fill_val, np.nan, kz_E_data)
        
        self.raw_data['kz_E'] = kz_E_data
        
        # CREATE INDIVIDUAL MESHES FOR EACH 2D VARIABLE (mirror EPAD exactly)
        # Store meshes in a dictionary for easy access
        object.__setattr__(self, 'variable_meshes', {})
        
        print_manager.dependency_management("=== MESH CREATION DEBUG START ===")
        print_manager.dependency_management(f"datetime_array shape: {self.datetime_array.shape if self.datetime_array is not None else 'None'}")
        print_manager.dependency_management(f"datetime_array length: {len(self.datetime_array) if self.datetime_array is not None else 'None'}")
        
        # For each 2D variable, create its own mesh (just like EPAD does for strahl)
        spectral_variables = ['ellipticity_b', 'wave_normal_b', 'coherency_b', 'B_power_para', 'B_power_perp', 'Wave_Power_b', 'S_mag', 'S_Theta', 'S_Phi', 'Sn', 'Sp', 'Sq', 'Bn_fft', 'Bp_fft', 'Bq_fft', 'ellipticity_e', 'wave_normal_e', 'coherency_e', 'E_power_para', 'E_power_perp', 'Wave_Power_e', 'En_fft', 'Ep_fft', 'Eq_fft', 'kx_B', 'ky_B', 'kz_B', 'kx_E', 'ky_E', 'kz_E']
        print_manager.dependency_management(f"Spectral variables to process: {spectral_variables}")
        
        for var_name in spectral_variables:
            var_data = self.raw_data.get(var_name)
            if var_data is not None:
                print_manager.dependency_management(f"Processing {var_name}:")
                print_manager.dependency_management(f"  - Shape: {var_data.shape}")
                print_manager.dependency_management(f"  - ndim: {var_data.ndim}")
                
                if var_data.ndim >= 2:
                    print_manager.dependency_management(f"  - Creating mesh with time_len={len(self.datetime_array)}, freq_len={var_data.shape[1]}")
                    
                    # Create mesh for this specific variable (EXACTLY like EPAD)
                    try:
                        mesh_result = np.meshgrid(
                            self.datetime_array,
                            np.arange(var_data.shape[1]),  # Use actual data dimensions
                            indexing='ij'
                        )[0]
                        self.variable_meshes[var_name] = mesh_result
                        print_manager.dependency_management(f"  - SUCCESS: Created mesh shape {mesh_result.shape}")
                    except Exception as mesh_error:
                        print_manager.dependency_management(f"  - ERROR creating mesh: {mesh_error}")
                        self.variable_meshes[var_name] = self.datetime_array
                        print_manager.dependency_management(f"  - FALLBACK: Using datetime_array")
                else:
                    print_manager.dependency_management(f"  - SKIP: {var_name} is {var_data.ndim}D, not 2D+")
            else:
                print_manager.dependency_management(f"{var_name}: No data (None)")
        
        print_manager.dependency_management("=== MESH CREATION DEBUG END ===")

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
        print_manager.dependency_management("Setting up plot options for psp_waves_spectral variables")
        
        self.FFT_time_1 = plot_manager(
            self.raw_data['FFT_time_1'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_1',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_1',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_1 (ns)',
                legend_label='FFT_time_1',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies = plot_manager(
            self.raw_data['Frequencies'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up ellipticity_b (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: ellipticity_b ===")
        ellipticity_b_data = self.raw_data.get('ellipticity_b')
        ellipticity_b_mesh = self.variable_meshes.get('ellipticity_b', self.datetime_array)
        ellipticity_b_additional = self.raw_data.get('Frequencies', None)
        
        print_manager.dependency_management(f"  - Data shape: {ellipticity_b_data.shape if ellipticity_b_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {ellipticity_b_mesh.shape if hasattr(ellipticity_b_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {ellipticity_b_additional.shape if ellipticity_b_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(ellipticity_b_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if ellipticity_b_additional is not None and ellipticity_b_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            ellipticity_b_additional_2d = np.tile(ellipticity_b_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {ellipticity_b_additional.shape} to 2D {ellipticity_b_additional_2d.shape}")
            ellipticity_b_additional = ellipticity_b_additional_2d
        
        self.ellipticity_b = plot_manager(
            ellipticity_b_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='ellipticity_b',
                class_name='psp_waves_spectral',
                subclass_name='ellipticity_b',
                plot_type='spectral',
                datetime_array=ellipticity_b_mesh,
                y_label='ellipticity_b',
                legend_label='Ellipticity (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=ellipticity_b_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_2 = plot_manager(
            self.raw_data['FFT_time_2'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_2',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_2',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_2 (ns)',
                legend_label='FFT_time_2',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_1 = plot_manager(
            self.raw_data['Frequencies_1'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_1',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_1',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_1',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up wave_normal_b (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: wave_normal_b ===")
        wave_normal_b_data = self.raw_data.get('wave_normal_b')
        wave_normal_b_mesh = self.variable_meshes.get('wave_normal_b', self.datetime_array)
        wave_normal_b_additional = self.raw_data.get('Frequencies_1', None)
        
        print_manager.dependency_management(f"  - Data shape: {wave_normal_b_data.shape if wave_normal_b_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {wave_normal_b_mesh.shape if hasattr(wave_normal_b_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {wave_normal_b_additional.shape if wave_normal_b_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(wave_normal_b_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if wave_normal_b_additional is not None and wave_normal_b_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            wave_normal_b_additional_2d = np.tile(wave_normal_b_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {wave_normal_b_additional.shape} to 2D {wave_normal_b_additional_2d.shape}")
            wave_normal_b_additional = wave_normal_b_additional_2d
        
        self.wave_normal_b = plot_manager(
            wave_normal_b_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='wave_normal_b',
                class_name='psp_waves_spectral',
                subclass_name='wave_normal_b',
                plot_type='spectral',
                datetime_array=wave_normal_b_mesh,
                y_label='wave_normal_b (degrees)',
                legend_label='Wave Normal Angle (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=wave_normal_b_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label='degrees'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_3 = plot_manager(
            self.raw_data['FFT_time_3'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_3',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_3',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_3 (ns)',
                legend_label='FFT_time_3',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_2 = plot_manager(
            self.raw_data['Frequencies_2'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_2',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_2',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_2',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up coherency_b (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: coherency_b ===")
        coherency_b_data = self.raw_data.get('coherency_b')
        coherency_b_mesh = self.variable_meshes.get('coherency_b', self.datetime_array)
        coherency_b_additional = self.raw_data.get('Frequencies_2', None)
        
        print_manager.dependency_management(f"  - Data shape: {coherency_b_data.shape if coherency_b_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {coherency_b_mesh.shape if hasattr(coherency_b_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {coherency_b_additional.shape if coherency_b_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(coherency_b_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if coherency_b_additional is not None and coherency_b_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            coherency_b_additional_2d = np.tile(coherency_b_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {coherency_b_additional.shape} to 2D {coherency_b_additional_2d.shape}")
            coherency_b_additional = coherency_b_additional_2d
        
        self.coherency_b = plot_manager(
            coherency_b_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='coherency_b',
                class_name='psp_waves_spectral',
                subclass_name='coherency_b',
                plot_type='spectral',
                datetime_array=coherency_b_mesh,
                y_label='coherency_b',
                legend_label='Coherency (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=coherency_b_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_4 = plot_manager(
            self.raw_data['FFT_time_4'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_4',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_4',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_4 (ns)',
                legend_label='FFT_time_4',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_3 = plot_manager(
            self.raw_data['Frequencies_3'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_3',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_3',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_3',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up B_power_para (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: B_power_para ===")
        B_power_para_data = self.raw_data.get('B_power_para')
        B_power_para_mesh = self.variable_meshes.get('B_power_para', self.datetime_array)
        B_power_para_additional = self.raw_data.get('Frequencies_3', None)
        
        print_manager.dependency_management(f"  - Data shape: {B_power_para_data.shape if B_power_para_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {B_power_para_mesh.shape if hasattr(B_power_para_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {B_power_para_additional.shape if B_power_para_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(B_power_para_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if B_power_para_additional is not None and B_power_para_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            B_power_para_additional_2d = np.tile(B_power_para_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {B_power_para_additional.shape} to 2D {B_power_para_additional_2d.shape}")
            B_power_para_additional = B_power_para_additional_2d
        
        self.B_power_para = plot_manager(
            B_power_para_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='B_power_para',
                class_name='psp_waves_spectral',
                subclass_name='B_power_para',
                plot_type='spectral',
                datetime_array=B_power_para_mesh,
                y_label='B_power_para (nT$^2$/Hz)',
                legend_label='Bfield Power Compressional',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=B_power_para_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='nT$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_5 = plot_manager(
            self.raw_data['FFT_time_5'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_5',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_5',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_5 (ns)',
                legend_label='FFT_time_5',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_4 = plot_manager(
            self.raw_data['Frequencies_4'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_4',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_4',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_4',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up B_power_perp (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: B_power_perp ===")
        B_power_perp_data = self.raw_data.get('B_power_perp')
        B_power_perp_mesh = self.variable_meshes.get('B_power_perp', self.datetime_array)
        B_power_perp_additional = self.raw_data.get('Frequencies_4', None)
        
        print_manager.dependency_management(f"  - Data shape: {B_power_perp_data.shape if B_power_perp_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {B_power_perp_mesh.shape if hasattr(B_power_perp_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {B_power_perp_additional.shape if B_power_perp_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(B_power_perp_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if B_power_perp_additional is not None and B_power_perp_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            B_power_perp_additional_2d = np.tile(B_power_perp_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {B_power_perp_additional.shape} to 2D {B_power_perp_additional_2d.shape}")
            B_power_perp_additional = B_power_perp_additional_2d
        
        self.B_power_perp = plot_manager(
            B_power_perp_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='B_power_perp',
                class_name='psp_waves_spectral',
                subclass_name='B_power_perp',
                plot_type='spectral',
                datetime_array=B_power_perp_mesh,
                y_label='B_power_perp (nT$^2$/Hz)',
                legend_label='Bfield Power Transverse',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=B_power_perp_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='nT$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_6 = plot_manager(
            self.raw_data['FFT_time_6'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_6',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_6',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_6 (ns)',
                legend_label='FFT_time_6',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_5 = plot_manager(
            self.raw_data['Frequencies_5'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_5',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_5',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_5',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Wave_Power_b (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Wave_Power_b ===")
        Wave_Power_b_data = self.raw_data.get('Wave_Power_b')
        Wave_Power_b_mesh = self.variable_meshes.get('Wave_Power_b', self.datetime_array)
        Wave_Power_b_additional = self.raw_data.get('Frequencies_5', None)
        
        print_manager.dependency_management(f"  - Data shape: {Wave_Power_b_data.shape if Wave_Power_b_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Wave_Power_b_mesh.shape if hasattr(Wave_Power_b_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Wave_Power_b_additional.shape if Wave_Power_b_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Wave_Power_b_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Wave_Power_b_additional is not None and Wave_Power_b_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Wave_Power_b_additional_2d = np.tile(Wave_Power_b_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Wave_Power_b_additional.shape} to 2D {Wave_Power_b_additional_2d.shape}")
            Wave_Power_b_additional = Wave_Power_b_additional_2d
        
        self.Wave_Power_b = plot_manager(
            Wave_Power_b_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Wave_Power_b',
                class_name='psp_waves_spectral',
                subclass_name='Wave_Power_b',
                plot_type='spectral',
                datetime_array=Wave_Power_b_mesh,
                y_label='Wave_Power_b (nT$^2$/Hz)',
                legend_label='Bfield Power perpendicular to wave normal direction k',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Wave_Power_b_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='nT$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_7 = plot_manager(
            self.raw_data['FFT_time_7'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_7',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_7',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_7 (ns)',
                legend_label='FFT_time_7',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_6 = plot_manager(
            self.raw_data['Frequencies_6'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_6',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_6',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_6',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up S_mag (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: S_mag ===")
        S_mag_data = self.raw_data.get('S_mag')
        S_mag_mesh = self.variable_meshes.get('S_mag', self.datetime_array)
        S_mag_additional = self.raw_data.get('Frequencies_6', None)
        
        print_manager.dependency_management(f"  - Data shape: {S_mag_data.shape if S_mag_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {S_mag_mesh.shape if hasattr(S_mag_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {S_mag_additional.shape if S_mag_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(S_mag_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if S_mag_additional is not None and S_mag_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            S_mag_additional_2d = np.tile(S_mag_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {S_mag_additional.shape} to 2D {S_mag_additional_2d.shape}")
            S_mag_additional = S_mag_additional_2d
        
        self.S_mag = plot_manager(
            S_mag_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='S_mag',
                class_name='psp_waves_spectral',
                subclass_name='S_mag',
                plot_type='spectral',
                datetime_array=S_mag_mesh,
                y_label='S_mag (W/m$^{-2}$)',
                legend_label='Poynting Flux Magnitude',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=S_mag_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label='W/m$^{-2}$'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_8 = plot_manager(
            self.raw_data['FFT_time_8'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_8',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_8',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_8 (ns)',
                legend_label='FFT_time_8',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_7 = plot_manager(
            self.raw_data['Frequencies_7'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_7',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_7',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_7',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up S_Theta (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: S_Theta ===")
        S_Theta_data = self.raw_data.get('S_Theta')
        S_Theta_mesh = self.variable_meshes.get('S_Theta', self.datetime_array)
        S_Theta_additional = self.raw_data.get('Frequencies_7', None)
        
        print_manager.dependency_management(f"  - Data shape: {S_Theta_data.shape if S_Theta_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {S_Theta_mesh.shape if hasattr(S_Theta_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {S_Theta_additional.shape if S_Theta_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(S_Theta_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if S_Theta_additional is not None and S_Theta_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            S_Theta_additional_2d = np.tile(S_Theta_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {S_Theta_additional.shape} to 2D {S_Theta_additional_2d.shape}")
            S_Theta_additional = S_Theta_additional_2d
        
        self.S_Theta = plot_manager(
            S_Theta_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='S_Theta',
                class_name='psp_waves_spectral',
                subclass_name='S_Theta',
                plot_type='spectral',
                datetime_array=S_Theta_mesh,
                y_label='S_Theta',
                legend_label='Poynting Theta (S dot B)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=S_Theta_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_9 = plot_manager(
            self.raw_data['FFT_time_9'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_9',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_9',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_9 (ns)',
                legend_label='FFT_time_9',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_8 = plot_manager(
            self.raw_data['Frequencies_8'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_8',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_8',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_8',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up S_Phi (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: S_Phi ===")
        S_Phi_data = self.raw_data.get('S_Phi')
        S_Phi_mesh = self.variable_meshes.get('S_Phi', self.datetime_array)
        S_Phi_additional = self.raw_data.get('Frequencies_8', None)
        
        print_manager.dependency_management(f"  - Data shape: {S_Phi_data.shape if S_Phi_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {S_Phi_mesh.shape if hasattr(S_Phi_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {S_Phi_additional.shape if S_Phi_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(S_Phi_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if S_Phi_additional is not None and S_Phi_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            S_Phi_additional_2d = np.tile(S_Phi_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {S_Phi_additional.shape} to 2D {S_Phi_additional_2d.shape}")
            S_Phi_additional = S_Phi_additional_2d
        
        self.S_Phi = plot_manager(
            S_Phi_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='S_Phi',
                class_name='psp_waves_spectral',
                subclass_name='S_Phi',
                plot_type='spectral',
                datetime_array=S_Phi_mesh,
                y_label='S_Phi',
                legend_label='Poynting Phi (clock angle where 0=RTN_T and 90=RTN_N)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=S_Phi_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_10 = plot_manager(
            self.raw_data['FFT_time_10'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_10',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_10',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_10 (ns)',
                legend_label='FFT_time_10',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_9 = plot_manager(
            self.raw_data['Frequencies_9'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_9',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_9',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_9',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Sn (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Sn ===")
        Sn_data = self.raw_data.get('Sn')
        Sn_mesh = self.variable_meshes.get('Sn', self.datetime_array)
        Sn_additional = self.raw_data.get('Frequencies_9', None)
        
        print_manager.dependency_management(f"  - Data shape: {Sn_data.shape if Sn_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Sn_mesh.shape if hasattr(Sn_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Sn_additional.shape if Sn_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Sn_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Sn_additional is not None and Sn_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Sn_additional_2d = np.tile(Sn_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Sn_additional.shape} to 2D {Sn_additional_2d.shape}")
            Sn_additional = Sn_additional_2d
        
        self.Sn = plot_manager(
            Sn_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Sn',
                class_name='psp_waves_spectral',
                subclass_name='Sn',
                plot_type='spectral',
                datetime_array=Sn_mesh,
                y_label='Sn',
                legend_label='Poynting Flux Parallel (Field-oriented)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Sn_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_11 = plot_manager(
            self.raw_data['FFT_time_11'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_11',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_11',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_11 (ns)',
                legend_label='FFT_time_11',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_10 = plot_manager(
            self.raw_data['Frequencies_10'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_10',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_10',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_10',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Sp (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Sp ===")
        Sp_data = self.raw_data.get('Sp')
        Sp_mesh = self.variable_meshes.get('Sp', self.datetime_array)
        Sp_additional = self.raw_data.get('Frequencies_10', None)
        
        print_manager.dependency_management(f"  - Data shape: {Sp_data.shape if Sp_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Sp_mesh.shape if hasattr(Sp_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Sp_additional.shape if Sp_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Sp_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Sp_additional is not None and Sp_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Sp_additional_2d = np.tile(Sp_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Sp_additional.shape} to 2D {Sp_additional_2d.shape}")
            Sp_additional = Sp_additional_2d
        
        self.Sp = plot_manager(
            Sp_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Sp',
                class_name='psp_waves_spectral',
                subclass_name='Sp',
                plot_type='spectral',
                datetime_array=Sp_mesh,
                y_label='Sp',
                legend_label='Poynting Flux Perpendicular (approximately in RTN_T direction)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Sp_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_12 = plot_manager(
            self.raw_data['FFT_time_12'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_12',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_12',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_12 (ns)',
                legend_label='FFT_time_12',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_11 = plot_manager(
            self.raw_data['Frequencies_11'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_11',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_11',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_11',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Sq (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Sq ===")
        Sq_data = self.raw_data.get('Sq')
        Sq_mesh = self.variable_meshes.get('Sq', self.datetime_array)
        Sq_additional = self.raw_data.get('Frequencies_11', None)
        
        print_manager.dependency_management(f"  - Data shape: {Sq_data.shape if Sq_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Sq_mesh.shape if hasattr(Sq_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Sq_additional.shape if Sq_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Sq_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Sq_additional is not None and Sq_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Sq_additional_2d = np.tile(Sq_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Sq_additional.shape} to 2D {Sq_additional_2d.shape}")
            Sq_additional = Sq_additional_2d
        
        self.Sq = plot_manager(
            Sq_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Sq',
                class_name='psp_waves_spectral',
                subclass_name='Sq',
                plot_type='spectral',
                datetime_array=Sq_mesh,
                y_label='Sq',
                legend_label='Poynting Flux Perpendicular (approximately in RTN_N direction)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Sq_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.Bfield_time = plot_manager(
            self.raw_data['Bfield_time'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bfield_time',
                class_name='psp_waves_spectral',
                subclass_name='Bfield_time',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bfield_time (ns)',
                legend_label='Bfield_time',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bn = plot_manager(
            self.raw_data['Bn'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bn',
                class_name='psp_waves_spectral',
                subclass_name='Bn',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bn',
                legend_label='Parallel Magnetic Field Component (B!B||!N)',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bfield_time_1 = plot_manager(
            self.raw_data['Bfield_time_1'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bfield_time_1',
                class_name='psp_waves_spectral',
                subclass_name='Bfield_time_1',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bfield_time_1 (ns)',
                legend_label='Bfield_time_1',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bp = plot_manager(
            self.raw_data['Bp'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bp',
                class_name='psp_waves_spectral',
                subclass_name='Bp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bp',
                legend_label='Perpendicular Magnetic Field Component in Quasi-Tangential RTN Direction (B!B&perp;T!N)',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bfield_time_2 = plot_manager(
            self.raw_data['Bfield_time_2'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bfield_time_2',
                class_name='psp_waves_spectral',
                subclass_name='Bfield_time_2',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bfield_time_2 (ns)',
                legend_label='Bfield_time_2',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Bq = plot_manager(
            self.raw_data['Bq'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bq',
                class_name='psp_waves_spectral',
                subclass_name='Bq',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Bq (nT)',
                legend_label='Perpendicular Magnetic Field Component in Quasi-Normal RTN Direction (B!B&perp;N!N)',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.FFT_time_13 = plot_manager(
            self.raw_data['FFT_time_13'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_13',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_13',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_13 (ns)',
                legend_label='FFT_time_13',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_12 = plot_manager(
            self.raw_data['Frequencies_12'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_12',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_12',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_12',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Bn_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Bn_fft ===")
        Bn_fft_data = self.raw_data.get('Bn_fft')
        Bn_fft_mesh = self.variable_meshes.get('Bn_fft', self.datetime_array)
        Bn_fft_additional = self.raw_data.get('Frequencies_12', None)
        
        print_manager.dependency_management(f"  - Data shape: {Bn_fft_data.shape if Bn_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Bn_fft_mesh.shape if hasattr(Bn_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Bn_fft_additional.shape if Bn_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Bn_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Bn_fft_additional is not None and Bn_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Bn_fft_additional_2d = np.tile(Bn_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Bn_fft_additional.shape} to 2D {Bn_fft_additional_2d.shape}")
            Bn_fft_additional = Bn_fft_additional_2d
        
        self.Bn_fft = plot_manager(
            Bn_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bn_fft',
                class_name='psp_waves_spectral',
                subclass_name='Bn_fft',
                plot_type='spectral',
                datetime_array=Bn_fft_mesh,
                y_label='Bn_fft',
                legend_label='FFT of Compressional magnetic field',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Bn_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_14 = plot_manager(
            self.raw_data['FFT_time_14'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_14',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_14',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_14 (ns)',
                legend_label='FFT_time_14',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_13 = plot_manager(
            self.raw_data['Frequencies_13'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_13',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_13',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_13',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Bp_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Bp_fft ===")
        Bp_fft_data = self.raw_data.get('Bp_fft')
        Bp_fft_mesh = self.variable_meshes.get('Bp_fft', self.datetime_array)
        Bp_fft_additional = self.raw_data.get('Frequencies_13', None)
        
        print_manager.dependency_management(f"  - Data shape: {Bp_fft_data.shape if Bp_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Bp_fft_mesh.shape if hasattr(Bp_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Bp_fft_additional.shape if Bp_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Bp_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Bp_fft_additional is not None and Bp_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Bp_fft_additional_2d = np.tile(Bp_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Bp_fft_additional.shape} to 2D {Bp_fft_additional_2d.shape}")
            Bp_fft_additional = Bp_fft_additional_2d
        
        self.Bp_fft = plot_manager(
            Bp_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bp_fft',
                class_name='psp_waves_spectral',
                subclass_name='Bp_fft',
                plot_type='spectral',
                datetime_array=Bp_fft_mesh,
                y_label='Bp_fft',
                legend_label='FFT of Transverse magnetic field in RTN_T direction',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Bp_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_15 = plot_manager(
            self.raw_data['FFT_time_15'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_15',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_15',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_15 (ns)',
                legend_label='FFT_time_15',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_14 = plot_manager(
            self.raw_data['Frequencies_14'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_14',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_14',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_14',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Bq_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Bq_fft ===")
        Bq_fft_data = self.raw_data.get('Bq_fft')
        Bq_fft_mesh = self.variable_meshes.get('Bq_fft', self.datetime_array)
        Bq_fft_additional = self.raw_data.get('Frequencies_14', None)
        
        print_manager.dependency_management(f"  - Data shape: {Bq_fft_data.shape if Bq_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Bq_fft_mesh.shape if hasattr(Bq_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Bq_fft_additional.shape if Bq_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Bq_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Bq_fft_additional is not None and Bq_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Bq_fft_additional_2d = np.tile(Bq_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Bq_fft_additional.shape} to 2D {Bq_fft_additional_2d.shape}")
            Bq_fft_additional = Bq_fft_additional_2d
        
        self.Bq_fft = plot_manager(
            Bq_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Bq_fft',
                class_name='psp_waves_spectral',
                subclass_name='Bq_fft',
                plot_type='spectral',
                datetime_array=Bq_fft_mesh,
                y_label='Bq_fft',
                legend_label='FFT of Transverse magnetic field in RTN_N direction',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Bq_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_16 = plot_manager(
            self.raw_data['FFT_time_16'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_16',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_16',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_16 (ns)',
                legend_label='FFT_time_16',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_15 = plot_manager(
            self.raw_data['Frequencies_15'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_15',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_15',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_15',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up ellipticity_e (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: ellipticity_e ===")
        ellipticity_e_data = self.raw_data.get('ellipticity_e')
        ellipticity_e_mesh = self.variable_meshes.get('ellipticity_e', self.datetime_array)
        ellipticity_e_additional = self.raw_data.get('Frequencies_15', None)
        
        print_manager.dependency_management(f"  - Data shape: {ellipticity_e_data.shape if ellipticity_e_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {ellipticity_e_mesh.shape if hasattr(ellipticity_e_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {ellipticity_e_additional.shape if ellipticity_e_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(ellipticity_e_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if ellipticity_e_additional is not None and ellipticity_e_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            ellipticity_e_additional_2d = np.tile(ellipticity_e_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {ellipticity_e_additional.shape} to 2D {ellipticity_e_additional_2d.shape}")
            ellipticity_e_additional = ellipticity_e_additional_2d
        
        self.ellipticity_e = plot_manager(
            ellipticity_e_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='ellipticity_e',
                class_name='psp_waves_spectral',
                subclass_name='ellipticity_e',
                plot_type='spectral',
                datetime_array=ellipticity_e_mesh,
                y_label='ellipticity_e',
                legend_label='Ellipticity (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=ellipticity_e_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_17 = plot_manager(
            self.raw_data['FFT_time_17'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_17',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_17',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_17 (ns)',
                legend_label='FFT_time_17',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_16 = plot_manager(
            self.raw_data['Frequencies_16'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_16',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_16',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_16',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up wave_normal_e (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: wave_normal_e ===")
        wave_normal_e_data = self.raw_data.get('wave_normal_e')
        wave_normal_e_mesh = self.variable_meshes.get('wave_normal_e', self.datetime_array)
        wave_normal_e_additional = self.raw_data.get('Frequencies_16', None)
        
        print_manager.dependency_management(f"  - Data shape: {wave_normal_e_data.shape if wave_normal_e_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {wave_normal_e_mesh.shape if hasattr(wave_normal_e_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {wave_normal_e_additional.shape if wave_normal_e_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(wave_normal_e_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if wave_normal_e_additional is not None and wave_normal_e_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            wave_normal_e_additional_2d = np.tile(wave_normal_e_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {wave_normal_e_additional.shape} to 2D {wave_normal_e_additional_2d.shape}")
            wave_normal_e_additional = wave_normal_e_additional_2d
        
        self.wave_normal_e = plot_manager(
            wave_normal_e_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='wave_normal_e',
                class_name='psp_waves_spectral',
                subclass_name='wave_normal_e',
                plot_type='spectral',
                datetime_array=wave_normal_e_mesh,
                y_label='wave_normal_e (degrees)',
                legend_label='Wave Normal Angle (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=wave_normal_e_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label='degrees'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_18 = plot_manager(
            self.raw_data['FFT_time_18'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_18',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_18',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_18 (ns)',
                legend_label='FFT_time_18',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_17 = plot_manager(
            self.raw_data['Frequencies_17'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_17',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_17',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_17',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up coherency_e (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: coherency_e ===")
        coherency_e_data = self.raw_data.get('coherency_e')
        coherency_e_mesh = self.variable_meshes.get('coherency_e', self.datetime_array)
        coherency_e_additional = self.raw_data.get('Frequencies_17', None)
        
        print_manager.dependency_management(f"  - Data shape: {coherency_e_data.shape if coherency_e_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {coherency_e_mesh.shape if hasattr(coherency_e_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {coherency_e_additional.shape if coherency_e_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(coherency_e_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if coherency_e_additional is not None and coherency_e_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            coherency_e_additional_2d = np.tile(coherency_e_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {coherency_e_additional.shape} to 2D {coherency_e_additional_2d.shape}")
            coherency_e_additional = coherency_e_additional_2d
        
        self.coherency_e = plot_manager(
            coherency_e_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='coherency_e',
                class_name='psp_waves_spectral',
                subclass_name='coherency_e',
                plot_type='spectral',
                datetime_array=coherency_e_mesh,
                y_label='coherency_e',
                legend_label='Coherency (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=coherency_e_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_19 = plot_manager(
            self.raw_data['FFT_time_19'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_19',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_19',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_19 (ns)',
                legend_label='FFT_time_19',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_18 = plot_manager(
            self.raw_data['Frequencies_18'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_18',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_18',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_18',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up E_power_para (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: E_power_para ===")
        E_power_para_data = self.raw_data.get('E_power_para')
        E_power_para_mesh = self.variable_meshes.get('E_power_para', self.datetime_array)
        E_power_para_additional = self.raw_data.get('Frequencies_18', None)
        
        print_manager.dependency_management(f"  - Data shape: {E_power_para_data.shape if E_power_para_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {E_power_para_mesh.shape if hasattr(E_power_para_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {E_power_para_additional.shape if E_power_para_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(E_power_para_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if E_power_para_additional is not None and E_power_para_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            E_power_para_additional_2d = np.tile(E_power_para_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {E_power_para_additional.shape} to 2D {E_power_para_additional_2d.shape}")
            E_power_para_additional = E_power_para_additional_2d
        
        self.E_power_para = plot_manager(
            E_power_para_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='E_power_para',
                class_name='psp_waves_spectral',
                subclass_name='E_power_para',
                plot_type='spectral',
                datetime_array=E_power_para_mesh,
                y_label='E_power_para (mV$^2$/m$^2$/Hz)',
                legend_label='Efield Power Compressional',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=E_power_para_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='mV$^2$/m$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_20 = plot_manager(
            self.raw_data['FFT_time_20'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_20',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_20',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_20 (ns)',
                legend_label='FFT_time_20',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_19 = plot_manager(
            self.raw_data['Frequencies_19'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_19',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_19',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_19',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up E_power_perp (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: E_power_perp ===")
        E_power_perp_data = self.raw_data.get('E_power_perp')
        E_power_perp_mesh = self.variable_meshes.get('E_power_perp', self.datetime_array)
        E_power_perp_additional = self.raw_data.get('Frequencies_19', None)
        
        print_manager.dependency_management(f"  - Data shape: {E_power_perp_data.shape if E_power_perp_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {E_power_perp_mesh.shape if hasattr(E_power_perp_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {E_power_perp_additional.shape if E_power_perp_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(E_power_perp_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if E_power_perp_additional is not None and E_power_perp_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            E_power_perp_additional_2d = np.tile(E_power_perp_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {E_power_perp_additional.shape} to 2D {E_power_perp_additional_2d.shape}")
            E_power_perp_additional = E_power_perp_additional_2d
        
        self.E_power_perp = plot_manager(
            E_power_perp_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='E_power_perp',
                class_name='psp_waves_spectral',
                subclass_name='E_power_perp',
                plot_type='spectral',
                datetime_array=E_power_perp_mesh,
                y_label='E_power_perp (mV$^2$/m$^2$/Hz)',
                legend_label='Efield Power Transverse',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=E_power_perp_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='mV$^2$/m$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_21 = plot_manager(
            self.raw_data['FFT_time_21'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_21',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_21',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_21 (ns)',
                legend_label='FFT_time_21',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_20 = plot_manager(
            self.raw_data['Frequencies_20'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_20',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_20',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_20',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Wave_Power_e (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Wave_Power_e ===")
        Wave_Power_e_data = self.raw_data.get('Wave_Power_e')
        Wave_Power_e_mesh = self.variable_meshes.get('Wave_Power_e', self.datetime_array)
        Wave_Power_e_additional = self.raw_data.get('Frequencies_20', None)
        
        print_manager.dependency_management(f"  - Data shape: {Wave_Power_e_data.shape if Wave_Power_e_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Wave_Power_e_mesh.shape if hasattr(Wave_Power_e_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Wave_Power_e_additional.shape if Wave_Power_e_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Wave_Power_e_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Wave_Power_e_additional is not None and Wave_Power_e_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Wave_Power_e_additional_2d = np.tile(Wave_Power_e_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Wave_Power_e_additional.shape} to 2D {Wave_Power_e_additional_2d.shape}")
            Wave_Power_e_additional = Wave_Power_e_additional_2d
        
        self.Wave_Power_e = plot_manager(
            Wave_Power_e_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Wave_Power_e',
                class_name='psp_waves_spectral',
                subclass_name='Wave_Power_e',
                plot_type='spectral',
                datetime_array=Wave_Power_e_mesh,
                y_label='Wave_Power_e (mV$^2$/m$^2$/Hz)',
                legend_label='Efield Power perpendicular to wave normal direction k',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Wave_Power_e_additional,
                colormap='turbo',
                colorbar_scale='log',
                colorbar_limits=None,
                colorbar_label='mV$^2$/m$^2$/Hz'
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_22 = plot_manager(
            self.raw_data['FFT_time_22'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_22',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_22',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_22 (ns)',
                legend_label='FFT_time_22',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_21 = plot_manager(
            self.raw_data['Frequencies_21'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_21',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_21',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_21',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up En_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: En_fft ===")
        En_fft_data = self.raw_data.get('En_fft')
        En_fft_mesh = self.variable_meshes.get('En_fft', self.datetime_array)
        En_fft_additional = self.raw_data.get('Frequencies_21', None)
        
        print_manager.dependency_management(f"  - Data shape: {En_fft_data.shape if En_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {En_fft_mesh.shape if hasattr(En_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {En_fft_additional.shape if En_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(En_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if En_fft_additional is not None and En_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            En_fft_additional_2d = np.tile(En_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {En_fft_additional.shape} to 2D {En_fft_additional_2d.shape}")
            En_fft_additional = En_fft_additional_2d
        
        self.En_fft = plot_manager(
            En_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='En_fft',
                class_name='psp_waves_spectral',
                subclass_name='En_fft',
                plot_type='spectral',
                datetime_array=En_fft_mesh,
                y_label='En_fft',
                legend_label='FFT of Compressional electric field',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=En_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_23 = plot_manager(
            self.raw_data['FFT_time_23'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_23',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_23',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_23 (ns)',
                legend_label='FFT_time_23',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_22 = plot_manager(
            self.raw_data['Frequencies_22'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_22',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_22',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_22',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Ep_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Ep_fft ===")
        Ep_fft_data = self.raw_data.get('Ep_fft')
        Ep_fft_mesh = self.variable_meshes.get('Ep_fft', self.datetime_array)
        Ep_fft_additional = self.raw_data.get('Frequencies_22', None)
        
        print_manager.dependency_management(f"  - Data shape: {Ep_fft_data.shape if Ep_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Ep_fft_mesh.shape if hasattr(Ep_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Ep_fft_additional.shape if Ep_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Ep_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Ep_fft_additional is not None and Ep_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Ep_fft_additional_2d = np.tile(Ep_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Ep_fft_additional.shape} to 2D {Ep_fft_additional_2d.shape}")
            Ep_fft_additional = Ep_fft_additional_2d
        
        self.Ep_fft = plot_manager(
            Ep_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Ep_fft',
                class_name='psp_waves_spectral',
                subclass_name='Ep_fft',
                plot_type='spectral',
                datetime_array=Ep_fft_mesh,
                y_label='Ep_fft',
                legend_label='FFT of Transverse electric field in RTN_T direction',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Ep_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_24 = plot_manager(
            self.raw_data['FFT_time_24'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_24',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_24',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_24 (ns)',
                legend_label='FFT_time_24',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_23 = plot_manager(
            self.raw_data['Frequencies_23'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_23',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_23',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_23',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up Eq_fft (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: Eq_fft ===")
        Eq_fft_data = self.raw_data.get('Eq_fft')
        Eq_fft_mesh = self.variable_meshes.get('Eq_fft', self.datetime_array)
        Eq_fft_additional = self.raw_data.get('Frequencies_23', None)
        
        print_manager.dependency_management(f"  - Data shape: {Eq_fft_data.shape if Eq_fft_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {Eq_fft_mesh.shape if hasattr(Eq_fft_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {Eq_fft_additional.shape if Eq_fft_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(Eq_fft_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if Eq_fft_additional is not None and Eq_fft_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            Eq_fft_additional_2d = np.tile(Eq_fft_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {Eq_fft_additional.shape} to 2D {Eq_fft_additional_2d.shape}")
            Eq_fft_additional = Eq_fft_additional_2d
        
        self.Eq_fft = plot_manager(
            Eq_fft_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Eq_fft',
                class_name='psp_waves_spectral',
                subclass_name='Eq_fft',
                plot_type='spectral',
                datetime_array=Eq_fft_mesh,
                y_label='Eq_fft',
                legend_label='FFT of Transverse electric field in RTN_N direction',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=Eq_fft_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_25 = plot_manager(
            self.raw_data['FFT_time_25'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_25',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_25',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_25 (ns)',
                legend_label='FFT_time_25',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_24 = plot_manager(
            self.raw_data['Frequencies_24'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_24',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_24',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_24',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up kx_B (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: kx_B ===")
        kx_B_data = self.raw_data.get('kx_B')
        kx_B_mesh = self.variable_meshes.get('kx_B', self.datetime_array)
        kx_B_additional = self.raw_data.get('Frequencies_24', None)
        
        print_manager.dependency_management(f"  - Data shape: {kx_B_data.shape if kx_B_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {kx_B_mesh.shape if hasattr(kx_B_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {kx_B_additional.shape if kx_B_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(kx_B_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if kx_B_additional is not None and kx_B_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            kx_B_additional_2d = np.tile(kx_B_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {kx_B_additional.shape} to 2D {kx_B_additional_2d.shape}")
            kx_B_additional = kx_B_additional_2d
        
        self.kx_B = plot_manager(
            kx_B_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='kx_B',
                class_name='psp_waves_spectral',
                subclass_name='kx_B',
                plot_type='spectral',
                datetime_array=kx_B_mesh,
                y_label='kx_B',
                legend_label='Wave Vector kx (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=kx_B_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_26 = plot_manager(
            self.raw_data['FFT_time_26'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_26',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_26',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_26 (ns)',
                legend_label='FFT_time_26',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_25 = plot_manager(
            self.raw_data['Frequencies_25'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_25',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_25',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_25',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up ky_B (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: ky_B ===")
        ky_B_data = self.raw_data.get('ky_B')
        ky_B_mesh = self.variable_meshes.get('ky_B', self.datetime_array)
        ky_B_additional = self.raw_data.get('Frequencies_25', None)
        
        print_manager.dependency_management(f"  - Data shape: {ky_B_data.shape if ky_B_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {ky_B_mesh.shape if hasattr(ky_B_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {ky_B_additional.shape if ky_B_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(ky_B_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if ky_B_additional is not None and ky_B_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            ky_B_additional_2d = np.tile(ky_B_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {ky_B_additional.shape} to 2D {ky_B_additional_2d.shape}")
            ky_B_additional = ky_B_additional_2d
        
        self.ky_B = plot_manager(
            ky_B_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='ky_B',
                class_name='psp_waves_spectral',
                subclass_name='ky_B',
                plot_type='spectral',
                datetime_array=ky_B_mesh,
                y_label='ky_B',
                legend_label='Wave Vector ky (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=ky_B_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_27 = plot_manager(
            self.raw_data['FFT_time_27'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_27',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_27',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_27 (ns)',
                legend_label='FFT_time_27',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_26 = plot_manager(
            self.raw_data['Frequencies_26'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_26',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_26',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_26',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up kz_B (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: kz_B ===")
        kz_B_data = self.raw_data.get('kz_B')
        kz_B_mesh = self.variable_meshes.get('kz_B', self.datetime_array)
        kz_B_additional = self.raw_data.get('Frequencies_26', None)
        
        print_manager.dependency_management(f"  - Data shape: {kz_B_data.shape if kz_B_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {kz_B_mesh.shape if hasattr(kz_B_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {kz_B_additional.shape if kz_B_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(kz_B_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if kz_B_additional is not None and kz_B_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            kz_B_additional_2d = np.tile(kz_B_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {kz_B_additional.shape} to 2D {kz_B_additional_2d.shape}")
            kz_B_additional = kz_B_additional_2d
        
        self.kz_B = plot_manager(
            kz_B_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='kz_B',
                class_name='psp_waves_spectral',
                subclass_name='kz_B',
                plot_type='spectral',
                datetime_array=kz_B_mesh,
                y_label='kz_B',
                legend_label='Wave Vector kz (Bfield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=kz_B_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_28 = plot_manager(
            self.raw_data['FFT_time_28'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_28',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_28',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_28 (ns)',
                legend_label='FFT_time_28',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_27 = plot_manager(
            self.raw_data['Frequencies_27'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_27',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_27',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_27',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up kx_E (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: kx_E ===")
        kx_E_data = self.raw_data.get('kx_E')
        kx_E_mesh = self.variable_meshes.get('kx_E', self.datetime_array)
        kx_E_additional = self.raw_data.get('Frequencies_27', None)
        
        print_manager.dependency_management(f"  - Data shape: {kx_E_data.shape if kx_E_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {kx_E_mesh.shape if hasattr(kx_E_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {kx_E_additional.shape if kx_E_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(kx_E_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if kx_E_additional is not None and kx_E_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            kx_E_additional_2d = np.tile(kx_E_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {kx_E_additional.shape} to 2D {kx_E_additional_2d.shape}")
            kx_E_additional = kx_E_additional_2d
        
        self.kx_E = plot_manager(
            kx_E_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='kx_E',
                class_name='psp_waves_spectral',
                subclass_name='kx_E',
                plot_type='spectral',
                datetime_array=kx_E_mesh,
                y_label='kx_E',
                legend_label='Wave Vector kx (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=kx_E_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_29 = plot_manager(
            self.raw_data['FFT_time_29'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_29',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_29',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_29 (ns)',
                legend_label='FFT_time_29',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_28 = plot_manager(
            self.raw_data['Frequencies_28'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_28',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_28',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_28',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up ky_E (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: ky_E ===")
        ky_E_data = self.raw_data.get('ky_E')
        ky_E_mesh = self.variable_meshes.get('ky_E', self.datetime_array)
        ky_E_additional = self.raw_data.get('Frequencies_28', None)
        
        print_manager.dependency_management(f"  - Data shape: {ky_E_data.shape if ky_E_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {ky_E_mesh.shape if hasattr(ky_E_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {ky_E_additional.shape if ky_E_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(ky_E_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if ky_E_additional is not None and ky_E_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            ky_E_additional_2d = np.tile(ky_E_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {ky_E_additional.shape} to 2D {ky_E_additional_2d.shape}")
            ky_E_additional = ky_E_additional_2d
        
        self.ky_E = plot_manager(
            ky_E_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='ky_E',
                class_name='psp_waves_spectral',
                subclass_name='ky_E',
                plot_type='spectral',
                datetime_array=ky_E_mesh,
                y_label='ky_E',
                legend_label='Wave Vector ky (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=ky_E_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")

        self.FFT_time_30 = plot_manager(
            self.raw_data['FFT_time_30'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='FFT_time_30',
                class_name='psp_waves_spectral',
                subclass_name='FFT_time_30',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='FFT_time_30 (ns)',
                legend_label='FFT_time_30',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        self.Frequencies_29 = plot_manager(
            self.raw_data['Frequencies_29'],
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='Frequencies_29',
                class_name='psp_waves_spectral',
                subclass_name='Frequencies_29',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Frequency (Hz)',
                legend_label='Frequencies_29',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        # DEBUG: Setting up kz_E (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: kz_E ===")
        kz_E_data = self.raw_data.get('kz_E')
        kz_E_mesh = self.variable_meshes.get('kz_E', self.datetime_array)
        kz_E_additional = self.raw_data.get('Frequencies_29', None)
        
        print_manager.dependency_management(f"  - Data shape: {kz_E_data.shape if kz_E_data is not None else 'None'}")
        print_manager.dependency_management(f"  - Mesh shape: {kz_E_mesh.shape if hasattr(kz_E_mesh, 'shape') else 'No shape attr'}")
        print_manager.dependency_management(f"  - Additional data shape: {kz_E_additional.shape if kz_E_additional is not None else 'None'}")
        print_manager.dependency_management(f"  - Additional data type: {type(kz_E_additional)}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if kz_E_additional is not None and kz_E_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            kz_E_additional_2d = np.tile(kz_E_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {kz_E_additional.shape} to 2D {kz_E_additional_2d.shape}")
            kz_E_additional = kz_E_additional_2d
        
        self.kz_E = plot_manager(
            kz_E_data,
            plot_options=ploptions(
                data_type='psp_waves_spectral',
                var_name='kz_E',
                class_name='psp_waves_spectral',
                subclass_name='kz_E',
                plot_type='spectral',
                datetime_array=kz_E_mesh,
                y_label='kz_E',
                legend_label='Wave Vector kz (Efield)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=kz_E_additional,
                colormap='turbo',
                colorbar_scale='linear',
                colorbar_limits=None,
                colorbar_label=None
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")


    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

# Initialize the class with no data
psp_waves_spectral = psp_waves_spectral_class(None)
print_manager.dependency_management(f'initialized psp_waves_spectral class')
