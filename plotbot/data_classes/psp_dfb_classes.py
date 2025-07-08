# plotbot/data_classes/psp_dfb_classes.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
from typing import Optional, List

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

class psp_dfb_class:
    """PSP FIELDS Digital Fields Board (DFB) electric field spectra data."""
    
    def __init__(self, imported_data):
        # Initialize basic attributes following wind_3dp/wind_mfi patterns
        object.__setattr__(self, 'class_name', 'psp_dfb')
        object.__setattr__(self, 'data_type', 'dfb_ac_spec_dv12hg')  # Primary data type 
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
            'ac_spec_dv12': None,         # AC spectrum dv12
            'ac_spec_dv34': None,         # AC spectrum dv34
            'dc_spec_dv12': None,         # DC spectrum dv12 (only available)
            'ac_freq_bins_dv12': None,    # Frequency bins for AC dv12
            'ac_freq_bins_dv34': None,    # Frequency bins for AC dv34  
            'dc_freq_bins_dv12': None,    # Frequency bins for DC dv12
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh_ac_dv12', None)  # For spectral plotting
        object.__setattr__(self, 'times_mesh_ac_dv34', None)
        object.__setattr__(self, 'times_mesh_dc_dv12', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_ploptions()
            print_manager.debug("No DFB data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.debug("Calculating DFB electric field spectra variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated DFB electric field spectra variables.")

    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Update the DFB data with new imported data and dependency management."""
        # Store the original requested trange for dependency management
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        
        if imported_data is not None:
            print_manager.debug("Updating DFB electric field spectra variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully updated DFB electric field spectra variables.")
        else:
            print_manager.warning("No DFB data provided for update.")

    def calculate_variables(self, imported_data):
        """Calculate and store DFB spectral variables following EPAD pattern"""
        print_manager.processing(f"[DFB_CALC_VARS ENTRY] id(self): {id(self)}")
        
        # Store TT2000 times as numpy array (EPAD pattern)
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        print_manager.processing(f"[DFB_CALC_VARS] self.datetime_array (id: {id(self.datetime_array)}) len: {len(self.datetime_array) if self.datetime_array is not None else 'None'}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}" if self.datetime_array is not None and len(self.datetime_array) > 0 else "[DFB_CALC_VARS] self.datetime_array is empty/None")

        # Extract and process AC dv12 data if present
        ac_vals_dv12 = imported_data.data.get('psp_fld_l2_dfb_ac_spec_dV12hg')
        ac_freq_vals_dv12 = imported_data.data.get('psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins')
        
        if ac_vals_dv12 is not None:
            # Convert to log scale (following EPAD pattern)
            ac_vals_dv12 = np.where(ac_vals_dv12 == 0, 1e-10, ac_vals_dv12)
            log_ac_vals_dv12 = np.log10(ac_vals_dv12)
            
            # Create times_mesh for spectral plotting (EXACT EPAD pattern)
            self.times_mesh_ac_dv12 = np.meshgrid(
                self.datetime_array,
                np.arange(log_ac_vals_dv12.shape[1]),
                indexing='ij'
            )[0]
            
            # Store spectral data in raw_data
            self.raw_data['ac_spec_dv12'] = log_ac_vals_dv12
            
            # Store frequency bins as 2D array (EXACT EPAD PATTERN)
            # Repeat frequency bins for each time step, just like EPAD does with pitch angles
            freq_bins_1d = ac_freq_vals_dv12[0,:]  # Get first row (all rows are identical)
            freq_bins_2d = np.tile(freq_bins_1d, (len(self.datetime_array), 1))  # Repeat for each time step
            self.raw_data['ac_freq_bins_dv12'] = freq_bins_2d
            
            print_manager.processing(f"[DFB_CALC_VARS] AC dv12: stored spectral data {log_ac_vals_dv12.shape} and frequency bins {freq_bins_2d.shape}")

        # Extract and process AC dv34 data if present
        ac_vals_dv34 = imported_data.data.get('psp_fld_l2_dfb_ac_spec_dV34hg')
        ac_freq_vals_dv34 = imported_data.data.get('psp_fld_l2_dfb_ac_spec_dV34hg_frequency_bins')
        
        if ac_vals_dv34 is not None:
            ac_vals_dv34 = np.where(ac_vals_dv34 == 0, 1e-10, ac_vals_dv34)
            log_ac_vals_dv34 = np.log10(ac_vals_dv34)
            
            self.times_mesh_ac_dv34 = np.meshgrid(
                self.datetime_array,
                np.arange(log_ac_vals_dv34.shape[1]),
                indexing='ij'
            )[0]
            
            self.raw_data['ac_spec_dv34'] = log_ac_vals_dv34
            
            # Store frequency bins as 2D array (EXACT EPAD PATTERN)
            freq_bins_1d = ac_freq_vals_dv34[0,:]  # Get first row (all rows are identical)
            freq_bins_2d = np.tile(freq_bins_1d, (len(self.datetime_array), 1))  # Repeat for each time step
            self.raw_data['ac_freq_bins_dv34'] = freq_bins_2d
            
            print_manager.processing(f"[DFB_CALC_VARS] AC dv34: stored spectral data {log_ac_vals_dv34.shape} and frequency bins {freq_bins_2d.shape}")

        # Extract and process DC dv12 data if present
        dc_vals_dv12 = imported_data.data.get('psp_fld_l2_dfb_dc_spec_dV12hg')
        dc_freq_vals_dv12 = imported_data.data.get('psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins')
        
        if dc_vals_dv12 is not None:
            dc_vals_dv12 = np.where(dc_vals_dv12 == 0, 1e-10, dc_vals_dv12)
            log_dc_vals_dv12 = np.log10(dc_vals_dv12)
            
            self.times_mesh_dc_dv12 = np.meshgrid(
                self.datetime_array,
                np.arange(log_dc_vals_dv12.shape[1]),
                indexing='ij'
            )[0]
            
            self.raw_data['dc_spec_dv12'] = log_dc_vals_dv12
            
            # Store frequency bins as 2D array (EXACT EPAD PATTERN)
            freq_bins_1d = dc_freq_vals_dv12[0,:]  # Get first row (all rows are identical)
            freq_bins_2d = np.tile(freq_bins_1d, (len(self.datetime_array), 1))  # Repeat for each time step
            self.raw_data['dc_freq_bins_dv12'] = freq_bins_2d
            
            print_manager.processing(f"[DFB_CALC_VARS] DC dv12: stored spectral data {log_dc_vals_dv12.shape} and frequency bins {freq_bins_2d.shape}")

        # Set default None values for missing data types (only for spectral data, not frequency bins)
        if ac_vals_dv12 is None:
            self.raw_data['ac_spec_dv12'] = None
            self.ac_freq_bins_dv12 = None
        if ac_vals_dv34 is None:
            self.raw_data['ac_spec_dv34'] = None
            self.ac_freq_bins_dv34 = None
        if dc_vals_dv12 is None:
            self.raw_data['dc_spec_dv12'] = None
            self.dc_freq_bins_dv12 = None

        if ac_vals_dv12 is None and ac_vals_dv34 is None and dc_vals_dv12 is None:
            print_manager.processing("No DFB data provided; initialized with empty attributes.")

    def set_ploptions(self):
        """Set up plotting options for DFB spectral data following EPAD pattern"""
        print_manager.processing(f"[DFB_SET_PLOPT ENTRY] id(self): {id(self)}")
        
        # Always create plot_manager instances, even if no data (following EPAD pattern)
        
        # AC dv12 spectrum
        datetime_array = getattr(self, 'times_mesh_ac_dv12', self.datetime_array)
        ac_data = self.raw_data.get('ac_spec_dv12', None)
        self.ac_spec_dv12 = plot_manager(
            ac_data,
            plot_options=ploptions(
                data_type='dfb_ac_spec_dv12hg',
                var_name='ac_spec_dv12',
                class_name='psp_dfb',
                subclass_name='ac_spec_dv12',
                plot_type='spectral',
                datetime_array=datetime_array,  # Use times_mesh like EPAD
                y_label='Frequency (Hz)',
                legend_label='AC Spectrum dV12',
                color=None,
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data.get('ac_freq_bins_dv12', None),  # Use 2D frequency bins from raw_data
            )
        )

        # AC dv34 spectrum
        datetime_array = getattr(self, 'times_mesh_ac_dv34', self.datetime_array)
        ac_data = self.raw_data.get('ac_spec_dv34', None)
        self.ac_spec_dv34 = plot_manager(
            ac_data,
            plot_options=ploptions(
                data_type='dfb_ac_spec_dv34hg',
                var_name='ac_spec_dv34',
                class_name='psp_dfb',
                subclass_name='ac_spec_dv34',
                plot_type='spectral',
                datetime_array=datetime_array,  # Use times_mesh like EPAD
                y_label='Frequency (Hz)',
                legend_label='AC Spectrum dV34',
                color=None,
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data.get('ac_freq_bins_dv34', None),  # Use 2D frequency bins from raw_data
            )
        )

        # DC dv12 spectrum
        datetime_array = getattr(self, 'times_mesh_dc_dv12', self.datetime_array)
        dc_data = self.raw_data.get('dc_spec_dv12', None)
        self.dc_spec_dv12 = plot_manager(
            dc_data,
            plot_options=ploptions(
                data_type='dfb_dc_spec_dv12hg',
                var_name='dc_spec_dv12',
                class_name='psp_dfb',
                subclass_name='dc_spec_dv12',
                plot_type='spectral',
                datetime_array=datetime_array,  # Use times_mesh like EPAD
                y_label='Frequency (Hz)',
                legend_label='DC Spectrum dV12',
                color=None,
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data.get('dc_freq_bins_dv12', None),  # Use 2D frequency bins from raw_data
            )
        )

        print_manager.processing(f"[DFB_SET_PLOPT] Plot managers created for all DFB variables")

    def get_subclass(self, subclass_name):
        """Get a specific subclass by name."""
        if hasattr(self, subclass_name):
            return getattr(self, subclass_name)
        else:
            print_manager.warning(f"Subclass '{subclass_name}' not found in {self.class_name}")
            return None

    def __getattr__(self, name):
        """Handle attribute access for unknown attributes following EPAD pattern."""
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        
        print_manager.debug('psp_dfb getattr helper!')
        available_attrs = list(self.raw_data.keys())
        print_manager.debug(f'psp_dfb available attrs: {available_attrs}')
        
        # Check if the requested attribute exists in raw_data
        if name in self.raw_data:
            return self.raw_data[name]
        else:
            # Provide helpful error message
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'. Available attributes: {available_attrs}")

    def __setattr__(self, name, value):
        """Handle attribute setting following EPAD pattern."""
        # Allow setting of private attributes and known class attributes
        if name.startswith('_') or name in ['raw_data', 'datetime_array', 'time', 'times_mesh_ac_dv12', 'times_mesh_ac_dv34', 'times_mesh_dc_dv12', 'ac_spec_dv12', 'ac_spec_dv34', 'dc_spec_dv12']:
            object.__setattr__(self, name, value)
        else:
            # For other attributes, store in raw_data if it exists
            if hasattr(self, 'raw_data'):
                self.raw_data[name] = value
            else:
                object.__setattr__(self, name, value)


# Create global instance
psp_dfb = psp_dfb_class(None)  # Initialize the class with no data 