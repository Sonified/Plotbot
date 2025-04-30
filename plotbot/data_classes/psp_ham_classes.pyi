# plotbot/data_classes/psp_ham_classes.pyi
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

class ham_class:
    # --- Internal Attributes ---
    raw_data: Dict[str, Optional[np.ndarray]]
    time: Optional[np.ndarray] # TT2000 times
    datetime_array: Optional[np.ndarray] # Python datetimes

    # --- Public Attributes (plot_manager instances) ---
    # Add attributes for ALL plot_manager instances created in set_ploptions
    hamogram_30s: plot_manager
    hamogram_og_30s: plot_manager
    # hamogram_1m: plot_manager # Removed - Placeholder
    # hamogram_og_1m: plot_manager # Removed - Placeholder
    hamogram_2m: plot_manager
    hamogram_og_2m: plot_manager
    hamogram_20m: plot_manager
    # hamogram_og_20m: plot_manager # Removed - Placeholder
    hamogram_90m: plot_manager
    # hamogram_og_90m: plot_manager # Removed - Placeholder
    hamogram_4h: plot_manager
    hamogram_og_4h: plot_manager
    # hamogram_12h: plot_manager # Removed - Placeholder
    # hamogram_og_12h: plot_manager # Removed - Placeholder
    trat_ham: plot_manager
    trat_ham_og: plot_manager
    ham_core_drift: plot_manager
    ham_core_drift_va: plot_manager
    Nham_div_Ncore: plot_manager
    Nham_div_Ncore_og: plot_manager
    Nham_div_Ntot: plot_manager
    Nham_div_Ntot_og: plot_manager
    Tperp_ham_div_core: plot_manager
    Tperp_ham_div_core_og: plot_manager
    Tperprat_driftva_hc: plot_manager
    Tperprat_driftva_hc_og: plot_manager
    # Placeholders like 'hamstring', 'N_core' etc. are not typically plot_managers

    # --- Methods ---
    def __init__(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def update(self, imported_data: Optional[ImportedDataType]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ... # Changed return to Any based on implementation
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: ImportedDataType) -> None: ...
    def _create_ham_scatter_ploptions(self, var_name: str, subclass_name: str, y_label: str, legend_label: str, color: str, marker_style: Tuple[int, int]=(5, 1), marker_size: int=20, alpha: float=0.2, y_limit: Optional[List[Optional[float]]]=None) -> ploptions: ...
    def _create_ham_timeseries_ploptions(self, var_name: str, subclass_name: str, y_label: str, legend_label: str, color: str, y_limit: List[Optional[float]]=[0, None], line_width: int=1, line_style: str='-') -> ploptions: ...
    def set_ploptions(self) -> None: ...

# --- Module-level Instance ---
ham: ham_class
