# tests/test_custom_variables_working.py
# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python -m pytest tests/test_custom_variables_working.py -vv -s
# To run a specific test and see print output:
# conda run -n plotbot_env python -m pytest tests/test_custom_variables_working.py::test_custom_variable_simple_addition -vv -s

"""
Custom Variables Test Suite

Tests the custom variable functionality that was recently fixed.
"""

import matplotlib
import pytest
import os
import sys
import numpy as np
from datetime import datetime
import traceback

# Path Setup
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

# Plotbot Imports
import plotbot
from plotbot.plotbot_main import plotbot as plotbot_function
from plotbot.showdahodo import showdahodo
from plotbot import print_manager
from plotbot import plt
from plotbot.test_pilot import phase, system_check
from plotbot import proton, mag_rtn_4sa
from plotbot.data_classes.custom_variables import custom_variable

# Test Constants
CUSTOM_VAR_TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

@pytest.fixture(autouse=True)
def setup_custom_var_tests():
    """Ensure plots are closed and print manager configured before and after each test."""
    # Configure print manager for debugging
    print_manager.show_status = True
    print_manager.show_debug = False  # Keep debug off to reduce noise
    print_manager.show_custom_debug = True  # Enable custom variable debugging
    print_manager.show_warning = True
    
    plt.close('all')
    yield
    plt.close('all')
    
    # Reset print manager
    print_manager.show_custom_debug = False

@pytest.mark.mission("Custom Variables: Simple Addition")
def test_custom_variable_simple_addition():
    """Test creating a simple custom variable with addition."""
    print("\n=== Testing Custom Variable Simple Addition ===")
    
    # Enable custom debug for this test
    print_manager.show_custom_debug = True
    print("🔍 Custom debug enabled for troubleshooting anisotropy plus ten")
    
    fig = None
    fig_num = None
    
    try:
        phase(1, "Creating custom variable: proton.anisotropy + 10")
        
        # Create the custom variable
        anisotropy_plus_ten = custom_variable('anisotropy_plus_ten', proton.anisotropy + 10)
        
        print(f"✅ Custom variable created: {anisotropy_plus_ten.subclass_name}")
        print(f"   Type: {type(anisotropy_plus_ten)}")
        
        # Verify the variable was created properly
        system_check("Custom Variable Created", anisotropy_plus_ten is not None, "Custom variable should be created")
        system_check("Custom Variable Type", isinstance(anisotropy_plus_ten, plotbot.plot_manager), "Custom variable should be plot_manager type")
        system_check("Custom Variable Name", anisotropy_plus_ten.subclass_name == 'anisotropy_plus_ten', "Custom variable should have correct name")
        
        phase(2, "Customizing variable appearance")
        
        # Customize appearance
        anisotropy_plus_ten.color = 'red'
        anisotropy_plus_ten.line_style = '-'
        anisotropy_plus_ten.line_width = 2
        anisotropy_plus_ten.legend_label = 'Anisotropy + 10'
        
        phase(3, "Plotting with custom variable")
        
        # Plot original vs custom variable
        plotbot_function(CUSTOM_VAR_TRANGE, proton.anisotropy, 1, anisotropy_plus_ten, 2)
        
        phase(4, "Verifying plot creation")
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Custom Variable Plot Completed", True, "plotbot call with custom variable should complete")
        system_check("Custom Variable Figure Exists", fig is not None and fig_num is not None, "plotbot should create figure for custom variable")
        
        print("✅ Custom variable simple addition test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Simple Addition test failed: {e}\n{traceback.format_exc()}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed custom variable figure {fig_num} ---")
            except Exception as close_err:
                print(f"--- Error closing custom variable figure {fig_num}: {close_err} ---")

@pytest.mark.mission("Custom Variables: Variable Division")
def test_custom_variable_division():
    """Test creating a custom variable with division between two variables."""
    print("\n=== Testing Custom Variable Division ===")
    fig = None
    fig_num = None
    
    try:
        phase(1, "Creating custom variable: proton.anisotropy / mag_rtn_4sa.bmag")
        
        # Create a classic ratio variable
        aniso_over_bmag = custom_variable('aniso_over_bmag', proton.anisotropy / mag_rtn_4sa.bmag)
        
        print(f"✅ Custom variable created: {aniso_over_bmag.subclass_name}")
        
        # Verify the variable was created properly
        system_check("Division Variable Created", aniso_over_bmag is not None, "Division custom variable should be created")
        system_check("Division Variable Type", isinstance(aniso_over_bmag, plotbot.plot_manager), "Division custom variable should be plot_manager type")
        
        phase(2, "Customizing division variable appearance")
        
        # Customize appearance
        aniso_over_bmag.color = 'blue'
        aniso_over_bmag.line_width = 2
        aniso_over_bmag.legend_label = 'Anisotropy / B_mag'
        
        phase(3, "Creating scatter plot with showdahodo")
        
        # Create a scatter plot using showdahodo
        fig, ax = showdahodo(CUSTOM_VAR_TRANGE, aniso_over_bmag, proton.anisotropy)
        
        phase(4, "Verifying scatter plot creation")
        
        fig_num = plt.gcf().number
        
        system_check("Division Variable Scatter Plot Completed", True, "showdahodo call with division variable should complete")
        system_check("Division Variable Figure Exists", fig is not None and fig_num is not None, "showdahodo should create figure for division variable")
        system_check("Division Variable Axis Exists", ax is not None, "showdahodo should create axis for division variable")
        
        print("✅ Custom variable division test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Division test failed: {e}\n{traceback.format_exc()}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed division variable figure {fig_num} ---")
            except Exception as close_err:
                print(f"--- Error closing division variable figure {fig_num}: {close_err} ---")

