import numpy as np

# 🎉 Define the generalized plotting options class 🎉
class plot_config:
    """A wrapper for storing plot-related config attributes"""
    # Class-level debug attribute
    debug = False
    
    @classmethod
    def reset(cls):
        """Reset all class-level attributes to their default values."""
        cls.debug = False
    
    def __init__(self, 
                 data_type=None, 
                 class_name=None, 
                 subclass_name=None, 
                 plot_type='time_series',
                 var_name=None,
                 time=None,
                 datetime_array=None,
                 y_label=None, 
                 legend_label=None, 
                 color=None, 
                 y_scale='linear',
                 y_limit=None,
                 line_width=1.0,
                 line_style='-',
                 marker_size=1.0,
                 colormap='viridis',
                 colorbar_scale='linear',
                 colorbar_limits=None,
                 additional_data=None,
                 colorbar_label=None,
                 requested_trange=None,
                 # Add common font size attributes explicitly
                 title_fontsize=12,
                 y_label_size=10,
                 x_label_size=10,
                 x_tick_label_size=8,
                 y_tick_label_size=8,
                 **kwargs):
        
        self.data_type = data_type 
        self.class_name = class_name
        self.subclass_name = subclass_name
        self.plot_type = plot_type
        self.var_name = var_name
        # Store time and datetime_array as private variables to avoid truth value comparisons
        self._time = time
        self._datetime_array = datetime_array
        self.y_label = y_label
        self.legend_label = legend_label
        self.color = color
        self.y_scale = y_scale
        self.y_limit = y_limit
        self.line_width = line_width
        self.line_style = line_style
        self.marker_size = marker_size
        self.colormap = colormap
        self.colorbar_scale = colorbar_scale
        self.colorbar_limits = colorbar_limits
        self.additional_data = additional_data
        self.colorbar_label = colorbar_label
        self.requested_trange = requested_trange
        # Set the explicit font sizes
        self.title_fontsize = title_fontsize
        self.y_label_size = y_label_size
        self.x_label_size = x_label_size
        self.x_tick_label_size = x_tick_label_size
        self.y_tick_label_size = y_tick_label_size
        
        # Add any *other* additional keyword arguments as attributes
        for key, value in kwargs.items():
            # Avoid overwriting explicitly defined attributes
            if not hasattr(self, key):
                setattr(self, key, value)
            
    # Add properties for time and datetime_array to safely handle them
    @property
    def time(self):
        return self._time
        
    @time.setter
    def time(self, value):
        # Safer setter implementation that avoids truth value comparisons
        self._time = value
    
    @property
    def datetime_array(self):
        return self._datetime_array
        
    @datetime_array.setter
    def datetime_array(self, value):
        # Safer setter implementation that avoids truth value comparisons
        self._datetime_array = value

print('initialized plot_config')

def retrieve_plot_config_snapshot(state_dict):
    """Helper function to create a readable snapshot of plot options state.
    
    Args:
        state_dict (dict): Dictionary containing plot state information
        
    Returns:
        dict: Formatted snapshot with truncated arrays/lists for readability
    """
    snapshot = {}
    for k, v in state_dict.items():  # Just iterates over the input dictionary
        if isinstance(v, (list, np.ndarray)):  # Checks types
            if isinstance(v, np.ndarray):
                snapshot[k] = str(v.flatten()[:10]) + "..."  # Truncates arrays
            else:
                snapshot[k] = str(v[:10]) + "..."  # Truncates lists
        else:
            snapshot[k] = v  # Passes through other types
    return snapshot