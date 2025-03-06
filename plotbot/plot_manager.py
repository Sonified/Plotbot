# 🎉 Extend numpy.ndarray with plotting functionality and friendly error handling 🎉
#SAFE! 

import numpy as np
from .ploptions import ploptions
from .print_manager import print_manager
from .data_cubby import data_cubby

class plot_manager(np.ndarray):
    
    PLOT_ATTRIBUTES = [
        'data', 'data_type', 'var_name', 'class_name', 'subclass_name', 'plot_type', 'datetime_array', 
        'y_label', 'legend_label', 'color', 'y_scale', 'y_limit', 'line_width',
        'line_style', 'colormap', 'colorbar_scale', 'colorbar_limits',
        'additional_data', 'colorbar_label'
    ]

    def __new__(cls, input_array, plot_options=None):
        obj = np.asarray(input_array).view(cls)
        # Add this new section for plot state
        if hasattr(input_array, '_plot_state'):
            obj._plot_state = dict(input_array._plot_state)
        else:
            obj._plot_state = {}
        # Keep existing code
        if hasattr(input_array, '_original_options'):
            obj._original_options = input_array._original_options
        else:
            obj._original_options = ploptions(**vars(plot_options))
        obj.plot_options = plot_options
        return obj

    def __array__(self, dtype=None):
        # Create a new plot_manager instead of just returning the array
        arr = np.asarray(self.view(np.ndarray), dtype=dtype)
        return plot_manager(arr, self.plot_options)

    def __array_wrap__(self, out_arr, context=None):
        if context is not None:
            # For ufuncs (like addition, subtraction, etc.), return a new plot_manager with the same options
            ufunc = context
            args = context
            # Check if any of the arguments are plot_manager instances
            has_plot_manager = any(isinstance(arg, plot_manager) for arg in args)
            if has_plot_manager:
                # If so, preserve the plot_options from the first plot_manager argument
                plot_options = next((arg.plot_options for arg in args if isinstance(arg, plot_manager)), None)
                return plot_manager(out_arr, plot_options=plot_options)
        # For other operations, return a regular numpy array
        return np.ndarray.__array_wrap__(self, out_arr, context)
    
    def __array_finalize__(self, obj):
        if obj is None:
            return
        print_manager.debug("\n=== Array Finalize Status ===")
        print_manager.debug(f"Finalizing array, obj type: {type(obj)}")
        
        # Add this line for plot state
        self._plot_state = getattr(obj, '_plot_state', {}).copy()
        print_manager.debug(f"Copied plot state: {self._plot_state}")
        
        # Keep existing lines
        if not hasattr(self, '_original_options'):
            self._original_options = getattr(obj, '_original_options', None)
        self.plot_options = getattr(obj, 'plot_options', None)
        print_manager.debug("=== End Array Finalize Status ===\n")

    @property
    def data(self):
        """Return the raw numpy array data"""
        return np.array(self)

    # Properties for data_type, class_name and subclass_name
    @property
    def data_type(self):
        return self.plot_options.data_type
        
    @data_type.setter
    def data_type(self, value):
        self._plot_state['data_type'] = value
        self.plot_options.data_type = value

    @property
    def class_name(self):
        return self.plot_options.class_name

    @class_name.setter 
    def class_name(self, value):
        self._plot_state['class_name'] = value
        self.plot_options.class_name = value

    @property
    def subclass_name(self):
        return self.plot_options.subclass_name

    @subclass_name.setter
    def subclass_name(self, value):
        self._plot_state['subclass_name'] = value
        self.plot_options.subclass_name = value

    @property
    def plot_type(self):
        return self.plot_options.plot_type

    @plot_type.setter
    def plot_type(self, value):
        self._plot_state['plot_type'] = value
        self.plot_options.plot_type = value
        
    @property
    def var_name(self):
        return self.plot_options.var_name

    @var_name.setter
    def var_name(self, value):
        self._plot_state['var_name'] = value
        self.plot_options.var_name = value

    @property
    def datetime_array(self):
        return self.plot_options.datetime_array

    @datetime_array.setter
    def datetime_array(self, value):
        self._plot_state['datetime_array'] = value
        self.plot_options.datetime_array = value
        
    @property
    def y_label(self):
        return self.plot_options.y_label

    @y_label.setter
    def y_label(self, value):
        self.plot_options.y_label = value
        
    @property
    def legend_label(self):
        return self.plot_options.legend_label

    @legend_label.setter
    def legend_label(self, value):
        self._plot_state['legend_label'] = value
        self.plot_options.legend_label = value

    @property
    def color(self):
        return self.plot_options.color

    @color.setter
    def color(self, value):
        self._plot_state['color'] = value
        self.plot_options.color = value
        
    @property
    def y_scale(self):
        return self.plot_options.y_scale

    @y_scale.setter
    def y_scale(self, value):
        self._plot_state['y_scale'] = value
        self.plot_options.y_scale = value
        
    @property
    def y_limit(self):
        return self.plot_options.y_limit

    @y_limit.setter
    def y_limit(self, value):
        self._plot_state['y_limit'] = value
        self.plot_options.y_limit = value
        
    @property
    def line_width(self):
        return self.plot_options.line_width

    @line_width.setter
    def line_width(self, value):
        self._plot_state['line_width'] = value
        self.plot_options.line_width = value
        
    @property
    def line_style(self):
        return self.plot_options.line_style

    @line_style.setter
    def line_style(self, value):
        self._plot_state['line_style'] = value
        self.plot_options.line_style = value
        
    @property
    def colormap(self):
        return self.plot_options.colormap

    @colormap.setter
    def colormap(self, value):
        self._plot_state['colormap'] = value
        self.plot_options.colormap = value
        
    @property
    def colorbar_scale(self):
        return self.plot_options.colorbar_scale

    @colorbar_scale.setter
    def colorbar_scale(self, value):
        self._plot_state['colorbar_scale'] = value
        self.plot_options.colorbar_scale = value
        
    @property
    def colorbar_limits(self):
        return self.plot_options.colorbar_limits

    @colorbar_limits.setter
    def colorbar_limits(self, value):
        self._plot_state['colorbar_limits'] = value
        self.plot_options.colorbar_limits = value
        
    @property
    def additional_data(self):
        return self.plot_options.additional_data

    @additional_data.setter
    def additional_data(self, value):
        self._plot_state['additional_data'] = value
        self.plot_options.additional_data = value
        
    @property
    def colorbar_label(self):
        return self.plot_options.colorbar_label

    @colorbar_label.setter
    def colorbar_label(self, value):
        self._plot_state['colorbar_label'] = value
        self.plot_options.colorbar_label = value

    #Inline friendly error handling in __setattr__, consistent with your style
    def __setattr__(self, name, value):
        try:
            if name in ['plot_options', '__dict__', '__doc__', '__module__', '_ipython_display_', '_original_options'] or name.startswith('_'):
                # Directly set these special or private attributes
                super().__setattr__(name, value)
                return
            
            if name in self.PLOT_ATTRIBUTES:
                if value == 'default':
                    print_manager.datacubby(f"DEFAULT RECEIVED_value={value}")
                    # First remove from plot state (like reset does)
                    if name in self._plot_state:
                        del self._plot_state[name]
                        print_manager.datacubby("action='remove_from_plot_state'")
                    # Then set to original value
                    if hasattr(self._original_options, name):
                        setattr(self.plot_options, name, getattr(self._original_options, name))
                        print_manager.datacubby(f"Attribute name: {name}, Attribute value: {getattr(self.plot_options, name)}")
                    else:
                        print(f"Warning: No default value found for {name}")
                    return
                if name == 'color':
                    try:
                        plt.matplotlib.colors.to_rgb(value)
                    except ValueError:
                        print(f"'{value}' is not a recognized color, friend!")
                        print("Try one of these:")
                        print(f"- Default: 'default' (sets to the original color: {self._original_options.color})")
                        print("- Reds: red, darkred, crimson, salmon, coral, tomato, firebrick, indianred")
                        print("- Oranges: orange, darkorange, peachpuff, sandybrown, coral") 
                        print("- Yellows: yellow, gold, khaki, moccasin, palegoldenrod")
                        print("- Greens: green, darkgreen, forestgreen, lime, seagreen, olive, springgreen, palegreen")
                        print("- Blues: blue, navy, royalblue, skyblue, cornflowerblue, steelblue, deepskyblue")
                        print("- Indigos: indigo, slateblue, mediumslateblue, darkslateblue")
                        print("- Violets: violet, purple, magenta, orchid, plum, mediumorchid")
                        print("- Neutrals: black, white, grey, silver, dimgray, lightgray")
                        print("- Or use any hex code like '#FF0000'")
                        return
                        
                elif name == 'y_scale':
                    if value not in ['linear', 'log']:
                        print(f"'{value}' is not a valid y-axis scale, friend!")
                        print("Try 'linear' or 'log'.")
                        return
                        
                elif name == 'line_style':
                    valid_styles = ['-', '--', '-.', ':', 'None', ' ', '']
                    if value not in valid_styles:
                        print('Manager setattr helper!')
                        print(f"'{value}' is not a valid line style, friend!")
                        print(f"Try one of these: {', '.join(valid_styles)}")
                        return
                        
                elif name == 'marker':
                    valid_markers = ['o', 's', '^', 'v', '<', '>', 'D', 'p', '*', 'h', '+', 'x', '.', ',', 'None', None]
                    if value not in valid_markers:
                        print_manager.debug('Manager setattr helper!')
                        print(f"'{value}' is not a valid marker, friend!")
                        print(f"Try one of these: {', '.join(str(m) for m in valid_markers if m)}")
                        return
                        
                elif name in ['line_width', 'marker_size', 'alpha']:
                    # Validate that value is numeric
                    try:
                        numeric_value = float(value)
                        if name == 'alpha' and not 0 <= numeric_value <= 1:
                            print_manager.debug('Manager setattr helper!')
                            print(f"Alpha must be between 0 and 1, friend! You tried: {value}")
                            return
                        if numeric_value < 0:
                            print_manager.debug('Manager setattr helper!')
                            print(f"{name} can't be negative, friend! You tried: {value}")
                            return
                    except ValueError:
                        print_manager.debug('Manager setattr helper!')
                        print(f"{name} must be a numeric value, friend! You tried: {value}")
                        return
                        
                elif name == 'y_limit':
                    # Validate y_limit if it is not None
                    if value is not None:
                        if not isinstance(value, (list, tuple)) or len(value) != 2:
                            print_manager.debug('Manager setattr helper!')
                            print(f"y_limit must be a tuple/list of two values, friend! You tried: {value}")
                            return
                        if not all(isinstance(v, (int, float)) for v in value):
                            print_manager.debug('Manager setattr helper!')
                            print(f"y_limit values must be numeric, friend! You tried: {value}")
                            return
                        if value[0] >= value[1]:
                            print_manager.debug('Manager setattr helper!')
                            print(f"y_limit min must be less than max, friend! You tried: {value}")
                            return

                # If validation passes or not needed, use property setter to maintain consistency
                super().__setattr__(name, value)
                return

            else:
                # For unrecognized attributes, provide a friendly error
                print_manager.debug('Manager message:')
                print(f"'{name}' is not a recognized attribute, friend!")
                print(f"Try one of these: {', '.join(self.PLOT_ATTRIBUTES)}")
                return

        except Exception as e:
            print(f"Error setting {name}: {str(e)}")

    # Attribute access handler for dynamic attributes
    def __getattr__(self, name):
        # Add this section at the start
        if hasattr(self, '_plot_state') and name in self._plot_state:
            return self._plot_state[name]
        # This is only called if an attribute is not found 
        # in the normal places (i.e., not found in __dict__ and not a dynamic attribute).
        # For recognized attributes, return from plot_options if available
        if name in self.PLOT_ATTRIBUTES:
            return getattr(self.plot_options, name, None)
        # For unrecognized attributes, provide a friendly error
        if not name.startswith('_'):
            print(f"'{name}' is not a recognized attribute, friend!")
            print(f"Try one of these: {', '.join(self.PLOT_ATTRIBUTES)}")

    def _set_plot_option(self, attribute, value):
        if not self.plot_options:
            self.plot_options = ploptions()
        setattr(self.plot_options, attribute, value)
        
print('initialized plot_manager')