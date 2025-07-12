# plotbot/data_classes/psp_orbit.pyi
# Stub file for type hinting

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional, Union

# Import dependencies used in type hints
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

# Define a type alias for the imported data structure
# For NPZ data, this could be either an NPZ file object or a dictionary
ImportedDataType = Any

class psp_orbit_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any]
    datetime_array: Optional[np.ndarray]
    _current_operation_trange: Optional[List[str]]
    r_sun: plot_manager
    carrington_lon: plot_manager
    carrington_lat: plot_manager
    icrf_x: Optional[plot_manager]  # Only available if ICRF data is present
    icrf_y: Optional[plot_manager]  # Only available if ICRF data is present
    icrf_z: Optional[plot_manager]  # Only available if ICRF data is present
    heliocentric_distance_au: plot_manager
    orbital_speed: plot_manager
    velocity_x: plot_manager
    velocity_y: plot_manager
    velocity_z: plot_manager
    angular_momentum: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def set_ploptions(self) -> None: ...
    def _calculate_orbital_speed(self, r_sun: np.ndarray, carrington_lon: np.ndarray, carrington_lat: np.ndarray) -> np.ndarray: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

psp_orbit: psp_orbit_class 