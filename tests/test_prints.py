# tests/test_prints.py
"""
Test script to track down print statement sources.

This script helps debug where various print statements are coming from
by setting up trace points and running key operations.

NOTES ON TEST OUTPUT:
- Use print_manager.test() for any debug information you want to see in test output
- Use print_manager.debug() for developer-level debugging details
- To see all print statements in test output, add the -s flag when running pytest:
  e.g., cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_prints.py -v -s

To run this test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_prints.py -v -s
"""

import sys
import inspect
import os
import traceback

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Plotbot modules
from plotbot.print_manager import print_manager
from plotbot.custom_variables import custom_variable
from plotbot import mag_rtn_4sa, proton

# Setup printing configuration
print_manager.show_module_prefix = False
print_manager.show_category_prefix = False
print_manager.enable_test()
print_manager.enable_debug()

# Override the warning method to show the source location
original_warning = print_manager.warning

def debug_warning(msg):
    """Enhanced warning method that shows call site information."""
    # Get the caller information
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno
    func_name = frame.f_code.co_name
    
    # Print the warning along with the call site
    print_manager.test("TRACE: {}:{} in {}()".format(filename, lineno, func_name))
    original_warning(msg)

# Install our debug warning function
print_manager.warning = debug_warning

def test_print_sources():
    """Test to track print statement sources"""
    # Test 1: Create a custom variable and see what prints
    print_manager.test("\n--- TEST 1: Creating custom variable ---")
    time_range = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    test_var = custom_variable('TestVar', proton.anisotropy / mag_rtn_4sa.bmag)

    # Test 2: Set various attributes
    print_manager.test("\n--- TEST 2: Setting attributes ---")
    test_var.color = 'red'
    test_var.line_style = '-'
    test_var.line_width = 2
    test_var.marker = 'o'       # Not in PLOT_ATTRIBUTES
    test_var.marker_size = 5    # Not in PLOT_ATTRIBUTES
    test_var.alpha = 0.7        # Not in PLOT_ATTRIBUTES
    test_var.zorder = 10        # Not in PLOT_ATTRIBUTES
    test_var.legend_label_override = "Test"  # Not in PLOT_ATTRIBUTES

    print_manager.test("\n--- COMPLETED TESTS ---")

    # Print a list of attributes in plot_manager.PLOT_ATTRIBUTES
    from plotbot.plot_manager import plot_manager
    print_manager.test("\nRecognized plot attributes (PLOT_ATTRIBUTES):")
    for attr in plot_manager.PLOT_ATTRIBUTES:
        print_manager.test("  - {}".format(attr))

    print_manager.test("\nSuggested fixes:")
    print_manager.test("1. Add missing attributes to the PLOT_ATTRIBUTES list in plot_manager.py")
    print_manager.test("2. Or, silence these warnings by setting print_manager.show_warnings = False")
    
    # Simple assertion to make the test pass
    assert True

if __name__ == "__main__":
    test_print_sources() 