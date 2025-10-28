# Plotbot Options - Global configuration for figure behavior
"""
Global options class for controlling plotbot figure behavior.
Similar to audifier pattern - simple, direct property access.
Includes per-axis options for adding vertical/horizontal lines.
"""

class AxisOptions:
    """Per-axis options for adding lines and customization."""
    
    def __init__(self):
        self._vertical_lines = []
        self._horizontal_lines = []
    
    def add_vertical_line(self, time, color='black', style='--', width=1.0, label=None):
        """Add a vertical line at a specific time.
        
        Args:
            time: Time value (datetime string or datetime object)
            color: Line color (default: 'black')
            style: Line style (default: '--' for dashed)
            width: Line width (default: 1.0)
            label: Optional label for the line
        """
        self._vertical_lines.append({
            'time': time,
            'color': color,
            'style': style,
            'width': width,
            'label': label
        })
    
    def add_horizontal_line(self, value, color='black', style='--', width=1.0, label=None):
        """Add a horizontal line at a specific y-value.
        
        Args:
            value: Y-value for the horizontal line
            color: Line color (default: 'black')
            style: Line style (default: '--' for dashed)
            width: Line width (default: 1.0)
            label: Optional label for the line
        """
        self._horizontal_lines.append({
            'value': value,
            'color': color,
            'style': style,
            'width': width,
            'label': label
        })
    
    def clear_vertical_lines(self):
        """Clear all vertical lines for this axis."""
        self._vertical_lines = []
    
    def clear_horizontal_lines(self):
        """Clear all horizontal lines for this axis."""
        self._horizontal_lines = []
    
    def clear_all_lines(self):
        """Clear all lines (vertical and horizontal) for this axis."""
        self._vertical_lines = []
        self._horizontal_lines = []
    
    @property
    def vertical_lines(self):
        """Get list of vertical lines."""
        return self._vertical_lines
    
    @property
    def horizontal_lines(self):
        """Get list of horizontal lines."""
        return self._horizontal_lines

class PlotbotOptions:
    """Global options for controlling plotbot figure behavior."""
    
    def __init__(self):
        self.axes = {}  # Store per-axis options
        self.reset()
    
    def reset(self):
        """Reset all options to defaults."""
        self.return_figure = False     # Whether plotting functions return the figure object
        self.display_figure = True     # Whether to display the figure (plt.show())
        self.axes = {}                 # Clear all axis-specific options
    
    def _get_axis_options(self, axis_number):
        """Get or create axis options for a specific axis number."""
        if axis_number not in self.axes:
            self.axes[axis_number] = AxisOptions()
        return self.axes[axis_number]
    
    # Define explicit property getters for axes 1-25 (matching multiplot convention)
    @property
    def ax1(self):
        return self._get_axis_options(1)
    
    @property
    def ax2(self):
        return self._get_axis_options(2)
    
    @property
    def ax3(self):
        return self._get_axis_options(3)
    
    @property
    def ax4(self):
        return self._get_axis_options(4)
    
    @property
    def ax5(self):
        return self._get_axis_options(5)
    
    @property
    def ax6(self):
        return self._get_axis_options(6)
    
    @property
    def ax7(self):
        return self._get_axis_options(7)
    
    @property
    def ax8(self):
        return self._get_axis_options(8)
    
    @property
    def ax9(self):
        return self._get_axis_options(9)
    
    @property
    def ax10(self):
        return self._get_axis_options(10)
    
    @property
    def ax11(self):
        return self._get_axis_options(11)
    
    @property
    def ax12(self):
        return self._get_axis_options(12)
    
    @property
    def ax13(self):
        return self._get_axis_options(13)
    
    @property
    def ax14(self):
        return self._get_axis_options(14)
    
    @property
    def ax15(self):
        return self._get_axis_options(15)
    
    @property
    def ax16(self):
        return self._get_axis_options(16)
    
    @property
    def ax17(self):
        return self._get_axis_options(17)
    
    @property
    def ax18(self):
        return self._get_axis_options(18)
    
    @property
    def ax19(self):
        return self._get_axis_options(19)
    
    @property
    def ax20(self):
        return self._get_axis_options(20)
    
    @property
    def ax21(self):
        return self._get_axis_options(21)
    
    @property
    def ax22(self):
        return self._get_axis_options(22)
    
    @property
    def ax23(self):
        return self._get_axis_options(23)
    
    @property
    def ax24(self):
        return self._get_axis_options(24)
    
    @property
    def ax25(self):
        return self._get_axis_options(25)
        
    def __repr__(self):
        return (f"PlotbotOptions(return_figure={self.return_figure}, "
                f"display_figure={self.display_figure}, "
                f"axes={list(self.axes.keys())})")

# Create global instance
ploptions = PlotbotOptions()

print('🎛️ initialized ploptions')
