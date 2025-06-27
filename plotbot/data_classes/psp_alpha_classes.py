import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
from typing import Optional, List

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

class psp_alpha_class:    
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'vel_inst_x': None,  # Velocity components (instrument frame)
            'vel_inst_y': None,
            'vel_inst_z': None,
            'vel_sc_x': None,    # Velocity components (spacecraft frame)
            'vel_sc_y': None,
            'vel_sc_z': None,
            'vr': None,          # RTN velocity components
            'vt': None,
            'vn': None,
            't_par': None,       # Temperature parallel
            't_perp': None,      # Temperature perpendicular
            'anisotropy': None,  # Temperature anisotropy
            'v_alfven': None,    # Alfven speed
            'beta_ppar': None,   # Plasma beta parallel
            'beta_pperp': None,  # Plasma beta perpendicular
            'pressure_ppar': None,    # Pressure parallel
            'pressure_pperp': None,   # Pressure perpendicular
            'energy_flux': None,      # Energy flux spectrogram
            'theta_flux': None,       # Theta flux spectrogram
            'phi_flux': None,         # Phi flux spectrogram
            'v_sw': None,            # Solar wind speed magnitude
            'm_alfven': None,        # Alfven Mach number
            'temperature': None,     # Scalar temperature
            'pressure': None,        # Total pressure
            'density': None,         # Alpha density
            'bmag': None,           # Magnetic field magnitude
            'sun_dist_rsun': None,  # Distance from Sun in solar radii
            'ENERGY_VALS': None,    # Energy bin values
            'THETA_VALS': None,     # Theta bin values
            'PHI_VALS': None        # Phi bin values
        })
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'times_mesh_angle', [])
        object.__setattr__(self, 'energy_vals', None)
        object.__setattr__(self, 'theta_vals', None)
        object.__setattr__(self, 'phi_vals', None)
        object.__setattr__(self, 'data_type', 'spi_sf0a_l3_mom')
        object.__setattr__(self, '_current_operation_trange', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.debug("Calculating alpha variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated alpha variables.")

    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data."""
        if original_requested_trange is not None:
            object.__setattr__(self, '_current_operation_trange', original_requested_trange)
            print_manager.dependency_management(f"[{self.__class__.__name__}] Updated _current_operation_trange to: {self._current_operation_trange}")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        # Check with DataTracker before recalculating
        from plotbot.data_tracker import global_tracker
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

        print_manager.datacubby("\n=== Alpha Update Debug ===")
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
        
        print_manager.datacubby("=== End Alpha Update Debug ===\n")

    def get_subclass(self, subclass_name):
        """Retrieve a specific component"""
        print_manager.debug(f"Getting subclass: {subclass_name}")
        if subclass_name in self.raw_data.keys():
            print_manager.debug(f"Returning {subclass_name} component")
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
            print_manager.error(f"[ALPHA_GETATTR_ERROR] raw_data not initialized for {self.__class__.__name__} instance when trying to get '{name}'")
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' (raw_data not initialized)")
        
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print_manager.dependency_management(f"[ALPHA_GETATTR] Attribute '{name}' not found directly. Known raw_data keys: {available_attrs}")
        print_manager.warning(f"[ALPHA_GETATTR] '{name}' is not a recognized attribute, friend!")
        print_manager.warning(f"Try one of these: {', '.join(available_attrs)}")
        return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        if name in ['datetime_array', 'raw_data', 'time', 'field', 'mag_field', 'temp_tensor', 'energy_flux', 'theta_flux', 'phi_flux', 'energy_vals', 'theta_vals', 'phi_vals', 'times_mesh', 'times_mesh_angle', 'data_type'] or \
           (hasattr(self, 'raw_data') and isinstance(self.raw_data, dict) and name in self.raw_data) or \
           (hasattr(self, name) and not callable(getattr(self, name))):
            object.__setattr__(self, name, value)
        else:
            print_manager.warning(f"[ALPHA_SETATTR] Attribute '{name}' is not explicitly defined in settable list for {self.__class__.__name__}.")
            available_attrs = list(getattr(self, 'raw_data', {}).keys()) + ['datetime_array', 'time', 'field', 'mag_field', 'temp_tensor', 'energy_flux', 'theta_flux', 'phi_flux', 'energy_vals', 'theta_vals', 'phi_vals', 'times_mesh', 'times_mesh_angle', 'data_type']
            print(f"[ALPHA_SETATTR] '{name}' is not a recognized settable attribute, friend!")
            print(f"Known data keys and core attributes: {', '.join(list(set(available_attrs)))}")
            object.__setattr__(self, name, value)

    def calculate_variables(self, imported_data):
        """Calculate the alpha particle parameters and derived quantities."""
        pm = print_manager
        pm.dependency_management(f"[ALPHA_CALC_VARS_ENTRY] Instance ID {id(self)} calculating variables. Imported data time type: {type(getattr(imported_data, 'times', None))}")

        # Extract time and field data
        self.time = imported_data.times
        
        pm.processing(f"[ALPHA_CALC_VARS] About to create self.datetime_array from self.time (len: {len(self.time) if self.time is not None else 'None'}) for instance ID {id(self)}")
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        pm.processing(f"[ALPHA_CALC_VARS] self.datetime_array created. len: {len(self.datetime_array) if self.datetime_array is not None else 'None'}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}" if self.datetime_array is not None and len(self.datetime_array) > 0 else f"[ALPHA_CALC_VARS] self.datetime_array is empty/None for instance ID {id(self)}")

        # Store magnetic field and temperature tensor for anisotropy calculation
        self.mag_field = imported_data.data['MAGF_INST']
        self.temp_tensor = imported_data.data['T_TENSOR_INST']
        
        # Extract data needed for calculations
        velocity_inst = imported_data.data['VEL_INST']
        velocity_sc = imported_data.data['VEL_SC']
        velocity_rtn = imported_data.data['VEL_RTN_SUN']
        density = imported_data.data['DENS']
        temperature = imported_data.data['TEMP']
        
        # Calculate velocity components
        vel_inst_x = velocity_inst[:, 0]
        vel_inst_y = velocity_inst[:, 1]
        vel_inst_z = velocity_inst[:, 2]
        vel_sc_x = velocity_sc[:, 0]
        vel_sc_y = velocity_sc[:, 1]
        vel_sc_z = velocity_sc[:, 2]
        vr = velocity_rtn[:, 0]
        vt = velocity_rtn[:, 1]
        vn = velocity_rtn[:, 2]
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

        # Distance from sun
        sun_dist_km = imported_data.data['SUN_DIST']
        sun_dist_rsun = sun_dist_km / 695700.0

        # Get energy flux data
        self.energy_flux = imported_data.data['EFLUX_VS_ENERGY']
        self.energy_vals = imported_data.data['ENERGY_VALS']
        self.theta_flux = imported_data.data['EFLUX_VS_THETA']
        self.theta_vals = imported_data.data['THETA_VALS']
        self.phi_flux = imported_data.data['EFLUX_VS_PHI']
        self.phi_vals = imported_data.data['PHI_VALS']

        # Calculate spectral data time arrays
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(self.energy_flux.shape[1]),
            indexing='ij'
        )[0]
        pm.processing(f"[ALPHA_CALC_VARS] self.times_mesh created. Shape: {self.times_mesh.shape if self.times_mesh is not None else 'None'}")

        self.times_mesh_angle = np.meshgrid(
            self.datetime_array,
            np.arange(self.theta_flux.shape[1]),
            indexing='ij'
        )[0]
        pm.processing(f"[ALPHA_CALC_VARS] self.times_mesh_angle created. Shape: {self.times_mesh_angle.shape if self.times_mesh_angle is not None else 'None'}")

        # Store raw data
        self.raw_data = {
            'vel_inst_x': vel_inst_x,
            'vel_inst_y': vel_inst_y,
            'vel_inst_z': vel_inst_z,
            'vel_sc_x': vel_sc_x,
            'vel_sc_y': vel_sc_y,
            'vel_sc_z': vel_sc_z,
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
                anisotropy.append(np.nan)
        
        return np.array(t_par), np.array(t_perp), np.array(anisotropy)

    def set_ploptions(self):
        """Set up the plotting options for all alpha particle parameters"""
        print_manager.processing(f"[ALPHA_SET_PLOPT ENTRY] id(self): {id(self)}")
        datetime_array_exists = hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0
        
        if datetime_array_exists:
            print_manager.processing(f"[ALPHA_SET_PLOPT] self.datetime_array len: {len(self.datetime_array)}. Range: {self.datetime_array[0]} to {self.datetime_array[-1]}")
        else:
            print_manager.processing(f"[ALPHA_SET_PLOPT] self.datetime_array does not exist, is None, or is empty for instance ID {id(self)}.")

        # Basic parameters with alpha-specific styling
        self.density = plot_manager(
            self.raw_data['density'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='dens',
                class_name='psp_alpha',
                subclass_name='density',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Dens\n(cm$^{-3}$)',
                legend_label='n$_{\\alpha}$',
                color='darkorange',  # Distinct alpha color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.temperature = plot_manager(
            self.raw_data['temperature'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='temp',
                class_name='psp_alpha',
                subclass_name='temperature',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Temp\n(eV)',
                legend_label='$T_{\\alpha}$',
                color='firebrick',  # Distinct alpha color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Velocity Components (RTN)
        self.vr = plot_manager(
            self.raw_data['vr'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='vr',
                class_name='psp_alpha',
                subclass_name='vr',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{R,\\alpha}$ (km/s)',
                legend_label='$V_{R,\\alpha}$',
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
                data_type='spi_sf0a_l3_mom',
                var_name='vt',
                class_name='psp_alpha',
                subclass_name='vt',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{T,\\alpha}$ (km/s)',
                legend_label='$V_{T,\\alpha}$',
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
                data_type='spi_sf0a_l3_mom',
                var_name='vn',
                class_name='psp_alpha',
                subclass_name='vn',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{N,\\alpha}$ (km/s)',
                legend_label='$V_{N,\\alpha}$',
                color='blue',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Temperature components
        self.t_par = plot_manager(
            self.raw_data['t_par'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='t_par',
                class_name='psp_alpha',
                subclass_name='t_par',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Temp\n(eV)',
                legend_label=r'$T_{\parallel,\alpha}$',
                color='lightcoral',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
            )
        )
        
        self.t_perp = plot_manager(
            self.raw_data['t_perp'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='t_perp',
                class_name='psp_alpha',
                subclass_name='t_perp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Temp\n(eV)',
                legend_label=r'$T_{\perp,\alpha}$',
                color='gold',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        
        self.anisotropy = plot_manager(
            self.raw_data['anisotropy'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='anisotropy',
                class_name='psp_alpha',
                subclass_name='anisotropy',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$T_{\perp}/T_{\parallel}$ Alpha',     
                legend_label=r'$T_{\perp}/T_{\parallel,\alpha}$',
                color='orange',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Solar wind speed and Alfven parameters
        self.v_sw = plot_manager(
            self.raw_data['v_sw'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='v_sw',
                class_name='psp_alpha',
                subclass_name='v_sw',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_{SW,\\alpha}$ (km/s)',
                legend_label='$V_{SW,\\alpha}$',
                color='darkred',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Distance from sun
        self.sun_dist_rsun = plot_manager(
            self.raw_data['sun_dist_rsun'],
            plot_options=ploptions(
                data_type='spi_sf0a_l3_mom',
                var_name='sun_dist_rsun',
                class_name='psp_alpha',
                subclass_name='sun_dist_rsun',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Sun Distance \n ($R_s$)',
                legend_label='$R_s$',
                color='goldenrod',
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
psp_alpha = psp_alpha_class(None)
print('initialized psp_alpha class')
