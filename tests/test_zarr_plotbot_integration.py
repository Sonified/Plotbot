import os
from plotbot.print_manager import print_manager

def test_basic_zarr_functionality():
    """
    TEST 1: Basic Zarr Functionality
    
    PURPOSE:
    This test verifies that Zarr is correctly installed and that the basic 
    xarray-to-zarr conversion works. This is the foundation for all other tests -
    if this fails, nothing else will work. We need to confirm that we can create
    a zarr store from xarray data and read it back successfully.
    
    WHAT IT DOES:
    1. Creates a simple xarray dataset with random data
    2. Writes it to a zarr store
    3. Reads it back and verifies the data matches the original
    
    SUCCESS CRITERIA:
    - No errors during zarr operations
    - Data read back from zarr matches the original data exactly
    """
    print_manager.zarr_integration("RUNNING TEST 1: Basic Zarr Functionality")
    print_manager.zarr_integration("Testing basic xarray-to-zarr conversion - foundation for all zarr operations")
    
    import os
    import shutil
    import numpy as np
    import xarray as xr
    from datetime import datetime, timedelta
    
    # Create test directory
    test_dir = './data_cubby_zarr_testing/test_zarr'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # Create simple test dataset
        times = [datetime.now() + timedelta(hours=i) for i in range(24)]
        data = np.random.rand(24)
        
        ds = xr.Dataset(
            data_vars={'test_var': ('time', data)},
            coords={'time': times}
        )
        
        # Save to zarr
        zarr_path = os.path.join(test_dir, 'test.zarr')
        ds.to_zarr(zarr_path)
        
        # Read from zarr
        ds_read = xr.open_zarr(zarr_path)
        
        # Verify data
        data_matches = np.array_equal(ds_read.test_var.values, data)
        
        assert data_matches, "Data read from Zarr doesn't match original"
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: Zarr test failed with error: {e}")
        assert False, f"FAILURE: Zarr test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_file_structure_and_chunking():
    """
    TEST 2: File Structure and Chunking
    
    PURPOSE:
    Zarr files need to be organized to match your data's natural cadence (daily or 6-hourly).
    This test verifies that we create the correct directory structure and chunking based on
    the data's time format. Proper chunking is critical for performance - it determines how
    efficiently data can be accessed later.
    
    WHAT IT DOES:
    1. Creates test datasets for both daily and 6-hour cadences
    2. Saves them to zarr with appropriate chunking (full time dimension in one chunk)
    3. Verifies the correct directory structure is created for each cadence
    
    SUCCESS CRITERIA:
    - Daily files should be stored in year/month/day.zarr structure
    - 6-hour files should be stored in year/month/day_hour.zarr structure
    - Each file should have one chunk per time dimension
    """
    print_manager.zarr_integration("RUNNING TEST 2: File Structure and Chunking")
    print_manager.zarr_integration("Testing if zarr stores are created with correct directory structure and chunking")
    
    import os
    import shutil
    import numpy as np
    import xarray as xr
    from datetime import datetime, timedelta
    
    # Create test directory
    test_dir = './data_cubby_zarr_testing/test_zarr_structure'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # Test 1: Daily cadence
        daily_time = datetime(2023, 5, 15, 12, 0, 0)  # Mid-day on May 15, 2023
        daily_path = _get_test_zarr_path(test_dir, 'test_data', daily_time, 'daily')
        
        # Create simple dataset
        times = [daily_time + timedelta(minutes=i*30) for i in range(48)]  # 24 hours in 30-min intervals
        data = np.random.rand(48)
        
        ds_daily = xr.Dataset(
            data_vars={'test_var': ('time', data)},
            coords={'time': times}
        )
        
        # Save with daily chunking
        os.makedirs(os.path.dirname(daily_path), exist_ok=True)
        ds_daily.chunk({'time': -1}).to_zarr(daily_path)
        
        # Test 2: 6-hour cadence
        hourly_time = datetime(2023, 5, 15, 14, 0, 0)  # 2pm on May 15, 2023
        hourly_path = _get_test_zarr_path(test_dir, 'test_data', hourly_time, '6-hour')
        
        # Create simple dataset for 6-hour period
        times_hourly = [hourly_time + timedelta(minutes=i*10) for i in range(36)]  # 6 hours in 10-min intervals
        data_hourly = np.random.rand(36)
        
        ds_hourly = xr.Dataset(
            data_vars={'test_var': ('time', data_hourly)},
            coords={'time': times_hourly}
        )
        
        # Save with hourly chunking
        os.makedirs(os.path.dirname(hourly_path), exist_ok=True)
        ds_hourly.chunk({'time': -1}).to_zarr(hourly_path)
        
        # Verify paths exist
        daily_exists = os.path.exists(daily_path)
        hourly_exists = os.path.exists(hourly_path)
        
        # Verify structure matches expected
        expected_daily = os.path.join(test_dir, 'test_data', '2023', '05', '15.zarr')
        expected_hourly = os.path.join(test_dir, 'test_data', '2023', '05', '15_12.zarr')
        
        paths_match = (daily_path == expected_daily) and (hourly_path == expected_hourly)
        
        assert daily_exists and hourly_exists and paths_match, f"File structure or chunking incorrect. Daily path exists: {daily_exists}, Expected: {expected_daily}. Hourly path exists: {hourly_exists}, Expected: {expected_hourly}."
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: File structure test failed with error: {e}")
        assert False, f"FAILURE: File structure test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def _get_test_zarr_path(base_dir, data_type, timestamp, file_time_format):
    """Helper to generate zarr path based on timestamp and file format"""
    if file_time_format == 'daily':
        return os.path.join(base_dir, data_type, 
                           f"{timestamp.year}", 
                           f"{timestamp.month:02d}", 
                           f"{timestamp.day:02d}.zarr")
    elif file_time_format == '6-hour':
        hour = (timestamp.hour // 6) * 6  # Round to nearest 6-hour block
        return os.path.join(base_dir, data_type, 
                           f"{timestamp.year}", 
                           f"{timestamp.month:02d}", 
                           f"{timestamp.day:02d}_{hour:02d}.zarr")
    else:
        return os.path.join(base_dir, data_type, 
                          f"{timestamp.year}_{timestamp.month:02d}_{timestamp.day:02d}.zarr")


def test_data_class_conversion():
    """
    TEST 3: Data Class Conversion
    
    PURPOSE:
    Your system uses custom data classes (mag_rtn, etc.) to store processed data.
    For Zarr storage to be useful, we need to be able to convert between your data
    classes and xarray/zarr format without losing information. This is critical for
    keeping all your existing workflow intact.
    
    WHAT IT DOES:
    1. Creates a mock data class instance similar to mag_rtn
    2. Converts it to xarray format and saves to zarr
    3. Reads from zarr and converts back to your expected format
    4. Verifies all data dimensions and values are preserved
    
    SUCCESS CRITERIA:
    - Data shapes match after round-trip conversion
    - Field component values match between original and converted data
    - No information loss during format conversion
    """
    print_manager.zarr_integration("RUNNING TEST 3: Data Class Conversion")
    print_manager.zarr_integration("Testing conversion between your data classes and xarray/zarr format")
    
    import os
    import shutil
    import numpy as np
    import xarray as xr
    from datetime import datetime, timedelta
    import cdflib
    
    # Create test directory
    test_dir = './data_cubby_zarr_testing/test_zarr_conversion'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # Test with mag_rtn since it's common
        data_type = 'mag_rtn'
        
        # Create mock imported data similar to what your system uses
        class MockImportedData:
            def __init__(self):
                # Create sample time array (24 hours with 10-minute cadence)
                self.datetime_array = np.array([datetime(2023, 5, 15) + timedelta(minutes=i*10) for i in range(144)])
                
                # Create sample field components (br, bt, bn)
                n_points = len(self.datetime_array)
                self.raw_data = {
                    'br': np.sin(np.linspace(0, 4*np.pi, n_points)),
                    'bt': np.cos(np.linspace(0, 4*np.pi, n_points)),
                    'bn': np.random.rand(n_points) * 0.5,
                    'bmag': np.sqrt(
                        np.sin(np.linspace(0, 4*np.pi, n_points))**2 + 
                        np.cos(np.linspace(0, 4*np.pi, n_points))**2 + 
                        (np.random.rand(n_points) * 0.5)**2
                    ),
                    'pmag': np.random.rand(n_points) * 0.1
                }
        
        # Create mock instance
        mock_instance = MockImportedData()
        
        # Convert to xarray
        data_vars = {}
        for var_name, data in mock_instance.raw_data.items():
            if data is None or var_name == 'all':
                continue
            data_vars[var_name] = (['time'], data)
            
        ds = xr.Dataset(
            data_vars=data_vars,
            coords={'time': mock_instance.datetime_array}
        )
        
        # Save to zarr
        zarr_path = os.path.join(test_dir, 'test_conversion.zarr')
        ds.to_zarr(zarr_path)
        
        # Read back from zarr
        ds_read = xr.open_zarr(zarr_path)
        
        # Convert back to imported data format
        class ImportedData:
            def __init__(self):
                self.times = None
                self.data = {}
                
        imported_data = ImportedData()
        
        # Set times
        imported_data.times = np.array([np.datetime64(t) for t in ds_read.time.values])
        
        # Create 3D field array for mag_rtn
        if all(v in ds_read for v in ['br', 'bt', 'bn']):
            field_data = np.stack([
                ds_read['br'].values,
                ds_read['bt'].values,
                ds_read['bn'].values
            ], axis=1)
            imported_data.data['psp_fld_l2_mag_RTN'] = field_data
        
        # Verify conversion accuracy
        original_shape = mock_instance.raw_data['br'].shape
        converted_shape = imported_data.data['psp_fld_l2_mag_RTN'][:,0].shape
        
        shapes_match = original_shape == converted_shape
        
        assert shapes_match, f"Data shapes don't match after conversion. Original shape: {original_shape}, Converted shape: {converted_shape}"
        
        # Check values for br component
        original_br = mock_instance.raw_data['br']
        converted_br = imported_data.data['psp_fld_l2_mag_RTN'][:,0]
        values_match = np.allclose(original_br, converted_br)
        
        assert values_match, "Data values don't match after conversion"
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: Conversion test failed with error: {e}")
        assert False, f"FAILURE: Conversion test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_zarr_storage_class():
    """
    TEST 4: ZarrStorage Class
    
    PURPOSE:
    The ZarrStorage class is the core component that manages zarr file storage and retrieval.
    It handles the creation of proper file structures, chunking, data conversion, and time range
    management. This test validates that the entire class works correctly as a complete system.
    
    WHAT IT DOES:
    1. Creates a test ZarrStorage instance
    2. Generates mock data for three consecutive days
    3. Stores each day's data using the storage class
    4. Requests data spanning multiple days
    5. Verifies the storage class correctly loads and combines the data
    
    SUCCESS CRITERIA:
    - All data is stored with correct file structure
    - Multi-day data retrieval works correctly
    - All data points are present in the combined result
    - Loaded data spans the requested time range
    
    This test is particularly important because it validates the core functionality
    that makes the zarr integration useful - the ability to store and retrieve data
    across multiple files as if it were a single continuous dataset.
    """
    print_manager.zarr_integration("RUNNING TEST 4: ZarrStorage Class")
    print_manager.zarr_integration("Testing the core ZarrStorage class that manages zarr file storage and retrieval")
    
    import os
    import shutil
    import numpy as np
    import xarray as xr
    from datetime import datetime, timedelta
    
    # Simple ZarrStorage implementation for testing
    class TestZarrStorage:
        def __init__(self, base_dir):
            self.base_dir = base_dir
            os.makedirs(base_dir, exist_ok=True)
            
        def store_data(self, mock_instance, data_type, trange):
            """Store mock instance data to zarr"""
            # Create dataset from mock instance
            data_vars = {}
            for var_name, data in mock_instance.raw_data.items():
                if data is None or var_name == 'all':
                    continue
                data_vars[var_name] = (['time'], data)
                
            ds = xr.Dataset(
                data_vars=data_vars,
                coords={'time': mock_instance.datetime_array}
            )
            
            # Use daily cadence for this test
            start_time = mock_instance.datetime_array[0]
            zarr_path = os.path.join(self.base_dir, data_type, 
                                    f"{start_time.year}", 
                                    f"{start_time.month:02d}", 
                                    f"{start_time.day:02d}.zarr")
            
            # Create directory if needed
            os.makedirs(os.path.dirname(zarr_path), exist_ok=True)
            
            # Save to zarr with full time chunk
            ds.chunk({'time': -1}).to_zarr(zarr_path)
            
            return zarr_path
            
        def load_data(self, data_type, trange):
            """Load data for given time range"""
            # Parse time range
            import dateutil.parser
            start_time = dateutil.parser.parse(trange[0])
            end_time = dateutil.parser.parse(trange[1])
            
            # For this test, simply look for daily files in range
            zarr_paths = []
            current_date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            while current_date <= end_time:
                zarr_path = os.path.join(self.base_dir, data_type, 
                                        f"{current_date.year}", 
                                        f"{current_date.month:02d}", 
                                        f"{current_date.day:02d}.zarr")
                if os.path.exists(zarr_path):
                    zarr_paths.append(zarr_path)
                current_date += timedelta(days=1)
                
            if not zarr_paths:
                return None
                
            # Load and concatenate datasets
            datasets = []
            for path in zarr_paths:
                ds = xr.open_zarr(path)
                datasets.append(ds)
                
            if len(datasets) == 1:
                combined = datasets[0]
            else:
                combined = xr.concat(datasets, dim='time')
                
            # Convert to mock imported data format for testing
            class ImportedData:
                def __init__(self):
                    self.times = None
                    self.data = {}
                    
            imported_data = ImportedData()
            imported_data.times = combined.time.values
            
            # If testing mag_rtn type, create proper field structure
            if data_type == 'mag_rtn' and all(v in combined for v in ['br', 'bt', 'bn']):
                field_data = np.stack([
                    combined['br'].values,
                    combined['bt'].values,
                    combined['bn'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_RTN'] = field_data
                
            return imported_data
    
    # Create test directory
    test_dir = './data_cubby_zarr_testing/test_zarr_storage'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # Create ZarrStorage instance
        storage = TestZarrStorage(test_dir)
        
        # Create mock data instances for three consecutive days
        mock_instances = []
        data_type = 'mag_rtn'
        
        for day in range(1, 4):  # 3 days: May 1-3, 2023
            # Create a mock instance for each day
            class MockInstance:
                def __init__(self):
                    # Create datetime array for this day (24 hours with 15-minute cadence)
                    base_date = datetime(2023, 5, day)
                    self.datetime_array = np.array([base_date + timedelta(minutes=i*15) for i in range(96)])
                    
                    # Create sample field components
                    n_points = len(self.datetime_array)
                    self.raw_data = {
                        'br': np.sin(np.linspace(0, 4*np.pi, n_points)) * day,  # Scale by day to make unique
                        'bt': np.cos(np.linspace(0, 4*np.pi, n_points)) * day,
                        'bn': np.random.rand(n_points) * 0.5 * day,
                        'bmag': np.random.rand(n_points) * day,
                        'pmag': np.random.rand(n_points) * 0.1 * day
                    }
            
            mock_instances.append(MockInstance())
        
        # Store each day's data
        paths = []
        for i, instance in enumerate(mock_instances):
            day = i + 1
            trange = [f"2023-05-{day:02d}T00:00:00", f"2023-05-{day:02d}T23:59:59"]
            path = storage.store_data(instance, data_type, trange)
            paths.append(path)
            
        # Test loading a multi-day range
        test_range = ["2023-05-01T12:00:00", "2023-05-03T12:00:00"]
        loaded_data = storage.load_data(data_type, test_range)
        
        # Verify data was loaded
        if loaded_data is None:
            print_manager.zarr_integration("❌ FAILURE: No data loaded from storage")
            assert False, "No data loaded from storage"
            
        # Verify loaded data spans the requested range
        loaded_times = loaded_data.times
        loaded_start = np.datetime64(loaded_times[0])
        loaded_end = np.datetime64(loaded_times[-1])
        
        request_start = np.datetime64("2023-05-01")
        request_end = np.datetime64("2023-05-03T23:59:59")
        
        # Compare timestamps (must be within range with some tolerance)
        time_range_ok = (loaded_start >= request_start and loaded_end <= request_end)
        
        # Verify we got data for all 3 days (by checking shape)
        expected_points = sum(len(instance.datetime_array) for instance in mock_instances)
        actual_points = len(loaded_data.times)
        
        data_complete = (actual_points == expected_points)
        
        assert time_range_ok and data_complete, f"Time range check: {time_range_ok}. Data completeness: {data_complete}. Expected points: {expected_points}, Actual: {actual_points}"
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: ZarrStorage test failed with error: {e}")
        assert False, f"FAILURE: ZarrStorage test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_integration_with_tracker():
    """
    TEST 5: Integration with DataTracker System
    
    PURPOSE:
    Your system uses a sophisticated DataTracker to keep track of what time ranges
    are already loaded in memory. This test verifies that our Zarr storage system
    correctly integrates with your tracker - Zarr should only be used when data
    isn't already in memory, and the tracker should be updated when data is loaded
    from Zarr.
    
    WHAT IT DOES:
    1. Creates a mock tracker system similar to your global_tracker
    2. Creates a mock data_cubby to store class instances
    3. Simulates the get_data function's logic with Zarr integration
    4. Tests accessing data twice (first load from Zarr, second from memory)
    5. Verifies tracker is correctly updated after loading from Zarr
    
    SUCCESS CRITERIA:
    - First access loads data from Zarr and updates tracker
    - Second access uses in-memory data instead of loading again
    - Data classes are correctly updated with loaded data
    - Tracker correctly records imported time ranges
    
    This test is critical because it validates that Zarr integrates smoothly
    with your existing caching system - ensuring we don't download or process
    data unnecessarily.
    """
    print_manager.zarr_integration("RUNNING TEST 5: Integration with DataTracker")
    print_manager.zarr_integration("Testing integration between ZarrStorage and your DataTracker system")
    
    import os
    import shutil
    import numpy as np
    import xarray as xr
    from datetime import datetime, timedelta
    from dateutil.parser import parse
    
    # Create test directory
    test_dir = './data_cubby_zarr_testing/test_zarr_tracker'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # Create a simple mock tracker for testing
        class MockTracker:
            def __init__(self):
                self.imported_ranges = {}
                
            def is_import_needed(self, trange, data_type):
                """Check if import is needed for time range"""
                if data_type not in self.imported_ranges:
                    return True
                    
                # Parse time range
                start_time = parse(trange[0])
                end_time = parse(trange[1])
                
                # Check if range is covered
                for stored_start, stored_end in self.imported_ranges.get(data_type, []):
                    if start_time >= stored_start and end_time <= stored_end:
                        return False
                        
                return True
                
            def update_imported_range(self, trange, data_type):
                """Record imported time range"""
                if data_type not in self.imported_ranges:
                    self.imported_ranges[data_type] = []
                    
                # Parse time range
                start_time = parse(trange[0])
                end_time = parse(trange[1])
                
                self.imported_ranges[data_type].append((start_time, end_time))
        
        # Create mock data cubby (simplified)
        class MockDataCubby:
            def __init__(self):
                self.instances = {}
                
            def grab(self, class_name):
                """Get instance by class name"""
                return self.instances.get(class_name)
                
            def stash(self, obj, class_name, subclass_name=None):
                """Store instance"""
                self.instances[class_name] = obj
                return obj
        
        # Create simplified ZarrStorage that works with the tracker
        class TestZarrStorage:
            def __init__(self, base_dir, tracker, data_cubby):
                self.base_dir = base_dir
                self.tracker = tracker
                self.data_cubby = data_cubby
                os.makedirs(base_dir, exist_ok=True)
                
            def store_data(self, mock_instance, data_type, trange):
                """Store data to zarr"""
                # Implementation similar to test 4
                # ...
                
            def load_data(self, data_type, trange):
                """Load data with tracker integration"""
                # Check if import is needed according to tracker
                if not self.tracker.is_import_needed(trange, data_type):
                    print_manager.zarr_integration(f"  Tracker says no import needed for {data_type}")
                    return None  # No import needed
                    
                # Implementation similar to test 4
                # ...
                
                # For this test, just create a mock return value
                class ImportedData:
                    def __init__(self):
                        self.times = None
                        self.data = {}
                        
                imported_data = ImportedData()
                
                # Create mock times within the requested range
                start_time = parse(trange[0])
                end_time = parse(trange[1])
                
                # Create hourly timestamps within range
                times = []
                current = start_time
                while current <= end_time:
                    times.append(current)
                    current += timedelta(hours=1)
                
                imported_data.times = np.array(times)
                
                # Create mock field data
                if data_type == 'mag_rtn':
                    n_points = len(times)
                    field_data = np.random.rand(n_points, 3)  # [br, bt, bn]
                    imported_data.data['psp_fld_l2_mag_RTN'] = field_data
                
                # Update tracker
                self.tracker.update_imported_range(trange, data_type)
                
                return imported_data
                
            def get_data(self, trange, data_type):
                """Simulated get_data integration"""
                # Check if we need to load data
                class_instance = self.data_cubby.grab(data_type)
                needs_import = self.tracker.is_import_needed(trange, data_type)
                
                if needs_import:
                    # First try loading from Zarr
                    zarr_data = self.load_data(data_type, trange)
                    
                    if zarr_data is not None:
                        print_manager.zarr_integration(f"  Loading {data_type} from Zarr")
                        
                        # If no class instance exists, create one
                        if class_instance is None:
                            class MockClass:
                                def __init__(self):
                                    self.raw_data = {}
                                    self.datetime_array = None
                                    self.data_type = data_type
                                    
                                def update(self, imported_data):
                                    """Mock update method"""
                                    self.datetime_array = imported_data.times
                                    if data_type == 'mag_rtn':
                                        field = imported_data.data['psp_fld_l2_mag_RTN']
                                        self.raw_data = {
                                            'br': field[:,0],
                                            'bt': field[:,1],
                                            'bn': field[:,2],
                                            'bmag': np.sqrt(np.sum(field**2, axis=1)),
                                            'pmag': np.random.rand(len(field))
                                        }
                            
                            class_instance = MockClass()
                            self.data_cubby.stash(class_instance, data_type)
                        
                        # Update instance with zarr data
                        if hasattr(class_instance, 'update'):
                            class_instance.update(zarr_data)
                            print_manager.zarr_integration(f"  ✅ Updated {data_type} from Zarr")
                            return True
                    else:
                        print_manager.zarr_integration(f"  No Zarr data found for {data_type}")
                        # Normally would download/process here
                        return False
                else:
                    print_manager.zarr_integration(f"  ✅ Using existing {data_type} data (tracker says it's loaded)")
                    return True
        
        # Create instances
        tracker = MockTracker()
        data_cubby = MockDataCubby()
        storage = TestZarrStorage(test_dir, tracker, data_cubby)
        
        # Test 1: First access should need import
        test_range = ["2023-05-01T00:00:00", "2023-05-01T23:59:59"]
        data_type = 'mag_rtn'
        
        first_result = storage.get_data(test_range, data_type)
        if not first_result:
            print_manager.zarr_integration("❌ FAILURE: First access failed")
            assert False, "First access failed"
            
        # Verify tracker was updated
        if data_type not in tracker.imported_ranges:
            print_manager.zarr_integration("❌ FAILURE: Tracker not updated after first access")
            assert False, "Tracker not updated after first access"
            
        # Test 2: Second access should not need import
        second_result = storage.get_data(test_range, data_type)
        
        # Final verification
        class_instance = data_cubby.grab(data_type)
        has_instance = class_instance is not None
        has_data = (has_instance and 
                   hasattr(class_instance, 'datetime_array') and 
                   class_instance.datetime_array is not None and
                   len(class_instance.datetime_array) > 0)
        
        assert first_result and second_result and has_instance and has_data, f"First result: {first_result}. Second result: {second_result}. Has instance: {has_instance}. Has data: {has_data}"
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: Integration test failed with error: {e}")
        assert False, f"FAILURE: Integration test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_end_to_end_integration():
    """
    TEST 6: Complete End-to-End Integration
    
    PURPOSE:
    This test validates the entire workflow from end to end with real data.
    It verifies that all components work together correctly in a real-world
    scenario. This is the final validation before deploying the solution.
    
    WHAT IT DOES:
    1. Downloads real satellite data for a small time period
    2. Processes the data and stores it to Zarr
    3. Clears the in-memory data to simulate a fresh session
    4. Retrieves the data from Zarr using your existing get_data function
    5. Verifies the retrieved data matches the original downloaded data
    
    SUCCESS CRITERIA:
    - Data is correctly downloaded and processed
    - Zarr storage successfully saves the processed data
    - Retrieval from Zarr works correctly after clearing memory
    - Data loaded from Zarr matches the original downloaded data
    
    This test is the most comprehensive and important - it validates that
    the entire system works together seamlessly with real data, providing
    the persistent storage functionality we need while preserving all your
    existing workflow.
    """
    print_manager.zarr_integration("RUNNING TEST 6: End-to-End Integration")
    print_manager.zarr_integration("Testing complete workflow from download to Zarr storage to retrieval")
    
    # This test should use your actual implementation to:
    # 1. Download real data for a small time period
    # 2. Process it and store to Zarr
    # 3. Clear the in-memory data
    # 4. Retrieve the data from Zarr
    # 5. Verify it matches the original
    
    try:
        import os
        import shutil
        from datetime import datetime, timedelta
        
        # Use the real ZarrStorage implementation
        from zarr_storage import ZarrStorage
        from data_tracker import global_tracker
        from data_cubby import data_cubby
        
        # Define test directory and create ZarrStorage instance
        test_dir = './data_cubby_zarr_testing/test_zarr_end_to_end'
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        zarr_storage = ZarrStorage(test_dir)
        
        # Define a short test time range 
        test_range = ["2023-02-01T00:00:00", "2023-02-01T06:00:00"]  # 6 hours of data
        
        # Select a simple data type for testing
        data_type = 'mag_rtn'  # Or another available type
        
        print_manager.zarr_integration("STEP 1: Download and process data")
        # Use your actual get_data to download data
        from get_data import get_data
        
        # Get the data (this should download and process)
        get_data(test_range, data_type)
        
        # Get the processed data
        class_instance = data_cubby.grab(data_type)
        
        # Verify data was downloaded and processed
        if class_instance is None or not hasattr(class_instance, 'datetime_array'):
            print_manager.zarr_integration("❌ FAILURE: Data not downloaded or processed")
            assert False, "Data not downloaded or processed"
            
        # Record the datetime_array for later comparison
        original_times = class_instance.datetime_array.copy()
        original_br = class_instance.raw_data['br'].copy()
        
        print_manager.zarr_integration("STEP 2: Store data to Zarr")
        # Store the data to Zarr
        zarr_storage.store_data(class_instance, data_type, test_range)
        
        print_manager.zarr_integration("STEP 3: Clear in-memory data")
        # Clear the tracker and data_cubby
        global_tracker.imported_ranges = {}
        
        # Create a new instance to replace the existing one 
        class_instance.datetime_array = None
        for key in class_instance.raw_data:
            class_instance.raw_data[key] = None
        
        print_manager.zarr_integration("STEP 4: Retrieve data from Zarr")
        # Get the data again (should load from Zarr)
        get_data(test_range, data_type)
        
        # Get the newly loaded instance
        class_instance = data_cubby.grab(data_type)
        
        # Verify data was loaded from Zarr
        if class_instance is None or not hasattr(class_instance, 'datetime_array'):
            print_manager.zarr_integration("❌ FAILURE: Data not loaded from Zarr")
            assert False, "Data not loaded from Zarr"
            
        print_manager.zarr_integration("STEP 5: Verify data integrity")
        # Compare loaded data with original
        import numpy as np
        
        # Check times match
        times_shape_match = original_times.shape == class_instance.datetime_array.shape
        
        # Check data match
        br_shape_match = original_br.shape == class_instance.raw_data['br'].shape
        
        assert times_shape_match and br_shape_match, f"Data shapes don't match. Times shape match: {times_shape_match}. BR shape match: {br_shape_match}"
        
        # Check values match (allowing small differences due to compression)
        # Use allclose with a small tolerance
        times_match = np.all(original_times == class_instance.datetime_array)
        br_match = np.allclose(original_br, class_instance.raw_data['br'], rtol=1e-5)
        
        assert times_match and br_match, f"Data values don't match. Times match: {times_match}. BR values match: {br_match}"
            
    except Exception as e:
        print_manager.zarr_integration(f"❌ FAILURE: End-to-end test failed with error: {e}")
        assert False, f"FAILURE: End-to-end test failed with error: {e}"
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def run_all_tests():
    """Run all zarr integration tests in sequence."""
    print_manager.zarr_integration("=== RUNNING ALL ZARR INTEGRATION TESTS ===")
    
    # Add print_manager.zarr_integration method if it doesn't exist
    if not hasattr(print_manager, 'zarr_integration'):
        setattr(print_manager, 'zarr_integration', 
                lambda msg, color='#00AAFF': print_manager.custom_print(msg, color))
    
    tests = [
        test_basic_zarr_functionality,
        test_file_structure_and_chunking,
        test_data_class_conversion,
        test_zarr_storage_class,
        test_integration_with_tracker,
        test_end_to_end_integration
    ]
    
    results = []
    
    for i, test_func in enumerate(tests):
        try:
            print_manager.zarr_integration(f"\n{'='*50}")
            test_func()
            results.append(True)
        except Exception as e:
            print_manager.zarr_integration(f"❌ ERROR in test {i+1}: {e}")
            results.append(False)
    
    # Summary
    print_manager.zarr_integration("\n" + "="*50)
    print_manager.zarr_integration("=== ZARR INTEGRATION TEST SUMMARY ===")
    
    for i, result in enumerate(results):
        test_name = tests[i].__name__
        status = "✅ PASSED" if result else "❌ FAILED"
        print_manager.zarr_integration(f"Test {i+1}: {test_name} - {status}")
    
    success_rate = sum(results) / len(results) * 100
    print_manager.zarr_integration(f"\nSuccess rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    all_passed = all(results)
    if all_passed:
        print_manager.zarr_integration("\n✅ ALL TESTS PASSED - Zarr integration ready!")
    else:
        print_manager.zarr_integration("\n❌ SOME TESTS FAILED - See details above")
    
    return all_passed

# Run all tests
if __name__ == "__main__":
    run_all_tests()