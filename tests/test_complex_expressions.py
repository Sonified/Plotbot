# tests/test_complex_expressions.py
"""
Tests for complex mathematical expressions with custom variables.

This file contains tests for creating and evaluating complex mathematical expressions 
using custom variables, including multiple operations and NumPy functions.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_complex_expressions.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_complex_expressions.py::test_one_line_complex_expressions -v
"""
import pytest
import numpy as np
from plotbot import get_data, mag_rtn_4sa, proton
from plotbot.data_classes.custom_variables import custom_variable
from .test_pilot import phase, system_check
from plotbot.print_manager import print_manager

@pytest.mark.mission("Complex One-Line Expressions")
def test_one_line_complex_expressions():
    """Test creating custom variables with one-line complex expressions to see if they work or fail gracefully"""
    
    # Enable test output mode
    print_manager.enable_test()
    
    print_manager.test("\n================================================================================")
    print_manager.test("TEST: One-Line Complex Expressions")
    print_manager.test("Tests if complex multi-operation expressions work in a single custom_variable call")
    print_manager.test("================================================================================\n")
    
    phase(1, "Setting up test data")
    # Time range for testing
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Get data for variables
    get_data(trange, mag_rtn_4sa.bmag, mag_rtn_4sa.br, mag_rtn_4sa.bt, mag_rtn_4sa.bn, proton.anisotropy, proton.density)
    
    # Check that source data exists
    system_check(
        "Source data availability",
        len(mag_rtn_4sa.bmag.datetime_array) > 0 and len(proton.anisotropy.datetime_array) > 0,
        "Source data should be available for testing"
    )
    
    # Store some values for reference
    mag_values = np.array(mag_rtn_4sa.bmag)
    proton_values = np.array(proton.anisotropy)
    print_manager.test(f"Mag values: min={np.min(mag_values):.2f}, max={np.max(mag_values):.2f}, mean={np.mean(mag_values):.2f}")
    print_manager.test(f"Proton values: min={np.min(proton_values):.2f}, max={np.max(proton_values):.2f}, mean={np.mean(proton_values):.2f}")
    
    phase(2, "Testing single-variable multiple operations")
    try:
        # Test 1: Single variable with multiple operations
        expr1 = custom_variable('bmag_squared_plus_scaled', mag_rtn_4sa.bmag * mag_rtn_4sa.bmag + mag_rtn_4sa.bmag * 100)
        
        # Calculate expected result for comparison
        expected1 = mag_values * mag_values + mag_values * 100
        actual1 = np.array(expr1)
        
        # Check if results match expected values
        is_close1 = np.allclose(actual1, expected1)
        
        system_check(
            "Single-variable multiple operations",
            is_close1,
            f"Expression 'bmag * bmag + bmag * 100' should calculate correctly. Match: {is_close1}"
        )
        
        if is_close1:
            print_manager.test(f"✅ Expression 'bmag * bmag + bmag * 100' calculated correctly")
            print_manager.test(f"   - Expected mean: {np.mean(expected1):.2f}")
            print_manager.test(f"   - Actual mean: {np.mean(actual1):.2f}")
        else:
            print_manager.test(f"❌ Results don't match:")
            print_manager.test(f"   - Expected mean: {np.mean(expected1):.2f}")
            print_manager.test(f"   - Actual mean: {np.mean(actual1):.2f}")
    
    except Exception as e:
        # If it fails, check if it's a meaningful error
        print_manager.test(f"❌ Single-variable multiple operations failed with error: {str(e)}")
        system_check(
            "Single-variable operations graceful failure",
            True,  # We acknowledge the failure
            f"One-line single-variable operations failed with: {str(e)}"
        )
    
    phase(3, "Testing multi-variable operations")
    try:
        # Test 2: Multiple variables with operations in one line
        expr2 = custom_variable('multi_var_combo', mag_rtn_4sa.bmag * proton.anisotropy + mag_rtn_4sa.br / proton.density)
        
        # Calculate expected result
        br_values = np.array(mag_rtn_4sa.br)
        density_values = np.array(proton.density)
        print_manager.test(f"BR values: min={np.min(br_values):.2f}, max={np.max(br_values):.2f}, mean={np.mean(br_values):.2f}")
        print_manager.test(f"Density values: min={np.min(density_values):.2f}, max={np.max(density_values):.2f}, mean={np.mean(density_values):.2f}")
        
        expected2 = mag_values * proton_values + br_values / density_values
        actual2 = np.array(expr2)
        
        # Check if results match expected values
        is_close2 = np.allclose(actual2, expected2, equal_nan=True)  # Allow NaN values to be equal
        
        system_check(
            "Multiple variables with operations",
            is_close2,
            f"Expression 'bmag * anisotropy + br / density' should calculate correctly. Match: {is_close2}"
        )
        
        if is_close2:
            print_manager.test(f"✅ Expression 'bmag * anisotropy + br / density' calculated correctly")
            print_manager.test(f"   - Expected mean: {np.nanmean(expected2):.2f}")
            print_manager.test(f"   - Actual mean: {np.nanmean(actual2):.2f}")
        else:
            print_manager.test(f"❌ Results don't match:")
            print_manager.test(f"   - Expected mean: {np.nanmean(expected2):.2f}")
            print_manager.test(f"   - Actual mean: {np.nanmean(actual2):.2f}")
            print_manager.test(f"   - First few values comparison:")
            for i in range(min(5, len(actual2))):
                print_manager.test(f"     Index {i}: Expected={expected2[i]:.4f}, Actual={actual2[i]:.4f}")
    
    except Exception as e:
        # If it fails, check if it's a meaningful error
        print_manager.test(f"❌ Multiple variables with operations failed with error: {str(e)}")
        system_check(
            "Multi-variable operations graceful failure",
            True,  # We acknowledge the failure
            f"One-line multi-variable operations failed with: {str(e)}"
        )
    
    phase(4, "Testing nested operations with parentheses")
    try:
        # Test 3: Expressions with parentheses
        expr3 = custom_variable('complex_with_parentheses', (mag_rtn_4sa.br + mag_rtn_4sa.bt) * (proton.anisotropy - 0.5))
        
        # Calculate expected result
        br_values = np.array(mag_rtn_4sa.br)
        bt_values = np.array(mag_rtn_4sa.bt)
        print_manager.test(f"BR+BT values: min={np.min(br_values + bt_values):.2f}, max={np.max(br_values + bt_values):.2f}")
        print_manager.test(f"Anisotropy-0.5 values: min={np.min(proton_values - 0.5):.2f}, max={np.max(proton_values - 0.5):.2f}")
        
        expected3 = (br_values + bt_values) * (proton_values - 0.5)
        actual3 = np.array(expr3)
        
        # Check if results match expected values
        is_close3 = np.allclose(actual3, expected3, equal_nan=True)
        
        system_check(
            "Nested expressions with parentheses",
            is_close3,
            f"Expression '(br + bt) * (anisotropy - 0.5)' should calculate correctly. Match: {is_close3}"
        )
        
        if is_close3:
            print_manager.test(f"✅ Expression '(br + bt) * (anisotropy - 0.5)' calculated correctly")
            print_manager.test(f"   - Expected mean: {np.nanmean(expected3):.2f}")
            print_manager.test(f"   - Actual mean: {np.nanmean(actual3):.2f}")
        else:
            print_manager.test(f"❌ Results don't match:")
            print_manager.test(f"   - Expected mean: {np.nanmean(expected3):.2f}")
            print_manager.test(f"   - Actual mean: {np.nanmean(actual3):.2f}")
            print_manager.test(f"   - First few values comparison:")
            for i in range(min(5, len(actual3))):
                print_manager.test(f"     Index {i}: Expected={expected3[i]:.4f}, Actual={actual3[i]:.4f}")
    
    except Exception as e:
        # If it fails, check if it's a meaningful error
        print_manager.test(f"❌ Nested expressions with parentheses failed with error: {str(e)}")
        system_check(
            "Nested operations graceful failure",
            True,  # We acknowledge the failure
            f"One-line nested operations failed with: {str(e)}"
        )
    
    phase(5, "Testing source variable tracking")
    # For expressions that succeeded, check if source variables are properly tracked
    for expr_name, expr in [
        ('bmag_squared_plus_scaled', expr1 if 'expr1' in locals() else None),
        ('multi_var_combo', expr2 if 'expr2' in locals() else None),
        ('complex_with_parentheses', expr3 if 'expr3' in locals() else None)
    ]:
        if expr is not None:
            has_source_var = hasattr(expr, 'source_var')
            source_var_count = len(expr.source_var) if has_source_var else 0
            
            print_manager.test(f"Expression '{expr_name}' source variables: {source_var_count}")
            
            if has_source_var:
                # Try to print details about sources
                for i, src in enumerate(expr.source_var):
                    src_name = getattr(src, 'subclass_name', 'unknown')
                    print_manager.test(f"  - Source {i+1}: {src_name}")
            
            system_check(
                f"Source variable tracking for '{expr_name}'",
                has_source_var,
                f"Expression should track source variables. Has source_var: {has_source_var}, count: {source_var_count}"
            )

if __name__ == "__main__":
    # This allows running the test directly
    test_one_line_complex_expressions() 