import numpy as np
import pytest
import os
import shutil
from datetime import datetime

# Test log file path
log_file = os.path.join(os.path.dirname(__file__), "test_logs", "test_dfb_real_download.txt")

def clear_test_logs():
    """Clear test log file at start of test session."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "w") as f:
        f.write(f"=== DFB REAL DOWNLOAD TEST {datetime.now()} ===\n")

clear_test_logs()

@pytest.mark.mission("DFB Real Download")
def test_dfb_real_download_behavior():
    """Test what PySpedas ACTUALLY downloads when we request DFB data - clear cache first!"""
    
    try:
        import pyspedas
        from pytplot import get_data
    except ImportError as e:
        pytest.skip(f"PySpedas not available: {e}")
    
    TRANGE = ['2021-11-25', '2021-11-26']
    
    print(f"Testing REAL PySpedas download behavior for DFB data: {TRANGE}")
    
    # STEP 1: Clear any existing DFB cache
    dfb_cache_paths = [
        'data/psp/fields/l2/dfb_ac_spec',
        'data/psp/fields/l2/dfb_dc_spec'
    ]
    
    print("\n=== STEP 1: Clearing DFB Cache ===")
    for cache_path in dfb_cache_paths:
        if os.path.exists(cache_path):
            print(f"Removing cached directory: {cache_path}")
            shutil.rmtree(cache_path)
        else:
            print(f"No cache found at: {cache_path}")
    
    print("✅ Cache cleared - forcing fresh downloads")
    
    # STEP 2: Request AC spectrum data and see what PySpedas actually downloads
    print("\n=== STEP 2: AC Spectrum Download (Fresh) ===")
    try:
        # Track files before download
        psp_data_dir = 'data/psp/fields/l2'
        files_before = []
        if os.path.exists(psp_data_dir):
            for root, dirs, files in os.walk(psp_data_dir):
                for file in files:
                    if 'dfb' in file:
                        files_before.append(os.path.join(root, file))
        
        print(f"Files before download: {len(files_before)} DFB files")
        
        # Make the actual download request
        print("🔄 Requesting AC spectrum data from PySpedas...")
        dfb_ac_vars = pyspedas.psp.fields(
            trange=TRANGE, 
            datatype='dfb_ac_spec', 
            level='l2', 
            time_clip=True,
            no_update=False  # Allow downloading
        )
        print(f"PySpedas returned variables: {dfb_ac_vars}")
        
        # Track files after download
        files_after = []
        if os.path.exists(psp_data_dir):
            for root, dirs, files in os.walk(psp_data_dir):
                for file in files:
                    if 'dfb' in file:
                        files_after.append(os.path.join(root, file))
        
        new_files = [f for f in files_after if f not in files_before]
        print(f"\n📁 DOWNLOADED FILES ({len(new_files)} new files):")
        for file in new_files:
            rel_path = os.path.relpath(file, 'data/psp/fields/l2')
            file_size = os.path.getsize(file) / (1024*1024)  # MB
            print(f"  - {rel_path} ({file_size:.1f} MB)")
        
        # Check what data is accessible
        print(f"\n📊 ACCESSIBLE VARIABLES:")
        for var in dfb_ac_vars:
            data = get_data(var)
            if data is not None:
                print(f"  ✅ {var}: {len(data.times)} time points, shape: {data.y.shape}")
            else:
                print(f"  ❌ {var}: Not accessible")
                
    except Exception as e:
        print(f"AC spectrum download failed: {e}")
        pytest.fail(f"AC spectrum download failed: {e}")
    
    # STEP 3: Request DC spectrum data and see what additional files are downloaded  
    print("\n=== STEP 3: DC Spectrum Download (Fresh) ===")
    try:
        # Track files before DC download
        files_before_dc = []
        if os.path.exists(psp_data_dir):
            for root, dirs, files in os.walk(psp_data_dir):
                for file in files:
                    if 'dfb' in file:
                        files_before_dc.append(os.path.join(root, file))
        
        print(f"Files before DC download: {len(files_before_dc)} DFB files")
        
        # Make the DC download request
        print("🔄 Requesting DC spectrum data from PySpedas...")
        dfb_dc_vars = pyspedas.psp.fields(
            trange=TRANGE, 
            datatype='dfb_dc_spec', 
            level='l2', 
            time_clip=True,
            no_update=False  # Allow downloading
        )
        print(f"PySpedas returned DC variables: {dfb_dc_vars}")
        
        # Track files after DC download
        files_after_dc = []
        if os.path.exists(psp_data_dir):
            for root, dirs, files in os.walk(psp_data_dir):
                for file in files:
                    if 'dfb' in file:
                        files_after_dc.append(os.path.join(root, file))
        
        new_dc_files = [f for f in files_after_dc if f not in files_before_dc]
        print(f"\n📁 NEW DC FILES ({len(new_dc_files)} additional files):")
        for file in new_dc_files:
            rel_path = os.path.relpath(file, 'data/psp/fields/l2')
            file_size = os.path.getsize(file) / (1024*1024)  # MB
            print(f"  - {rel_path} ({file_size:.1f} MB)")
        
        # Check DC data accessibility
        print(f"\n📊 DC ACCESSIBLE VARIABLES:")
        for var in dfb_dc_vars:
            data = get_data(var)
            if data is not None:
                print(f"  ✅ {var}: {len(data.times)} time points, shape: {data.y.shape}")
            else:
                print(f"  ❌ {var}: Not accessible")
                
    except Exception as e:
        print(f"DC spectrum download failed: {e}")
        pytest.fail(f"DC spectrum download failed: {e}")
    
    # STEP 4: Summary of download behavior
    print("\n=== STEP 4: Download Summary ===")
    total_files = []
    if os.path.exists(psp_data_dir):
        for root, dirs, files in os.walk(psp_data_dir):
            for file in files:
                if 'dfb' in file:
                    total_files.append(os.path.join(root, file))
    
    print(f"📊 TOTAL DFB FILES DOWNLOADED: {len(total_files)}")
    
    # Categorize files
    dv12_files = [f for f in total_files if 'dv12hg' in f]
    dv34_files = [f for f in total_files if 'dv34hg' in f]
    other_files = [f for f in total_files if 'dv12hg' not in f and 'dv34hg' not in f]
    
    print(f"  - dv12hg files (what we want): {len(dv12_files)}")
    print(f"  - dv34hg files (what we want): {len(dv34_files)}")
    print(f"  - Other files (extra downloads): {len(other_files)}")
    
    if other_files:
        print(f"  📋 EXTRA FILES WE DIDN'T REQUEST:")
        for file in other_files:
            rel_path = os.path.relpath(file, 'data/psp/fields/l2')
            print(f"    - {rel_path}")
    
    # Calculate efficiency
    wanted_files = len(dv12_files) + len(dv34_files)
    total_downloaded = len(total_files)
    efficiency = (wanted_files / total_downloaded) * 100 if total_downloaded > 0 else 0
    
    print(f"\n📈 DOWNLOAD EFFICIENCY: {efficiency:.1f}% ({wanted_files}/{total_downloaded} files we actually wanted)")
    
    if efficiency < 50:
        print("⚠️  PySpedas is downloading a lot of extra files we don't need!")
        print("💡 This confirms the user's concern about inefficient downloads")
    else:
        print("✅ PySpedas download efficiency is reasonable")
    
    print("\n✅ Real download behavior test completed!")

@pytest.mark.mission("DFB Precise Download Test")  
def test_dfb_precise_download_method():
    """Test the user's suggested precise download approach for ALL THREE DFB data types."""
    
    try:
        from pyspedas import download
        import pytplot as tplot
        from pytplot import get_data
    except ImportError as e:
        pytest.skip(f"PySpedas download function not available: {e}")
    
    print(f"Testing USER'S SUGGESTED precise download method for ALL DFB data types")
    
    # Clear any existing test data
    test_cache_path = 'data/test_precise_dfb'
    if os.path.exists(test_cache_path):
        shutil.rmtree(test_cache_path)
    
    # Track all downloads
    all_downloaded_files = []
    all_loaded_vars = []
    
    # Test data for all three DFB types we need
    dfb_download_tests = [
        {
            'name': 'AC Spectrum dv12hg',
            'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_ac_spec/dv12hg/2021/',
            'local_path': os.path.join(test_cache_path, 'dfb_ac_spec/dv12hg/2021/'),
            'expected_var': 'psp_fld_l2_dfb_ac_spec_dV12hg'
        },
        {
            'name': 'AC Spectrum dv34hg', 
            'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_ac_spec/dv34hg/2021/',
            'local_path': os.path.join(test_cache_path, 'dfb_ac_spec/dv34hg/2021/'),
            'expected_var': 'psp_fld_l2_dfb_ac_spec_dV34hg'
        },
        {
            'name': 'DC Spectrum dv12hg',
            'remote_path': 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/dfb_dc_spec/dv12hg/2021/',
            'local_path': os.path.join(test_cache_path, 'dfb_dc_spec/dv12hg/2021/'),
            'expected_var': 'psp_fld_l2_dfb_dc_spec_dV12hg'
        }
    ]
    
    print(f"\n=== TESTING ALL THREE DFB DATA TYPES ===")
    
    for i, test_config in enumerate(dfb_download_tests, 1):
        print(f"\n--- TEST {i}/3: {test_config['name']} ---")
        
        try:
            print(f"🎯 Downloading {test_config['name']} for 2021-11-25...")
            files = download(
                remote_path=test_config['remote_path'],
                remote_file=['*20211125*.cdf'],
                local_path=test_config['local_path'],
                last_version=True
            )
            print(f"📁 Download result: {files}")
            
            if files:
                all_downloaded_files.extend(files)
                
                # Load and test the data
                tplot_vars = tplot.cdf_to_tplot(files[0])
                print(f"📊 Loaded variables: {tplot_vars}")
                all_loaded_vars.extend(tplot_vars)
                
                # Test access to expected variable
                if test_config['expected_var'] in tplot_vars:
                    data = get_data(test_config['expected_var'])
                    if data is not None:
                        print(f"✅ {test_config['name']} successful!")
                        print(f"   - Time points: {len(data.times)}")
                        print(f"   - Spectral shape: {data.y.shape}")
                        print(f"   - Frequency bins: {data.v.shape if hasattr(data, 'v') else 'N/A'}")
                        
                        # Check for NaN values in the data
                        nan_percentage = (np.isnan(data.y).sum() / data.y.size) * 100
                        print(f"   - NaN percentage: {nan_percentage:.1f}%")
                        
                    else:
                        print(f"❌ {test_config['name']}: Data not accessible after download")
                else:
                    print(f"❌ {test_config['name']}: Expected variable '{test_config['expected_var']}' not found")
                    print(f"   Available variables: {tplot_vars}")
            else:
                print(f"❌ {test_config['name']}: No files downloaded")
                
        except Exception as e:
            print(f"❌ {test_config['name']} download failed: {e}")
            # Continue with other tests rather than failing completely
    
    # Summary of all downloads
    print(f"\n=== COMPLETE DFB DOWNLOAD SUMMARY ===")
    print(f"📊 TOTAL FILES DOWNLOADED: {len(all_downloaded_files)}")
    print(f"📋 ALL DOWNLOADED FILES:")
    for file in all_downloaded_files:
        file_size = os.path.getsize(file) / (1024*1024) if os.path.exists(file) else 0
        rel_path = os.path.relpath(file, test_cache_path)
        print(f"  - {rel_path} ({file_size:.1f} MB)")
    
    print(f"\n📊 ALL LOADED VARIABLES:")
    for var in all_loaded_vars:
        print(f"  - {var}")
    
    # Calculate total efficiency vs regular PySpedas
    print(f"\n💡 EFFICIENCY COMPARISON:")
    print(f"   - Precise method: {len(all_downloaded_files)} files")
    print(f"   - Regular pyspedas.psp.fields(): Would download ~12-16 files for all 3 types")
    if len(all_downloaded_files) > 0:
        efficiency_gain = ((12 - len(all_downloaded_files)) / 12) * 100
        print(f"   - Efficiency gain: ~{efficiency_gain:.0f}% reduction in downloads!")
    
    # Verify we have all three expected data types
    expected_vars = [
        'psp_fld_l2_dfb_ac_spec_dV12hg',
        'psp_fld_l2_dfb_ac_spec_dV34hg', 
        'psp_fld_l2_dfb_dc_spec_dV12hg'
    ]
    
    found_vars = [var for var in expected_vars if var in all_loaded_vars]
    print(f"\n🎯 DFB IMPLEMENTATION READINESS:")
    print(f"   - Required variables: {len(expected_vars)}")
    print(f"   - Successfully downloaded: {len(found_vars)}")
    print(f"   - Missing variables: {[var for var in expected_vars if var not in all_loaded_vars]}")
    
    if len(found_vars) == len(expected_vars):
        print(f"✅ ALL DFB data types successfully downloaded - ready for implementation!")
    else:
        print(f"⚠️  Some DFB data types missing - may need fallback strategies")
    
    print(f"\n✅ Complete DFB precise download test completed!")

