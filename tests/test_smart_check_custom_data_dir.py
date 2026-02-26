"""
Test that smart_check_local_pyspedas_files correctly handles custom config.data_dir,
and that download_spdf_data properly handles partial local coverage (gap downloading).

This test file covers:
1. Custom data_dir path construction (no duplicate 'data' prefix)
2. Partial coverage detection: some files local, some missing
3. Full pipeline: download_spdf_data selectively downloads only missing dates
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot.data_download_pyspedas import (
    smart_check_local_pyspedas_files, SmartCheckResult, download_spdf_data
)
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


def test_smart_check_partial_coverage(setup_test_environment):
    """Test that smart check detects missing dates when only some files exist locally.

    Reproduces the bug reported by a colleague: requesting a time range like
    2020-01-25 to 2020-02-05 when local files only exist for Jan 25 - Feb 02.
    Previously, smart check returned the partial list as if everything was fine,
    causing the tracker to stamp the full range as loaded and blocking downloads
    of the missing dates. Now it should return a SmartCheckResult with gap info.
    """
    env = setup_test_environment

    # Create files for Sep 28-30 (3 days present)
    present_dates = ['20230928', '20230929', '20230930']
    for date_str in present_dates:
        year_str = date_str[:4]
        data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / year_str
        data_path.mkdir(parents=True, exist_ok=True)
        test_file = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        test_file.write_text("mock CDF data")

    # Request a range that extends 2 days beyond what we have (Oct 1-2 missing)
    trange = ['2023-09-28/00:00:00', '2023-10-02/23:59:59']

    result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)

    # Should return a SmartCheckResult, NOT a plain list
    assert isinstance(result, SmartCheckResult), (
        f"Expected SmartCheckResult for partial coverage, got {type(result).__name__}"
    )
    assert result.all_present is False, "all_present should be False for partial coverage"

    # Should have found the 3 local files
    assert len(result.found_files) == 3, (
        f"Should find 3 local files, found {len(result.found_files)}"
    )

    # Should identify the 2 missing dates (Oct 1 and Oct 2)
    assert '20231001' in result.missing_dates, "Oct 1 should be in missing_dates"
    assert '20231002' in result.missing_dates, "Oct 2 should be in missing_dates"
    assert len(result.missing_dates) == 2, (
        f"Should have exactly 2 missing dates, got {len(result.missing_dates)}: {result.missing_dates}"
    )

    print(f"✅ Partial coverage test passed! Found {len(result.found_files)} files, "
          f"missing {len(result.missing_dates)} dates: {result.missing_dates}")


def test_smart_check_partial_coverage_gap_in_middle(setup_test_environment):
    """Test partial coverage where the gap is in the middle of the range."""
    env = setup_test_environment

    # Create files for Sep 28 and Sep 30, but NOT Sep 29 (gap in middle)
    for date_str in ['20230928', '20230930']:
        year_str = date_str[:4]
        data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / year_str
        data_path.mkdir(parents=True, exist_ok=True)
        test_file = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        test_file.write_text("mock CDF data")

    trange = ['2023-09-28/00:00:00', '2023-09-30/23:59:59']

    result = smart_check_local_pyspedas_files('spi_sf00_l3_mom', trange)

    assert isinstance(result, SmartCheckResult), (
        f"Expected SmartCheckResult for gap in middle, got {type(result).__name__}"
    )
    assert len(result.found_files) == 2, f"Should find 2 files, found {len(result.found_files)}"
    assert result.missing_dates == ['20230929'], (
        f"Should identify Sep 29 as missing, got {result.missing_dates}"
    )

    print(f"✅ Gap-in-middle test passed! Missing: {result.missing_dates}")


def test_download_spdf_partial_coverage_downloads_only_missing(setup_test_environment):
    """Full pipeline test: download_spdf_data should download ONLY missing dates.

    This reproduces the exact bug reported by a colleague:
    - Local files exist for Sep 28-30
    - Request covers Sep 28 - Oct 02
    - pyspedas should be called ONLY for the Oct 01-02 gap, not the full range
    - Return should include ALL 5 days of files
    """
    env = setup_test_environment

    # Create local files for Sep 28-30
    present_dates = ['20230928', '20230929', '20230930']
    data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / "2023"
    data_path.mkdir(parents=True, exist_ok=True)
    for date_str in present_dates:
        f = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        f.write_text("mock CDF data")

    trange = ['2023-09-28/00:00:00', '2023-10-02/23:59:59']

    # Mock pyspedas to simulate downloading the missing files
    def mock_pyspedas_spi(trange, datatype, no_update, downloadonly, notplot, **kwargs):
        """Simulate pyspedas download by creating files for the requested range."""
        from dateutil.parser import parse as dt_parse
        from datetime import timedelta

        start = dt_parse(trange[0].replace('/', ' '))
        end = dt_parse(trange[1].replace('/', ' '))
        created = []
        current = start.date()
        while current < end.date():
            date_str = current.strftime('%Y%m%d')
            year_str = str(current.year)
            file_dir = data_path.parent / year_str
            file_dir.mkdir(parents=True, exist_ok=True)
            fp = file_dir / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
            if not fp.exists():
                fp.write_text("mock CDF data - downloaded")
            created.append(str(fp))
            current += timedelta(days=1)
        return created

    # Mock _get_pyspedas_map to return our mock function
    mock_map = {
        'spi_sf00_l3_mom': {
            'pyspedas_datatype': 'spi_sf00_l3_mom',
            'pyspedas_func': mock_pyspedas_spi,
            'kwargs': {'level': 'l3'}
        }
    }

    with patch('plotbot.data_download_pyspedas._get_pyspedas_map', return_value=mock_map):
        # Also need to patch pyspedas import in _download_missing_dates
        mock_pyspedas_module = MagicMock()
        with patch.dict('sys.modules', {'pyspedas': mock_pyspedas_module}):
            result = download_spdf_data(trange, 'spi_sf00_l3_mom')

    # Should return files for all 5 days
    assert result is not None, "download_spdf_data should return files"
    assert len(result) >= 5, (
        f"Should return at least 5 files (3 local + 2 downloaded), got {len(result)}"
    )

    # Verify files for ALL dates exist
    for date_str in ['20230928', '20230929', '20230930', '20231001', '20231002']:
        matching = [f for f in result if date_str in f]
        assert len(matching) >= 1, f"Missing file for date {date_str} in result: {result}"

    print(f"✅ Full pipeline test passed! Got {len(result)} files covering all dates")


def test_download_spdf_all_local_skips_pyspedas(setup_test_environment):
    """Full pipeline test: when ALL files exist locally, pyspedas should NOT be called."""
    env = setup_test_environment

    # Create files for ALL 3 requested days
    data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / "2023"
    data_path.mkdir(parents=True, exist_ok=True)
    for date_str in ['20230928', '20230929', '20230930']:
        f = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        f.write_text("mock CDF data")

    trange = ['2023-09-28/00:00:00', '2023-09-30/23:59:59']

    # Track whether pyspedas would have been called
    pyspedas_called = False

    def mock_pyspedas_spi(**kwargs):
        nonlocal pyspedas_called
        pyspedas_called = True
        return []

    mock_map = {
        'spi_sf00_l3_mom': {
            'pyspedas_datatype': 'spi_sf00_l3_mom',
            'pyspedas_func': mock_pyspedas_spi,
            'kwargs': {'level': 'l3'}
        }
    }

    with patch('plotbot.data_download_pyspedas._get_pyspedas_map', return_value=mock_map):
        mock_pyspedas_module = MagicMock()
        with patch.dict('sys.modules', {'pyspedas': mock_pyspedas_module}):
            result = download_spdf_data(trange, 'spi_sf00_l3_mom')

    # Should return all 3 files
    assert result is not None, "Should return local files"
    assert len(result) == 3, f"Should find all 3 local files, got {len(result)}"

    # pyspedas should NOT have been called
    assert not pyspedas_called, "pyspedas should NOT be called when all files exist locally"

    print(f"✅ All-local test passed! Returned {len(result)} files, pyspedas not called")


def test_download_spdf_second_call_uses_cache(setup_test_environment):
    """Full pipeline test: after downloading missing files, a second call should find everything local.

    This is the critical regression test — the colleague's bug was that the second call
    said 'no data available' because the tracker blocked it. With the fix, the second call
    should find all files locally and skip pyspedas entirely.
    """
    env = setup_test_environment

    # Create local files for Sep 28-30
    data_path = env['custom_data_dir'] / "psp" / "sweap" / "spi" / "l3" / "spi_sf00_l3_mom" / "2023"
    data_path.mkdir(parents=True, exist_ok=True)
    for date_str in ['20230928', '20230929', '20230930']:
        f = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
        f.write_text("mock CDF data")

    trange = ['2023-09-28/00:00:00', '2023-10-02/23:59:59']

    # Mock pyspedas to create the missing files on first call
    pyspedas_call_count = 0

    def mock_pyspedas_spi(trange, datatype, no_update, downloadonly, notplot, **kwargs):
        nonlocal pyspedas_call_count
        pyspedas_call_count += 1
        from dateutil.parser import parse as dt_parse
        from datetime import timedelta
        start = dt_parse(trange[0].replace('/', ' '))
        end = dt_parse(trange[1].replace('/', ' '))
        created = []
        current = start.date()
        while current < end.date():
            date_str = current.strftime('%Y%m%d')
            fp = data_path / f"psp_swp_spi_sf00_l3_mom_{date_str}_v04.cdf"
            if not fp.exists():
                fp.write_text("mock CDF data - downloaded")
            created.append(str(fp))
            current += timedelta(days=1)
        return created

    mock_map = {
        'spi_sf00_l3_mom': {
            'pyspedas_datatype': 'spi_sf00_l3_mom',
            'pyspedas_func': mock_pyspedas_spi,
            'kwargs': {'level': 'l3'}
        }
    }

    mock_pyspedas_module = MagicMock()

    with patch('plotbot.data_download_pyspedas._get_pyspedas_map', return_value=mock_map):
        with patch.dict('sys.modules', {'pyspedas': mock_pyspedas_module}):
            # FIRST CALL: should download missing Oct 1-2
            result1 = download_spdf_data(trange, 'spi_sf00_l3_mom')
            assert pyspedas_call_count == 1, "First call should trigger one pyspedas download"
            assert len(result1) >= 5, f"First call should return 5 files, got {len(result1)}"

            # SECOND CALL: same range — all files now exist locally
            pyspedas_call_count = 0  # Reset counter
            result2 = download_spdf_data(trange, 'spi_sf00_l3_mom')

    # pyspedas should NOT be called on the second run
    assert pyspedas_call_count == 0, (
        f"Second call should NOT trigger pyspedas (all files local now), "
        f"but pyspedas was called {pyspedas_call_count} time(s)"
    )
    assert len(result2) >= 5, f"Second call should still return 5 files, got {len(result2)}"

    print(f"✅ Second-call cache test passed! First call downloaded, second call used local files only")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])

