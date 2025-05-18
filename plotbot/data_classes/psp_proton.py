# plotbot/data_classes/psp_proton.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

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
            'sun_dist_rsun': None  # Remains None initially
        })
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'times_mesh_angle', [])
        object.__setattr__(self, 'energy_vals', None)
        object.__setattr__(self, 'theta_vals', None)
        object.__setattr__(self, 'phi_vals', None)
        object.__setattr__(self, 'data_type', 'spi_sf00_l3_mom')

        # Attributes for lazy loading sun_dist_rsun
        object.__setattr__(self, '_sun_dist_km_raw', None)
        object.__setattr__(self, '_sun_dist_rsun_calculated_flag', False)
        object.__setattr__(self, '_sun_dist_rsun_plot_manager', None)

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
    def update(self, imported_data): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
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
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
            return getattr(self, subclass_name)  # Return the component
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

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.debug('proton getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print(f"'{name}' is not a recognized attribute, friend!")
        print(f"Try one of these: {', '.join(available_attrs)}")
        return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(f"Setting attribute: {name} with value: {value}")
        if name in ['datetime_array', 'raw_data', 'time', 'field', 'mag_field', 'temp_tensor', 'energy_flux', 'theta_flux', 'phi_flux', 'energy_vals', 'theta_vals', 'phi_vals', 'times_mesh', 'times_mesh_angle', 'data_type'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print('proton setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")

    def calculate_variables(self, imported_data):
        """Calculate the proton parameters and derived quantities."""
        # Extract time and field data
        self.time = imported_data.times
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))  # Use cdflib instead of pandas
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

        # Store raw sun distance data for lazy calculation
        self._sun_dist_km_raw = imported_data.data.get('SUN_DIST')
        self._sun_dist_rsun_calculated_flag = False # Reset flag on new data

        # Get energy flux data
        eflux_v_energy = imported_data.data['EFLUX_VS_ENERGY']
        eflux_v_theta = imported_data.data['EFLUX_VS_THETA']
        eflux_v_phi = imported_data.data['EFLUX_VS_PHI']

        # Extract specific components for spectral data
        self.energy_flux = imported_data.data['EFLUX_VS_ENERGY']
        self.energy_vals = imported_data.data['ENERGY_VALS']
        self.theta_flux = imported_data.data['EFLUX_VS_THETA']
        self.theta_vals = imported_data.data['THETA_VALS']
        self.phi_flux = imported_data.data['EFLUX_VS_PHI']
        self.phi_vals = imported_data.data['PHI_VALS']

        # Calculate spectral data time arrays
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(32),
            indexing='ij'
        )[0]

        self.times_mesh_angle = np.meshgrid(
            self.datetime_array,
            np.arange(8),
            indexing='ij'
        )[0]

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
            'sun_dist_rsun': None # Initialize as None, will be populated by lazy loader
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

    def _ensure_sun_dist_calculated(self):
        """Calculates sun_dist_rsun if raw data is available and it hasn't been calculated yet."""
        if not self._sun_dist_rsun_calculated_flag and \
           self._sun_dist_km_raw is not None and \
           self.datetime_array is not None: # Ensure datetime_array is also available

            # Perform the calculation
            calculated_value = self._sun_dist_km_raw / 695700.0
            
            # Ensure calculated_value is a proper array with correct shape
            if np.isscalar(calculated_value) or getattr(calculated_value, 'ndim', 0) == 0:
                print_manager.dependency_management(f"PROTON: Converting scalar sun_dist_rsun {calculated_value} to array with shape matching datetime_array ({len(self.datetime_array)})")
                # Create an array of the same value with the length of datetime_array
                calculated_value = np.full(len(self.datetime_array), calculated_value)
            
            self.raw_data['sun_dist_rsun'] = calculated_value

            # Update the plot_manager instance with the new data
            if self._sun_dist_rsun_plot_manager is not None:
                self._sun_dist_rsun_plot_manager.data = calculated_value
                # Ensure the plot_manager's datetime_array is consistent
                self._sun_dist_rsun_plot_manager.datetime_array = self.datetime_array
            else:
                # This case should ideally not be hit if set_ploptions ran correctly
                print_manager.warning("proton_class: _sun_dist_rsun_plot_manager was None during lazy calculation.")
                
                # Define SafePlotManager class here instead of trying to get it from property
                class SafePlotManager(plot_manager):
                    def __new__(cls, input_array, plot_options=None):
                        # Get the actual ndarray view from plot_manager's __new__
                        obj = plot_manager.__new__(cls, input_array, plot_options)
                        # Store a reference to the proton class for accessing raw_data
                        obj._proton_instance = proton
                        return obj
                        
                    def __array_finalize__(self, obj):
                        # Call parent's array_finalize to set up all required attributes
                        plot_manager.__array_finalize__(self, obj)
                        # Add our custom attribute if not already present
                        if not hasattr(self, '_proton_instance'):
                            self._proton_instance = getattr(obj, '_proton_instance', proton)
                            
                    def __array__(self, dtype=None):
                        """Override to ensure we always return the raw_data array directly."""
                        # First try to use the raw_data array which has the correct shape
                        if (hasattr(self._proton_instance, 'raw_data') and 
                            self._proton_instance.raw_data is not None and 
                            'sun_dist_rsun' in self._proton_instance.raw_data and 
                            self._proton_instance.raw_data['sun_dist_rsun'] is not None):
                            
                            print_manager.dependency_management(f"SafePlotManager: Using raw_data array with shape {self._proton_instance.raw_data['sun_dist_rsun'].shape}")
                            # Use the raw data array directly for plotting
                            return np.asarray(self._proton_instance.raw_data['sun_dist_rsun'], dtype=dtype)
                        
                        # Fallback to original data
                        arr = np.asarray(self.view(np.ndarray), dtype=dtype)
                        if arr.ndim == 0:  # If it's a scalar (0-dimensional array)
                            print_manager.dependency_management("SafePlotManager: Converting scalar to 1D array")
                            # Convert to 1D array with 1 element
                            return np.array([arr.item()], dtype=dtype)
                        return arr

                    # Override to handle 2D indexing when used in Plotbot
                    def __getitem__(self, key):
                        # Prioritize using raw_data for indexing
                        if (hasattr(self._proton_instance, 'raw_data') and 
                            self._proton_instance.raw_data is not None and 
                            'sun_dist_rsun' in self._proton_instance.raw_data and 
                            self._proton_instance.raw_data['sun_dist_rsun'] is not None):
                            
                            raw_arr = self._proton_instance.raw_data['sun_dist_rsun']
                            
                            # Handle 2D indexing case
                            if isinstance(key, tuple) and len(key) == 2:
                                return raw_arr[key[1]]
                            
                            # Normal indexing
                            return raw_arr[key]
                        
                        # Handle case where Plotbot tries to slice with [rows, cols]
                        if isinstance(key, tuple) and len(key) == 2:
                            print_manager.dependency_management(f"SafePlotManager: Got 2D indexing {key}, using just second part")
                            # Just use the second part of the index (the columns/time indices)
                            if self.ndim == 1:
                                return super().__getitem__(key[1])
                        # Otherwise use normal indexing
                        return super().__getitem__(key)
                
                # Create a new SafePlotManager instance
                self._sun_dist_rsun_plot_manager = SafePlotManager(
                    calculated_value,
                    plot_options=ploptions(
                        data_type='spi_sf00_l3_mom',
                        var_name='sun_dist_rsun',
                        class_name='proton',
                        subclass_name='sun_dist_rsun',
                        plot_type='time_series',
                        datetime_array=self.datetime_array,
                        y_label='Sun Distance \\n ($R_s$)',
                        legend_label='$R_s$',
                        color='goldenrod',
                        y_scale='linear',
                        line_width=1,
                        line_style='-'
                    )
                )
            self._sun_dist_rsun_calculated_flag = True
            print_manager.debug(f"Lazily calculated sun_dist_rsun for {self.data_type}")

    @property
    def sun_dist_rsun(self):
        """Property to lazily calculate and return the sun_dist_rsun plot_manager."""
        self._ensure_sun_dist_calculated() # Ensure it's calculated on access

        # Debug output to verify data before plotting
        print_manager.dependency_management(f"DEBUG CRITICAL: sun_dist_rsun property accessed, raw_data['sun_dist_rsun']: shape={self.raw_data['sun_dist_rsun'].shape if self.raw_data['sun_dist_rsun'] is not None else 'None'}, type={type(self.raw_data['sun_dist_rsun'])}")
        
        # Define the SafePlotManager class if it doesn't exist yet
        if not hasattr(self, '_SafePlotManager'):
            class SafePlotManager(plot_manager):
                def __new__(cls, input_array, plot_options=None):
                    # Get the actual ndarray view from plot_manager's __new__
                    obj = plot_manager.__new__(cls, input_array, plot_options)
                    # Store a reference to the proton class for accessing raw_data
                    obj._proton_instance = proton
                    return obj
                    
                def __array_finalize__(self, obj):
                    # Call parent's array_finalize to set up all required attributes
                    plot_manager.__array_finalize__(self, obj)
                    # Add our custom attribute if not already present
                    if not hasattr(self, '_proton_instance'):
                        self._proton_instance = getattr(obj, '_proton_instance', proton)
                
                def __array__(self, dtype=None):
                    """Override to ensure we always return the raw_data array directly."""
                    # First try to use the raw_data array which has the correct shape
                    if (hasattr(self._proton_instance, 'raw_data') and 
                        self._proton_instance.raw_data is not None and 
                        'sun_dist_rsun' in self._proton_instance.raw_data and 
                        self._proton_instance.raw_data['sun_dist_rsun'] is not None):
                        
                        print_manager.dependency_management(f"SafePlotManager: Using raw_data array with shape {self._proton_instance.raw_data['sun_dist_rsun'].shape}")
                        # Use the raw data array directly for plotting
                        return np.asarray(self._proton_instance.raw_data['sun_dist_rsun'], dtype=dtype)
                    
                    # Fallback to original data
                    arr = np.asarray(self.view(np.ndarray), dtype=dtype)
                    if arr.ndim == 0:  # If it's a scalar (0-dimensional array)
                        print_manager.dependency_management("SafePlotManager: Converting scalar to 1D array")
                        # Convert to 1D array with 1 element
                        return np.array([arr.item()], dtype=dtype)
                    return arr

                # Override to handle 2D indexing when used in Plotbot
                def __getitem__(self, key):
                    # Prioritize using raw_data for indexing
                    if (hasattr(self._proton_instance, 'raw_data') and 
                        self._proton_instance.raw_data is not None and 
                        'sun_dist_rsun' in self._proton_instance.raw_data and 
                        self._proton_instance.raw_data['sun_dist_rsun'] is not None):
                        
                        raw_arr = self._proton_instance.raw_data['sun_dist_rsun']
                        
                        # Handle 2D indexing case
                        if isinstance(key, tuple) and len(key) == 2:
                            return raw_arr[key[1]]
                        
                        # Normal indexing
                        return raw_arr[key]
                    
                    # Handle case where Plotbot tries to slice with [rows, cols]
                    if isinstance(key, tuple) and len(key) == 2:
                        print_manager.dependency_management(f"SafePlotManager: Got 2D indexing {key}, using just second part")
                        # Just use the second part of the index (the columns/time indices)
                        if self.ndim == 1:
                            return super().__getitem__(key[1])
                    # Otherwise use normal indexing
                    return super().__getitem__(key)
                    
            # Store the class for future use
            self._SafePlotManager = SafePlotManager

        if self._sun_dist_rsun_plot_manager is None:
            # This might happen if set_ploptions hasn't run or had an issue
            # For safety, try to initialize it if it's None, using raw_data for sun_dist_rsun
            print_manager.dependency_management("proton_class: sun_dist_rsun plot_manager accessed before full initialization or was None. Attempting to create.")
            
            # Use the raw data directly if available
            data_to_use = self.raw_data.get('sun_dist_rsun', np.array([0.0]))
            
            # Use our custom SafePlotManager instead of plot_manager
            self._sun_dist_rsun_plot_manager = self._SafePlotManager(
                data_to_use,
                plot_options=ploptions(
                    data_type='spi_sf00_l3_mom',
                    var_name='sun_dist_rsun',
                    class_name='proton',
                    subclass_name='sun_dist_rsun',
                    plot_type='time_series',
                    datetime_array=self.datetime_array,
                    y_label='Sun Distance \\n ($R_s$)',
                    legend_label='$R_s$',
                    color='goldenrod',
                    y_scale='linear',
                    line_width=1,
                    line_style='-'
                )
            )
        elif not isinstance(self._sun_dist_rsun_plot_manager, self._SafePlotManager):
            # If it exists but isn't our safe version, replace it with the safe version
            print_manager.dependency_management("Converting existing sun_dist_rsun to SafePlotManager")
            data = np.array(self._sun_dist_rsun_plot_manager)
            options = self._sun_dist_rsun_plot_manager.plot_options
            self._sun_dist_rsun_plot_manager = self._SafePlotManager(data, plot_options=options)

        return self._sun_dist_rsun_plot_manager

    def set_ploptions(self):
        """Set up the plotting options for all proton parameters"""
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
        self.energy_flux = plot_manager(
            self.raw_data['energy_flux'],
            plot_options=ploptions(
                data_type='spi_sf00_l3_mom',
                var_name='energy_flux',
                class_name='proton',
                subclass_name='energy_flux',
                plot_type='spectral',
                datetime_array=self.times_mesh,
                y_label='Proton\nEnergy\nFlux (eV)',
                legend_label='Proton Energy Flux',
                color='black',
                y_scale='log',
                y_limit=[50, 5000],
                line_width=1,
                line_style='-',
                additional_data=self.energy_vals,
                colormap='jet',
                colorbar_scale='log'
            )
        )

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
                additional_data=self.theta_vals,
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
                additional_data=self.phi_vals,
                colormap='jet',
                colorbar_scale='log'
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