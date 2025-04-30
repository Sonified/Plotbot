# Stubs for plotbot.multiplot_options
# -*- coding: utf-8 -*-

import matplotlib.pyplot as mpl_plt # Used as source for EnhancedPlotting
from typing import Optional, Tuple, Any, Union, Dict, ClassVar

# --- RightAxisOptions Class ---
class RightAxisOptions:
    # --- Attributes ---
    y_limit: Optional[Tuple[float, float]]
    color: Optional[str]

    # --- Methods ---
    def __init__(self) -> None: ...
    # Properties are implicitly defined by setters/getters in stub
    # @property def y_limit(...) -> ...
    # @y_limit.setter def y_limit(...) -> None: ...
    # @property def color(...) -> ...
    # @color.setter def color(...) -> None: ...

# --- AxisOptions Class ---
class AxisOptions:
    # --- Attributes ---
    y_limit: Optional[Tuple[float, float]]
    color: Optional[str]
    colorbar_limits: Optional[Tuple[float, float]]
    draw_horizontal_line: bool
    horizontal_line_value: float
    horizontal_line_width: float
    horizontal_line_color: str
    horizontal_line_style: str
    r: RightAxisOptions

    # --- Methods ---
    def __init__(self) -> None: ...
    # Properties are implicitly defined by setters/getters in stub
    # ... (properties for all attributes) ...

# --- MultiplotOptions Class ---
class MultiplotOptions:
    # --- Class Attributes ---
    PRESET_CONFIGS: ClassVar[Dict[str, Dict[str, Any]]]
    # --- Instance Attributes (Defaults set in reset) ---
    _global_y_limit: Optional[Tuple[float, float]]
    axes: Dict[int, AxisOptions] # Stores AxisOptions instances

    window: str
    position: str
    width: Union[int, float] # Can be overridden by presets
    height_per_panel: Union[int, float] # Can be overridden by presets
    hspace: float
    title_fontsize: int
    use_single_title: bool
    single_title_text: Optional[str]
    border_line_width: float
    draw_vertical_line: bool
    vertical_line_width: float
    vertical_line_color: str
    vertical_line_style: str
    draw_horizontal_line: bool # Global default
    horizontal_line_value: float # Global default
    horizontal_line_width: float # Global default
    horizontal_line_color: str # Global default
    horizontal_line_style: str # Global default
    use_relative_time: bool
    relative_time_step_units: str
    relative_time_step: int
    use_single_x_axis: bool
    use_custom_x_axis_label: bool
    custom_x_axis_label: Optional[str]
    y_label_uses_encounter: bool
    y_label_includes_time: bool
    y_label_size: Union[int, float]
    x_label_size: Union[int, float]
    y_label_pad: Union[int, float]
    x_label_pad: Union[int, float]
    x_tick_label_size: Union[int, float]
    y_tick_label_size: Union[int, float]
    second_variable_on_right_axis: bool
    color_mode: str
    single_color: Optional[str]
    save_output: bool
    save_preset: Optional[str]
    save_dpi: Optional[int]
    output_dimensions: Optional[Tuple[int, int]]
    title_pad: float
    title_y_position: float
    magnetic_field_line_width: float
    tick_length: float
    tick_width: float
    # Internal attributes for presets (usually omitted from stubs)
    # _orig_width: Union[int, float]
    # _orig_height_per_panel: Union[int, float]

    # --- Methods ---
    def __init__(self) -> None: ...
    def reset(self) -> None: ...
    # Internal helper omitted: _get_axis_options
    def set_global_y_limit(self, limits: Optional[Tuple[float, float]]) -> None: ...
    def __getattr__(self, name: str) -> AxisOptions: ... # Dynamic axis access
    def print_state(self) -> None: ...
    # Internal preset helpers omitted: _apply_preset_config, _restore_original_values

    # --- Properties for Axes (Explicitly defined up to ax25) ---
    @property
    def ax1(self) -> AxisOptions: ...
    @property
    def ax2(self) -> AxisOptions: ...
    # ... (ax3 through ax24) ...
    @property
    def ax25(self) -> AxisOptions: ...
    # __getattr__ handles axN beyond 25

# --- EnhancedPlotting Class ---
class EnhancedPlotting:
    # --- Attributes ---
    options: MultiplotOptions
    # Note: Other attributes are dynamically copied from mpl_plt.
    # Stubs cannot fully represent this dynamic behavior, but type checkers
    # might infer mpl_plt attributes if the inheritance was explicit or via protocols.
    # For basic stubs, just showing 'options' is often sufficient.
    # We can add __getattr__ to hint that other attributes exist.
    def __getattr__(self, name: str) -> Any: ... # Hint that other attributes might exist

    # --- Methods ---
    def __init__(self) -> None: ...


# --- Module-level Instances ---
plt: EnhancedPlotting

# Reminder: If you add functions directly to the .py file (outside of classes), add their signatures here too, ending with '...'.
