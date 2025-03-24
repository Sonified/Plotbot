"""
Derived Variable support for Plotbot

This module provides the ability to create derived variables by 
applying math operations to existing variables.
"""

import numpy as np
from .print_manager import print_manager
from .plot_manager import plot_manager
from .data_cubby import data_cubby
from .ploptions import ploptions

class DerivedVariable(plot_manager):
    """
    A class for representing derived variables created through mathematical
    operations on existing variables.
    """
    
    def __new__(cls, input_array, plot_options=None, source_var=None, operation=None):
        # Create the object with parent's __new__
        obj = plot_manager.__new__(cls, input_array, plot_options)
        
        # Add derived variable specific attributes
        obj.is_derived = True
        # Use object.__setattr__ instead of direct assignment to avoid boolean evaluation
        object.__setattr__(obj, 'source_var', source_var)
        obj.operation = operation
        
        # Return the new object
        return obj
        
    def __array_finalize__(self, obj):
        """Ensure all attributes are properly maintained during array operations."""
        # First call parent's array_finalize
        super().__array_finalize__(obj)
        
        # Add derived-specific attributes if not already present
        if not hasattr(self, 'is_derived'):
            self.is_derived = getattr(obj, 'is_derived', True)
        
        # FIX: Use object.__setattr__ to avoid triggering boolean evaluation
        if not hasattr(self, 'source_var'):
            source_var_ref = getattr(obj, 'source_var', None)
            object.__setattr__(self, 'source_var', source_var_ref)
            
        if not hasattr(self, 'operation'):
            self.operation = getattr(obj, 'operation', None)
            
        # Copy any color attributes
        if hasattr(obj, 'color') and not hasattr(self, 'color'):
            self.color = getattr(obj, 'color')


# Create a class to hold derived variables separate from the original data classes
class derived_class:
    """
    A container class for derived variables.
    This class has flexible __setattr__ to allow adding any derived variable.
    """
    
    def __init__(self):
        """Initialize an empty container for derived variables."""
        print_manager.variable_testing("Initializing derived class")
        # Stash in data_cubby for later retrieval
        data_cubby.stash(self, class_name='derived')
    
    def get_subclass(self, subclass_name):
        """Get a specific component by name."""
        print_manager.variable_testing(f"Accessing subclass: derived.{subclass_name}")
        if hasattr(self, subclass_name):
            return getattr(self, subclass_name)
        return None
    
    def __getattr__(self, name):
        """Friendly error message for missing attributes."""
        print_manager.variable_testing(f"__getattr__ called for derived.{name}")
        attrs = [attr for attr in dir(self) if not attr.startswith('__')]
        print_manager.variable_testing(f"'{name}' is not a recognized derived variable, friend!")
        if attrs:
            print_manager.variable_testing(f"Try one of these: {', '.join(attrs)}")
        else:
            print_manager.variable_testing("No derived variables have been created yet.")
        return None