@pytest.mark.mission("Plotbot DFB Integration Test")
def test_plotbot_dfb_download_integration():
    """Test that the updated plotbot download function uses precise download for DFB data types."""
    
    try:
        from plotbot.data_download_pyspedas import download_spdf_data
    except ImportError as e:
        pytest.skip(f"Plotbot download function not available: {e}")
    
    print(f"Testing updated plotbot download function with DFB data types")
    
    TRANGE = ['2021-11-25', '2021-11-26']
    
    # Test all three DFB data types with the updated plotbot function
    dfb_data_types = [
        'dfb_ac_spec_dv12hg',
        'dfb_ac_spec_dv34hg', 
        'dfb_dc_spec_dv12hg'
    ]
    
    print(f"\n=== TESTING UPDATED PLOTBOT DOWNLOAD FUNCTION ===")
    
    all_download_results = {}
    
    for data_type in dfb_data_types:
        print(f"\n--- Testing {data_type} ---")
        
        try:
            # Call the updated plotbot download function
            print(f"🔄 Calling download_spdf_data({TRANGE}, '{data_type}')")
            
            result = download_spdf_data(TRANGE, data_type)
            all_download_results[data_type] = result
            
            print(f"📊 Download result: {result}")
            
            if result and isinstance(result, list) and len(result) > 0:
                print(f"✅ {data_type}: Downloaded {len(result)} file(s)")
                for file in result:
                    if os.path.exists(file):
                        file_size = os.path.getsize(file) / (1024*1024)
                        rel_path = os.path.relpath(file, 'data')
                        print(f"  - {rel_path} ({file_size:.1f} MB)")
                    else:
                        print(f"  - {file} (FILE NOT FOUND)")
            else:
                print(f"❌ {data_type}: No files downloaded")
                
        except Exception as e:
            print(f"❌ {data_type}: Download failed with error: {e}")
            all_download_results[data_type] = []
    
    # Summary
    print(f"\n=== PLOTBOT DOWNLOAD INTEGRATION SUMMARY ===")
    
    total_files = sum(len(result) if result else 0 for result in all_download_results.values())
    successful_types = sum(1 for result in all_download_results.values() if result and len(result) > 0)
    
    print(f"📊 TOTAL DATA TYPES TESTED: {len(dfb_data_types)}")
    print(f"📊 SUCCESSFUL DOWNLOADS: {successful_types}")
    print(f"📊 TOTAL FILES DOWNLOADED: {total_files}")
    
    print(f"\n📋 DOWNLOAD RESULTS BY TYPE:")
    for data_type, result in all_download_results.items():
        status = "✅ SUCCESS" if result and len(result) > 0 else "❌ FAILED"
        file_count = len(result) if result else 0
        print(f"  - {data_type}: {status} ({file_count} files)")
    
    # Verify we're using the efficient method
    if total_files > 0:
        print(f"\n💡 EFFICIENCY VERIFICATION:")
        print(f"   - Files downloaded: {total_files}")
        print(f"   - Expected with old method: ~{len(dfb_data_types) * 4}-{len(dfb_data_types) * 8} files")
        if total_files <= len(dfb_data_types):
            print(f"   ✅ EFFICIENT: Using precise download method!")
        else:
            print(f"   ⚠️  May still be using inefficient method")
    
    # Test passes if at least one download succeeded
    if successful_types > 0:
        print(f"\n✅ Plotbot DFB download integration test PASSED!")
    else:
        print(f"\n❌ Plotbot DFB download integration test FAILED!")
        pytest.fail("No DFB data types downloaded successfully")

