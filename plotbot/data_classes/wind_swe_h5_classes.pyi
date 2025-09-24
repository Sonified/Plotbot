# wind_swe_h5_classes.pyi - Type hints for WIND SWE H5 electron temperature classes

from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager

class wind_swe_h5_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot manager attributes
    t_elec: plot_manager
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# Global instance
wind_swe_h5: wind_swe_h5_class 