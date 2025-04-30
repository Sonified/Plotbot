# plotbot/data_classes/psp_proton_classes.pyi
# Stub file for type hinting

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Import dependencies used in type hints (adjust paths if necessary)
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions

# Define a type alias for the imported data structure if possible
ImportedDataType = Any 

class proton_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray] # Updated based on usage
    times_mesh_angle: Optional[np.ndarray] # Updated based on usage
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    time: Optional[np.ndarray] # Added based on calculate_variables
    mag_field: Optional[np.ndarray] # Added based on calculate_variables
    temp_tensor: Optional[np.ndarray] # Added based on calculate_variables
    energy_flux: Optional[np.ndarray] # Added based on calculate_variables
    theta_flux: Optional[np.ndarray] # Added based on calculate_variables
    phi_flux: Optional[np.ndarray] # Added based on calculate_variables

    # Subclasses (plot managers) - define attributes for each component
    vr: plot_manager
    vt: plot_manager
    vn: plot_manager
    t_par: plot_manager
    t_perp: plot_manager
    anisotropy: plot_manager
    v_alfven: plot_manager
    beta_ppar: plot_manager
    beta_pperp: plot_manager
    pressure_ppar: plot_manager
    pressure_pperp: plot_manager
    energy_flux_spec: plot_manager # Renamed to avoid conflict with raw data
    theta_flux_spec: plot_manager  # Renamed to avoid conflict with raw data
    phi_flux_spec: plot_manager    # Renamed to avoid conflict with raw data
    v_sw: plot_manager
    m_alfven: plot_manager
    temperature: plot_manager
    pressure: plot_manager
    density: plot_manager
    bmag: plot_manager
    # Add centroids if they are assigned plot_managers
    # centroids_spi_nrg: plot_manager 
    # centroids_spi_theta: plot_manager
    # centroids_spi_phi: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def _calculate_temperature_anisotropy(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def set_ploptions(self) -> None: ...

proton: proton_class # Assuming 'proton' is the intended instance name

class proton_hr_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime_array: Optional[np.ndarray]
    times_mesh: Optional[np.ndarray]
    times_mesh_angle: Optional[np.ndarray]
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    time: Optional[np.ndarray]
    mag_field: Optional[np.ndarray]
    temp_tensor: Optional[np.ndarray]
    energy_flux: Optional[np.ndarray]
    theta_flux: Optional[np.ndarray]
    phi_flux: Optional[np.ndarray]

    # Subclasses (plot managers) - define attributes for each component
    vr: plot_manager
    vt: plot_manager
    vn: plot_manager
    t_par: plot_manager
    t_perp: plot_manager
    anisotropy: plot_manager
    v_alfven: plot_manager
    beta_ppar: plot_manager
    beta_pperp: plot_manager
    pressure_ppar: plot_manager
    pressure_pperp: plot_manager
    energy_flux_spec: plot_manager
    theta_flux_spec: plot_manager
    phi_flux_spec: plot_manager
    v_sw: plot_manager
    m_alfven: plot_manager
    temperature: plot_manager
    pressure: plot_manager
    density: plot_manager
    bmag: plot_manager
    # centroids_spi_nrg: plot_manager
    # centroids_spi_theta: plot_manager
    # centroids_spi_phi: plot_manager

    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def _calculate_temperature_anisotropy(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def set_ploptions(self) -> None: ...

proton_hr: proton_hr_class # Assuming 'proton_hr' is the intended instance name
