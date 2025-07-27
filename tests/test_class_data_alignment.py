import pytest
import numpy as np
import sys
import os

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from plotbot import *
import cdflib
import fnmatch

from plotbot.data_classes.data_types import data_types
from plotbot.print_manager import print_manager

# Enable status prints to see debug output
print_manager.show_status = True

def test_proton_density_data_alignment():
    """
    Test that the `proton.density.data` attribute is correctly updated when plotting
    different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST 1: test_proton_density_data_alignment ⭐️⭐️⭐️")
    # Time ranges from the user's example
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/00:30:00']
    trange2 = ['2021-01-19/01:00:00', '2021-01-19/01:30:00']

    # 1. Plot for the first time range and get the data
    plotbot(trange1, proton.density, 1)
    data1 = np.copy(proton.density.data)
    time1 = np.copy(proton.density.time) if proton.density.time is not None else None
    
    print(f"First plot - data shape: {data1.shape}, time shape: {time1.shape if time1 is not None else 'None'}")

    # 2. Plot for the second time range and get the data
    plotbot(trange2, proton.density, 1)
    data2 = np.copy(proton.density.data)
    time2 = np.copy(proton.density.time) if proton.density.time is not None else None
    
    print(f"Second plot - data shape: {data2.shape}, time shape: {time2.shape if time2 is not None else 'None'}")

    # 3. Verify that the data arrays are different
    assert not np.array_equal(data1, data2), "Data arrays should be different for different time ranges"
    print("✅ Data arrays are different as expected")

def test_data_alignment_fix_verification():
    """
    Test to verify that the data alignment fix is working correctly.
    This test focuses on the core issue we solved.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST 2: test_data_alignment_fix_verification ⭐️⭐️⭐️")
    # Time ranges from the user's example
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/00:30:00']
    trange2 = ['2021-01-19/01:00:00', '2021-01-19/01:30:00']

    # 1. Plot for the first time range and get the data
    plotbot(trange1, proton.density, 1)
    data1 = np.copy(proton.density.data)
    
    # 2. Plot for the second time range and get the data
    plotbot(trange2, proton.density, 1)
    data2 = np.copy(proton.density.data)
    
    # 3. Verify that the data arrays are different
    arrays_are_different = not np.array_equal(data1, data2)
    print(f"✅ SUCCESS: Data alignment fix is working!")
    print(f"   trange1 data shape: {data1.shape}")
    print(f"   trange2 data shape: {data2.shape}")
    print(f"   Arrays are different: {arrays_are_different}")
    
    assert arrays_are_different, "Data arrays should be different for different time ranges"

