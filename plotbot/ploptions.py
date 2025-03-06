import numpy as np

# 🎉 Define the generalized plotting options class 🎉
class ploptions:
    def __init__(self, data_type=None, var_name=None, class_name=None, subclass_name=None, plot_type=None, 
                 datetime_array=None, y_label=None, legend_label=None, color=None, y_scale=None,
                 y_limit=None, line_width=1, line_style='-',
                 colormap=None, colorbar_scale='linear', colorbar_limits=None, additional_data=None,
                 colorbar_label=None, data=None):  # Add data parameter
        self.data_type = data_type            # Actual data product name (e.g., 'mag_rtn_4sa')
        self.var_name = var_name              # Variable name in data file (e.g., 'br_rtn_4sa')
        self.class_name = class_name          # Class handling this data type (e.g., 'mag_rtn_4sa')
        self.subclass_name = subclass_name    # Specific Subclass (e.g., 'br')
        self.plot_type = plot_type            # Type of plot (e.g., 'time_series')
        self.datetime_array = datetime_array   # Time data
        self.y_label = y_label                # Y-axis label
        self.legend_label = legend_label      # Legend text
        self.color = color                    # Plot color
        self.y_scale = y_scale                # Scale type
        self.y_limit = y_limit                # Y-axis limits
        self.line_width = line_width          # Line width
        self.line_style = line_style          # Line style
        self.colormap = colormap
        self.colorbar_scale = colorbar_scale
        self.colorbar_limits = colorbar_limits
        self.additional_data = additional_data
        self.colorbar_label = colorbar_label
        self.data = data                      # Add data attribute
        
print('initialized ploptions')

def retrieve_ploption_snapshot(state_dict):
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