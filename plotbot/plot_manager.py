# 🎉 Extend numpy.ndarray with plotting functionality and friendly error handling 🎉
#SAFE! 

import numpy as np
import matplotlib.pyplot as plt
from .ploptions import ploptions
from .print_manager import print_manager
from .data_cubby import data_cubby
from .custom_variables import custom_variable  # Use custom_variable instead

class plot_manager(np.ndarray):
    
    PLOT_ATTRIBUTES = [
        'data', 'data_type', 'var_name', 'class_name', 'subclass_name', 'plot_type', 'datetime_array', 
        'y_label', 'legend_label', 'color', 'y_scale', 'y_limit', 'line_width',
        'line_style', 'colormap', 'colorbar_scale', 'colorbar_limits',
        'additional_data', 'colorbar_label', 'is_derived', 'source_var', 'operation',
        # RecalculableDerived attributes
        'source_vars', 'scalar_value', 'operation_str', 'is_recalculable',
        'recalculate_for_timerange', 'get_base_variables',
        # New attributes for improved derived variable handling
        'source_class_names', 'source_subclass_names',
        # Named variable reference tracking
        'original_derived_var', 'original_derived_name', 'add',
        # Add missing attributes
        # 'marker', 'marker_size', 'alpha', 'zorder', 'legend_label_override'
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
        
        # Safely handle plot_options
        if plot_options is None:
            from .ploptions import ploptions
            plot_options = ploptions(
                data_type="derived",
                class_name="derived", 
                subclass_name="temporary_derived_variable",
                plot_type="time_series"
            )
        
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
                print(f"'{name}' is not a recognized attribute, friend!")
                print(f"Try one of these: {', '.join(self.PLOT_ATTRIBUTES)}")
                return

        except Exception as e:
            print_manager.warning(f"Error setting {name}: {str(e)}")

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
        
        # For unrecognized attributes, TEMPORARY FIX: still allow storing the attribute
        # but print a warning
        if not name.startswith('_'):
            print_manager.warning(f"Warning: '{name}' is not a recognized attribute, but will be stored anyway.")
            # Create an entry in _plot_state for this attribute
            self._plot_state[name] = None
            return None

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
        from .print_manager import print_manager
        
        # First check if variables have valid shapes before trying to access size/length
        if not hasattr(self, 'shape') or not hasattr(other, 'shape'):
            print_manager.custom_debug(f"[MATH] Cannot align variables - one or both variables have no shape attribute")
            return np.array([]), np.array([]), None
        
        # Now check if they have any data to align
        if self.size == 0 or other.size == 0:
            print_manager.custom_debug(f"[MATH] Cannot align variables - one or both variables have no data yet")
            return np.array([]), np.array([]), None
        
        # CRITICAL FIX: Check if datetime arrays are None or empty
        no_datetime_self = not hasattr(self, 'datetime_array') or self.datetime_array is None or len(self.datetime_array) == 0
        no_datetime_other = not hasattr(other, 'datetime_array') or other.datetime_array is None or len(other.datetime_array) == 0
        
        if no_datetime_self and no_datetime_other:
            print_manager.custom_debug(f"[MATH] Both variables have no datetime arrays - cannot align")
            return np.array([]), np.array([]), None
        
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
            except:
                self_view = np.array([])
                
            try:
                other_view = other.view(np.ndarray)
            except:
                other_view = np.array([])
                
            return self_view, other_view, dt_array
            
        # Choose shorter time base to avoid extrapolation
        # Use try/except for safety with datetime array length checks
        try:
            # CRITICAL FIX: Additional safety checks before length comparison
            if not hasattr(self, 'datetime_array') or self.datetime_array is None or len(self.datetime_array) == 0:
                print_manager.custom_debug(f"[MATH] First variable has no datetime array - using second variable's times")
                target_times = other.datetime_array
                self_aligned = self.view(np.ndarray)
                other_aligned = other.view(np.ndarray)
            elif not hasattr(other, 'datetime_array') or other.datetime_array is None or len(other.datetime_array) == 0:
                print_manager.custom_debug(f"[MATH] Second variable has no datetime array - using first variable's times")
                target_times = self.datetime_array
                self_aligned = self.view(np.ndarray)
                other_aligned = other.view(np.ndarray)
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
            
            return self_aligned, other_aligned, target_times
        except (TypeError, AttributeError) as e:
            # If anything goes wrong during datetime array operations, return empty arrays
            print_manager.custom_debug(f"[MATH] Error during interpolation - {str(e)}")
            return np.array([]), np.array([]), None
    
    # Magic methods for arithmetic operations
    def __add__(self, other):
        """Add two variables or a variable and a scalar."""
        # No longer importing from derived_variable
        from .print_manager import print_manager
        from .custom_variables import custom_variable
        
        print_manager.custom_debug(f"[MATH] Adding {getattr(self, 'subclass_name', 'var1')} + {getattr(other, 'subclass_name', str(other))}")
        
        # Check if other is a plot_manager instance
        if isinstance(other, plot_manager):
            # Object addition case - align variables first
            self_aligned, other_aligned, dt_array = self.align_variables(other)
            result = self_aligned + other_aligned
            
            # Create a name for the variable
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_{getattr(other, 'subclass_name', 'var2')}_add"
            
            # Set up the result with datetime array from alignment using proper methods
            # that avoid truth value errors with arrays
            result_var = plot_manager(result)
            if dt_array is not None:
                # Use direct attribute setting to avoid truth value errors
                object.__setattr__(result_var, 'datetime_array', dt_array)
            
            # Store source info for later updates
            object.__setattr__(result_var, 'source_var', [self, other])
            object.__setattr__(result_var, 'operation', 'add')
            
            # Create a custom variable directly
            return custom_variable(var_name, result_var)
        else:
            # Scalar addition case
            result = self.view(np.ndarray) + other
            
            # Create a result variable with datetime array from self using proper methods
            # that avoid truth value errors with arrays
            result_var = plot_manager(result)
            if hasattr(self, 'datetime_array') and self.datetime_array is not None:
                # Use direct attribute setting to avoid truth value errors
                object.__setattr__(result_var, 'datetime_array', self.datetime_array)
            
            # Store source info for later updates
            object.__setattr__(result_var, 'source_var', [self])
            object.__setattr__(result_var, 'operation', 'add')
            object.__setattr__(result_var, 'scalar_value', other)
            
            # Create a custom variable directly
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_scalar_add"
            return custom_variable(var_name, result_var)
    
    def __radd__(self, other):
        """Handle right-sided addition (other + self)."""
        # For scalar + plot_manager
        print_manager.variable_testing(f"Right-sided addition: {other} + {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
            
        if not isinstance(other, plot_manager):
            result_array = other + self.data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} + {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_add_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}+{self.subclass_name}",
                legend_label=f"{other}+{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'add'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it
    
    def __radd__(self, other):
        """Support right addition (e.g., 5 + variable)."""
        return self.__add__(other)
    
    def __sub__(self, other):
        """Subtract two variables or a variable and a scalar."""
        # No longer importing from derived_variable
        from .print_manager import print_manager
        from .custom_variables import custom_variable
        
        print_manager.custom_debug(f"[MATH] Subtracting {getattr(self, 'subclass_name', 'var1')} - {getattr(other, 'subclass_name', str(other))}")
        
        # Check if other is a plot_manager instance
        if isinstance(other, plot_manager):
            # Object subtraction case - align variables first
            self_aligned, other_aligned, dt_array = self.align_variables(other)
            result = self_aligned - other_aligned
            
            # Create a name for the variable
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_{getattr(other, 'subclass_name', 'var2')}_sub"
            
            # Set up the result with datetime array from alignment using proper methods
            # that avoid truth value errors with arrays
            result_var = plot_manager(result)
            if dt_array is not None:
                # Use direct attribute setting to avoid truth value errors
                object.__setattr__(result_var, 'datetime_array', dt_array)
            
            # Store source info for later updates
            object.__setattr__(result_var, 'source_var', [self, other])
            object.__setattr__(result_var, 'operation', 'sub')
            
            # Create a custom variable directly
            return custom_variable(var_name, result_var)
        else:
            # Scalar subtraction case
            result = self.view(np.ndarray) - other
            
            # Create a result variable with datetime array from self using proper methods
            # that avoid truth value errors with arrays
            result_var = plot_manager(result)
            if hasattr(self, 'datetime_array') and self.datetime_array is not None:
                # Use direct attribute setting to avoid truth value errors
                object.__setattr__(result_var, 'datetime_array', self.datetime_array)
            
            # Store source info for later updates
            object.__setattr__(result_var, 'source_var', [self])
            object.__setattr__(result_var, 'operation', 'sub')
            object.__setattr__(result_var, 'scalar_value', other)
            
            # Create a custom variable directly
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_scalar_sub"
            return custom_variable(var_name, result_var)
    
    def __rsub__(self, other):
        """Support right subtraction (e.g., 5 - variable)."""
        print_manager.variable_testing(f"Right-sided subtraction: {other} - {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        # This is scalar - variable, so we flip and negate
        result_array = -(self.data - other)
        
        # STATUS PRINT: Show operation complete message for scalar operation
        print_manager.variable_basic(f"📊 Operation complete: {other} - {self.class_name}.{self.subclass_name}")
        print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
        
        # Create a new plot_manager with the result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=f"scalar_{other}_rsub_{self.subclass_name}",
            plot_type="time_series",
            datetime_array=self.datetime_array,
            y_label=f"{other}-{self.subclass_name}",
            legend_label=f"{other}-{self.subclass_name}"
        )
        
        # Create the result using plot_manager
        result = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result.operation = 'sub'
        result.source_var = source_vars
        result.scalar_value = other
        
        # Return the computed result
        return result
    
    def __rmul__(self, other):
        """Support right multiplication (e.g., 5 * variable)."""
        return self.__mul__(other)
    
    def __rsub__(self, other):
        """Support right subtraction (e.g., 5 - variable)."""
        # Import within function to avoid circular dependency
        from .derived_variable import RecalculableDerived
        from .print_manager import print_manager
        
        print_manager.custom_debug(f"[MATH] Right subtraction {other} - {getattr(self, 'subclass_name', 'var1')}")
        
        # This is scalar - variable, so we flip and negate
        result = -(self.view(np.ndarray) - other)
        
        # Create a recalculable derived variable
        if hasattr(self, 'datetime_array'):
            dt_array = self.datetime_array
        else:
            dt_array = None
            
        # Store source variables for recalculation
        source_vars = [self]
        
        return RecalculableDerived(
            result,
            dt_array,
            'sub',
            source_vars,
            scalar_value=other,
            operation_str=f"{other} - {getattr(self, 'subclass_name', 'var1')}"
        )
    
    def __mul__(self, other):
        """Multiply two variables or a variable and a scalar."""
        print_manager.variable_testing(f"Multiplication: {self.class_name}.{self.subclass_name} * {getattr(other, 'subclass_name', str(other))}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        # Check if other is a plot_manager instance
        if isinstance(other, plot_manager):
            # Also track other variable's sources if available
            if hasattr(other, 'source_var') and other.source_var is not None:
                source_vars.extend(other.source_var)
            elif hasattr(other, 'class_name') and hasattr(other, 'subclass_name'):
                source_vars.append(other)
                
            # Object multiplication case - align variables first
            self_aligned, other_aligned, dt_array = self.align_variables(other)
            result_array = self_aligned * other_aligned
            
            # STATUS PRINT: Show operation complete message after interpolation
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} * {other.class_name}.{other.subclass_name}")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"{self.subclass_name}_{other.subclass_name}_mul",
                plot_type="time_series",
                datetime_array=dt_array
                # Don't set y_label or legend_label here to let custom_variable set them
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'mul'
            result.source_var = source_vars
            
            # Return the result directly, without calling custom_variable
            return result
        else:
            # Scalar multiplication case
            result_array = self.data * other
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} * {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"{self.subclass_name}_scalar_mul",
                plot_type="time_series",
                datetime_array=self.datetime_array
                # Don't set y_label or legend_label here to let custom_variable set them
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'mul'
            result.source_var = source_vars
            result.scalar_value = other
            
            # Return the result directly, without calling custom_variable
            return result
    
    def __truediv__(self, other):
        """Divide two variables or a variable and a scalar."""
        # No longer importing from derived_variable
        from .print_manager import print_manager
        from .custom_variables import custom_variable
        
        print_manager.custom_debug(f"[MATH] Dividing {getattr(self, 'subclass_name', 'var1')} / {getattr(other, 'subclass_name', str(other))}")
        
        # Check if other is a plot_manager instance
        if isinstance(other, plot_manager):
            # Object division case - align variables first
            self_aligned, other_aligned, dt_array = self.align_variables(other)
            
            # Avoid division by zero
            other_aligned = np.where(other_aligned == 0, np.nan, other_aligned)
            result = self_aligned / other_aligned
            
            # Create a name for the variable
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_{getattr(other, 'subclass_name', 'var2')}_div"
            
            # Set up the result with datetime array from alignment using proper methods
            # that avoid truth value errors with arrays
            result_var = plot_manager(result)
            if dt_array is not None:
                # Use direct attribute setting to avoid truth value errors
                object.__setattr__(result_var, 'datetime_array', dt_array)
            
            # Store source info for later updates
            object.__setattr__(result_var, 'source_var', [self, other])
            object.__setattr__(result_var, 'operation', 'div')
            
            # Create a custom variable directly
            return custom_variable(var_name, result_var)
        else:
            # Scalar division case - avoid division by zero
            if other == 0:
                result = np.full_like(self.view(np.ndarray), np.nan)
            else:
                result = self.view(np.ndarray) / other
            
            # Create a result variable with datetime array from self
            result_var = plot_manager(result)
            if hasattr(self, 'datetime_array'):
                result_var.datetime_array = self.datetime_array
            
            # Store source info for later updates
            result_var.source_var = [self]
            result_var.operation = 'div'
            result_var.scalar_value = other
            
            # Create a custom variable directly
            var_name = f"{getattr(self, 'subclass_name', 'var1')}_scalar_div"
            return custom_variable(var_name, result_var)
    
    def __rtruediv__(self, other):
        """Support right division (e.g., 5 / variable)."""
        print_manager.variable_testing(f"Right-sided division: {other} / {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        # Avoid division by zero
        safe_data = np.where(self.data == 0, np.nan, self.data)
        result_array = other / safe_data
        
        # STATUS PRINT: Show operation complete message for scalar operation
        print_manager.variable_basic(f"📊 Operation complete: {other} / {self.class_name}.{self.subclass_name}")
        print_manager.variable_basic(f"   → No interpolation needed for scalar operation")
        print_manager.variable_basic(f"   → Any division by zero has been replaced with NaN values\n")
        
        # Create a new plot_manager with the result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=f"scalar_{other}_div_{self.subclass_name}",
            plot_type="time_series",
            datetime_array=self.datetime_array,
            y_label=f"{other}/{self.subclass_name}",
            legend_label=f"{other}/{self.subclass_name}"
        )
        
        # Create the result using plot_manager
        result = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result.operation = 'div'
        result.source_var = source_vars
        result.scalar_value = other
        
        # Return the computed result
        return result

    def __pow__(self, other):
        """Support exponentiation (e.g., variable ** 2)."""
        print_manager.variable_testing(f"Power operation: {self.class_name}.{self.subclass_name} ** {other}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
            
        result_array = np.power(self.data, other)
        
        # STATUS PRINT: Show operation complete message for scalar operation
        print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} ** {other}")
        print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
        
        # Create a new plot_manager with the result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=f"{self.subclass_name}_pow_{other}",
            plot_type="time_series",
            datetime_array=self.datetime_array,
            y_label=f"{self.subclass_name}^{other}",
            legend_label=f"{self.subclass_name}^{other}"
        )
        
        # Create the result using plot_manager
        result = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result.operation = 'pow'
        result.source_var = source_vars
        result.scalar_value = other
        
        # Return the computed result
        return result

    def __neg__(self):
        """Handle negation with automatic recalculation capability."""
        print_manager.variable_testing(f"Negating {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        result_array = -self.data
        
        # STATUS PRINT: Show operation details for __neg__
        print_manager.variable_basic(f"📊 Operation complete: -{self.class_name}.{self.subclass_name}")
        print_manager.variable_basic(f"   → Unary operation (no interpolation needed)\n")
        
        # Operation string for debugging
        operation_str = f"-{self.class_name}.{self.subclass_name}"
        
        # Create a new plot_manager with the result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=f"neg_{self.subclass_name}",
            plot_type="time_series",
            datetime_array=self.datetime_array,
            y_label=f"-{self.subclass_name}",
            legend_label=f"-{self.subclass_name}"
        )
        
        # Create the result using plot_manager
        result = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result.operation = 'neg'
        result.source_var = source_vars
        
        # Return the computed result
        return result

    def __abs__(self):
        """Handle absolute value with automatic recalculation capability."""
        print_manager.variable_testing(f"Taking absolute value of {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        result_array = abs(self.data)
        
        # STATUS PRINT: Show operation details for __abs__
        print_manager.variable_basic(f"📊 Operation complete: abs({self.class_name}.{self.subclass_name})")
        print_manager.variable_basic(f"   → Unary operation (no interpolation needed)\n")
        
        # Operation string for debugging
        operation_str = f"abs({self.class_name}.{self.subclass_name})"
        
        # Create a new plot_manager with the result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=f"abs_{self.subclass_name}",
            plot_type="time_series",
            datetime_array=self.datetime_array,
            y_label=f"|{self.subclass_name}|",
            legend_label=f"|{self.subclass_name}|"
        )
        
        # Create the result using plot_manager
        result = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result.operation = 'abs'
        result.source_var = source_vars
        
        # Return the computed result
        return result

    def __floordiv__(self, other):
        """Handle floor division with automatic recalculation capability."""
        print_manager.variable_testing(f"Floor dividing {self.class_name}.{self.subclass_name} by {other}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np

        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if isinstance(other, plot_manager):
            # Also track other variable's sources if available
            if hasattr(other, 'source_var') and other.source_var is not None:
                source_vars.extend(other.source_var)
            elif hasattr(other, 'class_name') and hasattr(other, 'subclass_name'):
                source_vars.append(other)
                
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"First array time points: {len(self_times)}, Second array time points: {len(other_times)}")
            
            # For user-friendly status message
            first_var = f"{self.class_name}.{self.subclass_name}"
            second_var = f"{other.class_name}.{other.subclass_name}"
            interpolated_var = None
            target_var = None
            
            # Check sampling rates if possible - handle numpy.datetime64 objects
            if len(self_times) > 1 and len(other_times) > 1:
                try:
                    # Try with total_seconds() for Python datetime objects
                    self_cadence = (self_times[1] - self_times[0]).total_seconds()
                    other_cadence = (other_times[1] - other_times[0]).total_seconds()
                except AttributeError:
                    # For numpy.datetime64 objects
                    self_cadence = (self_times[1] - self_times[0]) / np.timedelta64(1, 's')
                    other_cadence = (other_times[1] - other_times[0]) / np.timedelta64(1, 's')
                
                print_manager.variable_testing(f"First array sampling cadence: {self_cadence} seconds")
                print_manager.variable_testing(f"Second array sampling cadence: {other_cadence} seconds")
            
            # Determine which variable has fewer time points to use as target
            if len(self_times) <= len(other_times):
                # Use self's time points as the target (fewer points)
                target_times = self_times
                target_var = first_var
                interpolated_var = second_var
                print_manager.variable_testing(f"Using first array ({self.class_name}.{self.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {other.class_name}.{other.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate other's values to align with self's time points
                interpolated_values = self.interpolate_to_times(
                    other_times, other.data, target_times, self.__class__.interp_method)
                
                # Perform the floor division with the interpolated values
                result_array = self.data // interpolated_values
                dt_array = target_times
            else:
                # Use other's time points as the target (fewer points)
                target_times = other_times
                target_var = second_var
                interpolated_var = first_var
                print_manager.variable_testing(f"Using second array ({other.class_name}.{other.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {self.class_name}.{self.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate self's values to align with other's time points
                interpolated_values = self.interpolate_to_times(
                    self_times, self.data, target_times, self.__class__.interp_method)
                
                # Perform the floor division with the interpolated values
                result_array = interpolated_values // other.data
                dt_array = target_times
                
            print_manager.variable_testing(f"Floor division complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} // {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
            
            # Operation string for debugging
            operation_str = f"{self.class_name}.{self.subclass_name} // {other.class_name}.{other.subclass_name}"
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"{self.subclass_name}_floordiv_{other.subclass_name}",
                plot_type="time_series",
                datetime_array=dt_array,
                y_label=f"{self.subclass_name}//{other.subclass_name}",
                legend_label=f"{self.subclass_name}//{other.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'floordiv'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        else:
            # Handle scalar floor division
            result_array = self.data // other
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} // {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Operation string for debugging
            operation_str = f"{self.class_name}.{self.subclass_name} // {other}"
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"{self.subclass_name}_floordiv_{other}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{self.subclass_name}//{other}",
                legend_label=f"{self.subclass_name}//{other}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'floordiv'
            result.source_var = source_vars
            
            # Return the computed result
            return result

    def __radd__(self, other):
        """Handle right-sided addition (other + self)."""
        # For scalar + plot_manager
        print_manager.variable_testing(f"Right-sided addition: {other} + {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if not isinstance(other, plot_manager):
            result_array = other + self.data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} + {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_add_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}+{self.subclass_name}",
                legend_label=f"{other}+{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'add'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it

    def __rsub__(self, other):
        """Handle right-sided subtraction (other - self)."""
        # For scalar - plot_manager
        print_manager.variable_testing(f"Right-sided subtraction: {other} - {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if not isinstance(other, plot_manager):
            result_array = other - self.data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} - {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_sub_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}-{self.subclass_name}",
                legend_label=f"{other}-{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'sub'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it

    def __rmul__(self, other):
        """Support right multiplication (e.g., 5 * variable)."""
        return self.__mul__(other)

    def __rtruediv__(self, other):
        """Handle right-sided division (other / self)."""
        # For scalar / plot_manager
        print_manager.variable_testing(f"Right-sided division: {other} / {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if not isinstance(other, plot_manager):
            # Avoid division by zero
            safe_data = np.where(self.data == 0, np.nan, self.data)
            result_array = other / safe_data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} / {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation")
            print_manager.variable_basic(f"   → Any division by zero has been replaced with NaN values\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_div_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}/{self.subclass_name}",
                legend_label=f"{other}/{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'div'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it

    def __rpow__(self, other):
        """Handle right-sided power (other ** self)."""
        # For scalar ** plot_manager
        print_manager.variable_testing(f"Right-sided power: {other} ** {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if not isinstance(other, plot_manager):
            result_array = other ** self.data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} ** {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_pow_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}^{self.subclass_name}",
                legend_label=f"{other}^{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'pow'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it

    def __rfloordiv__(self, other):
        """Handle right-sided floor division (other // self)."""
        # For scalar // plot_manager
        print_manager.variable_testing(f"Right-sided floor division: {other} // {self.class_name}.{self.subclass_name}")
        
        # Import here to avoid circular imports
        from .custom_variables import custom_variable
        import numpy as np
        
        # Track source variables for the operation
        source_vars = []
        if hasattr(self, 'source_var') and self.source_var is not None:
            source_vars.extend(self.source_var)
        elif hasattr(self, 'class_name') and hasattr(self, 'subclass_name'):
            source_vars.append(self)
        
        if not isinstance(other, plot_manager):
            # Avoid division by zero
            safe_data = np.where(self.data == 0, np.nan, self.data)
            result_array = other // safe_data
            
            # STATUS PRINT: Show operation complete message for scalar operation
            print_manager.variable_basic(f"📊 Operation complete: {other} // {self.class_name}.{self.subclass_name}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation")
            print_manager.variable_basic(f"   → Any division by zero has been replaced with NaN values\n")
            
            # Create a new plot_manager with the result
            from .ploptions import ploptions
            result_plot_options = ploptions(
                data_type="custom_data_type",
                class_name="custom_class", 
                subclass_name=f"scalar_{other}_floordiv_{self.subclass_name}",
                plot_type="time_series",
                datetime_array=self.datetime_array,
                y_label=f"{other}//{self.subclass_name}",
                legend_label=f"{other}//{self.subclass_name}"
            )
            
            # Create the result using plot_manager
            result = plot_manager(result_array, result_plot_options)
            
            # Store the operation type and sources for custom variable container to use
            result.operation = 'floordiv'
            result.source_var = source_vars
            
            # Return the computed result
            return result
        return NotImplemented  # Let the left operand handle it
    
    def _create_derived(self, operation, source_vars, input_name=None, scalar_value=None):
        """Create a derived variable from operations."""
        from .print_manager import print_manager
        from .custom_variables import custom_variable
        import types
        import numpy as np
        
        # CRITICAL BUGFIX: Debug what's being passed in
        print_manager.variable_testing(f"_create_derived called with operation='{operation}', source_vars={[getattr(v, 'subclass_name', str(v)) for v in source_vars]}")
        
        # Generate a unique name for this derived variable if not provided
        if not input_name:
            if len(source_vars) == 1 and scalar_value is not None:
                var_name = f"{source_vars[0].class_name}_{source_vars[0].subclass_name}_{operation}_{scalar_value}"
            elif len(source_vars) == 2:
                var_name = f"{source_vars[0].class_name}_{source_vars[0].subclass_name}_{operation}_{source_vars[1].class_name}_{source_vars[1].subclass_name}"
            else:
                var_name = f"derived_{operation}_{np.random.randint(1000, 9999)}"
        else:
            var_name = input_name
        
        # Apply appropriate operation with proper interpolation
        if operation == 'add':
            if len(source_vars) == 1 and scalar_value is not None:
                # Scalar operation - no interpolation needed
                result_array = source_vars[0].data + scalar_value
                datetime_array = source_vars[0].datetime_array
                # Add user-friendly status message for scalar
                print_manager.variable_basic(f"📊 Operation complete: {source_vars[0].class_name}.{source_vars[0].subclass_name} + {scalar_value}")
                print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            elif len(source_vars) == 2:
                # Vector operation - needs interpolation
                var1 = source_vars[0]
                var2 = source_vars[1]
                
                # Get datetime arrays
                var1_times = var1.datetime_array
                var2_times = var2.datetime_array
                
                print_manager.variable_testing(f"First array time points: {len(var1_times)}, Second array time points: {len(var2_times)}")
                
                # For user-friendly status message
                first_var = f"{var1.class_name}.{var1.subclass_name}"
                second_var = f"{var2.class_name}.{var2.subclass_name}"
                
                # Determine which variable has fewer time points to use as target
                if len(var1_times) <= len(var2_times):
                    # Use var1's time points as the target (fewer points)
                    target_times = var1_times
                    print_manager.variable_testing(f"Using first array ({var1.class_name}.{var1.subclass_name}) time points as target (fewer points)")
                    print_manager.variable_testing(f"Interpolating {var2.class_name}.{var2.subclass_name} using method: {self.__class__.interp_method}")
                    
                    # Interpolate var2's values to align with var1's time points
                    interpolated_values = self.interpolate_to_times(
                        var2_times, var2.data, target_times, self.__class__.interp_method)
                    
                    # Perform the addition with the interpolated values
                    result_array = var1.data + interpolated_values
                    
                    # Add user-friendly status message
                    print_manager.variable_basic(f"📊 Operation complete: {var1.class_name}.{var1.subclass_name} + {var2.class_name}.{var2.subclass_name}")
                    print_manager.variable_basic(f"   → Interpolated {var2.class_name}.{var2.subclass_name} to match {var1.class_name}.{var1.subclass_name}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
                else:
                    # Use var2's time points as the target (fewer points)
                    target_times = var2_times
                    print_manager.variable_testing(f"Using second array ({var2.class_name}.{var2.subclass_name}) time points as target (fewer points)")
                    print_manager.variable_testing(f"Interpolating {var1.class_name}.{var1.subclass_name} using method: {self.__class__.interp_method}")
                    
                    # Interpolate var1's values to align with var2's time points
                    interpolated_values = self.interpolate_to_times(
                        var1_times, var1.data, target_times, self.__class__.interp_method)
                    
                    # Perform the addition with the interpolated values
                    result_array = interpolated_values + var2.data
                    
                    # Add user-friendly status message
                    print_manager.variable_basic(f"📊 Operation complete: {var1.class_name}.{var1.subclass_name} + {var2.class_name}.{var2.subclass_name}")
                    print_manager.variable_basic(f"   → Interpolated {var1.class_name}.{var1.subclass_name} to match {var2.class_name}.{var2.subclass_name}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
                
                datetime_array = target_times
            else:
                print_manager.variable_testing(f"Invalid number of source variables for add operation: {len(source_vars)}")
                return None
                
        # Other operations would be handled similarly...
        # For brevity, let's just return a result for the add operation
        
        # Create a plot_manager result
        from .ploptions import ploptions
        result_plot_options = ploptions(
            data_type="custom_data_type",
            class_name="custom_class", 
            subclass_name=var_name,
            plot_type="time_series",
            datetime_array=datetime_array,
            y_label=var_name,
            legend_label=var_name
        )
        
        # Create the result using plot_manager
        result_var = plot_manager(result_array, result_plot_options)
        
        # Store the operation type and sources for custom variable container to use
        result_var.operation = operation
        result_var.source_var = source_vars
        if scalar_value is not None:
            result_var.scalar_value = scalar_value
        
        # Use custom_variable to register it
        return custom_variable(var_name, result_var)
    
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