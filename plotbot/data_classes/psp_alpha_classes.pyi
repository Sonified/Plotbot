# psp_alpha_classes.pyi - Type hints for PSP alpha particle classes

from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager

class psp_alpha_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    times_mesh_angle: Optional[np.ndarray]
    time: Optional[np.ndarray]
    mag_field: Optional[np.ndarray]
    temp_tensor: Optional[np.ndarray]
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    energy_flux: Optional[np.ndarray]
    theta_flux: Optional[np.ndarray]
    phi_flux: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot managers for basic parameters
    density: plot_manager
    temperature: plot_manager
    sun_dist_rsun: plot_manager
    
    # Plot managers for velocity components
    vr: plot_manager           # Radial velocity (RTN)
    vt: plot_manager           # Tangential velocity (RTN)
    vn: plot_manager           # Normal velocity (RTN)
    v_sw: plot_manager         # Solar wind speed magnitude
    
    # Plot managers for velocity components (instrument frame)
    vel_inst_x: plot_manager   # X-component velocity (instrument frame)
    vel_inst_y: plot_manager   # Y-component velocity (instrument frame)
    vel_inst_z: plot_manager   # Z-component velocity (instrument frame)
    
    # Plot managers for velocity components (spacecraft frame)
    vel_sc_x: plot_manager     # X-component velocity (spacecraft frame)
    vel_sc_y: plot_manager     # Y-component velocity (spacecraft frame)
    vel_sc_z: plot_manager     # Z-component velocity (spacecraft frame)
    
    # Plot managers for temperature anisotropy
    t_par: plot_manager        # Parallel temperature
    t_perp: plot_manager       # Perpendicular temperature
    anisotropy: plot_manager   # Temperature anisotropy ratio
    
    # Plot managers for plasma parameters
    v_alfven: plot_manager     # Alfven speed
    m_alfven: plot_manager     # Alfven Mach number
    beta_ppar: plot_manager    # Parallel plasma beta
    beta_pperp: plot_manager   # Perpendicular plasma beta
    pressure_ppar: plot_manager    # Parallel pressure
    pressure_pperp: plot_manager   # Perpendicular pressure
    pressure: plot_manager         # Total pressure
    bmag: plot_manager            # Magnetic field magnitude
    
    # Plot managers for spectral data
    energy_flux: plot_manager  # Energy flux spectrogram
    theta_flux: plot_manager   # Theta flux spectrogram
    phi_flux: plot_manager     # Phi flux spectrogram

    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_ploptions(self) -> None: ...
    def _calculate_temperature_anisotropy(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# Global instance
psp_alpha: psp_alpha_class 