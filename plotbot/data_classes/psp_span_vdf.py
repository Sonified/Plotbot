# plotbot/data_classes/psp_span_vdf.py

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, List
import bisect

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

class psp_span_vdf_class:
    """PSP SPAN-I Velocity Distribution Function (VDF) data."""
    
    def __init__(self, imported_data):
        # Initialize basic attributes following plotbot patterns
        object.__setattr__(self, 'class_name', 'psp_span_vdf')
        object.__setattr__(self, 'data_type', 'spi_sf00_8dx32ex8a')  # Primary data type 
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
            # Raw CDF variables (following Jaye's approach)
            'epoch': None,           # Time array
            'theta': None,           # Theta angles (deflectors) - shape: (n_times, 2048)
            'phi': None,             # Phi angles (anodes) - shape: (n_times, 2048)  
            'energy': None,          # Energy channels - shape: (n_times, 2048)
            'eflux': None,           # Energy flux - shape: (n_times, 2048)
            'rotmat_sc_inst': None,  # Spacecraft to instrument rotation matrix
            
            # Reshaped arrays (8φ × 32E × 8θ structure)
            'theta_reshaped': None,   # Shape: (n_times, 8, 32, 8) 
            'phi_reshaped': None,     # Shape: (n_times, 8, 32, 8)
            'energy_reshaped': None,  # Shape: (n_times, 8, 32, 8)
            'eflux_reshaped': None,   # Shape: (n_times, 8, 32, 8)
            
            # VDF and velocity arrays
            'vdf': None,             # Velocity distribution function - shape: (n_times, 8, 32, 8)
            'vel': None,             # Velocity magnitude - shape: (n_times, 8, 32, 8)
            'vx': None,              # X velocity component - shape: (n_times, 8, 32, 8)
            'vy': None,              # Y velocity component - shape: (n_times, 8, 32, 8)
            'vz': None,              # Z velocity component - shape: (n_times, 8, 32, 8)
            
            # Processed 2D slices for plotting
            'vdf_theta_plane': None,  # VDF summed over theta dimension - shape: (n_times, 32, 8)
            'vdf_phi_plane': None,    # VDF summed over phi dimension - shape: (n_times, 8, 32)
            'vdf_collapsed': None,    # VDF collapsed to 1D - shape: (n_times, 32)
            
            # Field-aligned coordinate arrays (when magnetic field available)
            'vx_fac': None,          # Field-aligned X (parallel) - shape: (n_times, 8, 32, 8)
            'vy_fac': None,          # Field-aligned Y (perp1) - shape: (n_times, 8, 32, 8)
            'vz_fac': None,          # Field-aligned Z (perp2) - shape: (n_times, 8, 32, 8)
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
        # VDF-specific attributes
        object.__setattr__(self, '_mass_p', 0.010438870)    # Proton mass in eV/c^2 (Jaye's constant)
        object.__setattr__(self, '_charge_p', 1)           # Proton charge in eV (Jaye's constant)
        object.__setattr__(self, '_current_timeslice_index', None)  # For single-time plotting
        
        # ⭐ PLOTBOT-STYLE PARAMETER SYSTEM ⭐
        # Direct attributes following Plotbot pattern (like epad.strahl.colorbar_limits)
        
        # Smart bounds system (auto-zoom controls)
        object.__setattr__(self, 'enable_smart_padding', True)       # Enable/disable intelligent auto-zoom
        object.__setattr__(self, 'vdf_threshold_percentile', 10)     # 10th percentile separates bulk from background
        object.__setattr__(self, 'theta_smart_padding', 100)         # Single padding for theta plane (km/s) – square, zero-centered
        object.__setattr__(self, 'phi_x_smart_padding', 100)         # Vx padding for phi plane (km/s)
        object.__setattr__(self, 'phi_y_smart_padding', 100)         # Vy padding for phi plane (km/s)
        object.__setattr__(self, 'phi_peak_centered', False)         # Enable peak-centering for phi plane (default OFF)
        object.__setattr__(self, 'enable_zero_clipping', True)       # Auto-clip when bulk doesn't cross zero
        
        # Manual axis limits (override smart bounds when set)
        object.__setattr__(self, 'theta_x_axis_limits', None)       # Manual X-axis limits for theta plane (Vx range, km/s)
        object.__setattr__(self, 'theta_y_axis_limits', None)       # Manual Y-axis limits for theta plane (Vz range, km/s)
        object.__setattr__(self, 'phi_x_axis_limits', None)         # Manual X-axis limits for phi plane (Vx range, km/s)  
        object.__setattr__(self, 'phi_y_axis_limits', None)         # Manual Y-axis limits for phi plane (Vy range, km/s)
        
        # Visual settings
        object.__setattr__(self, 'vdf_colormap', 'cool')            # Default colormap for VDF plots
        object.__setattr__(self, 'vdf_figure_width', 18)            # Figure width in inches (default 18)
        object.__setattr__(self, 'vdf_figure_height', 5)            # Figure height in inches (default 5)
        object.__setattr__(self, 'vdf_text_scaling', 1.0)           # Text scaling multiplier (1.0 = default matplotlib size)
        
        if imported_data is None:
            # Set empty plotting options if imported_data is None
            self.set_ploptions()
            print_manager.dependency_management("VDF class initialized with empty attributes.")
        else:
            # Process VDF data if provided
            print_manager.dependency_management("Processing VDF data...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully processed VDF data.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Update VDF data with new imported data."""
        print_manager.dependency_management("Updating VDF data...")
        print_manager.debug(f"[VDF_UPDATE_DEBUG] imported_data type: {type(imported_data)}")
        print_manager.debug(f"[VDF_UPDATE_DEBUG] imported_data: {imported_data}")
        
        if imported_data is None:
            print_manager.error("VDF update called with None data")
            return
            
        self.calculate_variables(imported_data)
        print_manager.status("VDF data updated successfully.")
    
    def calculate_variables(self, imported_data):
        """Process raw VDF data following Jaye's exact approach."""
        
        # Handle both dictionary (testing) and DataObject (plotbot integration) inputs
        if hasattr(imported_data, 'data') and hasattr(imported_data, 'times'):
            # DataObject from plotbot's import system
            data_dict = imported_data.data
            time_array = imported_data.times
        elif hasattr(imported_data, 'get'):
            # Dictionary input (direct testing)
            data_dict = imported_data
            time_array = imported_data.get('Epoch', None)
        else:
            print_manager.error(f"Unknown imported_data type: {type(imported_data)}")
            return
        
        # Extract raw CDF variables (Jaye's Cell 9 approach)
        # For VDF, use time_array from DataObject.times (like other classes), fallback to data dict
        self.raw_data['epoch'] = time_array if time_array is not None else data_dict.get('Epoch', None)
        self.raw_data['theta'] = data_dict.get('THETA', None) 
        self.raw_data['phi'] = data_dict.get('PHI', None)
        self.raw_data['energy'] = data_dict.get('ENERGY', None)
        self.raw_data['eflux'] = data_dict.get('EFLUX', None)
        self.raw_data['rotmat_sc_inst'] = data_dict.get('ROTMAT_SC_INST', None)
        
        # Debug: Check what we actually extracted
        print_manager.debug(f"VDF data extraction results:")
        print_manager.debug(f"  data_dict type: {type(data_dict)}")
        print_manager.debug(f"  data_dict keys: {list(data_dict.keys()) if hasattr(data_dict, 'keys') else 'No keys method'}")
        print_manager.debug(f"  theta extracted: {self.raw_data['theta'] is not None} (shape: {getattr(self.raw_data['theta'], 'shape', 'None')})")
        print_manager.debug(f"  phi extracted: {self.raw_data['phi'] is not None} (shape: {getattr(self.raw_data['phi'], 'shape', 'None')})")
        print_manager.debug(f"  energy extracted: {self.raw_data['energy'] is not None} (shape: {getattr(self.raw_data['energy'], 'shape', 'None')})")
        print_manager.debug(f"  eflux extracted: {self.raw_data['eflux'] is not None} (shape: {getattr(self.raw_data['eflux'], 'shape', 'None')})")
        
        print_manager.debug(f"[VDF_CALC_DEBUG] About to check epoch data...")
        print_manager.debug(f"[VDF_CALC_DEBUG] time_array = {time_array}")
        print_manager.debug(f"[VDF_CALC_DEBUG] time_array type = {type(time_array)}")
        print_manager.debug(f"[VDF_CALC_DEBUG] self.raw_data['epoch'] = {self.raw_data['epoch']}")
        print_manager.debug(f"[VDF_CALC_DEBUG] epoch type = {type(self.raw_data['epoch'])}")
        
        if self.raw_data['epoch'] is None:
            print_manager.error("No Epoch data found in imported VDF data.")
            return
            
        # Convert time format (Jaye's Cell 11 approach)
        print_manager.debug(f"Epoch data type: {type(self.raw_data['epoch'])}")
        print_manager.debug(f"Epoch data shape: {getattr(self.raw_data['epoch'], 'shape', 'no shape')}")
        print_manager.debug(f"Epoch data sample: {self.raw_data['epoch'][:3] if hasattr(self.raw_data['epoch'], '__getitem__') else self.raw_data['epoch']}")
        
        if isinstance(self.raw_data['epoch'], list):
            self.datetime = self.raw_data['epoch']
        else:
            # Convert from CDF epoch to datetime list
            try:
                epoch_dt64 = cdflib.cdfepoch.to_datetime(self.raw_data['epoch'])
                self.datetime = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
                print_manager.debug(f"Time conversion successful: {len(self.datetime)} points")
            except Exception as e:
                print_manager.error(f"Time conversion failed: {e}")
                return
        
        self.datetime_array = np.array(self.datetime)
        
        # Reshape data to (8φ × 32E × 8θ) structure for all time points (Jaye's Cell 15 approach)
        n_times = len(self.datetime)
        
        if self.raw_data['theta'] is not None:
            # Reshape from (n_times, 2048) to (n_times, 8, 32, 8)
            self.raw_data['theta_reshaped'] = self.raw_data['theta'].reshape((n_times, 8, 32, 8))
            self.raw_data['phi_reshaped'] = self.raw_data['phi'].reshape((n_times, 8, 32, 8))
            self.raw_data['energy_reshaped'] = self.raw_data['energy'].reshape((n_times, 8, 32, 8))
            self.raw_data['eflux_reshaped'] = self.raw_data['eflux'].reshape((n_times, 8, 32, 8))
            
            # Calculate VDF following Jaye's exact formula (Cell 17)
            numberFlux = self.raw_data['eflux_reshaped'] / self.raw_data['energy_reshaped']
            self.raw_data['vdf'] = numberFlux * (self._mass_p**2) / ((2E-5) * self.raw_data['energy_reshaped'])
            
            # Calculate velocity components (Jaye's Cell 19 approach)
            self.raw_data['vel'] = np.sqrt(2 * self._charge_p * self.raw_data['energy_reshaped'] / self._mass_p)
            
            # Convert to cartesian velocity coordinates in instrument frame
            self.raw_data['vx'] = (self.raw_data['vel'] * 
                                 np.cos(np.radians(self.raw_data['phi_reshaped'])) * 
                                 np.cos(np.radians(self.raw_data['theta_reshaped'])))
            self.raw_data['vy'] = (self.raw_data['vel'] * 
                                 np.sin(np.radians(self.raw_data['phi_reshaped'])) * 
                                 np.cos(np.radians(self.raw_data['theta_reshaped'])))
            self.raw_data['vz'] = (self.raw_data['vel'] * 
                                 np.sin(np.radians(self.raw_data['theta_reshaped'])))
            
            # Calculate 2D slices for plotting (following Jaye's approach)
            # Theta plane: sum over theta dimension (axis=0 in reshaped array)
            self.raw_data['vdf_theta_plane'] = np.nansum(self.raw_data['vdf'], axis=1)  # Shape: (n_times, 32, 8)
            
            # Phi plane: sum over phi dimension (axis=2 in reshaped array) 
            self.raw_data['vdf_phi_plane'] = np.nansum(self.raw_data['vdf'], axis=3)    # Shape: (n_times, 8, 32)
            
            # Collapsed 1D: sum over both phi and theta dimensions (axes 1,3)
            self.raw_data['vdf_collapsed'] = np.nansum(self.raw_data['vdf'], axis=(1, 3))  # Shape: (n_times, 32)
            
            print_manager.status(f"VDF data processed for {n_times} time points, shape: {self.raw_data['vdf'].shape}")
        else:
            print_manager.error("No theta/phi data found for VDF processing.")
    
    def find_closest_timeslice(self, target_time):
        """Find closest time slice using Jaye's bisect approach (Cell 11)."""
        if isinstance(target_time, str):
            # Parse plotbot time string format
            from dateutil.parser import parse
            target_datetime = parse(target_time.replace('/', ' '))
        else:
            target_datetime = target_time
            
        # Use Jaye's exact bisect approach
        tSliceIndex = bisect.bisect_left(self.datetime, target_datetime)
        
        # Handle edge cases
        if tSliceIndex >= len(self.datetime):
            tSliceIndex = len(self.datetime) - 1
        elif tSliceIndex > 0:
            # Check if previous time is actually closer
            time_diff_current = abs((self.datetime[tSliceIndex] - target_datetime).total_seconds())
            time_diff_previous = abs((self.datetime[tSliceIndex-1] - target_datetime).total_seconds()) 
            if time_diff_previous < time_diff_current:
                tSliceIndex -= 1
        
        self._current_timeslice_index = tSliceIndex
        return tSliceIndex
    
    def get_timeslice_data(self, target_time):
        """Extract VDF data for specific time slice."""
        time_index = self.find_closest_timeslice(target_time)
        
        return {
            'epoch': self.datetime[time_index],
            'time_index': time_index,
            'vdf': self.raw_data['vdf'][time_index, :, :, :],
            'vel': self.raw_data['vel'][time_index, :, :, :],
            'vx': self.raw_data['vx'][time_index, :, :, :],
            'vy': self.raw_data['vy'][time_index, :, :, :],
            'vz': self.raw_data['vz'][time_index, :, :, :],
            'vdf_theta_plane': self.raw_data['vdf_theta_plane'][time_index, :, :],
            'vdf_phi_plane': self.raw_data['vdf_phi_plane'][time_index, :, :],
            'vdf_collapsed': self.raw_data['vdf_collapsed'][time_index, :],
            'energy_reshaped': self.raw_data['energy_reshaped'][time_index, :, :, :],
            'theta_reshaped': self.raw_data['theta_reshaped'][time_index, :, :, :],
            'phi_reshaped': self.raw_data['phi_reshaped'][time_index, :, :, :],
        }
    
    def update_plot_params(self, **kwargs):
        """
        Update VDF plotting parameters.
        
        Args:
            **kwargs: Any of the supported VDF plotting parameters
            
        Example:
            vdf.update_plot_params(
                enable_smart_padding=False,
                theta_x_axis_limits=(-800, 0),
                phi_y_smart_padding=150
            )
        """
        # List of valid VDF parameters (now direct attributes)
        valid_params = [
            'enable_smart_padding', 'vdf_threshold_percentile', 
            'theta_x_smart_padding', 'theta_y_smart_padding',
            'phi_x_smart_padding', 'phi_y_smart_padding', 'enable_zero_clipping',
            'theta_x_axis_limits', 'theta_y_axis_limits', 
            'phi_x_axis_limits', 'phi_y_axis_limits', 'vdf_colormap',
            'vdf_figure_width', 'vdf_figure_height'
        ]
        
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)
                print_manager.debug(f"Updated VDF parameter: {key} = {value}")
            else:
                print_manager.warning(f"Unknown VDF parameter: {key}. Valid parameters: {valid_params}")
    
    def calculate_smart_bounds(self, vx, vy, vdf_data, plane_type='theta'):
        """
        Calculate smart plot bounds based on data distribution and user parameters.
        
        Args:
            vx, vy: 2D velocity arrays for the plane
            vdf_data: 2D VDF array for the plane  
            plane_type: 'theta' or 'phi' to determine which padding parameters to use
            
        Returns:
            (xlim, ylim): Tuples of (min, max) for each axis
        """
        # Get padding values based on plane type (now direct attributes)
        if plane_type == 'theta':
            # For theta plane, we use the single theta_smart_padding for both directions
            x_padding = getattr(self, 'theta_smart_padding', 100)
            y_padding = getattr(self, 'theta_smart_padding', 100)
        else:  # phi plane
            x_padding = self.phi_x_smart_padding 
            y_padding = self.phi_y_smart_padding
        
        # Find valid data points (not NaN, not zero)
        valid_mask = np.isfinite(vdf_data) & (vdf_data > 0)
        
        if not np.any(valid_mask):
            print_manager.warning("No valid VDF data found, using Jaye's reference bounds")
            if plane_type == 'theta':
                # Jaye's exact bounds from his notebook (Cell 39 & 41)
                return (-800, 0), (-400, 400)
            else:
                # Jaye's exact bounds from his notebook (Cell 41)
                return (-800, 0), (-200, 600)
        
        # Find bulk data using percentile threshold
        valid_vdf = vdf_data[valid_mask]
        vdf_threshold = np.percentile(valid_vdf, self.vdf_threshold_percentile)
        bulk_mask = vdf_data > vdf_threshold
        
        if not np.any(bulk_mask):
            # Fallback to all valid data if threshold too strict
            bulk_mask = valid_mask
            print_manager.debug(f"VDF threshold too strict, using all valid data for {plane_type} plane")
        
        # Find extent of bulk data
        vx_bulk = vx[bulk_mask]
        vy_bulk = vy[bulk_mask]
        
        x_min_bulk, x_max_bulk = np.min(vx_bulk), np.max(vx_bulk)
        y_min_bulk, y_max_bulk = np.min(vy_bulk), np.max(vy_bulk)
        
        # Add padding
        xlim = (x_min_bulk - x_padding, x_max_bulk + x_padding)
        ylim = (y_min_bulk - y_padding, y_max_bulk + y_padding)
        
        # Apply zero clipping if enabled and appropriate
        if self.enable_zero_clipping:
            xlim, ylim = self._apply_zero_clipping(xlim, ylim, x_max_bulk, y_max_bulk)
        
        print_manager.debug(f"Smart bounds for {plane_type} plane: X={xlim}, Y={ylim}")
        return xlim, ylim

    def get_theta_square_bounds(self, vx_theta, vz_theta, df_theta):
        """Smart zero-centered, square bounds for theta plane using bulk data and user padding."""
        from plotbot.vdf_helpers import theta_smart_bounds
        
        padding = getattr(self, 'theta_smart_padding', 100)
        percentile = getattr(self, 'vdf_threshold_percentile', 10)
        enable_clipping = getattr(self, 'enable_zero_clipping', True)
        
        xlim, ylim = theta_smart_bounds(
            vx_theta, vz_theta, df_theta, 
            percentile=percentile,
            padding=padding, 
            enable_zero_clipping=enable_clipping
        )
        
        print_manager.debug(f"Theta smart square bounds: X={xlim}, Y={ylim} (padding={padding})")
        return xlim, ylim

    def _find_phi_peak_center(self, vx_phi, vy_phi, df_phi, search_radius=50):
        """Find the weighted centroid of the highest density region in PHI plane"""
        peak_idx = np.unravel_index(np.nanargmax(df_phi), df_phi.shape)
        peak_vx = vx_phi[peak_idx]
        peak_vy = vy_phi[peak_idx]
        
        distances = np.sqrt((vx_phi - peak_vx)**2 + (vy_phi - peak_vy)**2)
        circle_mask = distances <= search_radius
        
        if not np.any(circle_mask):
            return peak_vx, peak_vy
        
        circle_data = df_phi[circle_mask]
        circle_vx = vx_phi[circle_mask] 
        circle_vy = vy_phi[circle_mask]
        
        valid_mask = np.isfinite(circle_data) & (circle_data > 0)
        if not np.any(valid_mask):
            return peak_vx, peak_vy
        
        valid_data = circle_data[valid_mask]
        valid_vx = circle_vx[valid_mask]
        valid_vy = circle_vy[valid_mask]
        
        total_weight = np.nansum(valid_data)
        if total_weight <= 0:
            return peak_vx, peak_vy
            
        center_vx = np.nansum(valid_vx * valid_data) / total_weight
        center_vy = np.nansum(valid_vy * valid_data) / total_weight
        
        return center_vx, center_vy

    def get_phi_peak_centered_bounds(self, vx_phi, vy_phi, df_phi):
        """Peak-centered bounds for phi plane to avoid cutting off bulk distribution."""
        center_vx, center_vy = self._find_phi_peak_center(vx_phi, vy_phi, df_phi)
        
        x_padding = getattr(self, 'phi_x_smart_padding', 100)
        y_padding = getattr(self, 'phi_y_smart_padding', 100)
        
        valid_mask = np.isfinite(df_phi) & (df_phi > 0)
        if not np.any(valid_mask):
            return (-800, 0), (-200, 600)
        
        vdf_threshold = np.percentile(df_phi[valid_mask], self.vdf_threshold_percentile)
        bulk_mask = df_phi > vdf_threshold
        if not np.any(bulk_mask):
            bulk_mask = valid_mask
        
        vx_bulk = vx_phi[bulk_mask]
        vy_bulk = vy_phi[bulk_mask]
        
        vx_range = max(abs(np.min(vx_bulk) - center_vx), abs(np.max(vx_bulk) - center_vx))
        vy_range = max(abs(np.min(vy_bulk) - center_vy), abs(np.max(vy_bulk) - center_vy))
        
        x_half_range = vx_range + x_padding
        y_half_range = vy_range + y_padding
        
        xlim = (center_vx - x_half_range, center_vx + x_half_range)
        ylim = (center_vy - y_half_range, center_vy + y_half_range)
        
        if self.enable_zero_clipping:
            vx_min_bulk, vx_max_bulk = np.min(vx_bulk), np.max(vx_bulk)
            if vx_max_bulk < 0 and xlim[1] > 0:
                xlim = (xlim[0], 0.0)
            elif vx_min_bulk > 0 and xlim[0] < 0:
                xlim = (0.0, xlim[1])
        
        return xlim, ylim
    
    def _apply_zero_clipping(self, xlim, ylim, x_max_bulk, y_max_bulk):
        """Apply intelligent zero clipping when bulk data doesn't cross zero."""
        
        # Only clip if bulk data is entirely negative but padding pushes past zero
        if x_max_bulk < 0 and xlim[1] > 0:
            xlim = (xlim[0], 0)  # Clip X at zero
            print_manager.debug("Applied zero clipping to X-axis")
            
        if y_max_bulk < 0 and ylim[1] > 0:
            ylim = (ylim[0], 0)  # Clip Y at zero
            print_manager.debug("Applied zero clipping to Y-axis")
            
        return xlim, ylim
    
    def get_axis_limits(self, plane_type='theta', vx=None, vy=None, vdf_data=None):
        """Get axis limits following parameter hierarchy: Manual (only when smart_padding disabled) > Smart > Jaye's defaults."""
        if plane_type == 'theta':
            x_manual = self.theta_x_axis_limits
            y_manual = self.theta_y_axis_limits
            jaye_x_bounds, jaye_y_bounds = (-800, 0), (-400, 400)
            
            # Manual limits only used when smart padding is explicitly disabled
            if not self.enable_smart_padding and x_manual is not None and y_manual is not None:
                print_manager.debug(f"Using manual axis limits for theta plane: X={x_manual}, Y={y_manual}")
                return x_manual, y_manual
                
            # Use square bounds for theta when smart padding enabled
            if self.enable_smart_padding and vx is not None and vy is not None and vdf_data is not None:
                return self.get_theta_square_bounds(vx, vy, vdf_data)
            return jaye_x_bounds, jaye_y_bounds
        else:
            x_manual = self.phi_x_axis_limits
            y_manual = self.phi_y_axis_limits
            jaye_x_bounds, jaye_y_bounds = (-800, 0), (-200, 600)
        
        # Manual limits check for phi (only when smart padding disabled)
        if not self.enable_smart_padding and x_manual is not None and y_manual is not None:
            print_manager.debug(f"Using manual axis limits for {plane_type} plane: X={x_manual}, Y={y_manual}")
            return x_manual, y_manual
        
        # Mixed manual/smart bounds for phi (only when smart padding disabled)
        if not self.enable_smart_padding and (x_manual is not None or y_manual is not None):
            # When smart padding disabled, use Jaye's defaults for missing manual values
            xlim_smart, ylim_smart = jaye_x_bounds, jaye_y_bounds
            
            xlim = x_manual if x_manual is not None else xlim_smart
            ylim = y_manual if y_manual is not None else ylim_smart
            
            print_manager.debug(f"Using mixed bounds for {plane_type} plane: X={xlim} ({'manual' if x_manual else 'Jaye default'}), Y={ylim} ({'manual' if y_manual else 'Jaye default'})")
            return xlim, ylim
        
        # No manual limits - use smart bounds or fallback for phi
        if self.enable_smart_padding and vx is not None and vy is not None and vdf_data is not None:
            if plane_type == 'phi' and getattr(self, 'phi_peak_centered', False):
                xlim, ylim = self.get_phi_peak_centered_bounds(vx, vy, vdf_data)
                print_manager.debug(f"Using peak-centered bounds for phi plane")
                return xlim, ylim
            else:
                xlim, ylim = self.calculate_smart_bounds(vx, vy, vdf_data, plane_type)
                print_manager.debug(f"Using smart bounds for {plane_type} plane")
                return xlim, ylim
        else:
            xlim, ylim = jaye_x_bounds, jaye_y_bounds
            print_manager.debug(f"Using Jaye's reference bounds for {plane_type} plane: X={xlim}, Y={ylim}")
            return xlim, ylim
    
    def generate_velocity_grids(self, time_index, plane_type='theta'):
        """
        Generate velocity grids for 2D plotting following Jaye's approach.
        
        Args:
            time_index: Time slice index
            plane_type: 'theta' or 'phi' plane
            
        Returns:
            (vx_plane, vy_plane, vdf_plane): 2D arrays for plotting
        """
        if plane_type == 'theta':
            # Theta plane: sum over theta dimension (Jaye's Cell 26 approach)
            theta_cut = 0  # Use first theta slice for coordinate reference (Jaye's approach)
            
            phi_plane = self.raw_data['phi_reshaped'][time_index, theta_cut, :, :]
            theta_plane = self.raw_data['theta_reshaped'][time_index, theta_cut, :, :]
            energy_plane = self.raw_data['energy_reshaped'][time_index, theta_cut, :, :]
            vel_plane = np.sqrt(2 * self._charge_p * energy_plane / self._mass_p)
            
            # Calculate velocity grids
            vx_plane = vel_plane * np.cos(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
            vz_plane = vel_plane * np.sin(np.radians(theta_plane))  # Vz for theta plane
            
            # Sum VDF over theta dimension (axis=0 in reshaped array)
            vdf_plane = np.nansum(self.raw_data['vdf'][time_index, :, :, :], axis=0)
            
            return vx_plane, vz_plane, vdf_plane
            
        else:  # phi plane
            # Phi plane: sum over theta dimension but use middle theta for coordinates
            theta_middle = 4  # Middle theta bin (0-7 range)
            
            phi_plane = self.raw_data['phi_reshaped'][time_index, :, :, theta_middle]
            theta_plane = self.raw_data['theta_reshaped'][time_index, :, :, theta_middle]
            energy_plane = self.raw_data['energy_reshaped'][time_index, :, :, theta_middle]
            vel_plane = np.sqrt(2 * self._charge_p * energy_plane / self._mass_p)
            
            # Calculate velocity grids
            vx_plane = vel_plane * np.cos(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
            vy_plane = vel_plane * np.sin(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))  # Vy for phi plane
            
            # Sum VDF over theta dimension (axis=2 in reshaped array)
            vdf_plane = np.nansum(self.raw_data['vdf'][time_index, :, :, :], axis=2)
            
            return vx_plane, vy_plane, vdf_plane
    
    def plot_vdf_2d_contour(self, target_time, plane_type='theta', ax=None, **plot_kwargs):
        """
        Create 2D VDF contour plot using the parameter system.
        
        Args:
            target_time: Time string or datetime object
            plane_type: 'theta' or 'phi' plane
            ax: Matplotlib axis (optional, creates new if None)
            **plot_kwargs: Additional plot customization parameters
            
        Returns:
            (fig, ax): Matplotlib figure and axis objects
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import LogNorm
        
        # Find time slice and generate velocity grids
        time_index = self.find_closest_timeslice(target_time)
        selected_time = self.datetime[time_index]
        
        if plane_type == 'theta':
            vx_plane, vy_plane, vdf_plane = self.generate_velocity_grids(time_index, 'theta')
            default_title = f'VDF θ-plane: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}'
            x_label, y_label = 'Vx (km/s)', 'Vz (km/s)'
        else:  # phi plane
            vx_plane, vy_plane, vdf_plane = self.generate_velocity_grids(time_index, 'phi')
            default_title = f'VDF φ-plane: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}'
            x_label, y_label = 'Vx (km/s)', 'Vy (km/s)'
        
        # Create figure if not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.figure
        
        # Get axis limits using parameter hierarchy
        xlim, ylim = self.get_axis_limits(plane_type, vx_plane, vy_plane, vdf_plane)
        
        # Create contour plot with robust logarithmic scaling
        vdf_plot = vdf_plane.copy()
        vdf_plot[vdf_plot <= 0] = np.nan  # Remove zeros/negatives for log scale
        
        vmin = np.nanpercentile(vdf_plot, 1)   # 1st percentile for min
        vmax = np.nanpercentile(vdf_plot, 99)  # 99th percentile for max
        
        try:
            # Try logarithmic contours (Jaye's preferred approach)
            if vmin > 0 and vmax > vmin and np.isfinite(vmin) and np.isfinite(vmax):
                levels = np.logspace(np.log10(vmin), np.log10(vmax), 20)
                contour = ax.contourf(vx_plane, vy_plane, vdf_plot, levels=levels, 
                                    norm=LogNorm(), cmap=self.vdf_colormap)
            else:
                raise ValueError("Invalid range for logarithmic scale")
        except (ValueError, RuntimeError):
            # Fallback to linear scale for problematic data
            print_manager.debug(f"Using linear contours for {plane_type} plane (log scale failed)")
            contour = ax.contourf(vx_plane, vy_plane, vdf_plot, levels=20, 
                                cmap=self.vdf_colormap)
        
        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('f (s³/km³)')
        
        # Set axis limits and labels
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(plot_kwargs.get('title', default_title))
        
        # Add reference velocity circles if they fit in plot
        self._add_velocity_circles(ax, xlim, ylim)
        
        # Only call tight_layout for standalone plots
        if len(fig.axes) <= 2:  # Main plot + colorbar
            plt.tight_layout()
        
        print_manager.status(f"Created VDF {plane_type} plane plot for {selected_time}")
        return fig, ax
    
    def _add_velocity_circles(self, ax, xlim, ylim):
        """Add velocity reference circles if they fit within the plot bounds."""
        import matplotlib.patches as patches
        
        # Standard solar wind velocity circles (km/s)
        velocities = [200, 400, 600, 800]
        
        for vel in velocities:
            # Check if circle fits within current axis limits
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            if vel * 2 < min(x_range, y_range) * 0.8:  # Circle diameter < 80% of smaller axis range
                circle = patches.Circle((0, 0), vel, fill=False, color='white', 
                                      linestyle='--', alpha=0.7, linewidth=0.8)
                ax.add_patch(circle)
                
                # Add velocity label if space allows
                if vel < min(abs(xlim[0]), abs(xlim[1]), abs(ylim[0]), abs(ylim[1])) * 0.7:
                    ax.text(vel * 0.7, vel * 0.7, f'{vel}', color='white', 
                          fontsize=8, ha='center', va='center')
    
    def get_subclass(self, subclass_name):
        """Return plot manager for different VDF views."""
        valid_subclasses = [
            'vdf_collapsed',      # 1D collapsed distribution
            'vdf_theta_plane',    # 2D theta plane contour  
            'vdf_phi_plane',      # 2D phi plane contour
            'vdf_fac_par_perp1',  # Field-aligned coordinates v_parallel vs v_perp1
            'vdf_fac_par_perp2',  # Field-aligned coordinates v_parallel vs v_perp2
        ]
        
        if subclass_name not in valid_subclasses:
            print_manager.error(f"Invalid VDF subclass: {subclass_name}. Valid options: {valid_subclasses}")
            return None
            
        # Create a copy of this class with the specified subclass
        vdf_subclass = psp_span_vdf_class(None)  # Initialize empty
        
        # Copy relevant data
        vdf_subclass.raw_data = self.raw_data.copy()
        vdf_subclass.datetime = self.datetime.copy()
        vdf_subclass.datetime_array = self.datetime_array.copy() if self.datetime_array is not None else None
        vdf_subclass._current_operation_trange = self._current_operation_trange
        vdf_subclass._current_timeslice_index = self._current_timeslice_index
        
        # Set the subclass name
        object.__setattr__(vdf_subclass, 'subclass_name', subclass_name)
        
        # Configure plotting options for this subclass
        vdf_subclass._configure_subclass_ploptions(subclass_name)
        
        return vdf_subclass
    
    def _configure_subclass_ploptions(self, subclass_name):
        """Configure plotting options for specific VDF subclass."""
        
        if subclass_name == 'vdf_collapsed':
            # 1D collapsed VDF plot manager
            self.vdf_collapsed = plot_manager(
                None,  # Data will be set during plotting
                plot_options=ploptions(
                    data_type='spi_sf00_8dx32ex8a',
                    var_name='vdf_collapsed',
                    class_name='psp_span_vdf',
                    subclass_name='vdf_collapsed',
                    plot_type='line',
                    datetime_array=self.datetime_array,
                    x_label='Velocity (km/s)',
                    y_label='f (s³/km³)',
                    y_scale='log',
                    legend_label='VDF Collapsed',
                    color='blue',
                    line_width=1,
                    title='VDF Collapsed (1D)',
                )
            )
            
        elif subclass_name == 'vdf_theta_plane':
            # 2D theta plane contour plot manager
            self.vdf_theta_plane = plot_manager(
                None,  # Data will be set during plotting
                plot_options=ploptions(
                    data_type='spi_sf00_8dx32ex8a',
                    var_name='vdf_theta_plane',
                    class_name='psp_span_vdf',
                    subclass_name='vdf_theta_plane',
                    plot_type='contour',
                    datetime_array=self.datetime_array,
                    x_label='Vx (km/s)',
                    y_label='Vz (km/s)',
                    z_label='f (s³/km³)',
                    z_scale='log',
                    colormap='cool',
                    title='VDF θ-plane',
                )
            )
            
        elif subclass_name == 'vdf_phi_plane':
            # 2D phi plane contour plot manager
            self.vdf_phi_plane = plot_manager(
                None,  # Data will be set during plotting
                plot_options=ploptions(
                    data_type='spi_sf00_8dx32ex8a',
                    var_name='vdf_phi_plane',
                    class_name='psp_span_vdf',
                    subclass_name='vdf_phi_plane',
                    plot_type='contour',
                    datetime_array=self.datetime_array,
                    x_label='Vx (km/s)',
                    y_label='Vy (km/s)',
                    z_label='f (s³/km³)',
                    z_scale='log',
                    colormap='cool',
                    title='VDF φ-plane',
                )
            )
            
        elif subclass_name in ['vdf_fac_par_perp1', 'vdf_fac_par_perp2']:
            # Field-aligned coordinates plot manager
            perp_label = 'V_perp1' if 'perp1' in subclass_name else 'V_perp2'
            setattr(self, subclass_name, plot_manager(
                None,  # Data will be set during plotting
                plot_options=ploptions(
                    data_type='spi_sf00_8dx32ex8a',
                    var_name=subclass_name,
                    class_name='psp_span_vdf',
                    subclass_name=subclass_name,
                    plot_type='contour',
                    datetime_array=self.datetime_array,
                    x_label='V|| (km/s)',
                    y_label=f'{perp_label} (km/s)',
                    z_label='f (s³/km³)',
                    z_scale='log',
                    colormap='cool',
                    title=f'VDF Field-Aligned ({perp_label})',
                )
            ))
    
    def set_ploptions(self):
        """Set default plotting options for VDF data following plotbot patterns."""
        # Main VDF plot manager (default theta plane view)
        self.vdf_main = plot_manager(
            None,  # Data will be set during plotting
            plot_options=ploptions(
                data_type='spi_sf00_8dx32ex8a',
                var_name='vdf_theta_plane',
                class_name='psp_span_vdf',
                subclass_name=None,
                plot_type='contour',
                datetime_array=self.datetime_array,
                x_label='Vx (km/s)',
                y_label='Vz (km/s)',
                z_label='f (s³/km³)',
                z_scale='log',
                colormap='cool',
                title='PSP SPAN-I VDF',
                legend_label='VDF',
            )
        )
    
    def __setattr__(self, name, value):
        """Custom setattr to handle VDF data validation."""
        # Allow standard plotbot attributes
        allowed_attrs = [
            'raw_data', 'datetime', 'datetime_array', 'ploptions', 
            '_current_operation_trange', '_current_timeslice_index',
            'class_name', 'data_type', 'subclass_name', '_mass_p', '_charge_p',
            # VDF parameters now as direct attributes
            'enable_smart_padding', 'vdf_threshold_percentile', 
            'theta_smart_padding', 'phi_x_smart_padding', 'phi_y_smart_padding', 'phi_peak_centered',
            'enable_zero_clipping', 'theta_x_axis_limits', 'theta_y_axis_limits',
            'phi_x_axis_limits', 'phi_y_axis_limits', 'vdf_colormap',
            'vdf_figure_width', 'vdf_figure_height', 'vdf_text_scaling',
            # Plot manager attributes that may be dynamically set
            'vdf_main', 'vdf_collapsed', 'vdf_theta_plane', 'vdf_phi_plane'
        ]
        
        if name in allowed_attrs:
            object.__setattr__(self, name, value)
        else:
            print_manager.debug(f"VDF setattr: {name} = {value}")
            object.__setattr__(self, name, value)
    
    def __repr__(self):
        """String representation of VDF class."""
        n_times = len(self.datetime) if self.datetime else 0
        subclass_str = f" ({self.subclass_name})" if self.subclass_name else ""
        return f"<PSP SPAN-I VDF{subclass_str}: {n_times} time points>"

# Create global instance for DataCubby registration
psp_span_vdf = psp_span_vdf_class(None)  # Initialize the class with no data
print('initialized psp_span_vdf class')