"""
Type hints for auto-generated plotbot class psp_waves_real_test
Generated on: 2025-07-23T12:15:50.003400
Source: PSP_wavePower_2021-04-29_v1.3.cdf
"""

from typing import Optional, List, Dict, Any
from numpy import ndarray
from datetime import datetime
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions

class psp_waves_real_test_class:
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
    def set_ploptions(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# Instance
psp_waves_real_test: psp_waves_real_test_class
