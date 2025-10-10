"""
Isolated tests for custom variables core concepts.
Tests individual components to verify behavior in isolation.
"""

import numpy as np
import sys

def test_1_data_cubby_resolution():
    """Test: Can we resolve variables from data_cubby using paths?"""
    print("\n" + "="*70)
    print("TEST 1: Data Cubby Resolution")
    print("="*70)
    
    import plotbot
    from plotbot.data_cubby import data_cubby
    
    # Load some data first
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Can we grab it back using path?
    br_resolved = data_cubby.grab_component('mag_rtn_4sa', 'br')
    
    print(f"Original br ID: {id(plotbot.mag_rtn_4sa.br)}")
    print(f"Resolved br ID: {id(br_resolved)}")
    print(f"Are they the same object? {br_resolved is plotbot.mag_rtn_4sa.br}")
    print(f"Data shape: {br_resolved.data.shape if br_resolved else 'None'}")
    
    if br_resolved is plotbot.mag_rtn_4sa.br:
        print("✅ PASS: Data cubby resolution works")
        return True
    else:
        print("❌ FAIL: Resolution returned different object")
        return False

def test_2_simple_operation_tracking():
    """Test: Do simple plot_manager operations create source_var?"""
    print("\n" + "="*70)
    print("TEST 2: Simple Operation source_var Tracking")
    print("="*70)
    
    import plotbot
    
    # Load data
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Do simple operation
    result = plotbot.mag_rtn_4sa.br + 180
    
    print(f"Operation: br + 180")
    print(f"Has source_var? {hasattr(result, 'source_var')}")
    if hasattr(result, 'source_var'):
        print(f"source_var: {result.source_var}")
        print(f"source_var length: {len(result.source_var) if result.source_var else 0}")
        if result.source_var and len(result.source_var) > 0:
            src = result.source_var[0]
            print(f"First source has class_name? {hasattr(src, 'class_name')}")
            print(f"First source has subclass_name? {hasattr(src, 'subclass_name')}")
            if hasattr(src, 'class_name'):
                print(f"  class_name: {src.class_name}")
            if hasattr(src, 'subclass_name'):
                print(f"  subclass_name: {src.subclass_name}")
    
    print(f"Has operation? {hasattr(result, 'operation')}")
    if hasattr(result, 'operation'):
        print(f"operation: {result.operation}")
    
    if hasattr(result, 'source_var') and result.source_var:
        print("✅ PASS: Simple operations create source_var")
        return True
    else:
        print("❌ FAIL: No source_var tracking")
        return False

def test_3_numpy_ufunc_behavior():
    """Test: Do numpy ufuncs bypass plot_manager tracking?"""
    print("\n" + "="*70)
    print("TEST 3: Numpy Ufunc Bypasses plot_manager")
    print("="*70)
    
    import plotbot
    
    # Load data
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bn, 1)
    
    # Use numpy ufunc
    result = np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
    
    print(f"Operation: np.degrees(np.arctan2(br, bn))")
    print(f"Result type: {type(result)}")
    print(f"Is plot_manager? {hasattr(result, 'plot_config')}")
    print(f"Has source_var? {hasattr(result, 'source_var')}")
    
    # The result MIGHT be plot_manager due to __array_wrap__, but source_var won't be set
    if hasattr(result, 'source_var'):
        print(f"source_var value: {result.source_var}")
    
    # Ufuncs should NOT create source_var tracking
    has_source_var = hasattr(result, 'source_var') and result.source_var is not None and len(result.source_var) > 0
    
    if not has_source_var:
        print("✅ PASS: Numpy ufuncs bypass tracking (as expected)")
        return True
    else:
        print("❌ FAIL: Unexpected source_var tracking from ufunc")
        return False

def test_4_set_plot_config_reuses_objects():
    """Test: Does set_plot_config() reuse plot_manager objects (memory optimization)?"""
    print("\n" + "="*70)
    print("TEST 4: set_plot_config() Reuses Objects")
    print("="*70)
    
    import plotbot
    from plotbot.data_cubby import data_cubby
    
    # Load data first time
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Get object ID
    mag_class = data_cubby.grab('mag_rtn_4sa')
    br_id_1 = id(mag_class.br)
    print(f"br ID after first load: {br_id_1}")
    
    # Load data again (triggers update -> set_plot_config)
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    br_id_2 = id(mag_class.br)
    print(f"br ID after second load: {br_id_2}")
    print(f"Are they the same object? {br_id_1 == br_id_2}")
    
    if br_id_1 == br_id_2:
        print("✅ PASS: Objects are reused (memory efficient, no stale references!)")
        return True
    else:
        print("❌ FAIL: Objects were recreated (inefficient, potential stale refs)")
        return False

def test_5_lambda_storage():
    """Test: Can we store and execute lambdas?"""
    print("\n" + "="*70)
    print("TEST 5: Lambda Storage and Execution")
    print("="*70)
    
    import plotbot
    from plotbot.data_cubby import data_cubby
    
    # Create a lambda
    test_lambda = lambda: plotbot.mag_rtn_4sa.br + 100
    
    # Store it
    container = data_cubby.grab('custom_variables')  # Fixed: was 'custom_class'
    if not hasattr(container, 'callables'):
        container.callables = {}
    container.callables['test_var'] = test_lambda
    
    # Load data
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Execute lambda
    result = container.callables['test_var']()
    
    print(f"Lambda stored successfully? {True}")
    print(f"Lambda execution result type: {type(result)}")
    print(f"Result shape: {result.shape if hasattr(result, 'shape') else 'N/A'}")
    
    # Check if result is correct
    br_data = np.array(plotbot.mag_rtn_4sa.br.data)
    result_data = np.array(result.data) if hasattr(result, 'data') else result
    expected = br_data + 100
    
    if hasattr(result, 'data'):
        matches = np.allclose(result_data, expected)
    else:
        matches = np.allclose(result, expected)
    
    print(f"Result matches br + 100? {matches}")
    
    if matches:
        print("✅ PASS: Lambda storage and execution works")
        return True
    else:
        print("❌ FAIL: Lambda result incorrect")
        return False

