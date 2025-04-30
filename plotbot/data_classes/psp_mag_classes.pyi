#plotbot/data_classes/psp_mag_classes.pyi
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

class mag_rtn_4sa_class:
    raw_data: Dict[str, Optional[Union[np.ndarray, List[np.ndarray]]]]
    datetime: List[Any] # Or more specific type if known
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    field: Optional[np.ndarray]
    all: plot_manager
    br: plot_manager
    bt: plot_manager
    bn: plot_manager
    bmag: plot_manager
    pmag: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...

mag_rtn_4sa: mag_rtn_4sa_class

class mag_rtn_class:
    raw_data: Dict[str, Optional[Union[np.ndarray, List[np.ndarray]]]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    field: Optional[np.ndarray]
    all: plot_manager
    br: plot_manager
    bt: plot_manager
    bn: plot_manager
    bmag: plot_manager
    pmag: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...

mag_rtn: mag_rtn_class

class mag_sc_4sa_class:
    raw_data: Dict[str, Optional[Union[np.ndarray, List[np.ndarray]]]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    field: Optional[np.ndarray]
    all: plot_manager
    bx: plot_manager
    by: plot_manager
    bz: plot_manager
    bmag: plot_manager
    pmag: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...

mag_sc_4sa: mag_sc_4sa_class

class mag_sc_class:
    raw_data: Dict[str, Optional[Union[np.ndarray, List[np.ndarray]]]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    time: Optional[np.ndarray]
    field: Optional[np.ndarray]
    all: plot_manager
    bx: plot_manager
    by: plot_manager
    bz: plot_manager
    bmag: plot_manager
    pmag: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...

mag_sc: mag_sc_class