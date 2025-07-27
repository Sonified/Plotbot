# plotbot/data_classes/psp_proton.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
from typing import Optional, List # Added for type hinting

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store proton variables 🎉
class proton_class:    
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'vr': None,
            'vt': None,
            'vn': None,
            't_par': None,
            't_perp': None,
            'anisotropy': None,
            'v_alfven': None,
            'beta_ppar': None,
            'beta_pperp': None,
            'pressure_ppar': None,
            'pressure_pperp': None,
            'energy_flux': None,
            'theta_flux': None,
            'phi_flux': None,
            'v_sw': None,
            'm_alfven': None,
            'temperature': None,
            'pressure': None,
            'density': None,
            'bmag': None,
            'sun_dist_rsun': None,
            'ENERGY_VALS': None,  # Added for consistency
            'THETA_VALS': None,   # Added for consistency
            'PHI_VALS': None      # Added for consistency
        })
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'times_mesh_angle', [])
        object.__setattr__(self, 'energy_vals', None)
        object.__setattr__(self, 'theta_vals', None)
        object.__setattr__(self, 'phi_vals', None)
        object.__setattr__(self, 'data_type', 'spi_sf00_l3_mom')
        object.__setattr__(self, '_current_operation_trange', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating proton variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated proton variables.")

    #updateprotons
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if original_requested_trange is not None:
            object.__setattr__(self, '_current_operation_trange', original_requested_trange)
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")

        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        # Check with DataTracker before recalculating
        from plotbot.data_tracker import global_tracker # Moved import here
        # Try to get time range from imported_data
        trange = None
        if hasattr(imported_data, 'times') and imported_data.times is not None and len(imported_data.times) > 1:
            dt_array = cdflib.cdfepoch.to_datetime(imported_data.times)
            start = dt_array[0]
            end = dt_array[-1]
            # Format as string for DataTracker
            if hasattr(start, 'strftime'):
                start = start.strftime('%Y-%m-%d/%H:%M:%S.%f')
            if hasattr(end, 'strftime'):
                end = end.strftime('%Y-%m-%d/%H:%M:%S.%f')
            trange = [start, end]
        data_type = getattr(self, 'data_type', self.__class__.__name__)
        if trange and not global_tracker.is_calculation_needed(trange, data_type):
            print_manager.status(f"{data_type} already calculated for the time range: {trange}")
            return

        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_state = {}
        for subclass_name in self.raw_data.keys():                             # Use keys()
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)       # Save current plot state
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_ploptions()                                                  # Recreate plot managers
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():                    # Restore saved states
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)                                 # Restore plot state
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)                # Restore individual options
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")

    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component"""
        print_manager.dependency_management(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.dependency_management(f"Returning {subclass_name} component")  # Log successful component find
            
            # 🚀 PERFORMANCE FIX: Only set requested_trange on the SPECIFIC subclass being requested
            current_trange = TimeRangeTracker.get_current_trange()
            if current_trange:
                try:
                    attr_value = getattr(self, subclass_name)
                    if isinstance(attr_value, plot_manager):
                        attr_value.requested_trange = current_trange
                except Exception:
                    pass
            
            return getattr(self, subclass_name)  # Return the plot_manager instance
        else:
            print(f"'{subclass_name}' is not a recognized subclass, friend!")  # Friendly error message
            print(f"Try one of these: {', '.join(self.raw_data.keys())}")  # Show available components
            return None  # Return None if not found
    
    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if name == 'field':
            print_manager.dependency_management(f"[PROTON_GETATTR_FIELD_ACCESS] Attempt to access 'field' attribute on {self.__class__.__name__} instance ID {id(self)}")

        if 'raw_data' not in self.__dict__:
            # This case should ideally not be hit if __init__ runs correctly
            print_manager.error(f"[PROTON_GETATTR_ERROR] raw_data not initialized for {self.__class__.__name__} instance when trying to get '{name}'")
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' (raw_data not initialized)")
        
        # If the attribute is a known data component, it should have been set up by set_ploptions
        # and would be directly accessible, or handled by plot_manager's __get__ if it's a PlotManager instance.
        # This __getattr__ is more of a fallback for names NOT in raw_data.keys() or not plot_manager instances.
        
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print_manager.dependency_management(f"[PROTON_GETATTR] Attribute '{name}' not found directly. Known raw_data keys: {available_attrs}")
        # Default message for unrecognized attributes:
        print_manager.warning(f"[PROTON_GETATTR] '{name}' is not a recognized attribute, friend!")
        print_manager.warning(f"Try one of these: {', '.join(available_attrs)}")
        return None # Or raise AttributeError if preferred for stricter behavior
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        if name == 'field':
            print_manager.dependency_management(f"[PROTON_SETATTR_FIELD_SET] Attempt to set 'field' attribute on {self.__class__.__name__} instance ID {id(self)} to value of type {type(value)}")

        # Allow setting known attributes
        # print_manager.debug(f"Setting attribute: {name} with value: {value}") # Too verbose for general use
        if name in ['datetime_array', 'raw_data', 'time', 'field', 'mag_field', 'temp_tensor', 'energy_flux', 'theta_flux', 'phi_flux', 'energy_vals', 'theta_vals', 'phi_vals', 'times_mesh', 'times_mesh_angle', 'data_type'] or \
           (hasattr(self, 'raw_data') and isinstance(self.raw_data, dict) and name in self.raw_data) or \
           (hasattr(self, name) and not callable(getattr(self, name))): # Allow setting if it's an existing non-callable attribute (like a PlotManager instance)
            object.__setattr__(self, name, value) # Use object.__setattr__ to bypass this method for known attributes
        else:
            # Print friendly error message for truly unrecognized attributes
            print_manager.warning(f"[PROTON_SETATTR] Attribute '{name}' is not explicitly defined in settable list for {self.__class__.__name__}. Allowed if it's a plot_manager instance or in raw_data.")
            available_attrs = list(getattr(self, 'raw_data', {}).keys()) + ['datetime_array', 'time', 'field', 'mag_field', 'temp_tensor', 'energy_flux', 'theta_flux', 'phi_flux', 'energy_vals', 'theta_vals', 'phi_vals', 'times_mesh', 'times_mesh_angle', 'data_type']
            print(f"[PROTON_SETATTR] '{name}' is not a recognized settable attribute, friend! (Or it might be a method name)")
            print(f"Known data keys and core attributes: {', '.join(list(set(available_attrs)))}")
            # Potentially raise an error here if strict attribute setting is desired
            # For now, just warn and allow if it's an existing attribute (e.g. plot manager objects)
            object.__setattr__(self, name, value)

    def calculate_variables(self, imported_data):
        """Calculate the proton parameters and derived quantities."""
        pm = print_manager # local alias
        pm.dependency_management(f"[PROTON_CALC_VARS_ENTRY] Instance ID {id(self)} calculating variables. Imported data time type: {type(getattr(imported_data, 'times', None))}")

        # Extract time and field data
        self.time = imported_data.times
        
        pm.processing(f"[PROTON_CALC_VARS] About to create self.datetime_array from self.time (len: {len(self.time) if self.time is not None else 'None'}) for instance ID {id(self)}")
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))  # Use cdflib instead of pandas
        pm.processing(f"[PROTON_CALC_VARS] self.datetime_array (id: {id(self.datetime_array)}) created. len: {len(self.datetime_array) if self.datetime_array is not None else 'None'}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}" if self.datetime_array is not None and len(self.datetime_array) > 0 else f"[PROTON_CALC_VARS] self.datetime_array is empty/None for instance ID {id(self)}")

        # Store magnetic field and temperature tensor for anisotropy calculation
        self.mag_field = imported_data.data['MAGF_INST']
        self.temp_tensor = imported_data.data['T_TENSOR_INST']
        
        # Extract data needed for calculations
        velocity = imported_data.data['VEL_RTN_SUN']
        density = imported_data.data['DENS']
        temperature = imported_data.data['TEMP']
        
        # Calculate velocity components and magnitude
        vr = velocity[:, 0]
        vt = velocity[:, 1]
        vn = velocity[:, 2]
        v_sw = np.sqrt(vr**2 + vt**2 + vn**2)
        
        # Calculate magnetic field magnitude
        b_mag = np.sqrt(np.sum(self.mag_field**2, axis=1))
        
        # Calculate Alfvén speed and Mach number
        with np.errstate(divide='ignore', invalid='ignore'):
            v_alfven = np.where(density > 0, 21.8 * b_mag / np.sqrt(density), np.nan)
        m_alfven = v_sw / v_alfven
        
        # Calculate temperature anisotropy components
        t_par, t_perp, anisotropy = self._calculate_temperature_anisotropy()
        
        # Calculate plasma betas
        beta_ppar = (4.03E-11 * density * t_par) / (1e-5 * b_mag)**2
        beta_pperp = (4.03E-11 * density * t_perp) / (1e-5 * b_mag)**2
        
        # Calculate pressures (in nPa)
        pressure_ppar = 1.602E-4 * density * t_par
        pressure_pperp = 1.602E-4 * density * t_perp
        pressure_total = 1.602E-4 * temperature * density

        # Distance from sun - Added from Jaye's version
        sun_dist_km = imported_data.data['SUN_DIST']
        sun_dist_rsun = sun_dist_km / 695700.0 # Conversion factor for solar radii

        # Get energy flux data
        # eflux_v_energy = imported_data.data['EFLUX_VS_ENERGY'] # Redundant
        # eflux_v_theta = imported_data.data['EFLUX_VS_THETA']   # Redundant
        # eflux_v_phi = imported_data.data['EFLUX_VS_PHI']     # Redundant

        # Extract specific components for spectral data
        self.energy_flux = imported_data.data['EFLUX_VS_ENERGY']
        self.energy_vals = imported_data.data['ENERGY_VALS']
        self.theta_flux = imported_data.data['EFLUX_VS_THETA']
        self.theta_vals = imported_data.data['THETA_VALS']
        self.phi_flux = imported_data.data['EFLUX_VS_PHI']
        self.phi_vals = imported_data.data['PHI_VALS']

        # Calculate spectral data time arrays
        # Simplified to directly use .shape[1], mirroring electron class calculate_variables assumption
        # Assumes self.energy_flux (etc.) are valid 2D arrays after assignment from imported_data.
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(self.energy_flux.shape[1]), # Use self.energy_flux directly
            indexing='ij'
        )[0]
        pm.processing(f"[PROTON_CALC_VARS] self.times_mesh (id: {id(self.times_mesh)}) created. Shape: {self.times_mesh.shape if self.times_mesh is not None else 'None'}. "
                      f"Time range (mesh[0,:]): {self.times_mesh[0,0]} to {self.times_mesh[0,-1]} " if self.times_mesh is not None and self.times_mesh.size > 0 and self.times_mesh.ndim == 2 and self.times_mesh.shape[0] > 0 and self.times_mesh.shape[1] > 0 else 
                      f"[PROTON_CALC_VARS] self.times_mesh is empty/None or not 2D as expected. Shape: {self.times_mesh.shape if hasattr(self.times_mesh, 'shape') else 'N/A'}")

        # Simplified for times_mesh_angle, mirroring electron class calculate_variables assumption
        # Assumes self.theta_flux (etc.) are valid 2D arrays after assignment from imported_data.
        self.times_mesh_angle = np.meshgrid(
            self.datetime_array,
            np.arange(self.theta_flux.shape[1]), # Use self.theta_flux directly
            indexing='ij'
        )[0]
        pm.processing(f"[PROTON_CALC_VARS] self.times_mesh_angle (id: {id(self.times_mesh_angle)}) created. Shape: {self.times_mesh_angle.shape if self.times_mesh_angle is not None else 'None'}. "
                      f"Time range (mesh[0,:]): {self.times_mesh_angle[0,0]} to {self.times_mesh_angle[0,-1]} " if self.times_mesh_angle is not None and self.times_mesh_angle.size > 0 and self.times_mesh_angle.ndim == 2 and self.times_mesh_angle.shape[0] > 0 and self.times_mesh_angle.shape[1] > 0 else 
                      f"[PROTON_CALC_VARS] self.times_mesh_angle is empty/None or not 2D as expected. Shape: {self.times_mesh_angle.shape if hasattr(self.times_mesh_angle, 'shape') else 'N/A'}")

        # Compute centroids
        centroids_spi_nrg = np.ma.average(self.energy_vals, 
                            weights=self.energy_flux, 
                            axis=1)
        centroids_spi_theta = np.ma.average(self.theta_vals, 
                            weights=self.theta_flux, 
                            axis=1)
        centroids_spi_phi = np.ma.average(self.phi_vals, 
                            weights=self.phi_flux, 
                            axis=1)

        # Store raw data including time
        self.raw_data = {
            'vr': vr,
            'vt': vt, 
            'vn': vn,
            't_par': t_par,
            't_perp': t_perp,
            'anisotropy': anisotropy,
            'v_alfven': v_alfven,
            'beta_ppar': beta_ppar,
            'beta_pperp': beta_pperp,
            'pressure_ppar': pressure_ppar,
            'pressure_pperp': pressure_pperp,
            'energy_flux': self.energy_flux,
            'theta_flux': self.theta_flux,
            'phi_flux': self.phi_flux,
            'v_sw': v_sw,
            'm_alfven': m_alfven,
            'temperature': temperature,
            'pressure': pressure_total,
            'density': density,
            'bmag': b_mag,
            'sun_dist_rsun': sun_dist_rsun,
            'ENERGY_VALS': self.energy_vals,
            'THETA_VALS': self.theta_vals,
            'PHI_VALS': self.phi_vals
        }

    def _calculate_temperature_anisotropy(self):
        """Calculate temperature anisotropy from the temperature tensor."""
        # Extract magnetic field components
        bx = self.mag_field[:, 0]
        by = self.mag_field[:, 1]
        bz = self.mag_field[:, 2]
        b_mag = np.sqrt(bx**2 + by**2 + bz**2)
        
        t_par = []
        t_perp = []
        anisotropy = []
        
        for i in range(len(bx)):
            # Extract tensor components
            t_xx = self.temp_tensor[i, 0]
            t_yy = self.temp_tensor[i, 1]
            t_zz = self.temp_tensor[i, 2]
            t_xy = t_yx = self.temp_tensor[i, 3]
            t_xz = t_zx = self.temp_tensor[i, 4]
            t_yz = t_zy = self.temp_tensor[i, 5]
            
            # Calculate parallel temperature using full tensor projection
            t_para = (bx[i]**2 * t_xx + by[i]**2 * t_yy + bz[i]**2 * t_zz +
                     2 * (bx[i]*by[i]*t_xy + bx[i]*bz[i]*t_xz + by[i]*bz[i]*t_yz)) / b_mag[i]**2
            
            # Calculate perpendicular temperature
            trace_temp = t_xx + t_yy + t_zz
            t_perp_val = (trace_temp - t_para) / 2.0
            
            t_par.append(t_para)
            t_perp.append(t_perp_val)
            if t_para != 0:
                anisotropy.append(t_perp_val/t_para)
            else:
                anisotropy.append(np.nan)  # or any other value that makes sense in your context
        
        return np.array(t_par), np.array(t_perp), np.array(anisotropy)

    def set_ploptions(self):
        """Set up the plotting options for all proton parameters"""
        print_manager.processing(f"[PROTON_SET_PLOPT ENTRY] id(self): {id(self)}")
        datetime_array_exists = hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0
        if datetime_array_exists:
            print_manager.processing(f"[PROTON_SET_PLOPT] self.datetime_array (id: {id(self.datetime_array)}) len: {len(self.datetime_array)}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}")
        else:
            print_manager.processing(f"[PROTON_SET_PLOPT] self.datetime_array does not exist, is None, or is empty for instance ID {id(self)}.")

        # Temperature components
        self.t_par = plot_manager(
            self.raw_data['t_par'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='t_par',
                class_name='proton',
                subclass_name='t_par',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Temp\n(eV)',
                y_limit=None,
                legend_label=r'$T_\parallel$',
                color='deepskyblue',
                y_scale='linear',
                line_width=1,
                line_style='-',
            )
        )
        
        self.t_perp = plot_manager(
            self.raw_data['t_perp'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='t_perp',
                class_name='proton',
                subclass_name='t_perp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Temp\n(eV)',
                legend_label=r'$T_\perp$',
                color='hotpink',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.anisotropy = plot_manager(
            self.raw_data['anisotropy'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='anisotropy',
                class_name='proton',
                subclass_name='anisotropy',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$T_\perp/T_\parallel$',     
                legend_label=r'$T_\perp/T_\parallel$',
                color='mediumspringgreen',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        # Velocities
        self.v_alfven = plot_manager(  
            self.raw_data['v_alfven'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='v_alfven_spi',
                class_name='proton',
                subclass_name='v_alfven',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{A}$ (km/s)',
                legend_label='$V_{A}$',
                color='deepskyblue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.v_sw = plot_manager(
            self.raw_data['v_sw'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='v_sw',
                class_name='proton',
                subclass_name='v_sw',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{SW}$ (km/s)',
                legend_label='$V_{SW}$',
                color='red',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.m_alfven = plot_manager(
            self.raw_data['m_alfven'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='m_alfven',
                class_name='proton',
                subclass_name='m_alfven',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$M_A$',
                legend_label='$M_A$',
                color='black',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'    
            )
        )
        
        # Plasma parameters
        self.beta_ppar = plot_manager(
            self.raw_data['beta_ppar'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='beta_ppar',
                class_name='proton',
                subclass_name='beta_ppar',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$\beta$',
                legend_label=r'$\beta_\parallel$',
                color='purple',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.beta_pperp = plot_manager(
            self.raw_data['beta_pperp'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='beta_pperp',
                class_name='proton',
                subclass_name='beta_pperp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$\beta$',
                legend_label=r'$\beta_\perp$',
                color='green',
                y_scale='log',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        # Pressures
        self.pressure_ppar = plot_manager(
            self.raw_data['pressure_ppar'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='pressure_ppar',
                class_name='proton',
                subclass_name='pressure_ppar',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pressure (nPa)',
                legend_label=r'$P_\parallel$',
                color='darkviolet',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.pressure_pperp = plot_manager(
            self.raw_data['pressure_pperp'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='pressure_pperp',
                class_name='proton',
                subclass_name='pressure_pperp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pressure (nPa)',
                legend_label=r'$P_\perp$',
                color='limegreen',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.pressure = plot_manager(
            self.raw_data['pressure'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='pressure',
                class_name='proton',
                subclass_name='pressure',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pressure (nPa)',
                legend_label='$P_{SPI}$',
                color='cyan',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        # Basic parameters
        self.density = plot_manager(
            self.raw_data['density'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='dens',
                class_name='proton',
                subclass_name='density',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Dens\n(cm$^{-3}$)',
                legend_label='n$_{SPI}$',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.temperature = plot_manager(
            self.raw_data['temperature'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='temp',
                class_name='proton',
                subclass_name='temperature',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Temp\n(eV)',
                legend_label='$T_{SPI}$',
                color='magenta',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='bmag',
                class_name='proton',
                subclass_name='bmag',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='|B| (nT)',
                legend_label='$|B|_{SPI}$',
                color='purple',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Velocity Components
        self.vr = plot_manager(
            self.raw_data['vr'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='vr',
                class_name='proton',
                subclass_name='vr',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_R$ (km/s)',
                legend_label='$V_R$',
                color='red',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.vt = plot_manager(
            self.raw_data['vt'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='vt',
                class_name='proton',
                subclass_name='vt',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_T$ (km/s)',
                legend_label='$V_T$',
                color='green',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.vn = plot_manager(
            self.raw_data['vn'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='vn',
                class_name='proton',
                subclass_name='vn',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_N$ (km/s)',
                legend_label='$V_N$',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Spectral Plots
        # --- Energy Flux ---
        print_manager.processing(f"[PROTON_SET_PLOPT] Preparing plot_manager for energy_flux. Instance ID {id(self)}.")
        # Check and regenerate times_mesh for energy_flux if necessary
        times_mesh_exists = hasattr(self, 'times_mesh') and self.times_mesh is not None
        raw_data_eflux_exists = hasattr(self, 'raw_data') and 'energy_flux' in self.raw_data and self.raw_data['energy_flux'] is not None and isinstance(self.raw_data['energy_flux'], np.ndarray)

        if times_mesh_exists and isinstance(self.times_mesh, np.ndarray) and raw_data_eflux_exists and datetime_array_exists:
            needs_regeneration_eflux = False
            expected_y_dim_eflux = self.raw_data['energy_flux'].shape[1] if self.raw_data['energy_flux'].ndim == 2 else 1

            if self.times_mesh.ndim != 2:
                needs_regeneration_eflux = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh for energy_flux is not 2D (shape: {self.times_mesh.shape}). Regenerating.")
            elif self.times_mesh.shape[0] != len(self.datetime_array):
                needs_regeneration_eflux = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh for energy_flux shape[0] ({self.times_mesh.shape[0]}) != len(datetime_array) ({len(self.datetime_array)}). Regenerating.")
            elif self.times_mesh.shape[1] != expected_y_dim_eflux:
                needs_regeneration_eflux = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh for energy_flux shape[1] ({self.times_mesh.shape[1]}) != expected data y_dim ({expected_y_dim_eflux}). Regenerating.")

            if needs_regeneration_eflux:
                print_manager.processing(f"[PROTON_SET_PLOPT] Regenerating times_mesh for energy_flux. Old shape: {self.times_mesh.shape if isinstance(self.times_mesh, np.ndarray) else 'N/A'}. Instance ID {id(self)}.")
                self.times_mesh = np.meshgrid(
                    self.datetime_array,
                    np.arange(expected_y_dim_eflux),
                    indexing='ij'
                )[0]
                print_manager.processing(f"[PROTON_SET_PLOPT] Regenerated times_mesh for energy_flux. New shape: {self.times_mesh.shape}. Instance ID {id(self)}.")
        elif not datetime_array_exists and hasattr(self, 'times_mesh'): # If datetime_array is bad, times_mesh should be empty
             self.times_mesh = np.array([])
             print_manager.warning(f"[PROTON_SET_PLOPT] datetime_array is not valid, ensuring times_mesh for energy_flux is empty. Instance ID {id(self)}.")


        # Log state of times_mesh before passing to plot_manager
        current_times_mesh_to_pass = self.times_mesh if hasattr(self, 'times_mesh') else None
        if current_times_mesh_to_pass is not None and isinstance(current_times_mesh_to_pass, np.ndarray):
            shape_str_tm = str(current_times_mesh_to_pass.shape)
            time_range_str_tm = "N/A or not applicable for 0/1D"
            if current_times_mesh_to_pass.ndim == 2 and current_times_mesh_to_pass.shape[0] > 0 and current_times_mesh_to_pass.shape[1] > 0:
                time_range_str_tm = f"{current_times_mesh_to_pass[0,0]} to {current_times_mesh_to_pass[0,-1]}"
            
            print_manager.processing(f"[PROTON_SET_PLOPT] plot_manager for energy_flux gets datetime_array (is self.times_mesh, id: {id(current_times_mesh_to_pass)}). Shape: {shape_str_tm}. Time range (mesh[0,:]): {time_range_str_tm}. Instance ID {id(self)}.")
        else:
            print_manager.processing(f"[PROTON_SET_PLOPT] plot_manager for energy_flux gets datetime_array (self.times_mesh) that is None or not an ndarray. Value: {current_times_mesh_to_pass}. Instance ID {id(self)}.")

        self.energy_flux = plot_manager(
            self.raw_data['energy_flux'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='energy_flux',
                class_name='proton',
                subclass_name='energy_flux',
                plot_type='spectral',
                datetime_array=self.times_mesh,
                y_label='Proton\\nEnergy\\nFlux (eV)',
                legend_label='Proton Energy Flux',
                color='black',
                y_scale='log',
                y_limit=[50, 5000],
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['ENERGY_VALS'],
                colormap='jet',
                colorbar_scale='log'
            )
        )

        # --- Theta Flux & Phi Flux ---
        print_manager.processing(f"[PROTON_SET_PLOPT] Preparing plot_managers for theta_flux and phi_flux. Instance ID {id(self)}.")
        # Check and regenerate times_mesh_angle if necessary
        times_mesh_angle_exists = hasattr(self, 'times_mesh_angle') and self.times_mesh_angle is not None
        # Assuming theta_flux is representative for raw_data check, or use a combined check
        raw_data_tflux_exists = hasattr(self, 'raw_data') and 'theta_flux' in self.raw_data and self.raw_data['theta_flux'] is not None and isinstance(self.raw_data['theta_flux'], np.ndarray)

        if times_mesh_angle_exists and isinstance(self.times_mesh_angle, np.ndarray) and raw_data_tflux_exists and datetime_array_exists:
            needs_regeneration_angle = False
            # Use theta_flux's shape for expected y-dimension for times_mesh_angle
            expected_y_dim_angle = self.raw_data['theta_flux'].shape[1] if self.raw_data['theta_flux'].ndim == 2 else 1

            if self.times_mesh_angle.ndim != 2:
                needs_regeneration_angle = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh_angle is not 2D (shape: {self.times_mesh_angle.shape}). Regenerating.")
            elif self.times_mesh_angle.shape[0] != len(self.datetime_array):
                needs_regeneration_angle = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh_angle shape[0] ({self.times_mesh_angle.shape[0]}) != len(datetime_array) ({len(self.datetime_array)}). Regenerating.")
            elif self.times_mesh_angle.shape[1] != expected_y_dim_angle:
                needs_regeneration_angle = True
                print_manager.processing(f"[PROTON_SET_PLOPT] times_mesh_angle shape[1] ({self.times_mesh_angle.shape[1]}) != expected data y_dim ({expected_y_dim_angle}). Regenerating.")

            if needs_regeneration_angle:
                print_manager.processing(f"[PROTON_SET_PLOPT] Regenerating times_mesh_angle. Old shape: {self.times_mesh_angle.shape if isinstance(self.times_mesh_angle, np.ndarray) else 'N/A'}. Instance ID {id(self)}.")
                self.times_mesh_angle = np.meshgrid(
                    self.datetime_array,
                    np.arange(expected_y_dim_angle),
                    indexing='ij'
                )[0]
                print_manager.processing(f"[PROTON_SET_PLOPT] Regenerated times_mesh_angle. New shape: {self.times_mesh_angle.shape}. Instance ID {id(self)}.")
        elif not datetime_array_exists and hasattr(self, 'times_mesh_angle'): # If datetime_array is bad, times_mesh_angle should be empty
            self.times_mesh_angle = np.array([])
            print_manager.warning(f"[PROTON_SET_PLOPT] datetime_array is not valid, ensuring times_mesh_angle is empty. Instance ID {id(self)}.")


        # Log state of times_mesh_angle before passing to plot_managers
        current_times_mesh_angle_to_pass = self.times_mesh_angle if hasattr(self, 'times_mesh_angle') else None
        if current_times_mesh_angle_to_pass is not None and isinstance(current_times_mesh_angle_to_pass, np.ndarray):
            shape_str_tma = str(current_times_mesh_angle_to_pass.shape)
            time_range_str_tma = "N/A or not applicable for 0/1D"
            if current_times_mesh_angle_to_pass.ndim == 2 and current_times_mesh_angle_to_pass.shape[0] > 0 and current_times_mesh_angle_to_pass.shape[1] > 0:
                time_range_str_tma = f"{current_times_mesh_angle_to_pass[0,0]} to {current_times_mesh_angle_to_pass[0,-1]}"

            print_manager.processing(f"[PROTON_SET_PLOPT] plot_managers for theta/phi_flux get datetime_array (is self.times_mesh_angle, id: {id(current_times_mesh_angle_to_pass)}). Shape: {shape_str_tma}. Time range (mesh[0,:]): {time_range_str_tma}. Instance ID {id(self)}.")
        else:
            print_manager.processing(f"[PROTON_SET_PLOPT] plot_managers for theta/phi_flux get datetime_array (self.times_mesh_angle) that is None or not an ndarray. Value: {current_times_mesh_angle_to_pass}. Instance ID {id(self)}.")

        self.theta_flux = plot_manager(
            self.raw_data['theta_flux'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='theta_flux',
                class_name='proton',
                subclass_name='theta_flux',
                plot_type='spectral',
                datetime_array=self.times_mesh_angle,
                y_label='Theta (degrees)',
                legend_label='Proton Theta Flux',
                color='black',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['THETA_VALS'],
                colormap='jet',
                colorbar_scale='log'
            )
        )

        self.phi_flux = plot_manager(
            self.raw_data['phi_flux'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='phi_flux',
                class_name='proton',
                subclass_name='phi_flux',
                plot_type='spectral',
                datetime_array=self.times_mesh_angle,
                y_label='Phi (degrees)',
                legend_label='Proton Phi Flux',
                color='black',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.raw_data['PHI_VALS'],
                colormap='jet',
                colorbar_scale='log'
            )
        )

        # Added Sun Distance variable
        self.sun_dist_rsun = plot_manager(
            self.raw_data['sun_dist_rsun'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='sun_dist_rsun',
                class_name='proton',
                subclass_name='sun_dist_rsun',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Sun Distance \n ($R_s$)', # Using solar radii units
                legend_label='$R_s$',
                color='goldenrod', # Distinct color for sun distance
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

proton = proton_class(None) #Initialize the class with no data
print('initialized proton class') 