"""
Tests for basic arithmetic operations with custom variables.

This file contains tests for addition, subtraction, multiplication, and division 
operations with custom variables, including tests for operator precedence.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_arithmetic.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_arithmetic.py::test_global_variables -v
"""

import numpy as np
import sys
import os
import pytest

# Add the parent directory to the path to import plotbot modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import get_data, mag_rtn_4sa, proton, plt
from plotbot.custom_variables import custom_variable
from plotbot.showdahodo import showdahodo
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby

# Enable debug output
print_manager.show_custom_debug = True
print_manager.show_variable_testing = True
print_manager.show_variable_basic = True

def create_test_variable(name, data, datetime_array=None, class_name="test", subclass_name=None):
    """Create a test variable for testing."""
    if datetime_array is None:
        datetime_array = np.arange(len(data))
        
    options = ploptions(
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

def test_global_variables():
    """Test that variables are accessible globally."""
    var1 = custom_variable('Testing Variable', mag_rtn_4sa.br * 2)
    var2 = custom_variable('Testing Variable 2', mag_rtn_4sa.br - 5)
    
    # Add these variables
    var_sum = var1 + var2
    
    assert var_sum is not None

if __name__ == "__main__":
    print("=== Testing Arithmetic Operations ===")
    
    success = test_global_variables()
    print(f"\nTests {'PASSED' if success else 'FAILED'}") 