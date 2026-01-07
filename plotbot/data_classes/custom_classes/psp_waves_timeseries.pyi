"""
Type hints for auto-generated plotbot class psp_waves_timeseries
Generated on: 2026-01-07T13:16:32.717691
Source: PSP_wavePower_2021-04-29_v1.3.cdf
"""

from typing import Optional, List, Dict, Any
from numpy import ndarray
from datetime import datetime
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

class psp_waves_timeseries_class:
    """CDF data class for PSP_wavePower_2021-04-29_v1.3.cdf"""
    
    # Class attributes
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[ndarray]]
    datetime: List[datetime]
    datetime_array: Optional[ndarray]
    time: Optional[ndarray]
    times_mesh: Optional[ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Variable attributes
    wavePower_LH: plot_manager
    wavePower_RH: plot_manager
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

# Instance
psp_waves_timeseries: psp_waves_timeseries_class
