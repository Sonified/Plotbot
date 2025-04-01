# tests/test_multiplot.py
"""
Tests for the multiplot functionality in Plotbot.

This file contains tests for creating multi-panel plots with various configurations,
including standard variables, custom variables, and different plot types.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot.py::test_multiplot_single_custom_variable -v
"""
import pytest
import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plotbot import mag_rtn_4sa, proton, plt
from plotbot.custom_variables import custom_variable
from plotbot.multiplot import multiplot
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.data_import import import_data_function
from plotbot.data_tracker import global_tracker

# Add the tests directory to sys.path
sys.path.append(os.path.dirname(__file__))

# Import the record_test_result function from conftest
try:
    from conftest import record_test_result
except ImportError:
    # Fallback in case import fails
    def record_test_result(test_name, check):
        pass

# Global test status dictionary
test_results = {}

# Store original system_check and phase functions
original_system_check = system_check
original_phase = phase

# Wrapper for system_check that records results without recursion
def record_system_check(description, condition, message):
    """Record system check results in summary"""
    # Store the result for the current test
    current_test = pytest._current_test_name if hasattr(pytest, '_current_test_name') else "Unknown Test"
    
    # Record test result
    record_test_result(current_test, {
        "description": description,
        "result": "PASS" if condition else "FAIL",
        "message": message
    })
    
    # Call the original system_check directly
    return system_check(description, condition, message)

# Add a pytest hook to capture the current test name
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    pytest._current_test_name = item.name

# Add a summary function to display all test results
def print_test_summary():
    """Print a colored summary of all test results at the end"""
    print("\n" + "="*80)
    print("🔍 TEST SUMMARY 🔍".center(80))
    print("="*80)
    
    all_passed = True
    
    for test_name, checks in test_results.items():
        # Count passes and fails
        passes = sum(1 for check in checks if check["result"] == "PASS")
        fails = len(checks) - passes
        
        # Determine test status
        if fails == 0:
            status = "✅ PASSED"
            color = "\033[92m"  # Green
        elif passes > 0:
            status = "⚠️ PARTIAL"
            color = "\033[93m"  # Yellow
            all_passed = False
        else:
            status = "❌ FAILED"
            color = "\033[91m"  # Red
            all_passed = False
        
        # Print test name and status with color
        print(f"{color}{test_name:<60} {status}\033[0m")
        
        # Print details of each check
        for check in checks:
            check_status = "✅" if check["result"] == "PASS" else "❌"
            check_color = "\033[92m" if check["result"] == "PASS" else "\033[91m"
            print(f"  {check_color}{check_status} {check['description']}\033[0m")
    
    print("="*80)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"
    overall_color = "\033[92m" if all_passed else "\033[91m"
    print(f"{overall_color}{overall_status}\033[0m".center(90))
    print("="*80 + "\n")

# Register the summary function to run after all tests
@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    print_test_summary()

@pytest.fixture
def test_environment():
    """Test environment with exact perihelion times from encounters"""
    return {
        'encounters': [
            {'perihelion': '2023/09/27 23:28:00.000'},  # Enc 17
            {'perihelion': '2023/12/29 00:56:00.000'},  # Enc 18
            {'perihelion': '2024/03/30 02:21:00.000'},  # Enc 19
        ],
    }

def setup_plot_options():
    """Set up common plot options"""
    plt.options.reset()  # Reset options to ensure a clean slate
    
    # Plot setup
    plt.options.width = 15
    plt.options.height_per_panel = 1
    
    # Title and labels
    plt.options.use_single_title = True
    plt.options.single_title_text = "Testing PSP FIELDS data around Perihelion For Multiple Encounters"
    plt.options.y_label_uses_encounter = True
    plt.options.y_label_includes_time = False
    
    # Vertical line
    plt.options.draw_vertical_line = True
    plt.options.vertical_line_width = 1.5
    
    # Time settings
    plt.options.use_relative_time = True
    plt.options.relative_time_step_units = 'minutes'
    plt.options.relative_time_step = 30
    
    # Window settings
    plt.options.window = '6:00:00.000'
    plt.options.position = 'around'  # Position options: 'before', 'after', 'around'

