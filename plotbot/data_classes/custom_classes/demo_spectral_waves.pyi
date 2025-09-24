"""
Type hints for auto-generated plotbot class demo_spectral_waves
Generated on: 2025-07-23T17:28:11.535757
Source: PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf
"""

from typing import Optional, List, Dict, Any
from numpy import ndarray
from datetime import datetime
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config

class demo_spectral_waves_class:
    """CDF data class for PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf"""
    
    # Class attributes
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[ndarray]]
    datetime: List[datetime]
    datetime_array: Optional[ndarray]
    time: Optional[ndarray]
    times_mesh: Optional[ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Variable attributes
    FFT_time_1: plot_manager
    Frequencies: plot_manager
    ellipticity_b: plot_manager
    FFT_time_2: plot_manager
    Frequencies_1: plot_manager
    wave_normal_b: plot_manager
    FFT_time_3: plot_manager
    Frequencies_2: plot_manager
    coherency_b: plot_manager
    FFT_time_4: plot_manager
    Frequencies_3: plot_manager
    B_power_para: plot_manager
    FFT_time_5: plot_manager
    Frequencies_4: plot_manager
    B_power_perp: plot_manager
    FFT_time_6: plot_manager
    Frequencies_5: plot_manager
    Wave_Power_b: plot_manager
    FFT_time_7: plot_manager
    Frequencies_6: plot_manager
    S_mag: plot_manager
    FFT_time_8: plot_manager
    Frequencies_7: plot_manager
    S_Theta: plot_manager
    FFT_time_9: plot_manager
    Frequencies_8: plot_manager
    S_Phi: plot_manager
    FFT_time_10: plot_manager
    Frequencies_9: plot_manager
    Sn: plot_manager
    FFT_time_11: plot_manager
    Frequencies_10: plot_manager
    Sp: plot_manager
    FFT_time_12: plot_manager
    Frequencies_11: plot_manager
    Sq: plot_manager
    Bfield_time: plot_manager
    Bn: plot_manager
    Bfield_time_1: plot_manager
    Bp: plot_manager
    Bfield_time_2: plot_manager
    Bq: plot_manager
    FFT_time_13: plot_manager
    Frequencies_12: plot_manager
    Bn_fft: plot_manager
    FFT_time_14: plot_manager
    Frequencies_13: plot_manager
    Bp_fft: plot_manager
    FFT_time_15: plot_manager
    Frequencies_14: plot_manager
    Bq_fft: plot_manager
    FFT_time_16: plot_manager
    Frequencies_15: plot_manager
    ellipticity_e: plot_manager
    FFT_time_17: plot_manager
    Frequencies_16: plot_manager
    wave_normal_e: plot_manager
    FFT_time_18: plot_manager
    Frequencies_17: plot_manager
    coherency_e: plot_manager
    FFT_time_19: plot_manager
    Frequencies_18: plot_manager
    E_power_para: plot_manager
    FFT_time_20: plot_manager
    Frequencies_19: plot_manager
    E_power_perp: plot_manager
    FFT_time_21: plot_manager
    Frequencies_20: plot_manager
    Wave_Power_e: plot_manager
    FFT_time_22: plot_manager
    Frequencies_21: plot_manager
    En_fft: plot_manager
    FFT_time_23: plot_manager
    Frequencies_22: plot_manager
    Ep_fft: plot_manager
    FFT_time_24: plot_manager
    Frequencies_23: plot_manager
    Eq_fft: plot_manager
    FFT_time_25: plot_manager
    Frequencies_24: plot_manager
    kx_B: plot_manager
    FFT_time_26: plot_manager
    Frequencies_25: plot_manager
    ky_B: plot_manager
    FFT_time_27: plot_manager
    Frequencies_26: plot_manager
    kz_B: plot_manager
    FFT_time_28: plot_manager
    Frequencies_27: plot_manager
    kx_E: plot_manager
    FFT_time_29: plot_manager
    Frequencies_28: plot_manager
    ky_E: plot_manager
    FFT_time_30: plot_manager
    Frequencies_29: plot_manager
    kz_E: plot_manager
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_plot_config(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

# Instance
demo_spectral_waves: demo_spectral_waves_class