def store_derived_variable(result_array, var_name, source_var, operation=None, datetime_array=None, suppress_status=False):
    """
    Store a derived variable in the data_cubby and set up proper attributes.
    
    Parameters
    ----------
    result_array : numpy.ndarray
        The array of values for the derived variable
    var_name : str
        The name to use for the derived variable
    source_var : plot_manager
        The source variable that was used in the operation
    operation : str, optional
        Description of the operation used to create the variable
    datetime_array : array-like, optional
        Explicitly provided datetime array to use for the result (typically from interpolation)
    suppress_status : bool, optional
        If True, don't print the status message (useful when called from store_data)
        
    Returns
    -------
    DerivedVariable
        The newly created derived variable object
    """
    print_manager.variable_testing(f"Creating derived variable: {var_name}")
    
    # Create a copy of the plot options from the source variable
    from copy import deepcopy
    if hasattr(source_var, 'plot_options') and source_var.plot_options is not None:
        plot_options = deepcopy(source_var.plot_options)
    else:
        plot_options = ploptions()
    
    # Set new values for the derived variable in plot_options
    plot_options.data_type = "derived"
    plot_options.class_name = "derived"  # Use our derived class instead of source class
    plot_options.subclass_name = var_name
    
    # SIMPLIFIED DATETIME ARRAY HANDLING:
    # If datetime_array is explicitly provided, use it (after validation)
    if datetime_array is not None:
        print_manager.variable_testing(f"Using explicitly provided datetime_array (length: {len(datetime_array)})")
        
        # Ensure the datetime_array length matches the result_array length
        if len(datetime_array) != len(result_array):
            print_manager.variable_testing(f"WARNING: Provided datetime_array length ({len(datetime_array)}) doesn't match result_array length ({len(result_array)})")
            # Always truncate to the shorter length to ensure consistency
            min_length = min(len(datetime_array), len(result_array))
            datetime_array = datetime_array[:min_length]
            result_array = result_array[:min_length]
            print_manager.variable_testing(f"Truncated both arrays to length: {min_length}")
            
        plot_options.datetime_array = datetime_array
    
    # If no datetime_array is provided, try to use source_var's datetime_array
    elif hasattr(source_var, 'datetime_array'):
        # Check if the lengths match
        if len(source_var.datetime_array) == len(result_array):
            print_manager.variable_testing(f"Using source_var's datetime_array (length: {len(source_var.datetime_array)})")
            plot_options.datetime_array = source_var.datetime_array
        else:
            print_manager.variable_testing(f"WARNING: Source datetime_array length ({len(source_var.datetime_array)}) != result_array length ({len(result_array)})")
            # Truncate the datetime_array to match the result_array length
            min_length = min(len(source_var.datetime_array), len(result_array))
            plot_options.datetime_array = source_var.datetime_array[:min_length]
            result_array = result_array[:min_length]
            print_manager.variable_testing(f"Truncated both arrays to length: {min_length}")
    
    # IMPORTANT: Create a fresh copy of the array to ensure it's distinct
    # This prevents the new array from being treated as the same as the source array
    result_array_copy = np.array(result_array).copy()
    
    # FIX 1: Create a reference to source_var without triggering boolean evaluation
    # Store source_var as a reference, not as a direct attribute to avoid boolean evaluation
    source_var_reference = source_var
    
    # Create the derived variable object
    derived_var = DerivedVariable(
        result_array_copy,
        plot_options=plot_options,
        source_var=None,  # Initially set to None to avoid the boolean evaluation
        operation=operation
    )
    
    # FINAL CHECK: Ensure the datetime_array length matches the data array length
    if len(derived_var.datetime_array) != len(derived_var.data):
        print_manager.variable_testing(f"ERROR: Length mismatch! datetime_array: {len(derived_var.datetime_array)}, data: {len(derived_var.data)}")
        # Create a new datetime_array of the correct length as a last resort
        min_length = min(len(derived_var.datetime_array), len(derived_var.data))
        derived_var.datetime_array = derived_var.datetime_array[:min_length]
        derived_var.data = derived_var.data[:min_length]
        print_manager.variable_testing(f"Fixed by truncating both arrays to length: {min_length}")
    
    # FIX 2: Set source_var after initialization to avoid the boolean error
    # This avoids the "truth value of an array is ambiguous" error
    object.__setattr__(derived_var, 'source_var', source_var_reference)
    
    # IMPORTANT: Explicitly set these attributes to ensure proper plotting
    derived_var.data_type = "derived"
    derived_var.class_name = "derived"
    derived_var.subclass_name = var_name
    
    # Set variable name
    derived_var.var_name = var_name
    
    # Set legend, label, etc.
    if operation:
        derived_var.legend_label = f"{var_name}"  # Simplified name for readability
        derived_var.y_label = f"{var_name}"
    else:
        derived_var.legend_label = var_name
        derived_var.y_label = var_name
    
    # Get or create the derived class instance
    derived_instance = data_cubby.grab('derived')
    if derived_instance is None:
        derived_instance = derived_class()
    
    # Store the derived variable in the derived class
    print_manager.variable_testing(f"Adding {var_name} to derived class")
    setattr(derived_instance, var_name, derived_var)
    
    # Re-stash the derived class
    data_cubby.stash(derived_instance, 'derived')
    
    # Debug: Print all the important attributes to verify they're being set correctly
    print_manager.variable_testing("DERIVED VARIABLE DEBUG INFO:")
    print_manager.variable_testing(f"data_type: {derived_var.data_type}")
    print_manager.variable_testing(f"class_name: {derived_var.class_name}")
    print_manager.variable_testing(f"subclass_name: {derived_var.subclass_name}")
    print_manager.variable_testing(f"shape: {derived_var.shape}")
    print_manager.variable_testing(f"datetime_array length: {len(derived_var.datetime_array) if hasattr(derived_var, 'datetime_array') and derived_var.datetime_array is not None else 'None'}")
    print_manager.variable_testing(f"data array length: {len(derived_var.data)}")
    print_manager.variable_testing(f"operation: {derived_var.operation}")
    
    # Check the first few values to verify operation worked
    if len(derived_var) > 0 and source_var_reference is not None and len(source_var_reference) > 0:
        print_manager.variable_testing(f"  Source first value: {source_var_reference[0]}")
        print_manager.variable_testing(f"  Derived first value: {derived_var[0]}")
        
    # Verify the derived class has our variable
    derived_check = data_cubby.grab('derived')
    if derived_check is not None:
        if hasattr(derived_check, var_name):
            derived_check_var = getattr(derived_check, var_name)
            print_manager.variable_testing(f"Verified that derived.{var_name} exists in data_cubby")
            if hasattr(derived_check_var, 'data_type'):
                print_manager.variable_testing(f"  data_type: {derived_check_var.data_type}")
            if len(derived_check_var) > 0:
                print_manager.variable_testing(f"  First value from derived.{var_name}: {derived_check_var[0]}")
        else:
            print_manager.variable_testing(f"ERROR: derived.{var_name} does not exist in data_cubby!")
    else:
        print_manager.variable_testing("ERROR: derived class not found in data_cubby!")
    
    # Now make this variable accessible in the global scope by its name
    data_cubby.make_globally_accessible(derived_var, var_name)
    
    # STATUS PRINT: Show a user-friendly status message when a new variable is created
    # Use print_manager.variable_basic and report full dimensions
    array_shape = derived_var.shape
    time_points = len(derived_var.datetime_array)
    if not suppress_status:
        if operation:
            print_manager.variable_basic(f"✅ Created result from '{operation}' with size {array_shape} and {time_points} time points\n")
        else:
            print_manager.variable_basic(f"✅ Created derived variable with size {array_shape} and {time_points} time points\n")
    
    return derived_var


