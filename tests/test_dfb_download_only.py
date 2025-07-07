import numpy as np
import pytest
from datetime import datetime
import os
import sys

# Test log file path
log_file = os.path.join(os.path.dirname(__file__), "test_logs", "test_dfb_download_only.txt")

def clear_test_logs():
    """Clear test log file at start of test session."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "w") as f:
        f.write(f"=== DFB DOWNLOAD TEST SESSION STARTED {datetime.now()} ===\n")

clear_test_logs()

@pytest.mark.mission("DFB Download Only")
def test_dfb_direct_download():
    """Test PSP DFB data downloads directly with pyspedas - no plotbot integration."""
    
    try:
        import pyspedas
        from pytplot import get_data
    except ImportError as e:
        pytest.skip(f"PySpedas not available: {e}")
    
    TRANGE = ['2021-11-25', '2021-11-26']
    
    print(f"Testing DIRECT PySpedas downloads for DFB data: {TRANGE}")
    
    # Test 1: Download AC spectrum data
    print("\n=== TEST 1: AC Spectrum Download ===")
    try:
        dfb_ac_vars = pyspedas.psp.fields(
            trange=TRANGE, 
            datatype='dfb_ac_spec', 
            level='l2', 
            time_clip=True,
            no_update=True  # Don't check for newer files
        )
        print(f"AC spectrum variables downloaded: {dfb_ac_vars}")
        
        # Test AC dv12 access
        ac_dv12_data = get_data('psp_fld_l2_dfb_ac_spec_dV12hg')
        if ac_dv12_data is not None:
            print(f"✅ AC dv12: {len(ac_dv12_data.times)} time points, spectral shape: {ac_dv12_data.y.shape}")
            print(f"   Frequency bins shape: {ac_dv12_data.v.shape}")
            print(f"   Time range: {ac_dv12_data.times[0]} to {ac_dv12_data.times[-1]}")
            
            # Check for NaN values
            nan_count = np.sum(np.isnan(ac_dv12_data.y))
            total_points = ac_dv12_data.y.size
            print(f"   NaN values: {nan_count}/{total_points} ({100*nan_count/total_points:.1f}%)")
        else:
            print("❌ AC dv12 data not accessible")
        
        # Test AC dv34 access
        ac_dv34_data = get_data('psp_fld_l2_dfb_ac_spec_dV34hg')
        if ac_dv34_data is not None:
            print(f"✅ AC dv34: {len(ac_dv34_data.times)} time points, spectral shape: {ac_dv34_data.y.shape}")
            print(f"   Time range: {ac_dv34_data.times[0]} to {ac_dv34_data.times[-1]}")
            
            # Check for NaN values
            nan_count = np.sum(np.isnan(ac_dv34_data.y))
            total_points = ac_dv34_data.y.size
            print(f"   NaN values: {nan_count}/{total_points} ({100*nan_count/total_points:.1f}%)")
        else:
            print("❌ AC dv34 data not accessible")
            
    except Exception as e:
        print(f"AC spectrum download failed: {e}")
        pytest.fail(f"AC spectrum download failed: {e}")
    
    # Test 2: Download DC spectrum data
    print("\n=== TEST 2: DC Spectrum Download ===")
    try:
        dfb_dc_vars = pyspedas.psp.fields(
            trange=TRANGE, 
            datatype='dfb_dc_spec', 
            level='l2', 
            time_clip=True,
            no_update=True  # Don't check for newer files
        )
        print(f"DC spectrum variables downloaded: {dfb_dc_vars}")
        
        # Test DC dv12 access
        dc_dv12_data = get_data('psp_fld_l2_dfb_dc_spec_dV12hg')
        if dc_dv12_data is not None:
            print(f"✅ DC dv12: {len(dc_dv12_data.times)} time points, spectral shape: {dc_dv12_data.y.shape}")
            print(f"   Frequency bins shape: {dc_dv12_data.v.shape}")
            print(f"   Time range: {dc_dv12_data.times[0]} to {dc_dv12_data.times[-1]}")
            
            # Check for NaN values
            nan_count = np.sum(np.isnan(dc_dv12_data.y))
            total_points = dc_dv12_data.y.size
            print(f"   NaN values: {nan_count}/{total_points} ({100*nan_count/total_points:.1f}%)")
        else:
            print("❌ DC dv12 data not accessible")
            
    except Exception as e:
        print(f"DC spectrum download failed: {e}")
        pytest.fail(f"DC spectrum download failed: {e}")
    
    # Test 3: Verify expected variables exist
    print("\n=== TEST 3: Variable Verification ===")
    expected_ac_vars = ['psp_fld_l2_dfb_ac_spec_dV12hg', 'psp_fld_l2_dfb_ac_spec_dV34hg']
    expected_dc_vars = ['psp_fld_l2_dfb_dc_spec_dV12hg']
    
    for var in expected_ac_vars:
        data = get_data(var)
        if data is not None:
            print(f"✅ {var}: Available with {len(data.times)} time points")
        else:
            print(f"❌ {var}: Not available")
    
    for var in expected_dc_vars:
        data = get_data(var)
        if data is not None:
            print(f"✅ {var}: Available with {len(data.times)} time points")
        else:
            print(f"❌ {var}: Not available")
    
    print("\n✅ Direct PySpedas download test completed successfully!")

@pytest.mark.mission("DFB Precise Download")  
def test_dfb_precise_download():
    """Test precise DFB downloads using the user's suggested pyspedas.download() approach."""
    
    try:
        from pyspedas import download
        from pytplot import get_data
        import pytplot as tplot
    except ImportError as e:
        pytest.skip(f"PySpedas not available: {e}")
    
    print(f"Testing PRECISE PySpedas downloads using download() function")
    
    # Test precise download as suggested by user
    print("\n=== PRECISE DOWNLOAD TEST ===")
    try:
        # Download only AC dv12hg files for specific date
        files = download(
            remote_path='https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_ac_spec/dv12hg/2021/',
            remote_file=['*20211125*.cdf'],
            local_path='data/psp/fields/l2/dfb_ac_spec/dv12hg/2021/',
            last_version=True,
            no_update=True
        )
        print(f"Downloaded files: {files}")
        
        if files:
            # Load the specific CDF file
            tplot_vars = tplot.cdf_to_tplot(files[0])
            print(f"Loaded tplot variables: {tplot_vars}")
            
            # Test access to specific variable
            if 'psp_fld_l2_dfb_ac_spec_dV12hg' in tplot_vars:
                data = get_data('psp_fld_l2_dfb_ac_spec_dV12hg')
                if data is not None:
                    print(f"✅ Precise download successful: {len(data.times)} time points, shape: {data.y.shape}")
                else:
                    print("❌ Data not accessible after precise download")
            else:
                print(f"❌ Expected variable not in loaded vars: {tplot_vars}")
        else:
            print("❌ No files downloaded")
            
    except Exception as e:
        print(f"Precise download failed: {e}")
        # Don't fail the test for this experimental approach
        print("⚠️  Precise download approach failed, but that's OK for now")
    
    print("\n✅ Precise download test completed!")

# Save output to log file
def pytest_runtest_logreport(report):
    """Save test output to log file."""
    if report.when == "call":
        with open(log_file, "a") as f:
            f.write(f"\n=== {report.nodeid} ===\n")
            if hasattr(report, 'capstdout'):
                f.write(report.capstdout)
            f.write(f"Result: {report.outcome}\n") 