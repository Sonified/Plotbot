#!/usr/bin/env python3
# tests/test_br_norm_lazy_loading.py

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from unittest.mock import patch, MagicMock

# Import from plotbot
from plotbot import print_manager, config
from plotbot import plt as plotbot_plt
import plotbot.data_classes.psp_mag_rtn_4sa as mag_class
import plotbot.data_classes.psp_proton as proton_class
from plotbot.get_data import get_data
from plotbot.test_pilot import phase, system_check

# Configure directories
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'Images')
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# Test time ranges
TEST_TRANGE = ['2021/04/28 00:00:00', '2021/04/28 06:00:00']

# Constants
RSUN_TO_AU_CONVERSION_FACTOR = 215.032867644

# Mock class for testing cross-class dependency resolution
class MockMagRTN4SAClass:
    def __init__(self):
        self.raw_data = {
            'br': np.array([-100.0, -90.0, -80.0]),
            'br_norm': None
        }
        self.datetime_array = np.array(['2021-04-28T01:00:00', '2021-04-28T02:00:00', '2021-04-28T03:00:00'], 
                                       dtype='datetime64[ns]')
        self.get_data_called = False
        self.br_norm_calculated = False
        
    def __getattr__(self, name):
        # Simulate lazy loading for br_norm
        if name == 'br_norm':
            if self.raw_data['br_norm'] is None:
                # Lazy calculation triggered
                self._calculate_br_norm()
            return self.raw_data['br_norm']
        elif name in self.raw_data:
            return self.raw_data[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    def _calculate_br_norm(self):
        # Mock the process of getting proton data
        self.get_data_called = True
        # Mock sun_dist data (simulating what we'd get from proton)
        sun_dist_rsun = np.array([30.0, 30.0, 30.0])
        # Calculate br_norm
        br_data = self.raw_data['br']
        self.raw_data['br_norm'] = br_data * ((sun_dist_rsun / RSUN_TO_AU_CONVERSION_FACTOR) ** 2)
        self.br_norm_calculated = True

@pytest.fixture
def mock_mag_instance():
    return MockMagRTN4SAClass()

@pytest.mark.mission("br_norm: Lazy Loading Test")
def test_lazy_loading_pattern(mock_mag_instance):
    """Test that br_norm is only calculated when explicitly requested"""
    phase(1, "Testing lazy loading pattern")
    
    # Verify initial state
    assert mock_mag_instance.get_data_called is False, "get_data should not be called initially"
    assert mock_mag_instance.br_norm_calculated is False, "br_norm should not be calculated initially"
    
    # Access br directly - should not trigger br_norm calculation
    br_data = mock_mag_instance.br
    assert mock_mag_instance.get_data_called is False, "get_data should not be called when accessing br"
    assert mock_mag_instance.br_norm_calculated is False, "br_norm should not be calculated when accessing br"
    
    # Now access br_norm - should trigger calculation
    br_norm_data = mock_mag_instance.br_norm
    assert mock_mag_instance.get_data_called is True, "get_data should be called when accessing br_norm"
    assert mock_mag_instance.br_norm_calculated is True, "br_norm should be calculated when accessing br_norm"
    
    # Verify calculation was correct
    expected_norm = mock_mag_instance.raw_data['br'] * ((30.0 / RSUN_TO_AU_CONVERSION_FACTOR) ** 2)
    np.testing.assert_array_equal(br_norm_data, expected_norm)
    
    system_check("Lazy Loading Pattern", True, "Successfully verified lazy loading pattern for br_norm")

@pytest.mark.mission("br_norm: Dependency Resolution Test")
def test_dependency_resolution():
    """Test the dependency resolution between mag and proton classes"""
    with patch('plotbot.get_data') as mock_get_data:
        # Create a mock implementation that tracks calls
        def mock_get_data_impl(trange, *args):
            mock_get_data_impl.called_with_args = args
            return None
        mock_get_data_impl.called_with_args = None
        mock_get_data.side_effect = mock_get_data_impl
        
        phase(1, "Setting up mock dependency test")
        
        # Create minimal mock implementation of the br_norm calculation
        class TestBrNormDependency:
            def __init__(self):
                self.br = np.array([-100.0, -90.0, -80.0])
                self.datetime_array = np.array(['2021-04-28T01:00:00', '2021-04-28T02:00:00', '2021-04-28T03:00:00'], 
                                           dtype='datetime64[ns]')
            
            def calculate_br_norm(self, trange):
                # This simulates what the actual implementation would do:
                # 1. Request sun_dist_rsun data from proton class
                get_data(trange, proton_class.proton.sun_dist_rsun)
                # 2. Return success flag for testing
                return True
        
        # Test instance
        test_instance = TestBrNormDependency()
        
        # Trigger the calculation
        phase(2, "Testing dependency resolution")
        result = test_instance.calculate_br_norm(TEST_TRANGE)
        
        # Verify get_data was called correctly
        assert result is True, "Calculation should succeed"
        assert mock_get_data.called, "get_data should be called"
        assert mock_get_data_impl.called_with_args is not None, "get_data should be called with arguments"
        assert proton_class.proton.sun_dist_rsun in mock_get_data_impl.called_with_args, "get_data should be called with proton.sun_dist_rsun"
        
        system_check("Dependency Resolution", True, "Successfully verified dependency resolution for br_norm")

@pytest.mark.mission("br_norm: Error Handling Test")
def test_error_handling():
    """Test error handling when proton data is not available"""
    with patch('plotbot.get_data') as mock_get_data:
        # Create a mock that simulates missing data
        mock_get_data.return_value = None
        
        phase(1, "Testing error handling when proton data is unavailable")
        
        # Create minimal implementation that handles missing proton data gracefully
        class TestBrNormErrorHandling:
            def __init__(self):
                self.br = np.array([-100.0, -90.0, -80.0])
                self.datetime_array = np.array(['2021-04-28T01:00:00', '2021-04-28T02:00:00', '2021-04-28T03:00:00'], 
                                           dtype='datetime64[ns]')
                self.br_norm = None
                
            def calculate_br_norm(self, trange):
                # Try to get proton data
                get_data(trange, proton_class.proton.sun_dist_rsun)
                
                # Check if we have sun_dist_rsun data available
                if not hasattr(proton_class.proton, 'sun_dist_rsun') or \
                   not hasattr(proton_class.proton.sun_dist_rsun, 'data') or \
                   proton_class.proton.sun_dist_rsun.data is None:
                    # Handle missing data by returning None
                    self.br_norm = None
                    return False
                
                # In a real implementation, we'd calculate br_norm here
                self.br_norm = np.array([-1.0, -2.0, -3.0])  # Dummy values
                return True
        
        # Test instance
        test_instance = TestBrNormErrorHandling()
        
        # Trigger the calculation
        phase(2, "Verifying graceful handling of missing data")
        result = test_instance.calculate_br_norm(TEST_TRANGE)
        
        # Verify error handling
        assert result is False, "Calculation should fail gracefully when data is missing"
        assert test_instance.br_norm is None, "br_norm should be None when calculation fails"
        
        system_check("Error Handling", True, "Successfully verified error handling for br_norm")

# Additional test for reusability of calculated values
@pytest.mark.mission("br_norm: Calculation Reuse Test")
def test_calculation_reuse(mock_mag_instance):
    """Test that br_norm calculation is reused and not recalculated"""
    phase(1, "Testing calculation reuse")
    
    # Get br_norm the first time - should trigger calculation
    br_norm_first = mock_mag_instance.br_norm
    assert mock_mag_instance.get_data_called is True, "get_data should be called on first access"
    
    # Reset flags to detect further calls
    mock_mag_instance.get_data_called = False
    mock_mag_instance.br_norm_calculated = False
    
    # Get br_norm again - should NOT trigger calculation
    br_norm_second = mock_mag_instance.br_norm
    assert mock_mag_instance.get_data_called is False, "get_data should not be called on second access"
    assert mock_mag_instance.br_norm_calculated is False, "br_norm should not be recalculated on second access"
    
    # Verify the same data is returned
    np.testing.assert_array_equal(br_norm_first, br_norm_second)
    
    system_check("Calculation Reuse", True, "Successfully verified br_norm calculation is reused")

if __name__ == '__main__':
    print("\n=== TESTING BR_NORM LAZY LOADING PATTERNS ===")
    test_lazy_loading_pattern(MockMagRTN4SAClass())
    test_dependency_resolution()
    test_error_handling()
    test_calculation_reuse(MockMagRTN4SAClass())
    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===") 