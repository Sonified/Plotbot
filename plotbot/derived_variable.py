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
        obj.source_var = source_var
        obj.operation = operation
        
        # Return the new object
        return obj
        
    def __array_finalize__(self, obj):
        # First call parent's array_finalize
        super().__array_finalize__(obj)
        
        # Add derived-specific attributes if not already present
        if not hasattr(self, 'is_derived'):
            self.is_derived = getattr(obj, 'is_derived', True)
        if not hasattr(self, 'source_var'):
            self.source_var = getattr(obj, 'source_var', None)
        if not hasattr(self, 'operation'):
            self.operation = getattr(obj, 'operation', None)


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


def store_derived_variable(result_array, var_name, source_var, operation=None):
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
    # Set datetime array directly in plot_options
    if hasattr(source_var, 'datetime_array'):
        plot_options.datetime_array = source_var.datetime_array
    
    # IMPORTANT: Create a fresh copy of the array to ensure it's distinct
    # This prevents the new array from being treated as the same as the source array
    result_array_copy = np.array(result_array).copy()
    
    # Create the derived variable object
    derived_var = DerivedVariable(
        result_array_copy,
        plot_options=plot_options,
        source_var=None,  # Set to None initially
        operation=operation
    )
    
    # Add source_var to _plot_state directly instead of using the property
    if not hasattr(derived_var, '_plot_state'):
        derived_var._plot_state = {}
    derived_var._plot_state['source_var'] = source_var
    
    # IMPORTANT: Explicitly set these attributes to ensure proper plotting
    derived_var.data_type = "derived"
    derived_var.class_name = "derived"
    derived_var.subclass_name = var_name
    
    # Set variable name
    derived_var.var_name = var_name
    
    # Set legend, label, etc.
    if operation:
        derived_var.legend_label = f"{var_name} ({operation})"
        derived_var.y_label = f"{var_name} ({operation})"
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
    print_manager.variable_testing(f"datetime_array length: {len(derived_var.datetime_array) if hasattr(derived_var, 'datetime_array') else 'None'}")
    print_manager.variable_testing("is derived array 100x larger? First value comparison:")
    
    # Check the first few values to verify multiplication worked
    if len(derived_var) > 0 and source_var is not None and len(source_var) > 0:
        print_manager.variable_testing(f"  Source first value: {source_var[0]}")
        print_manager.variable_testing(f"  Derived first value: {derived_var[0]}")
        if derived_var[0] != source_var[0] * 100 and operation and "100" in operation:
            print_manager.variable_testing(f"  MISMATCH! Expected {source_var[0] * 100}, got {derived_var[0]}")
        
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
    
    print_manager.variable_testing(f"Created derived variable {var_name} successfully")
    
    # Now make this variable accessible in the global scope by its name
    data_cubby.make_globally_accessible(derived_var, var_name)
    
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
    
    # Create the plot_manager instance with the data array
    # y_values becomes the data property of the plot_manager
    derived_var = plot_manager(y_values, plot_options)
    
    # Flag as derived variable
    derived_var.is_derived = True
    
    # Get the derived class instance and add this variable
    derived_instance = data_cubby.grab('derived')
    if derived_instance is None:
        derived_instance = derived_class()
        data_cubby.stash(derived_instance, 'derived')
    
    # Add the variable to the derived class and stash in data_cubby
    setattr(derived_instance, name, derived_var)
    print_manager.variable_testing(f"Adding {name} to derived class")
    data_cubby.stash(derived_instance, 'derived')
    
    # Add to global scope for easy access
    import builtins
    setattr(builtins, name, derived_var)
    
    # Print a message confirming the variable can now be used directly
    print_manager.variable_testing(f"Created variable '{name}' - you can now use it directly with plotbot")
    print_manager.variable_testing(f"  First few values in data: {derived_var.data[:3] if len(derived_var) > 0 else []}")
    
    return derived_var 