@pytest.mark.mission("Custom Variables: Complex Chained Expressions")
def test_custom_variable_complex_expressions():
    """Test creating complex custom variables with multiple operations."""
    print("\n=== Testing Custom Variable Complex Expressions ===")
    fig = None
    fig_num = None
    
    try:
        phase(1, "Creating complex custom variables")
        
        print("   1. Creating: proton.anisotropy / mag_rtn_4sa.br + proton.temperature")
        complex_var1 = custom_variable('complex_var1', proton.anisotropy / mag_rtn_4sa.br + proton.temperature)
        
        print("   2. Creating: mag_rtn_4sa.br * mag_rtn_4sa.bt")
        b_product = custom_variable('b_product', mag_rtn_4sa.br * mag_rtn_4sa.bt)
        
        print("   3. Creating: (proton.anisotropy + 5) * mag_rtn_4sa.bmag / 100")
        fancy_var = custom_variable('fancy_var', (proton.anisotropy + 5) * mag_rtn_4sa.bmag / 100)
        
        print("✅ All complex custom variables created successfully!")
        
        # Verify all variables were created
        system_check("Complex Variable 1 Created", complex_var1 is not None, "Complex variable 1 should be created")
        system_check("B Product Variable Created", b_product is not None, "B product variable should be created")
        system_check("Fancy Variable Created", fancy_var is not None, "Fancy variable should be created")
        
        phase(2, "Customizing complex variable appearance")
        
        # Customize colors
        complex_var1.color = 'purple'
        complex_var1.legend_label = 'T_aniso/Br + T_proton'
        
        b_product.color = 'green'
        b_product.legend_label = 'Br × Bt'
        
        fancy_var.color = 'orange'
        fancy_var.legend_label = '(T_aniso+5)×B_mag/100'
        
        phase(3, "Creating multi-panel plot with complex variables")
        
        # Create a comprehensive plot
        plotbot_function(CUSTOM_VAR_TRANGE, 
                        proton.anisotropy, 1,      # Original variable
                        mag_rtn_4sa.bmag, 2,       # Original variable  
                        complex_var1, 3,           # Complex custom variable
                        b_product, 4,              # Magnetic field product
                        fancy_var, 5)              # Fancy nested expression
        
        phase(4, "Verifying complex variable plot")
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Complex Variables Plot Completed", True, "plotbot call with complex variables should complete")
        system_check("Complex Variables Figure Exists", fig is not None and fig_num is not None, "plotbot should create figure for complex variables")
        
        print("✅ Complex custom variables test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Complex Expressions test failed: {e}\n{traceback.format_exc()}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed complex variables figure {fig_num} ---")
            except Exception as close_err:
                print(f"--- Error closing complex variables figure {fig_num}: {close_err} ---")

@pytest.mark.mission("Custom Variables: Global Accessibility")
def test_custom_variable_global_accessibility():
    """Test that custom variables are globally accessible."""
    print("\n=== Testing Custom Variable Global Accessibility ===")
    
    try:
        phase(1, "Creating custom variables for global access test")
        
        # Create some custom variables
        test_var1 = custom_variable('global_test_var1', proton.anisotropy + 5)
        test_var2 = custom_variable('global_test_var2', mag_rtn_4sa.br * 2)
        
        phase(2, "Testing global accessibility")
        
        # Test that variables are accessible via plotbot module
        import plotbot as pb
        
        # Check if variables are accessible
        has_var1 = hasattr(pb, 'global_test_var1')
        has_var2 = hasattr(pb, 'global_test_var2')
        
        system_check("Global Variable 1 Accessible", has_var1, "Custom variable 1 should be globally accessible")
        system_check("Global Variable 2 Accessible", has_var2, "Custom variable 2 should be globally accessible")
        
        if has_var1 and has_var2:
            # Get the global variables
            global_var1 = getattr(pb, 'global_test_var1')
            global_var2 = getattr(pb, 'global_test_var2')
            
            system_check("Global Variable 1 Type", isinstance(global_var1, plotbot.plot_manager), "Global variable 1 should be plot_manager")
            system_check("Global Variable 2 Type", isinstance(global_var2, plotbot.plot_manager), "Global variable 2 should be plot_manager")
            
            phase(3, "Creating variable using other custom variables")
            
            # Create a variable that uses other custom variables
            super_custom = custom_variable('super_custom', global_var1 * global_var2)
            
            system_check("Super Custom Variable Created", super_custom is not None, "Variable using other custom variables should be created")
            
            print("✅ Global accessibility test completed successfully")
        else:
            pytest.fail("Custom variables are not globally accessible")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Global Accessibility test failed: {e}\n{traceback.format_exc()}")

