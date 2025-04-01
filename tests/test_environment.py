#!/usr/bin/env python3
"""
Tests for the Plotbot environment and dependencies.

This file contains tests to verify that the Plotbot environment is correctly set up,
including tests for required dependencies, Python version, and system configuration.

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_environment.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_environment.py::test_python_version -v
"""
import sys
import os
import importlib

# Try to import pytest
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

def print_python_info():
    """Print information about the Python environment"""
    print("\n--- Python Environment Info ---")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    print("--- End Python Environment Info ---\n")

def check_import(module_name, submodule=None):
    """Check if a module can be imported and return the result"""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, '__version__'):
            result = f"✅ {module_name} version: {module.__version__}"
        else:
            result = f"✅ Successfully imported {module_name}"
            
        # Try importing a submodule if specified
        if submodule:
            sub = importlib.import_module(f"{module_name}.{submodule}")
            result += f"\n✅ Successfully imported {module_name}.{submodule}"
            
        return True, result
    except ImportError as e:
        return False, f"❌ Error importing {module_name}: {e}"

@pytest.mark.skipif(not PYTEST_AVAILABLE, reason="pytest not available")
def test_pytest_available():
    """Test that pytest is available"""
    assert PYTEST_AVAILABLE, "pytest should be available"
    
@pytest.mark.skipif(not PYTEST_AVAILABLE, reason="pytest not available")
def test_python_version():
    """Test that Python version is 3.6+"""
    assert sys.version_info.major == 3, "Python major version should be 3"
    assert sys.version_info.minor >= 6, "Python minor version should be at least 6"

@pytest.mark.skipif(not PYTEST_AVAILABLE, reason="pytest not available")
def test_matplotlib_import():
    """Test that matplotlib can be imported"""
    success, _ = check_import("matplotlib")
    assert success, "matplotlib should be importable"

@pytest.mark.skipif(not PYTEST_AVAILABLE, reason="pytest not available")
def test_numpy_import():
    """Test that numpy can be imported"""
    success, _ = check_import("numpy")
    assert success, "numpy should be importable"

@pytest.mark.skipif(not PYTEST_AVAILABLE, reason="pytest not available")
def test_plotbot_import():
    """Test that plotbot can be imported"""
    success, _ = check_import("plotbot", "custom_variables")
    assert success, "plotbot and plotbot.custom_variables should be importable"

if __name__ == "__main__":
    print("\n============== PLOTBOT ENVIRONMENT TEST ==============\n")
    print_python_info()
    
    # Check for pytest
    _, pytest_result = check_import("pytest")
    print(pytest_result)
    
    # Matplotlib
    _, matplotlib_result = check_import("matplotlib")
    print("\n" + matplotlib_result)
    
    # NumPy
    _, numpy_result = check_import("numpy")
    print("\n" + numpy_result)
    
    # Plotbot
    _, plotbot_result = check_import("plotbot", "custom_variables")
    print("\n" + plotbot_result)
    
    print("\n✅ Environment check complete!")
    
    # If pytest is available, suggest running as pytest
    if PYTEST_AVAILABLE:
        print("\n💡 TIP: For more detailed tests, run this file with pytest:")
        print("cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_environment.py -v")
    
    print("\n============== END ENVIRONMENT TEST ==============") 