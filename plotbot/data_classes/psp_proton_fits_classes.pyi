# plotbot/data_classes/psp_proton_fits_classes.pyi
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
from plotbot.ploptions import ploptions

# Define constants (optional in stub, but can help clarity)
m: float
m_proton_kg: float

# Define a type alias for the imported data structure if possible
ImportedDataType = Any 

class proton_fits_class:
    # --- Internal Attributes ---
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime: List[Any] # Or more specific type if known
    datetime_array: Optional[np.ndarray]
    # 'time' attribute is not explicitly set, but likely implicitly exists if datetime_array does

    # --- Public Attributes (plot_manager instances) ---
    # Add attributes for ALL plot_manager instances created in set_ploptions
    np1: plot_manager
    np2: plot_manager
    Tperp1: plot_manager
    Tperp2: plot_manager
    Trat1: plot_manager
    Trat2: plot_manager
    vdrift: plot_manager
    vp1_x: plot_manager
    vp1_y: plot_manager
    vp1_z: plot_manager
    chi_p: plot_manager  # Changed from 'chi' to 'chi_p' to match usage
    qz_p: plot_manager
    # vsw_mach: plot_manager # Placeholder, might not be plotted
    beta_ppar: plot_manager
    beta_pperp: plot_manager
    ham_param: plot_manager
    n_tot: plot_manager
    np2_np1_ratio: plot_manager
    vp1_mag: plot_manager
    vcm_x: plot_manager
    vcm_y: plot_manager
    vcm_z: plot_manager
    vcm_mag: plot_manager
    vdrift_abs: plot_manager
    vdrift_va: plot_manager
    Trat_tot: plot_manager
    Tpar1: plot_manager
    Tpar2: plot_manager
    Tpar_tot: plot_manager
    Tperp_tot: plot_manager
    Temp_tot: plot_manager
    abs_qz_p: plot_manager # Renamed from '|qz_p|' for attribute validity
    chi_p_norm: plot_manager
    valfven: plot_manager
    B_mag: plot_manager
    # bhat_x: plot_manager # Unit vector components might not be plotted
    # bhat_y: plot_manager
    # bhat_z: plot_manager
    vp2_x: plot_manager
    vp2_y: plot_manager
    vp2_z: plot_manager
    vp2_mag: plot_manager
    qz_p_perp: plot_manager
    qz_p_par: plot_manager
    Vcm_mach: plot_manager
    Vp1_mach: plot_manager
    beta_p_tot: plot_manager
    
    # Scatter plot specific attributes (if they are plot_manager instances)
    # qz_p_beta_ppar_scatter: plot_manager 
    # ... add others if needed

    # --- Methods ---
    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ... # Changed return to Any based on implementation
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def _create_fits_scatter_ploptions(self, var_name: str, subclass_name: str, y_label: str, legend_label: str, color: str) -> ploptions: ...
    def set_ploptions(self) -> None: ...

# --- Module-level Instance ---
proton_fits: proton_fits_class
