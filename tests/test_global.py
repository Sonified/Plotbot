"""
Tests for global variable access in Plotbot.

This file contains tests for accessing and manipulating global variables.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_global.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_global.py::test_global_variables -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
import os
import sys
import inspect
from plotbot.print_manager import print_manager

def test_global_variables():
    """Minimal test for the global variable functionality."""
    print_manager.show_variable_testing = True
    print_manager.show_variable_basic = True
    
    # Creating a dynamic attribute on the module
    mod = sys.modules[__name__]
    setattr(mod, 'test_value', 42)
    
    # Dynamic module attributes
    assert mod.test_value == 42
    
    # Test from inside a function
    assert test_global_variables.__module__ == "__main__"

    # Create a global variable
    global global_test_var 
    global_test_var = np.array([1, 2, 3])
    
    # Check the global variable
    assert len(global_test_var) == 3
    assert np.all(global_test_var == np.array([1, 2, 3])) 