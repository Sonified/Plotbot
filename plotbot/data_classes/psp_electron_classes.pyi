# plotbot/data_classes/psp_electron_classes.pyi
# Stub file for type hinting

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Import dependencies used in type hints (adjust paths if necessary)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

# Define a type alias for the imported data structure if possible
ImportedDataType = Any 

class epad_strahl_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any] # Or more specific type if known
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    pitch_angle: Optional[np.ndarray]
    time: Optional[np.ndarray] # Added based on calculate_variables
    energy_index: int # Added based on calculate_variables
    strahl: plot_manager
    centroids: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_plot_config(self) -> None: ...

epad: epad_strahl_class # Assuming 'epad' is the intended instance name based on data_cubby.stash

class epad_strahl_high_res_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any] # Or more specific type if known
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    pitch_angle: Optional[np.ndarray]
    time: Optional[np.ndarray] # Added based on calculate_variables
    energy_index: int # Added based on calculate_variables
    strahl: plot_manager
    centroids: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_plot_config(self) -> None: ...

epad_hr: epad_strahl_high_res_class # Assuming 'epad_high_res' is the intended instance name
