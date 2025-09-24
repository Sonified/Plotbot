# Type hints for wind_swe_h1_classes.py
from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager

class wind_swe_h1_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot managers for each variable
    proton_wpar: plot_manager        # Proton parallel thermal speed
    proton_wperp: plot_manager       # Proton perpendicular thermal speed  
    proton_anisotropy: plot_manager  # Calculated anisotropy (Wperp/Wpar)
    alpha_w: plot_manager            # Alpha particle thermal speed
    fit_flag: plot_manager           # Data quality flag

    def __init__(self, imported_data: Any) -> None: ...
    def update(self, imported_data: Any, original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Dict[str, Any]) -> None: ...

# Global instance
wind_swe_h1: wind_swe_h1_class 