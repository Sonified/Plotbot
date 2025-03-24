# 🎉 Extend numpy.ndarray with plotting functionality and friendly error handling 🎉
#SAFE! 

import numpy as np
import matplotlib.pyplot as plt
from .ploptions import ploptions
from .print_manager import print_manager
from .data_cubby import data_cubby

class plot_manager(np.ndarray):
    
    PLOT_ATTRIBUTES = [
        'data', 'data_type', 'var_name', 'class_name', 'subclass_name', 'plot_type', 'datetime_array', 
        'y_label', 'legend_label', 'color', 'y_scale', 'y_limit', 'line_width',
        'line_style', 'colormap', 'colorbar_scale', 'colorbar_limits',
        'additional_data', 'colorbar_label', 'is_derived', 'source_var', 'operation'
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
        
        print_manager.variable_testing(f"Starting interpolation with method: {method}")
        print_manager.variable_testing(f"Source times length: {len(source_times)}, Target times length: {len(target_times)}")
        
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

    def __add__(self, other):
        """Add two plot_manager objects with time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Adding {self.class_name}.{self.subclass_name} and {other.class_name}.{other.subclass_name}")
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
                    import numpy as np
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
                
                # Perform the addition with the interpolated values
                result_array = self.data + interpolated_values
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
                
                # Perform the addition with the interpolated values
                result_array = interpolated_values + other.data
            
            print_manager.variable_testing(f"Addition complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} + {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} + {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar or array addition
            result_array = self.data + other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} + {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} + {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __sub__(self, other):
        """Subtract two plot_manager objects with time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Subtracting {other.class_name}.{other.subclass_name} from {self.class_name}.{self.subclass_name}")
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
                    import numpy as np
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
                
                # Perform the subtraction with the interpolated values
                result_array = self.data - interpolated_values
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
                
                # Perform the subtraction with the interpolated values
                result_array = interpolated_values - other.data
            
            print_manager.variable_testing(f"Subtraction complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} - {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} - {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar or array subtraction
            result_array = self.data - other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} - {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} - {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __mul__(self, other):
        """Multiply two plot_manager objects with time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Multiplying {self.class_name}.{self.subclass_name} and {other.class_name}.{other.subclass_name}")
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
                    import numpy as np
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
                
                # Perform the multiplication with the interpolated values
                result_array = self.data * interpolated_values
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
                
                # Perform the multiplication with the interpolated values
                result_array = interpolated_values * other.data
            
            print_manager.variable_testing(f"Multiplication complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} * {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} * {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar or array multiplication
            result_array = self.data * other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} * {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} * {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __truediv__(self, other):
        """Divide two plot_manager objects with time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Dividing {self.class_name}.{self.subclass_name} by {other.class_name}.{other.subclass_name}")
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
                    import numpy as np
                    self_cadence = (self_times[1] - self_times[0]) / np.timedelta64(1, 's')
                    other_cadence = (other_times[1] - other_times[0]) / np.timedelta64(1, 's')
                
                print_manager.variable_testing(f"First array sampling cadence: {self_cadence} seconds")
                print_manager.variable_testing(f"Second array sampling cadence: {other_cadence} seconds")
            
            # Import numpy for handling division by zero
            import numpy as np
            
            # Determine which variable has fewer time points to use as target
            if len(self_times) <= len(other_times):
                # Use self's time points as the target (fewer points)
                target_times = self_times
                target_var = first_var
                interpolated_var = second_var
                print_manager.variable_testing(f"Using first array ({self.class_name}.{self.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {other.class_name}.{other.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate other's values to align with self's time points
                interpolated_other = self.interpolate_to_times(
                    other_times, other.data, target_times, self.__class__.interp_method)
                
                # Avoid division by zero
                interpolated_other = np.where(interpolated_other == 0, np.nan, interpolated_other)
                
                # Perform the division with the interpolated values
                result_array = self.data / interpolated_other
            else:
                # Use other's time points as the target (fewer points)
                target_times = other_times
                target_var = second_var
                interpolated_var = first_var
                print_manager.variable_testing(f"Using second array ({other.class_name}.{other.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {self.class_name}.{self.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate self's values to align with other's time points
                interpolated_self = self.interpolate_to_times(
                    self_times, self.data, target_times, self.__class__.interp_method)
                
                # Avoid division by zero
                other_data = np.where(other.data == 0, np.nan, other.data)
                
                # Perform the division with the interpolated values
                result_array = interpolated_self / other_data
            
            print_manager.variable_testing(f"Division complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} / {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method")
            print_manager.variable_basic(f"   → Any division by zero has been replaced with NaN values\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} / {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar or array division
            result_array = self.data / other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} / {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} / {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __pow__(self, other):
        """Handle exponentiation (power) with automatic time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Calculating {self.class_name}.{self.subclass_name} raised to power of {other.class_name}.{other.subclass_name}")
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
                    import numpy as np
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
                
                # Perform the exponentiation with the interpolated values
                result_array = self.data ** interpolated_values
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
                
                # Perform the exponentiation with the interpolated values
                result_array = interpolated_values ** other.data
            
            print_manager.variable_testing(f"Exponentiation complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} ** {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} ** {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar exponentiation
            result_array = self.data ** other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} ** {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} ** {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __neg__(self):
        """Handle negation."""
        print_manager.variable_testing(f"Negating {self.class_name}.{self.subclass_name}")
        
        result_array = -self.data
        
        # STATUS PRINT: Show operation details for __neg__
        print_manager.variable_basic(f"📊 Operation complete: -{self.class_name}.{self.subclass_name}")
        print_manager.variable_basic(f"   → Unary operation (no interpolation needed)\n")
        
        # Create new plot_manager with the result
        from .derived_variable import store_derived_variable
        operation = f"-{self.class_name}.{self.subclass_name}"
        
        # IMPROVED: Explicitly pass our datetime_array to ensure consistency
        return store_derived_variable(
            result_array,
            operation,
            self,
            operation,
            datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
            suppress_status=True  # Suppress redundant status message
        )

    def __abs__(self):
        """Handle absolute value."""
        print_manager.variable_testing(f"Taking absolute value of {self.class_name}.{self.subclass_name}")
        
        result_array = abs(self.data)
        
        # STATUS PRINT: Show operation details for __abs__
        print_manager.variable_basic(f"📊 Operation complete: abs({self.class_name}.{self.subclass_name})")
        print_manager.variable_basic(f"   → Unary operation (no interpolation needed)\n")
        
        # Create new plot_manager with the result
        from .derived_variable import store_derived_variable
        operation = f"abs({self.class_name}.{self.subclass_name})"
        
        # IMPROVED: Explicitly pass our datetime_array to ensure consistency
        return store_derived_variable(
            result_array,
            operation,
            self,
            operation,
            datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
            suppress_status=True  # Suppress redundant status message
        )

    def __floordiv__(self, other):
        """Handle floor division with automatic time alignment."""
        if isinstance(other, plot_manager):
            # Get datetime arrays
            self_times = self.datetime_array
            other_times = other.datetime_array
            
            print_manager.variable_testing(f"Floor dividing {self.class_name}.{self.subclass_name} by {other.class_name}.{other.subclass_name}")
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
                    import numpy as np
                    self_cadence = (self_times[1] - self_times[0]) / np.timedelta64(1, 's')
                    other_cadence = (other_times[1] - other_times[0]) / np.timedelta64(1, 's')
                
                print_manager.variable_testing(f"First array sampling cadence: {self_cadence} seconds")
                print_manager.variable_testing(f"Second array sampling cadence: {other_cadence} seconds")
            
            # Import numpy for handling division by zero
            import numpy as np
            
            # Determine which variable has fewer time points to use as target
            if len(self_times) <= len(other_times):
                # Use self's time points as the target (fewer points)
                target_times = self_times
                target_var = first_var
                interpolated_var = second_var
                print_manager.variable_testing(f"Using first array ({self.class_name}.{self.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {other.class_name}.{other.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate other's values to align with self's time points
                interpolated_other = self.interpolate_to_times(
                    other_times, other.data, target_times, self.__class__.interp_method)
                
                # Avoid division by zero
                interpolated_other = np.where(interpolated_other == 0, np.nan, interpolated_other)
                
                # Perform the floor division with the interpolated values
                result_array = self.data // interpolated_other
            else:
                # Use other's time points as the target (fewer points)
                target_times = other_times
                target_var = second_var
                interpolated_var = first_var
                print_manager.variable_testing(f"Using second array ({other.class_name}.{other.subclass_name}) time points as target (fewer points)")
                print_manager.variable_testing(f"Interpolating {self.class_name}.{self.subclass_name} using method: {self.__class__.interp_method}")
                
                # Interpolate self's values to align with other's time points
                interpolated_self = self.interpolate_to_times(
                    self_times, self.data, target_times, self.__class__.interp_method)
                
                # Avoid division by zero
                other_data = np.where(other.data == 0, np.nan, other.data)
                
                # Perform the floor division with the interpolated values
                result_array = interpolated_self // other_data
            
            print_manager.variable_testing(f"Floor division complete. Result length: {len(result_array)}")
            
            # STATUS PRINT: Show interpolation details after the operation is complete
            print_manager.variable_basic(f"📊 Operation complete: {first_var} // {second_var}")
            print_manager.variable_basic(f"   → Interpolated {interpolated_var} to match {target_var}'s {len(target_times)} time points using '{self.__class__.interp_method}' method")
            print_manager.variable_basic(f"   → Any division by zero has been replaced with NaN values\n")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} // {other.class_name}.{other.subclass_name}"
            
            # IMPROVED: Explicitly pass the target_times to store_derived_variable
            # This ensures the datetime_array matches the result_array exactly
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=target_times,  # Explicitly pass the datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        else:
            # Handle scalar floor division
            result_array = self.data // other
            
            # STATUS PRINT: Show operation complete message for scalar operation (no interpolation)
            print_manager.variable_basic(f"📊 Operation complete: {self.class_name}.{self.subclass_name} // {other}")
            print_manager.variable_basic(f"   → No interpolation needed for scalar operation")
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{self.class_name}.{self.subclass_name} // {other}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Use our own datetime_array for scalar operations
                suppress_status=True  # Suppress redundant status message
            )

    def __radd__(self, other):
        """Handle right-sided addition (other + self)."""
        # For scalar + plot_manager
        print_manager.variable_testing(f"Right-sided addition: {other} + {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            result_array = other + self.data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} + {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it

    def __rsub__(self, other):
        """Handle right-sided subtraction (other - self)."""
        # For scalar - plot_manager
        print_manager.variable_testing(f"Right-sided subtraction: {other} - {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            result_array = other - self.data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} - {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it

    def __rmul__(self, other):
        """Handle right-sided multiplication (other * self)."""
        # For scalar * plot_manager
        print_manager.variable_testing(f"Right-sided multiplication: {other} * {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            result_array = other * self.data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} * {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it

    def __rtruediv__(self, other):
        """Handle right-sided division (other / self)."""
        # For scalar / plot_manager
        print_manager.variable_testing(f"Right-sided division: {other} / {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            # Avoid division by zero
            import numpy as np
            safe_data = np.where(self.data == 0, np.nan, self.data)
            result_array = other / safe_data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} / {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it

    def __rpow__(self, other):
        """Handle right-sided power (other ** self)."""
        # For scalar ** plot_manager
        print_manager.variable_testing(f"Right-sided power: {other} ** {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            result_array = other ** self.data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} ** {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it

    def __rfloordiv__(self, other):
        """Handle right-sided floor division (other // self)."""
        # For scalar // plot_manager
        print_manager.variable_testing(f"Right-sided floor division: {other} // {self.class_name}.{self.subclass_name}")
        
        if not isinstance(other, plot_manager):
            # Avoid division by zero
            import numpy as np
            safe_data = np.where(self.data == 0, np.nan, self.data)
            result_array = other // safe_data
            
            # Create new plot_manager with the result
            from .derived_variable import store_derived_variable
            operation = f"{other} // {self.class_name}.{self.subclass_name}"
            
            # IMPROVED: Explicitly pass our datetime_array to ensure consistency
            return store_derived_variable(
                result_array,
                operation,
                self,
                operation,
                datetime_array=self.datetime_array,  # Explicitly pass our datetime_array
                suppress_status=True  # Suppress redundant status message
            )
        return NotImplemented  # Let the left operand handle it
    
print('initialized plot_manager')