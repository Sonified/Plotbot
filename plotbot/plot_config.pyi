# plotbot/plot_config.pyi
from typing import Any, List, Tuple, Optional
import numpy as np
from .print_manager import print_manager # Assuming print_manager is needed

class plot_config:
    debug: bool
    data_type: Optional[str]
    class_name: Optional[str]
    subclass_name: Optional[str]
    plot_type: str
    var_name: Optional[str]
    _datetime_array: Optional[np.ndarray] # Private storage
    y_label: Optional[str]
    legend_label: Optional[str]
    color: Optional[str]
    y_scale: str
    y_limit: Optional[Tuple[float, float]]
    line_width: float
    line_style: str
    marker_size: float
    marker_style: str | Tuple[int, int]
    alpha: float
    colormap: str
    colorbar_scale: str
    colorbar_limits: Optional[Tuple[float, float]]
    additional_data: Any
    colorbar_label: Optional[str]
    title_font_size: int | float # Corrected name
    y_axis_label_font_size: int | float # Corrected name
    x_axis_label_font_size: int | float # Corrected name
    x_tick_label_font_size: int | float # Corrected name
    y_tick_label_font_size: int | float # Corrected name
    use_relative_time: bool
    # ... add other specific attributes if needed ...

    @property
    def datetime_array(self) -> Optional[np.ndarray]: ...
    @datetime_array.setter
    def datetime_array(self, value: Optional[np.ndarray]) -> None: ...

    # --- Deprecated Aliases ---
    # TODO: Remove these in future version
    @property
    def title_fontsize(self) -> int | float: ...
    @title_fontsize.setter
    def title_fontsize(self, value: int | float) -> None: ...

    @property
    def y_label_size(self) -> int | float: ...
    @y_label_size.setter
    def y_label_size(self, value: int | float) -> None: ...

    @property
    def x_label_size(self) -> int | float: ...
    @x_label_size.setter
    def x_label_size(self, value: int | float) -> None: ...

    @property
    def x_tick_label_size(self) -> int | float: ...
    @x_tick_label_size.setter
    def x_tick_label_size(self, value: int | float) -> None: ...

    @property
    def y_tick_label_size(self) -> int | float: ...
    @y_tick_label_size.setter
    def y_tick_label_size(self, value: int | float) -> None: ...

    def __init__(self, **kwargs) -> None: ...
    def reset(self) -> None: ...
    def save_state(self) -> None: ...
    def restore_state(self) -> None: ...

def retrieve_plot_config_snapshot(state_dict: dict) -> dict: ...

# Global instance
plt: plot_config 