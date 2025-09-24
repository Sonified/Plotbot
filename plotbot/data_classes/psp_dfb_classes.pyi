# plotbot/data_classes/psp_dfb_classes.pyi - Type hints for PSP DFB electric field spectra classes

from typing import Optional, List, Dict, Any
import numpy as np
from plotbot.plot_manager import plot_manager
from plotbot.data_import import DataObject

class psp_dfb_class:
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Plot managers for electric field spectra
    ac_spec_dv12: plot_manager    # AC spectrum from antenna pair 1-2
    ac_spec_dv34: plot_manager    # AC spectrum from antenna pair 3-4
    dc_spec_dv12: plot_manager    # DC spectrum from antenna pair 1-2
    
    def __init__(self, imported_data: Optional[DataObject]) -> None: ...
    def update(self, imported_data: Optional[DataObject], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def calculate_variables(self, imported_data: DataObject) -> None: ...
    def set_plot_config(self) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

# Global instance
psp_dfb: psp_dfb_class 