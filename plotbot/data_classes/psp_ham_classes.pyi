# plotbot/data_classes/psp_ham_classes.pyi
# Stub file for type hinting - Ham CDF class (v02 format)

import numpy as np
from typing import Any, Dict, Optional

from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

# Define a type alias for the imported data structure
ImportedDataType = Any

class ham_class:
    # --- Internal Attributes ---
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[np.ndarray]]
    time: Optional[np.ndarray]  # TT2000 times
    datetime_array: Optional[np.ndarray]  # Python datetimes
    _original_cdf_file_path: str
    _cdf_file_pattern: str
    _current_operation_trange: Optional[Any]

    # --- Public Attributes (plot_manager instances) ---
    # Densities
    n_core: plot_manager
    n_neck: plot_manager
    n_ham: plot_manager

    # Velocities - Core
    vx_inst_core: plot_manager
    vy_inst_core: plot_manager
    vz_inst_core: plot_manager

    # Velocities - Neck
    vx_inst_neck: plot_manager
    vy_inst_neck: plot_manager
    vz_inst_neck: plot_manager

    # Velocities - Ham
    vx_inst_ham: plot_manager
    vy_inst_ham: plot_manager
    vz_inst_ham: plot_manager

    # Temperatures (scalar)
    temp_core: plot_manager
    temp_neck: plot_manager
    temp_ham: plot_manager

    # Temperatures (perpendicular/parallel)
    Tperp_core: plot_manager
    Tpar_core: plot_manager
    Tperp_neck: plot_manager
    Tpar_neck: plot_manager
    Tperp_ham: plot_manager
    Tpar_ham: plot_manager

    # Magnetic field
    Bx_inst: plot_manager
    By_inst: plot_manager
    Bz_inst: plot_manager

    # Other
    sun_dist_rsun: plot_manager

    # --- Methods ---
    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType], original_requested_trange: Optional[Any] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def _find_frequency_data(self) -> np.ndarray: ...
    def set_plot_config(self) -> None: ...
    def ensure_internal_consistency(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

# --- Module-level Instance ---
ham: ham_class
