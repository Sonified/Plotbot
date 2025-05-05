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
    hspace_vertical_space_between_plots: float
    title_font_size: int
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
    y_axis_label_font_size: int
    x_axis_label_font_size: int
    y_label_pad: Union[int, float]
    x_label_pad: Union[int, float]
    x_tick_label_font_size: int
    y_tick_label_font_size: int
    second_variable_on_right_axis: bool
    # HAM-specific options
    hamify: bool
    ham_var: Any  # Will be a plot_manager object
    color_mode: str
    single_color: Optional[str]
    save_output: bool
    save_preset: Optional[str]
    save_dpi: Optional[int]
    output_dimensions: Optional[Tuple[int, int]]
    bbox_inches_save_crop_mode: str
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    title_pad: float
    title_y_position: float
    magnetic_field_line_width: float
    tick_length: float
    tick_width: float
    # Positional X-Axis Properties
    x_axis_r_sun: bool
    x_axis_carrington_lon: bool
    x_axis_carrington_lat: bool
    _x_axis_positional_range: Optional[Tuple[float, float]]
    positional_tick_density: int
    positional_data_path: str
    # Internal attributes for presets (usually omitted from stubs)
    # _orig_width: Union[int, float]
    # _orig_height_per_panel: Union[int, float]
    bold_title: bool
    bold_x_axis_label: bool
    bold_y_axis_label: bool
    use_default_plot_settings: bool
    constrained_layout: bool
    y_label_left_align: bool
    y_label_alignment: str
    size_of_tiny_date_in_the_corner: int
    ham_opacity: float

    # --- Methods ---
    def __init__(self) -> None: ...
    def reset(self) -> None: ...
    # Internal helper omitted: _get_axis_options
    def set_global_y_limit(self, limits: Optional[Tuple[float, float]]) -> None: ...
    def __getattr__(self, name: str) -> AxisOptions: ... # Dynamic axis access
    def print_state(self) -> None: ...
    # Internal preset helpers omitted: _apply_preset_config, _restore_original_values

    # --- Properties for Positional X-Axis ---
    @property
    def using_positional_x_axis(self) -> bool: ...
    @property
    def active_positional_data_type(self) -> Optional[str]: ...
    @property
    def x_axis_positional_range(self) -> Optional[Tuple[float, float]]: ...
    @x_axis_positional_range.setter
    def x_axis_positional_range(self, value: Optional[Tuple[float, float]]) -> None: ...
    @property
    def hspace_vertical_space_between_plots(self) -> float: ...
    @hspace_vertical_space_between_plots.setter
    def hspace_vertical_space_between_plots(self, value: float) -> None: ...
    # Deprecated alias for backward compatibility
    @property
    def h_space_vertical_between_plots(self) -> float: ...
    @h_space_vertical_between_plots.setter
    def h_space_vertical_between_plots(self, value: float) -> None: ...

    # --- Properties for Axes (Explicitly defined for all 30) ---
    @property
    def ax1(self) -> AxisOptions: ...
    @property
    def ax2(self) -> AxisOptions: ...
    @property
    def ax3(self) -> AxisOptions: ...
    @property
    def ax4(self) -> AxisOptions: ...
    @property
    def ax5(self) -> AxisOptions: ...
    @property
    def ax6(self) -> AxisOptions: ...
    @property
    def ax7(self) -> AxisOptions: ...
    @property
    def ax8(self) -> AxisOptions: ...
    @property
    def ax9(self) -> AxisOptions: ...
    @property
    def ax10(self) -> AxisOptions: ...
    @property
    def ax11(self) -> AxisOptions: ...
    @property
    def ax12(self) -> AxisOptions: ...
    @property
    def ax13(self) -> AxisOptions: ...
    @property
    def ax14(self) -> AxisOptions: ...
    @property
    def ax15(self) -> AxisOptions: ...
    @property
    def ax16(self) -> AxisOptions: ...
    @property
    def ax17(self) -> AxisOptions: ...
    @property
    def ax18(self) -> AxisOptions: ...
    @property
    def ax19(self) -> AxisOptions: ...
    @property
    def ax20(self) -> AxisOptions: ...
    @property
    def ax21(self) -> AxisOptions: ...
    @property
    def ax22(self) -> AxisOptions: ...
    @property
    def ax23(self) -> AxisOptions: ...
    @property
    def ax24(self) -> AxisOptions: ...
    @property
    def ax25(self) -> AxisOptions: ...
    @property
    def ax26(self) -> AxisOptions: ...
    @property
    def ax27(self) -> AxisOptions: ...
    @property
    def ax28(self) -> AxisOptions: ...
    @property
    def ax29(self) -> AxisOptions: ...
    @property
    def ax30(self) -> AxisOptions: ...

    @property
    def y_label_left_align(self) -> bool: ...
    @y_label_left_align.setter
    def y_label_left_align(self, value: bool) -> None: ...

    @property
    def y_label_alignment(self) -> str:
        ...
    
    @property
    def y_axis_label_font_size(self) -> int:
        ...
    
    @property
    def x_axis_label_font_size(self) -> int: ...
    @x_axis_label_font_size.setter
    def x_axis_label_font_size(self, value: int) -> None: ...

    @property
    def y_tick_label_font_size(self) -> int: ...
    @y_tick_label_font_size.setter
    def y_tick_label_font_size(self, value: int) -> None: ...

    @property
    def x_tick_label_font_size(self) -> int: ...
    @x_tick_label_font_size.setter
    def x_tick_label_font_size(self, value: int) -> None: ...

    @property
    def title_font_size(self) -> int: ...
    @title_font_size.setter
    def title_font_size(self, value: int) -> None: ...

    @property
    def bbox_inches_save_crop_mode(self) -> str: ...
    @bbox_inches_save_crop_mode.setter
    def bbox_inches_save_crop_mode(self, value: str) -> None: ...
    # Deprecated alias for backward compatibility
    @property
    def save_bbox_inches(self) -> str: ...
    @save_bbox_inches.setter
    def save_bbox_inches(self, value: str) -> None: ...

    # --- NEW PROPERTIES for Degrees from Perihelion --- 
    @property
    def use_degrees_from_perihelion(self) -> bool: ...
    @use_degrees_from_perihelion.setter
    def use_degrees_from_perihelion(self, value: bool) -> None: ...
    
    @property
    def degrees_from_perihelion_range(self) -> Optional[Tuple[float, float]]: ...
    @degrees_from_perihelion_range.setter
    def degrees_from_perihelion_range(self, value: Optional[Tuple[float, float]]) -> None: ...
    
    @property
    def degrees_from_perihelion_tick_step(self) -> Optional[float]: ...
    @degrees_from_perihelion_tick_step.setter
    def degrees_from_perihelion_tick_step(self, value: Optional[float]) -> None: ...
    # --- END NEW PROPERTIES --- 

    # --- NEW PROPERTY for Tight X Axis ---
    @property
    def tight_x_axis(self) -> bool: ...
    @tight_x_axis.setter
    def tight_x_axis(self, value: bool) -> None: ...
    # --- END NEW PROPERTY ---

# --- EnhancedPlotting Class ---
class EnhancedPlotting:
    # --- Attributes ---
    options: MultiplotOptions
    # Note: Other attributes are dynamically copied from mpl_plt
    figure: Any
    subplots: Any
    show: Any
    plot: Any
    scatter: Any
    colorbar: Any
    xlabel: Any
    ylabel: Any
    title: Any
    xlim: Any
    ylim: Any
    savefig: Any
    close: Any
    grid: Any
    legend: Any
    
    # --- Methods ---
    def __init__(self) -> None: ...


# --- Module-level Instances ---
plt: EnhancedPlotting

# Reminder: If you add functions directly to the .py file (outside of classes), add their signatures here too, ending with '...'.
