# Stubs for plotbot.data_classes.psp_qtn_classes
# -*- coding: utf-8 -*-

import numpy as np
from typing import Optional, List, Any, Dict
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions

class psp_qtn_class:
    # Core attributes
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot manager attributes
    density: plot_manager
    temperature: plot_manager
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = ...) -> None: ...
    
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    
    def calculate_variables(self, imported_data: Any) -> None: ...
    
    def set_ploptions(self) -> None: ...
    
    def ensure_internal_consistency(self) -> None: ...
    
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# Module-level instance
psp_qtn: psp_qtn_class 