"""
Utility for generating robust axis metadata for spectral/time-series data arrays.
"""

def generate_axis_metadata(data, axis_names, context_obj=None):
    """
    Dynamically generate axis metadata for a data array, using standard axis names and (optionally) a class instance for axis values.
    Args:
        data (np.ndarray): The data array (e.g., 2D or 3D)
        axis_names (list of str): Axis names in order (e.g., ['time', 'pitch_angle'])
        context_obj (object, optional): Class instance to pull axis values from (e.g., self)
    Returns:
        dict: Metadata with axis info and data shape
    """
    # Standard label/unit mapping
    axis_info_defaults = {
        'time':        {'label': 'Time',         'unit': 'datetime'},
        'pitch_angle': {'label': 'Pitch Angle',  'unit': 'degrees'},
        'energy':      {'label': 'Energy',       'unit': 'eV'},
        'theta':       {'label': 'Theta',        'unit': 'degrees'},
        'phi':         {'label': 'Phi',          'unit': 'degrees'},
    }
    # Standard attribute mapping for axis values
    axis_attr_map = {
        'time':        'datetime_array',
        'pitch_angle': 'pitch_angle',
        'energy':      'energy_vals',
        'theta':       'theta_vals',
        'phi':         'phi_vals',
    }
    axes = []
    for name in axis_names:
        info = axis_info_defaults.get(name, {'label': name, 'unit': None})
        values = None
        if context_obj is not None:
            attr = axis_attr_map.get(name)
            if attr and hasattr(context_obj, attr):
                values = getattr(context_obj, attr)
        axis_entry = {
            'name': name,
            'label': info['label'],
            'unit': info['unit'],
            'values': values.tolist() if hasattr(values, 'tolist') else values
        }
        axes.append(axis_entry)
    return {
        'axes': axes,
        'data_shape': data.shape
    } 