@pytest.mark.mission("Options Reset")
def test_options_reset():
    """Test that plt.options.reset() properly resets all options to defaults"""
    
    print("\n================================================================================")
    print("TEST #4: Options Reset Test")
    print("Verifies that options.reset() properly resets all multiplot options")
    print("================================================================================\n")
    
    phase(1, "Getting default options and setting custom values")
    # First make sure we have a clean slate
    plt.options.reset()
    
    # Get default values
    default_width = plt.options.width
    default_height = plt.options.height_per_panel
    default_title = plt.options.single_title_text
    default_window = plt.options.window
    default_position = plt.options.position
    default_use_single_title = plt.options.use_single_title
    default_draw_vertical = plt.options.draw_vertical_line
    
    # Set custom values
    custom_width = 14 if default_width != 14 else 15
    custom_height = 4 if default_height != 4 else 5
    custom_title = "Custom Test Title"
    custom_window = "0 days 12:00:00" if default_window != "0 days 12:00:00" else "0 days 06:00:00" 
    custom_position = "before" if default_position != "before" else "after"
    custom_use_single_title = not default_use_single_title
    custom_draw_vertical = not default_draw_vertical
    
    plt.options.width = custom_width
    plt.options.height_per_panel = custom_height
    plt.options.single_title_text = custom_title
    plt.options.window = custom_window
    plt.options.position = custom_position
    plt.options.use_single_title = custom_use_single_title
    plt.options.draw_vertical_line = custom_draw_vertical
    
    # Verify that each custom value is actually different from its default
    # Record test results for summary
    record_test_result("test_options_reset", {
        "description": "Width changed",
        "result": "PASS" if custom_width != default_width else "FAIL",
        "message": f"Custom width ({custom_width}) should be different from default ({default_width})"
    })
    system_check("Width changed",
                custom_width != default_width,
                f"Custom width ({custom_width}) should be different from default ({default_width})")
    
    record_test_result("test_options_reset", {
        "description": "Height changed",
        "result": "PASS" if custom_height != default_height else "FAIL",
        "message": f"Custom height ({custom_height}) should be different from default ({default_height})"
    })
    system_check("Height changed",
                custom_height != default_height,
                f"Custom height ({custom_height}) should be different from default ({default_height})")
    
    record_test_result("test_options_reset", {
        "description": "Title changed",
        "result": "PASS" if custom_title != default_title else "FAIL",
        "message": "Custom title should be different from default"
    })
    system_check("Title changed",
                custom_title != default_title,
                f"Custom title should be different from default")
    
    record_test_result("test_options_reset", {
        "description": "Window changed",
        "result": "PASS" if custom_window != default_window else "FAIL",
        "message": f"Custom window ({custom_window}) should be different from default ({default_window})"
    })
    system_check("Window changed",
                custom_window != default_window,
                f"Custom window ({custom_window}) should be different from default ({default_window})")
    
    record_test_result("test_options_reset", {
        "description": "Position changed",
        "result": "PASS" if custom_position != default_position else "FAIL",
        "message": f"Custom position ({custom_position}) should be different from default ({default_position})"
    })
    system_check("Position changed",
                custom_position != default_position,
                f"Custom position ({custom_position}) should be different from default ({default_position})")
    
    record_test_result("test_options_reset", {
        "description": "Use single title changed",
        "result": "PASS" if custom_use_single_title != default_use_single_title else "FAIL",
        "message": f"Custom use_single_title ({custom_use_single_title}) should be different from default ({default_use_single_title})"
    })
    system_check("Use single title changed",
                custom_use_single_title != default_use_single_title,
                f"Custom use_single_title ({custom_use_single_title}) should be different from default ({default_use_single_title})")
                
    record_test_result("test_options_reset", {
        "description": "Draw vertical line changed",
        "result": "PASS" if custom_draw_vertical != default_draw_vertical else "FAIL",
        "message": f"Custom draw_vertical_line ({custom_draw_vertical}) should be different from default ({default_draw_vertical})"
    })
    system_check("Draw vertical line changed",
                custom_draw_vertical != default_draw_vertical,
                f"Custom draw_vertical_line ({custom_draw_vertical}) should be different from default ({default_draw_vertical})")
    
    phase(2, "Resetting options")
    # Now reset the options
    plt.options.reset()
    
    phase(3, "Verifying reset worked correctly")
    # Verify options are reset to their default values
    record_test_result("test_options_reset", {
        "description": "Width reset",
        "result": "PASS" if plt.options.width == default_width else "FAIL",
        "message": f"Width should be reset to {default_width}, got {plt.options.width}"
    })
    system_check("Width reset",
                plt.options.width == default_width,
                f"Width should be reset to {default_width}, got {plt.options.width}")
    
    record_test_result("test_options_reset", {
        "description": "Height reset",
        "result": "PASS" if plt.options.height_per_panel == default_height else "FAIL",
        "message": f"Height should be reset to {default_height}, got {plt.options.height_per_panel}"
    })
    system_check("Height reset",
                plt.options.height_per_panel == default_height,
                f"Height should be reset to {default_height}, got {plt.options.height_per_panel}")
    
    record_test_result("test_options_reset", {
        "description": "Title reset",
        "result": "PASS" if plt.options.single_title_text == default_title else "FAIL",
        "message": f"Title should be reset to default, got {plt.options.single_title_text}"
    })
    system_check("Title reset",
                plt.options.single_title_text == default_title,
                f"Title should be reset to default, got {plt.options.single_title_text}")
    
    record_test_result("test_options_reset", {
        "description": "Window reset",
        "result": "PASS" if plt.options.window == default_window else "FAIL",
        "message": f"Window should be reset to default, got {plt.options.window}"
    })
    system_check("Window reset",
                plt.options.window == default_window,
                f"Window should be reset to default, got {plt.options.window}")
    
    record_test_result("test_options_reset", {
        "description": "Position reset",
        "result": "PASS" if plt.options.position == default_position else "FAIL",
        "message": f"Position should be reset to {default_position}, got {plt.options.position}"
    })
    system_check("Position reset",
                plt.options.position == default_position,
                f"Position should be reset to {default_position}, got {plt.options.position}")
    
    record_test_result("test_options_reset", {
        "description": "Use single title reset",
        "result": "PASS" if plt.options.use_single_title == default_use_single_title else "FAIL",
        "message": f"use_single_title should be reset to {default_use_single_title}, got {plt.options.use_single_title}"
    })
    system_check("Use single title reset",
                plt.options.use_single_title == default_use_single_title,
                f"use_single_title should be reset to {default_use_single_title}, got {plt.options.use_single_title}")
                
    record_test_result("test_options_reset", {
        "description": "Draw vertical line reset",
        "result": "PASS" if plt.options.draw_vertical_line == default_draw_vertical else "FAIL",
        "message": f"draw_vertical_line should be reset to {default_draw_vertical}, got {plt.options.draw_vertical_line}"
    })
    system_check("Draw vertical line reset",
                plt.options.draw_vertical_line == default_draw_vertical,
                f"draw_vertical_line should be reset to {default_draw_vertical}, got {plt.options.draw_vertical_line}")

