"""
Test WIND data downloads through Plotbot infrastructure.
Phase 3 validation for WIND integration.
"""

import pytest
import os
from plotbot.test_pilot import phase, system_check
from plotbot.data_download_pyspedas import download_spdf_data, PYSPEDAS_MAP
from plotbot.print_manager import print_manager

# Enable test output
print_manager.enable_test()

# Test time range (short range for quick testing)
TEST_TRANGE = ['2020-01-01/00:00:00', '2020-01-01/06:00:00']

# WIND data types to test
WIND_DATA_TYPES = [
    'wind_mfi_h2',      # Magnetic field
    'wind_swe_h1',      # Proton/alpha moments  
    'wind_swe_h5',      # Electron temperature
    'wind_3dp_pm',      # Ion parameters
    'wind_3dp_elpd'     # Electron pitch-angle distributions
]

@pytest.mark.mission("WIND PySpedas Integration")
@pytest.mark.parametrize("wind_data_type", WIND_DATA_TYPES)
def test_wind_data_download_pyspedas_integration(wind_data_type):
    """
    Test WIND data download through Plotbot's PYSPEDAS_MAP infrastructure.
    Validates Phase 3 implementation.
    """
    phase(1, f"Validate PYSPEDAS_MAP Entry for {wind_data_type}")
    
    # Check that WIND data type is in PYSPEDAS_MAP
    map_present = wind_data_type in PYSPEDAS_MAP
    system_check("PYSPEDAS_MAP Entry Present", map_present,
                f"WIND data type {wind_data_type} not found in PYSPEDAS_MAP")
    
    if not map_present:
        return  # Skip if mapping not present
        
    phase(2, f"Validate PYSPEDAS_MAP Configuration for {wind_data_type}")
    
    # Validate configuration structure
    config = PYSPEDAS_MAP[wind_data_type]
    required_keys = ['pyspedas_datatype', 'pyspedas_func', 'kwargs']
    
    for key in required_keys:
        key_present = key in config
        system_check(f"Config Key '{key}' Present", key_present,
                    f"Required key '{key}' missing from {wind_data_type} config")
        
        if not key_present:
            return  # Skip if configuration incomplete
    
    phase(3, f"Test Download Function Call for {wind_data_type}")
    
    # Test download function (should not crash)
    download_successful = False
    download_result = []
    
    try:
        print_manager.test(f"Attempting download for {wind_data_type}...")
        download_result = download_spdf_data(TEST_TRANGE, wind_data_type)
        download_successful = True
        print_manager.test(f"Download call completed for {wind_data_type}")
        
    except Exception as e:
        print_manager.test(f"Download failed with exception: {e}")
        download_successful = False
    
    system_check("Download Function Execution", download_successful,
                f"download_spdf_data() failed for {wind_data_type}")
    
    phase(4, f"Validate Download Result for {wind_data_type}")
    
    # Check result type (should be list)
    result_is_list = isinstance(download_result, list)
    system_check("Download Result Type", result_is_list,
                f"download_spdf_data() should return list, got {type(download_result)}")
    
    # Note: We don't require files to be downloaded (may not be available for test range)
    # but the function should execute without errors
    print_manager.test(f"Download result for {wind_data_type}: {len(download_result)} files")

@pytest.mark.mission("WIND PySpedas Mapping Validation")
def test_wind_pyspedas_map_completeness():
    """
    Verify all defined WIND data types are present in PYSPEDAS_MAP.
    """
    phase(1, "Check WIND Data Types Coverage")
    
    # Get WIND data types from data_types.py
    from plotbot.data_classes.data_types import data_types
    
    wind_data_types_defined = [key for key in data_types.keys() if key.startswith('wind_')]
    wind_data_types_mapped = [key for key in PYSPEDAS_MAP.keys() if key.startswith('wind_')]
    
    print_manager.test(f"WIND data types defined: {wind_data_types_defined}")
    print_manager.test(f"WIND data types mapped: {wind_data_types_mapped}")
    
    phase(2, "Validate Mapping Coverage")
    
    for wind_type in wind_data_types_defined:
        mapped = wind_type in wind_data_types_mapped
        system_check(f"Mapping for {wind_type}", mapped,
                    f"WIND data type {wind_type} defined but not mapped in PYSPEDAS_MAP")
    
    # Check counts match
    counts_match = len(wind_data_types_defined) == len(wind_data_types_mapped)
    system_check("Complete Coverage", counts_match,
                f"Defined WIND types ({len(wind_data_types_defined)}) != Mapped types ({len(wind_data_types_mapped)})")

@pytest.mark.mission("WIND PySpedas Configuration Validation")  
def test_wind_pyspedas_configuration_structure():
    """
    Validate the structure and content of WIND PYSPEDAS_MAP entries.
    """
    phase(1, "Validate WIND Configuration Structure")
    
    wind_entries = {k: v for k, v in PYSPEDAS_MAP.items() if k.startswith('wind_')}
    
    expected_wind_functions = {
        'wind_mfi_h2': 'pyspedas.wind.mfi',
        'wind_swe_h1': 'pyspedas.wind.swe', 
        'wind_swe_h5': 'pyspedas.wind.swe',
        'wind_3dp_pm': 'pyspedas.wind.threedp',
        'wind_3dp_elpd': 'pyspedas.wind.threedp'
    }
    
    for wind_key, config in wind_entries.items():
        phase(2, f"Validate Configuration for {wind_key}")
        
        # Check pyspedas function
        func_obj = config.get('pyspedas_func')
        func_correct = func_obj is not None
        system_check(f"PySpedas Function for {wind_key}", func_correct,
                    f"Missing pyspedas_func for {wind_key}")
        
        # Check kwargs structure
        kwargs = config.get('kwargs', {})
        kwargs_is_dict = isinstance(kwargs, dict)
        system_check(f"Kwargs Structure for {wind_key}", kwargs_is_dict,
                    f"kwargs should be dict for {wind_key}, got {type(kwargs)}")
        
        # Check level parameter
        # level_present = 'level' in kwargs
        # system_check(f"Level Parameter for {wind_key}", level_present,
        #             f"Missing 'level' in kwargs for {wind_key}")

        # WIND functions don't use 'level' parameter, so we check that it's NOT present
        level_absent = 'level' not in kwargs
        system_check(f"Level Parameter Absent for {wind_key}", level_absent,
                    f"WIND functions should NOT have 'level' in kwargs for {wind_key}")
        
        print_manager.test(f"✅ Configuration validated for {wind_key}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 