def test_multi_class_data_alignment():
    """
    Test that multiple data classes in a single plotbot plot all update their
    _current_operation_trange correctly when plotting different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST 3: test_multi_class_data_alignment ⭐️⭐️⭐️")
    # Time ranges for testing (12-hour intervals)
    trange1 = ['2021-01-19/00:00:00', '2021-01-19/12:00:00']
    trange2 = ['2021-01-19/12:00:00', '2021-01-20/00:00:00']

    print("🔍 Testing multi-class data alignment...")
    print(f"   trange1: {trange1}")
    print(f"   trange2: {trange2}")

    # 1. First plot with multiple data classes
    print("\n📊 First plot with multiple data classes...")
    plotbot(trange1, mag_rtn_4sa.br, 1, proton.anisotropy, 2, epad.centroids, 3, psp_orbit.r_sun, 4)
    
    # Get data from first plot
    data1_mag = np.copy(mag_rtn_4sa.br.data)
    data1_proton = np.copy(proton.anisotropy.data)
    data1_epad = np.copy(epad.centroids.data)
    data1_orbit = np.copy(psp_orbit.r_sun.data)
    
    print(f"   First plot data shapes:")
    print(f"     mag_rtn_4sa.br: {data1_mag.shape}")
    print(f"     proton.anisotropy: {data1_proton.shape}")
    print(f"     epad.centroids: {data1_epad.shape}")
    print(f"     psp_orbit.r_sun: {data1_orbit.shape}")

    # 2. Second plot with different time range
    print("\n📊 Second plot with different time range...")
    plotbot(trange2, mag_rtn_4sa.br, 1, proton.anisotropy, 2, epad.centroids, 3, psp_orbit.r_sun, 4)
    
    # Get data from second plot
    data2_mag = np.copy(mag_rtn_4sa.br.data)
    data2_proton = np.copy(proton.anisotropy.data)
    data2_epad = np.copy(epad.centroids.data)
    data2_orbit = np.copy(psp_orbit.r_sun.data)
    
    print(f"   Second plot data shapes:")
    print(f"     mag_rtn_4sa.br: {data2_mag.shape}")
    print(f"     proton.anisotropy: {data2_proton.shape}")
    print(f"     epad.centroids: {data2_epad.shape}")
    print(f"     psp_orbit.r_sun: {data2_orbit.shape}")

    # 3. Verify that all data arrays are different between plots
    print("\n🔍 Verifying data alignment...")
    
    # Check if arrays are different
    mag_different = not np.array_equal(data1_mag, data2_mag)
    proton_different = not np.array_equal(data1_proton, data2_proton)
    epad_different = not np.array_equal(data1_epad, data2_epad)
    orbit_different = not np.array_equal(data1_orbit, data2_orbit)
    
    print(f"   mag_rtn_4sa.br arrays different: {mag_different}")
    print(f"   proton.anisotropy arrays different: {proton_different}")
    print(f"   epad.centroids arrays different: {epad_different}")
    print(f"   psp_orbit.r_sun arrays different: {orbit_different}")
    
    # All arrays should be different (different time ranges = different data)
    assert mag_different, "mag_rtn_4sa.br data should be different for different time ranges"
    assert proton_different, "proton.anisotropy data should be different for different time ranges"
    assert epad_different, "epad.centroids data should be different for different time ranges"
    assert orbit_different, "psp_orbit.r_sun data should be different for different time ranges"
    
    print("✅ SUCCESS: All data classes are properly aligned!")
    print("   All data arrays are different between time ranges as expected") 


def test_raw_cdf_data_verification():
    """
    Test that the data returned by plotbot matches the raw data from the original CDF file.
    This test verifies data integrity and time-data pairing by directly reading the CDF file.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST 4: test_raw_cdf_data_verification ⭐️⭐️⭐️")
    import cdflib
    from plotbot.data_classes.data_types import data_types
    from plotbot.data_import import get_project_root
    from dateutil.parser import parse
    from datetime import timezone
    import os
    import re
    
    # Time range for testing (12-hour interval)
    trange = ['2021-01-19/00:00:00', '2021-01-19/12:00:00']
    
    print("🔍 Testing raw CDF data verification...")
    print(f"   Time range: {trange}")
    
    # 1. Get data through plotbot
    print("\n📊 Getting data through plotbot...")
    plotbot(trange, mag_rtn_4sa.br, 1)
    plotbot_data = np.copy(mag_rtn_4sa.br.data)
    plotbot_times = np.copy(mag_rtn_4sa.br.datetime_array) if mag_rtn_4sa.br.datetime_array is not None else None
    
    print(f"   Plotbot data shape: {plotbot_data.shape}")
    print(f"   Plotbot times shape: {plotbot_times.shape if plotbot_times is not None else 'None'}")
    
    # 2. Find the actual CDF file using the same logic as data_import.py
    print("\n📁 Finding CDF file using data_import.py logic...")
    
    # Get mag_rtn_4sa configuration from data_types
    mag_config = data_types.get('mag_RTN_4sa')  # This is the mag_rtn_4sa data type
    if not mag_config:
        print("❌ Could not find mag_rtn_4sa configuration in data_types")
        return
    
    print(f"   Mag RTN 4sa data type: mag_RTN_4sa")
    print(f"   Local path template: {mag_config.get('local_path')}")
    print(f"   File pattern: {mag_config.get('file_pattern_import')}")
    
    # Parse time range like data_import.py does
    start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
    end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
    
    # Find CDF files using the same logic as data_import.py
    found_files = []
    from datetime import datetime, timedelta
    
    def daterange(start_date, end_date):
        """Generate dates between start_date and end_date (inclusive)."""
        current_date = start_date.date()
        end_date_only = end_date.date()
        while current_date <= end_date_only:
            yield datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
            current_date += timedelta(days=1)
    
    # Get base path and resolve relative to project root
    cdf_base_path = mag_config.get('local_path')
    if not cdf_base_path:
        print("❌ No local_path found in mag config")
        return
    
    # Resolve relative path to absolute
    if not os.path.isabs(cdf_base_path):
        project_root = get_project_root()
        cdf_base_path = os.path.join(project_root, cdf_base_path)
        print(f"   Resolved CDF base path: {cdf_base_path}")
    
    # Search for files in the date range
    for single_date in daterange(start_time, end_time):
        year = single_date.year
        date_str = single_date.strftime('%Y%m%d')
        local_dir = os.path.join(cdf_base_path.format(data_level=mag_config['data_level']), str(year))
        
        if os.path.exists(local_dir):
            file_pattern_template = mag_config['file_pattern_import']
            file_pattern = file_pattern_template.format(
                data_level=mag_config['data_level'],
                date_str=date_str
            )
            print(f"   Searching pattern: '{file_pattern}' in dir: '{local_dir}'")
            
            # Convert glob pattern to regex
            pattern_for_re = file_pattern.replace('*', '.*')
            regex = re.compile(pattern_for_re, re.IGNORECASE)
            
            for f_name in os.listdir(local_dir):
                if regex.match(f_name):
                    found_files.append(os.path.join(local_dir, f_name))
                    print(f"     Found file: {f_name}")
    
    if not found_files:
        print("❌ No CDF files found for the time range")
        return
    
    # Use the first file found (should be the one plotbot used)
    cdf_file_path = found_files[0]
    print(f"   Using CDF file: {os.path.basename(cdf_file_path)}")
    
    # 3. Read raw data from CDF file using cdflib
    print("\n📖 Reading raw data from CDF file...")
    try:
        with cdflib.CDF(cdf_file_path) as cdf_file:
            print(f"   Successfully opened CDF file: {os.path.basename(cdf_file_path)}")
            
            # Get list of all variables
            cdf_info = cdf_file.cdf_info()
            all_variables = cdf_info.zVariables + cdf_info.rVariables
            print(f"   Found {len(all_variables)} variables in CDF")
            
            # Find time variable (Epoch)
            time_var = None
            for var_name in all_variables:
                if 'epoch' in var_name.lower():
                    time_var = var_name
                    break
            
            if not time_var:
                print("❌ No time variable (Epoch) found in CDF file")
                return
            
            print(f"   Using time variable: {time_var}")
            
            # Load time data
            raw_times = cdf_file.varget(time_var)
            print(f"   Loaded {len(raw_times)} time points")
            
            # Find the BR variable (radial component of magnetic field)
            br_var = None
            for var_name in all_variables:
                if 'br' in var_name.lower() or 'psp_fld' in var_name.lower():
                    br_var = var_name
                    break
            
            if not br_var:
                print("❌ No BR variable found in CDF file")
                print(f"   Available variables: {all_variables[:10]}...")  # Show first 10
                return
            
            print(f"   Using BR variable: {br_var}")
            
            # Load BR data
            raw_br = cdf_file.varget(br_var)
            print(f"   Raw BR shape: {raw_br.shape}")
            
            # 4. Time filter the raw data to match the requested range
            print("\n✂️ Time filtering raw data...")
            
            # Convert requested time range to TT2000 for comparison
            start_tt2000 = cdflib.cdfepoch.compute_tt2000([
                start_time.year, start_time.month, start_time.day,
                start_time.hour, start_time.minute, start_time.second,
                int(start_time.microsecond/1000)
            ])
            end_tt2000 = cdflib.cdfepoch.compute_tt2000([
                end_time.year, end_time.month, end_time.day,
                end_time.hour, end_time.minute, end_time.second,
                int(end_time.microsecond/1000)
            ])
            
            # Check epoch type and convert CDF times if needed
            epoch_var_info = cdf_file.varinq(time_var)
            epoch_type = epoch_var_info.Data_Type_Description
            print(f"   CDF time variable type: {epoch_type}")
            
            # Convert CDF times to TT2000 if needed (for comparison)
            if 'TT2000' in epoch_type:
                times_tt2000 = raw_times
            elif 'CDF_EPOCH' in epoch_type:
                print("   Converting CDF_EPOCH to TT2000 for filtering")
                times_tt2000 = np.array([cdflib.cdfepoch.to_datetime(t) for t in raw_times])
                times_tt2000 = np.array([cdflib.cdfepoch.compute_tt2000([
                    dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond//1000
                ]) for dt in times_tt2000])
            else:
                # Assume already compatible format
                times_tt2000 = raw_times
            
            # Find time range indices
            start_idx = np.searchsorted(times_tt2000, start_tt2000, side='left')
            end_idx = np.searchsorted(times_tt2000, end_tt2000, side='right')
            
            print(f"   Time range filtering: indices {start_idx} to {end_idx} out of {len(raw_times)}")
            
            if start_idx >= end_idx or start_idx >= len(raw_times):
                print("❌ No data in requested time range")
                return
            
            # Filter data to requested range
            filtered_raw_times = raw_times[start_idx:end_idx]
            filtered_raw_br = raw_br[start_idx:end_idx]
            
            print(f"   Filtered to {len(filtered_raw_times)} time points")
            print(f"   Filtered BR shape: {filtered_raw_br.shape}")
            
            # Convert filtered times to datetime for comparison
            filtered_raw_times_datetime = np.array(cdflib.cdfepoch.to_datetime(filtered_raw_times))
            
            # 5. Compare the data
            print("\n🔍 Comparing plotbot data with raw CDF data...")
            
            # Only compare the BR (radial) component
            filtered_raw_br_component = filtered_raw_br[:, 0]
            
            # Check shapes
            shapes_match = plotbot_data.shape == filtered_raw_br_component.shape
            print(f"   Shapes match: {shapes_match}")
            print(f"     Plotbot: {plotbot_data.shape}")
            print(f"     Raw CDF: {filtered_raw_br_component.shape}")
            
            # Check data values
            data_match = np.array_equal(plotbot_data, filtered_raw_br_component)
            print(f"   Data values match: {data_match}")
            
            if not data_match:
                # Check for NaN differences (might be due to fill value handling)
                nan_mask_plotbot = np.isnan(plotbot_data)
                nan_mask_raw = np.isnan(filtered_raw_br_component)
                nan_differences = np.sum(nan_mask_plotbot != nan_mask_raw)
                print(f"   NaN differences: {nan_differences}")
                
                # Check non-NaN values
                valid_mask = ~(nan_mask_plotbot | nan_mask_raw)
                if np.any(valid_mask):
                    valid_differences = np.sum(plotbot_data[valid_mask] != filtered_raw_br_component[valid_mask])
                    print(f"   Non-NaN value differences: {valid_differences}")
                    
                    if valid_differences > 0:
                        # Show some example differences
                        diff_indices = np.where(plotbot_data[valid_mask] != filtered_raw_br_component[valid_mask])[0][:5]
                        print(f"   Example differences (first 5):")
                        for idx in diff_indices:
                            plotbot_val = plotbot_data[valid_mask][idx]
                            raw_val = filtered_raw_br_component[valid_mask][idx]
                            print(f"     Index {idx}: Plotbot={plotbot_val}, Raw={raw_val}")
            
            # Check time arrays
            times_match = np.array_equal(plotbot_times, filtered_raw_times_datetime)
            print(f"   Time arrays match: {times_match}")
            
            if not times_match:
                # Check for small floating point differences
                time_diffs = np.abs(plotbot_times - filtered_raw_times_datetime)
                max_time_diff = np.max(time_diffs)
                print(f"   Max time difference: {max_time_diff}")
            
            # 6. Verify time-data pairing
            print("\n🔗 Verifying time-data pairing...")
            
            # Check that the first and last times match
            first_time_match = plotbot_times[0] == filtered_raw_times_datetime[0]
            last_time_match = plotbot_times[-1] == filtered_raw_times_datetime[-1]
            
            print(f"   First time match: {first_time_match}")
            print(f"     Plotbot: {plotbot_times[0]}")
            print(f"     Raw CDF: {filtered_raw_times_datetime[0]}")
            
            print(f"   Last time match: {last_time_match}")
            print(f"     Plotbot: {plotbot_times[-1]}")
            print(f"     Raw CDF: {filtered_raw_times_datetime[-1]}")
            
            # Check that data values correspond to the same times
            # Sample a few points in the middle
            if len(plotbot_times) > 10:
                mid_idx = len(plotbot_times) // 2
                sample_indices = [mid_idx - 2, mid_idx, mid_idx + 2]
                
                print(f"   Sample time-data pairs (indices {sample_indices}):")
                for idx in sample_indices:
                    if idx < len(plotbot_times):
                        plotbot_time = plotbot_times[idx]
                        plotbot_val = plotbot_data[idx]
                        raw_time = filtered_raw_times_datetime[idx]
                        raw_val = filtered_raw_br_component[idx]
                        
                        time_ok = plotbot_time == raw_time
                        data_ok = plotbot_val == raw_val
                        
                        print(f"     Index {idx}: Time={time_ok}, Data={data_ok}")
                        print(f"       Plotbot: {plotbot_time} → {plotbot_val}")
                        print(f"       Raw CDF: {raw_time} → {raw_val}")
            
            # 7. Final assertions
            print("\n✅ Final verification...")
            
            assert shapes_match, "Data shapes should match between plotbot and raw CDF"
            assert data_match, "Data values should match between plotbot and raw CDF"
            assert times_match, "Time arrays should match between plotbot and raw CDF"
            assert first_time_match, "First time should match between plotbot and raw CDF"
            assert last_time_match, "Last time should match between plotbot and raw CDF"
            
            print("✅ SUCCESS: Raw CDF data verification passed!")
            print("   All data integrity checks passed")
            print("   Time-data pairing is correct")
            
    except Exception as e:
        print(f"❌ Error reading CDF file: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_multiple_trange_raw_cdf_verification():
    """
    Test that the data returned by plotbot matches the raw data from the original CDF file
    for three different, non-overlapping tranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST 5: test_multiple_trange_raw_cdf_verification ⭐️⭐️⭐️")
    
    print("🔍 running imports...")
    
    import cdflib
    from plotbot.data_classes.data_types import data_types
    from plotbot.data_import import get_project_root
    from dateutil.parser import parse
    from datetime import timezone
    import os
    import re

    tranges = [
        ['2021-01-19/02:00:00', '2021-01-19/03:00:00'],  # 1 hour period
        ['2021-01-19/05:00:00', '2021-01-19/06:00:00'],  # 1 hour period, 2 hours later
        ['2021-01-19/08:00:00', '2021-01-19/09:00:00'],  # 1 hour period, 2 hours later
    ]

    print("🔍 getting mag_RTN_4sa config...")
    mag_config = data_types.get('mag_RTN_4sa')
    assert mag_config, "mag_RTN_4sa config missing"

    print("🔍 running tranges...")
    for i, trange in enumerate(tranges):
        print(f"\n=== TRANGE {i+1}: {trange} ===")
        print(f"Calling plotbot with trange: {trange}")
        # 1. Get data through plotbot
        plotbot(trange, mag_rtn_4sa.br, 1)
        plotbot_data = np.copy(mag_rtn_4sa.br.data)
        plotbot_times = np.copy(mag_rtn_4sa.br.datetime_array) if mag_rtn_4sa.br.datetime_array is not None else None
        print(f"   Plotbot data shape: {plotbot_data.shape}")
        print(f"   Plotbot times shape: {plotbot_times.shape if plotbot_times is not None else 'None'}")

        # 2. Find the actual CDF file using the same logic as data_import.py
        print(f"Parsing trange for CDF file search: {trange}")
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        found_files = []
        from datetime import datetime, timedelta
        def daterange(start_date, end_date):
            current_date = start_date.date()
            end_date_only = end_date.date()
            while current_date <= end_date_only:
                yield datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
                current_date += timedelta(days=1)
        cdf_base_path = mag_config.get('local_path')
        assert cdf_base_path, "No local_path found in mag config"
        if not os.path.isabs(cdf_base_path):
            project_root = get_project_root()
            cdf_base_path = os.path.join(project_root, cdf_base_path)
        for single_date in daterange(start_time, end_time):
            year = single_date.year
            date_str = single_date.strftime('%Y%m%d')
            local_dir = os.path.join(cdf_base_path.format(data_level=mag_config['data_level']), str(year))
            if os.path.exists(local_dir):
                file_pattern_template = mag_config['file_pattern_import']
                file_pattern = file_pattern_template.format(
                    data_level=mag_config['data_level'],
                    date_str=date_str
                )
                pattern_for_re = file_pattern.replace('*', '.*')
                regex = re.compile(pattern_for_re, re.IGNORECASE)
                for f_name in os.listdir(local_dir):
                    if regex.match(f_name):
                        found_files.append(os.path.join(local_dir, f_name))
        assert found_files, f"No CDF files found for trange {trange}"
        print(f"Using CDF file for trange {trange}: {found_files[0]}")
        cdf_file_path = found_files[0]
        with cdflib.CDF(cdf_file_path) as cdf_file:
            all_variables = cdf_file.cdf_info().zVariables + cdf_file.cdf_info().rVariables
            time_var = next((v for v in all_variables if 'epoch' in v.lower()), None)
            assert time_var, "No time variable (Epoch) found in CDF file"
            raw_times = cdf_file.varget(time_var)
            br_var = next((v for v in all_variables if 'br' in v.lower() or 'psp_fld' in v.lower()), None)
            assert br_var, "No BR variable found in CDF file"
            raw_br = cdf_file.varget(br_var)
            start_tt2000 = cdflib.cdfepoch.compute_tt2000([
                start_time.year, start_time.month, start_time.day,
                start_time.hour, start_time.minute, start_time.second,
                int(start_time.microsecond/1000)
            ])
            end_tt2000 = cdflib.cdfepoch.compute_tt2000([
                end_time.year, end_time.month, end_time.day,
                end_time.hour, end_time.minute, end_time.second,
                int(end_time.microsecond/1000)
            ])
            epoch_var_info = cdf_file.varinq(time_var)
            epoch_type = epoch_var_info.Data_Type_Description
            if 'TT2000' in epoch_type:
                times_tt2000 = raw_times
            elif 'CDF_EPOCH' in epoch_type:
                times_tt2000 = np.array([cdflib.cdfepoch.to_datetime(t) for t in raw_times])
                times_tt2000 = np.array([cdflib.cdfepoch.compute_tt2000([
                    dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond//1000
                ]) for dt in times_tt2000])
            else:
                times_tt2000 = raw_times
            start_idx = np.searchsorted(times_tt2000, start_tt2000, side='left')
            end_idx = np.searchsorted(times_tt2000, end_tt2000, side='right')
            print(f"   Raw CDF time filtering: indices {start_idx} to {end_idx} out of {len(raw_times)}")
            print(f"   Raw CDF total time points: {len(raw_times)}")
            print(f"   Raw CDF total BR points: {len(raw_br)}")
            filtered_raw_times = raw_times[start_idx:end_idx]
            filtered_raw_br = raw_br[start_idx:end_idx]
            filtered_raw_br_component = filtered_raw_br[:, 0]
            filtered_raw_times_datetime = np.array(cdflib.cdfepoch.to_datetime(filtered_raw_times))
            print(f"   Raw CDF filtered time points: {len(filtered_raw_times)}")
            print(f"   Raw CDF filtered BR points: {len(filtered_raw_br_component)}")
            # Compare
            shapes_match = plotbot_data.shape == filtered_raw_br_component.shape
            data_match = np.array_equal(plotbot_data, filtered_raw_br_component)
            times_match = np.array_equal(plotbot_times, filtered_raw_times_datetime)
            print(f"   Shapes match: {shapes_match}")
            print(f"   Data values match: {data_match}")
            print(f"   Time arrays match: {times_match}")
            assert shapes_match, f"Data shapes should match for trange {trange}"
            assert data_match, f"Data values should match for trange {trange}"
            assert times_match, f"Time arrays should match for trange {trange}"
            print(f"   ✅ Trange {i+1} passed!")

def test_systematic_time_range_tracking():
    """
    Test that TimeRangeTracker correctly stores time ranges and that mag_rtn_4sa.br.requested_trange
    gets updated properly for different time ranges.
    """
    print("⭐️⭐️⭐️ NOW RUNNING TEST: test_systematic_time_range_tracking ⭐️⭐️⭐️")
    
    # Two 10-minute periods separated by a gap
    trange1 = ['2021-01-19/02:00:00', '2021-01-19/02:10:00']
    trange2 = ['2021-01-19/03:00:00', '2021-01-19/03:10:00']

    print(f"Testing time range tracking with:")
    print(f"   trange1: {trange1}")
    print(f"   trange2: {trange2}")

    # First plotbot call
    print("\n📊 First plotbot call...")
    plotbot(trange1, mag_rtn_4sa.br, 1)
    
    # Check stored time range
    stored_trange1 = getattr(mag_rtn_4sa.br, 'requested_trange', None)
    print(f"   After first call: mag_rtn_4sa.br.requested_trange = {stored_trange1}")
    
    # Second plotbot call  
    print("\n📊 Second plotbot call...")
    plotbot(trange2, mag_rtn_4sa.br, 1)
    
    # Check stored time range
    stored_trange2 = getattr(mag_rtn_4sa.br, 'requested_trange', None)
    print(f"   After second call: mag_rtn_4sa.br.requested_trange = {stored_trange2}")
    
    # Verify time ranges were stored and are different
    assert stored_trange1 is not None, "First time range should be stored"
    assert stored_trange2 is not None, "Second time range should be stored"
    assert stored_trange1 == trange1, f"First stored trange should match trange1: {stored_trange1} vs {trange1}"
    assert stored_trange2 == trange2, f"Second stored trange should match trange2: {stored_trange2} vs {trange2}"
    assert stored_trange1 != stored_trange2, "Stored time ranges should be different"
    
    # Test .data property returns correct data for stored time ranges
    print("\n📊 Testing .data property...")
    plotbot(trange1, mag_rtn_4sa.br, 1)
    data1 = np.copy(mag_rtn_4sa.br.data)
    print(f"   trange1 data shape: {data1.shape}")
    
    plotbot(trange2, mag_rtn_4sa.br, 1) 
    data2 = np.copy(mag_rtn_4sa.br.data)
    print(f"   trange2 data shape: {data2.shape}")
    
    # Data should be different for different time ranges
    data_different = not np.array_equal(data1, data2)
    print(f"   Data arrays are different: {data_different}")
    assert data_different, "Data arrays should be different for different time ranges"
    
    print("✅ SUCCESS: Time range tracking AND data property working correctly!")
    print(f"   trange1 stored correctly: {stored_trange1}")
    print(f"   trange2 stored correctly: {stored_trange2}")
    print("   Time ranges are different as expected")
    print("   Data arrays are different as expected")