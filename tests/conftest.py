"""
Configuration file for pytest.

This module contains test fixtures and setup/teardown functions for tests.
"""

import pytest
import os
import sys
import json

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary modules
from plotbot.print_manager import print_manager
from plotbot.ploptions import ploptions

# Configure print_manager for tests
print_manager.enable_test()  # Enable only test output by default
print_manager.show_time_tracking = False  # Disable time tracking
print_manager.show_error = True    # Keep error messages enabled

# Dictionary to store test results for later summarization
test_results = {}

def record_test_result(test_name, check):
    """
    Record a test result for later summarization.
    
    Args:
        test_name (str): Name of the test
        check (dict): Dictionary with test details
    """
    if test_name not in test_results:
        test_results[test_name] = []
    test_results[test_name].append(check)

# Define module-level fixtures

@pytest.fixture(scope='session')
def test_data_path():
    """Return path to test data directory."""
    return os.path.join(os.path.dirname(__file__), 'test_data')

@pytest.fixture(scope='session')
def write_test_report():
    """Write test report to file after all tests have completed."""
    yield  # This happens before the test
    
    # This happens after all tests
    if test_results:
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, 'test_report.json')
        with open(report_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\nTest report written to: {report_file}")

@pytest.fixture(autouse=True)
def reset_ploptions():
    """Reset the ploptions to default values before each test."""
    # Store original settings
    original_debug = ploptions.debug
    
    # Reset options
    ploptions.reset()
    
    yield  # Allow test to run
    
    # Restore debug setting only
    ploptions.debug = original_debug
    
# Register the write_test_report fixture to run for the whole session
pytest.main.write_test_report = write_test_report 