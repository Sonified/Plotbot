# 🎉 Extend numpy.ndarray with plotting functionality and friendly error handling 🎉
#SAFE! 

import numpy as np
import pandas as pd
import logging
import matplotlib.pyplot as plt
from .ploptions import ploptions
from .print_manager import print_manager
from .data_classes.custom_variables import custom_variable  # UPDATED PATH

class plot_manager(np.ndarray):
    
    PLOT_ATTRIBUTES = [
        'data', 'data_type', 'var_name', 'class_name', 'subclass_name', 'plot_type', 'datetime_array', 
        'y_label', 'legend_label', 'color', 'y_scale', 'y_limit', 'line_width',
        'line_style', 'colormap', 'colorbar_scale', 'colorbar_limits',
        'additional_data', 'colorbar_label', 'is_derived', 'source_var', 'operation',

        # Add missing attributes
        'marker', 'marker_size', 'alpha', 'marker_style' #, 'zorder', 'legend_label_override'
    ]

    # Set up class-level interpolation settings
    interp_method = 'nearest'  # Default interpolation method ('nearest' or 'linear')

    def __new__(cls, input_array, plot_options=None):
        obj = np.asarray(input_array).view(cls)
        # Add this new section for plot state
        if hasattr(input_array, '_plot_state'):
            obj._plot_state = dict(input_array._plot_state)
        else:
            obj._plot_state = {}
        
        from .print_manager import print_manager
        # Require plot_options to be provided
        if plot_options is None:
            raise ValueError("plot_options must be provided when creating a plot_manager instance")
        
        print_manager.zarr_integration(f"Using plot_options: data_type={getattr(plot_options, 'data_type', 'None')}, class={getattr(plot_options, 'class_name', 'None')}, subclass={getattr(plot_options, 'subclass_name', 'None')}")
        
        # Keep existing code with better error handling
        if hasattr(input_array, '_original_options'):
            obj._original_options = input_array._original_options
        else:
            # Safely create original options
            try:
                from .ploptions import ploptions
                if hasattr(plot_options, '__dict__'):
                    obj._original_options = ploptions(**vars(plot_options))
                else:
                    # Handle case where plot_options doesn't have __dict__
                    obj._original_options = ploptions() if not isinstance(plot_options, dict) else ploptions(**plot_options)
            except Exception as e:
                # Fallback to empty options
                from .print_manager import print_manager
                print_manager.warning(f"Error creating plot options: {str(e)}, using empty options")
                from .ploptions import ploptions
                obj._original_options = ploptions()
        
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
            has_plot_manager = any(isinstance(arg, self.__class__) for arg in args)
            if has_plot_manager:
                # If so, preserve the plot_options from the first plot_manager argument
                plot_options = next((arg.plot_options for arg in args if isinstance(arg, self.__class__)), None)
                return self.__class__(out_arr, plot_options=plot_options)
        # For other operations, return a regular numpy array
        return np.ndarray.__array_wrap__(self, out_arr, context)
    
    def __array_finalize__(self, obj):
        if obj is None:
            return
        # Always ensure _plot_state exists
        self._plot_state = getattr(obj, '_plot_state', None)
        if self._plot_state is None:
            self._plot_state = {}
        else:
            self._plot_state = dict(self._plot_state)
        # Always ensure plot_options exists
        self.plot_options = getattr(obj, 'plot_options', None)
        if self.plot_options is None:
            from .ploptions import ploptions
            self.plot_options = ploptions()
        if not hasattr(self, '_original_options'):
            self._original_options = getattr(obj, '_original_options', None)

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
        # FIX: For safety, directly use __setattr__ rather than going through _plot_state
        # which can trigger truth value evaluation of arrays
        try:
            # First update the plot_options directly
            if hasattr(self.plot_options, '_datetime_array'):
                self.plot_options._datetime_array = value
            else:
                object.__setattr__(self.plot_options, 'datetime_array', value)
                
            # Then update the _plot_state dictionary if needed
            if hasattr(self, '_plot_state'):
                self._plot_state['datetime_array'] = value
        except Exception as e:
            from .print_manager import print_manager
            print_manager.warning(f"Error setting datetime_array: {str(e)}")
        
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
        if hasattr(self, '_colorbar_label'):
            return self._colorbar_label
        return getattr(self.plot_options, 'colorbar_label', None)
        
    @colorbar_label.setter
    def colorbar_label(self, value):
        self._plot_state['colorbar_label'] = value
        self._colorbar_label = value
        setattr(self.plot_options, 'colorbar_label', value)

    # New properties for derived variable handling
    @property
    def source_class_names(self):
        if hasattr(self, '_source_class_names'):
            return self._source_class_names
        return getattr(self.plot_options, 'source_class_names', None)
        
    @source_class_names.setter
    def source_class_names(self, value):
        self._plot_state['source_class_names'] = value
        self._source_class_names = value
        setattr(self.plot_options, 'source_class_names', value)
        
    @property
    def source_subclass_names(self):
        if hasattr(self, '_source_subclass_names'):
            return self._source_subclass_names
        return getattr(self.plot_options, 'source_subclass_names', None)
        
    @source_subclass_names.setter
    def source_subclass_names(self, value):
        self._plot_state['source_subclass_names'] = value
        self._source_subclass_names = value
        setattr(self.plot_options, 'source_subclass_names', value)

    #Inline friendly error handling in __setattr__, consistent with your style
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return
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
                        print_manager.warning(f"No default value found for {name}")
                    return
                if name == 'color':
                    if value is None:
                        # None is a valid color (use default/auto)
                        pass
                    else:
                        try:
                            plt.matplotlib.colors.to_rgb(value)
                        except ValueError:
                            print_manager.warning(f"'{value}' is not a recognized color, friend!")
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
                        print_manager.warning(f"'{value}' is not a valid y-axis scale, friend!")
                        print("Try 'linear' or 'log'.")
                        return
                        
                elif name == 'line_style':
                    valid_styles = ['-', '--', '-.', ':', 'None', ' ', '']
                    if value not in valid_styles:
                        print_manager.warning('Manager setattr helper!')
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
                print(f"[Plot Manager] '{name}' is not a recognized attribute, friend!")
                print(f"[Plot Manager] Try one of these: {', '.join(self.PLOT_ATTRIBUTES)}")
                return

        except Exception as e:
            print_manager.warning(f"Error setting {name}: {str(e)}")

    # Attribute access handler for dynamic attributes
    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                # Important: Use object.__getattribute__ for these
                return object.__getattribute__(self, name)
            except AttributeError:
                # Let AttributeError propagate if internal/dunder doesn't exist
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # If _plot_state is missing, initialize it and warn (except if directly accessing _plot_state)
        if name == '_plot_state':
            if '_plot_state' not in self.__dict__:
                self._plot_state = {}
            return self._plot_state
        elif '_plot_state' not in self.__dict__:
            self._plot_state = {}
        # Fallback: If plot_options is missing, auto-initialize and warn
        if 'plot_options' not in self.__dict__ or self.plot_options is None:
            from .ploptions import ploptions
            self.plot_options = ploptions()
        if hasattr(self, '_plot_state') and name in self._plot_state:
            return self._plot_state[name]
        # This is only called if an attribute is not found 
        # in the normal places (i.e., not found in __dict__ and not a dynamic attribute).
        # For recognized attributes, return from plot_options if available
        if name in self.PLOT_ATTRIBUTES:
            return getattr(self.plot_options, name, None)
        # For unrecognized attributes (not found in _plot_state or as a PLOT_ATTRIBUTE)
        if not name.startswith('_'): # Ensure it's not an internal attribute we missed
            # Behavior for trying to GET an unrecognized attribute:
            # Warn and return None, but do not store it.
            print_manager.warning(f"Warning: '{name}' is not a recognized attribute for {self.__class__.__name__}. Returning None.")
            return None
        # If it's an underscore attribute not caught by the initial check in this method
        # (object.__getattribute__) and it's not a recognized plot state or option,
        # it implies a missing dunder/internal attribute or a misconfiguration.
        # Standard behavior is to raise AttributeError.
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _set_plot_option(self, attribute, value):
        if not self.plot_options:
            self.plot_options = ploptions()
        setattr(self.plot_options, attribute, value)
        
    @staticmethod
    def interpolate_to_times(source_times, source_values, target_times, method='nearest'):
        """
        Interpolate source values to align with target times.
        
        Parameters
        ----------
        source_times : array-like
            Original datetime array (can be Python datetime or numpy.datetime64)
        source_values : array-like
            Original values to interpolate
        target_times : array-like
            Target datetime array to interpolate to
        method : str
            Interpolation method ('nearest' or 'linear')
            
        Returns
        -------
        numpy.ndarray
            Values interpolated to match target_times
        """
        from scipy import interpolate
        import matplotlib.dates as mdates
        import numpy as np
        from .print_manager import print_manager
        
        print_manager.variable_testing(f"Starting interpolation: method={method}, source_length={len(source_times)}, target_length={len(target_times)}")
        
        # Convert datetime arrays to numeric for interpolation
        # Handle both Python datetime and numpy.datetime64 objects
        try:
            # For Python datetime objects
            source_numeric = mdates.date2num(source_times)
            target_numeric = mdates.date2num(target_times)
        except (ValueError, TypeError):
            # For numpy.datetime64 objects
            # Convert to seconds since epoch
            source_numeric = source_times.astype('datetime64[s]').astype(np.float64)
            target_numeric = target_times.astype('datetime64[s]').astype(np.float64)
            print_manager.variable_testing("Using numpy datetime64 conversion to numeric")
        
        # Skip interpolation if the times are already aligned
        if len(source_times) == len(target_times) and np.array_equal(source_numeric, target_numeric):
            print_manager.variable_testing("Times already aligned, skipping interpolation")
            return source_values
        
        # Handle NaN values in source data
        valid_mask = ~np.isnan(source_values)
        if not np.any(valid_mask):
            print_manager.variable_testing("All source values are NaN, returning NaN array")
            return np.full_like(target_numeric, np.nan)
        
        if not np.all(valid_mask):
            print_manager.variable_testing(f"Removing {len(source_values) - np.sum(valid_mask)} NaN values from source data")
            source_numeric = source_numeric[valid_mask]
            source_values = source_values[valid_mask]
            print_manager.variable_testing(f"Source data length after NaN removal: {len(source_values)}")
        
        # Create interpolation function
        if method == 'nearest':
            print_manager.variable_testing("Using nearest-neighbor interpolation")
            f = interpolate.interp1d(
                source_numeric, source_values,
                kind='nearest',
                bounds_error=False,
                fill_value=np.nan
            )
        else:  # linear
            print_manager.variable_testing("Using linear interpolation")
            f = interpolate.interp1d(
                source_numeric, source_values,
                kind='linear',
                bounds_error=False,
                fill_value=np.nan
            )
        
        # Perform interpolation
        interpolated_values = f(target_numeric)
        print_manager.variable_testing(f"Interpolation complete. Result length: {len(interpolated_values)}")
        
        # Check for NaNs in the result
        nan_count = np.sum(np.isnan(interpolated_values))
        if nan_count > 0:
            print_manager.variable_testing(f"Warning: {nan_count} NaN values in interpolated result")
        
        return interpolated_values

    def align_variables(self, other):
        """
        Align two variables by time, interpolating as needed.
        
        This method compares timestamps between variables and performs
        interpolation to ensure they match for element-wise operations.
        
        Parameters
        ----------
        other : plot_manager
            Variable to align with
            
        Returns
        -------
        tuple
            (self_aligned, other_aligned, datetime_array)
            Aligned numpy arrays and the common datetime array
        """
        from .data_cubby import data_cubby  # Moved import here to avoid circular import
        from .print_manager import print_manager
        from .data_classes.custom_variables import custom_variable
        
        # CRITICAL FIX: Check if variables have been corrupted and try to reload if possible
        # This fixes the state corruption issue when plotbot loads data for a different timerange
        
        # Check self variable state
        self_is_corrupt = False
        if self is None or (hasattr(self, 'data') and self.data is None):
            self_is_corrupt = True
        elif not hasattr(self, 'datetime_array') or self.datetime_array is None:
            self_is_corrupt = True
        
        # Check other variable state
        other_is_corrupt = False
        if other is None or (hasattr(other, 'data') and other.data is None):
            other_is_corrupt = True
        elif not hasattr(other, 'datetime_array') or other.datetime_array is None:
            other_is_corrupt = True
        
        # Attempt to reload corrupted variables from data_cubby
        if self_is_corrupt and hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            fresh_self = data_cubby.grab_component(self.class_name, self.subclass_name)
            if fresh_self is not None and hasattr(fresh_self, 'datetime_array') and fresh_self.datetime_array is not None:
                self = fresh_self
                self_is_corrupt = False
        
        if other_is_corrupt and hasattr(other, 'class_name') and hasattr(other, 'subclass_name'):
            fresh_other = data_cubby.grab_component(other.class_name, other.subclass_name)
            if fresh_other is not None and hasattr(fresh_other, 'datetime_array') and fresh_other.datetime_array is not None:
                other = fresh_other
                other_is_corrupt = False
        
        # If either variable is still corrupt after reload attempts, return empty arrays with proper shape
        if self_is_corrupt or other_is_corrupt:
            print_manager.custom_debug(f"[MATH] One or both variables still corrupt after reload attempt")
            empty_array = np.zeros(1)
            return empty_array, empty_array, np.array([])
        
        # First check if variables have valid shapes before trying to access size/length
        if not hasattr(self, 'shape') or not hasattr(other, 'shape'):
            print_manager.custom_debug(f"[MATH] Cannot align variables - one or both variables have no shape attribute")
            empty_array = np.zeros(1)
            return empty_array, empty_array, np.array([])
        
        # Now check if they have any data to align
        if self.size == 0 or other.size == 0:
            print_manager.custom_debug(f"[MATH] Cannot align variables - one or both variables have no data yet")
            empty_array = np.zeros(1)
            return empty_array, empty_array, np.array([])
        
        # Check if datetime arrays are None or empty
        no_datetime_self = not hasattr(self, 'datetime_array') or self.datetime_array is None or len(self.datetime_array) == 0
        no_datetime_other = not hasattr(other, 'datetime_array') or other.datetime_array is None or len(other.datetime_array) == 0
        
        if no_datetime_self and no_datetime_other:
            print_manager.custom_debug(f"[MATH] Both variables have no datetime arrays - cannot align")
            empty_array = np.zeros(1)
            return empty_array, empty_array, np.array([])
        
        # Check if interpolation is needed - use try/except to safely handle len() calls
        try:
            same_length = len(self) == len(other)
        except (TypeError, AttributeError):
            # If len() fails, assume they don't have the same length
            print_manager.custom_debug(f"[MATH] Cannot determine lengths - assuming unequal")
            same_length = False
        
        if same_length or no_datetime_self or no_datetime_other:
            # No interpolation needed or possible
            print_manager.custom_debug(f"[MATH] No interpolation needed or possible")
            
            # Use datetime array from either source
            if hasattr(self, 'datetime_array') and self.datetime_array is not None and len(self.datetime_array) > 0:
                dt_array = self.datetime_array
            elif hasattr(other, 'datetime_array') and other.datetime_array is not None and len(other.datetime_array) > 0:
                dt_array = other.datetime_array
            else:
                dt_array = None
                
            # Safely convert to array views
            try:
                self_view = self.view(np.ndarray)
            except Exception as e:
                self_view = np.zeros(1)
                
            try:
                other_view = other.view(np.ndarray)
            except Exception as e:
                other_view = np.zeros(1)
                
            # One final safety check - ensure we're not returning None values
            if self_view is None:
                self_view = np.zeros(1)
            if other_view is None:
                other_view = np.zeros(1)
                
            return self_view, other_view, dt_array
            
        # Choose shorter time base to avoid extrapolation
        # Use try/except for safety with datetime array length checks
        try:
            # Safety checks before length comparison
            if not hasattr(self, 'datetime_array') or self.datetime_array is None or len(self.datetime_array) == 0:
                print_manager.custom_debug(f"[MATH] First variable has no datetime array - using second variable's times")
                target_times = other.datetime_array
                self_aligned = np.zeros(len(target_times))  # Return zeros instead of None
                other_aligned = other.view(np.ndarray)
            elif not hasattr(other, 'datetime_array') or other.datetime_array is None or len(other.datetime_array) == 0:
                print_manager.custom_debug(f"[MATH] Second variable has no datetime array - using first variable's times")
                target_times = self.datetime_array
                self_aligned = self.view(np.ndarray)
                other_aligned = np.zeros(len(target_times))  # Return zeros instead of None
            elif len(self.datetime_array) <= len(other.datetime_array):
                print_manager.custom_debug(f"[MATH] Interpolating {getattr(other, 'subclass_name', 'var2')} to match {getattr(self, 'subclass_name', 'var1')}")
                target_times = self.datetime_array
                other_aligned = self.interpolate_to_times(
                    other.datetime_array, other.view(np.ndarray), 
                    target_times, method=plot_manager.interp_method
                )
                self_aligned = self.view(np.ndarray)
            else:
                print_manager.custom_debug(f"[MATH] Interpolating {getattr(self, 'subclass_name', 'var1')} to match {getattr(other, 'subclass_name', 'var2')}")
                target_times = other.datetime_array
                self_aligned = self.interpolate_to_times(
                    self.datetime_array, self.view(np.ndarray), 
                    target_times, method=plot_manager.interp_method
                )
                other_aligned = other.view(np.ndarray)
            
            # One final safety check - ensure we're not returning None values
            if self_aligned is None:
                self_aligned = np.zeros(len(target_times) if target_times is not None and len(target_times) > 0 else 1)
            if other_aligned is None:
                other_aligned = np.zeros(len(target_times) if target_times is not None and len(target_times) > 0 else 1)
                
            return self_aligned, other_aligned, target_times
        except (TypeError, AttributeError) as e:
            # If anything goes wrong during datetime array operations, return empty arrays
            print_manager.custom_debug(f"[MATH] Error during interpolation - {str(e)}")
            empty_array = np.zeros(1)
            return empty_array, empty_array, np.array([])
            
    def _perform_operation(self, other, operation_name, operation_func, reverse_op=False):
        """Helper method to perform arithmetic operations."""
        from .print_manager import print_manager
        from .data_classes.custom_variables import custom_variable
        from .ploptions import ploptions
        import numpy as np
        
        # Special handling for unary operations (where other is None)
        if other is None:  # Unary operation like __neg__ or __abs__
            print_manager.custom_debug(f"[MATH] Performing unary {operation_name}: {getattr(self, 'subclass_name', 'var1')}")
            
            # Track source variables
            source_vars = []
            if hasattr(self, 'source_var') and self.source_var is not None:
                source_vars.extend(self.source_var)
            elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
                source_vars.append(self)
            
            try:
                # Apply the unary operation to self's data
                self_data = self.view(np.ndarray)
                # The lambda in the method call handles applying just to first arg
                result = operation_func(self_data, None)
                
                # Create variable name
                var_name = f"{operation_name}_{getattr(self, 'subclass_name', 'var1')}"
                
                # Create result plot_manager
                result_plot_options = ploptions(
                    data_type="custom_data_type",
                    class_name="custom_class", 
                    subclass_name=var_name,
                    plot_type="time_series",
                    datetime_array=self.datetime_array if hasattr(self, 'datetime_array') else None
                )
                
                # Create the result
                result_var = plot_manager(result, result_plot_options)
                
                # Set metadata
                object.__setattr__(result_var, 'operation', operation_name)
                object.__setattr__(result_var, 'source_var', source_vars)
                
                # Return wrapped in custom_variable
                return custom_variable(var_name, result_var)
            
            except Exception as e:
                print_manager.custom_debug(f"[MATH] Error during unary {operation_name}: {str(e)}")
                # For unary ops, return self on error as fallback
                return self
        
        # Rest of the existing method for binary operations...
        print_manager.custom_debug(f"[MATH] Performing {operation_name}: {getattr(self, 'subclass_name', 'var1')} vs {getattr(other, 'subclass_name', str(other))}")
        
        source_vars = []
        scalar_value = None
        dt_array = None
        
        # Initial source tracking for 'self'
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if isinstance(other, plot_manager):
            # --- Plot Manager vs Plot Manager ---
            # Also track other variable's sources if available
            if hasattr(other, 'source_var') and other.source_var is not None:
                source_vars.extend(other.source_var)
            elif hasattr(other, 'class_name') and hasattr(other, 'subclass_name'):
                source_vars.append(other)
                
            self_aligned, other_aligned, dt_array = self.align_variables(other)

            # Safety check after alignment
            if self_aligned is None or other_aligned is None:
                print_manager.warning(f"Cannot perform {operation_name}: Alignment failed.")
                result = np.zeros(1)
                var_name = f"{getattr(self, 'subclass_name', 'var1')}_{getattr(other, 'subclass_name', 'var2')}_{operation_name}_failed"
                # Early return for failure case, maybe wrapped? Or handle below?
                # For simplicity, let's create a placeholder result below.
            else:
                try:
                    # Safety check for empty arrays
                    if len(self_aligned) == 0 or len(other_aligned) == 0:
                        print_manager.warning(f"Cannot perform {operation_name}: Empty array after alignment.")
                        result = np.zeros(1) # Or maybe shape of dt_array if available?
                    else:
                        # Perform the actual operation
                        if reverse_op: # Handle things like scalar / variable
                            result = operation_func(other_aligned, self_aligned)
                        else:
                            result = operation_func(self_aligned, other_aligned)

                    # STATUS PRINT (Optional - Add back if needed)
                    # print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} {op_symbol} {other.class_name}.{other.subclass_name}")
                    # print_manager.variable_basic(f"   → Interpolation may have occurred.")

                except Exception as e:
                    print_manager.custom_debug(f"[MATH] Error during {operation_name}: {str(e)}")
                    result = np.zeros(1) # Fallback result on error

            # Create variable name
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_{getattr(other, 'subclass_name', 'var2')}_{operation_name}"

        else:
            # --- Plot Manager vs Scalar ---
            scalar_value = other
            
            # Add self to source vars if not already tracked (e.g. if self was already a derived var)
            if not any(sv is self for sv in source_vars):
                if hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
                    source_vars.append(self)

            try:
                self_data = self.view(np.ndarray)
                # Perform the actual operation
                if reverse_op: # Handle things like scalar / variable
                    # Special handling for division by zero if needed
                    if operation_name == 'div' or operation_name == 'floordiv':
                        safe_self_data = np.where(self_data == 0, np.nan, self_data)
                        result = operation_func(scalar_value, safe_self_data)
                    else:
                        result = operation_func(scalar_value, self_data)
                else:
                    # Special handling for division by zero if needed
                    if (operation_name == 'div' or operation_name == 'floordiv') and scalar_value == 0:
                        result = np.full_like(self_data, np.nan)
                    else:
                        result = operation_func(self_data, scalar_value)

                # STATUS PRINT (Optional - Add back if needed)
                # print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} {op_symbol} {scalar_value}")
                # print_manager.variable_basic(f"   → No interpolation needed for scalar operation.")

            except Exception as e:
                print_manager.custom_debug(f"[MATH] Error during scalar {operation_name}: {str(e)}")
                result = np.zeros(1) # Fallback result on error

            # Create variable name
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_scalar_{operation_name}"
            if reverse_op:
                var_name = f"scalar_{scalar_value}_{operation_name}_{getattr(self, 'subclass_name', 'var1')}"

        # --- Create result plot_manager ---
        # Use placeholder options initially, custom_variable will refine
        result_plot_options = ploptions(
            data_type="custom_data_type", # Let custom_variable set to custom_data_type
            class_name="custom_class", # Let custom_variable set to custom_class
            subclass_name=var_name, # Temporary, custom_variable uses this
            plot_type="time_series",
            datetime_array=(dt_array if dt_array is not None else (self.datetime_array if hasattr(self, 'datetime_array') else None))
        )
        
        # Create the result using plot_manager constructor
        result_var = plot_manager(result, result_plot_options)

        # --- Set metadata on the result object ---
        # Explicitly using object.__setattr__ might be safer here
        object.__setattr__(result_var, 'operation', operation_name)
        object.__setattr__(result_var, 'source_var', source_vars) # Set the tracked sources
        if scalar_value is not None:
            object.__setattr__(result_var, 'scalar_value', scalar_value)

        # --- Wrap in custom_variable for registration ---
        # custom_variable will set final names, labels, and register it
        return custom_variable(var_name, result_var)

    def __add__(self, other):
        """Add two variables or a variable and a scalar."""
        import numpy as np
        return self._perform_operation(other, 'add', np.add)

    def __sub__(self, other):
        """Subtract two variables or a variable and a scalar."""
        import numpy as np
        return self._perform_operation(other, 'sub', np.subtract)

    def __radd__(self, other):
        """Handle right-sided addition (other + self)."""
        import numpy as np
        return self._perform_operation(other, 'add', np.add, reverse_op=True)

    def __rsub__(self, other):
        """Handle right-sided subtraction (other - self)."""
        import numpy as np
        return self._perform_operation(other, 'sub', np.subtract, reverse_op=True)

    def __mul__(self, other):
        """Multiply two variables or a variable and a scalar."""
        import numpy as np
        # This would now consistently call custom_variable via the helper
        return self._perform_operation(other, 'mul', np.multiply)

    def __rmul__(self, other):
        """Support right multiplication (e.g., 5 * variable)."""
        import numpy as np
        return self._perform_operation(other, 'mul', np.multiply, reverse_op=True)

    def __truediv__(self, other):
        """Divide two variables or a variable and a scalar."""
        import numpy as np
        # Helper needs to handle division by zero for scalar case
        return self._perform_operation(other, 'div', np.true_divide)
    
    def __rtruediv__(self, other):
        """Handle right-sided division (other / self)."""
        import numpy as np
        return self._perform_operation(other, 'div', np.true_divide, reverse_op=True)

    def __pow__(self, other):
        """Support exponentiation (e.g., variable ** 2)."""
        import numpy as np
        return self._perform_operation(other, 'pow', np.power)
        
    def __rpow__(self, other):
        """Handle right-sided power (other ** self)."""
        import numpy as np
        return self._perform_operation(other, 'pow', np.power, reverse_op=True)

    def __floordiv__(self, other):
        """Handle floor division with automatic recalculation capability."""
        import numpy as np
        return self._perform_operation(other, 'floordiv', np.floor_divide)

    def __rfloordiv__(self, other):
        """Handle right-sided floor division (other // self)."""
        import numpy as np
        return self._perform_operation(other, 'floordiv', np.floor_divide, reverse_op=True)

    def __neg__(self):
        """Handle negation with automatic recalculation capability."""
        import numpy as np
        # For unary operations, we can pass None as 'other', only perform op on self
        # The operation func needs to handle just the data, not two arguments
        return self._perform_operation(None, 'neg', lambda x, _: np.negative(x))

    def __abs__(self):
        """Handle absolute value with automatic recalculation capability."""
        import numpy as np
        # For unary operations, we can pass None as 'other', only perform op on self
        # The operation func needs to handle just the data, not two arguments
        return self._perform_operation(None, 'abs', lambda x, _: np.abs(x))

    def __radd__(self, other):
        """Handle right-sided addition (other + self)."""
        import numpy as np
        return self._perform_operation(other, 'add', np.add, reverse_op=True)

    def __rsub__(self, other):
        """Handle right-sided subtraction (other - self)."""
        import numpy as np
        return self._perform_operation(other, 'sub', np.subtract, reverse_op=True)

    def __rmul__(self, other):
        """Support right multiplication (e.g., 5 * variable)."""
        import numpy as np
        return self._perform_operation(other, 'mul', np.multiply, reverse_op=True)

    def __rtruediv__(self, other):
        """Handle right-sided division (other / self)."""
        import numpy as np
        return self._perform_operation(other, 'div', np.true_divide, reverse_op=True)

    def __rpow__(self, other):
        """Handle right-sided power (other ** self)."""
        import numpy as np
        return self._perform_operation(other, 'pow', np.power, reverse_op=True)

    def __rfloordiv__(self, other):
        """Handle right-sided floor division (other // self)."""
        import numpy as np
        return self._perform_operation(other, 'floordiv', np.floor_divide, reverse_op=True)
    
    def _check_default_value(self, name):
        """Check if a default value exists for a given attribute."""
        try:
            default_value = self._default_values.get(name, None)
            if default_value is None:
                print_manager.warning(f"No default value found for {name}")
            return default_value
        except Exception as e:
            return None

print('initialized plot_manager')
