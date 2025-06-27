# wind_3dp_pm_classes.pyi - Type hints for WIND 3DP PM plasma moment classes

from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager

class wind_3dp_pm_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot managers for velocity components
    p_vels: plot_manager       # Full velocity vector [N, 3]
    vx: plot_manager           # X-component velocity
    vy: plot_manager           # Y-component velocity  
    vz: plot_manager           # Z-component velocity
    v_mag: plot_manager        # Velocity magnitude
    all_v: plot_manager        # All velocity components together
    
    # Plot managers for proton parameters
    p_dens: plot_manager       # Proton density
    p_temp: plot_manager       # Proton temperature
    
    # Plot managers for alpha parameters (new for WIND)
    a_dens: plot_manager       # Alpha particle density
    a_temp: plot_manager       # Alpha particle temperature
    
    # Plot manager for quality flags
    valid: plot_manager        # Data quality flags

    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_ploptions(self) -> None: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# Global instance
wind_3dp_pm: wind_3dp_pm_class 