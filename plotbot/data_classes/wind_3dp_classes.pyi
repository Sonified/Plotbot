# wind_3dp_classes.pyi - Type hints for WIND 3DP electron classes

from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager

class wind_3dp_elpd_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    time: Optional[np.ndarray]
    energy_index: int
    _current_operation_trange: Optional[List[str]]
    
    # Plot manager attributes
    flux: plot_manager
    flux_selected_energy: plot_manager  
    centroids: plot_manager
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...
    
    @property
    def pitch_angle_y_values(self) -> Optional[np.ndarray]: ...

# Global instance
wind_3dp_elpd: wind_3dp_elpd_class 