def store_data(name, data=None):
    """
    Store data in a derived variable format.
    
    Parameters
    ----------
    name : str
        Name of the variable to store
    data : dict
        Dictionary with 'x' (time array) and 'y' (data array) keys
        
    Returns
    -------
    plot_manager
        The variable that can be used in plotbot calls
    """
    print_manager.variable_testing(f"Store_data called for {name}")
    
    if data is None or not isinstance(data, dict):
        print_manager.variable_testing("Error: data must be a dictionary with 'x' and 'y' keys")
        return None
        
    if 'x' not in data or 'y' not in data:
        print_manager.variable_testing("Error: data must contain 'x' (time array) and 'y' (data values) keys")
        return None
    
    # Get the arrays from the dictionary
    time_array = data['x']
    y_values = data['y']  # This becomes the data property of the plot_manager
    
    print_manager.variable_testing(f"Creating derived variable: {name}")
    
    # ENSURE TIME ARRAY AND DATA ARRAY HAVE MATCHING LENGTHS
    if isinstance(y_values, np.ndarray) and isinstance(time_array, np.ndarray):
        if len(time_array) != len(y_values):
            print_manager.variable_testing(f"WARNING: Time array length ({len(time_array)}) != data array length ({len(y_values)})")
            
            # Adjust the arrays to match in length
            min_length = min(len(time_array), len(y_values))
            time_array = time_array[:min_length] 
            y_values = y_values[:min_length]
            
            print_manager.variable_testing(f"Adjusted both arrays to length: {min_length}")
    
    # Create plot options for the derived variable
    plot_options = ploptions()
    plot_options.data_type = "derived"
    plot_options.class_name = "derived"
    plot_options.subclass_name = name
    plot_options.plot_type = "time_series"
    plot_options.datetime_array = time_array
    plot_options.y_scale = "linear"
    plot_options.y_label = name
    plot_options.legend_label = name
    plot_options.var_name = name
    plot_options.y_limit = None
    plot_options.line_width = 1.0
    plot_options.line_style = "-"
    
    # Check if input is already a DerivedVariable to preserve properties
    if isinstance(y_values, plot_manager) or hasattr(y_values, 'is_derived'):
        # Using the improved store_derived_variable approach
        # with explicit datetime_array passing
        derived_var = store_derived_variable(
            y_values.data,  # Use the data directly
            name,
            y_values,
            operation=f"store_data('{name}')",
            datetime_array=time_array,  # Explicitly pass time_array
            suppress_status=True
        )
        
        # Copy color if it exists
        if hasattr(y_values, 'color'):
            derived_var.color = y_values.color
    else:
        # For non-derived inputs, use the improved store_derived_variable approach
        derived_var = store_derived_variable(
            y_values,
            name,
            None,
            operation=f"store_data('{name}')",
            datetime_array=time_array,  # Explicitly pass time_array
            suppress_status=True
        )
    
    # Print a message confirming the variable can now be used directly
    print_manager.variable_testing(f"Created variable '{name}' - you can now use it directly with plotbot")
    print_manager.variable_testing(f"  Variable dimensions: data length: {len(derived_var.data)}, datetime_array length: {len(derived_var.datetime_array)}")
    if len(derived_var) > 0:
        print_manager.variable_testing(f"  First few values in data: {derived_var.data[:3] if len(derived_var) > 0 else []}")
    
    # Add user-friendly status message
    array_shape = derived_var.shape
    time_points = len(derived_var.datetime_array)
    print_manager.variable_basic(f"✅ Created variable '{name}' with size {array_shape} and {time_points} time points\n")
    
    return derived_var 