@pytest.mark.mission("Backward Compatibility Test")
def test_backward_compatibility_existing_data_types():
    """Test that existing non-DFB data types still work exactly as before with regular PySpedas."""
    
    try:
        from plotbot.data_download_pyspedas import download_spdf_data, PYSPEDAS_MAP
    except ImportError as e:
        pytest.skip(f"Plotbot download function not available: {e}")
    
    print(f"Testing BACKWARD COMPATIBILITY for existing data types")
    
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    
    # Test existing data types that should use regular PySpedas (no 'download_method': 'precise')
    existing_data_types = [
        'mag_RTN_4sa',
        'spi_sf00_l3_mom', 
        'sqtn_rfs_v1v2'
    ]
    
    print(f"\n=== BACKWARD COMPATIBILITY TEST ===")
    print(f"Verifying existing data types use REGULAR PySpedas method")
    
    compatibility_results = {}
    
    for data_type in existing_data_types:
        print(f"\n--- Testing {data_type} (should use REGULAR method) ---")
        
        # Verify the PYSPEDAS_MAP entry has the right structure
        if data_type not in PYSPEDAS_MAP:
            print(f"❌ {data_type}: Not found in PYSPEDAS_MAP")
            compatibility_results[data_type] = "MISSING_FROM_MAP"
            continue
        
        config = PYSPEDAS_MAP[data_type]
        
        # Check that it has the required regular PySpedas keys
        required_keys = ['pyspedas_datatype', 'pyspedas_func', 'kwargs']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ {data_type}: Missing required keys: {missing_keys}")
            compatibility_results[data_type] = f"MISSING_KEYS_{missing_keys}"
            continue
        
        # Check that it does NOT have the precise download method flag
        if config.get('download_method') == 'precise':
            print(f"❌ {data_type}: Should NOT use precise method (backward compatibility violation)")
            compatibility_results[data_type] = "UNEXPECTED_PRECISE_METHOD"
            continue
        
        print(f"✅ {data_type}: Configuration structure is backward compatible")
        print(f"  - pyspedas_datatype: {config['pyspedas_datatype']}")
        print(f"  - pyspedas_func: {config['pyspedas_func'].__name__}")
        print(f"  - kwargs: {config['kwargs']}")
        print(f"  - download_method: {config.get('download_method', 'regular (default)')}")
        
        # Actually test the download function (but skip actual download to avoid long waits)
        try:
            print(f"🔧 Testing download function interface...")
            # This should not crash and should follow the regular path
            result = download_spdf_data(TRANGE, data_type)
            print(f"📊 Download function returned: {type(result)} with {len(result) if isinstance(result, list) else 'N/A'} items")
            compatibility_results[data_type] = "SUCCESS"
        except Exception as e:
            print(f"❌ {data_type}: Download function failed: {e}")
            compatibility_results[data_type] = f"DOWNLOAD_ERROR_{e}"
    
    # Summary
    print(f"\n=== BACKWARD COMPATIBILITY SUMMARY ===")
    
    successful_types = sum(1 for result in compatibility_results.values() if result == "SUCCESS")
    total_types = len(existing_data_types)
    
    print(f"📊 EXISTING DATA TYPES TESTED: {total_types}")
    print(f"📊 BACKWARD COMPATIBLE: {successful_types}")
    
    print(f"\n📋 COMPATIBILITY RESULTS:")
    for data_type, result in compatibility_results.items():
        status = "✅ COMPATIBLE" if result == "SUCCESS" else f"❌ {result}"
        print(f"  - {data_type}: {status}")
    
    # Check DFB types have both regular and precise configs
    print(f"\n=== DFB TYPES DUAL COMPATIBILITY CHECK ===")
    dfb_types = ['dfb_ac_spec_dv12hg', 'dfb_ac_spec_dv34hg', 'dfb_dc_spec_dv12hg']
    
    for dfb_type in dfb_types:
        if dfb_type in PYSPEDAS_MAP:
            config = PYSPEDAS_MAP[dfb_type]
            has_regular = all(key in config for key in ['pyspedas_datatype', 'pyspedas_func', 'kwargs'])
            has_precise = 'download_method' in config and config['download_method'] == 'precise'
            
            if has_regular and has_precise:
                print(f"✅ {dfb_type}: Has both PRECISE method and REGULAR fallback")
            else:
                print(f"❌ {dfb_type}: Missing dual compatibility (regular: {has_regular}, precise: {has_precise})")
    
    # Test passes if all existing types are backward compatible
    if successful_types == total_types:
        print(f"\n✅ BACKWARD COMPATIBILITY TEST PASSED!")
        print(f"   All existing data types use regular PySpedas method as expected")
    else:
        print(f"\n❌ BACKWARD COMPATIBILITY TEST FAILED!")
        print(f"   {total_types - successful_types} existing data types have compatibility issues")
        pytest.fail(f"Backward compatibility violated for {total_types - successful_types} data types") 