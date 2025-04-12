import matplotlib.pyplot as mpl_plt
from .print_manager import print_manager
from typing import Optional, Tuple, Any, Union

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
    """Configuration options for the multiplot function, including per-axis customization."""
    
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
            'x_tick_label_size': 16,
            'y_tick_label_size': 16,
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
            'x_tick_label_size': 25,
            'y_tick_label_size': 25,
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
            'x_tick_label_size': 16,
            'y_tick_label_size': 16,
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
    
    # Make axes a class-level attribute
    axes = {}

    def __init__(self):
        # No need to initialize axes here since it's a class attribute
        self.reset()
        
        # Pre-initialize axis options for axes 1-25
        for i in range(1, 26):
            if i not in MultiplotOptions.axes:
                MultiplotOptions.axes[i] = AxisOptions()

        self.tick_length = 6.0
        self.tick_width = 1.0

    def reset(self):
        """Reset all options to their default values."""
        # Clear existing axes
        MultiplotOptions.axes.clear()
        
        # General plotting options
        self.window = '00:12:00.000'
        self.position = 'around'
        self.width = 22
        self.height_per_panel = 3
        self.hspace = 0.5
        self.title_fontsize = 12
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
        
        self.use_relative_time = False
        self.relative_time_step_units = 'hours'
        self.relative_time_step = 2
        self.use_single_x_axis = True
        self.use_custom_x_axis_label = False
        self.custom_x_axis_label = None
        self.y_label_uses_encounter = True
        self.y_label_includes_time = True
        self.y_label_size = 11
        self.x_label_size = 11
        self.y_label_pad = 20
        self.x_label_pad = 20
        self.x_tick_label_size = 10
        self.y_tick_label_size = 10
        self.second_variable_on_right_axis = False
        
        # New color mode options
        self.color_mode = 'default'  # Options: 'default', 'rainbow', 'single'
        self.single_color = None     # Used when color_mode = 'single'
        
        # New save options
        self.save_output = False
        self.save_preset = None
        self.save_dpi = None  # Will be set by preset if used
        self.output_dimensions = None # Tuple (width_px, height_px) or None
        
        # Pre-initialize axis options for axes 1-25
        for i in range(1, 26):
            if i not in MultiplotOptions.axes:
                MultiplotOptions.axes[i] = AxisOptions()
        
        self.title_pad = 6.0 # Add title_pad default
        self.title_y_position = 0.98
        self.magnetic_field_line_width = 1.0
        self.tick_length = 6.0
        self.tick_width = 1.0
    
    def _get_axis_options(self, axis_number: int) -> AxisOptions:
        """Helper method to get or create axis options"""
        print_manager.debug(f"Accessing axis ax{axis_number}")
        if axis_number not in MultiplotOptions.axes:
            print_manager.debug(f"Creating new axis options for ax{axis_number}")
            MultiplotOptions.axes[axis_number] = AxisOptions()
        else:
            print_manager.debug(f"Using existing axis options for ax{axis_number}")
        return MultiplotOptions.axes[axis_number]
    
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
        print("\nAxis-specific options:")
        for axis_num, axis_opts in MultiplotOptions.axes.items():
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
        self.title_fontsize = config['title_size']
        self.title_y_position = config.get('title_y_position', self.title_y_position)
        self.title_pad = config.get('title_pad', self.title_pad)
        
        # Apply axis label sizes (prioritize specific, fallback to general)
        base_axis_size = config.get('axis_label_size', None) # Get the general one if it exists
        self.x_label_size = config.get('x_axis_label_size', base_axis_size if base_axis_size is not None else self.x_label_size)
        self.y_label_size = config.get('y_axis_label_size', base_axis_size if base_axis_size is not None else self.y_label_size)
        
        self.x_tick_label_size = config['x_tick_label_size']
        self.y_tick_label_size = config['y_tick_label_size']
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

    def _restore_original_values(self):
        """Restore original values after using a preset."""
        if hasattr(self, '_orig_width'):
            self.width = self._orig_width
            self.height_per_panel = self._orig_height_per_panel
            delattr(self, '_orig_width')
            delattr(self, '_orig_height_per_panel')
            

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