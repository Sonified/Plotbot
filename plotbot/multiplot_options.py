#plotbot/multiplot_options.py

import matplotlib.pyplot as mpl_plt
from .print_manager import print_manager
from typing import Optional, Tuple, Any, Union
import pathlib

class RightAxisOptions:
    """Stores right-axis specific options."""
    def __init__(self):
        self.y_limit = None
        self.color = None
    
    # Properties for IDE autocompletion
    @property
    def y_limit(self) -> Optional[Tuple[float, float]]:
        """Y-axis limits for the right axis."""
        return self.__dict__['y_limit']
        
    @y_limit.setter
    def y_limit(self, value: Optional[Tuple[float, float]]):
        self.__dict__['y_limit'] = value
        
    @property
    def color(self) -> Optional[str]:
        """Color for the right axis."""
        return self.__dict__['color']
        
    @color.setter
    def color(self, value: Optional[str]):
        self.__dict__['color'] = value

class AxisOptions:
    """Stores per-axis options like y_limit and color."""
    def __init__(self):
        self.y_limit = None
        self.color = None
        self.colorbar_limits = None
        # Horizontal line options
        self.draw_horizontal_line = False
        self.horizontal_line_value = 1.0
        self.horizontal_line_width = 1.0
        self.horizontal_line_color = 'black'
        self.horizontal_line_style = '-'
        self.r = RightAxisOptions()  # Add right axis options
    
    # Properties for IDE autocompletion
    @property
    def y_limit(self) -> Optional[Tuple[float, float]]:
        """Y-axis limits for this axis."""
        return self.__dict__['y_limit']
        
    @y_limit.setter
    def y_limit(self, value: Optional[Tuple[float, float]]):
        self.__dict__['y_limit'] = value
        print_manager.debug(f"[AxisOptions Setter] Set y_limit to {value} for instance ID {id(self)}")
        
    @property
    def color(self) -> Optional[str]:
        """Color for this axis."""
        return self.__dict__['color']
        
    @color.setter
    def color(self, value: Optional[str]):
        self.__dict__['color'] = value
        
    @property
    def colorbar_limits(self) -> Optional[Tuple[float, float]]:
        """Colorbar limits for this axis."""
        return self.__dict__['colorbar_limits']
        
    @colorbar_limits.setter
    def colorbar_limits(self, value: Optional[Tuple[float, float]]):
        self.__dict__['colorbar_limits'] = value
    
    # Horizontal line properties
    @property
    def draw_horizontal_line(self) -> bool:
        """Whether to draw a horizontal line on this axis."""
        return self.__dict__['draw_horizontal_line']
        
    @draw_horizontal_line.setter
    def draw_horizontal_line(self, value: bool):
        self.__dict__['draw_horizontal_line'] = value
        
    @property
    def horizontal_line_value(self) -> float:
        """Y-value at which to draw the horizontal line."""
        return self.__dict__['horizontal_line_value']
        
    @horizontal_line_value.setter
    def horizontal_line_value(self, value: float):
        self.__dict__['horizontal_line_value'] = value
        
    @property
    def horizontal_line_width(self) -> float:
        """Width of the horizontal line."""
        return self.__dict__['horizontal_line_width']
        
    @horizontal_line_width.setter
    def horizontal_line_width(self, value: float):
        self.__dict__['horizontal_line_width'] = value
        
    @property
    def horizontal_line_color(self) -> str:
        """Color of the horizontal line."""
        return self.__dict__['horizontal_line_color']
        
    @horizontal_line_color.setter
    def horizontal_line_color(self, value: str):
        self.__dict__['horizontal_line_color'] = value
        
    @property
    def horizontal_line_style(self) -> str:
        """Style of the horizontal line."""
        return self.__dict__['horizontal_line_style']
        
    @horizontal_line_style.setter
    def horizontal_line_style(self, value: str):
        self.__dict__['horizontal_line_style'] = value
        
    @property
    def r(self) -> RightAxisOptions:
        """Right axis options."""
        return self.__dict__['r']
        
    @r.setter
    def r(self, value: RightAxisOptions):
        self.__dict__['r'] = value

