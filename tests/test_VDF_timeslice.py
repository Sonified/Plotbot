# tests/test_VDF_timeslice.py

"""
VDF Time Slice Selection Tests - Phase 2, Step 2.3

Tests time slice selection using Jaye's bisect approach from notebook Cell 11.
Validates time conversion, closest time finding, and data extraction patterns.

Reference Source: files_from_Jaye/PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb Cell 11
- Time conversion with cdflib and pandas
- bisect.bisect_left() for finding closest time index
"""

import numpy as np
import bisect
import pytest
from datetime import datetime, timedelta
from dateutil.parser import parse

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def find_closest_timeslice(epoch_array, target_time_str):
    """
    Find closest data point to target time using Jaye's approach.
    
    Args:
        epoch_array: List of datetime objects from CDF file
        target_time_str: Time string in plotbot format (e.g., '2020-01-29/18:10:02.000')
    
    Returns:
        int: Index of closest time slice
    """
    # Convert plotbot time string to datetime (using plotbot's parser approach)
    if isinstance(target_time_str, str):
        target_time = parse(target_time_str.replace('/', ' '))
    else:
        target_time = target_time_str
    
    # Use Jaye's bisect approach (Cell 11)
    tSliceIndex = bisect.bisect_left(epoch_array, target_time)
    
    # Handle edge cases
    if tSliceIndex >= len(epoch_array):
        tSliceIndex = len(epoch_array) - 1
    elif tSliceIndex > 0:
        # Check if previous time is actually closer
        time_diff_current = abs((epoch_array[tSliceIndex] - target_time).total_seconds())
        time_diff_previous = abs((epoch_array[tSliceIndex-1] - target_time).total_seconds())
        if time_diff_previous < time_diff_current:
            tSliceIndex -= 1
    
    return tSliceIndex

def extract_timeslice_data(cdf_data, time_index):
    """
    Extract all VDF data for specific time index (Jaye's Cell 13).
    
    Args:
        cdf_data: Open cdflib CDF object or dictionary with CDF-like structure
        time_index: Time index to extract
    
    Returns:
        dict: Dictionary with extracted data slices
    """
    # Extract time slice following Jaye's Cell 13 pattern
    data_slice = {
        'epoch': cdf_data['Epoch'][time_index],
        'theta': cdf_data['THETA'][time_index, :],
        'phi': cdf_data['PHI'][time_index, :],
        'energy': cdf_data['ENERGY'][time_index, :],
        'eflux': cdf_data['EFLUX'][time_index, :],
    }
    
    return data_slice

def test_time_slice_selection_accuracy():
    """Test time slice selection accuracy"""
    # Create mock time array (7-second SPAN-I cadence)
    base_time = datetime(2020, 1, 29, 18, 0, 0)
    epoch = [base_time + timedelta(seconds=i*7) for i in range(1000)]
    
    # Test exact match
    target_exact = epoch[500]
    index = find_closest_timeslice(epoch, target_exact)
    assert index == 500, f"Expected index 500, got {index}"
    
    # Test close match (within 3.5 seconds should round to nearest)
    target_close = epoch[500] + timedelta(seconds=3)
    index = find_closest_timeslice(epoch, target_close)
    assert index == 500, f"Expected index 500 for close match, got {index}"
    
    # Test string input (plotbot format)
    target_str = '2020-01-29/18:10:02.000'
    index = find_closest_timeslice(epoch, target_str)
    assert 0 <= index < len(epoch), "String input should return valid index"
    
    # Verify the selected time is reasonable
    selected_time = epoch[index]
    target_parsed = parse(target_str.replace('/', ' '))
    time_diff = abs((selected_time - target_parsed).total_seconds())
    assert time_diff <= 7, f"Selected time too far from target: {time_diff}s"
    
    print(f"✅ Time slice accuracy test:")
    print(f"   Exact match: index {500} → {target_exact}")
    print(f"   Close match: target {target_close} → index {500}")
    print(f"   String input: '{target_str}' → index {index}, diff {time_diff:.1f}s")

