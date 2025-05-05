# tests/test_custom_variable_operators.py
"""
Tests for custom variable operators in Plotbot.

This file contains tests for arithmetic and comparison operators applied to custom variables.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_custom_variable_operators.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_custom_variable_operators.py::test_custom_variable_operators -v
"""
import pytest
import numpy as np
from plotbot import get_data, mag_rtn_4sa, proton
from plotbot.data_classes.custom_variables import custom_variable
from plotbot.plotbot_main import plotbot as plot_main
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager

@pytest.mark.mission("Custom Variable Operators Test")
def test_custom_variable_operators():
    """Test all mathematical operators with custom variables using mag_rtn_4sa.bmag and proton.anisotropy"""
    
    print("\n================================================================================")
    print("TEST: Custom Variable Operators")
    print("Tests all mathematical operators with custom variables")
    print("================================================================================\n")
    
    phase(1, "Setting up test data")
    # Time range for testing
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Get data for variables
    get_data(trange, mag_rtn_4sa.bmag, proton.anisotropy)
    
    # Print data availability in initial range
    bmag_indices = len(mag_rtn_4sa.bmag.datetime_array)
    proton_indices = len(proton.anisotropy.datetime_array)
    print(f"Initial data: Mag has {bmag_indices} points, Proton has {proton_indices} points")
    
    # Check data values for scaling appropriately in operations
    bmag_values = np.array(mag_rtn_4sa.bmag)
    proton_values = np.array(proton.anisotropy)
    
    print(f"Mag bmag stats: min={np.min(bmag_values):.2f}, max={np.max(bmag_values):.2f}, mean={np.mean(bmag_values):.2f}")
    print(f"Proton anisotropy stats: min={np.min(proton_values):.2f}, max={np.max(proton_values):.2f}, mean={np.mean(proton_values):.2f}")
    
    phase(2, "Testing basic operators")
    # Create variables with different operators and set proper equation labels
    variables = {
        # Standard operators
        'add': custom_variable('bmag_plus_anisotropy', mag_rtn_4sa.bmag + proton.anisotropy),
        'sub': custom_variable('bmag_minus_anisotropy', mag_rtn_4sa.bmag - proton.anisotropy),
        'mul': custom_variable('bmag_times_anisotropy', mag_rtn_4sa.bmag * proton.anisotropy),
        'div': custom_variable('bmag_over_anisotropy', mag_rtn_4sa.bmag / proton.anisotropy),
        
        # Right-side operators (variables reversed)
        'radd': custom_variable('anisotropy_plus_bmag', proton.anisotropy + mag_rtn_4sa.bmag), 
        'rsub': custom_variable('anisotropy_minus_bmag', proton.anisotropy - mag_rtn_4sa.bmag),
        'rmul': custom_variable('anisotropy_times_bmag', proton.anisotropy * mag_rtn_4sa.bmag),
        'rdiv': custom_variable('anisotropy_over_bmag', proton.anisotropy / mag_rtn_4sa.bmag),
    }
    
    # Set descriptive y-axis labels in shorthand notation for equations
    equation_labels = {
        'add': 'B + TA',
        'sub': 'B - TA',
        'mul': 'B × TA',
        'div': 'B ÷ TA',
        'radd': 'TA + B',
        'rsub': 'TA - B',
        'rmul': 'TA × B',
        'rdiv': 'TA ÷ B',
    }
    
    # Apply equation labels and colors
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'brown']
    line_styles = ['-', '--', '-.', ':']
    
    for i, (op_name, var) in enumerate(variables.items()):
        var.y_label = equation_labels[op_name]
        var.color = colors[i % len(colors)]
        var.line_style = line_styles[(i//len(colors)) % len(line_styles)]
        var.line_width = 2.0
        
        # Make plots smaller (use same scale for all)
        var.panel_height = 0.5  # Reduce panel height
    
    # Verify all variables were created successfully
    for op_name, var in variables.items():
        system_check(
            f"Variable creation ({op_name})", 
            var is not None and hasattr(var, 'datetime_array') and len(var.datetime_array) > 0,
            f"Failed to create variable with operator {op_name}"
        )
        
        # Print some stats about the variable
        values = np.array(var)
        print(f"{op_name} stats: min={np.min(values):.2f}, max={np.max(values):.2f}, mean={np.mean(values):.2f}")
    
    # Verify addition and reverse addition produce the same result
    system_check(
        "Addition commutativity",
        np.allclose(np.array(variables['add']), np.array(variables['radd'])),
        "Addition should be commutative: bmag + anisotropy should equal anisotropy + bmag"
    )
    
    # Verify multiplication and reverse multiplication produce the same result
    system_check(
        "Multiplication commutativity",
        np.allclose(np.array(variables['mul']), np.array(variables['rmul'])),
        "Multiplication should be commutative: bmag * anisotropy should equal anisotropy * bmag"
    )
    
    phase(3, "Testing more complex operations")
    # Create complex expressions
    complex_variables = {}
    
    # Exponentiation (square) - using multiplication
    bmag_squared = custom_variable('bmag_squared', mag_rtn_4sa.bmag * mag_rtn_4sa.bmag)
    bmag_squared.y_label = 'B²'
    bmag_squared.color = 'darkgreen'
    bmag_squared.panel_height = 0.5  # Reduce panel height
    complex_variables['square'] = bmag_squared
    
    # Create a more complex expression using multiple operations
    complex_expr = custom_variable('complex_expression', 
                                  (mag_rtn_4sa.bmag + proton.anisotropy) / (mag_rtn_4sa.bmag * proton.anisotropy))
    complex_expr.y_label = '(B + TA) ÷ (B × TA)'
    complex_expr.color = 'darkred'
    complex_expr.panel_height = 0.5  # Reduce panel height
    complex_variables['complex'] = complex_expr
    
    # Verify complex expressions were created
    for op_name, var in complex_variables.items():
        system_check(
            f"Complex variable creation ({op_name})", 
            var is not None and hasattr(var, 'datetime_array') and len(var.datetime_array) > 0,
            f"Failed to create complex variable {op_name}"
        )
    
    phase(4, "Plotting using plotbot - with nearest interpolation")
    # Set interpolation method to nearest
    plot_manager.interp_method = 'nearest'
    
    # Set the figure width to be smaller
    plot_manager.figure_width = 8
    
    try:
        # Plot with nearest interpolation - use fewer panels
        plot_main(trange, 
               # Addition and subtraction in panel 1
               variables['add'], 1,
               variables['sub'], 1,
               # Multiplication and division in panel 2
               variables['mul'], 2,
               variables['div'], 2,
               # Reversed operations in panel 3
               variables['radd'], 3,
               variables['rsub'], 3,
               # Reversed multiplication and division in panel 4
               variables['rmul'], 4,
               variables['rdiv'], 4,
               # Complex expressions in panel 5
               complex_variables['square'], 5,
               complex_variables['complex'], 5)
        
        system_check("Nearest Interpolation Plot", True, "Successfully created plot with nearest interpolation")
    except Exception as e:
        system_check("Nearest Interpolation Plot Attempt", False, f"Failed to create plot: {str(e)}")
    
    phase(5, "Plotting using plotbot - with linear interpolation")
    # Change interpolation method to linear
    plot_manager.interp_method = 'linear'
    
    try:
        # Plot with linear interpolation - same panels as above
        plot_main(trange, 
               # Addition and subtraction in panel 1
               variables['add'], 1,
               variables['sub'], 1,
               # Multiplication and division in panel 2
               variables['mul'], 2,
               variables['div'], 2,
               # Reversed operations in panel 3
               variables['radd'], 3,
               variables['rsub'], 3,
               # Reversed multiplication and division in panel 4
               variables['rmul'], 4,
               variables['rdiv'], 4,
               # Complex expressions in panel 5
               complex_variables['square'], 5,
               complex_variables['complex'], 5)
        
        system_check("Linear Interpolation Plot", True, "Successfully created plot with linear interpolation")
    except Exception as e:
        system_check("Linear Interpolation Plot Attempt", False, f"Failed to create plot: {str(e)}")
    
    # Verify all variables were registered and are accessible
    import plotbot
    for op_name, var in variables.items():
        var_name = var.subclass_name
        try:
            # Try to access the variable by name in the plotbot module
            retrieved_var = getattr(plotbot, var_name)
            system_check(
                f"Global access ({var_name})",
                retrieved_var is not None,
                f"Variable {var_name} should be globally accessible"
            )
        except Exception as e:
            system_check(
                f"Global access ({var_name})",
                False,
                f"Failed to access variable {var_name}: {str(e)}"
            )

if __name__ == "__main__":
    # This allows running the test directly
    test_custom_variable_operators() 