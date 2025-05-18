# plotbot/data_classes/psp_proton_hr.pyi
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from plotbot.plot_manager import plot_manager
from plotbot.data_import import DataObject # Assuming DataObject is the type for imported_data

class proton_hr_class:
    raw_data: Dict[str, Optional[np.ndarray]]
    datetime_array: Optional[np.ndarray]
    times_mesh: Union[List[Any], np.ndarray]
    times_mesh_angle: Union[List[Any], np.ndarray]
    energy_vals: Optional[np.ndarray]
    theta_vals: Optional[np.ndarray]
    phi_vals: Optional[np.ndarray]
    data_type: str
    time: Optional[np.ndarray]
    mag_field: Optional[np.ndarray]
    temp_tensor: Optional[np.ndarray]
    # field: Optional[np.ndarray] # This attribute is not explicitly initialized or set in psp_proton_hr.py

    # Attributes that become plot_manager instances
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
    energy_flux: plot_manager # This is re-assigned in set_ploptions
    theta_flux: plot_manager  # This is re-assigned in set_ploptions
    phi_flux: plot_manager    # This is re-assigned in set_ploptions

    def __init__(self, imported_data: Optional[DataObject]) -> None: ...
    def update(self, imported_data: Optional[DataObject]) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def calculate_variables(self, imported_data: DataObject) -> None: ...
    def _calculate_temperature_anisotropy(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def set_ploptions(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...

proton_hr: proton_hr_class 