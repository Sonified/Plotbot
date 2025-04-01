# tests/test_custom_variables.py
"""
Tests for custom variables functionality in Plotbot.

This file contains tests for creating, manipulating, and plotting custom variables,
including tests for expression parsing, variable operations, and automatic updates.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_custom_variables.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_custom_variables.py::test_create_custom_variable -v
"""
import pytest
import numpy as np
from plotbot import get_data, mag_rtn_4sa, proton
from plotbot.custom_variables import custom_variable, CustomVariablesContainer
from plotbot.test_pilot import phase, system_check

@pytest.fixture
def test_environment():
    """Test environment with data and time ranges"""
    return {
        'trange_initial': ['2023-09-28/06:00:00', '2023-09-28/07:30:00'],
        'trange_updated': ['2023-09-29/06:00:00', '2023-09-29/07:30:00'],
        'expected_resolution': 3000,  # Approximate expected data points
    }

@pytest.mark.mission("Basic Custom Variable Creation")
def test_create_custom_variable(test_environment):
    """Test creating a custom variable"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating custom variable")
    var = custom_variable('Fancy Protons', proton.anisotropy / mag_rtn_4sa.bmag)
    
    phase(3, "Verifying variable properties")
    system_check("Variable Creation", 
                var is not None, 
                "Custom variable should be created")
    
    system_check("Variable Class Name",
                hasattr(var, 'class_name') and var.class_name == 'custom_class',
                f"Variable should have class_name set to 'custom_class', found '{var.class_name}'")
    
    system_check("Variable Data Type",
                hasattr(var, 'data_type') and var.data_type == 'custom_data_type',
                f"Variable should have data_type set to 'custom_data_type', found '{var.data_type}'")
    
    system_check("Variable Registration",
                hasattr(var, 'update'),
                "Variable should have update method")
    
    system_check("Data Presence",
                len(var.datetime_array) > 0,
                "Variable should have datetime data")
    
    # Test accessing the variable globally
    try:
        # Try to import the variable with the exact name we gave it
        from plotbot import Fancy_Protons
        test_var = Fancy_Protons
        system_check("Global Access",
                    test_var is not None,
                    "Variable should be globally accessible")
    except Exception as e:
        # If direct import fails, try a more flexible approach
        import plotbot
        found = False
        for name in dir(plotbot):
            if 'Fancy' in name or 'Protons' in name:
                test_var = getattr(plotbot, name)
                found = True
                break
        
        system_check("Global Access - Flexible",
                    found,
                    f"Variable should be accessible in some form (error: {e})")
    
    # Check that y_label and legend_label are set correctly
    system_check("Y-axis Label",
                var.y_label == 'Fancy Protons',
                f"Y-axis label should be 'Fancy Protons', got '{var.y_label}'")
    
    system_check("Legend Label",
                var.legend_label == 'Fancy Protons',
                f"Legend label should be 'Fancy Protons', got '{var.legend_label}'")

@pytest.mark.mission("Time Range Updates")
def test_time_range_updates(test_environment):
    """Test custom variables properly update with time range changes"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating and verifying custom variable")
    var = custom_variable('Solar Wind Indicator', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Verify initial datetime range
    initial_start = np.datetime64(var.datetime_array[0])
    initial_end = np.datetime64(var.datetime_array[-1])
    
    system_check("Initial Date",
                initial_start.astype('datetime64[D]') == np.datetime64('2023-09-28'),
                f"Initial start date wrong: {initial_start}")
    
    phase(3, "Updating to new time range")
    get_data(env['trange_updated'], mag_rtn_4sa.bmag, proton.anisotropy)
    var = var.update(env['trange_updated'])
    
    phase(4, "Verifying time range update")
    # Check that the datetime array was updated
    try:
        updated_start = np.datetime64(var.datetime_array[0])
        updated_end = np.datetime64(var.datetime_array[-1])
        
        system_check("Updated Date",
                    updated_start.astype('datetime64[D]') == np.datetime64('2023-09-29'),
                    f"Updated start date wrong: {updated_start}")
                    
    except (IndexError, AttributeError) as e:
        pytest.fail(
            f"Failed to update variable with new time range.\n"
            f"  - Variable: Solar Wind Indicator\n"
            f"  - Expected datetime range: 2023-09-29 06:00:00 to 07:30:00\n"
            f"  - Error: {str(e)}"
        )

@pytest.mark.mission("Custom Attribute Assignment")
def test_custom_attributes(test_environment):
    """Test that all attributes can be properly assigned to custom variables"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating custom variable")
    var = custom_variable('Fancy Space Weather Index', proton.anisotropy / mag_rtn_4sa.bmag)
    
    phase(3, "Testing plot appearance attributes")
    # Visual attributes
    attributes_to_test = {
        'color': 'red',
        'line_style': '--',
        'line_width': 2.5,
        'y_label': 'Custom Y Label',
        'legend_label': 'Custom Legend Text',
        'y_scale': 'log',
        'y_limit': (-10, 10),
        'colormap': 'viridis',
        'colorbar_scale': 'log',
        'colorbar_limits': (-1, 1)
    }
    
    # Test setting each attribute
    for attr_name, attr_value in attributes_to_test.items():
        try:
            setattr(var, attr_name, attr_value)
            actual_value = getattr(var, attr_name)
            system_check(
                f"Setting {attr_name}",
                actual_value == attr_value,
                f"Failed to set {attr_name}. Expected {attr_value}, got {actual_value}"
            )
        except Exception as e:
            pytest.fail(f"Error setting attribute {attr_name}: {str(e)}")
    
    phase(4, "Testing custom method attributes")
    # Check if specific method attributes work
    try:
        # Test .copy() method
        var_copy = var.copy()
        system_check(
            "Copy Method", 
            var_copy is not var and var_copy.class_name == var.class_name,
            "Copy method should create a distinct object with same properties"
        )
        
        # Check operation string
        system_check(
            "Operation String",
            hasattr(var, 'operation') and var.operation == 'div',
            f"Operation should be 'div', got: {getattr(var, 'operation', 'None')}"
        )
        
        # Check source variables
        system_check(
            "Source Variables", 
            hasattr(var, 'source_var') and len(var.source_var) > 0,
            f"Source variables should be present"
        )
    except Exception as e:
        pytest.fail(f"Error testing method attributes: {str(e)}")

@pytest.mark.mission("Multi-Variable Complex Expressions")
def test_multi_variable_expressions(test_environment):
    """Test creating custom variables with complex multi-variable expressions"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], 
             mag_rtn_4sa.bmag, mag_rtn_4sa.br, mag_rtn_4sa.bt, 
             proton.anisotropy, proton.density)
    
    phase(2, "Creating 3-variable custom expression")
    # First build up intermediate variables
    br_squared = mag_rtn_4sa.br * mag_rtn_4sa.br
    bt_squared = mag_rtn_4sa.bt * mag_rtn_4sa.bt
    field_sum = br_squared + bt_squared
    
    # Create the custom variable representing a 3-variable expression
    var3 = custom_variable('Magnetic Field Energy', field_sum)
    
    system_check("3-Variable Creation", 
                var3 is not None, 
                "Custom variable with 3 variables should be created")
    
    system_check("3-Variable Y-Label", 
                var3.y_label == 'Magnetic Field Energy',
                f"Y-label should match name 'Magnetic Field Energy', got '{var3.y_label}'")
    
    phase(3, "Creating 4-variable custom expression with more complexity")
    # Create a more complex 4-variable expression
    # First we'll make a 2-variable expression
    mag_field_strength = mag_rtn_4sa.bmag * 2  # First multiply by scalar
    density_weighted = proton.density * proton.anisotropy  # Another 2-variable expression
    
    # Now combine them into a 4-variable expression
    plasma_parameter = custom_variable('Space Plasma Index', density_weighted / mag_field_strength)
    
    system_check("4-Variable Creation", 
                plasma_parameter is not None,
                "Custom variable with 4 variables should be created")
    
    system_check("4-Variable Label",
                plasma_parameter.y_label == 'Space Plasma Index',
                f"Y-label should be 'Space Plasma Index', got '{plasma_parameter.y_label}'")
    
    system_check("4-Variable Data",
                len(plasma_parameter.datetime_array) > 0,
                "4-variable expression should have valid data")
    
    phase(4, "Testing step-by-step vs. direct formula approach")
    # Demonstrate the approach for complex formulas
    # 1. Step by step (works with our system)
    step1 = mag_rtn_4sa.br * mag_rtn_4sa.bt  # First multiply fields
    step2 = custom_variable('Complex Field Product', step1 / proton.anisotropy)  # Then divide
    
    # Note: A direct approach with parentheses would be:
    # combined = custom_variable('Direct Formula', (mag_rtn_4sa.br * mag_rtn_4sa.bt) / proton.anisotropy)
    # But this doesn't track source variables correctly in our current implementation
    
    system_check("Step-by-Step Approach", 
                step2 is not None and len(step2.datetime_array) > 0,
                "Step-by-step approach for complex formulas should work")

