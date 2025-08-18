# wind_3dp_classes.py - Calculates and stores WIND 3DP electron pitch-angle distribution variables

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

# 🎉 Define the main class to calculate and store WIND 3DP ELPD electron variables 🎉
class wind_3dp_elpd_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'wind_3dp_elpd')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'wind_3dp_elpd')      # Key for data_types
        object.__setattr__(self, 'subclass_name', None)             # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'flux': None,                    # Main electron flux data [N x 8 x 15]
            'centroids': None,               # Pitch angle centroids
            'pitch_angle_y_values': None,    # Pitch angle bins [N x 8]
            'flux_selected_energy': None,    # Selected energy channel for display
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'energy_index', 4)  # Channel 4 corresponds to 255 eV
        object.__setattr__(self, '_current_operation_trange', None)

        print_manager.dependency_management(f"*** WIND_3DP_ELPD_CLASS_INIT (wind_3dp_elpd_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating WIND 3DP ELPD variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated WIND 3DP ELPD variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[WIND_3DP_ELPD_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[WIND_3DP_ELPD_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['flux', 'centroids', 'flux_selected_energy']
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
        print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[WIND_3DP_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[WIND_3DP_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
        print_manager.dependency_management('wind_3dp_elpd getattr helper!')
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
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'times_mesh', 'energy_index', 'data_type'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('wind_3dp_elpd setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate WIND 3DP ELPD electron variables from imported CDF data."""
        print_manager.processing("WIND 3DP ELPD: Starting calculate_variables...")

        if imported_data is None or not hasattr(imported_data, 'data') or imported_data.data is None:
            print_manager.warning("WIND 3DP ELPD: No data available for calculation")
            return

        data = imported_data.data
        print_manager.processing(f"WIND 3DP ELPD: Processing data with keys: {list(data.keys())}")

        # Store only TT2000 times as numpy array (following PSP pattern)
        if hasattr(imported_data, 'times') and imported_data.times is not None:
            self.time = np.asarray(imported_data.times)
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"self.datetime_array type after conversion: {type(self.datetime_array)}")
            print_manager.dependency_management(f"First element type: {type(self.datetime_array[0])}")
            print_manager.processing(f"WIND 3DP ELPD: Processed {len(self.datetime_array)} time points")
        else:
            print_manager.warning("WIND 3DP ELPD: No times data found in imported_data")
            return

        # Extract electron pitch-angle distribution data
        if 'FLUX' in data and 'PANGLE' in data:
            flux_data = data['FLUX']    # [N x 8 x 15] array (time x pitch_angle x energy)
            pangle_data = data['PANGLE']  # [N x 8] pitch angle bins

            print_manager.processing(f"WIND 3DP ELPD: FLUX shape: {flux_data.shape}, PANGLE shape: {pangle_data.shape}")
            print_manager.processing(f"WIND 3DP ELPD: FLUX range: [{np.nanmin(flux_data):.2e}, {np.nanmax(flux_data):.2e}]")

            # Clean pitch angle data - replace any NaN values with interpolated values
            # or reasonable defaults (evenly spaced from 0 to 180 degrees)
            if np.any(np.isnan(pangle_data)):
                print_manager.processing("WIND 3DP ELPD: Found NaN values in pitch angle data, cleaning...")
                # For each time point, if pitch angles have NaN, use default uniform spacing
                for i in range(pangle_data.shape[0]):
                    if np.any(np.isnan(pangle_data[i, :])):
                        # Replace with evenly spaced angles from 0 to 180 degrees
                        pangle_data[i, :] = np.linspace(0, 180, pangle_data.shape[1])

            # Store pitch angle data 
            self.raw_data['pitch_angle_y_values'] = pangle_data

            # Extract flux for selected energy channel (default energy_index = 7, mid-range of 0-14)
            flux_selected_energy = flux_data[:, :, self.energy_index]
            print_manager.processing(f"WIND 3DP ELPD: Using energy index {self.energy_index} out of {flux_data.shape[2]} channels")

            # Replace zeros and negative values, then take log
            flux_selected_energy = np.where(flux_selected_energy <= 0, 1e-10, flux_selected_energy)
            log_flux = np.log10(flux_selected_energy)

            # Create time mesh to match flux data dimensions for spectral plotting
            self.times_mesh = np.meshgrid(
                self.datetime_array,
                np.arange(flux_selected_energy.shape[1]),  # 8 pitch angle bins
                indexing='ij'
            )[0]
            print_manager.processing(f"WIND 3DP ELPD: Created times_mesh with shape: {self.times_mesh.shape}")

            # Calculate centroids using weighted average across pitch angles
            centroids = np.ma.average(pangle_data, 
                                    weights=flux_selected_energy, 
                                    axis=1)
            
            # Convert MaskedArray to regular numpy array and handle NaN values
            if isinstance(centroids, np.ma.MaskedArray):
                # Fill masked values with NaN, then convert to regular array
                centroids = centroids.filled(np.nan)
            
            # Replace any remaining NaN values with a reasonable default (middle of pitch angle range)
            # Use 90 degrees as default (middle of 0-180 degree range)
            centroids = np.where(np.isnan(centroids), 90.0, centroids)

            # Store all data in raw_data dictionary
            self.raw_data = {
                'flux': flux_data,                    # Full [N x 8 x 15] data
                'centroids': centroids,               # Pitch angle centroids
                'pitch_angle_y_values': pangle_data,  # Pitch angle bins [N x 8]
                'flux_selected_energy': log_flux,     # Selected energy channel, log scale
            }

            print_manager.processing("WIND 3DP ELPD: Successfully calculated electron flux components")
            print_manager.processing(f"WIND 3DP ELPD: Selected energy flux range: [{np.nanmin(log_flux):.2f}, {np.nanmax(log_flux):.2f}] log10")
            print_manager.processing(f"WIND 3DP ELPD: Centroids range: [{np.nanmin(centroids):.1f}, {np.nanmax(centroids):.1f}] degrees")

            print_manager.dependency_management(f"\nDebug - Data Arrays:")
            print_manager.dependency_management(f"Time array shape: {self.time.shape}")
            print_manager.dependency_management(f"FLUX data shape: {flux_data.shape}")
            print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")

        else:
            print_manager.warning("WIND 3DP ELPD: Missing required electron data (FLUX and/or PANGLE)")

    def set_ploptions(self):
        """Set up the plotting options for all electron components"""
        print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT ENTRY] id(self): {id(self)}")
        
        # Check and regenerate times_mesh if needed (following PSP electron pattern)
        times_mesh_exists = hasattr(self, 'times_mesh') and self.times_mesh is not None
        raw_data_flux_exists = hasattr(self, 'raw_data') and 'flux_selected_energy' in self.raw_data and self.raw_data['flux_selected_energy'] is not None
        datetime_array_exists = hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0

        if times_mesh_exists and isinstance(self.times_mesh, np.ndarray) and raw_data_flux_exists and datetime_array_exists:
            needs_regeneration = False
            if self.times_mesh.ndim != 2:
                needs_regeneration = True
                print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT] times_mesh is not 2D (shape: {self.times_mesh.shape}). Regenerating.")
            elif self.times_mesh.shape[0] != len(self.datetime_array):
                needs_regeneration = True
                print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT] times_mesh.shape[0] ({self.times_mesh.shape[0]}) != len(datetime_array) ({len(self.datetime_array)}). Regenerating.")
            elif self.raw_data['flux_selected_energy'].ndim == 2 and self.times_mesh.shape[1] != self.raw_data['flux_selected_energy'].shape[1]:
                needs_regeneration = True
                print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT] times_mesh.shape[1] ({self.times_mesh.shape[1]}) != flux_selected_energy.shape[1] ({self.raw_data['flux_selected_energy'].shape[1]}). Regenerating.")

            if needs_regeneration:
                print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT] Regenerating times_mesh. Old shape: {self.times_mesh.shape if isinstance(self.times_mesh, np.ndarray) else 'N/A'}")
                self.times_mesh = np.meshgrid(
                    self.datetime_array,
                    np.arange(self.raw_data['flux_selected_energy'].shape[1] if self.raw_data['flux_selected_energy'].ndim == 2 else 1),
                    indexing='ij'
                )[0]
                print_manager.processing(f"[WIND_3DP_ELPD_SET_PLOPT] Regenerated times_mesh. New shape: {self.times_mesh.shape}")

        # Main flux spectrogram (selected energy channel)
        self.flux_selected_energy = plot_manager(
            self.raw_data['flux_selected_energy'],
            plot_options=ploptions(
                data_type='wind_3dp_elpd',
                var_name='electron_flux_log',
                class_name='wind_3dp_elpd',
                subclass_name='flux_selected_energy',
                plot_type='spectral',
                datetime_array=self.times_mesh,  # Use the mesh for time array
                y_label='Pitch Angle\n(degrees)',
                legend_label=f'Electron Flux (E_idx={self.energy_index})',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['pitch_angle_y_values'],
                colormap='jet',
                colorbar_scale='log',
                colorbar_limits=None
            )
        )

        # Centroids time series 
        self.centroids = plot_manager(
            self.raw_data['centroids'],
            plot_options=ploptions(
                data_type='wind_3dp_elpd',
                var_name='electron_centroids',
                class_name='wind_3dp_elpd', 
                subclass_name='centroids',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pitch Angle\n(degrees)',
                legend_label='Electron Centroids',
                color='crimson',
                y_scale='linear',
                y_limit=[0, 180],
                line_width=1,
                line_style='-'
            )
        )

        # Full flux data (not plotted by default, but available for advanced use)
        self.flux = plot_manager(
            self.raw_data['flux'],
            plot_options=ploptions(
                data_type='wind_3dp_elpd',
                var_name='electron_flux_full',
                class_name='wind_3dp_elpd',
                subclass_name='flux',
                plot_type='data_array',  # Special type for 3D data
                datetime_array=self.datetime_array,
                y_label='Full Flux Data',
                legend_label='Full Electron Flux [N x 8 x 15]',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    @property
    def pitch_angle_y_values(self):
        """Property to access pitch angle values (following PSP pattern)"""
        if hasattr(self, 'raw_data') and 'pitch_angle_y_values' in self.raw_data:
            return self.raw_data['pitch_angle_y_values']
        print_manager.warning(f"Property 'pitch_angle_y_values' accessed but not found in raw_data for {self.__class__.__name__}")
        return None

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** WIND_3DP_ELPD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        # For electron data, we don't have a single 'field' like magnetic field data
        # Main consistency is between time arrays and flux data
        
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
            
        print_manager.dependency_management(f"*** WIND_3DP_ELPD ENSURE ID:{id(self)} *** Finished.")

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

# Initialize the class with no data
wind_3dp_elpd = wind_3dp_elpd_class(None)  
print_manager.dependency_management('initialized wind_3dp_elpd class') 