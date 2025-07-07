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
        """Extract electric field spectra from PySpedas CDF data."""
        # ⭐️ THIS IS THE SPECIAL MATH FROM e10_iaw.ipynb ⭐️
        
        print_manager.debug("Starting DFB electric field spectra calculation...")
        
        # Import required functions for data processing
        try:
            from pytplot import get_data, time_datetime
        except ImportError:
            print_manager.error("Cannot import pytplot functions. Make sure pytplot is installed.")
            return
        
        # Extract CDF data from imported_data
        data = imported_data.data
        times = imported_data.times
        
        # Convert TT2000 timestamps to datetime objects
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(times))
        
        # STEP 1: Extract raw spectral data from PySpedas variables
        # Following exact e10_iaw.ipynb implementation patterns:
        
        # AC Spectrum Processing (dv12 and dv34):
        ac_times_dv12 = None
        ac_freq_vals_dv12 = None
        ac_vals_dv12 = None
        times_ac_repeat_dv12 = None
        
        if 'psp_fld_l2_dfb_ac_spec_dV12hg' in data:
            print_manager.debug("Processing AC spectrum dv12 data...")
            # Extract AC dv12 data
            ac_spec_dv12_data = data['psp_fld_l2_dfb_ac_spec_dV12hg']
            ac_freq_dv12_data = data.get('psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins')
            
            if ac_spec_dv12_data is not None and len(ac_spec_dv12_data) > 0:
                ac_vals_dv12 = np.asarray(ac_spec_dv12_data)
                if ac_freq_dv12_data is not None:
                    ac_freq_vals_dv12 = np.asarray(ac_freq_dv12_data)
                else:
                    # Default frequency bins if not available (54 bins as per e10_iaw.ipynb)
                    ac_freq_vals_dv12 = np.arange(54)
                
                # Time mesh creation for spectral plotting (following e10_iaw.ipynb):
                datetime_ac_dv12 = self.datetime_array
                if len(datetime_ac_dv12) > 0 and ac_vals_dv12.ndim >= 2:
                    freq_bins = ac_vals_dv12.shape[1] if ac_vals_dv12.ndim > 1 else len(ac_freq_vals_dv12)
                    times_ac_repeat_dv12 = np.repeat(np.expand_dims(datetime_ac_dv12, 1), freq_bins, 1)
                    print_manager.debug(f"Created AC dv12 time mesh with shape: {times_ac_repeat_dv12.shape}")
        
        # AC dv34 processing
        ac_times_dv34 = None
        ac_freq_vals_dv34 = None
        ac_vals_dv34 = None
        times_ac_repeat_dv34 = None
        
        if 'psp_fld_l2_dfb_ac_spec_dV34hg' in data:
            print_manager.debug("Processing AC spectrum dv34 data...")
            # Extract AC dv34 data
            ac_spec_dv34_data = data['psp_fld_l2_dfb_ac_spec_dV34hg']
            ac_freq_dv34_data = data.get('psp_fld_l2_dfb_ac_spec_dV34hg_frequency_bins')
            
            if ac_spec_dv34_data is not None and len(ac_spec_dv34_data) > 0:
                ac_vals_dv34 = np.asarray(ac_spec_dv34_data)
                if ac_freq_dv34_data is not None:
                    ac_freq_vals_dv34 = np.asarray(ac_freq_dv34_data)
                else:
                    # Default frequency bins if not available
                    ac_freq_vals_dv34 = np.arange(54)
                
                # Time mesh creation for AC dv34:
                datetime_ac_dv34 = self.datetime_array
                if len(datetime_ac_dv34) > 0 and ac_vals_dv34.ndim >= 2:
                    freq_bins = ac_vals_dv34.shape[1] if ac_vals_dv34.ndim > 1 else len(ac_freq_vals_dv34)
                    times_ac_repeat_dv34 = np.repeat(np.expand_dims(datetime_ac_dv34, 1), freq_bins, 1)
                    print_manager.debug(f"Created AC dv34 time mesh with shape: {times_ac_repeat_dv34.shape}")
            
        # DC Spectrum Processing (dv12 only - dv34 not available):
        dc_times_dv12 = None
        dc_freq_vals_dv12 = None
        dc_vals_dv12 = None
        times_dc_repeat_dv12 = None
        
        if 'psp_fld_l2_dfb_dc_spec_dV12hg' in data:
            print_manager.debug("Processing DC spectrum dv12 data...")
            # Extract DC dv12 data
            dc_spec_dv12_data = data['psp_fld_l2_dfb_dc_spec_dV12hg']
            dc_freq_dv12_data = data.get('psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins')
            
            if dc_spec_dv12_data is not None and len(dc_spec_dv12_data) > 0:
                dc_vals_dv12 = np.asarray(dc_spec_dv12_data)
                if dc_freq_dv12_data is not None:
                    dc_freq_vals_dv12 = np.asarray(dc_freq_dv12_data)
                else:
                    # Default frequency bins if not available
                    dc_freq_vals_dv12 = np.arange(54)
                
                # Time mesh for DC plotting:
                datetime_dc_dv12 = self.datetime_array
                if len(datetime_dc_dv12) > 0 and dc_vals_dv12.ndim >= 2:
                    freq_bins = dc_vals_dv12.shape[1] if dc_vals_dv12.ndim > 1 else len(dc_freq_vals_dv12)
                    times_dc_repeat_dv12 = np.repeat(np.expand_dims(datetime_dc_dv12, 1), freq_bins, 1)
                    print_manager.debug(f"Created DC dv12 time mesh with shape: {times_dc_repeat_dv12.shape}")
            
        # STEP 2: Update only the keys that have real data (don't overwrite entire dict)
        if ac_vals_dv12 is not None:
            self.raw_data['ac_spec_dv12'] = ac_vals_dv12
            self.raw_data['ac_freq_bins_dv12'] = ac_freq_vals_dv12
            
        if ac_vals_dv34 is not None:
            self.raw_data['ac_spec_dv34'] = ac_vals_dv34
            self.raw_data['ac_freq_bins_dv34'] = ac_freq_vals_dv34
            
        if dc_vals_dv12 is not None:
            self.raw_data['dc_spec_dv12'] = dc_vals_dv12
            self.raw_data['dc_freq_bins_dv12'] = dc_freq_vals_dv12
        
        # STEP 3: Store time meshes for spectral plotting (only if created)
        if times_ac_repeat_dv12 is not None:
            self.times_mesh_ac_dv12 = times_ac_repeat_dv12
            
        if times_ac_repeat_dv34 is not None:
            self.times_mesh_ac_dv34 = times_ac_repeat_dv34
            
        if times_dc_repeat_dv12 is not None:
            self.times_mesh_dc_dv12 = times_dc_repeat_dv12
        
        print_manager.debug("DFB electric field spectra calculation completed.")
        
    def set_ploptions(self):
        """Set up plotting options - follow electron classes pattern for spectral data"""
        
        # FOLLOW ELECTRON PATTERN: Use 2D time mesh + 1D frequency arrays
        
        # AC Spectrum dv12 - Use 1D time array for filtering, 2D mesh for plotting
        self.ac_spec_dv12 = plot_manager(
            self.raw_data['ac_spec_dv12'] if self.raw_data['ac_spec_dv12'] is not None else np.array([]),
            plot_options=ploptions(
                data_type='dfb_ac_spec_dv12hg',
                var_name='ac_spec_dv12',
                class_name='psp_dfb',
                subclass_name='ac_spec_dv12',
                plot_type='spectral',
                datetime_array=self.datetime_array,  # ✅ 1D time array for filtering
                y_label='AC Spec dV12\nFrequency (Hz)',
                legend_label='AC Spectrum dV12',
                color='blue',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['ac_freq_bins_dv12'],  # 1D frequency array
                colormap='jet',
                colorbar_scale='log'
            )
        )
        # Store 2D time mesh separately for spectral plotting
        if hasattr(self, 'times_mesh_ac_dv12') and self.times_mesh_ac_dv12 is not None:
            self.ac_spec_dv12.times_mesh = self.times_mesh_ac_dv12
        
        # AC Spectrum dv34 - Use 1D time array for filtering, 2D mesh for plotting  
        self.ac_spec_dv34 = plot_manager(
            self.raw_data['ac_spec_dv34'] if self.raw_data['ac_spec_dv34'] is not None else np.array([]),
            plot_options=ploptions(
                data_type='dfb_ac_spec_dv34hg',
                var_name='ac_spec_dv34',
                class_name='psp_dfb',
                subclass_name='ac_spec_dv34',
                plot_type='spectral',
                datetime_array=self.datetime_array,  # ✅ 1D time array for filtering
                y_label='AC Spec dV34\nFrequency (Hz)',
                legend_label='AC Spectrum dV34',
                color='green',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['ac_freq_bins_dv34'],  # 1D frequency array
                colormap='jet',
                colorbar_scale='log'
            )
        )
        # Store 2D time mesh separately for spectral plotting
        if hasattr(self, 'times_mesh_ac_dv34') and self.times_mesh_ac_dv34 is not None:
            self.ac_spec_dv34.times_mesh = self.times_mesh_ac_dv34
        
        # DC Spectrum dv12 - Use 1D time array for filtering, 2D mesh for plotting
        self.dc_spec_dv12 = plot_manager(
            self.raw_data['dc_spec_dv12'] if self.raw_data['dc_spec_dv12'] is not None else np.array([]),
            plot_options=ploptions(
                data_type='dfb_dc_spec_dv12hg',
                var_name='dc_spec_dv12',
                class_name='psp_dfb',
                subclass_name='dc_spec_dv12',
                plot_type='spectral',
                datetime_array=self.datetime_array,  # ✅ 1D time array for filtering
                y_label='DC Spec dV12\nFrequency (Hz)',
                legend_label='DC Spectrum dV12',
                color='red',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['dc_freq_bins_dv12'],  # 1D frequency array
                colormap='jet',
                colorbar_scale='log'
            )
        )
        # Store 2D time mesh separately for spectral plotting
        if hasattr(self, 'times_mesh_dc_dv12') and self.times_mesh_dc_dv12 is not None:
            self.dc_spec_dv12.times_mesh = self.times_mesh_dc_dv12
        
        print_manager.debug("DFB plotting options set successfully.")

    def get_subclass(self, subclass_name):
        """Get a specific subclass by name."""
        if hasattr(self, subclass_name):
            return getattr(self, subclass_name)
        else:
            print_manager.warning(f"Subclass '{subclass_name}' not found in {self.class_name}")
            return None

    def __getattr__(self, name):
        """Handle attribute access for unknown attributes."""
        if name in self.raw_data:
            return self.raw_data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """Control attribute setting to maintain consistency."""
        if name.startswith('_') or name in ['class_name', 'data_type', 'subclass_name', 'raw_data', 'datetime', 'datetime_array', 'times_mesh_ac_dv12', 'times_mesh_ac_dv34', 'times_mesh_dc_dv12']:
            object.__setattr__(self, name, value)
        else:
            # For plot_manager attributes, allow direct setting
            if isinstance(value, plot_manager):
                object.__setattr__(self, name, value)
            else:
                print_manager.warning(f"Attempting to set non-plot_manager attribute '{name}' on {self.__class__.__name__}")
                object.__setattr__(self, name, value)


# Create global instance
psp_dfb = psp_dfb_class(None)  # Initialize the class with no data 