@pytest.mark.mission("Multiplot with Single Custom Variable")
def test_multiplot_single_custom_variable(test_environment):
    """Test multiplot with a single custom variable"""
    
    print("\n================================================================================")
    print("TEST #5: Multiplot with Single Custom Variable")
    print("Tests that multiplot works with a single custom variable")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Creating custom variable")
    # Create a simple custom variable without getting data first
    ta_over_b = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.color = 'red'
    ta_over_b.line_style = '--'
    
    # Print diagnostic information about the variable
    print_manager.test(f"✅ Custom variable created with name: {getattr(ta_over_b, 'subclass_name', 'Unknown')}")
    print_manager.test(f"🔍 DIAGNOSTIC - Variable attributes:")
    print_manager.test(f"  - Type: {type(ta_over_b)}")
    print_manager.test(f"  - Has data_type: {hasattr(ta_over_b, 'data_type')}")
    if hasattr(ta_over_b, 'data_type'):
        print_manager.test(f"  - data_type: {ta_over_b.data_type}")
    print_manager.test(f"  - Has class_name: {hasattr(ta_over_b, 'class_name')}")
    if hasattr(ta_over_b, 'class_name'):
        print_manager.test(f"  - class_name: {ta_over_b.class_name}")
    print_manager.test(f"  - Has subclass_name: {hasattr(ta_over_b, 'subclass_name')}")
    if hasattr(ta_over_b, 'subclass_name'):
        print_manager.test(f"  - subclass_name: {ta_over_b.subclass_name}")
    print_manager.test(f"  - Has is_derived: {hasattr(ta_over_b, 'is_derived')}")
    if hasattr(ta_over_b, 'is_derived'):
        print_manager.test(f"  - is_derived: {ta_over_b.is_derived}")
    print_manager.test(f"  - Has operation_str: {hasattr(ta_over_b, 'operation_str')}")
    if hasattr(ta_over_b, 'operation_str'):
        print_manager.test(f"  - operation_str: {ta_over_b.operation_str}")
    
    phase(2, "Setting up options and creating multiplot with custom variable")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set title for this test
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #5: Multiplot with Single Custom Variable"
        
        # Create the plot data list using list comprehension
        # Use only the most recent encounter to increase chances of data availability
        last_encounter = env['encounters'][-1]
        plot_data = [(last_encounter['perihelion'], ta_over_b)]
        
        # Print information about our data_cubby before calling multiplot
        print_manager.test(f"🔍 DIAGNOSTIC - Checking data_cubby for derived container")
        from plotbot.data_cubby import data_cubby
        derived_container = data_cubby.grab('derived')
        if derived_container is not None:
            print_manager.test(f"  - Derived container found")
            
            # Check for our variable in the container
            if hasattr(derived_container, 'TAoverB'):
                print_manager.test(f"  - 'TAoverB' found in derived container")
            else:
                print_manager.test(f"  - 'TAoverB' NOT found in derived container")
                
            # List available variables
            print_manager.test(f"  - Available variables in derived container:")
            for attr in dir(derived_container):
                if not attr.startswith('__'):
                    print_manager.test(f"      {attr}")
        else:
            print_manager.test(f"  - No derived container found in data_cubby")
        
        print_manager.test(f"🔍 DIAGNOSTIC - About to call multiplot...")
        
        # Create multiplot - returns a tuple of (fig, axs)
        fig, axs = multiplot(plot_data)
        
        # Check that there's actual data in the plot
        # This requires checking if we have any line objects in the axes
        has_plotted_data = False
        if len(axs) > 0:
            # Get the lines in the first axes
            lines = axs[0].get_lines()
            has_plotted_data = len(lines) > 0
            print_manager.test(f"🔍 Plot has {len(lines)} data lines")
        
        # Record the complete result
        record_test_result("test_multiplot_single_custom_variable", {
            "description": "Multiplot Creation",
            "result": "PASS" if fig is not None and has_plotted_data else "FAIL",
            "message": f"Multiplot should be created with plotted data. Has data: {has_plotted_data}"
        })
        
        system_check("Multiplot Creation", 
                    fig is not None and has_plotted_data, 
                    "Multiplot should be created with plotted data")
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create/update multiplot: {str(e)}")

@pytest.mark.mission("Multiplot with Same-Rate Custom Variable")
def test_multiplot_same_rate_custom(test_environment):
    """Test multiplot with a custom variable derived from same-rate sources"""
    
    print("\n================================================================================")
    print("TEST #6: Multiplot with Same-Rate Custom Variable")
    print("Tests multiplot with a custom variable derived from same-rate sources")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Creating custom variable with same sampling rate sources")
    # Create a custom variable from components with the same sampling rate
    br_plus_bt = custom_variable('BrPlusBt', mag_rtn_4sa.br + mag_rtn_4sa.bt)
    br_plus_bt.color = 'green'
    br_plus_bt.y_label = 'Br + Bt'
    
    phase(2, "Setting up options and creating multiplot with same-rate custom variable")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set title for this test
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #6: Multiplot with Same-Rate Custom Variable"
        
        # Create the plot data list with single encounter for simpler testing
        last_encounter = env['encounters'][-1]
        plot_data = [(last_encounter['perihelion'], br_plus_bt)]
        
        # Create multiplot
        fig, axs = multiplot(plot_data)
        
        # Check that there's actual data in the plot
        has_plotted_data = False
        if len(axs) > 0:
            lines = axs[0].get_lines()
            has_plotted_data = len(lines) > 0
        
        # Record the complete result
        record_test_result("test_multiplot_same_rate_custom", {
            "description": "Multiplot Creation",
            "result": "PASS" if fig is not None and has_plotted_data else "FAIL",
            "message": f"Multiplot should be created with plotted data. Has data: {has_plotted_data}"
        })
        
        system_check("Multiplot Creation", 
                    fig is not None and has_plotted_data, 
                    "Multiplot should be created with plotted data")
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create multiplot: {str(e)}")