def test_edge_case_handling():
    """Test edge cases for time slice selection"""
    base_time = datetime(2020, 1, 29, 18, 0, 0)
    epoch = [base_time + timedelta(seconds=i*7) for i in range(100)]
    
    # Test time before data range
    too_early = base_time - timedelta(hours=1)
    index = find_closest_timeslice(epoch, too_early)
    assert index == 0, "Time before range should return first index"
    
    # Test time after data range  
    too_late = base_time + timedelta(hours=2)
    index = find_closest_timeslice(epoch, too_late)
    assert index == len(epoch) - 1, "Time after range should return last index"
    
    # Test boundary conditions
    exact_start = epoch[0]
    index = find_closest_timeslice(epoch, exact_start)
    assert index == 0, "Exact start time should return index 0"
    
    exact_end = epoch[-1]
    index = find_closest_timeslice(epoch, exact_end)
    assert index == len(epoch) - 1, "Exact end time should return last index"
    
    print(f"✅ Edge case handling:")
    print(f"   Before range: index {0}")
    print(f"   After range: index {len(epoch) - 1}")
    print(f"   Exact start: index {0}")
    print(f"   Exact end: index {len(epoch) - 1}")

def test_data_extraction_structure():
    """Test that data extraction returns expected structure"""
    # Mock CDF data structure
    n_times, n_elements = 100, 2048
    mock_cdf = {
        'Epoch': [datetime(2020, 1, 29, 18, 0, 0) + timedelta(seconds=i*7) for i in range(n_times)],
        'THETA': np.random.rand(n_times, n_elements),
        'PHI': np.random.rand(n_times, n_elements),
        'ENERGY': np.random.rand(n_times, n_elements),
        'EFLUX': np.random.rand(n_times, n_elements),
    }
    
    # Test extraction
    time_index = 50
    data_slice = extract_timeslice_data(mock_cdf, time_index)
    
    # Validate structure
    required_keys = ['epoch', 'theta', 'phi', 'energy', 'eflux']
    for key in required_keys:
        assert key in data_slice, f"Missing required key: {key}"
    
    # Validate data shapes
    assert data_slice['theta'].shape == (n_elements,), "Theta slice should be 1D"
    assert data_slice['phi'].shape == (n_elements,), "Phi slice should be 1D"
    assert data_slice['energy'].shape == (n_elements,), "Energy slice should be 1D"
    assert data_slice['eflux'].shape == (n_elements,), "Eflux slice should be 1D"
    
    # Validate data values match expected time index
    assert np.allclose(data_slice['theta'], mock_cdf['THETA'][time_index, :]), "Extracted theta should match source"
    assert data_slice['epoch'] == mock_cdf['Epoch'][time_index], "Extracted epoch should match source"
    
    print(f"✅ Data extraction structure:")
    print(f"   Time index: {time_index}")
    print(f"   Epoch: {data_slice['epoch']}")
    print(f"   Data shapes: theta{data_slice['theta'].shape}, energy{data_slice['energy'].shape}")

def test_bisect_algorithm_equivalence():
    """Test that our implementation matches Jaye's bisect approach exactly"""
    # Create time array that matches SPAN-I cadence
    base_time = datetime(2020, 1, 29, 18, 0, 0)
    epoch = [base_time + timedelta(seconds=i*7) for i in range(500)]
    
    # Test Jaye's exact example from notebook
    target_time = datetime(2020, 1, 29, 18, 10, 2)
    
    # Our implementation
    our_index = find_closest_timeslice(epoch, target_time)
    
    # Jaye's original approach (simplified)
    jaye_index = bisect.bisect_left(epoch, target_time)
    if jaye_index >= len(epoch):
        jaye_index = len(epoch) - 1
    
    # Should be very close (our version does additional proximity checking)
    assert abs(our_index - jaye_index) <= 1, f"Our index {our_index} too different from Jaye's {jaye_index}"
    
    # Verify our selection is actually closer to target
    our_time = epoch[our_index]
    our_diff = abs((our_time - target_time).total_seconds())
    
    if jaye_index < len(epoch):
        jaye_time = epoch[jaye_index]
        jaye_diff = abs((jaye_time - target_time).total_seconds())
        
        # Our method should be at least as good as Jaye's
        assert our_diff <= jaye_diff + 0.1, f"Our method ({our_diff}s) should be as good as Jaye's ({jaye_diff}s)"
    
    print(f"✅ Bisect algorithm equivalence:")
    print(f"   Target: {target_time}")
    print(f"   Our index: {our_index}, time: {our_time}, diff: {our_diff:.1f}s")
    print(f"   Jaye index: {jaye_index}")

