import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
from typing import Optional, List

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config, retrieve_plot_config_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

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
            'PHI_VALS': None,       # Phi bin values
            # --- NEW: Alpha/Proton Derived Variables ---
            'na_div_np': None,      # Alpha/proton density ratio
            'ap_drift': None,       # Alpha-proton drift speed |VEL_alpha - VEL_proton|
            'ap_drift_va': None,    # Drift speed normalized by Alfvén speed
        })
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'time', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'times_mesh_angle', [])
        object.__setattr__(self, 'energy_vals', None)
        object.__setattr__(self, 'theta_vals', None)
        object.__setattr__(self, 'phi_vals', None)
        object.__setattr__(self, 'data_type', 'spi_sf0a_l3_mom')
        # --- ADD: Dependency Management Infrastructure ---
        object.__setattr__(self, '_current_operation_trange', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_plot_config()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided
            print_manager.debug("Calculating alpha variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status("Successfully calculated alpha variables.")

    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data."""
        # --- ADD: Store dependency management trange ---
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
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_plot_config_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_plot_config()
        
        # Restore state
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(var.plot_config, attr):
                        setattr(var.plot_config, attr, value)
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_plot_config_snapshot(state)}")
        
        print_manager.datacubby("=== End Alpha Update Debug ===\n")

    def get_subclass(self, subclass_name):
        """
        Retrieves a specific data component (subclass) by its name.
        
        Args:
            subclass_name (str): The name of the component to retrieve.
            
        Returns:
            The requested component, or None if not found.
        """
        print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[ALPHA_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[ALPHA_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
            'PHI_VALS': self.phi_vals,
            'na_div_np': None,      # Alpha/proton density ratio
            'ap_drift': None,       # Alpha-proton drift speed |VEL_alpha - VEL_proton|
            'ap_drift_va': None,    # Drift speed normalized by Alfvén speed
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

    def set_plot_config(self):
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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='dens',
                class_name='psp_alpha',
                subclass_name='density',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='temp',
                class_name='psp_alpha',
                subclass_name='temperature',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='vr',
                class_name='psp_alpha',
                subclass_name='vr',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='vt',
                class_name='psp_alpha',
                subclass_name='vt',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='vn',
                class_name='psp_alpha',
                subclass_name='vn',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='t_par',
                class_name='psp_alpha',
                subclass_name='t_par',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='t_perp',
                class_name='psp_alpha',
                subclass_name='t_perp',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='anisotropy',
                class_name='psp_alpha',
                subclass_name='anisotropy',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='v_sw',
                class_name='psp_alpha',
                subclass_name='v_sw',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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
            plot_config=plot_config(
                data_type='spi_sf0a_l3_mom',
                var_name='sun_dist_rsun',
                class_name='psp_alpha',
                subclass_name='sun_dist_rsun',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,

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

    # --- ADD: Alpha/Proton Derived Variables as Properties ---
    
    @property
    def na_div_np(self):
        """Alpha/proton density ratio with lazy loading and dependency management."""
        print_manager.dependency_management(f"[NA_DIV_NP_PROPERTY ENTRY] Accessing na_div_np for instance ID: {id(self)}")
        
        # Store the plot_manager in a private attribute
        if not hasattr(self, '_na_div_np_manager'):
            print_manager.dependency_management("[NA_DIV_NP_PROPERTY] Creating initial placeholder manager")
            # Create an empty placeholder initially
            self._na_div_np_manager = plot_manager(
                np.array([]),
                plot_config=plot_config(
                    var_name='na_div_np',
                    data_type='spi_sf0a_l3_mom',
                    class_name='psp_alpha',
                    subclass_name='na_div_np',
                    plot_type='time_series',
                    time=self.time if hasattr(self, 'time') else None,

                    datetime_array=self.datetime_array,
                    y_label=r'$n_\alpha / n_p$',
                    legend_label=r'$n_\alpha / n_p$',
                    color='purple',
                    y_scale='linear',
                    y_limit=None,
                    line_width=1,
                    line_style='-'
                )
            )

        # If alpha data is available, try to calculate
        alpha_density_exists = (hasattr(self, 'raw_data') and 'density' in self.raw_data and 
                               self.raw_data['density'] is not None and len(self.raw_data['density']) > 0)
        
        if alpha_density_exists:
            print_manager.dependency_management("[NA_DIV_NP_PROPERTY] Alpha density exists. Attempting calculation.")
            success = self._calculate_alpha_proton_derived()
            if success and self.raw_data.get('na_div_np') is not None:
                print_manager.dependency_management("[NA_DIV_NP_PROPERTY] Calculation successful, updating manager.")
                options = self._na_div_np_manager.plot_config
                
                # Ensure the plot_options uses the PARENT's datetime_array
                if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                    options.datetime_array = self.datetime_array
                else:
                    options.datetime_array = np.array([])

                self._na_div_np_manager = plot_manager(
                    self.raw_data['na_div_np'],
                    plot_config=options 
                )
                print_manager.dependency_management(f"[NA_DIV_NP_PROPERTY] Updated manager with data shape: {self.raw_data['na_div_np'].shape}")
            else:
                print_manager.dependency_management(f"[NA_DIV_NP_PROPERTY] Calculation failed or data is None. Success: {success}")
        else:
            print_manager.dependency_management("[NA_DIV_NP_PROPERTY] Alpha density MISSING or EMPTY. Not attempting calculation.")
        
        return self._na_div_np_manager

    @property  
    def ap_drift(self):
        """Alpha-proton drift speed with lazy loading and dependency management."""
        print_manager.dependency_management(f"[AP_DRIFT_PROPERTY ENTRY] Accessing ap_drift for instance ID: {id(self)}")
        
        # Store the plot_manager in a private attribute
        if not hasattr(self, '_ap_drift_manager'):
            print_manager.dependency_management("[AP_DRIFT_PROPERTY] Creating initial placeholder manager")
            # Create an empty placeholder initially
            self._ap_drift_manager = plot_manager(
                np.array([]),
                plot_config=plot_config(
                    var_name='ap_drift',
                    data_type='spi_sf0a_l3_mom',
                    class_name='psp_alpha',
                    subclass_name='ap_drift',
                    plot_type='time_series',
                    time=self.time if hasattr(self, 'time') else None,

                    datetime_array=self.datetime_array,
                    y_label=r'$|V_\alpha - V_p|$ (km/s)',
                    legend_label=r'$|V_\alpha - V_p|$',
                    color='red',
                    y_scale='linear',
                    y_limit=None,
                    line_width=1,
                    line_style='-'
                )
            )

        # If alpha velocity data is available, try to calculate
        alpha_velocity_exists = (hasattr(self, 'raw_data') and 'vr' in self.raw_data and 'vt' in self.raw_data and 'vn' in self.raw_data and
                                self.raw_data['vr'] is not None and len(self.raw_data['vr']) > 0)
        
        if alpha_velocity_exists:
            print_manager.dependency_management("[AP_DRIFT_PROPERTY] Alpha velocity data exists. Attempting calculation.")
            success = self._calculate_alpha_proton_derived()
            if success and self.raw_data.get('ap_drift') is not None:
                print_manager.dependency_management("[AP_DRIFT_PROPERTY] Calculation successful, updating manager.")
                options = self._ap_drift_manager.plot_config
                
                # Ensure the plot_options uses the PARENT's datetime_array
                if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                    options.datetime_array = self.datetime_array
                else:
                    options.datetime_array = np.array([])

                self._ap_drift_manager = plot_manager(
                    self.raw_data['ap_drift'],
                    plot_config=options 
                )
                print_manager.dependency_management(f"[AP_DRIFT_PROPERTY] Updated manager with data shape: {self.raw_data['ap_drift'].shape}")
            else:
                print_manager.dependency_management(f"[AP_DRIFT_PROPERTY] Calculation failed or data is None. Success: {success}")
        else:
            print_manager.dependency_management("[AP_DRIFT_PROPERTY] Alpha velocity data MISSING or EMPTY. Not attempting calculation.")
        
        return self._ap_drift_manager

    @property
    def ap_drift_va(self):
        """Drift speed normalized by Alfvén speed with lazy loading and dependency management."""
        print_manager.dependency_management(f"[AP_DRIFT_VA_PROPERTY ENTRY] Accessing ap_drift_va for instance ID: {id(self)}")
        
        # Store the plot_manager in a private attribute
        if not hasattr(self, '_ap_drift_va_manager'):
            print_manager.dependency_management("[AP_DRIFT_VA_PROPERTY] Creating initial placeholder manager")
            # Create an empty placeholder initially
            self._ap_drift_va_manager = plot_manager(
                np.array([]),
                plot_config=plot_config(
                    var_name='ap_drift_va',
                    data_type='spi_sf0a_l3_mom',
                    class_name='psp_alpha',
                    subclass_name='ap_drift_va',
                    plot_type='time_series',
                    time=self.time if hasattr(self, 'time') else None,

                    datetime_array=self.datetime_array,
                    y_label=r'$|V_\alpha - V_p| / V_A$',
                    legend_label=r'$|V_\alpha - V_p| / V_A$',
                    color='orange',
                    y_scale='linear',
                    y_limit=None,
                    line_width=1,
                    line_style='-'
                )
            )

        # If alpha velocity data is available, try to calculate
        alpha_velocity_exists = (hasattr(self, 'raw_data') and 'vr' in self.raw_data and 'vt' in self.raw_data and 'vn' in self.raw_data and
                                self.raw_data['vr'] is not None and len(self.raw_data['vr']) > 0)
        
        if alpha_velocity_exists:
            print_manager.dependency_management("[AP_DRIFT_VA_PROPERTY] Alpha velocity data exists. Attempting calculation.")
            success = self._calculate_alpha_proton_derived()
            if success and self.raw_data.get('ap_drift_va') is not None:
                print_manager.dependency_management("[AP_DRIFT_VA_PROPERTY] Calculation successful, updating manager.")
                options = self._ap_drift_va_manager.plot_config
                
                # Ensure the plot_options uses the PARENT's datetime_array
                if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                    options.datetime_array = self.datetime_array
                else:
                    options.datetime_array = np.array([])

                self._ap_drift_va_manager = plot_manager(
                    self.raw_data['ap_drift_va'],
                    plot_config=options 
                )
                print_manager.dependency_management(f"[AP_DRIFT_VA_PROPERTY] Updated manager with data shape: {self.raw_data['ap_drift_va'].shape}")
            else:
                print_manager.dependency_management(f"[AP_DRIFT_VA_PROPERTY] Calculation failed or data is None. Success: {success}")
        else:
            print_manager.dependency_management("[AP_DRIFT_VA_PROPERTY] Alpha velocity data MISSING or EMPTY. Not attempting calculation.")
        
        return self._ap_drift_va_manager
    
    def _calculate_alpha_proton_derived(self):
        """Calculate alpha-proton derived variables using dependency best practices."""
        from plotbot.get_data import get_data
        from plotbot import proton  # Use regular proton class (CDF data) - RTN coordinates
        
        print_manager.dependency_management(f"[ALPHA_PROTON_CALC] Starting calculation for derived variables")
        
        # CRITICAL: Use the stored operation trange for dependencies
        trange_for_dependencies = None
        if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:
            trange_for_dependencies = self._current_operation_trange
            print_manager.dependency_management(f"[ALPHA_PROTON_CALC] Using _current_operation_trange: {trange_for_dependencies}")
        else:
            print_manager.error("[ALPHA_PROTON_CALC] Cannot determine time range for dependencies: _current_operation_trange is None")
            print_manager.warning("[ALPHA_PROTON_CALC] The derived variable calculation now STRICTLY requires _current_operation_trange.")
            self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
            return False

        # Fetch proton data with correct time range (using regular CDF proton data)
        print_manager.dependency_management(f"[ALPHA_PROTON_CALC] Fetching proton dependencies for trange: {trange_for_dependencies}")
        
        # Get required proton data for calculations from regular proton class
        get_data(trange_for_dependencies, proton.density)   # Proton density from CDF
        get_data(trange_for_dependencies, proton.vr)        # Velocity components from VEL_RTN_SUN
        get_data(trange_for_dependencies, proton.vt)
        get_data(trange_for_dependencies, proton.vn)
        get_data(trange_for_dependencies, proton.bmag)      # Magnetic field magnitude
        
        # Validation
        required_attrs = ['density', 'vr', 'vt', 'vn', 'bmag']
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(proton, attr):
                missing_attrs.append(f"proton.{attr}")
                continue
            proton_var = getattr(proton, attr)
            if not hasattr(proton_var, 'data') or proton_var.data is None or len(proton_var.data) == 0:
                missing_attrs.append(f"proton.{attr}.data")
        
        if missing_attrs:
            print_manager.error(f"[ALPHA_PROTON_CALC] Missing proton dependency data: {missing_attrs} for trange {trange_for_dependencies}")
            self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
            return False

        # Check if we have alpha data
        if (self.raw_data.get('density') is None or 
            self.raw_data.get('vr') is None or 
            self.raw_data.get('vt') is None or 
            self.raw_data.get('vn') is None):
            print_manager.error("[ALPHA_PROTON_CALC] Missing essential alpha data for derived calculations")
            self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
            return False

        try:
            # Get alpha data arrays
            alpha_density = self.raw_data['density']
            alpha_vr = self.raw_data['vr']
            alpha_vt = self.raw_data['vt'] 
            alpha_vn = self.raw_data['vn']
            alpha_times = self.datetime_array
            
            # Get proton data arrays from regular proton class (CDF data)
            proton_density = np.array(proton.density)  # Use raw array, not .data property
            proton_vr = np.array(proton.vr)  # Use raw array, not .data property
            proton_vt = np.array(proton.vt)  # Use raw array, not .data property
            proton_vn = np.array(proton.vn)  # Use raw array, not .data property
            proton_bmag = np.array(proton.bmag)  # Use raw array, not .data property
            proton_times = proton.datetime_array
            
            print_manager.dependency_management(f"[ALPHA_PROTON_CALC] Alpha data length: {len(alpha_density)}, Proton data length: {len(proton_density)}")
            
            # Interpolate proton data to alpha cadence
            import pandas as pd
            
            alpha_df = pd.DataFrame({'time': alpha_times})
            proton_df = pd.DataFrame({
                'time': proton_times,
                'density': proton_density,
                'vr': proton_vr,
                'vt': proton_vt,
                'vn': proton_vn,
                'bmag': proton_bmag
            })
            
            # Merge and interpolate
            merged = pd.merge_asof(alpha_df.sort_values('time'), 
                                   proton_df.sort_values('time'), 
                                   on='time', 
                                   direction='nearest')
            
            # Extract interpolated proton data
            proton_density_interp = merged['density'].values
            proton_vr_interp = merged['vr'].values
            proton_vt_interp = merged['vt'].values
            proton_vn_interp = merged['vn'].values
            proton_bmag_interp = merged['bmag'].values
            
            # Calculate derived variables
            with np.errstate(all='ignore'):
                
                # 1. na_div_np - Alpha/proton density ratio
                na_div_np = alpha_density / proton_density_interp
                
                # 2. ap_drift - Alpha-proton drift speed (vector magnitude)
                # Use VEL_RTN_SUN coordinate system for both species
                vel_diff_r = alpha_vr - proton_vr_interp
                vel_diff_t = alpha_vt - proton_vt_interp
                vel_diff_n = alpha_vn - proton_vn_interp
                ap_drift = np.sqrt(vel_diff_r**2 + vel_diff_t**2 + vel_diff_n**2)
                
                # 3. ap_drift_va - Drift speed normalized by Alfvén speed
                # v_alfven = 21.8 * |MAGF_INST| / sqrt(DENS_proton + DENS_alpha)
                total_density = proton_density_interp + alpha_density
                total_density_safe = np.where(total_density > 0, total_density, np.nan)
                v_alfven = 21.8 * proton_bmag_interp / np.sqrt(total_density_safe)
                v_alfven_safe = np.where(v_alfven > 0, v_alfven, np.nan)
                ap_drift_va = ap_drift / v_alfven_safe
                
                print_manager.dependency_management(f"[ALPHA_PROTON_CALC] Calculated values - na_div_np median: {np.nanmedian(na_div_np):.4f}, ap_drift median: {np.nanmedian(ap_drift):.2f} km/s, ap_drift_va median: {np.nanmedian(ap_drift_va):.4f}")
                
                # Store results
                self.raw_data.update({
                    'na_div_np': na_div_np,
                    'ap_drift': ap_drift,
                    'ap_drift_va': ap_drift_va
                })
                
                return True
                
        except Exception as e:
            print_manager.error(f"[ALPHA_PROTON_CALC] Error during calculation: {e}")
            import traceback
            print_manager.error(f"[ALPHA_PROTON_CALC] Traceback: {traceback.format_exc()}")
            self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
            return False

# Initialize the class with no data
psp_alpha = psp_alpha_class(None)
print('initialized psp_alpha class')