@pytest.mark.mission("Multiplot with Different-Rate Custom Variable")
def test_multiplot_different_rate_custom(test_environment):
    """Test multiplot with a custom variable derived from different-rate sources"""
    
    print("\n================================================================================")
    print("TEST #7: Multiplot with Different-Rate Custom Variable")
    print("Tests multiplot with a custom variable derived from sources with different rates")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Creating custom variable with different sampling rate sources")
    # Create a custom variable from components with different sampling rates
    ta_over_b = custom_variable('TAoverB2', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.color = 'purple'
    ta_over_b.y_label = 'Temperature Anisotropy / B'
    
    phase(2, "Setting up options and creating multiplot with different-rate custom variable")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set title for this test
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #7: Multiplot with Different-Rate Sources"
        
        # Create the plot data list with single encounter for simpler testing
        last_encounter = env['encounters'][-1]
        plot_data = [(last_encounter['perihelion'], ta_over_b)]
        
        # Create multiplot
        fig, axs = multiplot(plot_data)
        
        # Check that there's actual data in the plot
        has_plotted_data = False
        if len(axs) > 0:
            lines = axs[0].get_lines()
            has_plotted_data = len(lines) > 0
        
        # Record the complete result
        record_test_result("test_multiplot_different_rate_custom", {
            "description": "Multiplot Creation",
            "result": "PASS" if fig is not None and has_plotted_data else "FAIL",
            "message": f"Multiplot should be created with plotted data. Has data: {has_plotted_data}"
        })
        
        system_check("Multiplot Creation", 
                    fig is not None and has_plotted_data, 
                    "Multiplot should be created with plotted data")
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create multiplot: {str(e)}")

@pytest.mark.mission("Multiplot with Multiple Mixed Variables")
def test_multiplot_multiple_variables(test_environment):
    """Test multiplot with multiple variables including custom operations"""
    
    print("\n================================================================================")
    print("TEST #8: Multiplot with Multiple Mixed Variables")
    print("Tests multiplot with multiple variables including custom variables")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Creating custom variables for multiple variable test")
    # Create a more complex custom variable (mag component / anisotropy)
    br_ratio = custom_variable('BrRatio', mag_rtn_4sa.br / proton.anisotropy)
    br_ratio.color = 'blue'
    br_ratio.line_style = '-'
    
    phase(2, "Setting up options and creating multiplot with multiple variables")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set title for this test
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #8: Multiplot with Multiple Mixed Variables"
        
        # Create plot data with multiple variables but only for one encounter
        last_encounter = env['encounters'][-1]
        plot_data = [
            (last_encounter['perihelion'], mag_rtn_4sa.bmag),
            (last_encounter['perihelion'], mag_rtn_4sa.br),
            (last_encounter['perihelion'], br_ratio)
        ]
        
        # Create multiplot
        fig, axs = multiplot(plot_data)
        
        # Check that there's actual data in the plots
        has_plotted_data = True
        for i in range(len(axs)):
            lines = axs[i].get_lines()
            if len(lines) == 0:
                has_plotted_data = False
                break
        
        # Record the complete result
        record_test_result("test_multiplot_multiple_variables", {
            "description": "Multiplot Creation",
            "result": "PASS" if fig is not None and has_plotted_data else "FAIL",
            "message": f"Multiplot should be created with plotted data. Has data: {has_plotted_data}"
        })
        
        system_check("Multiplot Creation", 
                    fig is not None and has_plotted_data, 
                    "Multiplot should be created with all panels having data")
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create multiplot: {str(e)}")

@pytest.mark.mission("Multiplot with Pre-existing Variable")
def test_multiplot_preexisting_variable(test_environment):
    """Test multiplot with a pre-existing variable"""
    
    print("\n================================================================================")
    print("TEST #9: Multiplot with Pre-existing Variable")
    print("Tests multiplot with a standard pre-existing variable (Bmag)")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Setting up options and creating multiplot with pre-existing variable")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set title for this test
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #9: Multiplot with Pre-existing Variable"
        
        # Use just one encounter for simpler testing
        last_encounter = env['encounters'][-1]
        plot_data = [(last_encounter['perihelion'], mag_rtn_4sa.bmag)]
        
        # Create multiplot
        fig, axs = multiplot(plot_data)
        
        # Check that there's actual data in the plot
        has_plotted_data = False
        if len(axs) > 0:
            lines = axs[0].get_lines()
            has_plotted_data = len(lines) > 0
        
        # Record the complete result
        record_test_result("test_multiplot_preexisting_variable", {
            "description": "Multiplot Creation",
            "result": "PASS" if fig is not None and has_plotted_data else "FAIL",
            "message": f"Multiplot should be created with plotted data. Has data: {has_plotted_data}"
        })
        
        system_check("Multiplot Creation", 
                    fig is not None and has_plotted_data, 
                    "Multiplot should be created with plotted data")
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create multiplot: {str(e)}")

@pytest.mark.mission("Multiplot with Log Scale Custom Variable")
def test_multiplot_log_scale_custom_variable(test_environment):
    """Test multiplot with a custom variable that uses log scale"""
    
    print("\n================================================================================")
    print("TEST #10: Multiplot with Log Scale Custom Variable")
    print("Tests multiplot with a custom variable that uses log scale")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Creating log-scale custom variable and getting initial data")
    # Get data for a specific time range first (different from the encounters)
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Import the get_data function
    from plotbot import get_data
    
    # Get data for this specific time range
    get_data(trange, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Create a custom variable and set it to use log scale
    ta_over_b = custom_variable('LogScaleVar', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.color = 'red'
    ta_over_b.line_style = '--'
    ta_over_b.y_scale = 'log'  # This is what causes the issue
    
    print_manager.test(f"✅ Created log-scale custom variable with time range: {trange[0]} to {trange[1]}")
    print_manager.test(f"✅ Variable has y_scale set to: {ta_over_b.y_scale}")
    
    # Print the encounters we're testing with
    print_manager.test(f"Test will create plots for {len(env['encounters'])} encounters:")
    for i, enc in enumerate(env['encounters']):
        print_manager.test(f"  - Encounter {i+1}: {enc['perihelion']}")
    
    phase(2, "Setting up options and creating multiplot with log-scale custom variable")
    try:
        # Set up plot options
        setup_plot_options()
        
        # Set the title to include the test name
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST #10: Multiplot with Log Scale Custom Variable"
        
        # Create plot data for all encounters (will cause no-data situation for some panels)
        plot_data = [(encounter['perihelion'], ta_over_b) for encounter in env['encounters']]
        print_manager.test(f"Created plot_data with {len(plot_data)} items")
        
        # Attempt to create multiplot - this should now handle the empty data case
        fig, axs = multiplot(plot_data)
        
        # Check that the figure was created (even if some panels might be empty)
        system_check("Multiplot Creation", 
                    fig is not None, 
                    "Multiplot should be created even with empty panels")
        
        # Debug information about the panels
        print_manager.test(f"Multiplot created with {len(axs)} panels")
        
        # Check each panel for data
        panels_with_data = 0
        for i, ax in enumerate(axs):
            lines = ax.get_lines()
            has_data = len(lines) > 0
            if has_data:
                panels_with_data += 1
                print_manager.test(f"Panel {i+1} has {len(lines)} data lines ✅")
            else:
                print_manager.test(f"Panel {i+1} has no data ❌")
        
        # Check if at least one panel contains data (the panel with the time range we prepared)
        has_any_data = panels_with_data > 0
        print_manager.test(f"Total panels with data: {panels_with_data} out of {len(axs)}")
        
        system_check("At Least One Panel Has Data", 
                     has_any_data,
                     "At least one panel should have data (for our prepared time range)")
        
        # Check if the expected number of panels is created
        expected_panels = len(env['encounters'])
        system_check("Correct Number of Panels", 
                     len(axs) == expected_panels,
                     f"Expected {expected_panels} panels, got {len(axs)}")
        
        # Record success - we were able to create the multiplot without errors
        record_test_result("test_multiplot_log_scale_custom_variable", {
            "description": "Multiplot With Log Scale Variables",
            "result": "PASS" if has_any_data else "FAIL",
            "message": "Multiplot should handle log scale variables with empty data gracefully"
        })
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except ValueError as e:
        if "Data has no positive values, and therefore cannot be log-scaled" in str(e):
            # This is the expected error we're trying to fix
            print_manager.test(f"❌ EXPECTED ERROR: {str(e)}")
            record_test_result("test_multiplot_log_scale_custom_variable", {
                "description": "Multiplot With Log Scale Variables",
                "result": "FAIL",
                "message": "Multiplot should handle log scale variables with empty data gracefully"
            })
            pytest.fail(f"Failed to handle log scale with empty data: {str(e)}")
        else:
            # Some other ValueError occurred
            pytest.fail(f"Unexpected ValueError: {str(e)}")
    except Exception as e:
        # Any other exception is unexpected
        pytest.fail(f"Unexpected error: {str(e)}")

@pytest.mark.mission("Multiplot with Custom Variable Time Update")
def test_multiplot_custom_variable_time_update(test_environment):
    """Test that multiplot properly updates custom variables when time ranges change"""
    
    print("\n================================================================================")
    print("TEST #12: Multiplot with Custom Variable Time Update")
    print("Tests that multiplot properly updates custom variables when time ranges change")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Getting data for first time range")
    # Get initial data for a specific time range
    first_trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Import the get_data function to ensure we have data
    from plotbot import get_data
    get_data(first_trange, mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating custom variable and setting initial attributes")
    # Create a custom variable with specific styling
    ta_over_b = custom_variable('TAoverBStyled', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.color = 'magenta'
    ta_over_b.line_style = '-.'
    ta_over_b.line_width = 2.5
    ta_over_b.y_label = 'Temp. Anisotropy / |B|'
    
    # Print initial diagnostic information
    print_manager.test(f"Created custom variable with subclass_name: {ta_over_b.subclass_name}")
    print_manager.test(f"Initial attributes: color={ta_over_b.color}, style={ta_over_b.line_style}, width={ta_over_b.line_width}")
    
    # Save ID of initial variable for later comparison
    initial_id = id(ta_over_b)
    if hasattr(ta_over_b, 'datetime_array') and ta_over_b.datetime_array is not None and len(ta_over_b.datetime_array) > 0:
        initial_start = ta_over_b.datetime_array[0]
        initial_end = ta_over_b.datetime_array[-1]
        print_manager.test(f"Initial time range: {initial_start} to {initial_end}")
    
    phase(3, "Creating multiplot with first time range")
    try:
        # Set up plot options for a specific time window
        setup_plot_options()
        plt.options.window = '1:30:00.000'  # 1.5 hour window
        plt.options.single_title_text = "TEST #12-A: Custom Variable with First Time Range"
        
        # Plot the custom variable using first time
        plot_time = '2023-09-28/06:45:00.000'  # Middle of our first range
        plot_data = [(plot_time, ta_over_b)]
        
        # Create first multiplot
        fig1, axs1 = multiplot(plot_data)
        plt.close(fig1)  # Close figure to avoid memory leaks
        
        # Check if variable still has original styling after first plot
        has_style_preserved = (
            ta_over_b.color == 'magenta' and 
            ta_over_b.line_style == '-.' and
            ta_over_b.line_width == 2.5
        )
        system_check("Styling preserved after first plot", 
                    has_style_preserved,
                    f"Custom variable should preserve styling after first plot")
        record_test_result("test_multiplot_custom_variable_time_update", {
            "description": "Style preservation after first plot",
            "result": "PASS" if has_style_preserved else "FAIL",
            "message": "Custom variable should preserve styling after first plot"
        })
        
        # Save updated variable ID and time range
        first_plot_id = id(ta_over_b)
        
        if hasattr(ta_over_b, 'datetime_array') and ta_over_b.datetime_array is not None and len(ta_over_b.datetime_array) > 0:
            first_plot_start = ta_over_b.datetime_array[0]
            first_plot_end = ta_over_b.datetime_array[-1]
            print_manager.test(f"Time range after first plot: {first_plot_start} to {first_plot_end}")
        
        phase(4, "Creating multiplot with different time range")
        # Now use a different time range
        plt.options.window = '1:30:00.000'  # Keep same window size
        plt.options.single_title_text = "TEST #12-B: Custom Variable with Different Time Range"
        
        # Get data for the second time range
        second_trange = ['2023-12-28/06:00:00.000', '2023-12-28/07:30:00.000']
        get_data(second_trange, mag_rtn_4sa.bmag, proton.anisotropy)
        
        # Update the custom variable with the new time range
        print_manager.test("Updating custom variable with new time range")
        ta_over_b = ta_over_b.update(second_trange)
        
        # Use a different day to force data download and variable update
        second_plot_time = '2023-12-28/06:45:00.000'  # Different day
        plot_data = [(second_plot_time, ta_over_b)]
        
        # Create second multiplot
        fig2, axs2 = multiplot(plot_data)
        plt.close(fig2)  # Close figure to avoid memory leaks
        
        # Check if variable still has original styling after second plot with different time
        has_style_preserved_second = (
            ta_over_b.color == 'magenta' and 
            ta_over_b.line_style == '-.' and
            ta_over_b.line_width == 2.5
        )
        system_check("Styling preserved across time update", 
                     has_style_preserved_second,
                     f"Custom variable should preserve styling after updating to new time range")
        record_test_result("test_multiplot_custom_variable_time_update", {
            "description": "Style preservation across time update",
            "result": "PASS" if has_style_preserved_second else "FAIL", 
            "message": "Custom variable should preserve styling after updating to new time range"
        })
        
        # Check time range to confirm an update actually happened
        time_range_changed = False
        if hasattr(ta_over_b, 'datetime_array') and ta_over_b.datetime_array is not None and len(ta_over_b.datetime_array) > 0:
            second_plot_start = ta_over_b.datetime_array[0]
            second_plot_end = ta_over_b.datetime_array[-1]
            print_manager.test(f"Time range after second plot: {second_plot_start} to {second_plot_end}")
            
            # Convert to datetime64 for proper comparison
            try:
                first_start_dt64 = np.datetime64(first_plot_start)
                first_end_dt64 = np.datetime64(first_plot_end)
                second_start_dt64 = np.datetime64(second_plot_start)
                second_end_dt64 = np.datetime64(second_plot_end)
                
                # Check if time ranges are actually different
                time_range_changed = (
                    second_start_dt64 != first_start_dt64 or 
                    second_end_dt64 != first_end_dt64
                )
                
                print_manager.test(f"Time range changed between plots: {time_range_changed}")
                print_manager.test(f"  First plot: {first_start_dt64} to {first_end_dt64}")
                print_manager.test(f"  Second plot: {second_start_dt64} to {second_end_dt64}")
            except Exception as e:
                print_manager.test(f"Error comparing time ranges: {str(e)}")
        
        system_check("Time range updated for different date", 
                     time_range_changed,
                     f"Custom variable time range should change when plotting with different date")
        record_test_result("test_multiplot_custom_variable_time_update", {
            "description": "Time range updated for different date",
            "result": "PASS" if time_range_changed else "FAIL",
            "message": "Custom variable time range should change when plotting with different date"
        })
        
    except Exception as e:
        pytest.fail(f"Failed during multiplot custom variable test: {str(e)}") 

@pytest.mark.mission("Multiplot with Custom Variable Caching Test")
def test_multiplot_custom_variable_caching():
    """Test to reproduce and diagnose custom variable caching issues in multiplot"""
    
    print("\n================================================================================")
    print("TEST #13: Multiplot Custom Variable Caching Test")
    print("Tests multiplot behavior when plotting custom variables multiple times")
    print("================================================================================\n")
    
    phase(1, "Setting up test environment")
    # Define the initial time range
    initial_trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Import necessary modules
    from plotbot import get_data, plt, mag_rtn_4sa, proton
    from plotbot.custom_variables import custom_variable
    from plotbot.multiplot import multiplot
    from plotbot.data_tracker import global_tracker
    from plotbot.print_manager import print_manager
    
    # Reset plt options 
    plt.options.reset()
    plt.options.width = 15
    plt.options.height_per_panel = 1
    plt.options.use_single_title = True
    plt.options.window = '6:00:00.000'
    plt.options.position = 'around'
    
    # Set up encounters for plotting
    encounters = [
        {'perihelion': '2023/09/27 23:28:00.000'},  # Enc 17
        {'perihelion': '2023/12/29 00:56:00.000'},  # Enc 18
        {'perihelion': '2024/03/30 02:21:00.000'},  # Enc 19
    ]
    
    phase(2, "Creating custom variable with initial data")
    # Get data for initial time range
    get_data(initial_trange, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Create a custom variable
    test_var = custom_variable('CachingTestVar', proton.anisotropy - mag_rtn_4sa.bmag)
    test_var.color = 'blue'
    
    # Check if our variable has valid data
    has_initial_data = hasattr(test_var, 'datetime_array') and len(test_var.datetime_array) > 0
    initial_data_points = len(test_var.datetime_array) if has_initial_data else 0
    
    system_check("Initial variable creation", 
                 has_initial_data,
                 f"Custom variable should have data. Has {initial_data_points} points")
    
    # Get the initial time range of the variable
    if has_initial_data:
        initial_start = np.datetime64(test_var.datetime_array[0])
        initial_end = np.datetime64(test_var.datetime_array[-1])
        print(f"Initial variable time range: {initial_start} to {initial_end}")
    
    phase(3, "First plotting attempt")
    # Create the plot data list using list comprehension
    plot_data = [(encounter['perihelion'], test_var) for encounter in encounters]
    
    # First run of multiplot
    plt.options.single_title_text = "TEST #13-A: First Run with Custom Variable"
    fig1, axs1 = multiplot(plot_data)
    
    # Check that at least one panel got data
    panels_with_data_first_run = 0
    for ax in axs1:
        if len(ax.get_lines()) > 0:
            panels_with_data_first_run += 1
    
    system_check("First run panels with data", 
                 panels_with_data_first_run > 0,
                 f"At least one panel should have data. Found {panels_with_data_first_run} panels with data")
    
    # Close first figure to avoid memory leaks
    plt.close(fig1)
    
    phase(4, "Second plotting attempt - after global tracker marks calculation as done")
    # Check calculated ranges in global tracker
    print("Checking global tracker status before second run:")
    if hasattr(global_tracker, 'calculated_ranges'):
        for calc_type, ranges in global_tracker.calculated_ranges.items():
            print(f"  - {calc_type}: {len(ranges)} ranges")
            for start, end in ranges:
                print(f"    {start} to {end}")
    
    # Check if our variable still has the initial data
    current_data_points = len(test_var.datetime_array) if hasattr(test_var, 'datetime_array') else 0
    current_start = np.datetime64(test_var.datetime_array[0]) if current_data_points > 0 else None
    current_end = np.datetime64(test_var.datetime_array[-1]) if current_data_points > 0 else None
    
    print(f"Variable data before second run: {current_data_points} points")
    if current_start is not None:
        print(f"Current variable time range: {current_start} to {current_end}")
    
    # Second run of multiplot with same variable
    plt.options.single_title_text = "TEST #13-B: Second Run with Same Custom Variable"
    fig2, axs2 = multiplot(plot_data)
    
    # Check how many panels got data this time
    panels_with_data_second_run = 0
    for ax in axs2:
        if len(ax.get_lines()) > 0:
            panels_with_data_second_run += 1
    
    system_check("Second run panels with data", 
                 panels_with_data_second_run == panels_with_data_first_run,
                 f"Second run should have same number of panels with data. First: {panels_with_data_first_run}, Second: {panels_with_data_second_run}")
    
    # Close second figure
    plt.close(fig2)
    
    phase(5, "Testing solution - forced recalculation")
    # Reset the data tracker or force recalculation
    if hasattr(global_tracker, 'calculated_ranges') and 'custom_data_type' in global_tracker.calculated_ranges:
        print("Clearing cached calculation ranges for custom variables")
        global_tracker.calculated_ranges['custom_data_type'] = []
    
    # Create a new custom variable to avoid potential issues with the old one
    test_var_new = custom_variable('CachingTestVarNew', proton.anisotropy - mag_rtn_4sa.bmag)
    test_var_new.color = 'green'
    
    # Create plot data with the new variable
    plot_data_new = [(encounter['perihelion'], test_var_new) for encounter in encounters]
    
    # Third run with fresh variable and reset cache
    plt.options.single_title_text = "TEST #13-C: Third Run with Reset Cache"
    fig3, axs3 = multiplot(plot_data_new)
    
    # Check panels with data in third run
    panels_with_data_third_run = 0
    for ax in axs3:
        if len(ax.get_lines()) > 0:
            panels_with_data_third_run += 1
    
    system_check("Third run panels with data", 
                 panels_with_data_third_run > 0,
                 f"Third run should have data in some panels. Found {panels_with_data_third_run} panels with data")
    
    # Close third figure
    plt.close(fig3)
    
    # Final check - compare first and third runs
    system_check("Consistent behavior across runs", 
                 panels_with_data_third_run == panels_with_data_first_run,
                 f"First and third runs should have same number of data panels: {panels_with_data_first_run} vs {panels_with_data_third_run}")
    
    # Record test results
    record_test_result("test_multiplot_custom_variable_caching", {
        "description": "First Run Data Display",
        "result": "PASS" if panels_with_data_first_run > 0 else "FAIL",
        "message": f"First run should display data in some panels. Found {panels_with_data_first_run} panels with data"
    })
    
    record_test_result("test_multiplot_custom_variable_caching", {
        "description": "Second Run Data Display",
        "result": "PASS" if panels_with_data_second_run == panels_with_data_first_run else "FAIL",
        "message": f"Second run should match first run. First: {panels_with_data_first_run}, Second: {panels_with_data_second_run}"
    })
    
    record_test_result("test_multiplot_custom_variable_caching", {
        "description": "Forced Recalculation",
        "result": "PASS" if panels_with_data_third_run > 0 else "FAIL",
        "message": f"Third run with reset cache should display data. Found {panels_with_data_third_run} panels with data"
    }) 

@pytest.mark.mission("Multiplot Rainbow Color Mode Test")
def test_multiplot_rainbow_color_mode(test_environment):
    """Test multiplot with rainbow color mode across multiple panels"""
    
    print("\n================================================================================")
    print("TEST #14: Multiplot Rainbow Color Mode Test")
    print("Tests that rainbow color mode is consistently applied across all panels")
    print("================================================================================\n")
    
    env = test_environment
    
    phase(1, "Setting up test environment")
    # Reset plt options
    plt.options.reset()
    
    # Plot Sizing (matching notebook settings)
    plt.options.width = 20
    plt.options.height_per_panel = 0.8
    plt.options.hspace = 0.1
    
    # Font Sizes and Padding
    plt.options.title_fontsize = 11
    plt.options.y_label_size = 14
    plt.options.x_label_size = 12
    plt.options.x_tick_label_size = 10
    plt.options.y_tick_label_size = 10
    plt.options.y_label_pad = 5
    
    # Title and labels
    plt.options.use_single_title = True
    plt.options.single_title_text = "PSP FIELDS Br Component Around Perihelion for Multiple Encounters"
    plt.options.y_label_uses_encounter = True
    plt.options.y_label_includes_time = False
    
    # Vertical line
    plt.options.draw_vertical_line = True
    plt.options.vertical_line_width = 1.5
    plt.options.vertical_line_color = 'red'
    plt.options.vertical_line_style = '--'
    
    # Time settings
    plt.options.use_relative_time = True
    plt.options.relative_time_step_units = 'hours'
    plt.options.relative_time_step = 6
    plt.options.use_single_x_axis = True
    plt.options.use_custom_x_axis_label = False
    plt.options.custom_x_axis_label = None
    
    # Rainbow settings
    plt.options.color_mode = 'rainbow'
    plt.options.single_color = None
    
    # Window settings
    plt.options.window = '48:00:00.000'
    plt.options.position = 'around'
    
    phase(2, "Creating plot data")
    # Use mag_rtn_4sa.br directly like in the notebook
    plot_variable = mag_rtn_4sa.br
    
    # Create plot data with the same encounters as the notebook
    encounters = [
        {'perihelion': '2023/09/27 23:28:00.000'},  # Enc 17
        {'perihelion': '2023/12/29 00:56:00.000'},  # Enc 18
        {'perihelion': '2024/03/30 02:21:00.000'},  # Enc 19
    ]
    
    plot_data = [(enc['perihelion'], plot_variable) for enc in encounters]
    
    phase(3, "Creating multiplot and verifying colors")
    try:
        # Create multiplot
        fig, axs = multiplot(plot_data)
        
        # First verify we have data in each panel
        has_data = True
        for i, ax in enumerate(axs):
            lines = ax.get_lines()
            if len(lines) == 0:
                print_manager.warning(f"Panel {i+1} has no data")
                has_data = False
            else:
                print_manager.test(f"Panel {i+1} has {len(lines)} data points")
        
        if not has_data:
            pytest.fail("Some panels have no data")
        
        # Verify that each panel has the correct rainbow color
        colors = ['red', 'gold', 'blue']  # Expected colors for 3 panels
        all_colors_correct = True
        
        for i, ax in enumerate(axs):
            panel_colors_correct = True  # Track colors for each panel separately
            
            # Get the color of the plotted line
            lines = ax.get_lines()
            if len(lines) > 0:
                line_color = lines[0].get_color()
                expected_color = colors[i]
                
                # Convert colors to RGB for comparison
                try:
                    line_rgb = plt.matplotlib.colors.to_rgb(line_color)
                    expected_rgb = plt.matplotlib.colors.to_rgb(expected_color)
                    
                    # Check if colors match within a small tolerance
                    if not np.allclose(line_rgb, expected_rgb, atol=0.01):
                        print_manager.warning(f"Panel {i+1} line color mismatch: got {line_rgb}, expected {expected_rgb}")
                        panel_colors_correct = False
                except ValueError as e:
                    print_manager.warning(f"Error converting colors: {str(e)}")
                    panel_colors_correct = False
            
            # Check axis elements (spines, labels, ticks)
            for spine_name, spine in ax.spines.items():
                spine_color = spine.get_edgecolor()
                
                # Convert spine color to RGB for comparison
                try:
                    # If spine_color is already an RGB/RGBA tuple, use it directly
                    if isinstance(spine_color, tuple):
                        spine_rgb = spine_color[:3] if len(spine_color) == 4 else spine_color
                    else:
                        spine_rgb = plt.matplotlib.colors.to_rgb(spine_color)
                    
                    expected_rgb = plt.matplotlib.colors.to_rgb(colors[i])
                    
                    if not np.allclose(spine_rgb, expected_rgb, atol=0.01):
                        print_manager.warning(f"Panel {i+1} spine {spine_name} color mismatch: got {spine_rgb}, expected {expected_rgb}")
                        panel_colors_correct = False
                except (ValueError, TypeError) as e:
                    print_manager.warning(f"Error checking spine color: {str(e)}")
                    panel_colors_correct = False
            
            # Get label color
            if ax.yaxis.label:
                label_color = ax.yaxis.label.get_color()
                try:
                    label_rgb = plt.matplotlib.colors.to_rgb(label_color)
                    expected_rgb = plt.matplotlib.colors.to_rgb(colors[i])
                    
                    if not np.allclose(label_rgb, expected_rgb, atol=0.01):
                        print_manager.warning(f"Panel {i+1} label color mismatch: got {label_rgb}, expected {expected_rgb}")
                        panel_colors_correct = False
                except ValueError as e:
                    print_manager.warning(f"Error checking label color: {str(e)}")
                    panel_colors_correct = False
            
            # Get tick colors
            tick_params = ax.yaxis.get_tick_params()
            if 'labelcolor' in tick_params:
                tick_color = tick_params['labelcolor']
                try:
                    tick_rgb = plt.matplotlib.colors.to_rgb(tick_color)
                    expected_rgb = plt.matplotlib.colors.to_rgb(colors[i])
                    
                    if not np.allclose(tick_rgb, expected_rgb, atol=0.01):
                        print_manager.warning(f"Panel {i+1} tick color mismatch: got {tick_rgb}, expected {expected_rgb}")
                        panel_colors_correct = False
                except ValueError as e:
                    print_manager.warning(f"Error checking tick color: {str(e)}")
                    panel_colors_correct = False
            
            assert panel_colors_correct, f"Panel {i+1} colors do not match expected rainbow colors"
        
        # Record the complete result with more detailed message
        result_message = "All panels have consistent rainbow colors" if all_colors_correct else "Some panels have incorrect colors"
        record_test_result("test_multiplot_rainbow_color_mode", {
            "description": "Rainbow Color Mode Test",
            "result": "PASS" if all_colors_correct else "FAIL",
            "message": result_message
        })
        
        # This should now properly fail if colors don't match
        system_check("Rainbow Color Mode", 
                    all_colors_correct, 
                    result_message)
        
        # Close the figure to avoid memory leaks
        plt.close(fig)
        
    except Exception as e:
        pytest.fail(f"Failed to create rainbow multiplot: {str(e)}") 