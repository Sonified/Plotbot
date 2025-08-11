# plotbot/data_classes/psp_span_vdf.pyi
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from plotbot.plot_manager import plot_manager
from plotbot.data_import import DataObject

class psp_span_vdf_class:
    # Core data attributes
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[datetime]
    datetime_array: Optional[np.ndarray]
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    _current_operation_trange: Optional[List[str]]
    _current_timeslice_index: Optional[int]
    
    # Physical constants
    _mass_p: float  # Proton mass in eV/c^2
    _charge_p: float  # Proton charge in eV
    
    # ⭐ VDF PLOTTING PARAMETERS - SMART BOUNDS SYSTEM ⭐
    # Smart bounds system (auto-zoom controls)
    enable_smart_padding: bool          # Enable/disable intelligent auto-zoom
    vdf_threshold_percentile: float     # Percentile threshold to separate bulk from background data
    theta_smart_padding: float          # Single padding for theta plane (km/s), square and zero-centered
    phi_x_smart_padding: float          # Vx padding for phi plane (km/s)
    phi_y_smart_padding: float          # Vy padding for phi plane (km/s)
    phi_peak_centered: bool             # If True, center phi bounds on density peak
    enable_zero_clipping: bool          # Auto-clip when bulk doesn't cross zero
    
    # Manual axis limits (override smart bounds when set)
    theta_x_axis_limits: Optional[Tuple[float, float]]  # Manual X-axis limits for theta plane (Vx range, km/s)
    theta_y_axis_limits: Optional[Tuple[float, float]]  # Manual Y-axis limits for theta plane (Vz range, km/s)
    phi_x_axis_limits: Optional[Tuple[float, float]]    # Manual X-axis limits for phi plane (Vx range, km/s)  
    phi_y_axis_limits: Optional[Tuple[float, float]]    # Manual Y-axis limits for phi plane (Vy range, km/s)
    
    # Visual settings
    vdf_colormap: str                   # Colormap for VDF plots ('cool', 'viridis', 'plasma', etc.)
    vdf_figure_width: float
    vdf_figure_height: float
    
    # Plot managers for different VDF views
    vdf_main: plot_manager              # Main VDF plot manager (default theta plane)
    vdf_collapsed: plot_manager         # 1D collapsed distribution plot manager
    vdf_theta_plane: plot_manager       # 2D theta plane contour plot manager
    vdf_phi_plane: plot_manager         # 2D phi plane contour plot manager
    
    def __init__(self, imported_data: Optional[Union[DataObject, Dict[str, Any]]]) -> None: ...
    def update(self, imported_data: Optional[Union[DataObject, Dict[str, Any]]], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def calculate_variables(self, imported_data: Union[DataObject, Dict[str, Any]]) -> None: ...
    
    # Time slice methods
    def find_closest_timeslice(self, target_time: Union[str, datetime]) -> int: ...
    def get_timeslice_data(self, target_time: Union[str, datetime]) -> Dict[str, Any]: ...
    
    # Parameter management
    def update_plot_params(self, **kwargs: Any) -> None: ...
    
    # Smart bounds system
    def calculate_smart_bounds(self, vx: np.ndarray, vy: np.ndarray, vdf_data: np.ndarray, plane_type: str = 'theta') -> Tuple[Tuple[float, float], Tuple[float, float]]: ...
    def _apply_zero_clipping(self, xlim: Tuple[float, float], ylim: Tuple[float, float], x_max_bulk: float, y_max_bulk: float) -> Tuple[Tuple[float, float], Tuple[float, float]]: ...
    def get_axis_limits(self, plane_type: str = 'theta', vx: Optional[np.ndarray] = None, vy: Optional[np.ndarray] = None, vdf_data: Optional[np.ndarray] = None) -> Tuple[Tuple[float, float], Tuple[float, float]]: ...
    def _find_phi_peak_center(self, vx_phi: np.ndarray, vy_phi: np.ndarray, df_phi: np.ndarray, search_radius: int = 50) -> Tuple[float, float]: ...
    def get_phi_peak_centered_bounds(self, vx_phi: np.ndarray, vy_phi: np.ndarray, df_phi: np.ndarray) -> Tuple[Tuple[float, float], Tuple[float, float]]: ...
    def get_theta_square_bounds(self, vx_theta: np.ndarray, vz_theta: np.ndarray, df_theta: np.ndarray) -> Tuple[Tuple[float, float], Tuple[float, float]]: ...
    
    # Velocity and plotting methods
    def generate_velocity_grids(self, time_index: int, plane_type: str = 'theta') -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def plot_vdf_2d_contour(self, target_time: Union[str, datetime], plane_type: str = 'theta', ax: Optional[Any] = None, **plot_kwargs: Any) -> Tuple[Any, Any]: ...
    def _add_velocity_circles(self, ax: Any, xlim: Tuple[float, float], ylim: Tuple[float, float]) -> None: ...
    
    # Subclass system
    def get_subclass(self, subclass_name: str) -> Optional['psp_span_vdf_class']: ...
    def _configure_subclass_ploptions(self, subclass_name: str) -> None: ...
    def set_ploptions(self) -> None: ...
    
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __repr__(self) -> str: ...

# Global instance for plotbot integration
psp_span_vdf: psp_span_vdf_class