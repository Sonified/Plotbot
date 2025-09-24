"""
Plotbot Test Package

This package contains tests for the Plotbot application.
Tests are organized by functionality and can be run
using the run_tests.py script at the project root.

Example usage:
    python run_tests.py                    # Run all tests
    python run_tests.py test_arithmetic.py # Run specific test file
    python run_tests.py test_custom_variables.py::test_create_custom_variable # Run specific test

Test files include:
- test_arithmetic.py: Tests for arithmetic operations on variables
- test_derived.py: Tests for derived variables functionality
- test_global.py: Tests for global variable access
- test_custom_variables.py: Tests for the custom variables system
"""

import os
import sys

# Add parent directory to the Python path for importing plotbot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import common test utilities
try:
    from plotbot.test_pilot import phase, system_check, run_missions
except ImportError:
    # Fallback for when test_pilot is not available
    print("Warning: test_pilot module not available. Some test functionality may be limited.")
    
    def phase(num, description):
        """Print a test phase marker (fallback version)"""
        print(f"--- PHASE {num}: {description} ---")
        
    def system_check(name, condition, message):
        """Check a system condition (fallback version)"""
        if not condition:
            print(f"FAILURE: {message}")
            assert condition, message
        return True
        
    def run_missions(test_module=None, test_name=None):
        """Fallback function when pytest is not installed"""
        print("ERROR: pytest not installed. Please install pytest to run tests:")
        print("  pip install pytest termcolor")
        print("Tests cannot be run without pytest.")
        return 1

# Import common test helper functions
def create_test_variable(name, data, datetime_array=None, class_name="test", subclass_name=None):
    """
    Create a test variable for testing.
    
    This is a utility function used by multiple test modules to create
    plot_manager variables for testing purposes.
    
    Parameters
    ----------
    name : str
        The name of the variable
    data : array-like
        The data array for the variable
    datetime_array : array-like, optional
        The time array for the variable (defaults to range(len(data)))
    class_name : str, optional
        The class name for the variable (defaults to "test")
    subclass_name : str, optional
        The subclass name for the variable (defaults to name)
        
    Returns
    -------
    plot_manager
        A plot_manager instance with the specified data and properties
    """
    import numpy as np
    from plotbot.plot_config import plot_config
    from plotbot.plot_manager import plot_manager
    from plotbot.data_cubby import data_cubby
    
    if datetime_array is None:
        datetime_array = np.arange(len(data))
        
    options = plot_config(
        data_type="test",
        class_name=class_name,
        subclass_name=subclass_name or name,
        plot_type="time_series",
        datetime_array=datetime_array,
        y_label=name,
        legend_label=name,
        color='blue',
        y_scale='linear'
    )
    var = plot_manager(data, options)
    
    # Store in data_cubby
    class_obj = data_cubby.grab(class_name)
    if class_obj is None:
        class_obj = type('TestClass', (), {'get_subclass': lambda self, name: getattr(self, name, None)})()
        data_cubby.stash(class_obj, class_name=class_name)
    
    setattr(class_obj, subclass_name or name, var)
    
    return var 