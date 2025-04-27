# Stubs for plotbot.data_classes.psp_proton_classes
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from cdflib import cdfepoch
from datetime import datetime
from typing import Optional, Tuple, Any, Union, List, Dict

# Assume these types are defined elsewhere in plotbot and importable
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions

# Type alias for potential data object structure (replace Any if a specific class exists)
ImportedDataType = Any

# Define the structure of the raw_data dictionary more accurately if possible
RawDataDict = Dict[str, Optional[np.ndarray]]

# --- proton_class ---
class proton_class:
    # --- Internal Attributes (with type hints) ---
    raw_data: RawDataDict
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray] # Actually created via meshgrid
    times_mesh_angle: Optional[np.ndarray] # Actually created via meshgrid
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    time: Optional[np.ndarray] # Added from calculate_variables
    mag_field: Optional[np.ndarray] # Added from calculate_variables
    temp_tensor: Optional[np.ndarray] # Added from calculate_variables

    # --- Public Attributes (plot_manager instances created by set_ploptions) ---
    t_par: plot_manager
    t_perp: plot_manager
    anisotropy: plot_manager
    v_alfven: plot_manager
    v_sw: plot_manager
    m_alfven: plot_manager
    beta_ppar: plot_manager
    beta_pperp: plot_manager
    pressure_ppar: plot_manager
    pressure_pperp: plot_manager
    pressure: plot_manager
    density: plot_manager
    temperature: plot_manager
    bmag: plot_manager
    vr: plot_manager
    vt: plot_manager
    vn: plot_manager
    energy_flux: plot_manager
    theta_flux: plot_manager
    phi_flux: plot_manager

    # --- Methods ---
    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> None: ... # Returns None implicitly
    def __setattr__(self, name: str, value: Any) -> None: ...
    # Note: calculate_variables, set_ploptions, _calculate_temperature_anisotropy
    # are typically internal, not part of public API stub
    # def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    # def _calculate_temperature_anisotropy(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    # def set_ploptions(self) -> None: ...

# --- proton_hr_class ---
class proton_hr_class:
    # --- Internal Attributes ---
    raw_data: RawDataDict
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    times_mesh_angle: Optional[np.ndarray]
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    time: Optional[np.ndarray]
    mag_field: Optional[np.ndarray]
    temp_tensor: Optional[np.ndarray]

    # --- Public Attributes ---
    t_par: plot_manager
    t_perp: plot_manager
    anisotropy: plot_manager
    v_alfven: plot_manager
    v_sw: plot_manager
    m_alfven: plot_manager
    beta_ppar: plot_manager
    beta_pperp: plot_manager
    pressure_ppar: plot_manager
    pressure_pperp: plot_manager
    pressure: plot_manager
    density: plot_manager
    temperature: plot_manager
    bmag: plot_manager
    vr: plot_manager
    vt: plot_manager
    vn: plot_manager
    energy_flux: plot_manager
    theta_flux: plot_manager
    phi_flux: plot_manager

    # --- Methods ---
    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> None: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    # def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    # def _calculate_temperature_anisotropy(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    # def set_ploptions(self) -> None: ...

# --- Module-level Instances ---
proton: proton_class
proton_hr: proton_hr_class

# Reminder: If you add functions directly to the .py file (outside of classes), add their signatures here too, ending with '...'.
