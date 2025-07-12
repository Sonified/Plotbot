# plotbot/data_classes/psp_orbit.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from ._utils import _format_setattr_debug

# 🛰️ Define the main class to store PSP orbital/positional data 🛰️
class psp_orbit_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'psp_orbit')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'psp_orbit_data') # Key for psp_data_types.data_types
        object.__setattr__(self, 'subclass_name', None)         # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'r_sun': None,
            'carrington_lon': None,
            'carrington_lat': None,
            'icrf_x': None,                    # ICRF coordinates (inertial)
            'icrf_y': None,
            'icrf_z': None,
            'heliocentric_distance_au': None,  # Derived: r_sun converted to AU
            'orbital_speed': None,             # Derived: calculated from position changes
            'angular_momentum': None,          # Derived: L = r × v (conservation check)
            'velocity_x': None,               # Derived: velocity components
            'velocity_y': None,
            'velocity_z': None,
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.dependency_management("Processing PSP orbital data...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully processed PSP orbital data.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data."""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[PSP_ORBIT_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[PSP_ORBIT_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return

        print_manager.datacubby("\n=== PSP Orbit Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update
        current_plot_states = {}
        standard_components = ['r_sun', 'carrington_lon', 'carrington_lat', 'heliocentric_distance_au', 'orbital_speed', 'icrf_x', 'icrf_y', 'icrf_z', 'angular_momentum', 'velocity_x', 'velocity_y', 'velocity_z']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_ploption_snapshot(current_plot_states[comp_name])}")

        # Perform update
        self.calculate_variables(imported_data, original_requested_trange=original_requested_trange)
        self.set_ploptions()
        
        # Restore state
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
        
        print_manager.datacubby("=== End PSP Orbit Update Debug ===\n")
    
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

        # Handle special case for 'time' attribute
        if name == 'time':
            # Return None if time attribute doesn't exist yet
            return self.__dict__.get('time', None)

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.dependency_management('psp_orbit getattr helper!')
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
        if name in ['datetime', 'datetime_array', 'raw_data', 'times', 'time', 'npz_data'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('psp_orbit setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Process the orbital data and calculate derived quantities."""
        
        # Handle DataObject format (new format from import_data_function)
        if hasattr(imported_data, 'data') and hasattr(imported_data, 'times'):
            # This is a DataObject containing NPZ data
            npz_data = imported_data.data
            if hasattr(npz_data, 'files'):
                times = npz_data['times']
                r_sun = npz_data['r_sun']
                carrington_lon = npz_data['carrington_lon'] 
                carrington_lat = npz_data['carrington_lat']
                # Check for ICRF coordinates (new data)
                icrf_x = npz_data.get('icrf_x', None)
                icrf_y = npz_data.get('icrf_y', None)
                icrf_z = npz_data.get('icrf_z', None)
            else:
                raise ValueError(f"DataObject.data is not an NPZ file object: {type(npz_data)}")
        # For NPZ data, imported_data should be a dict-like object with the NPZ contents
        elif hasattr(imported_data, 'files'):
            # It's an NPZ file object (legacy format)
            times = imported_data['times']
            r_sun = imported_data['r_sun']
            carrington_lon = imported_data['carrington_lon'] 
            carrington_lat = imported_data['carrington_lat']
            # Check for ICRF coordinates (new data)
            icrf_x = imported_data.get('icrf_x', None)
            icrf_y = imported_data.get('icrf_y', None)
            icrf_z = imported_data.get('icrf_z', None)
        elif isinstance(imported_data, dict):
            # It's already a dictionary
            times = imported_data['times']
            r_sun = imported_data['r_sun']
            carrington_lon = imported_data['carrington_lon']
            carrington_lat = imported_data['carrington_lat']
            # Check for ICRF coordinates (new data)
            icrf_x = imported_data.get('icrf_x', None)
            icrf_y = imported_data.get('icrf_y', None)
            icrf_z = imported_data.get('icrf_z', None)
        else:
            raise ValueError(f"Unexpected imported_data type: {type(imported_data)}")
        
        # --- Time-based Slicing ---
        if original_requested_trange:
            try:
                # Convert trange strings to numpy.datetime64 for comparison
                start_time = np.datetime64(original_requested_trange[0].replace('/', 'T'))
                end_time = np.datetime64(original_requested_trange[1].replace('/', 'T'))

                # Find indices for the given time range from the full, unsliced 'times' array.
                indices = np.where((times >= start_time) & (times <= end_time))[0]
                
                if len(indices) > 0:
                    # Overwrite the full arrays with the sliced versions.
                    times = times[indices]
                    r_sun = r_sun[indices]
                    carrington_lon = carrington_lon[indices]
                    carrington_lat = carrington_lat[indices]
                    if icrf_x is not None:
                        icrf_x = icrf_x[indices]
                    if icrf_y is not None:
                        icrf_y = icrf_y[indices]
                    if icrf_z is not None:
                        icrf_z = icrf_z[indices]
                    
                    print_manager.status(f"Sliced psp_orbit data to {len(times)} points for trange: {original_requested_trange}")
                else:
                    # If no data is found in the range, create empty arrays to prevent errors.
                    print_manager.warning(f"No psp_orbit data found within trange: {original_requested_trange}. Storing empty arrays.")
                    times = np.array([], dtype='datetime64[ns]')
                    r_sun, carrington_lon, carrington_lat = np.array([]), np.array([]), np.array([])
                    icrf_x = np.array([]) if icrf_x is not None else None
                    icrf_y = np.array([]) if icrf_y is not None else None
                    icrf_z = np.array([]) if icrf_z is not None else None
            except Exception as e:
                print_manager.error(f"Failed to slice psp_orbit data with trange {original_requested_trange}: {e}")
                # Fallback to using unsliced data to avoid crashing, but log the error.
                pass

        # Store datetime array
        if isinstance(times[0], np.datetime64):
            self.datetime_array = np.array(times)
        else:
            # Convert to datetime64 if needed
            self.datetime_array = np.array(times, dtype='datetime64[ns]')
        
        # Store raw positional data
        r_sun_array = np.asarray(r_sun)
        carrington_lon_array = np.asarray(carrington_lon)
        carrington_lat_array = np.asarray(carrington_lat)
        
        # Store ICRF coordinates if available
        icrf_x_array = np.asarray(icrf_x) if icrf_x is not None else None
        icrf_y_array = np.asarray(icrf_y) if icrf_y is not None else None
        icrf_z_array = np.asarray(icrf_z) if icrf_z is not None else None
        
        # Calculate derived quantities
        # Convert r_sun to AU (1 R_sun = 696,000 km; 1 AU = 149,597,871 km)
        rsun_to_au = 696000.0 / 149597871.0  # = 0.004652473...
        heliocentric_distance_au = r_sun_array * rsun_to_au
        
        # Calculate orbital mechanics derived quantities
        # Use ICRF coordinates if available (proper physics), otherwise fall back to Carrington
        if icrf_x_array is not None and icrf_y_array is not None and icrf_z_array is not None:
            print_manager.dependency_management("Using ICRF coordinates for orbital mechanics calculation (inertial frame)")
            orbital_speed, velocity_x, velocity_y, velocity_z, angular_momentum = self._calculate_orbital_mechanics_icrf(
                icrf_x_array, icrf_y_array, icrf_z_array, r_sun_array)
        else:
            print_manager.dependency_management("Using Carrington coordinates for orbital speed calculation (rotating frame - less accurate)")
            orbital_speed = self._calculate_orbital_speed_carrington(r_sun_array, carrington_lon_array, carrington_lat_array)
            velocity_x = velocity_y = velocity_z = angular_momentum = None
        
        # Store all data in raw_data dictionary
        self.raw_data = {
            'r_sun': r_sun_array,
            'carrington_lon': carrington_lon_array,
            'carrington_lat': carrington_lat_array,
            'icrf_x': icrf_x_array,
            'icrf_y': icrf_y_array,
            'icrf_z': icrf_z_array,
            'heliocentric_distance_au': heliocentric_distance_au,
            'orbital_speed': orbital_speed,
            'angular_momentum': angular_momentum,
            'velocity_x': velocity_x,
            'velocity_y': velocity_y,
            'velocity_z': velocity_z,
        }

        print_manager.dependency_management(f"\nDebug - PSP Orbital Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.datetime_array.shape}")
        print_manager.dependency_management(f"Time range: {self.datetime_array[0]} to {self.datetime_array[-1]}")
        print_manager.dependency_management(f"r_sun range: {np.min(r_sun_array):.2f} to {np.max(r_sun_array):.2f} R_sun")
        print_manager.dependency_management(f"Carrington lon range: {np.min(carrington_lon_array):.2f} to {np.max(carrington_lon_array):.2f} deg")
        print_manager.dependency_management(f"Carrington lat range: {np.min(carrington_lat_array):.2f} to {np.max(carrington_lat_array):.2f} deg")
        if icrf_x_array is not None:
            print_manager.dependency_management(f"ICRF X range: {np.min(icrf_x_array):.2f} to {np.max(icrf_x_array):.2f} R_sun")
            print_manager.dependency_management(f"ICRF Y range: {np.min(icrf_y_array):.2f} to {np.max(icrf_y_array):.2f} R_sun")
            print_manager.dependency_management(f"ICRF Z range: {np.min(icrf_z_array):.2f} to {np.max(icrf_z_array):.2f} R_sun")
    
    def _calculate_orbital_mechanics_icrf(self, icrf_x, icrf_y, icrf_z, r_sun):
        """Calculate comprehensive orbital mechanics from ICRF coordinates (inertial frame) - OPTIMIZED VERSION."""
        if len(icrf_x) < 2:
            return np.array([0.0]), None, None, None, None
        
        # Handle NaN values in input data
        valid_mask = ~(np.isnan(icrf_x) | np.isnan(icrf_y) | np.isnan(icrf_z) | np.isnan(r_sun))
        
        # Constants
        dt_hours = 1.0  # Hourly data
        dt_seconds = dt_hours * 3600.0
        rsun_to_km = 696000.0  # R_sun to km conversion
        
        # Initialize output arrays
        n_points = len(icrf_x)
        vx = np.full(n_points, np.nan)
        vy = np.full(n_points, np.nan)
        vz = np.full(n_points, np.nan)
        speed = np.full(n_points, np.nan)
        angular_momentum = np.full(n_points, np.nan)
        
        # Calculate velocity components using gradient (handles NaN appropriately)
        vx_raw = np.gradient(icrf_x, dt_seconds) * rsun_to_km  # km/s
        vy_raw = np.gradient(icrf_y, dt_seconds) * rsun_to_km  # km/s
        vz_raw = np.gradient(icrf_z, dt_seconds) * rsun_to_km  # km/s
        
        # Apply valid mask to velocity components
        vx[valid_mask] = vx_raw[valid_mask]
        vy[valid_mask] = vy_raw[valid_mask]
        vz[valid_mask] = vz_raw[valid_mask]
        
        # Calculate speed magnitude where valid
        speed[valid_mask] = np.sqrt(vx[valid_mask]**2 + vy[valid_mask]**2 + vz[valid_mask]**2)
        
        # OPTIMIZED: Vectorized angular momentum calculation (no Python loop!)
        # Position vectors (convert to km) - broadcast to (n_points, 3)
        r_vecs = np.column_stack([icrf_x, icrf_y, icrf_z]) * rsun_to_km  # Shape: (n_points, 3)
        # Velocity vectors (km/s) - broadcast to (n_points, 3)
        v_vecs = np.column_stack([vx, vy, vz])  # Shape: (n_points, 3)
        
        # Vectorized cross product for all points at once
        L_vecs = np.cross(r_vecs, v_vecs)  # Shape: (n_points, 3)
        # Vectorized norm calculation
        angular_momentum_all = np.linalg.norm(L_vecs, axis=1)  # Shape: (n_points,)
        
        # Apply valid mask
        angular_momentum[valid_mask] = angular_momentum_all[valid_mask]
        
        print_manager.dependency_management(f"Orbital mechanics calculation complete (OPTIMIZED):")
        print_manager.dependency_management(f"  Valid data points: {np.sum(valid_mask)}/{n_points}")
        print_manager.dependency_management(f"  Speed range: {np.nanmin(speed):.2f} to {np.nanmax(speed):.2f} km/s")
        print_manager.dependency_management(f"  Angular momentum range: {np.nanmin(angular_momentum):.2f} to {np.nanmax(angular_momentum):.2f} km²/s")
        
        return speed, vx, vy, vz, angular_momentum
    
    def _calculate_orbital_speed_carrington(self, r_sun, carrington_lon, carrington_lat):
        """Calculate orbital speed in km/s from Carrington coordinates (rotating frame - less accurate) - OPTIMIZED VERSION."""
        # Convert to Cartesian coordinates for speed calculation
        # Note: This method is contaminated by coordinate system rotation
        
        if len(r_sun) < 2:
            return np.array([0.0])  # Can't calculate speed with only one point
        
        # OPTIMIZED: Vectorized coordinate transformation (no intermediate variables)
        lon_rad = np.radians(carrington_lon)
        lat_rad = np.radians(carrington_lat)
        
        # Vectorized Cartesian conversion
        cos_lat = np.cos(lat_rad)
        x = r_sun * cos_lat * np.cos(lon_rad)
        y = r_sun * cos_lat * np.sin(lon_rad)
        z = r_sun * np.sin(lat_rad)
        
        # Calculate velocity components (vectorized finite difference)
        dt_hours = 1.0  # Assuming hourly data
        dt_seconds = dt_hours * 3600.0
        rsun_to_km = 696000.0  # R_sun to km conversion
        
        # OPTIMIZED: Single vectorized gradient calculation
        vx = np.gradient(x, dt_seconds) * rsun_to_km
        vy = np.gradient(y, dt_seconds) * rsun_to_km
        vz = np.gradient(z, dt_seconds) * rsun_to_km
        
        # OPTIMIZED: Vectorized speed magnitude calculation
        speed = np.sqrt(vx**2 + vy**2 + vz**2)
        
        return speed
    
    def set_ploptions(self):
        """Set up the plotting options for all orbital components"""
        
        self.r_sun = plot_manager(
            self.raw_data['r_sun'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='r_sun',
                class_name='psp_orbit',
                subclass_name='r_sun',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Distance (R$\odot$)',
                legend_label='Heliocentric Distance',
                color='orange',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.carrington_lon = plot_manager(
            self.raw_data['carrington_lon'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='carrington_lon',
                class_name='psp_orbit',
                subclass_name='carrington_lon',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Carrington Longitude (°)',
                legend_label='Carrington Longitude',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.carrington_lat = plot_manager(
            self.raw_data['carrington_lat'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='carrington_lat',
                class_name='psp_orbit',
                subclass_name='carrington_lat',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Carrington Latitude (°)',
                legend_label='Carrington Latitude',
                color='green',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.heliocentric_distance_au = plot_manager(
            self.raw_data['heliocentric_distance_au'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='heliocentric_distance_au',
                class_name='psp_orbit',
                subclass_name='heliocentric_distance_au',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Distance (AU)',
                legend_label='Heliocentric Distance (AU)',
                color='red',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.orbital_speed = plot_manager(
            self.raw_data['orbital_speed'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='orbital_speed',
                class_name='psp_orbit',
                subclass_name='orbital_speed',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Speed (km/s)',
                legend_label='Orbital Speed',
                color='purple',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Always create ICRF coordinate plot managers (even if data is None)
        self.icrf_x = plot_manager(
            self.raw_data['icrf_x'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='icrf_x',
                class_name='psp_orbit',
                subclass_name='icrf_x',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='ICRF X (R$\odot$)',
                legend_label='ICRF X Coordinate',
                color='darkred',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.icrf_y = plot_manager(
            self.raw_data['icrf_y'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='icrf_y',
                class_name='psp_orbit',
                subclass_name='icrf_y',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='ICRF Y (R$\odot$)',
                legend_label='ICRF Y Coordinate',
                color='darkgreen',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.icrf_z = plot_manager(
            self.raw_data['icrf_z'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='icrf_z',
                class_name='psp_orbit',
                subclass_name='icrf_z',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='ICRF Z (R$\odot$)',
                legend_label='ICRF Z Coordinate',
                color='darkblue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Orbital mechanics validation plot managers
        self.angular_momentum = plot_manager(
            self.raw_data['angular_momentum'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='angular_momentum',
                class_name='psp_orbit',
                subclass_name='angular_momentum',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Angular Momentum (km²/s)',
                legend_label='Angular Momentum |r × v|',
                color='brown',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Velocity component plot managers
        self.velocity_x = plot_manager(
            self.raw_data['velocity_x'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='velocity_x',
                class_name='psp_orbit',
                subclass_name='velocity_x',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Velocity X (km/s)',
                legend_label='Velocity X Component',
                color='crimson',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.velocity_y = plot_manager(
            self.raw_data['velocity_y'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='velocity_y',
                class_name='psp_orbit',
                subclass_name='velocity_y',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Velocity Y (km/s)',
                legend_label='Velocity Y Component',
                color='forestgreen',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.velocity_z = plot_manager(
            self.raw_data['velocity_z'],
            plot_options=ploptions(
                data_type='psp_orbit_data',
                var_name='velocity_z',
                class_name='psp_orbit',
                subclass_name='velocity_z',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Velocity Z (km/s)',
                legend_label='Velocity Z Component',
                color='mediumblue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    def ensure_internal_consistency(self):
        """Ensures internal data consistency."""
        print_manager.dependency_management(f"*** PSP ORBIT ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        
        # For orbital data, we mainly need to ensure datetime_array consistency
        if hasattr(self, 'datetime_array') and self.datetime_array is not None:
            print_manager.dependency_management(f"    datetime_array length: {len(self.datetime_array)}")
            
            # Check that all raw_data arrays have consistent lengths
            expected_len = len(self.datetime_array)
            for key, data in self.raw_data.items():
                if data is not None and len(data) != expected_len:
                    print_manager.dependency_management(f"    Inconsistent length for {key}: {len(data)} vs expected {expected_len}")
        
        print_manager.dependency_management(f"*** PSP ORBIT ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

# Initialize the class with no data
psp_orbit = psp_orbit_class(None)
print('initialized psp_orbit class') 