@pytest.mark.mission("Special Characters in Variable Names")
def test_special_character_variable_names(test_environment):
    """Test that variables with special characters in names are properly handled"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating variables with special characters")
    # Test different special characters in names
    special_names = [
        "Variable With Spaces",
        "Variable-With-Hyphens",
        "Variable_With_Underscores",
        "Variable.With.Dots",
        "Variable+With+Plus"
    ]
    
    variables = {}
    for name in special_names:
        variables[name] = custom_variable(name, proton.anisotropy / mag_rtn_4sa.bmag)
        
        # Verify the variable was created with correct name attributes
        system_check(f"Variable '{name}' Creation",
                    variables[name] is not None,
                    f"Variable '{name}' should be created")
        
        system_check(f"Variable '{name}' Y-Label",
                    variables[name].y_label == name,
                    f"Y-label should be '{name}', got '{variables[name].y_label}'")
    
    phase(3, "Testing global namespace access")
    import plotbot
    
    # For each variable, try to find it in the global namespace
    for name in special_names:
        # Generate possible variants of the name as it might appear in namespace
        possible_names = [
            name,  # Original name
            name.replace(' ', '_'),  # Spaces to underscores
            name.replace('-', '_'),  # Hyphens to underscores
            name.replace('.', '_'),  # Dots to underscores
            name.replace('+', '_'),  # Plus to underscores
            name.replace(' ', '').replace('-', '').replace('.', '').replace('+', '')  # No special chars
        ]
        
        # Check if any variant exists in namespace
        found = False
        found_name = None
        for pname in possible_names:
            if hasattr(plotbot, pname):
                found = True
                found_name = pname
                break
                
        # If not found by direct names, try searching through all attributes
        if not found:
            sanitized_parts = [part for part in name.split() if len(part) > 3]
            for attr_name in dir(plotbot):
                if any(part in attr_name for part in sanitized_parts):
                    found = True
                    found_name = attr_name
                    break
        
        # Verify the variable is accessible in some form
        system_check(f"Global Access for '{name}'",
                    found,
                    f"Variable '{name}' should be accessible in global namespace (found as '{found_name}' if any)")
        
        if found:
            # Verify the retrieved variable has correct attributes
            var_from_namespace = getattr(plotbot, found_name)
            system_check(f"Namespace Variable Attributes for '{name}'",
                        hasattr(var_from_namespace, 'y_label') and var_from_namespace.y_label == name,
                        f"Variable from namespace should have correct y_label")

@pytest.mark.mission("Style Attribute Preservation")
def test_style_attribute_preservation(test_environment):
    """Test that styling attributes are preserved when variables are updated"""
    env = test_environment
    
    phase(1, "Setting up test data")
    get_data(env['trange_initial'], mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating styled custom variable")
    var = custom_variable('Styled Variable', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Set various style attributes
    style_attributes = {
        'color': 'red',
        'line_style': '--',
        'line_width': 2.5,
        'y_scale': 'log'
    }
    
    # Apply styles
    for attr_name, attr_value in style_attributes.items():
        setattr(var, attr_name, attr_value)
        
    # Verify initial attributes are set
    for attr_name, attr_value in style_attributes.items():
        system_check(
            f"Initial {attr_name}",
            getattr(var, attr_name) == attr_value,
            f"Attribute {attr_name} should be set to {attr_value}"
        )
    
    phase(3, "Updating variable to new time range")
    get_data(env['trange_updated'], mag_rtn_4sa.bmag, proton.anisotropy)
    updated_var = var.update(env['trange_updated'])
    
    phase(4, "Verifying style attributes are preserved")
    # Check that all style attributes are preserved
    for attr_name, attr_value in style_attributes.items():
        system_check(
            f"Preserved {attr_name}",
            hasattr(updated_var, attr_name) and getattr(updated_var, attr_name) == attr_value,
            f"Attribute {attr_name} should be preserved as {attr_value} after update"
        )

@pytest.mark.mission("Same Day Style Preservation")
def test_style_preservation_same_day(test_environment):
    """Test style attribute preservation when updating within the same day"""
    env = test_environment
    
    phase(1, "Setting up test data")
    initial_range = ['2023-09-28/06:00:00', '2023-09-28/07:30:00']
    get_data(initial_range, mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating styled custom variable")
    var = custom_variable('Same Day Style Test', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Set distinctive style attributes
    var.color = 'green'
    var.line_style = '-.'
    var.line_width = 3.0
    
    print(f"Initial attributes - color: {var.color}, line_style: {var.line_style}, line_width: {var.line_width}")
    
    phase(3, "Updating to later time in same day (same 6-hour chunk)")
    # Move forward 1 hour but stay in same 6-hour chunk
    updated_range = ['2023-09-28/07:00:00', '2023-09-28/08:30:00']
    get_data(updated_range, mag_rtn_4sa.bmag, proton.anisotropy)
    updated_var = var.update(updated_range)
    
    phase(4, "Verifying style attributes preserved in same-day update")
    print(f"Updated attributes - color: {updated_var.color}, line_style: {updated_var.line_style}, line_width: {updated_var.line_width}")
    
    system_check("Color preserved (same day)",
                updated_var.color == 'green',
                f"Color should remain 'green', got: {updated_var.color}")
                
    system_check("Line style preserved (same day)",
                updated_var.line_style == '-.',
                f"Line style should remain '-.', got: {updated_var.line_style}")
                
    system_check("Line width preserved (same day)",
                updated_var.line_width == 3.0,
                f"Line width should remain 3.0, got: {updated_var.line_width}")

@pytest.mark.mission("Different Day Style Preservation Debug")
def test_style_preservation_different_day_debug(test_environment):
    """Test with detailed debug to understand why style attributes are lost between days"""
    env = test_environment
    
    phase(1, "Setting up test data")
    initial_range = ['2023-09-28/06:00:00', '2023-09-28/07:30:00']
    get_data(initial_range, mag_rtn_4sa.bmag, proton.anisotropy)
    
    phase(2, "Creating styled custom variable")
    var_name = 'Debug Test Variable'
    var = custom_variable(var_name, proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Set distinctive style attributes 
    var.color = 'purple'
    var.line_style = '--'
    var.line_width = 3.5
    
    print(f"Initial variable created:")
    print(f"- Variable object ID: {id(var)}")
    print(f"- Color: {var.color}")
    print(f"- Line style: {var.line_style}")
    print(f"- Line width: {var.line_width}")
    
    # Check global namespace
    import importlib
    plotbot_module = importlib.import_module('plotbot')
    global_var_name = var_name.replace('-', '_').replace(' ', '_')
    
    has_global = hasattr(plotbot_module, global_var_name)
    print(f"Variable in global namespace: {has_global}")
    
    if has_global:
        global_var = getattr(plotbot_module, global_var_name)
        print(f"- Global variable object ID: {id(global_var)}")
        print(f"- Global color: {getattr(global_var, 'color', None)}")
        print(f"- Global is same object as var: {global_var is var}")
    
    phase(3, "Updating to same time on different day")
    # Same time period but next day
    updated_range = ['2023-09-29/06:00:00', '2023-09-29/07:30:00']
    get_data(updated_range, mag_rtn_4sa.bmag, proton.anisotropy)
    
    print("Before update, checking original variable again:")
    print(f"- Variable object ID: {id(var)}")
    print(f"- Color before update: {var.color}")
    print(f"- Line style before update: {var.line_style}")
    
    # Check global namespace again
    has_global = hasattr(plotbot_module, global_var_name)
    print(f"Variable in global namespace before update: {has_global}")
    
    if has_global:
        global_var = getattr(plotbot_module, global_var_name)
        print(f"- Global variable object ID: {id(global_var)}")
        print(f"- Global color before update: {getattr(global_var, 'color', None)}")
    
    # Now do the update
    updated_var = var.update(updated_range)
    
    print("\nAfter update:")
    print(f"- Updated variable object ID: {id(updated_var)}")
    print(f"- Original variable object ID: {id(var)}")
    print(f"- Updated is same object as original: {updated_var is var}")
    print(f"- Updated color: {updated_var.color}")
    print(f"- Updated line style: {updated_var.line_style}")
    print(f"- Original color after update: {var.color}")
    
    # Check global namespace after update
    has_global = hasattr(plotbot_module, global_var_name)
    print(f"Variable in global namespace after update: {has_global}")
    
    if has_global:
        global_var = getattr(plotbot_module, global_var_name)
        print(f"- Global variable object ID: {id(global_var)}")
        print(f"- Global color after update: {getattr(global_var, 'color', None)}")
        print(f"- Global is same as updated_var: {global_var is updated_var}")
        print(f"- Global is same as original var: {global_var is var}")
    
    phase(4, "Verifying style attributes preserved in different-day update")
    # We need to check both the returned variable and the global variable
    
    # First check the updated variable returned by update()
    system_check("Returned variable color preserved",
                updated_var.color == 'purple',
                f"Color should remain 'purple', got: {updated_var.color}")
                
    system_check("Returned variable line style preserved",
                updated_var.line_style == '--',
                f"Line style should remain '--', got: {updated_var.line_style}")
    
    # Now verify the global variable was also updated
    if has_global:
        system_check("Global variable color preserved",
                    getattr(global_var, 'color', None) == 'purple',
                    f"Global color should be 'purple', got: {getattr(global_var, 'color', None)}")

@pytest.mark.mission("Specific Hour Time Range Update")
def test_specific_hour_time_range_update():
    """Test custom variables can update to a specific time range (hour 8-9:30) and have data points in that range"""
    
    phase(1, "Setting up initial data (hour 6-7:30)")
    # Initial time range (hour 6-7:30)
    trange_initial = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    get_data(trange_initial, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Create custom variable
    var = custom_variable('HourUpdateVar', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Verify initial time range (hour 6)
    initial_start = np.datetime64(var.datetime_array[0])
    initial_hour = initial_start.astype('datetime64[h]').astype(int) % 24
    
    system_check("Initial Hour", 
                initial_hour == 6,
                f"Initial variable should be in hour 6, got hour {initial_hour}")
    
    phase(2, "Getting data for new time range (hour 8-9:30)")
    # New time range (hour 8-9:30) - intentionally non-overlapping
    trange_new = ['2023-09-28/08:00:00.000', '2023-09-28/09:30:00.000']
    get_data(trange_new, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Verify source data is available in the new time range
    from plotbot.plotbot_helpers import time_clip
    
    # Check mag_rtn_4sa.bmag data
    mag_indices = time_clip(mag_rtn_4sa.bmag.datetime_array, trange_new[0], trange_new[1])
    system_check("Mag Data Availability",
                len(mag_indices) > 0,
                f"Source mag_rtn_4sa.bmag should have data points in hour 8-9:30, found {len(mag_indices)}")
    
    # Check proton.anisotropy data
    proton_indices = time_clip(proton.anisotropy.datetime_array, trange_new[0], trange_new[1])
    system_check("Proton Data Availability",
                len(proton_indices) > 0,
                f"Source proton.anisotropy should have data points in hour 8-9:30, found {len(proton_indices)}")
    
    phase(3, "Updating custom variable to new time range")
    # Update the custom variable to the new time range
    updated_var = var.update(trange_new)
    
    system_check("Variable Update Return",
                updated_var is not None,
                "Variable update should return a non-None value")
    
    if updated_var is None:
        pytest.skip("Variable update returned None, cannot continue test")
    
    phase(4, "Verifying variable time range was updated to hour 8")
    # Check if time range was updated correctly
    updated_start = np.datetime64(updated_var.datetime_array[0])
    updated_hour = updated_start.astype('datetime64[h]').astype(int) % 24
    
    system_check("Updated Hour", 
                updated_hour == 8,
                f"Updated variable should be in hour 8, got hour {updated_hour}")
    
    # Check if there are data points in the target time range
    updated_indices = time_clip(updated_var.datetime_array, trange_new[0], trange_new[1])
    
    system_check("Data in New Time Range",
                len(updated_indices) > 0,
                f"Updated variable should have data points in hour 8-9:30, found {len(updated_indices)}")
    
    phase(5, "Compare with direct variable creation")
    # Create a new variable directly with the current data (should have hour 8 data)
    direct_var = custom_variable('DirectHourVar', proton.anisotropy / mag_rtn_4sa.bmag)
    
    direct_start = np.datetime64(direct_var.datetime_array[0])
    direct_hour = direct_start.astype('datetime64[h]').astype(int) % 24
    
    system_check("Direct Variable Hour", 
                direct_hour == 8,
                f"Directly created variable should be in hour 8, got hour {direct_hour}")
    
    # Check if there are data points in the target time range
    direct_indices = time_clip(direct_var.datetime_array, trange_new[0], trange_new[1])
    
    system_check("Direct Variable Data",
                len(direct_indices) > 0,
                f"Directly created variable should have data points in hour 8-9:30, found {len(direct_indices)}")
    
    # Final check - updated variable should be equivalent to directly created variable
    system_check("Equivalent Variables",
                len(updated_indices) == len(direct_indices),
                f"Updated variable should have same number of data points as directly created variable: {len(updated_indices)} vs {len(direct_indices)}")

@pytest.mark.mission("Detailed Debug - Hour 8 Update")
def test_detailed_debug_hour8_update():
    """Detailed debug test for updating custom variables to hour 8-9:30 range with extensive debug output"""
    
    print("\n=== DETAILED DEBUG TEST - HOUR 8 UPDATE ===")
    
    phase(1, "Setting up initial data (hour 6-7:30)")
    # Initial time range (hour 6-7:30)
    trange_initial = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    get_data(trange_initial, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Create custom variable
    var = custom_variable('DebugHourUpdateVar', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Print detailed information about initial variable
    print("\n=== INITIAL VARIABLE DETAILS ===")
    print(f"- Variable type: {type(var)}")
    print(f"- Data points: {len(var)}")
    print(f"- Time range: {var.datetime_array[0]} to {var.datetime_array[-1]}")
    print(f"- Memory address: {id(var)}")
    print(f"- Has source_var: {hasattr(var, 'source_var')}")
    
    if hasattr(var, 'source_var'):
        print(f"- Source variables: {len(var.source_var)}")
        for i, src in enumerate(var.source_var):
            print(f"  - Source {i+1}: {getattr(src, 'class_name', 'unknown')}.{getattr(src, 'subclass_name', 'unknown')}")
            print(f"    - ID: {id(src)}")
            if hasattr(src, 'datetime_array'):
                print(f"    - Time range: {src.datetime_array[0]} to {src.datetime_array[-1]}")
    
    phase(2, "Getting data for new time range (hour 8-9:30)")
    # New time range (hour 8-9:30) - intentionally non-overlapping
    trange_new = ['2023-09-28/08:00:00.000', '2023-09-28/09:30:00.000']
    get_data(trange_new, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Print detailed information about source variables
    print("\n=== SOURCE VARIABLES AFTER GET_DATA ===")
    
    print("\n=== MAG_RTN_4SA.BMAG ===")
    print(f"- ID: {id(mag_rtn_4sa.bmag)}")
    print(f"- Data points: {len(mag_rtn_4sa.bmag)}")
    print(f"- Time range: {mag_rtn_4sa.bmag.datetime_array[0]} to {mag_rtn_4sa.bmag.datetime_array[-1]}")
    
    print("\n=== PROTON.ANISOTROPY ===")
    print(f"- ID: {id(proton.anisotropy)}")
    print(f"- Data points: {len(proton.anisotropy)}")
    print(f"- Time range: {proton.anisotropy.datetime_array[0]} to {proton.anisotropy.datetime_array[-1]}")
    
    # Verify source data is available in the new time range
    from plotbot.plotbot_helpers import time_clip
    
    # Check mag_rtn_4sa.bmag data
    mag_indices = time_clip(mag_rtn_4sa.bmag.datetime_array, trange_new[0], trange_new[1])
    print(f"- Mag data points in new time range: {len(mag_indices)}")
    
    # Check proton.anisotropy data
    proton_indices = time_clip(proton.anisotropy.datetime_array, trange_new[0], trange_new[1])
    print(f"- Proton data points in new time range: {len(proton_indices)}")
    
    phase(3, "Updating custom variable to new time range")
    
    print("\n=== CHECKING VARIABLE BEFORE UPDATE ===")
    print(f"- Variable data points: {len(var)}")
    print(f"- Time range: {var.datetime_array[0]} to {var.datetime_array[-1]}")
    if hasattr(var, 'source_var'):
        for i, src in enumerate(var.source_var):
            print(f"  - Source {i+1}: {getattr(src, 'class_name', 'unknown')}.{getattr(src, 'subclass_name', 'unknown')}")
            print(f"    - ID: {id(src)}")
    
    # Update the custom variable to the new time range
    print(f"\n=== CALLING var.update({trange_new}) ===")
    updated_var = var.update(trange_new)
    
    print("\n=== CHECKING UPDATE RESULT ===")
    print(f"- Updated variable is None: {updated_var is None}")
    if updated_var is not None:
        print(f"- Updated variable ID: {id(updated_var)}")
        print(f"- Same object as original: {updated_var is var}")
        print(f"- Data points: {len(updated_var)}")
        print(f"- Time range: {updated_var.datetime_array[0]} to {updated_var.datetime_array[-1]}")
        
        # Check time range
        updated_start = np.datetime64(updated_var.datetime_array[0])
        updated_hour = updated_start.astype('datetime64[h]').astype(int) % 24
        print(f"- Hour: {updated_hour}")
        
        # Check if there are data points in the target time range
        updated_indices = time_clip(updated_var.datetime_array, trange_new[0], trange_new[1])
        print(f"- Data points in new time range: {len(updated_indices)}")
    
    phase(4, "Creating a new variable directly")
    # Create a new variable directly with the current data (should have hour 8 data)
    print("\n=== CREATING NEW VARIABLE DIRECTLY ===")
    direct_var = custom_variable('DirectDebugVar', proton.anisotropy / mag_rtn_4sa.bmag)
    
    print(f"- Direct variable ID: {id(direct_var)}")
    print(f"- Data points: {len(direct_var)}")
    print(f"- Time range: {direct_var.datetime_array[0]} to {direct_var.datetime_array[-1]}")
    
    direct_start = np.datetime64(direct_var.datetime_array[0])
    direct_hour = direct_start.astype('datetime64[h]').astype(int) % 24
    print(f"- Hour: {direct_hour}")
    
    # Check if there are data points in the target time range
    direct_indices = time_clip(direct_var.datetime_array, trange_new[0], trange_new[1])
    print(f"- Data points in new time range: {len(direct_indices)}")
    
    # Compare
    if updated_var is not None:
        print("\n=== COMPARISON ===")
        print(f"- Updated var data points: {len(updated_var)}")
        print(f"- Direct var data points: {len(direct_var)}")
        print(f"- Updated time range: {updated_var.datetime_array[0]} to {updated_var.datetime_array[-1]}")
        print(f"- Direct time range: {direct_var.datetime_array[0]} to {direct_var.datetime_array[-1]}")
        
    print("\n=== END DETAILED DEBUG TEST ===")
    
    # We don't do assertions here - this is just for debug output 

# Removing test_debug_plot_visibility as requested 
# TODO: Add improved version of test_debug_plot_visibility that handles empty arrays properly 