def test_6_simple_custom_variable_with_data():
    """Test: Simple custom variable when data already loaded"""
    print("\n" + "="*70)
    print("TEST 6: Simple Custom Variable (Data Pre-loaded)")
    print("="*70)
    
    import plotbot
    
    # Load data FIRST
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Now create custom variable
    test_var = plotbot.custom_variable('test_simple', plotbot.mag_rtn_4sa.br + 50)
    
    br_data = np.array(plotbot.mag_rtn_4sa.br.data)
    test_data = np.array(test_var.data)
    expected = br_data + 50
    
    print(f"br shape: {br_data.shape}")
    print(f"test_var shape: {test_data.shape}")
    print(f"Shapes match? {br_data.shape == test_data.shape}")
    
    if len(test_data) > 0:
        matches = np.allclose(test_data, expected)
        print(f"Values match br + 50? {matches}")
        
        if matches:
            print("✅ PASS: Simple custom variable works with pre-loaded data")
            return True
    
    print("❌ FAIL: Custom variable incorrect or empty")
    return False

def test_7_lambda_custom_variable():
    """Test: Lambda-based custom variable with attribute setting"""
    print("\n" + "="*70)
    print("TEST 7: Lambda Custom Variable with Attributes")
    print("="*70)
    
    import plotbot
    
    # Create lambda custom variable and set attributes
    test_lambda_var = plotbot.custom_variable('test_lambda',
        lambda: plotbot.mag_rtn_4sa.br * 2
    )
    test_lambda_var.color = 'purple'
    test_lambda_var.y_label = 'Test Lambda'
    test_lambda_var.plot_type = 'scatter'
    test_lambda_var.marker_size = 5
    
    print(f"Set attributes: color={test_lambda_var.color}, y_label={test_lambda_var.y_label}")
    
    # Load data
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.test_lambda, 2)
    
    br_data = np.array(plotbot.mag_rtn_4sa.br.data)
    lambda_data = np.array(plotbot.test_lambda.data)
    expected = br_data * 2
    
    print(f"br shape: {br_data.shape}")
    print(f"test_lambda shape: {lambda_data.shape}")
    
    # Check data is correct
    if len(lambda_data) > 0:
        matches = np.allclose(lambda_data, expected)
        print(f"Values match br * 2? {matches}")
        
        # Check attributes survived lambda evaluation
        attrs_ok = (plotbot.test_lambda.color == 'purple' and 
                   plotbot.test_lambda.y_label == 'Test Lambda' and
                   plotbot.test_lambda.plot_type == 'scatter' and
                   plotbot.test_lambda.marker_size == 5)
        print(f"Attributes preserved? {attrs_ok}")
        print(f"  color: {plotbot.test_lambda.color}")
        print(f"  y_label: {plotbot.test_lambda.y_label}")
        print(f"  marker_size: {plotbot.test_lambda.marker_size}")
        
        if matches and attrs_ok:
            print("✅ PASS: Lambda custom variable works with attributes")
            return True
    
    print("❌ FAIL: Lambda custom variable incorrect")
    return False

def test_8_2d_datetime_clipping():
    """Test: 2D datetime array clipping (EPAD fix)"""
    print("\n" + "="*70)
    print("TEST 8: 2D Datetime Array Clipping")
    print("="*70)
    
    import plotbot
    
    trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
    plotbot.plotbot(trange, plotbot.epad.strahl, 1)
    
    epad_data = np.array(plotbot.epad.strahl.data)
    epad_time = np.array(plotbot.epad.strahl.time)
    
    print(f"epad.strahl.time shape: {epad_time.shape}")
    print(f"epad.strahl.data shape: {epad_data.shape}")
    print(f"Shapes compatible? {epad_data.shape[0] == epad_time.shape[0]}")
    
    # Check no repetition
    if len(epad_data) >= 2:
        first_different = not np.array_equal(epad_data[0], epad_data[1])
        print(f"First two rows different? {first_different}")
        
        if epad_data.shape[0] == epad_time.shape[0] and first_different:
            print("✅ PASS: 2D datetime clipping works correctly")
            return True
    
    print("❌ FAIL: 2D clipping issue detected")
    return False

def run_all_tests():
    """Run all core concept tests"""
    print("\n" + "🔬" * 35)
    print(" CUSTOM VARIABLES CORE CONCEPT TESTS")
    print("🔬" * 35)
    
    tests = [
        test_1_data_cubby_resolution,
        test_2_simple_operation_tracking,
        test_3_numpy_ufunc_behavior,
        test_4_set_plot_config_reuses_objects,
        test_5_lambda_storage,
        test_6_simple_custom_variable_with_data,
        test_7_lambda_custom_variable,
        test_8_2d_datetime_clipping,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ EXCEPTION in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅" if result else "❌"
        print(f"{status} Test {i}: {test.__name__}")
    
    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


