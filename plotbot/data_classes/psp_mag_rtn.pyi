# plotbot/data_classes/psp_mag_rtn.pyi
# Stub file for type hinting

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional, Union

# Import dependencies used in type hints (adjust paths if necessary)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

# Define a type alias for the imported data structure if possible
# Replace 'Any' with a more specific type if available (e.g., the DataObject namedtuple)
ImportedDataType = Any

class mag_rtn_class:
    raw_data: Dict[str, Optional[Union[np.ndarray, List[np.ndarray]]]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    field: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    all: plot_manager
    br: plot_manager
    bt: plot_manager
    bn: plot_manager
    bmag: plot_manager
    pmag: plot_manager
    br_norm: plot_manager
    _br_norm_manager: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...
    def _calculate_br_norm(self) -> bool: ...

mag_rtn: mag_rtn_class 