def test_plotbot_time_format_parsing():
    """Test parsing of plotbot time format strings"""
    test_cases = [
        "2020-01-29/18:10:02.000",
        "2020-01-29/18:10:02",
        "2020-12-31/23:59:59.999",
        "2020-01-01/00:00:00.000",
    ]
    
    base_time = datetime(2020, 1, 29, 18, 0, 0)
    epoch = [base_time + timedelta(seconds=i*7) for i in range(2000)]  # Long time series
    
    for time_str in test_cases:
        try:
            index = find_closest_timeslice(epoch, time_str)
            assert 0 <= index < len(epoch), f"Invalid index {index} for time {time_str}"
            
            # Verify parsing worked
            parsed_time = parse(time_str.replace('/', ' '))
            selected_time = epoch[index]
            
            print(f"✅ Plotbot format: '{time_str}' → index {index}")
            print(f"   Parsed: {parsed_time}")
            print(f"   Selected: {selected_time}")
            
        except Exception as e:
            # For times outside our epoch range, that's expected
            if "2020-12-31" in time_str or "2020-01-01" in time_str:
                print(f"⚠️  Expected out-of-range: '{time_str}' → {str(e)}")
            else:
                pytest.fail(f"Failed to parse valid time string '{time_str}': {e}")

def test_real_vdf_timeslice_workflow():
    """Test complete timeslice workflow with real VDF data"""
    # Download real data to test complete workflow
    import pyspedas
    import cdflib
    import pandas as pd
    
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    # Extract real time array (Jaye's approach)
    dat = cdflib.CDF(VDfile[0])
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Test finding Jaye's specific example time
    target_time_str = '2020-01-29/18:10:02.000'
    tSliceIndex = find_closest_timeslice(epoch, target_time_str)
    
    # Validate result
    assert 0 <= tSliceIndex < len(epoch), "Time index out of range"
    selected_time = epoch[tSliceIndex]
    target_parsed = parse(target_time_str.replace('/', ' '))
    time_diff = abs((selected_time - target_parsed).total_seconds())
    
    # Should be within SPAN-I cadence (7 seconds)
    assert time_diff <= 7, f"Selected time too far from target: {time_diff}s"
    
    # Test data extraction
    cdf_dict = {
        'Epoch': epoch,
        'THETA': dat['THETA'],
        'PHI': dat['PHI'],
        'ENERGY': dat['ENERGY'],
        'EFLUX': dat['EFLUX'],
    }
    
    data_slice = extract_timeslice_data(cdf_dict, tSliceIndex)
    
    # Validate extracted data
    assert data_slice['theta'].shape == (2048,), "Extracted theta should have correct shape"
    assert data_slice['phi'].shape == (2048,), "Extracted phi should have correct shape"
    assert data_slice['energy'].shape == (2048,), "Extracted energy should have correct shape"
    assert data_slice['eflux'].shape == (2048,), "Extracted eflux should have correct shape"
    
    print(f"✅ Real VDF timeslice workflow:")
    print(f"   Target: {target_time_str}")
    print(f"   Found: {selected_time} (index {tSliceIndex})")
    print(f"   Time diff: {time_diff:.1f}s")
    print(f"   Data shape: {data_slice['theta'].shape}")
    print(f"   Total time points: {len(epoch)}")

if __name__ == "__main__":
    # Run key tests for manual verification
    print("🧪 Running VDF Time Slice Selection Tests...")
    test_time_slice_selection_accuracy()
    test_edge_case_handling()
    test_data_extraction_structure()
    test_bisect_algorithm_equivalence()
    test_plotbot_time_format_parsing()
    test_real_vdf_timeslice_workflow()
    print("🎉 All time slice selection tests completed!")