class MultiplotOptions:
    """Configuration options for the multiplot function, including per-axis customization.
    y_label_alignment: 'left', 'center', or 'right' (default: 'right') controls y-axis label alignment.
    """
    
    # Add preset configurations
    PRESET_CONFIGS = {
        'VERTICAL_POSTER_MEDIUM': {
            'width_pixels': 5400,
            'height_pixels': 7200,
            'dpi': 300,
            'figsize': (18, 24),
            'margins': {
                'left': 0.11,
                'right': 0.97,
                'bottom': 0.05,
                'top': 0.95
            },
            'vertical_space': 0.1,
            'title_size': 20,
            'title_y_position': 0.975,
            'title_pad': 10.0,
            'axis_label_size': 20,
            'x_tick_label_size': 17,
            'y_tick_label_size': 17,
            'magnetic_field_line_width': 0.5,
            'line_widths': {
                'vertical': 2.0,
                'spine': 1.5,
                'tick': 1.5
            },
            'tick_length': 6,
            'label_padding': {
                'x': 8,
                'y': 8
            }
        },
        'VERTICAL_POSTER_LARGE': {
            'width_pixels': 7200,
            'height_pixels': 10800,
            'dpi': 300,
            'figsize': (24, 36),
            'margins': {
                'left': 0.11,
                'right': 0.97,
                'bottom': 0.05,
                'top': 0.95
            },
            'vertical_space': 0.1,
            'title_size': 30,
            'title_y_position': 0.975,
            'title_pad': 14.0,
            'axis_label_size': 30,
            'x_axis_label_size': 36,
            'y_axis_label_size': 30,
            'x_tick_label_size': 26,
            'y_tick_label_size': 26,
            'magnetic_field_line_width': 0.5,
            'line_widths': {
                'vertical': 2.0,
                'spine': 1.5,
                'tick': 1.5
            },
            'tick_length': 10,
            'label_padding': {
                'x': 16,
                'y': 16
            }
        },
        
        'HORIZONTAL_POSTER': {
            'width_pixels': 7200,
            'height_pixels': 5400,
            'dpi': 300,
            'figsize': (24, 18),
            'margins': {
                'left': 0.11,
                'right': 0.97,
                'bottom': 0.05,
                'top': 0.95
            },
            'vertical_space': 0.1,
            'title_size': 20,
            'title_y_position': 0.975,
            'title_pad': 10.0,
            'axis_label_size': 20,
            'x_tick_label_size': 17,
            'y_tick_label_size': 17,
            'magnetic_field_line_width': 0.5,
            'line_widths': {
                'vertical': 2.0,
                'spine': 1.5,
                'tick': 1.5
            },
            'tick_length': 6,
            'label_padding': {
                'x': 8,
                'y': 8
            }
        }
    }
    
    def __init__(self):
        # Initialize axes as an instance attribute
        self.axes = {}
        self._global_y_limit = None # ADDED: Store the desired global limit
        # No need to initialize axes here since it's a class attribute
        self.reset()
        
        self.tick_length = 10.0
        self.tick_width = 1.0

        # --- POSITIONAL X-AXIS PROPERTIES ---
        self.x_axis_r_sun = False
        self.x_axis_carrington_lon = False 
        self.x_axis_carrington_lat = False
        
        try:
            # Use try-except for __file__ which might not exist in all contexts
            _current_dir = pathlib.Path(__file__).parent.resolve()
            self.positional_data_path = str(_current_dir / "../support_data/trajectories/psp_positional_data.npz")
        except NameError:
            # Fallback if __file__ is not defined (e.g., interactive session)
            self.positional_data_path = "../support_data/trajectories/psp_positional_data.npz"
            print_manager.warning("__file__ not defined, using basic relative path for positional_data_path")
        
        # Tick density for x-axis when using positional data
        self.positional_tick_density = 1  # Default is normal density
        # --------------------------------

        self.size_of_tiny_date_in_the_corner = 13  # Default font size for tiny date in the corner

    def reset(self):
        """Reset all options to their default values."""
        # Clear existing axes
        self.axes.clear()
        self._global_y_limit = None # ADDED: Reset the global limit storage
        
        # General plotting options
        self.window = '00:12:00.000'
        self.position = 'around'
        self.width = 15  # Changed from 22 to 15 for notebook default
        self.height_per_panel = 1.8  # Changed from 2 to 1.8 for more compact multiplots (notebook default)
        self.hspace = 0.2  # Reduced from 0.35 to 0.2 for tighter vertical spacing between panels
        self.hspace_vertical_space_between_plots = 0.25  # Changed from 0.2 to 0.25 for notebook default
        self._user_set_hspace = False  # Track if user explicitly set hspace
        self.title_font_size = 16
        self.use_single_title = True
        self.single_title_text = None
        
        # Border line width option
        self.border_line_width = 1.0
        
        # Vertical line options
        self.draw_vertical_line = False
        self.vertical_line_width = 1.0
        self.vertical_line_color = 'red'
        self.vertical_line_style = ':'
        
        # Horizontal line options (global)
        self.draw_horizontal_line = False
        self.horizontal_line_value = 1.0
        self.horizontal_line_width = 1.0
        self.horizontal_line_color = 'black'
        self.horizontal_line_style = '-'
        
        self._use_relative_time = False  # Now use internal variable
        self.relative_time_step_units = 'hours'
        self.relative_time_step = 2
        self.use_single_x_axis = True
        self.use_custom_x_axis_label = False
        self.custom_x_axis_label = None
        self.y_label_uses_encounter = True
        self.y_label_includes_time = True
        self.y_axis_label_font_size = 16
        self.x_axis_label_font_size = 16
        self.y_label_pad = 12
        self.x_label_pad = 8
        self.x_tick_label_font_size = 14
        self.y_tick_label_font_size = 14
        self.second_variable_on_right_axis = False
        
        # HAM-specific options
        self.hamify = False
        self.ham_var = None  # Will hold the actual plot_manager object
        self.ham_opacity = 1.0  # New: Opacity for HAM data (default 1.0)
        
        # New color mode options
        self.color_mode = 'default'  # Options: 'default', 'rainbow', 'single'
        self.single_color = None     # Used when color_mode = 'single'
        
        # New save options
        self.save_output = False
        self.save_preset = None
        self.save_dpi = None  # Will be set by preset if used
        self.output_dimensions = None # Tuple (width_px, height_px) or None
        self.bbox_inches_save_crop_mode = 'tight'  # Options: 'tight', None
        
        # Layout margins - control space around plots
        self.margin_top = 0.98  # Default: minimal top margin for tight layout
        self.margin_bottom = 0.05  # Default: minimal bottom margin for tight layout
        self.margin_left = 0.10  # Symmetric left margin for labels
        self.margin_right = 0.90  # Symmetric right margin for labels/legends
        
        self.title_pad = 21.0  # Increased from 18.0 to 21.0 for more space between titles and plots
        self.title_y_position = 0.9  # Changed from 0.97 to 0.9 for notebook default
        self.x_label_pad = 8  # Reduced from 12 to bring labels closer to the plot
        self.magnetic_field_line_width = 1.0
        self.tick_length = 10.0
        self.tick_width = 1.0

        # User-facing options for controlling boldness of plot text
        # House style: bold title for clarity, regular axis labels for tradition
        self.bold_title = True   # If True, plot titles are bold (default: True)
        self.bold_x_axis_label = False # If True, x-axis labels are bold (default: False)
        self.bold_y_axis_label = True  # Changed from False to True for notebook default

        # User-facing option: control whether to use matplotlib's constrained_layout
        self.constrained_layout = True  # If True, use constrained_layout for multiplot spacing

        # Reset positional x-axis properties
        self.__dict__['_x_axis_r_sun'] = False
        self.__dict__['_x_axis_carrington_lon'] = False
        self.__dict__['_x_axis_carrington_lat'] = False
        self.__dict__['_x_axis_positional_range'] = None
        self.__dict__['_positional_tick_density'] = 1

        # User-facing option: bypass all Plotbot presets and use matplotlib's default plot settings (constrained_layout, etc.)
        self.use_default_plot_settings = False  # If True, disables all Plotbot layout/preset logic

        self.y_label_alignment = 'center'  # 'left', 'center', or 'right' alignment for y-axis labels

    def _get_axis_options(self, axis_number: int) -> AxisOptions:
        """Helper method to get or create axis options"""
        print_manager.debug(f"Accessing axis ax{axis_number}")
        if axis_number not in self.axes:
            print_manager.debug(f"Creating new axis options for ax{axis_number}")
            new_opts = AxisOptions()
            # Apply stored global limit if it exists
            if self._global_y_limit is not None:
                print_manager.debug(f"Applying stored global y_limit {self._global_y_limit} to new ax{axis_number}")
                new_opts.y_limit = self._global_y_limit # Apply the stored global limit
            self.axes[axis_number] = new_opts
        else:
            print_manager.debug(f"Using existing axis options for ax{axis_number}")
        return self.axes[axis_number]
    
    # Define explicit property getters for axes 1-25
    @property
    def ax1(self) -> AxisOptions:
        return self._get_axis_options(1)
        
    @property
    def ax2(self) -> AxisOptions:
        return self._get_axis_options(2)
        
    @property
    def ax3(self) -> AxisOptions:
        return self._get_axis_options(3)
        
    @property
    def ax4(self) -> AxisOptions:
        return self._get_axis_options(4)
        
    @property
    def ax5(self) -> AxisOptions:
        return self._get_axis_options(5)
        
    @property
    def ax6(self) -> AxisOptions:
        return self._get_axis_options(6)
        
    @property
    def ax7(self) -> AxisOptions:
        return self._get_axis_options(7)
        
    @property
    def ax8(self) -> AxisOptions:
        return self._get_axis_options(8)
        
    @property
    def ax9(self) -> AxisOptions:
        return self._get_axis_options(9)
        
    @property
    def ax10(self) -> AxisOptions:
        return self._get_axis_options(10)
        
    @property
    def ax11(self) -> AxisOptions:
        return self._get_axis_options(11)
        
    @property
    def ax12(self) -> AxisOptions:
        return self._get_axis_options(12)
        
    @property
    def ax13(self) -> AxisOptions:
        return self._get_axis_options(13)
        
    @property
    def ax14(self) -> AxisOptions:
        return self._get_axis_options(14)
        
    @property
    def ax15(self) -> AxisOptions:
        return self._get_axis_options(15)
        
    @property
    def ax16(self) -> AxisOptions:
        return self._get_axis_options(16)
        
    @property
    def ax17(self) -> AxisOptions:
        return self._get_axis_options(17)
        
    @property
    def ax18(self) -> AxisOptions:
        return self._get_axis_options(18)
        
    @property
    def ax19(self) -> AxisOptions:
        return self._get_axis_options(19)
        
    @property
    def ax20(self) -> AxisOptions:
        return self._get_axis_options(20)
        
    @property
    def ax21(self) -> AxisOptions:
        return self._get_axis_options(21)
        
    @property
    def ax22(self) -> AxisOptions:
        return self._get_axis_options(22)
        
    @property
    def ax23(self) -> AxisOptions:
        return self._get_axis_options(23)
        
    @property
    def ax24(self) -> AxisOptions:
        return self._get_axis_options(24)
        
    @property
    def ax25(self) -> AxisOptions:
        return self._get_axis_options(25)
                
    def __getattr__(self, name: str) -> AxisOptions:
        """Dynamically handle axis attributes beyond ax25."""
        if name.startswith('ax'):
            try:
                axis_number = int(name[2:])
                return self._get_axis_options(axis_number)
            except ValueError:
                pass
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def print_state(self):
        """Print current state of options"""
        print("\nMultiplotOptions current state:")
        for key, value in self.__dict__.items():
            if key != 'axes':
                print(f"{key}: {value}")
        print(f"hspace_vertical_space_between_plots: {self.hspace_vertical_space_between_plots}")
        print("\nAxis-specific options (Instance):")
        for axis_num, axis_opts in self.axes.items():
            print(f"ax{axis_num}:")
            print(f"  y_limit: {axis_opts.y_limit}")
            print(f"  color: {axis_opts.color}")
            print(f"  draw_horizontal_line: {axis_opts.draw_horizontal_line}")
            if axis_opts.draw_horizontal_line:
                print(f"  horizontal_line_value: {axis_opts.horizontal_line_value}")
                print(f"  horizontal_line_width: {axis_opts.horizontal_line_width}")
                print(f"  horizontal_line_color: {axis_opts.horizontal_line_color}")
                print(f"  horizontal_line_style: {axis_opts.horizontal_line_style}")
            print(f"  right y_limit: {axis_opts.r.y_limit}")
            print(f"  right color: {axis_opts.r.color}")

    # New methods for applying presets
    def _apply_preset_config(self):
        """Apply the current preset configuration if one is set."""
        if not self.save_preset or self.save_preset not in self.PRESET_CONFIGS:
            return

        config = self.PRESET_CONFIGS[self.save_preset]
        
        # Store original panel-based values
        self._orig_width = self.width
        self._orig_height_per_panel = self.height_per_panel
        
        # Apply preset values
        self.width = config['figsize'][0]
        self.height_per_panel = config['figsize'][1]  # Will be adjusted per panel in multiplot
        self.save_dpi = config['dpi']
        self.hspace = config['vertical_space']
        self.title_font_size = config['title_size']
        self.title_y_position = config.get('title_y_position', self.title_y_position)
        self.title_pad = config.get('title_pad', self.title_pad)
        
        # Apply axis label sizes (prioritize specific, fallback to general)
        base_axis_size = config.get('axis_label_size', None) # Get the general one if it exists
        self.x_axis_label_font_size = config.get('x_axis_label_size', base_axis_size if base_axis_size is not None else self.x_axis_label_font_size)
        self.y_axis_label_font_size = config.get('y_axis_label_size', base_axis_size if base_axis_size is not None else self.y_axis_label_font_size)
        
        self.x_tick_label_font_size = config['x_tick_label_size']
        self.y_tick_label_font_size = config['y_tick_label_size']
        self.border_line_width = config['line_widths']['spine']
        self.vertical_line_width = config['line_widths']['vertical']
        self.magnetic_field_line_width = config.get('magnetic_field_line_width', self.magnetic_field_line_width)
        self.tick_length = config.get('tick_length', self.tick_length)
        # Get tick_width from line_widths sub-dictionary
        if 'line_widths' in config and isinstance(config['line_widths'], dict):
            self.tick_width = config['line_widths'].get('tick', self.tick_width)

        # Apply padding from presets if they exist (using renamed key)
        if 'label_padding' in config:
            self.x_label_pad = config['label_padding'].get('x', self.x_label_pad)
            self.y_label_pad = config['label_padding'].get('y', self.y_label_pad)
        # Fallback for old presets that might still use 'tick_pad' (optional, but safe)
        elif 'tick_pad' in config:
             print_manager.warning("Preset uses deprecated 'tick_pad'. Use 'label_padding' instead.")
             self.x_label_pad = config['tick_pad'].get('x', self.x_label_pad)
             self.y_label_pad = config['tick_pad'].get('y', self.y_label_pad)

    def set_global_y_limit(self, limits: Optional[Tuple[float, float]]):
        """Set the same y_limit for all currently defined axes.

        Args:
            limits: A tuple (min, max) for the y-axis, or None to clear.
        """
        if limits is not None and (not isinstance(limits, (tuple, list)) or len(limits) != 2):
            print_manager.warning(f"Invalid y_limit format: {limits}. Expected (min, max) tuple or None.")
            return

        print_manager.status(f"Storing global y_limit: {limits}. Will be applied when axes are created.")
        self._global_y_limit = limits # Just store the limit

    def _restore_original_values(self):
        """Restore original values after using a preset."""
        if hasattr(self, '_orig_width'):
            self.width = self._orig_width
            self.height_per_panel = self._orig_height_per_panel
            delattr(self, '_orig_width')
            delattr(self, '_orig_height_per_panel')
            
    # --- POSITIONAL X-AXIS PROPERTIES ---
    @property
    def x_axis_r_sun(self) -> bool:
        """Whether to use radial distance (R_sun) for the x-axis instead of time."""
        return self.__dict__.get('_x_axis_r_sun', False)
        
    @x_axis_r_sun.setter
    def x_axis_r_sun(self, value: bool):
        """Set the R_sun x-axis option, disabling others."""
        self.__dict__['_x_axis_r_sun'] = value
        if value:
            print_manager.debug("Positional Axis: R_sun enabled")
            self.__dict__['_x_axis_carrington_lon'] = False
            self.__dict__['_x_axis_carrington_lat'] = False
            self.__dict__['_use_relative_time'] = False
            # Ensure degrees from perihelion is also disabled
            if hasattr(self, '_use_degrees_from_perihelion'):
                 self.__dict__['_use_degrees_from_perihelion'] = False
            self.__dict__['_active_positional_data_type'] = 'r_sun'
            
    @property
    def x_axis_carrington_lon(self) -> bool:
        """Whether to use Carrington longitude (degrees) for the x-axis instead of time."""
        return self.__dict__.get('_x_axis_carrington_lon', False)

    @x_axis_carrington_lon.setter
    def x_axis_carrington_lon(self, value: bool):
        """Set the Carrington longitude x-axis option, disabling others."""
        self.__dict__['_x_axis_carrington_lon'] = value
        if value:
            print_manager.debug("Positional Axis: Carrington Lon enabled")
            self.__dict__['_x_axis_r_sun'] = False
            self.__dict__['_x_axis_carrington_lat'] = False
            self.__dict__['_use_relative_time'] = False
            # Ensure degrees from perihelion is also disabled
            if hasattr(self, '_use_degrees_from_perihelion'):
                 self.__dict__['_use_degrees_from_perihelion'] = False
            self.__dict__['_active_positional_data_type'] = 'carrington_lon'
            
    @property
    def x_axis_carrington_lat(self) -> bool:
        """Whether to use Carrington latitude (degrees) for the x-axis instead of time."""
        return self.__dict__.get('_x_axis_carrington_lat', False)
        
    @x_axis_carrington_lat.setter
    def x_axis_carrington_lat(self, value: bool):
        """Set the Carrington latitude x-axis option, disabling others."""
        self.__dict__['_x_axis_carrington_lat'] = value
        if value:
            print_manager.debug("Positional Axis: Carrington Lat enabled")
            self.__dict__['_x_axis_r_sun'] = False
            self.__dict__['_x_axis_carrington_lon'] = False
            self.__dict__['_use_relative_time'] = False
            # Ensure degrees from perihelion is also disabled
            if hasattr(self, '_use_degrees_from_perihelion'):
                 self.__dict__['_use_degrees_from_perihelion'] = False
            self.__dict__['_active_positional_data_type'] = 'carrington_lat'
            
    @property
    def using_positional_x_axis(self) -> bool:
        """Helper property to check if any positional data option is enabled."""
        return self.x_axis_r_sun or self.x_axis_carrington_lon or self.x_axis_carrington_lat
            
    @property
    def x_axis_positional_range(self) -> Optional[Tuple[float, float]]:
        """Get the fixed range for the positional x-axis (min, max).
        
        This range will be used for all plots when using a positional x-axis.
        For Carrington longitude/latitude, the values are in degrees.
        For radial distance, the values are in solar radii (R_sun).
        
        Returns:
            A tuple (min, max) if a range has been set, or None for auto-scaling.
        """
        return self.__dict__.get('_x_axis_positional_range', None)
        
    @x_axis_positional_range.setter
    def x_axis_positional_range(self, value: Optional[Tuple[float, float]]):
        """Set the fixed range for the positional x-axis.
        
        Args:
            value: A tuple (min, max) to set a fixed range, or None to use auto-scaling.
                  For Carrington longitude/latitude, the values should be in degrees.
                  For radial distance, the values should be in solar radii (R_sun).
        """
        if value is not None and not (isinstance(value, (tuple, list)) and len(value) == 2):
            print_manager.warning(f"Invalid x_axis_positional_range format: {value}. Expected (min, max) tuple or None.")
            return
            
        self.__dict__['_x_axis_positional_range'] = value
        
    @property
    def active_positional_data_type(self) -> str:
        """Return the active positional data type being used for the x-axis, if any."""
        if self.x_axis_r_sun:
            return 'r_sun'
        elif self.x_axis_carrington_lon:
            return 'carrington_lon'
        elif self.x_axis_carrington_lat:
            return 'carrington_lat'
        else:
            return None

    @property
    def positional_data_path(self) -> str:
        """Path to the NPZ file containing Parker Solar Probe positional data."""
        _default_path = "../support_data/trajectories/psp_positional_data.npz" # Basic default
        try:
            _current_dir = pathlib.Path(__file__).parent.resolve()
            _default_path = str(_current_dir / "../support_data/trajectories/psp_positional_data.npz")
        except NameError:
            pass
        return self.__dict__.get('_positional_data_path', _default_path)

    @positional_data_path.setter
    def positional_data_path(self, value: str):
        """Set the path to the NPZ file containing positional data."""
        self.__dict__['_positional_data_path'] = value
        
    @property
    def positional_tick_density(self) -> int:
        """Density multiplier for positional axis ticks. 1 = normal, 2 = twice as many, etc."""
        return self.__dict__.get('_positional_tick_density', 1)  # Default is normal density
        
    @positional_tick_density.setter
    def positional_tick_density(self, value: int):
        """Set the density multiplier for positional axis ticks."""
        if not isinstance(value, int) or value < 1:
            print_manager.warning(f"Invalid positional_tick_density value: {value}. Must be a positive integer.")
            return
        self.__dict__['_positional_tick_density'] = value
    # --- END POSITIONAL X-AXIS PROPERTIES ---

    # --- NEW PROPERTIES for Degrees from Perihelion --- 
    @property
    def use_degrees_from_perihelion(self) -> bool:
        """Whether to use degrees relative to perihelion longitude for the x-axis."""
        return self.__dict__.get('use_degrees_from_perihelion', False)

    @use_degrees_from_perihelion.setter
    def use_degrees_from_perihelion(self, value: bool):
        """Set whether to use degrees from perihelion for the x-axis."""
        # Only proceed if the value is actually changing to avoid redundant operations
        if value != self.__dict__.get('use_degrees_from_perihelion', False):
            self.__dict__['use_degrees_from_perihelion'] = value # Set the primary option first
            if value:
                print_manager.status("Enabling degrees from perihelion axis.")
                # Disable other specific positional x-axis modes
                self.__dict__['_x_axis_r_sun'] = False
                self.__dict__['_x_axis_carrington_lon'] = False
                self.__dict__['_x_axis_carrington_lat'] = False
                
                # IMPORTANT: DO NOT automatically disable _use_relative_time here.
                # Let the user control if they want relative time in conjunction with degrees.
                # The multiplot function's main logic will handle how these combine.
                
                # If enabling degrees, print a message if relative time is also active.
                if self.__dict__.get('_use_relative_time', False):
                    print_manager.status("Note: 'use_relative_time' is also active with 'degrees_from_perihelion'.")
                
            # else: # Optional: handle disabling use_degrees_from_perihelion
            #     print_manager.status("Disabling degrees from perihelion axis.")

    @property
    def degrees_from_perihelion_range(self) -> Optional[Tuple[float, float]]:
        """Fixed range for the 'degrees from perihelion' x-axis (min_deg, max_deg). None for auto."""
        return self.__dict__.get('degrees_from_perihelion_range', None)

    @degrees_from_perihelion_range.setter
    def degrees_from_perihelion_range(self, value: Optional[Tuple[float, float]]):
        """Set the fixed range for the 'degrees from perihelion' x-axis."""
        if value is not None and not (isinstance(value, (tuple, list)) and len(value) == 2):
            print_manager.warning(f"Invalid degrees_from_perihelion_range format: {value}. Expected (min, max) tuple or None.")
            return
        self.__dict__['degrees_from_perihelion_range'] = value

    @property
    def degrees_from_perihelion_tick_step(self) -> Optional[float]:
        """Step size between major ticks for 'degrees from perihelion' x-axis. None for auto."""
        return self.__dict__.get('degrees_from_perihelion_tick_step', None)

    @degrees_from_perihelion_tick_step.setter
    def degrees_from_perihelion_tick_step(self, value: Optional[float]):
        """Set the step size for major ticks for 'degrees from perihelion' x-axis."""
        if value is not None and not isinstance(value, (int, float)):
            print_manager.warning(f"Invalid degrees_from_perihelion_tick_step format: {value}. Expected number or None.")
            return
        self.__dict__['degrees_from_perihelion_tick_step'] = value
    # --- END NEW PROPERTIES --- 

    # --- HAM DATA PROPERTIES ---
    @property
    def hamify(self) -> bool:
        """Whether to display HAM data on right axis when available."""
        return self.__dict__.get('hamify', False)
        
    @hamify.setter
    def hamify(self, value: bool):
        """Set whether to display HAM data on right axis."""
        self.__dict__['hamify'] = value
        
    @property
    def ham_var(self):
        """HAM variable to display on right axis (actual plot_manager object)."""
        return self.__dict__.get('ham_var', None)
        
    @ham_var.setter
    def ham_var(self, value):
        """Set the HAM variable to display on right axis."""
        self.__dict__['ham_var'] = value

    @property
    def ham_opacity(self) -> float:
        """Opacity for HAM data plotted on the right axis (0.0=transparent, 1.0=opaque)."""
        return self.__dict__.get('ham_opacity', 1.0)

    @ham_opacity.setter
    def ham_opacity(self, value: float):
        self.__dict__['ham_opacity'] = value
    # --- END HAM DATA PROPERTIES ---

    # Keep these for backward compatibility (but they're deprecated now)
    @property
    def use_longitude_x_axis(self) -> bool:
        """Whether to use Carrington Longitude for the x-axis instead of time.
        DEPRECATED: Use use_positional_x_axis with x_axis_positional_data='carrington_lon' instead."""
        print_manager.debug("Warning: use_longitude_x_axis is deprecated. Use use_positional_x_axis with x_axis_positional_data='carrington_lon' instead.")
        return self.use_positional_x_axis and self.x_axis_positional_data == 'carrington_lon'

    @use_longitude_x_axis.setter
    def use_longitude_x_axis(self, value: bool):
        """DEPRECATED: Use use_positional_x_axis with x_axis_positional_data='carrington_lon' instead."""
        print_manager.debug("Warning: use_longitude_x_axis is deprecated. Use use_positional_x_axis with x_axis_positional_data='carrington_lon' instead.")
        self.use_positional_x_axis = value
        if value:
            self.x_axis_positional_data = 'carrington_lon'

    @property
    def longitude_data_path(self) -> str:
        """Path to the NPZ file containing longitude data.
        DEPRECATED: Use positional_data_path instead."""
        print_manager.debug("Warning: longitude_data_path is deprecated. Use positional_data_path instead.")
        return self.positional_data_path

    @longitude_data_path.setter
    def longitude_data_path(self, value: str):
        """DEPRECATED: Use positional_data_path instead."""
        print_manager.debug("Warning: longitude_data_path is deprecated. Use positional_data_path instead.")
        self.positional_data_path = value
        
    @property
    def longitude_tick_density(self) -> int:
        """Density multiplier for longitude axis ticks.
        DEPRECATED: Use positional_tick_density instead."""
        print_manager.debug("Warning: longitude_tick_density is deprecated. Use positional_tick_density instead.")
        return self.positional_tick_density
        
    @longitude_tick_density.setter
    def longitude_tick_density(self, value: int):
        """DEPRECATED: Use positional_tick_density instead."""
        print_manager.debug("Warning: longitude_tick_density is deprecated. Use positional_tick_density instead.")
        self.positional_tick_density = value

    # Add use_relative_time property with special behavior
    @property
    def use_relative_time(self) -> bool:
        """Whether to show relative time on the x-axis."""
        # If positional mapping is enabled, relative time is always disabled
        if self.__dict__.get('use_positional_x_axis', False):
            return False
        return self.__dict__.get('_use_relative_time', False)

    @use_relative_time.setter
    def use_relative_time(self, value: bool):
        """Set whether to use relative time on the x-axis."""
        # Store in a private variable so we can manage conflicts
        self.__dict__['_use_relative_time'] = value
        
        # If enabling relative time, disable conflicting positional mapping
        if value and self.__dict__.get('use_positional_x_axis', False):
            print_manager.status("Disabling positional mapping since relative time is now enabled")
            self.__dict__['use_positional_x_axis'] = False

    # New property getter/setter for hspace
    @property
    def hspace(self) -> float:
        """Get the vertical spacing between subplots."""
        return self.__dict__['hspace']
    
    @hspace.setter
    def hspace(self, value: float):
        """
        Set the vertical spacing between subplots.
        When called directly by user code, marks hspace as explicitly set.
        """
        self.__dict__['hspace'] = value
        
        # Only mark as user-set if this isn't being called during initialization/reset
        import inspect
        caller_name = inspect.currentframe().f_back.f_code.co_name
        if caller_name != 'reset' and caller_name != '__init__':
            self.__dict__['_user_set_hspace'] = True
            from .print_manager import print_manager
            # print_manager.debug(f"User explicitly set hspace to {value}")

    @property
    def hspace_vertical_space_between_plots(self) -> float:
        """
        User-facing property for vertical space between plot panels (in figure-relative units).
        This is an alias for hspace, but is the preferred way to set vertical spacing.
        """
        return self.hspace

    @hspace_vertical_space_between_plots.setter
    def hspace_vertical_space_between_plots(self, value: float):
        self.hspace = value
        # If both are set to different values, print a warning
        if hasattr(self, 'hspace') and self.hspace != value:
            from .print_manager import print_manager
            print_manager.warning("hspace and hspace_vertical_space_between_plots are set to different values! Using hspace_vertical_space_between_plots.")
        self.hspace = value

    # Deprecated alias for backward compatibility
    @property
    def h_space_vertical_between_plots(self) -> float:
        from .print_manager import print_manager
        print_manager.warning("h_space_vertical_between_plots is deprecated. Use hspace_vertical_space_between_plots instead.")
        return self.hspace_vertical_space_between_plots

    @h_space_vertical_between_plots.setter
    def h_space_vertical_between_plots(self, value: float):
        from .print_manager import print_manager
        print_manager.warning("h_space_vertical_between_plots is deprecated. Use hspace_vertical_space_between_plots instead.")
        self.hspace_vertical_space_between_plots = value

    @property
    def y_label_alignment(self) -> str:
        return self.__dict__.get('y_label_alignment', 'right')

    @y_label_alignment.setter
    def y_label_alignment(self, value: str):
        value = value.lower()
        if value not in ['left', 'center', 'right']:
            raise ValueError("y_label_alignment must be 'left', 'center', or 'right'")
        self.__dict__['y_label_alignment'] = value

    @property
    def y_axis_label_font_size(self) -> int:
        return self.__dict__.get('y_axis_label_font_size', 16)

    @y_axis_label_font_size.setter
    def y_axis_label_font_size(self, value: int):
        self.__dict__['y_axis_label_font_size'] = value

    @property
    def x_axis_label_font_size(self) -> int:
        return self.__dict__.get('x_axis_label_font_size', 16)

    @x_axis_label_font_size.setter
    def x_axis_label_font_size(self, value: int):
        self.__dict__['x_axis_label_font_size'] = value

    @property
    def x_tick_label_font_size(self) -> int:
        return self.__dict__.get('x_tick_label_font_size', 14)

    @x_tick_label_font_size.setter
    def x_tick_label_font_size(self, value: int):
        self.__dict__['x_tick_label_font_size'] = value

    @property
    def y_tick_label_font_size(self) -> int:
        return self.__dict__.get('y_tick_label_font_size', 14)

    @y_tick_label_font_size.setter
    def y_tick_label_font_size(self, value: int):
        self.__dict__['y_tick_label_font_size'] = value

    @property
    def bbox_inches_save_crop_mode(self) -> str:
        """
        Controls how much whitespace is cropped when saving the figure. 'tight' removes extra whitespace, None preserves it.
        """
        return self.__dict__.get('bbox_inches_save_crop_mode', 'tight')

    @bbox_inches_save_crop_mode.setter
    def bbox_inches_save_crop_mode(self, value: str):
        self.__dict__['bbox_inches_save_crop_mode'] = value

    # Deprecated alias for backward compatibility
    @property
    def save_bbox_inches(self) -> str:
        from .print_manager import print_manager
        print_manager.warning("save_bbox_inches is deprecated. Use bbox_inches_save_crop_mode instead.")
        return self.bbox_inches_save_crop_mode

    @save_bbox_inches.setter
    def save_bbox_inches(self, value: str):
        from .print_manager import print_manager
        print_manager.warning("save_bbox_inches is deprecated. Use bbox_inches_save_crop_mode instead.")
        self.bbox_inches_save_crop_mode = value

    @property
    def title_font_size(self) -> int:
        return self.__dict__.get('title_font_size', 16)

    @title_font_size.setter
    def title_font_size(self, value: int):
        self.__dict__['title_font_size'] = value

    # Alias for title_font_size
    @property
    def title_fontsize(self) -> int:
        return self.title_font_size

    @title_fontsize.setter
    def title_fontsize(self, value: int):
        self.title_font_size = value

# Create a custom plt object that extends matplotlib.pyplot
class EnhancedPlotting:
    """Enhanced matplotlib.pyplot with custom options support"""
    
    def __init__(self):
        # Copy all attributes from matplotlib.pyplot
        for attr in dir(mpl_plt):
            if not attr.startswith('_') and attr != 'options':  # Skip existing options if any
                setattr(self, attr, getattr(mpl_plt, attr))
        
        # Add the options attribute
        self.options = MultiplotOptions()

# Create the global instance
plt = EnhancedPlotting()