@pytest.mark.mission("Custom Variables: Different Time Ranges")
def test_custom_variable_time_ranges():
    """Test custom variables with different time ranges."""
    print("\n=== Testing Custom Variable Time Ranges ===")
    fig = None
    fig_num = None
    
    try:
        phase(1, "Creating custom variable for time range test")
        
        # Create a custom variable
        time_test_var = custom_variable('time_test_var', proton.anisotropy / mag_rtn_4sa.bmag)
        
        phase(2, "Testing with original time range")
        
        original_trange = CUSTOM_VAR_TRANGE
        print(f"📅 Original time range: {original_trange}")
        
        # Plot with original time range
        plotbot_function(original_trange, time_test_var, 1)
        plt.close('all')  # Close this plot
        
        phase(3, "Testing with different time range")
        
        # Try a different time range
        new_trange = ['2023-09-28/08:00:00.000', '2023-09-28/09:00:00.000']
        print(f"📅 New time range: {new_trange}")
        
        # Plot with new time range
        plotbot_function(new_trange, time_test_var, 1)
        
        phase(4, "Verifying time range adaptation")
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Time Range Adaptation Plot Completed", True, "plotbot call with different time range should complete")
        system_check("Time Range Adaptation Figure Exists", fig is not None and fig_num is not None, "plotbot should create figure for different time range")
        
        print("✅ Custom variables adapt to different time ranges successfully")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Time Ranges test failed: {e}\n{traceback.format_exc()}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed time range figure {fig_num} ---")
            except Exception as close_err:
                print(f"--- Error closing time range figure {fig_num}: {close_err} ---")

@pytest.mark.mission("Custom Variables: Comprehensive Integration")
def test_custom_variable_comprehensive():
    """Comprehensive test that exercises multiple custom variable features together."""
    print("\n=== Testing Custom Variable Comprehensive Integration ===")
    fig = None
    fig_num = None
    
    try:
        phase(1, "Creating a suite of custom variables")
        
        # Create various types of custom variables
        simple_add = custom_variable('comprehensive_add', proton.anisotropy + 10)
        ratio_var = custom_variable('comprehensive_ratio', proton.anisotropy / mag_rtn_4sa.bmag)
        complex_var = custom_variable('comprehensive_complex', 
                                    (proton.temperature - proton.temperature.mean()) / mag_rtn_4sa.br)
        
        phase(2, "Customizing all variables")
        
        # Customize appearance
        simple_add.color = 'red'
        simple_add.legend_label = 'Simple Addition'
        
        ratio_var.color = 'blue' 
        ratio_var.legend_label = 'Aniso/B Ratio'
        
        complex_var.color = 'green'
        complex_var.legend_label = 'Complex Expression'
        
        phase(3, "Creating comprehensive plot")
        
        # Create a plot with all variable types
        plotbot_function(CUSTOM_VAR_TRANGE,
                        simple_add, 1,
                        ratio_var, 2, 
                        complex_var, 3)
        
        phase(4, "Verifying comprehensive integration")
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        
        system_check("Comprehensive Integration Plot Completed", True, "plotbot call with multiple custom variables should complete")
        system_check("Comprehensive Integration Figure Exists", fig is not None and fig_num is not None, "plotbot should create figure for comprehensive test")
        
        # Test that all variables are globally accessible
        import plotbot as pb
        global_vars = ['comprehensive_add', 'comprehensive_ratio', 'comprehensive_complex']
        
        for var_name in global_vars:
            has_var = hasattr(pb, var_name)
            system_check(f"Global {var_name} Accessible", has_var, f"Variable {var_name} should be globally accessible")
        
        print("✅ Comprehensive custom variables integration test completed successfully")
        
    except Exception as e:
        pytest.fail(f"Custom Variable Comprehensive Integration test failed: {e}\n{traceback.format_exc()}")
    finally:
        if fig_num is not None:
            try:
                plt.close(fig_num)
                print(f"--- Explicitly closed comprehensive figure {fig_num} ---")
            except Exception as close_err:
                print(f"--- Error closing comprehensive figure {fig_num}: {close_err} ---")

# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_custom_variables_module():
    """Module-level cleanup for custom variables tests."""
    yield
    plt.close('all')
    # Reset print manager to defaults
    print_manager.show_status = True
    print_manager.show_debug = False
    print_manager.show_custom_debug = False
    print_manager.show_warnings = True 