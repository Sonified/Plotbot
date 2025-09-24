# wind_mfi_classes.pyi - Type hints for WIND MFI magnetic field classes

import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any, Union
from plotbot.plot_manager import plot_manager

class wind_mfi_h2_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: pd.Series
    datetime_array: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot managers for each component
    all: plot_manager
    bx: plot_manager
    by: plot_manager
    bz: plot_manager
    bmag: plot_manager
    bgse: plot_manager

    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[Union[plot_manager, np.ndarray]]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Dict[str, Any]) -> None: ...
    def ensure_internal_consistency(self) -> None: ...

# Global instance
wind_mfi_h2: wind_mfi_h2_class 