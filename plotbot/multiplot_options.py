import matplotlib.pyplot as plt
from .print_manager import print_manager

class MultiplotOptions:
    """Configuration options for the multiplot function, including per-axis customization."""
    
    # Make axes a class-level attribute
    axes = {}

    class RightAxisOptions:
        """Stores right-axis specific options."""
        def __init__(self):
            self.y_limit = None
            self.color = None

    class AxisOptions:
        """Stores per-axis options like y_limit and color."""
        def __init__(self):
            self.y_limit = None
            self.color = None
            self.r = MultiplotOptions.RightAxisOptions()  # Add right axis options

    def __init__(self):
        # No need to initialize axes here since it's a class attribute
        self.reset()

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
        self.draw_vertical_line = False
        self.vertical_line_width = 1.0
        self.vertical_line_color = 'red'
        self.vertical_line_style = ':'
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
        self.x_tick_label_size = 10
        self.y_tick_label_size = 10
        self.second_variable_on_right_axis = False
        
        # New color mode options
        self.color_mode = 'default'  # Options: 'default', 'rainbow', 'single'
        self.single_color = None     # Used when color_mode = 'single'
        
        # Clear any dynamically created axis attributes
        for attr in list(self.__dict__.keys()):
            if attr.startswith('ax'):
                delattr(self, attr)
                
    def __getattr__(self, name):
        """Dynamically create ax1, ax2, etc. as attributes when accessed."""
        if name.startswith('ax'):
            try:
                axis_number = int(name[2:])
                print_manager.debug(f"Accessing axis {name}")
                if axis_number not in MultiplotOptions.axes:
                    print_manager.debug(f"Creating new axis options for {name}")
                    MultiplotOptions.axes[axis_number] = self.AxisOptions()
                    setattr(self, name, MultiplotOptions.axes[axis_number])
                else:
                    print_manager.debug(f"Using existing axis options for {name}")
                return MultiplotOptions.axes[axis_number]
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
            print(f"  right y_limit: {axis_opts.r.y_limit}")
            print(f"  right color: {axis_opts.r.color}")

# Create global instance
plt.options = MultiplotOptions()