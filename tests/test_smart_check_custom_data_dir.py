"""
Test that smart_check_local_pyspedas_files correctly handles custom config.data_dir.

This test verifies the fix for the bug where setting config.data_dir to something
like '../data' caused the smart check to look in '../data/data/...' (duplicate 'data').
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot.data_download_pyspedas import smart_check_local_pyspedas_files
from plotbot.config import config
from plotbot.print_manager import print_manager


@pytest.fixture
def setup_test_environment(tmp_path):
    """Set up a temporary test environment with mock data files."""
    # Save original config
    original_data_dir = config.data_dir
    
    # Create a custom data directory structure
    custom_data_dir = tmp_path / "custom_data"
    custom_data_dir.mkdir()
    
    # Set custom data_dir
    config.data_dir = str(custom_data_dir)
    
    # Create the expected directory structure for spi_sf00_l3_mom
    data_path = custom_data_dir / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / "2023"
    data_path.mkdir(parents=True)
    
    # Create a mock CDF file
    test_file = data_path / "psp_swp_spi_sf00_l3_mom_20230928_v04.cdf"
    test_file.write_text("mock CDF data")
    
    yield {
        'custom_data_dir': custom_data_dir,
        'test_file': test_file,
        'data_path': data_path
    }
    
    # Restore original config
    config.data_dir = original_data_dir


def test_smart_check_with_custom_data_dir(setup_test_environment):
    """Test that smart check finds files in custom data_dir without duplicating 'data'."""
    env = setup_test_environment
    
    # Enable our new download debug print type
    print_manager.show_download_debug = True
    
    # Time range that includes our test file
    trange = ['2023-09-28/00:00:00', '2023-09-28/23:59:59']
    
    # Run smart check
    result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)
    
    # Print result for debugging before asserting
    print_manager.download_debug(f"Result from smart_check: {result}")

    # Should find the file
    assert result is not None, f"Smart check should find the test file at {env['test_file']}"
    assert len(result) == 1, f"Should find exactly 1 file, found {len(result)}"
    
    # Verify the path is correct (no duplicate 'data' directory)
    found_path = Path(result[0])
    assert found_path.exists(), f"Found path should exist: {found_path}"
    
    # The path should NOT contain 'data/data'
    path_str = str(found_path)
    assert 'data/data' not in path_str, f"Path should not contain duplicate 'data': {path_str}"
    
    # Verify it matches our test file
    assert found_path == env['test_file'], f"Found path {found_path} != expected {env['test_file']}"
    
    print(f"✅ Test passed! Found file at correct path: {found_path}")


def test_smart_check_with_relative_data_dir(setup_test_environment):
    """Test that smart check works with relative paths like '../data'."""
    env = setup_test_environment
    
    # Change to a different directory and use relative path
    original_dir = os.getcwd()
    
    try:
        # Create a subdirectory and change to it
        subdir = env['custom_data_dir'] / "subdir"
        subdir.mkdir()
        os.chdir(subdir)
        
        # Set relative data_dir
        config.data_dir = '../'
        
        # Time range that includes our test file
        trange = ['2023-09-28/00:00:00', '2023-09-28/23:59:59']
        
        # Run smart check
        result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)
        
        # Should find the file
        assert result is not None, "Smart check should find the test file with relative path"
        assert len(result) == 1, f"Should find exactly 1 file, found {len(result)}"
        
        # Verify the path exists
        found_path = Path(result[0])
        assert found_path.exists(), f"Found path should exist: {found_path}"
        
        print(f"✅ Relative path test passed! Found file at: {found_path}")
        
    finally:
        # Restore original directory
        os.chdir(original_dir)


def test_smart_check_path_construction(setup_test_environment):
    """Test the internal path construction logic."""
    from plotbot.data_classes.data_types import get_local_path
    
    env = setup_test_environment
    
    # Get the local path using the helper function
    local_path = get_local_path('spi_sf00_l3_mom')
    
    assert local_path is not None, "get_local_path should return a path"
    
    # Should start with our custom data dir
    assert str(env['custom_data_dir']) in local_path, \
        f"Path {local_path} should contain custom data dir {env['custom_data_dir']}"
    
    # Should NOT have duplicate 'data'
    assert 'data/data' not in local_path, f"Path should not have duplicate 'data': {local_path}"
    
    print(f"✅ Path construction test passed! Path: {local_path}")


def test_smart_check_no_files_found(setup_test_environment):
    """Test that smart check correctly reports when files are not found."""
    # Time range with no corresponding files
    trange = ['2024-01-01/00:00:00', '2024-01-01/23:59:59']
    
    # Run smart check
    result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)
    
    # Should return None when no files found
    assert result is None, "Smart check should return None when no files found"
    
    print("✅ No files test passed!")


def test_smart_check_multiple_files(setup_test_environment):
    """Test that smart check finds multiple files across date range."""
    env = setup_test_environment
    
    # Create files for multiple dates
    dates = ['20230928', '20230929', '20230930']
    created_files = []
    
    for date_str in dates:
        year_str = date_str[:4]
        data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / year_str
        data_path.mkdir(parents=True, exist_ok=True)
        
        test_file = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        test_file.write_text("mock CDF data")
        created_files.append(test_file)
    
    # Time range spanning all three days
    trange = ['2023-09-28/00:00:00', '2023-09-30/23:59:59']
    
    # Run smart check
    result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)
    
    # Should find all three files
    assert result is not None, "Smart check should find files"
    assert len(result) == 3, f"Should find 3 files, found {len(result)}"
    
    # All found paths should exist
    for path_str in result:
        path = Path(path_str)
        assert path.exists(), f"Found path should exist: {path}"
        assert 'data/data' not in path_str, f"Path should not have duplicate 'data': {path_str}"
    
    print(f"✅ Multiple files test passed! Found {len(result)} files")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])

